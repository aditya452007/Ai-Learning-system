"""Prototype compatibility system routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_system
from app.application.rag_learning_system import RagLearningSystem

router = APIRouter(tags=["system"])


@router.post("/reset")
def reset(system: RagLearningSystem = Depends(get_rag_system)) -> dict[str, str]:
    system.reset()
    return {"status": "ok"}

