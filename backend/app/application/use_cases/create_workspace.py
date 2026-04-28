"""Create workspace use case."""

from __future__ import annotations

from app.domain.models.workspace import Workspace
from app.domain.ports.workspace_repository import WorkspaceRepositoryPort


class CreateWorkspace:
    def __init__(self, repository: WorkspaceRepositoryPort) -> None:
        self.repository = repository

    def execute(self, name: str) -> Workspace:
        workspace = Workspace.create(name)
        self.repository.save_workspace(workspace)
        return workspace

