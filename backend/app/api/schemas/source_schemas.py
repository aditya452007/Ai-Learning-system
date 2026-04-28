"""Source ingestion API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class UrlIngestionRequest(BaseModel):
    workspace_id: str
    url: HttpUrl
    max_depth: int = Field(default=1, ge=1, le=1)


class IngestionResponse(BaseModel):
    job_id: str
    status: str
    sources_added: int
    chunks_added: int
    index_version: int
    warnings: list[str]


class PrototypeIngestionResponse(BaseModel):
    session_id: str
    token_count: int
    sources_added: int
    chunks_added: int
    warnings: list[str]

