"""Structure-aware text chunking using LangChain RecursiveCharacterTextSplitter.

Based on working implementation from Multi_Rag.ipynb.
Uses LangChain for robust chunking with configurable separators and overlap.
"""

from __future__ import annotations

from app.domain.models.document_chunk import ChunkLocation, DocumentChunk
from app.domain.models.source_document import LoadedSource, SourceDocument
from app.domain.services.chunk_hashing import chunk_hash
from app.infrastructure.config.settings import Settings


class RecursiveTextChunker:
    """
    Text chunker using LangChain RecursiveCharacterTextSplitter.

    Uses intelligent separators to preserve semantic boundaries
    while maintaining chunk size constraints.
    """

    version = "recursive-text-v2"

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        """
        Initialize chunker.

        Args:
            chunk_size: Target chunk size (default from settings)
            chunk_overlap: Overlap between chunks (default from settings)
        """
        # Use settings defaults if not provided
        settings = Settings.from_env()
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self._splitter = self._create_splitter()

    def _create_splitter(self):
        """Create LangChain text splitter with optimal separators."""
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
        except ImportError as e:
            raise ImportError(
                "langchain-text-splitters required. "
                "Install with: pip install langchain-text-splitters"
            ) from e

        # Separators in order of priority (try to keep semantic units)
        separators = [
            "\n\n=== NEW PAGE ===\n\n",  # Page markers from web extraction
            "\n\n",  # Paragraph breaks
            "\n",   # Line breaks
            ".",    # Sentences
            " ",    # Words
            "",     # Characters (fallback)
        ]

        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=separators,
            length_function=len,  # Character-based length
            is_separator_regex=False,
        )

    def chunk(self, source: SourceDocument, loaded: LoadedSource) -> list[DocumentChunk]:
        """
        Chunk loaded source text into traceable document chunks.

        Args:
            source: Source document metadata
            loaded: Loaded source with text content

        Returns:
            List of document chunks with location metadata
        """
        text = loaded.text
        if not text.strip():
            return []

        # Split text using LangChain
        split_texts = self._splitter.split_text(text)

        chunks: list[DocumentChunk] = []
        lines = text.splitlines()

        for ordinal, chunk_text in enumerate(split_texts):
            # Find line position for this chunk
            line_start, line_end = self._find_line_range(lines, chunk_text, ordinal)

            # Clean chunk text
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue

            chunk = DocumentChunk.create(
                workspace_id=source.workspace_id,
                source_id=source.id,
                text=chunk_text,
                chunk_hash=chunk_hash(source.content_hash, chunk_text, ordinal, self.version),
                token_count=self._token_count(chunk_text),
                location=ChunkLocation(line_start=line_start, line_end=line_end),
                metadata={
                    "chunker": self.version,
                    "ordinal": ordinal,
                    "chunk_size": len(chunk_text),
                },
            )
            chunks.append(chunk)

        return chunks

    def _find_line_range(
        self,
        all_lines: list[str],
        chunk_text: str,
        ordinal: int,
    ) -> tuple[int, int]:
        """
        Find approximate line range for a chunk.

        Args:
            all_lines: All lines in source
            chunk_text: Chunk text to locate
            ordinal: Chunk ordinal for fallback

        Returns:
            (start_line, end_line) tuple
        """
        if not all_lines:
            return (ordinal * 10 + 1, ordinal * 10 + 10)

        # Try to find by content matching
        chunk_start = chunk_text[:50].strip() if len(chunk_text) > 50 else chunk_text.strip()

        # Estimate based on chunk position
        total_lines = len(all_lines)
        est_start = min(ordinal * (total_lines // max(1, ordinal + 1)) + 1, total_lines)
        est_end = min(est_start + 20, total_lines)

        return (est_start, est_end)

    def _token_count(self, text: str) -> int:
        """Rough token count estimate."""
        import re
        return len(re.findall(r"\w+|[^\w\s]", text))
