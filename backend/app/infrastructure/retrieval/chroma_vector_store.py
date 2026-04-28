"""ChromaDB vector store adapter for modern embeddings.

Uses ChromaDB as a persistent vector database with automatic embedding management.
Supports both local SentenceTransformer embeddings and API-based embeddings.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.retrieval import RetrievalResult
from app.domain.ports.vector_store import VectorStorePort

logger = logging.getLogger(__name__)


class ChromaVectorStore(VectorStorePort):
    """
    ChromaDB vector store implementation.
    Provides persistent storage with efficient similarity search.
    """

    def __init__(
        self,
        persist_dir: Path,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        collection_name_prefix: str = "workspace",
    ) -> None:
        """
        Initialize ChromaDB store.

        Args:
            persist_dir: Directory for ChromaDB persistence
            embedding_model: Name of the sentence-transformer model
            collection_name_prefix: Prefix for collection names
        """
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_model = embedding_model
        self.collection_name_prefix = collection_name_prefix
        self._client: Any | None = None
        self._embeddings: Any | None = None

    def _get_client(self) -> Any:
        """Lazy initialization of ChromaDB client."""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings

                self._client = chromadb.PersistentClient(
                    path=str(self.persist_dir),
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                    ),
                )
            except ImportError as e:
                logger.error("ChromaDB not installed. Install with: pip install chromadb")
                raise ImportError("ChromaDB required") from e
        return self._client

    def _get_embeddings(self) -> Any:
        """Lazy initialization of embedding function."""
        if self._embeddings is None:
            try:
                from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

                self._embeddings = SentenceTransformerEmbeddingFunction(
                    model_name=self.embedding_model,
                )
            except ImportError as e:
                logger.error("ChromaDB embedding functions not available")
                raise ImportError("ChromaDB embedding functions required") from e
        return self._embeddings

    def _collection_name(self, workspace_id: str) -> str:
        """Generate collection name from workspace ID."""
        # Sanitize workspace_id for ChromaDB collection name
        safe_id = "".join(c if c.isalnum() else "_" for c in workspace_id)
        return f"{self.collection_name_prefix}_{safe_id}"

    def upsert(
        self,
        workspace_id: str,
        chunks: list[DocumentChunk],
        vectors: list[list[float]] | None = None,
    ) -> None:
        """
        Upsert chunks into ChromaDB collection.
        If vectors are provided, use them; otherwise let ChromaDB generate embeddings.

        Args:
            workspace_id: Target workspace
            chunks: List of document chunks
            vectors: Optional pre-computed embeddings
        """
        if not chunks:
            return

        collection_name = self._collection_name(workspace_id)
        client = self._get_client()

        # Get or create collection
        if vectors is not None:
            # Using provided embeddings - create collection without embedding function
            collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"embedding_model": self.embedding_model},
            )
        else:
            # Let ChromaDB handle embeddings
            collection = client.get_or_create_collection(
                name=collection_name,
                embedding_function=self._get_embeddings(),
                metadata={"embedding_model": self.embedding_model},
            )

        # Prepare data
        ids = [chunk.id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "source_id": chunk.source_id,
                "workspace_id": chunk.workspace_id,
                "chunk_hash": chunk.chunk_hash,
                "token_count": chunk.token_count,
                "location_label": chunk.location.label(),
                **chunk.metadata,
            }
            for chunk in chunks
        ]

        # Upsert with or without embeddings
        if vectors is not None:
            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=vectors,
            )
        else:
            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )

        logger.info(f"Upserted {len(chunks)} chunks to ChromaDB collection {collection_name}")

    def search(
        self,
        workspace_id: str,
        query_vector: list[float],
        top_k: int,
    ) -> list[RetrievalResult]:
        """
        Search for similar chunks using the query vector.

        Args:
            workspace_id: Target workspace
            query_vector: Query embedding vector
            top_k: Number of results

        Returns:
            List of retrieval results
        """
        collection_name = self._collection_name(workspace_id)
        client = self._get_client()

        try:
            collection = client.get_collection(name=collection_name)
        except Exception:
            logger.warning(f"Collection {collection_name} not found")
            return []

        # Query with embeddings
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["metadatas", "documents", "distances"],
        )

        # Build retrieval results
        retrieval_results: list[RetrievalResult] = []

        if not results["ids"] or not results["ids"][0]:
            return retrieval_results

        for rank, (chunk_id, metadata, document, distance) in enumerate(
            zip(
                results["ids"][0],
                results["metadatas"][0],
                results["documents"][0],
                results["distances"][0],
            ),
            start=1,
        ):
            # Convert cosine distance to similarity score (1 - distance for normalized vectors)
            score = 1.0 - float(distance)

            retrieval_results.append(
                RetrievalResult(
                    chunk_id=str(chunk_id),
                    source_id=str(metadata.get("source_id", "")),
                    score=score,
                    rank=rank,
                    retriever="semantic",
                    excerpt=str(document)[:360] + "..." if len(str(document)) > 360 else str(document),
                    metadata=dict(metadata),
                )
            )

        return retrieval_results

    def clear(self, workspace_id: str) -> None:
        """Clear all data for a workspace."""
        collection_name = self._collection_name(workspace_id)
        client = self._get_client()

        try:
            client.delete_collection(name=collection_name)
            logger.info(f"Deleted ChromaDB collection {collection_name}")
        except Exception as e:
            logger.warning(f"Could not delete collection {collection_name}: {e}")

    def search_by_text(
        self,
        workspace_id: str,
        query_text: str,
        top_k: int,
    ) -> list[RetrievalResult]:
        """
        Search using text query (let ChromaDB handle embedding).

        Args:
            workspace_id: Target workspace
            query_text: Query text
            top_k: Number of results

        Returns:
            List of retrieval results
        """
        collection_name = self._collection_name(workspace_id)
        client = self._get_client()

        try:
            collection = client.get_collection(
                name=collection_name,
                embedding_function=self._get_embeddings(),
            )
        except Exception:
            logger.warning(f"Collection {collection_name} not found")
            return []

        results = collection.query(
            query_texts=[query_text],
            n_results=top_k,
            include=["metadatas", "documents", "distances"],
        )

        retrieval_results: list[RetrievalResult] = []

        if not results["ids"] or not results["ids"][0]:
            return retrieval_results

        for rank, (chunk_id, metadata, document, distance) in enumerate(
            zip(
                results["ids"][0],
                results["metadatas"][0],
                results["documents"][0],
                results["distances"][0],
            ),
            start=1,
        ):
            score = 1.0 - float(distance)
            retrieval_results.append(
                RetrievalResult(
                    chunk_id=str(chunk_id),
                    source_id=str(metadata.get("source_id", "")),
                    score=score,
                    rank=rank,
                    retriever="semantic",
                    excerpt=str(document)[:360] + "..." if len(str(document)) > 360 else str(document),
                    metadata=dict(metadata),
                )
            )

        return retrieval_results
