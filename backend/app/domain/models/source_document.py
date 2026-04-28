"""Source document contracts produced by loaders."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.domain.models.base import new_id


class SourceType(str, Enum):
    PDF = "pdf"
    MARKDOWN = "markdown"
    TEXT = "text"
    URL = "url"
    CODE = "code"


@dataclass(slots=True)
class SourceInput:
    uri: str
    path: str | None = None
    source_type: SourceType | None = None
    title: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class LoadedSource:
    title: str
    source_type: SourceType
    uri: str
    text: str
    content_hash: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class SourceDocument:
    id: str
    workspace_id: str
    title: str
    source_type: SourceType
    uri: str
    content_hash: str
    metadata: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_loaded(cls, workspace_id: str, loaded: LoadedSource) -> "SourceDocument":
        return cls(
            id=new_id("source"),
            workspace_id=workspace_id,
            title=loaded.title,
            source_type=loaded.source_type,
            uri=loaded.uri,
            content_hash=loaded.content_hash,
            metadata=dict(loaded.metadata),
        )
