"""URL loader with BeautifulSoup and single-level crawling.

Based on working implementation from Multi_Rag.ipynb.
Uses requests + BeautifulSoup for robust HTML extraction.
Only crawls the initial URL (single level) as per requirements.
"""

from __future__ import annotations

import logging
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.domain.models.source_document import SourceInput, SourceType
from app.infrastructure.loaders.base_loader import BaseLoader
from app.infrastructure.utils.text_processor import text_processor

logger = logging.getLogger(__name__)


class WebLoader(BaseLoader):
    """
    Web content loader using requests and BeautifulSoup.
    Extracts meaningful content from single URL (no deep crawling).
    """

    source_type = SourceType.URL

    def __init__(self, timeout_seconds: int = 10, max_retries: int = 3) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=retry_strategy
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    async def extract_text(self, source_input: SourceInput) -> tuple[str, dict[str, object]]:
        """
        Extract text from URL using requests + BeautifulSoup.
        Only fetches the single URL (no crawling).
        """
        url = source_input.uri

        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise

        content_type = response.headers.get("content-type", "")
        size_bytes = len(response.content)

        # Only process HTML content
        if "text/html" not in content_type.lower():
            logger.warning(f"Non-HTML content at {url}: {content_type}")
            return response.text, {
                "url": url,
                "content_type": content_type,
                "size_bytes": size_bytes,
                "extractor": "raw_text",
            }

        # Extract meaningful content
        final_text = text_processor.extract_meaningful_content(
            response.content,
            url=url
        )

        if not final_text:
            logger.warning(f"No meaningful text extracted from {url}")
            return "", {
                "url": url,
                "content_type": content_type,
                "size_bytes": size_bytes,
                "extractor": "beautifulsoup",
                "error": "No extractable text",
            }

        return final_text, {
            "url": url,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "extractor": "beautifulsoup",
        }

