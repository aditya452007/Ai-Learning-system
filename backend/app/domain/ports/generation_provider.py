"""Generation provider port shielded from concrete LLM SDKs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.domain.models.answer import SourceGuide
from app.domain.models.document_chunk import DocumentChunk


@dataclass(slots=True)
class GenerationRequest:
    query: str
    chunks: list[DocumentChunk]
    citations: list[str]
    workspace_name: str


@dataclass(slots=True)
class GeneratedAnswer:
    text: str
    used_citation_ids: list[str]
    model_name: str


class GenerationProviderPort(Protocol):
    @property
    def model_name(self) -> str:
        ...

    async def generate_answer(self, request: GenerationRequest) -> GeneratedAnswer:
        ...

    async def generate_source_guide(self, chunks: list[DocumentChunk], source_title: str | None = None) -> SourceGuide:
        ...

