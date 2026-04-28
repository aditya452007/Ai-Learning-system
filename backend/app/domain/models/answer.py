"""Answer and citation contracts returned by grounded generation."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.models.retrieval import RetrievalDiagnostics, RetrievalMode


@dataclass(slots=True)
class Citation:
    citation_id: str
    chunk_id: str
    source_id: str
    title: str
    location_label: str
    excerpt: str


@dataclass(slots=True)
class SourceGuide:
    summary: str
    key_topics: list[str]
    glossary: list[dict[str, str]]
    suggested_questions: list[str]
    coverage_notes: str = ""
    cache_hit: bool = False


@dataclass(slots=True)
class Answer:
    answer: str
    retrieval_mode: RetrievalMode
    citations: list[Citation]
    diagnostics: RetrievalDiagnostics
    metadata: dict[str, object] = field(default_factory=dict)

