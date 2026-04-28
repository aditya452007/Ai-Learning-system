"""Retrieval request and result contracts shared by all retrievers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RetrievalMode(str, Enum):
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    GRAPH = "graph"
    AUTO = "auto"


@dataclass(slots=True)
class RetrievalQuery:
    workspace_id: str
    text: str
    mode: RetrievalMode = RetrievalMode.HYBRID
    top_k: int = 6
    filters: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievalResult:
    chunk_id: str
    source_id: str
    score: float
    rank: int
    retriever: str
    excerpt: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievalDiagnostics:
    semantic_hits: int = 0
    keyword_hits: int = 0
    graph_hits: int = 0
    fused_hits: int = 0
    retrieval_cache_hit: bool = False
    answer_cache_hit: bool = False
    latency_ms: int = 0
    planned_mode: RetrievalMode = RetrievalMode.HYBRID
