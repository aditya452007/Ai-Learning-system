"""Persistent BM25 keyword retrieval adapter."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.retrieval import RetrievalResult


class Bm25Store:
    def __init__(self, root_dir: Path, k1: float = 1.5, b: float = 0.75) -> None:
        self.root_dir = root_dir
        self.k1 = k1
        self.b = b
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def build(self, workspace_id: str, chunks: list[DocumentChunk]) -> None:
        documents: list[dict[str, Any]] = []
        document_frequency: Counter[str] = Counter()
        for chunk in chunks:
            tokens = self._tokens(chunk.text)
            counts = Counter(tokens)
            document_frequency.update(counts.keys())
            documents.append(
                {
                    "chunk_id": chunk.id,
                    "source_id": chunk.source_id,
                    "text": chunk.text,
                    "length": len(tokens),
                    "term_frequency": dict(counts),
                    "metadata": dict(chunk.metadata),
                }
            )
        index = {
            "documents": documents,
            "document_frequency": dict(document_frequency),
            "average_length": sum(doc["length"] for doc in documents) / max(len(documents), 1),
            "document_count": len(documents),
        }
        self._write(self._path(workspace_id), index)

    def search(self, workspace_id: str, query: str, top_k: int) -> list[RetrievalResult]:
        index = self._read(self._path(workspace_id))
        if not index:
            return []
        query_terms = self._tokens(query)
        scored: list[tuple[float, dict[str, Any]]] = []
        for document in index["documents"]:
            score = self._score(document, query_terms, index)
            if score > 0:
                scored.append((score, document))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievalResult(
                chunk_id=document["chunk_id"],
                source_id=document["source_id"],
                score=float(score),
                rank=rank,
                retriever="keyword",
                excerpt=self._excerpt(document["text"]),
                metadata=dict(document.get("metadata", {})),
            )
            for rank, (score, document) in enumerate(scored[:top_k], start=1)
        ]

    def clear(self, workspace_id: str) -> None:
        path = self._path(workspace_id)
        if path.exists():
            path.unlink()

    def _score(self, document: dict[str, Any], query_terms: list[str], index: dict[str, Any]) -> float:
        score = 0.0
        average_length = float(index["average_length"]) or 1.0
        document_count = int(index["document_count"])
        for term in query_terms:
            tf = int(document["term_frequency"].get(term, 0))
            if tf == 0:
                continue
            df = int(index["document_frequency"].get(term, 0))
            idf = math.log(1 + (document_count - df + 0.5) / (df + 0.5))
            denominator = tf + self.k1 * (1 - self.b + self.b * document["length"] / average_length)
            score += idf * (tf * (self.k1 + 1)) / denominator
        return score

    def _tokens(self, text: str) -> list[str]:
        return re.findall(r"[A-Za-z0-9_]+", text.lower())

    def _path(self, workspace_id: str) -> Path:
        return self.root_dir / workspace_id / "bm25_index.json"

    def _read(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, path: Path, value: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def _excerpt(self, text: str, limit: int = 360) -> str:
        compact = " ".join(text.split())
        return compact[:limit] + ("..." if len(compact) > limit else "")

