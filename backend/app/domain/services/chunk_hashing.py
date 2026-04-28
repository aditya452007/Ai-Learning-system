"""Hashing helpers for source, chunk, and cache identity."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def stable_json_hash(value: Any) -> str:
    serialized = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return sha256_text(serialized)


def chunk_hash(source_hash: str, text: str, ordinal: int, chunker_version: str) -> str:
    return stable_json_hash(
        {
            "source_hash": source_hash,
            "text": text,
            "ordinal": ordinal,
            "chunker_version": chunker_version,
        }
    )

