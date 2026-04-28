"""Keyword retrieval store port."""

from __future__ import annotations

from typing import Protocol

from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.retrieval import RetrievalResult


class KeywordStorePort(Protocol):
    def build(self, workspace_id: str, chunks: list[DocumentChunk]) -> None:
        ...

    def search(self, workspace_id: str, query: str, top_k: int) -> list[RetrievalResult]:
        ...

    def clear(self, workspace_id: str) -> None:
        ...

