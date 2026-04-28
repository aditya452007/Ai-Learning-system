"""Query planning strategy for retrieval mode selection."""

from __future__ import annotations

import re

from app.domain.models.retrieval import RetrievalMode


class QueryPlanner:
    def plan(self, query: str, requested_mode: RetrievalMode) -> RetrievalMode:
        if requested_mode != RetrievalMode.AUTO:
            return requested_mode
        lowered = query.lower()
        if any(term in lowered for term in ("depend", "relate", "relationship", "connected", "graph")):
            return RetrievalMode.GRAPH
        if re.search(r"`[^`]+`|[A-Z_]{3,}|[A-Za-z]+Error|Exception|[./_-]", query):
            return RetrievalMode.HYBRID
        return RetrievalMode.HYBRID

