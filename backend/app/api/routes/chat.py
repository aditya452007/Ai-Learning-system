"""Chat API routes."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_system
from app.api.schemas.chat_schemas import ChatRequest, ChatResponse
from app.application.rag_learning_system import RagLearningSystem
from app.domain.models.retrieval import RetrievalMode

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    system: RagLearningSystem = Depends(get_rag_system),
) -> ChatResponse:
    workspace_id = request.workspace_id or request.session_id
    if not workspace_id:
        raise ValueError("workspace_id or session_id is required")
    answer = await system.ask(
        workspace_id=workspace_id,
        query=request.query,
        retrieval_mode=RetrievalMode(request.retrieval_mode),
        top_k=request.top_k,
    )
    diagnostics = asdict(answer.diagnostics)
    diagnostics["planned_mode"] = answer.diagnostics.planned_mode.value
    return ChatResponse(
        answer=answer.answer,
        response=answer.answer,
        retrieval_mode=answer.retrieval_mode.value,
        citations=[asdict(citation) for citation in answer.citations],
        diagnostics=diagnostics,
    )

