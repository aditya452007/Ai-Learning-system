"""Graph snapshot use case."""

from __future__ import annotations

from app.domain.models.graph import GraphSnapshot
from app.domain.ports.graph_store import GraphStorePort
from app.domain.ports.workspace_repository import WorkspaceRepositoryPort


class GetGraph:
    def __init__(self, repository: WorkspaceRepositoryPort, graph_store: GraphStorePort) -> None:
        self.repository = repository
        self.graph_store = graph_store

    def execute(self, workspace_id: str, focus_node_id: str | None = None, depth: int = 1) -> GraphSnapshot:
        self.repository.get_workspace(workspace_id)
        return self.graph_store.snapshot(workspace_id, focus_node_id=focus_node_id, depth=depth)

