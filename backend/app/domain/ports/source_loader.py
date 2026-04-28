"""Loader port for turning source inputs into normalized text."""

from __future__ import annotations

from typing import Protocol

from app.domain.models.source_document import LoadedSource, SourceInput


class SourceLoaderPort(Protocol):
    async def load(self, source_input: SourceInput) -> LoadedSource:
        ...

