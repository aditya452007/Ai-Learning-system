"""PDF loader with optional PyMuPDF support and a safe text fallback."""

from __future__ import annotations

from pathlib import Path

from app.domain.models.source_document import SourceInput, SourceType
from app.infrastructure.loaders.base_loader import BaseLoader


class PdfLoader(BaseLoader):
    source_type = SourceType.PDF

    async def extract_text(self, source_input: SourceInput) -> tuple[str, dict[str, object]]:
        path = Path(source_input.path or source_input.uri)
        try:
            import fitz  # type: ignore
        except Exception:
            data = path.read_bytes()
            return data.decode("utf-8", errors="ignore"), {
                "size_bytes": path.stat().st_size,
                "pdf_extractor": "binary_text_fallback",
            }

        pages: list[str] = []
        with fitz.open(path) as document:
            for page_number, page in enumerate(document, start=1):
                pages.append(f"\n\n[Page {page_number}]\n{page.get_text('text')}")
        return "\n".join(pages), {
            "size_bytes": path.stat().st_size,
            "page_count": len(pages),
            "pdf_extractor": "pymupdf",
        }

