"""Structure-aware text chunking with overlap and location metadata."""

from __future__ import annotations

import re

from app.domain.models.document_chunk import ChunkLocation, DocumentChunk
from app.domain.models.source_document import LoadedSource, SourceDocument
from app.domain.services.chunk_hashing import chunk_hash


class RecursiveTextChunker:
    version = "recursive-text-v1"

    def __init__(self, chunk_size_tokens: int = 700, overlap_tokens: int = 100) -> None:
        self.chunk_size_tokens = chunk_size_tokens
        self.overlap_tokens = min(overlap_tokens, max(chunk_size_tokens // 3, 1))

    def chunk(self, source: SourceDocument, loaded: LoadedSource) -> list[DocumentChunk]:
        paragraphs = self._paragraphs(loaded.text)
        chunks: list[DocumentChunk] = []
        current: list[str] = []
        current_tokens = 0
        current_line = 1
        start_line = 1

        for paragraph, line_number in paragraphs:
            tokens = self._token_count(paragraph)
            if current and current_tokens + tokens > self.chunk_size_tokens:
                chunks.append(self._make_chunk(source, current, len(chunks), start_line, line_number - 1))
                overlap = self._overlap_text(current)
                current = [overlap] if overlap else []
                current_tokens = self._token_count(overlap)
                start_line = max(current_line, line_number - 1)
            if not current:
                start_line = line_number
            current.append(paragraph)
            current_tokens += tokens
            current_line = line_number

        if current:
            chunks.append(self._make_chunk(source, current, len(chunks), start_line, current_line))
        return chunks

    def _make_chunk(
        self,
        source: SourceDocument,
        parts: list[str],
        ordinal: int,
        line_start: int,
        line_end: int,
    ) -> DocumentChunk:
        text = "\n\n".join(part for part in parts if part).strip()
        return DocumentChunk.create(
            workspace_id=source.workspace_id,
            source_id=source.id,
            text=text,
            chunk_hash=chunk_hash(source.content_hash, text, ordinal, self.version),
            token_count=self._token_count(text),
            location=ChunkLocation(line_start=line_start, line_end=line_end),
            metadata={"chunker": self.version, "ordinal": ordinal},
        )

    def _paragraphs(self, text: str) -> list[tuple[str, int]]:
        parts: list[tuple[str, int]] = []
        buffer: list[str] = []
        start_line = 1
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.strip():
                if not buffer:
                    start_line = line_number
                buffer.append(line)
            elif buffer:
                parts.append(("\n".join(buffer), start_line))
                buffer = []
        if buffer:
            parts.append(("\n".join(buffer), start_line))
        if not parts and text.strip():
            parts.append((text.strip(), 1))
        return parts

    def _token_count(self, text: str) -> int:
        return len(re.findall(r"\w+|[^\w\s]", text))

    def _overlap_text(self, parts: list[str]) -> str:
        tokens = re.findall(r"\S+", "\n\n".join(parts))
        if not tokens:
            return ""
        return " ".join(tokens[-self.overlap_tokens :])

