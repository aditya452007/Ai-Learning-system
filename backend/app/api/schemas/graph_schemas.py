"""Graph API schemas."""

from __future__ import annotations

from pydantic import BaseModel


class GraphNodeResponse(BaseModel):
    id: str
    label: str
    type: str
    weight: float


class GraphEdgeResponse(BaseModel):
    id: str
    source: str
    target: str
    type: str
    weight: float


class GraphResponse(BaseModel):
    nodes: list[GraphNodeResponse]
    edges: list[GraphEdgeResponse]

