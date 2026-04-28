"""Base loader safety contract."""

from __future__ import annotations

from pathlib import Path

from app.domain.models.exceptions import SourceLoadError
from app.domain.models.source_document import LoadedSource, SourceInput, SourceType
from app.domain.services.chunk_hashing import sha256_text


class BaseLoader:
    source_type: SourceType

    async def load(self, source_input: SourceInput) -> LoadedSource:
        try:
            text, metadata = await self.extract_text(source_input)
        except Exception as exc:
            raise SourceLoadError(f"Failed to load {source_input.uri}: {exc}") from exc
        clean_text = self._clean_text(text)
        if not clean_text:
            raise SourceLoadError(f"No text could be extracted from {source_input.uri}")
        title = source_input.title or Path(source_input.uri).name or source_input.uri
        content_hash = sha256_text(f"{source_input.uri}\n{clean_text}")
        metadata = {**metadata, **source_input.metadata, "loader": type(self).__name__}
        return LoadedSource(
            title=title,
            source_type=self.source_type,
            uri=source_input.uri,
            text=clean_text,
            content_hash=content_hash,
            metadata=metadata,
        )

    async def extract_text(self, source_input: SourceInput) -> tuple[str, dict[str, object]]:
        raise NotImplementedError

    def _clean_text(self, text: str) -> str:
        lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
        return "\n".join(lines).strip()

