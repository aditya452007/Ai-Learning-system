"""Graph DTOs for source, chunk, and concept exploration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GraphNodeType(str, Enum):
    SOURCE = "source"
    CHUNK = "chunk"
    CONCEPT = "concept"


@dataclass(slots=True)
class GraphNode:
    id: str
    label: str
    type: GraphNodeType
    weight: float = 1.0


@dataclass(slots=True)
class GraphEdge:
    id: str
    source: str
    target: str
    type: str
    weight: float = 1.0


@dataclass(slots=True)
class GraphSnapshot:
    nodes: list[GraphNode]
    edges: list[GraphEdge]
