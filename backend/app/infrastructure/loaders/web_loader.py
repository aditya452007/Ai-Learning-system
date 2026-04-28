"""URL loader with stdlib fetching, timeout, and basic HTML cleanup."""

from __future__ import annotations

import html
import re
import urllib.request
from html.parser import HTMLParser

from app.domain.models.source_document import SourceInput, SourceType
from app.infrastructure.loaders.base_loader import BaseLoader


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self.skip_depth += 1
        if tag in {"p", "br", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self.skip_depth:
            self.skip_depth -= 1
        if tag in {"p", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        value = html.unescape(" ".join(self.parts))
        return re.sub(r"[ \t]+", " ", value)


class WebLoader(BaseLoader):
    source_type = SourceType.URL

    def __init__(self, timeout_seconds: int = 10) -> None:
        self.timeout_seconds = timeout_seconds

    async def extract_text(self, source_input: SourceInput) -> tuple[str, dict[str, object]]:
        request = urllib.request.Request(
            source_input.uri,
            headers={"User-Agent": "MultiRAGLearningSystem/0.1"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            content_type = response.headers.get("content-type", "")
            raw = response.read(2_000_000)
        decoded = raw.decode("utf-8", errors="ignore")
        if "html" in content_type.lower() or "<html" in decoded[:500].lower():
            parser = _TextExtractor()
            parser.feed(decoded)
            decoded = parser.text()
        return decoded, {"content_type": content_type, "size_bytes": len(raw)}

