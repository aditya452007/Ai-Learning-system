"""Gemini generation adapter with an extractive local fallback."""

from __future__ import annotations

import re

from app.domain.models.answer import SourceGuide
from app.domain.models.document_chunk import DocumentChunk
from app.domain.ports.generation_provider import GeneratedAnswer, GenerationProviderPort, GenerationRequest


class GeminiProvider(GenerationProviderPort):
    def __init__(self, api_key: str | None = None, model_name: str = "gemini-2.5-flash") -> None:
        self._model_name = model_name
        self._client = None
        if api_key and api_key != "GEMINI_API_KEY":
            try:
                import google.generativeai as genai  # type: ignore
            except Exception:
                self._client = None
            else:
                genai.configure(api_key=api_key)
                self._client = genai.GenerativeModel(model_name)

    @property
    def model_name(self) -> str:
        return self._model_name if self._client is not None else "extractive-local"

    async def generate_answer(self, request: GenerationRequest) -> GeneratedAnswer:
        if not request.chunks:
            return GeneratedAnswer(
                text="I do not have enough evidence in the workspace sources to answer that.",
                used_citation_ids=[],
                model_name=self.model_name,
            )
        if self._client is None:
            return self._extractive_answer(request)

        context = "\n\n".join(
            f"[{citation_id}] {chunk.text}" for citation_id, chunk in zip(request.citations, request.chunks, strict=True)
        )
        prompt = (
            "Answer only from the context. Include citation ids like [cite_1]. "
            "If the context is insufficient, say so.\n\n"
            f"Question: {request.query}\n\nContext:\n{context}"
        )
        response = await self._client.generate_content_async(prompt)
        text = getattr(response, "text", "") or "The model returned an empty answer."
        return GeneratedAnswer(text=text, used_citation_ids=self._citation_ids(text), model_name=self.model_name)

    async def generate_source_guide(self, chunks: list[DocumentChunk], source_title: str | None = None) -> SourceGuide:
        combined = "\n".join(chunk.text for chunk in chunks[:8])
        topics = self._topics(combined, limit=8)
        summary = self._summarize(combined, source_title)
        glossary = [{"term": topic, "definition": f"A recurring concept in {source_title or 'the selected sources'}."} for topic in topics[:5]]
        questions = [f"How does {topic} relate to the rest of this workspace?" for topic in topics[:5]]
        return SourceGuide(
            summary=summary,
            key_topics=topics,
            glossary=glossary,
            suggested_questions=questions,
            coverage_notes=f"Guide generated from {len(chunks)} indexed chunk(s).",
            cache_hit=False,
        )

    def _extractive_answer(self, request: GenerationRequest) -> GeneratedAnswer:
        query_terms = set(re.findall(r"[A-Za-z0-9_]+", request.query.lower()))
        selected: list[tuple[str, DocumentChunk]] = []
        for citation_id, chunk in zip(request.citations, request.chunks, strict=True):
            chunk_terms = set(re.findall(r"[A-Za-z0-9_]+", chunk.text.lower()))
            if query_terms.intersection(chunk_terms) or len(selected) < 2:
                selected.append((citation_id, chunk))
            if len(selected) >= 3:
                break
        if not selected:
            return GeneratedAnswer(
                text="I do not have enough evidence in the retrieved sources to answer that.",
                used_citation_ids=[],
                model_name=self.model_name,
            )
        sentences = []
        used = []
        for citation_id, chunk in selected:
            sentence = self._best_sentence(chunk.text, query_terms)
            if sentence:
                sentences.append(f"{sentence} [{citation_id}]")
                used.append(citation_id)
        answer = " ".join(sentences) or "The retrieved sources are relevant, but the evidence is too weak to summarize confidently."
        return GeneratedAnswer(text=answer, used_citation_ids=used, model_name=self.model_name)

    def _best_sentence(self, text: str, query_terms: set[str]) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
        ranked = sorted(
            sentences,
            key=lambda sentence: len(query_terms.intersection(re.findall(r"[A-Za-z0-9_]+", sentence.lower()))),
            reverse=True,
        )
        return (ranked[0] if ranked else text[:240])[:420]

    def _citation_ids(self, text: str) -> list[str]:
        return sorted(set(re.findall(r"cite_\d+", text)))

    def _topics(self, text: str, limit: int) -> list[str]:
        stop = {"that", "with", "from", "this", "have", "will", "should", "retrieval", "source", "chunk"}
        counts: dict[str, int] = {}
        for token in re.findall(r"\b[A-Za-z][A-Za-z0-9_-]{3,}\b", text):
            lowered = token.lower()
            if lowered not in stop:
                counts[lowered] = counts.get(lowered, 0) + 1
        return [term.title() for term, _ in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]]

    def _summarize(self, text: str, source_title: str | None) -> str:
        compact = " ".join(text.split())
        prefix = f"{source_title} covers" if source_title else "The selected sources cover"
        if not compact:
            return f"{prefix} no indexed text yet."
        return f"{prefix} {compact[:500]}{'...' if len(compact) > 500 else ''}"

