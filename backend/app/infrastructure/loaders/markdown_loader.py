"""Markdown source loader."""

from __future__ import annotations

from app.domain.models.source_document import SourceType
from app.infrastructure.loaders.text_loader import TextLoader


class MarkdownLoader(TextLoader):
    source_type = SourceType.MARKDOWN

