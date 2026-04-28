"""Embedding cache decorator."""

from __future__ import annotations

from app.domain.ports.cache_store import CacheStorePort
from app.domain.ports.embedding_provider import EmbeddingProviderPort
from app.domain.services.chunk_hashing import sha256_text, stable_json_hash


class CachedEmbeddingProvider:
    def __init__(self, provider: EmbeddingProviderPort, cache_store: CacheStorePort) -> None:
        self.provider = provider
        self.cache_store = cache_store

    @property
    def model_name(self) -> str:
        return self.provider.model_name

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float] | None] = []
        missing_texts: list[str] = []
        missing_indexes: list[int] = []
        for index, text in enumerate(texts):
            key = self._key(text)
            cached = self.cache_store.get_json("embeddings", key)
            if isinstance(cached, list):
                vectors.append([float(item) for item in cached])
            else:
                vectors.append(None)
                missing_texts.append(text)
                missing_indexes.append(index)

        if missing_texts:
            fresh_vectors = self.provider.embed_texts(missing_texts)
            for local_index, vector in zip(missing_indexes, fresh_vectors, strict=True):
                vectors[local_index] = vector
                self.cache_store.set_json("embeddings", self._key(texts[local_index]), vector)

        return [vector for vector in vectors if vector is not None]

    def embed_query(self, text: str) -> list[float]:
        key = stable_json_hash({"model": self.model_name, "query": sha256_text(text)})
        cached = self.cache_store.get_json("query_embeddings", key)
        if isinstance(cached, list):
            return [float(item) for item in cached]
        vector = self.provider.embed_query(text)
        self.cache_store.set_json("query_embeddings", key, vector)
        return vector

    def _key(self, text: str) -> str:
        return stable_json_hash({"model": self.model_name, "text_hash": sha256_text(text)})

