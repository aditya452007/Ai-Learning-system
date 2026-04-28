"""Grounded question answering use case."""

from __future__ import annotations

import time
from dataclasses import asdict

from app.application.services.citation_verifier import CitationVerifier
from app.application.services.context_builder import ContextBuilder
from app.application.services.query_planner import QueryPlanner
from app.domain.models.answer import Answer
from app.domain.models.retrieval import RetrievalDiagnostics, RetrievalMode, RetrievalQuery, RetrievalResult
from app.domain.ports.cache_store import CacheStorePort
from app.domain.ports.embedding_provider import EmbeddingProviderPort
from app.domain.ports.generation_provider import GenerationProviderPort, GenerationRequest
from app.domain.ports.graph_store import GraphStorePort
from app.domain.ports.keyword_store import KeywordStorePort
from app.domain.ports.vector_store import VectorStorePort
from app.domain.ports.workspace_repository import WorkspaceRepositoryPort
from app.domain.services.retrieval_fusion import ReciprocalRankFusionService
from app.domain.services.chunk_hashing import stable_json_hash
from app.infrastructure.generation.prompt_templates import ANSWER_PROMPT_VERSION


class AskQuestion:
    def __init__(
        self,
        repository: WorkspaceRepositoryPort,
        embedding_provider: EmbeddingProviderPort,
        vector_store: VectorStorePort,
        keyword_store: KeywordStorePort,
        graph_store: GraphStorePort,
        generation_provider: GenerationProviderPort,
        cache_store: CacheStorePort,
        query_planner: QueryPlanner,
        fusion_service: ReciprocalRankFusionService,
        context_builder: ContextBuilder,
        citation_verifier: CitationVerifier,
    ) -> None:
        self.repository = repository
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.keyword_store = keyword_store
        self.graph_store = graph_store
        self.generation_provider = generation_provider
        self.cache_store = cache_store
        self.query_planner = query_planner
        self.fusion_service = fusion_service
        self.context_builder = context_builder
        self.citation_verifier = citation_verifier

    async def execute(self, query: RetrievalQuery) -> Answer:
        started = time.perf_counter()
        workspace = self.repository.get_workspace(query.workspace_id)
        planned_mode = self.query_planner.plan(query.text, query.mode)
        cache_key = self._answer_cache_key(query.text, planned_mode, workspace.index_version, query.top_k)
        cached_answer = self.cache_store.get_json("answers", cache_key)
        if isinstance(cached_answer, dict):
            answer = self._answer_from_cache(cached_answer, planned_mode)
            answer.diagnostics.answer_cache_hit = True
            answer.diagnostics.latency_ms = int((time.perf_counter() - started) * 1000)
            return answer

        retrieval_results, diagnostics = self._retrieve(query, planned_mode, workspace.index_version)
        sources = self.repository.list_sources(query.workspace_id)
        chunks = self.repository.list_chunks(query.workspace_id)
        selected_chunks, citations = self.context_builder.build(retrieval_results, chunks, sources)

        generated = await self.generation_provider.generate_answer(
            GenerationRequest(
                query=query.text,
                chunks=selected_chunks,
                citations=[citation.citation_id for citation in citations],
                workspace_name=workspace.name,
            )
        )
        verified = self.citation_verifier.verified_citations(generated.text, citations, generated.used_citation_ids)
        if selected_chunks and not verified:
            generated.text = "I found related source material, but could not verify citations strongly enough to answer."
        diagnostics.latency_ms = int((time.perf_counter() - started) * 1000)
        answer = Answer(
            answer=generated.text,
            retrieval_mode=planned_mode,
            citations=verified,
            diagnostics=diagnostics,
            metadata={"model_name": generated.model_name},
        )
        if verified:
            self.cache_store.set_json("answers", cache_key, self._answer_to_cache(answer))
        return answer

    def _retrieve(
        self,
        query: RetrievalQuery,
        planned_mode: RetrievalMode,
        index_version: int,
    ) -> tuple[list[RetrievalResult], RetrievalDiagnostics]:
        diagnostics = RetrievalDiagnostics(planned_mode=planned_mode)
        retrieval_key = stable_json_hash(
            {
                "workspace_id": query.workspace_id,
                "query": query.text.strip().lower(),
                "mode": planned_mode.value,
                "top_k": query.top_k,
                "index_version": index_version,
            }
        )
        cached = self.cache_store.get_json("retrieval", retrieval_key)
        if isinstance(cached, list):
            results = [RetrievalResult(**item) for item in cached]
            diagnostics.retrieval_cache_hit = True
            diagnostics.fused_hits = len(results)
            return results, diagnostics

        semantic_results: list[RetrievalResult] = []
        keyword_results: list[RetrievalResult] = []
        graph_results: list[RetrievalResult] = []

        if planned_mode in {RetrievalMode.SEMANTIC, RetrievalMode.HYBRID}:
            query_vector = self.embedding_provider.embed_query(query.text)
            semantic_results = self.vector_store.search(query.workspace_id, query_vector, max(query.top_k * 2, 12))
        if planned_mode in {RetrievalMode.KEYWORD, RetrievalMode.HYBRID}:
            keyword_results = self.keyword_store.search(query.workspace_id, query.text, max(query.top_k * 2, 12))
        if planned_mode == RetrievalMode.GRAPH:
            graph_results = self.graph_store.search(query.workspace_id, query.text, query.top_k)

        diagnostics.semantic_hits = len(semantic_results)
        diagnostics.keyword_hits = len(keyword_results)
        diagnostics.graph_hits = len(graph_results)

        if planned_mode == RetrievalMode.SEMANTIC:
            results = semantic_results[: query.top_k]
        elif planned_mode == RetrievalMode.KEYWORD:
            results = keyword_results[: query.top_k]
        elif planned_mode == RetrievalMode.GRAPH:
            results = graph_results[: query.top_k]
        else:
            results = self.fusion_service.fuse([semantic_results, keyword_results], query.top_k)

        diagnostics.fused_hits = len(results)
        self.cache_store.set_json("retrieval", retrieval_key, [asdict(result) for result in results])
        return results, diagnostics

    def _answer_cache_key(self, query: str, mode: RetrievalMode, index_version: int, top_k: int) -> str:
        return stable_json_hash(
            {
                "query": query.strip().lower(),
                "mode": mode.value,
                "index_version": index_version,
                "top_k": top_k,
                "prompt_version": ANSWER_PROMPT_VERSION,
                "model_name": self.generation_provider.model_name,
            }
        )

    def _answer_to_cache(self, answer: Answer) -> dict[str, object]:
        return {
            "answer": answer.answer,
            "retrieval_mode": answer.retrieval_mode.value,
            "citations": [asdict(citation) for citation in answer.citations],
            "diagnostics": asdict(answer.diagnostics) | {"planned_mode": answer.diagnostics.planned_mode.value},
            "metadata": answer.metadata,
        }

    def _answer_from_cache(self, value: dict[str, object], mode: RetrievalMode) -> Answer:
        from app.domain.models.answer import Citation

        diagnostics_value = dict(value["diagnostics"])  # type: ignore[arg-type]
        diagnostics_value["planned_mode"] = RetrievalMode(diagnostics_value.get("planned_mode", mode.value))
        return Answer(
            answer=str(value["answer"]),
            retrieval_mode=mode,
            citations=[Citation(**item) for item in value.get("citations", [])],  # type: ignore[arg-type]
            diagnostics=RetrievalDiagnostics(**diagnostics_value),
            metadata=dict(value.get("metadata", {})),  # type: ignore[arg-type]
        )
