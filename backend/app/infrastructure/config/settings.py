"""Runtime settings loaded from environment variables and optional .env files."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "MultiRAG Learning System"
    app_version: str = "0.1.0"
    data_dir: Path = Path("data/workspaces")
    cache_dir: Path = Path("data/cache")
    embedding_model: str = "local-hashing-384"
    generation_model: str = "gemini-2.5-flash"
    gemini_api_key: str | None = None
    url_timeout_seconds: int = 10
    max_upload_bytes: int = 50 * 1024 * 1024
    chunk_size_tokens: int = 700
    chunk_overlap_tokens: int = 100

    @classmethod
    def from_env(cls) -> "Settings":
        repo_root = Path(__file__).resolve().parents[4]
        _load_dotenv(repo_root / ".env")
        _load_dotenv(repo_root / "MultRAG System" / ".env")

        data_dir = Path(os.getenv("MULTIRAG_DATA_DIR", repo_root / "data" / "workspaces"))
        cache_dir = Path(os.getenv("MULTIRAG_CACHE_DIR", repo_root / "data" / "cache"))
        return cls(
            data_dir=data_dir,
            cache_dir=cache_dir,
            embedding_model=os.getenv("MULTIRAG_EMBEDDING_MODEL", "local-hashing-384"),
            generation_model=os.getenv("MULTIRAG_GENERATION_MODEL", "gemini-2.5-flash"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            url_timeout_seconds=int(os.getenv("MULTIRAG_URL_TIMEOUT_SECONDS", "10")),
            max_upload_bytes=int(os.getenv("MULTIRAG_MAX_UPLOAD_BYTES", str(50 * 1024 * 1024))),
            chunk_size_tokens=int(os.getenv("MULTIRAG_CHUNK_SIZE_TOKENS", "700")),
            chunk_overlap_tokens=int(os.getenv("MULTIRAG_CHUNK_OVERLAP_TOKENS", "100")),
        )
