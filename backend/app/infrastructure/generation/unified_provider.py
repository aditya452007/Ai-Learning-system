"""Unified multi-provider LLM generation adapter.

Supports NVIDIA, OpenAI, Anthropic, and Gemini APIs with automatic
provider detection and provider-agnostic parameter mapping.
"""

from __future__ import annotations

import json
import re
from typing import Any

from app.domain.models.answer import SourceGuide
from app.domain.models.document_chunk import DocumentChunk
from app.domain.ports.generation_provider import GeneratedAnswer, GenerationProviderPort, GenerationRequest
from app.infrastructure.config.llm_providers import LLMConfig, ModelRegistry, ProviderType


class UnifiedGenerationProvider(GenerationProviderPort):
    """Multi-provider LLM generation with automatic provider detection."""

    def __init__(self, config: LLMConfig | None = None) -> None:
        self._config = config or LLMConfig.from_env()
        self._client: Any = None
        self._init_client()

    def _init_client(self) -> None:
        """Initialize the appropriate client based on provider type."""
        try:
            if self._config.provider == ProviderType.NVIDIA:
                import openai  # type: ignore
                base_url = self._config.base_url or "https://integrate.api.nvidia.com/v1"
                self._client = openai.AsyncOpenAI(
                    base_url=base_url,
                    api_key=self._config.api_key,
                )
            elif self._config.provider == ProviderType.OPENAI:
                import openai  # type: ignore
                self._client = openai.AsyncOpenAI(api_key=self._config.api_key)
            elif self._config.provider == ProviderType.ANTHROPIC:
                import anthropic  # type: ignore
                self._client = anthropic.AsyncAnthropic(api_key=self._config.api_key)
            elif self._config.provider == ProviderType.GEMINI:
                import google.generativeai as genai  # type: ignore
                genai.configure(api_key=self._config.api_key)
                self._client = genai.GenerativeModel(self._config.model)
        except Exception as e:
            print(f"Failed to initialize {self._config.provider} client: {e}")
            self._client = None

    @property
    def model_name(self) -> str:
        """Return the model name, or fallback identifier if client unavailable."""
        if self._client is None:
            return "extractive-local"
        return self._config.model

    @property
    def config(self) -> LLMConfig:
        """Access current configuration."""
        return self._config

    def update_config(self, config: LLMConfig) -> None:
        """Update configuration and reinitialize client if provider changed."""
        provider_changed = self._config.provider != config.provider
        self._config = config
        if provider_changed or self._client is None:
            self._init_client()

    def get_llm(self, temp: float, top_p: float, max_tokens: int) -> Any:
        """Get a LangChain LLM instance."""
        try:
            if self._config.provider in (ProviderType.NVIDIA, ProviderType.OPENAI):
                try:
                    from langchain_openai import ChatOpenAI
                except ImportError:
                    from langchain_community.chat_models import ChatOpenAI
                base_url = self._config.base_url
                if self._config.provider == ProviderType.NVIDIA and not base_url:
                    base_url = "https://integrate.api.nvidia.com/v1"
                return ChatOpenAI(
                    model=self._config.model,
                    api_key=self._config.api_key,
                    base_url=base_url,
                    temperature=temp,
                    model_kwargs={"top_p": top_p},
                    max_tokens=max_tokens
                )
            elif self._config.provider == ProviderType.ANTHROPIC:
                try:
                    from langchain_anthropic import ChatAnthropic
                except ImportError:
                    from langchain_community.chat_models import ChatAnthropic
                return ChatAnthropic(
                    model=self._config.model,
                    anthropic_api_key=self._config.api_key,
                    temperature=temp,
                    model_kwargs={"top_p": top_p},
                    max_tokens=max_tokens
                )
            elif self._config.provider == ProviderType.GEMINI:
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(
                    model=self._config.model,
                    google_api_key=self._config.api_key,
                    temperature=temp,
                    max_output_tokens=max_tokens
                )
        except Exception as e:
            print(f"Failed to initialize LangChain LLM: {e}")
        return None

    async def generate_answer(
        self,
        request: GenerationRequest,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
    ) -> GeneratedAnswer:
        """Generate an answer using the configured provider."""
        if not request.chunks:
            return GeneratedAnswer(
                text="I do not have enough evidence in the workspace sources to answer that.",
                used_citation_ids=[],
                model_name=self.model_name,
            )

        # Use request-specific params or fall back to config defaults
        temp = temperature if temperature is not None else self._config.temperature
        p_val = top_p if top_p is not None else self._config.top_p
        k_val = top_k if top_k is not None else self._config.top_k
        tokens = max_tokens if max_tokens is not None else self._config.max_tokens
        sys_prompt = system_prompt if system_prompt is not None else self._config.system_prompt

        if self._client is None:
            return self._extractive_answer(request)

        # Build context with citations
        context_str = "\n---\n".join(
            f"[{citation_id}] {chunk.text}"
            for citation_id, chunk in zip(request.citations, request.chunks, strict=True)
        )

        try:
            llm = self.get_llm(temp, p_val, tokens)
            if llm is None:
                raise ValueError("Could not initialize LangChain LLM")

            from langchain_core.messages import SystemMessage, HumanMessage

            full_prompt = (
                f"Context:\n{context_str}\n\n"
                f"Question: {request.query}\n\n"
                f"Answer:"
            )

            print(f"SENDING MODEL VIA LANGCHAIN: {self._config.model}")
            response = await llm.ainvoke([
                SystemMessage(content=sys_prompt),
                HumanMessage(content=full_prompt)
            ])
            text = str(response.content) if response else ""

            return GeneratedAnswer(
                text=text or "The model returned an empty answer.",
                used_citation_ids=self._citation_ids(text),
                model_name=self.model_name,
            )
        except Exception as e:
            return GeneratedAnswer(
                text=f"Error generating response: {str(e)}. Falling back to extractive mode.",
                used_citation_ids=[],
                model_name=self.model_name,
            )

    async def _generate_nvidia(
        self, query: str, context: str, system: str, temp: float, top_p: float, max_tokens: int
    ) -> str:
        """Generate using NVIDIA API (OpenAI-compatible)."""
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": f"Answer only from the context. Include citation ids like [cite_1]. "
                f"If the context is insufficient, say so.\n\nQuestion: {query}\n\nContext:\n{context}",
            },
        ]
        print(f"SENDING MODEL: {self._config.model}")
        response = await self._client.chat.completions.create(
            model=self._config.model,
            messages=messages,
            temperature=temp,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    async def _generate_openai(
        self, query: str, context: str, system: str, temp: float, top_p: float, max_tokens: int
    ) -> str:
        """Generate using OpenAI API."""
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": f"Answer only from the context. Include citation ids like [cite_1]. "
                f"If the context is insufficient, say so.\n\nQuestion: {query}\n\nContext:\n{context}",
            },
        ]
        response = await self._client.chat.completions.create(
            model=self._config.model,
            messages=messages,
            temperature=temp,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    async def _generate_anthropic(
        self, query: str, context: str, system: str, temp: float, top_p: float, top_k: int, max_tokens: int
    ) -> str:
        """Generate using Anthropic Claude API."""
        response = await self._client.messages.create(
            model=self._config.model,
            max_tokens=max_tokens,
            temperature=temp,
            top_p=top_p,
            top_k=top_k,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": f"Answer only from the context. Include citation ids like [cite_1]. "
                    f"If the context is insufficient, say so.\n\nQuestion: {query}\n\nContext:\n{context}",
                }
            ],
        )
        return response.content[0].text

    async def _generate_gemini(
        self, query: str, context: str, system: str, temp: float, top_p: float, top_k: int, max_tokens: int
    ) -> str:
        """Generate using Google Gemini API."""
        # Gemini uses generation_config differently
        generation_config = {
            "temperature": temp,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_tokens,
        }

        prompt = f"{system}\n\nAnswer only from the context. Include citation ids like [cite_1]. "
        prompt += f"If the context is insufficient, say so.\n\nQuestion: {query}\n\nContext:\n{context}"

        response = await self._client.generate_content_async(
            prompt,
            generation_config=generation_config,
        )
        try:
            return response.text
        except ValueError:
            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
            return ""

    async def generate_source_guide(
        self,
        chunks: list[DocumentChunk],
        source_title: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> SourceGuide:
        """Generate a learning guide from source chunks."""
        combined = "\n".join(chunk.text for chunk in chunks[:8])
        temp = temperature if temperature is not None else self._config.temperature
        tokens = max_tokens if max_tokens is not None else self._config.max_tokens

        topics = self._topics(combined, limit=8)
        summary = self._summarize(combined, source_title)

        # Try to generate enhanced content if LLM is available
        if self._client is not None and len(chunks) > 2:
            try:
                summary = await self._generate_enhanced_summary(
                    chunks[:6], source_title, temp, tokens
                )
                topics = await self._generate_enhanced_topics(
                    chunks[:6], temp, tokens
                )
            except Exception:
                pass  # Fallback to extractive

        glossary = [
            {"term": topic, "definition": f"A recurring concept in {source_title or 'the selected sources'}."}
            for topic in topics[:5]
        ]
        questions = [
            f"How does {topic} relate to the rest of this workspace?" for topic in topics[:5]
        ]

        return SourceGuide(
            summary=summary,
            key_topics=topics,
            glossary=glossary,
            suggested_questions=questions,
            coverage_notes=f"Guide generated from {len(chunks)} indexed chunk(s) using {self.model_name}.",
            cache_hit=False,
        )

    async def _generate_enhanced_summary(
        self, chunks: list[DocumentChunk], source_title: str | None, temp: float, max_tokens: int
    ) -> str:
        """Generate AI-enhanced summary."""
        context = "\n\n".join(chunk.text for chunk in chunks)
        prompt = (
            "Create a concise 2-3 sentence summary of the following content. "
            "Focus on the main topics, key concepts, and purpose.\n\n" + context
        )

        if self._config.provider == ProviderType.ANTHROPIC:
            response = await self._client.messages.create(
                model=self._config.model,
                max_tokens=min(500, max_tokens),
                temperature=temp,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        elif self._config.provider == ProviderType.GEMINI:
            response = await self._client.generate_content_async(
                prompt,
                generation_config={"temperature": temp, "max_output_tokens": min(500, max_tokens)},
            )
            try:
                return response.text
            except ValueError:
                return self._summarize(context, source_title)
        else:  # NVIDIA, OpenAI
            response = await self._client.chat.completions.create(
                model=self._config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                max_tokens=min(500, max_tokens),
            )
            return response.choices[0].message.content

    async def _generate_enhanced_topics(
        self, chunks: list[DocumentChunk], temp: float, max_tokens: int
    ) -> list[str]:
        """Generate AI-enhanced topic extraction."""
        context = "\n\n".join(chunk.text for chunk in chunks)
        prompt = (
            "Extract 5-8 key topics or concepts from the following content. "
            "Return ONLY a JSON array of strings. Example: [\"Machine Learning\", \"Neural Networks\"]\n\n"
            + context
        )

        try:
            if self._config.provider == ProviderType.ANTHROPIC:
                response = await self._client.messages.create(
                    model=self._config.model,
                    max_tokens=min(300, max_tokens),
                    temperature=temp,
                    messages=[{"role": "user", "content": prompt}],
                )
                result = response.content[0].text
            elif self._config.provider == ProviderType.GEMINI:
                response = await self._client.generate_content_async(
                    prompt,
                    generation_config={"temperature": temp, "max_output_tokens": min(300, max_tokens)},
                )
                try:
                    result = response.text
                except ValueError:
                    result = ""
            else:  # NVIDIA, OpenAI
                response = await self._client.chat.completions.create(
                    model=self._config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temp,
                    max_tokens=min(300, max_tokens),
                )
                result = response.choices[0].message.content

            # Parse JSON response
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            topics = json.loads(result.strip())
            if isinstance(topics, list):
                return [str(t) for t in topics[:8]]
        except Exception:
            pass

        return self._topics("\n".join(c.text for c in chunks), limit=8)

    def _extractive_answer(self, request: GenerationRequest) -> GeneratedAnswer:
        """Fallback extractive answer generation."""
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

        answer = " ".join(sentences) or "The retrieved sources are relevant, but the evidence is too weak."
        return GeneratedAnswer(text=answer, used_citation_ids=used, model_name=self.model_name)

    def _best_sentence(self, text: str, query_terms: set[str]) -> str:
        """Find the best sentence matching query terms."""
        sentences = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
        ranked = sorted(
            sentences,
            key=lambda s: len(query_terms.intersection(re.findall(r"[A-Za-z0-9_]+", s.lower()))),
            reverse=True,
        )
        return (ranked[0] if ranked else text[:240])[:420]

    def _citation_ids(self, text: str) -> list[str]:
        """Extract citation IDs from generated text."""
        return sorted(set(re.findall(r"cite_\d+", text)))

    def _topics(self, text: str, limit: int) -> list[str]:
        """Extract topics from text."""
        stop = {"that", "with", "from", "this", "have", "will", "should", "retrieval", "source", "chunk"}
        counts: dict[str, int] = {}
        for token in re.findall(r"\b[A-Za-z][A-Za-z0-9_-]{3,}\b", text):
            lowered = token.lower()
            if lowered not in stop:
                counts[lowered] = counts.get(lowered, 0) + 1
        return [term.title() for term, _ in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]]

    def _summarize(self, text: str, source_title: str | None) -> str:
        """Simple extractive summary."""
        compact = " ".join(text.split())
        prefix = f"{source_title} covers" if source_title else "The selected sources cover"
        if not compact:
            return f"{prefix} no indexed text yet."
        return f"{prefix} {compact[:500]}{'...' if len(compact) > 500 else ''}"


class UnifiedProviderFactory:
    """Factory for creating the appropriate provider based on env config."""

    _instance: UnifiedGenerationProvider | None = None

    @classmethod
    def get_provider(cls) -> UnifiedGenerationProvider:
        """Get or create the singleton provider instance."""
        if cls._instance is None:
            cls._instance = UnifiedGenerationProvider()
        return cls._instance

    @classmethod
    def create_with_config(cls, config: LLMConfig) -> UnifiedGenerationProvider:
        """Create a new provider with specific config."""
        return UnifiedGenerationProvider(config)

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance."""
        cls._instance = None
