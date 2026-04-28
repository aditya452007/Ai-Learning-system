"""Vector retrieval store port."""

from __future__ import annotations

from typing import Protocol

from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.retrieval import RetrievalResult


class VectorStorePort(Protocol):
    def upsert(self, workspace_id: str, chunks: list[DocumentChunk], vectors: list[list[float]]) -> None:
        ...

    def search(self, workspace_id: str, query_vector: list[float], top_k: int) -> list[RetrievalResult]:
        ...

    def clear(self, workspace_id: str) -> None:
        ...

