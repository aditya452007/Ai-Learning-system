"""Chunk model preserving source traceability."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.models.base import new_id


@dataclass(slots=True)
class ChunkLocation:
    page: int | None = None
    heading: str | None = None
    line_start: int | None = None
    line_end: int | None = None

    def label(self) -> str:
        if self.page is not None:
            return f"page {self.page}"
        if self.heading:
            return self.heading
        if self.line_start is not None:
            end = self.line_end if self.line_end is not None else self.line_start
            return f"lines {self.line_start}-{end}"
        return "source"


@dataclass(slots=True)
class DocumentChunk:
    id: str
    workspace_id: str
    source_id: str
    text: str
    chunk_hash: str
    token_count: int
    location: ChunkLocation
    metadata: dict[str, object] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        workspace_id: str,
        source_id: str,
        text: str,
        chunk_hash: str,
        token_count: int,
        location: ChunkLocation,
        metadata: dict[str, object] | None = None,
    ) -> "DocumentChunk":
        return cls(
            id=new_id("chunk"),
            workspace_id=workspace_id,
            source_id=source_id,
            text=text,
            chunk_hash=chunk_hash,
            token_count=token_count,
            location=location,
            metadata=metadata or {},
        )

