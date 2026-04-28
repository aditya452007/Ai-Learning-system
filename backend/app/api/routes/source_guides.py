"""Source guide API route."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_system
from app.api.schemas.source_guide_schemas import SourceGuideResponse
from app.application.rag_learning_system import RagLearningSystem

router = APIRouter(tags=["source-guides"])


@router.get("/source-guide", response_model=SourceGuideResponse)
async def source_guide(
    workspace_id: str,
    source_id: str | None = None,
    system: RagLearningSystem = Depends(get_rag_system),
) -> SourceGuideResponse:
    guide = await system.generate_source_guide(workspace_id, source_id=source_id)
    return SourceGuideResponse(**asdict(guide))

