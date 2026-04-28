"""Graph API route."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_rag_system
from app.api.schemas.graph_schemas import GraphResponse
from app.application.rag_learning_system import RagLearningSystem

router = APIRouter(tags=["graph"])


@router.get("/graph", response_model=GraphResponse)
def graph(
    workspace_id: str,
    focus_node_id: str | None = None,
    depth: int = Query(default=1, ge=1, le=3),
    system: RagLearningSystem = Depends(get_rag_system),
) -> GraphResponse:
    snapshot = system.get_graph(workspace_id, focus_node_id=focus_node_id, depth=depth)
    return GraphResponse(
        nodes=[asdict(node) | {"type": node.type.value} for node in snapshot.nodes],
        edges=[asdict(edge) for edge in snapshot.edges],
    )

