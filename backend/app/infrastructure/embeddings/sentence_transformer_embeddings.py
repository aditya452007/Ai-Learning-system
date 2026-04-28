"""Modern embedding adapters using SentenceTransformers.

Based on working implementation from Multi_Rag.ipynb.
Uses SentenceTransformer with proper GPU/CPU handling and normalization.
"""

from __future__ import annotations

import hashlib
import logging
import math
import re
from typing import Any

from app.domain.ports.embedding_provider import EmbeddingProviderPort

logger = logging.getLogger(__name__)


class SentenceTransformerEmbeddingProvider(EmbeddingProviderPort):
    """
    Modern sentence-transformers adapter with GPU support.
    Uses cached model loading and efficient batch encoding.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str | None = None,
        normalize_embeddings: bool = True,
    ) -> None:
        """
        Initialize embedding provider.

        Args:
            model_name: HuggingFace model name
            device: Device to use (cuda/cpu), auto-detected if None
            normalize_embeddings: Whether to L2-normalize embeddings
        """
        self._model_name = model_name
        self._normalize = normalize_embeddings
        self._device = device or self._auto_device()
        self._model: Any | None = None

    def _auto_device(self) -> str:
        """Auto-detect best available device."""
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    def _load_model(self) -> Any:
        """Lazy load the SentenceTransformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info(f"Loading embedding model {self._model_name} on {self._device}")
                self._model = SentenceTransformer(
                    self._model_name,
                    device=self._device,
                )
            except ImportError as e:
                logger.error(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
                raise ImportError("sentence-transformers required") from e
        return self._model

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Embed multiple texts efficiently in batches.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        model = self._load_model()

        # Encode with normalization
        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=self._normalize,
            show_progress_bar=False,
        )

        # Convert to list of lists
        return [list(map(float, embedding)) for embedding in embeddings]

    def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query text.

        Args:
            text: Query text

        Returns:
            Embedding vector
        """
        return self.embed_texts([text])[0]


class HashingEmbeddingProvider(EmbeddingProviderPort):
    """
    Fallback deterministic embedding using feature hashing.
    Used when SentenceTransformer is not available.
    """

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
