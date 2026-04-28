"""Workspace API routes."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_system
from app.api.schemas.workspace_schemas import (
    CreateWorkspaceResponse,
    ListWorkspacesResponse,
    WorkspaceCreateRequest,
    WorkspaceResponse,
)
from app.application.rag_learning_system import RagLearningSystem

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

