"""Chat API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    workspace_id: str | None = None
    session_id: str | None = None
    query: str = Field(min_length=1)
    retrieval_mode: str = "hybrid"
    top_k: int = Field(default=6, ge=1, le=20)


class CitationResponse(BaseModel):
    citation_id: str
    chunk_id: str
    source_id: str
    title: str
    location_label: str
    excerpt: str


class RetrievalDiagnosticsResponse(BaseModel):
    semantic_hits: int
    keyword_hits: int
    graph_hits: int
    fused_hits: int
    retrieval_cache_hit: bool
    answer_cache_hit: bool
    latency_ms: int
    planned_mode: str


class ChatResponse(BaseModel):
    answer: str
    response: str
    retrieval_mode: str
    citations: list[CitationResponse]
    diagnostics: RetrievalDiagnosticsResponse

