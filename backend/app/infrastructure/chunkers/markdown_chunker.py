"""Markdown chunker preserving the active heading path."""

from __future__ import annotations

import re

from app.domain.models.document_chunk import ChunkLocation, DocumentChunk
from app.domain.models.source_document import LoadedSource, SourceDocument
from app.domain.services.chunk_hashing import chunk_hash
from app.infrastructure.chunkers.recursive_text_chunker import RecursiveTextChunker


class MarkdownChunker(RecursiveTextChunker):
    """Markdown-aware chunker preserving heading structure."""

    version = "markdown-v2"

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def chunk(self, source: SourceDocument, loaded: LoadedSource) -> list[DocumentChunk]:
        """Chunk markdown preserving heading hierarchy."""
        sections = self._sections(loaded.text)
        chunks: list[DocumentChunk] = []
        for section_text, heading, start_line, end_line in sections:
            pseudo_loaded = LoadedSource(
                title=loaded.title,
                source_type=loaded.source_type,
                uri=loaded.uri,
                text=section_text,
                content_hash=loaded.content_hash,
                metadata=loaded.metadata,
            )
            section_chunks = super().chunk(source, pseudo_loaded)
            for chunk in section_chunks:
                ordinal = len(chunks)
                chunk.location = ChunkLocation(heading=heading, line_start=start_line, line_end=end_line)
                chunk.metadata["heading"] = heading
                chunk.metadata["ordinal"] = ordinal
                chunk.chunk_hash = chunk_hash(source.content_hash, chunk.text, ordinal, self.version)
                chunks.append(chunk)
        return chunks

    def _sections(self, text: str) -> list[tuple[str, str | None, int, int]]:
        sections: list[tuple[str, str | None, int, int]] = []
        heading_path: list[str] = []
        buffer: list[str] = []
        section_heading: str | None = None
        start_line = 1

        def flush(end_line: int) -> None:
            nonlocal buffer, section_heading, start_line
            if buffer:
                sections.append(("\n".join(buffer).strip(), section_heading, start_line, end_line))
                buffer = []

        for line_number, line in enumerate(text.splitlines(), start=1):
            match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if match:
                flush(line_number - 1)
                level = len(match.group(1))
                heading_path[:] = heading_path[: level - 1]
                heading_path.append(match.group(2))
                section_heading = " > ".join(heading_path)
                start_line = line_number
            buffer.append(line)
        flush(len(text.splitlines()) or 1)
        return sections or [(text, None, 1, len(text.splitlines()) or 1)]

