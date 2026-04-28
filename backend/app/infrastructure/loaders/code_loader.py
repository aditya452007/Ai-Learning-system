"""Basic source code loader for later repository ingestion."""

from __future__ import annotations

from pathlib import Path

from app.domain.models.source_document import SourceInput, SourceType
from app.infrastructure.loaders.base_loader import BaseLoader


class CodeLoader(BaseLoader):
    source_type = SourceType.CODE

    async def extract_text(self, source_input: SourceInput) -> tuple[str, dict[str, object]]:
        path = Path(source_input.path or source_input.uri)
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text, {"size_bytes": path.stat().st_size, "language": path.suffix.lstrip(".")}

