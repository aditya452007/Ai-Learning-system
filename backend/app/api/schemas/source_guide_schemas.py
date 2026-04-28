"""Source guide API schemas."""

from __future__ import annotations

from pydantic import BaseModel


class SourceGuideResponse(BaseModel):
    summary: str
    key_topics: list[str]
    glossary: list[dict[str, str]]
    suggested_questions: list[str]
    coverage_notes: str
    cache_hit: bool

