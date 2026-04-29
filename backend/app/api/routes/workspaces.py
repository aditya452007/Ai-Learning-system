"""Workspace API routes and schemas."""

from __future__ import annotations
from dataclasses import asdict
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import get_rag_system
from app.application.rag_learning_system import RagLearningSystem

# --- Schemas ---

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

# --- Routes ---

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.post("", response_model=CreateWorkspaceResponse)
def create_workspace(
    request: WorkspaceCreateRequest,
    system: RagLearningSystem = Depends(get_rag_system),
) -> CreateWorkspaceResponse:
    workspace = system.create_workspace(request.name)
    return CreateWorkspaceResponse(workspace=WorkspaceResponse(**asdict(workspace)))

@router.get("", response_model=ListWorkspacesResponse)
def list_workspaces(system: RagLearningSystem = Depends(get_rag_system)) -> ListWorkspacesResponse:
    return ListWorkspacesResponse(
        workspaces=[WorkspaceResponse(**asdict(workspace)) for workspace in system.list_workspaces()]
    )
