"""Unified loader that routes source inputs to specialist loaders."""

from __future__ import annotations

from pathlib import Path

from app.domain.models.exceptions import UnsupportedSourceError
from app.domain.models.source_document import LoadedSource, SourceInput, SourceType
from app.infrastructure.loaders.base_loader import BaseLoader


class UnifiedLoader:
    def __init__(self, loaders: dict[SourceType, BaseLoader]) -> None:
        self.loaders = loaders

    async def load(self, source_input: SourceInput) -> LoadedSource:
        source_type = source_input.source_type or self.detect_source_type(source_input.uri)
        loader = self.loaders.get(source_type)
        if not loader:
            raise UnsupportedSourceError(f"Unsupported source type for {source_input.uri}")
        routed_input = SourceInput(
            uri=source_input.uri,
            path=source_input.path,
            source_type=source_type,
            title=source_input.title,
            metadata=source_input.metadata,
        )
        return await loader.load(routed_input)

    def detect_source_type(self, uri: str) -> SourceType:
        lowered = uri.lower()
        if lowered.startswith(("http://", "https://")):
            return SourceType.URL
        suffix = Path(lowered).suffix
        if suffix == ".pdf":
            return SourceType.PDF
        if suffix in {".md", ".markdown"}:
            return SourceType.MARKDOWN
        if suffix in {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs"}:
            return SourceType.CODE
        if suffix in {".txt", ".log", ".rst"}:
            return SourceType.TEXT
        raise UnsupportedSourceError(f"Unsupported source extension: {suffix or uri}")

