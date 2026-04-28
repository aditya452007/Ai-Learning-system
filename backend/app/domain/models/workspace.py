"""Workspace domain model and index version state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.domain.models.base import new_id, utc_now


@dataclass(slots=True)
class Workspace:
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    index_version: int = 0
    source_count: int = 0
    chunk_count: int = 0
    metadata: dict[str, object] = field(default_factory=dict)

    @classmethod
    def create(cls, name: str) -> "Workspace":
        now = utc_now()
        return cls(id=new_id("workspace"), name=name.strip() or "Untitled Workspace", created_at=now, updated_at=now)

    def mark_index_changed(self, source_count: int, chunk_count: int) -> None:
        self.index_version += 1
        self.source_count = source_count
        self.chunk_count = chunk_count
        self.updated_at = utc_now()

