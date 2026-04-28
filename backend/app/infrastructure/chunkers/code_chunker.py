"""Simple code chunker that keeps class/function blocks visible."""

from __future__ import annotations

import re

from app.domain.models.document_chunk import ChunkLocation, DocumentChunk
from app.domain.models.source_document import LoadedSource, SourceDocument
from app.domain.services.chunk_hashing import chunk_hash


class CodeChunker:
    version = "code-basic-v1"

    def chunk(self, source: SourceDocument, loaded: LoadedSource) -> list[DocumentChunk]:
        lines = loaded.text.splitlines()
        boundaries = [idx for idx, line in enumerate(lines) if re.match(r"^\s*(class|def|function)\s+\w+", line)]
        boundaries = boundaries or list(range(0, len(lines), 80))
        chunks: list[DocumentChunk] = []
        for ordinal, start in enumerate(boundaries):
            end = boundaries[ordinal + 1] if ordinal + 1 < len(boundaries) else min(len(lines), start + 120)
            text = "\n".join(lines[start:end]).strip()
            if not text:
                continue
            chunks.append(
                DocumentChunk.create(
                    workspace_id=source.workspace_id,
                    source_id=source.id,
                    text=text,
                    chunk_hash=chunk_hash(source.content_hash, text, ordinal, self.version),
                    token_count=len(re.findall(r"\w+|[^\w\s]", text)),
                    location=ChunkLocation(line_start=start + 1, line_end=end),
                    metadata={"chunker": self.version, "ordinal": ordinal},
                )
            )
        return chunks

