"""Unified text processing and cleaning utilities.

Based on the working implementation from Multi_Rag.ipynb.
Provides robust text cleaning for PDF, web, and document extraction.
"""

from __future__ import annotations

import re
from typing import Optional


class TextProcessor:
    """
    Consolidated text cleaning logic for document processing.
    Handles normalization, whitespace cleanup, and quality gating.
    """

    def __init__(self) -> None:
        # Collapse multiple spaces/tabs into one space
        self.multi_space = re.compile(r"[ \t]+")
        # Collapse 3+ newlines into 2 (preserves paragraph structure)
        self.multi_newline = re.compile(r"\n{3,}")
        # Remove empty brackets often left behind by removed links/citations
        self.empty_brackets = re.compile(r"\[\s*\]")
        # Critical Filters (Fast Fail) - common error pages
        self.error_404 = re.compile(r"404: This page could not be found", re.IGNORECASE)
        self.error_page = re.compile(r"(page not found|error 404|not found|403 forbidden)", re.IGNORECASE)

    def clean(self, text: str | None) -> Optional[str]:
        """
        Clean and normalize text content.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text or None if text is invalid/too short
        """
        if not text:
            return None

        # Fast Fail: Check for error pages immediately
        if self.error_404.search(text) or self.error_page.search(text):
            return None

        # 1. Normalize Unicode non-breaking spaces
        cleaned_text = text.replace("\xa0", " ")

        # 2. Remove empty brackets
        cleaned_text = self.empty_brackets.sub("", cleaned_text)

        # 3. Collapse multiple spaces within lines
        cleaned_text = self.multi_space.sub(" ", cleaned_text)

        # 4. Collapse excessive newlines
        cleaned_text = self.multi_newline.sub("\n\n", cleaned_text)

        # 5. Filter for printable ASCII (keep newlines)
        cleaned_text = "".join(c for c in cleaned_text if c.isprintable() or c == "\n")

        cleaned_text = cleaned_text.strip()

        # Quality Gate: Must have at least 50 meaningful characters
        if len(cleaned_text) < 50:
            return None

        return cleaned_text

    def extract_meaningful_content(self, html_content: bytes | str, url: str = "") -> Optional[str]:
        """
        Extract meaningful text from HTML content.

        Args:
            html_content: Raw HTML content (bytes or string)
            url: Source URL for context

        Returns:
            Extracted and cleaned text with source attribution
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            # Fallback if BeautifulSoup not available
            if isinstance(html_content, bytes):
                text = html_content.decode("utf-8", errors="ignore")
            else:
                text = html_content
            cleaned = self.clean(text)
            if cleaned and url:
                return f"Source: {url}\n\n{cleaned}"
            return cleaned

        if isinstance(html_content, bytes):
            soup = BeautifulSoup(html_content, "html.parser")
        else:
            soup = BeautifulSoup(html_content, "html.parser")

        # Remove garbage tags that don't contain meaningful content
        garbage_tags = {
            "script", "style", "noscript", "svg", "header", "footer",
            "nav", "aside", "form", "iframe", "button", "input",
            "select", "textarea", "meta", "link"
        }

        for tag in soup.find_all(garbage_tags):
            tag.decompose()

        # Get text with paragraph separation
        raw_text = soup.get_text(separator="\n")

        # Apply standard cleaning
        final_text = self.clean(raw_text)

        if final_text and url:
            return f"Source: {url}\n\n{final_text}"

        return final_text


# Global singleton for processor
text_processor = TextProcessor()


def clean_text(text: str | None) -> Optional[str]:
    """Convenience function using global processor."""
    return text_processor.clean(text)
