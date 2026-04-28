"""Build grounded context and citations from retrieval results."""

from __future__ import annotations

from app.domain.models.answer import Citation
from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.retrieval import RetrievalResult
from app.domain.models.source_document import SourceDocument


class ContextBuilder:
    def build(
        self,
        results: list[RetrievalResult],
        chunks: list[DocumentChunk],
        sources: list[SourceDocument],
    ) -> tuple[list[DocumentChunk], list[Citation]]:
        chunk_by_id = {chunk.id: chunk for chunk in chunks}
        source_by_id = {source.id: source for source in sources}
        selected_chunks: list[DocumentChunk] = []
        citations: list[Citation] = []
        for index, result in enumerate(results, start=1):
            chunk = chunk_by_id.get(result.chunk_id)
            if not chunk:
                continue
            source = source_by_id.get(chunk.source_id)
            if not source:
                continue
            citation_id = f"cite_{index}"
            selected_chunks.append(chunk)
            citations.append(
                Citation(
                    citation_id=citation_id,
                    chunk_id=chunk.id,
                    source_id=source.id,
                    title=source.title,
                    location_label=chunk.location.label(),
                    excerpt=result.excerpt or self._excerpt(chunk.text),
                )
            )
        return selected_chunks, citations

    def _excerpt(self, text: str, limit: int = 360) -> str:
        compact = " ".join(text.split())
        return compact[:limit] + ("..." if len(compact) > limit else "")

