"""Persistent vector store adapter.

The class name is intentionally FAISS-compatible for the architecture contract.
For the MVP it uses a JSON-backed normalized inner-product index so tests and
local demos run without compiled FAISS wheels. A future implementation can swap
the internals without changing application code.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.retrieval import RetrievalResult


class FaissVectorStore:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def upsert(self, workspace_id: str, chunks: list[DocumentChunk], vectors: list[list[float]]) -> None:
        path = self._path(workspace_id)
        existing = self._read(path)
        by_id = {item["chunk_id"]: item for item in existing}
        for chunk, vector in zip(chunks, vectors, strict=True):
            by_id[chunk.id] = {
                "chunk_id": chunk.id,
                "source_id": chunk.source_id,
                "text": chunk.text,
                "vector": self._normalize(vector),
                "metadata": {
                    "location": asdict(chunk.location),
                    **chunk.metadata,
                },
            }
        self._write(path, list(by_id.values()))

    def search(self, workspace_id: str, query_vector: list[float], top_k: int) -> list[RetrievalResult]:
        query = self._normalize(query_vector)
        scored: list[tuple[float, dict[str, Any]]] = []
        for item in self._read(self._path(workspace_id)):
            score = sum(a * b for a, b in zip(query, item["vector"], strict=False))
            scored.append((score, item))
        scored.sort(key=lambda item: item[0], reverse=True)
        results: list[RetrievalResult] = []
        for rank, (score, item) in enumerate(scored[:top_k], start=1):
            results.append(
                RetrievalResult(
                    chunk_id=item["chunk_id"],
                    source_id=item["source_id"],
                    score=float(score),
                    rank=rank,
                    retriever="semantic",
                    excerpt=self._excerpt(item["text"]),
                    metadata=dict(item.get("metadata", {})),
                )
            )
        return results

    def clear(self, workspace_id: str) -> None:
        path = self._path(workspace_id)
        if path.exists():
            path.unlink()

    def _path(self, workspace_id: str) -> Path:
        return self.root_dir / workspace_id / "vector_index.json"

    def _read(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, path: Path, items: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")

    def _normalize(self, vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(item * item for item in vector)) or 1.0
        return [float(item) / norm for item in vector]

    def _excerpt(self, text: str, limit: int = 360) -> str:
        compact = " ".join(text.split())
        return compact[:limit] + ("..." if len(compact) > limit else "")

