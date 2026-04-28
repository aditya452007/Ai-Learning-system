"""Chunker port for splitting loaded sources into traceable chunks."""

from __future__ import annotations

from typing import Protocol

from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.source_document import LoadedSource, SourceDocument


class ChunkerPort(Protocol):
    def chunk(self, source: SourceDocument, loaded: LoadedSource) -> list[DocumentChunk]:
        ...

