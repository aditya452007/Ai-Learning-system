"""Chat API routes and schemas."""

from __future__ import annotations
from dataclasses import asdict
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import get_rag_system
from app.application.rag_learning_system import RagLearningSystem
from app.domain.models.retrieval import RetrievalMode
from app.infrastructure.generation.unified_provider import UnifiedProviderFactory
from app.infrastructure.config.llm_providers import LLMConfig, ModelRegistry

# --- Schemas ---

class ChatRequest(BaseModel):
    workspace_id: str | None = None
    session_id: str | None = None
    query: str = Field(min_length=1)
    retrieval_mode: str = "hybrid"
    top_k: int = Field(default=6, ge=1, le=20)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    top_k_gen: int | None = Field(default=None, ge=-1, le=100, alias="top_k")
    max_tokens: int | None = Field(default=None, ge=1, le=8192)
    system_prompt: str | None = Field(default=None, max_length=4000)

class CitationResponse(BaseModel):
    citation_id: str
    chunk_id: str
    source_id: str
    title: str
    location_label: str
    excerpt: str

class RetrievalDiagnosticsResponse(BaseModel):
    semantic_hits: int
    keyword_hits: int
    graph_hits: int
    fused_hits: int
    retrieval_cache_hit: bool
    answer_cache_hit: bool
    latency_ms: int
    planned_mode: str

class ChatResponse(BaseModel):
    answer: str
    response: str
    retrieval_mode: str
    citations: list[CitationResponse]
    diagnostics: RetrievalDiagnosticsResponse

class ProviderInfo(BaseModel):
    id: str
    name: str
    models: list[str]

class GenerationSettingsResponse(BaseModel):
    provider: str
    model: str
    temperature: float
    top_p: float
    top_k: int
    max_tokens: int
    system_prompt: str
    available_providers: list[ProviderInfo]

class GenerationSettingsRequest(BaseModel):
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    top_k: int | None = Field(default=None, ge=-1, le=100)
    max_tokens: int | None = Field(default=None, ge=1, le=8192)
    system_prompt: str | None = Field(default=None, max_length=4000)

# --- Routes ---

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    system: RagLearningSystem = Depends(get_rag_system),
) -> ChatResponse:
    workspace_id = request.workspace_id or request.session_id
    if not workspace_id:
        raise ValueError("workspace_id or session_id is required")

    provider = UnifiedProviderFactory.get_provider()

    gen_params = {}
    if request.temperature is not None:
        gen_params["temperature"] = request.temperature
    if request.top_p is not None:
        gen_params["top_p"] = request.top_p
    if request.top_k_gen is not None:
        gen_params["top_k"] = request.top_k_gen
    if request.max_tokens is not None:
        gen_params["max_tokens"] = request.max_tokens
    if request.system_prompt is not None:
        gen_params["system_prompt"] = request.system_prompt

    answer = await system.ask(
        workspace_id=workspace_id,
        query=request.query,
        retrieval_mode=RetrievalMode(request.retrieval_mode),
        top_k=request.top_k,
        generation_params=gen_params if gen_params else None,
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

@router.get("/settings/generation", response_model=GenerationSettingsResponse)
async def get_generation_settings() -> GenerationSettingsResponse:
    config = LLMConfig.from_env()
    return GenerationSettingsResponse(
        provider=config.provider.value,
        model=config.model,
        temperature=config.temperature,
        top_p=config.top_p,
        top_k=config.top_k,
        max_tokens=config.max_tokens,
        system_prompt=config.system_prompt,
        available_providers=[
            {"id": "nvidia", "name": "NVIDIA", "models": list(ModelRegistry.NVIDIA_MODELS.keys())},
            {"id": "openai", "name": "OpenAI", "models": list(ModelRegistry.OPENAI_MODELS.keys())},
            {"id": "anthropic", "name": "Anthropic", "models": list(ModelRegistry.ANTHROPIC_MODELS.keys())},
            {"id": "gemini", "name": "Google Gemini", "models": list(ModelRegistry.GEMINI_MODELS.keys())},
        ],
    )

@router.post("/settings/generation")
async def update_generation_settings(request: GenerationSettingsRequest) -> dict:
    provider = UnifiedProviderFactory.get_provider()
    new_config = provider.config.with_params(
        temperature=request.temperature,
        top_p=request.top_p,
        top_k=request.top_k,
        max_tokens=request.max_tokens,
        system_prompt=request.system_prompt,
    )
    provider.update_config(new_config)
    return {"status": "ok", "message": "Settings updated successfully"}
