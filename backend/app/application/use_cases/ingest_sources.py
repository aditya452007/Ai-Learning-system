"""Source ingestion and indexing use case."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.source_document import SourceDocument, SourceInput, SourceType
from app.domain.ports.chunker import ChunkerPort
from app.domain.ports.embedding_provider import EmbeddingProviderPort
from app.domain.ports.graph_store import GraphStorePort
from app.domain.ports.keyword_store import KeywordStorePort
from app.domain.ports.source_loader import SourceLoaderPort
from app.domain.ports.vector_store import VectorStorePort
from app.domain.ports.workspace_repository import WorkspaceRepositoryPort


@dataclass(slots=True)
class IngestionResult:
    job_id: str
    status: str
    sources_added: int
    chunks_added: int
    index_version: int
    warnings: list[str] = field(default_factory=list)


class IngestSources:
    def __init__(
        self,
        repository: WorkspaceRepositoryPort,
        loader: SourceLoaderPort,
        chunkers: dict[SourceType, ChunkerPort],
        default_chunker: ChunkerPort,
        embedding_provider: EmbeddingProviderPort,
        vector_store: VectorStorePort,
        keyword_store: KeywordStorePort,
        graph_store: GraphStorePort,
        batch_concurrency: int = 3,
    ) -> None:
        self.repository = repository
        self.loader = loader
        self.chunkers = chunkers
        self.default_chunker = default_chunker
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.keyword_store = keyword_store
        self.graph_store = graph_store
        self.batch_concurrency = batch_concurrency

    async def execute(self, workspace_id: str, inputs: list[SourceInput]) -> IngestionResult:
        workspace = self.repository.get_workspace(workspace_id)
        semaphore = asyncio.Semaphore(self.batch_concurrency)
        warnings: list[str] = []
        added_sources: list[SourceDocument] = []
        added_chunks: list[DocumentChunk] = []

        async def process(source_input: SourceInput) -> None:
            async with semaphore:
                try:
                    loaded = await self.loader.load(source_input)
                    existing = self.repository.find_source_by_hash(workspace_id, loaded.content_hash)
                    if existing:
                        warnings.append(f"Skipped unchanged source: {loaded.title}")
                        return
                    source = SourceDocument.from_loaded(workspace_id, loaded)
                    chunker = self.chunkers.get(source.source_type, self.default_chunker)
                    chunks = chunker.chunk(source, loaded)
                    self.repository.add_source_with_chunks(source, chunks)
                    added_sources.append(source)
                    added_chunks.extend(chunks)
                except Exception as exc:
                    warnings.append(f"{source_input.uri}: {exc}")

        await asyncio.gather(*(process(item) for item in inputs))

        if added_chunks:
            vectors = self.embedding_provider.embed_texts([chunk.text for chunk in added_chunks])
            self.vector_store.upsert(workspace_id, added_chunks, vectors)

        all_sources = self.repository.list_sources(workspace_id)
        all_chunks = self.repository.list_chunks(workspace_id)
        self.keyword_store.build(workspace_id, all_chunks)
        try:
            if added_sources or added_chunks:
                self.graph_store.build(workspace_id, added_sources, added_chunks)
        except Exception as exc:
            warnings.append(f"Graph build degraded: {exc}")

        if added_sources or added_chunks:
            workspace.mark_index_changed(source_count=len(all_sources), chunk_count=len(all_chunks))
            self.repository.save_workspace(workspace)

        return IngestionResult(
            job_id=f"job_{workspace.index_version}",
            status="completed" if added_sources or not warnings else "failed",
            sources_added=len(added_sources),
            chunks_added=len(added_chunks),
            index_version=workspace.index_version,
            warnings=warnings,
        )

