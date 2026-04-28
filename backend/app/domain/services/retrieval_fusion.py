"""Deterministic retrieval fusion services."""

from __future__ import annotations

from dataclasses import replace

from app.domain.models.retrieval import RetrievalResult


class ReciprocalRankFusionService:
    """Fuse ranked lists without assuming score scales are comparable."""

    def __init__(self, rank_constant: int = 60) -> None:
        self.rank_constant = rank_constant

    def fuse(self, result_sets: list[list[RetrievalResult]], top_k: int) -> list[RetrievalResult]:
        scores: dict[str, float] = {}
        first_seen: dict[str, RetrievalResult] = {}
        contributors: dict[str, set[str]] = {}

        for results in result_sets:
            for result in results:
                scores[result.chunk_id] = scores.get(result.chunk_id, 0.0) + 1.0 / (
                    self.rank_constant + result.rank
                )
                first_seen.setdefault(result.chunk_id, result)
                contributors.setdefault(result.chunk_id, set()).add(result.retriever)

        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
        fused: list[RetrievalResult] = []
        for rank, (chunk_id, score) in enumerate(ordered, start=1):
            base = first_seen[chunk_id]
            metadata = dict(base.metadata)
            metadata["contributors"] = sorted(contributors[chunk_id])
            fused.append(
                replace(
                    base,
                    score=score,
                    rank=rank,
                    retriever="hybrid",
                    metadata=metadata,
                )
            )
        return fused

