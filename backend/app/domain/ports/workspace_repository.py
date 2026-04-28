"""Repository port for workspace metadata, sources, and chunks."""

from __future__ import annotations

from typing import Protocol

from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.source_document import SourceDocument
from app.domain.models.workspace import Workspace


class WorkspaceRepositoryPort(Protocol):
    def save_workspace(self, workspace: Workspace) -> None:
        ...

    def get_workspace(self, workspace_id: str) -> Workspace:
        ...

    def list_workspaces(self) -> list[Workspace]:
        ...

    def add_source_with_chunks(self, source: SourceDocument, chunks: list[DocumentChunk]) -> None:
        ...

    def list_sources(self, workspace_id: str) -> list[SourceDocument]:
        ...

    def list_chunks(self, workspace_id: str, source_id: str | None = None) -> list[DocumentChunk]:
        ...

    def find_source_by_hash(self, workspace_id: str, content_hash: str) -> SourceDocument | None:
        ...

    def clear_all(self) -> None:
        ...

