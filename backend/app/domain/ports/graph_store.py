"""Graph persistence and retrieval port."""

from __future__ import annotations

from typing import Protocol

from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.graph import GraphSnapshot
from app.domain.models.source_document import SourceDocument
from app.domain.models.retrieval import RetrievalResult


class GraphStorePort(Protocol):
    def build(self, workspace_id: str, sources: list[SourceDocument], chunks: list[DocumentChunk]) -> None:
        ...

    def snapshot(self, workspace_id: str, focus_node_id: str | None = None, depth: int = 1) -> GraphSnapshot:
        ...

    def search(self, workspace_id: str, query: str, top_k: int) -> list[RetrievalResult]:
        ...

