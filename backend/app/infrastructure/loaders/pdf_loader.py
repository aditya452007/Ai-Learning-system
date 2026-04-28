"""PDF loader with robust PyMuPDF implementation.

Based on working implementation from Multi_Rag.ipynb.
Safely handles corrupt PDFs and extracts text with page tracking.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from app.domain.models.source_document import SourceInput, SourceType
from app.infrastructure.loaders.base_loader import BaseLoader
from app.infrastructure.utils.text_processor import text_processor

logger = logging.getLogger(__name__)


class PdfLoader(BaseLoader):
    """Robust PDF text extraction using PyMuPDF (fitz)."""

    source_type = SourceType.PDF

    async def extract_text(self, source_input: SourceInput) -> tuple[str, dict[str, object]]:
        """
        Extracts text from PDF using PyMuPDF.
        Iterates safely page-by-page to handle corrupt PDFs.
        """
        path = Path(source_input.path or source_input.uri)

        try:
            import fitz  # PyMuPDF
        except ImportError as e:
            logger.error("PyMuPDF (fitz) not installed. Install with: pip install pymupdf")
            raise ImportError("PyMuPDF required for PDF processing") from e

        text_parts: list[str] = []
        pages_processed = 0
        pages_skipped = 0

        try:
            doc = fitz.open(path)

            # Safe iteration to skip bad pages
            for i in range(len(doc)):
                try:
                    page = doc.load_page(i)
                    page_text = page.get_text("text", sort=True)
                    if page_text.strip():
                        text_parts.append(f"\n\n[Page {i + 1}]\n{page_text}")
                        pages_processed += 1
                except Exception as e:
                    logger.warning(f"Skipping corrupt page {i} in {path}: {e}")
                    pages_skipped += 1
                    continue

            doc.close()

            if not text_parts:
                logger.warning(f"No readable text found in {path}")
                return "", {
                    "size_bytes": path.stat().st_size,
                    "page_count": 0,
                    "pages_processed": 0,
                    "pages_skipped": pages_skipped,
                    "pdf_extractor": "pymupdf",
                    "error": "No extractable text",
                }

            full_text = "\n".join(text_parts)

            # Apply text cleaning
            cleaned_text = text_processor.clean(full_text) or full_text

            return cleaned_text, {
                "size_bytes": path.stat().st_size,
                "page_count": pages_processed + pages_skipped,
                "pages_processed": pages_processed,
                "pages_skipped": pages_skipped,
                "pdf_extractor": "pymupdf",
            }

        except Exception as e:
            logger.error(f"PDF processing failed for {path}: {e}")
            raise

