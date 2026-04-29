"""Application facade coordinating the MultiRAG learning workflows."""

from __future__ import annotations

import logging
from pathlib import Path

from app.application.services.citation_verifier import CitationVerifier
from app.application.services.context_builder import ContextBuilder
from app.application.services.query_planner import QueryPlanner
from app.application.use_cases.ask_question import AskQuestion
from app.application.use_cases.create_workspace import CreateWorkspace
from app.application.use_cases.generate_source_guide import GenerateSourceGuide
from app.application.use_cases.get_graph import GetGraph
from app.application.use_cases.ingest_sources import IngestSources, IngestionResult
from app.domain.models.answer import Answer, SourceGuide
from app.domain.models.graph import GraphSnapshot
from app.domain.models.retrieval import RetrievalMode, RetrievalQuery
from app.domain.models.source_document import SourceInput, SourceType
from app.domain.models.workspace import Workspace
from app.domain.services.retrieval_fusion import ReciprocalRankFusionService
from app.infrastructure.chunkers.code_chunker import CodeChunker
from app.infrastructure.chunkers.markdown_chunker import MarkdownChunker
from app.infrastructure.chunkers.recursive_text_chunker import RecursiveTextChunker
from app.infrastructure.config.settings import Settings
from app.infrastructure.embeddings.embedding_cache import CachedEmbeddingProvider
from app.infrastructure.embeddings.sentence_transformer_embeddings import (
    HashingEmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
)
from app.infrastructure.generation.unified_provider import UnifiedGenerationProvider, UnifiedProviderFactory
from app.infrastructure.loaders.code_loader import CodeLoader
from app.infrastructure.loaders.markdown_loader import MarkdownLoader
from app.infrastructure.loaders.pdf_loader import PdfLoader
from app.infrastructure.loaders.text_loader import TextLoader
from app.infrastructure.loaders.unified_loader import UnifiedLoader
from app.infrastructure.loaders.web_loader import WebLoader
from app.infrastructure.persistence.disk_cache_store import DiskCacheStore
from app.infrastructure.persistence.file_workspace_repository import FileWorkspaceRepository
from app.infrastructure.retrieval.bm25_store import Bm25Store
from app.infrastructure.retrieval.chroma_vector_store import ChromaVectorStore
from app.infrastructure.retrieval.faiss_vector_store import FaissVectorStore
from app.infrastructure.retrieval.graph_networkx_store import GraphNetworkxStore

logger = logging.getLogger(__name__)


class RagLearningSystem:
    """Friendly public facade over application use cases."""

    def __init__(
        self,
        create_workspace_use_case: CreateWorkspace,
        ingest_sources_use_case: IngestSources,
        ask_question_use_case: AskQuestion,
        generate_source_guide_use_case: GenerateSourceGuide,
        get_graph_use_case: GetGraph,
        repository: FileWorkspaceRepository,
    ) -> None:
        self._create_workspace = create_workspace_use_case
        self._ingest_sources = ingest_sources_use_case
        self._ask_question = ask_question_use_case
        self._generate_source_guide = generate_source_guide_use_case
        self._get_graph = get_graph_use_case
        self.repository = repository

    @classmethod
    def from_settings(cls, settings: Settings) -> "RagLearningSystem":
        repository = FileWorkspaceRepository(settings.data_dir)
        cache_store = DiskCacheStore(settings.cache_dir)
        index_dir = settings.data_dir / "_indexes"

        # Ensure ChromaDB directory exists
        settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)

        loader = UnifiedLoader(
            {
                SourceType.PDF: PdfLoader(),
                SourceType.MARKDOWN: MarkdownLoader(),
                SourceType.TEXT: TextLoader(),
                SourceType.URL: WebLoader(settings.url_timeout_seconds),
                SourceType.CODE: CodeLoader(),
            }
        )
        
        # Use new settings names (chunk_size, chunk_overlap)
        text_chunker = RecursiveTextChunker(settings.chunk_size, settings.chunk_overlap)
        markdown_chunker = MarkdownChunker(settings.chunk_size, settings.chunk_overlap)
        code_chunker = CodeChunker()
        
        # Modern embedding provider with sentence-transformers
        if settings.embedding_model == "local-hashing-384":
            base_embedding_provider = HashingEmbeddingProvider()
        else:
            base_embedding_provider = SentenceTransformerEmbeddingProvider(
                model_name=settings.embedding_model,
            )
        
        embedding_provider = CachedEmbeddingProvider(base_embedding_provider, cache_store)
        
        # Select vector store based on settings
        if settings.vector_store_type == "chroma":
            logger.info(f"Using ChromaDB vector store at {settings.chroma_persist_dir}")
            vector_store = ChromaVectorStore(
                persist_dir=settings.chroma_persist_dir,
                embedding_model=settings.embedding_model,
            )
        else:
            logger.info(f"Using FAISS vector store at {index_dir}")
            vector_store = FaissVectorStore(index_dir)
        
        keyword_store = Bm25Store(index_dir)
        graph_store = GraphNetworkxStore(index_dir)
        generation_provider = UnifiedProviderFactory.get_provider()

        create_workspace = CreateWorkspace(repository)
        ingest_sources = IngestSources(
            repository=repository,
            loader=loader,
            chunkers={
                SourceType.MARKDOWN: markdown_chunker,
                SourceType.CODE: code_chunker,
            },
            default_chunker=text_chunker,
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            keyword_store=keyword_store,
            graph_store=graph_store,
        )
        ask_question = AskQuestion(
            repository=repository,
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            keyword_store=keyword_store,
            graph_store=graph_store,
            generation_provider=generation_provider,
            cache_store=cache_store,
            query_planner=QueryPlanner(),
            fusion_service=ReciprocalRankFusionService(),
            context_builder=ContextBuilder(),
            citation_verifier=CitationVerifier(),
        )
        generate_source_guide = GenerateSourceGuide(repository, generation_provider, cache_store)
        get_graph = GetGraph(repository, graph_store)
        return cls(create_workspace, ingest_sources, ask_question, generate_source_guide, get_graph, repository)

    def create_workspace(self, name: str) -> Workspace:
        return self._create_workspace.execute(name)

    def list_workspaces(self) -> list[Workspace]:
        return self.repository.list_workspaces()

    def get_workspace(self, workspace_id: str) -> Workspace:
        return self.repository.get_workspace(workspace_id)

    async def ingest_sources(self, workspace_id: str, inputs: list[SourceInput]) -> IngestionResult:
        return await self._ingest_sources.execute(workspace_id, inputs)

    async def ask(
        self,
        workspace_id: str,
        query: str,
        retrieval_mode: RetrievalMode = RetrievalMode.HYBRID,
        top_k: int = 6,
        generation_params: dict | None = None,
    ) -> Answer:
        return await self._ask_question.execute(
            RetrievalQuery(workspace_id=workspace_id, text=query, mode=retrieval_mode, top_k=top_k),
            generation_params=generation_params,
        )

    def get_graph(self, workspace_id: str, focus_node_id: str | None = None, depth: int = 1) -> GraphSnapshot:
        return self._get_graph.execute(workspace_id, focus_node_id=focus_node_id, depth=depth)

    async def generate_source_guide(self, workspace_id: str, source_id: str | None = None) -> SourceGuide:
        return await self._generate_source_guide.execute(workspace_id, source_id)

    def workspace_storage_dir(self, workspace_id: str) -> Path:
        return self.repository.workspace_storage_dir(workspace_id)

    def reset(self) -> None:
        self.repository.clear_all()

