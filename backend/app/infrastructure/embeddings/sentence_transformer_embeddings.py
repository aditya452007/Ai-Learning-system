"""Embedding adapters with a deterministic local fallback."""

from __future__ import annotations

import hashlib
import math
import re


class HashingEmbeddingProvider:
    """Fast local embedding fallback based on signed feature hashing."""

    def __init__(self, dimensions: int = 384, model_name: str = "local-hashing-384") -> None:
        self.dimensions = dimensions
        self._model_name = model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[A-Za-z0-9_]+", text.lower())
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            value = int.from_bytes(digest, "big")
            index = value % self.dimensions
            sign = 1.0 if value & 1 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(item * item for item in vector)) or 1.0
        return [item / norm for item in vector]


class SentenceTransformerEmbeddingProvider:
    """sentence-transformers adapter, falling back to hashing if unavailable."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._fallback = HashingEmbeddingProvider(model_name="local-hashing-384")
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception:
            self._model = None
        else:
            self._model = SentenceTransformer(model_name)

    @property
    def model_name(self) -> str:
        return self._model_name if self._model is not None else self._fallback.model_name

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self._model is None:
            return self._fallback.embed_texts(texts)
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return [list(map(float, vector)) for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

