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
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "MultiRAG Learning System"
    app_version: str = "0.2.0"
    data_dir: Path = Path("data/workspaces")
    cache_dir: Path = Path("data/cache")
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    generation_model: str = "gemini-2.5-flash"
    gemini_api_key: str | None = None
    huggingface_token: str | None = None
    url_timeout_seconds: int = 10
    max_upload_bytes: int = 50 * 1024 * 1024
    chunk_size: int = 512
    chunk_overlap: int = 64
    max_crawl_pages: int = 50
    max_workers: int = 10
    vector_store_type: str = "chroma"
    chroma_persist_dir: Path = Path("data/chroma")

    @classmethod
    def from_env(cls) -> "Settings":
        repo_root = Path(__file__).resolve().parents[4]
        backend_root = Path(__file__).resolve().parents[3]
        _load_dotenv(backend_root / ".env")          # backend/.env (primary)
        _load_dotenv(repo_root / ".env")              # repo root .env
        _load_dotenv(repo_root / "MultRAG System" / ".env")

        data_dir = Path(os.getenv("MULTIRAG_DATA_DIR", repo_root / "data" / "workspaces"))
        cache_dir = Path(os.getenv("MULTIRAG_CACHE_DIR", repo_root / "data" / "cache"))
        chroma_dir = Path(os.getenv("MULTIRAG_CHROMA_DIR", repo_root / "data" / "chroma"))

        return cls(
            data_dir=data_dir,
            cache_dir=cache_dir,
            chroma_persist_dir=chroma_dir,
            embedding_model=os.getenv("MULTIRAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            generation_model=os.getenv("MULTIRAG_GENERATION_MODEL", "gemini-2.5-flash"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            huggingface_token=os.getenv("HUGGING_FACE_TOKEN"),
            url_timeout_seconds=int(os.getenv("MULTIRAG_URL_TIMEOUT_SECONDS", "10")),
            max_upload_bytes=int(os.getenv("MULTIRAG_MAX_UPLOAD_BYTES", str(50 * 1024 * 1024))),
            chunk_size=int(os.getenv("MULTIRAG_CHUNK_SIZE", "512")),
            chunk_overlap=int(os.getenv("MULTIRAG_CHUNK_OVERLAP", "64")),
            max_crawl_pages=int(os.getenv("MULTIRAG_MAX_CRAWL_PAGES", "50")),
            max_workers=int(os.getenv("MULTIRAG_MAX_WORKERS", "10")),
            vector_store_type=os.getenv("MULTIRAG_VECTOR_STORE", "chroma"),
        )
