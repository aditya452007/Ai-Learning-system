"""Workspace API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(default="Untitled Workspace", min_length=1, max_length=120)


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    index_version: int
    source_count: int
    chunk_count: int


class CreateWorkspaceResponse(BaseModel):
    workspace: WorkspaceResponse


class ListWorkspacesResponse(BaseModel):
    workspaces: list[WorkspaceResponse]

