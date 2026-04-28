"""Source ingestion API routes."""

from __future__ import annotations

import shutil
from dataclasses import asdict
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.dependencies import get_rag_system
from app.api.schemas.source_schemas import IngestionResponse, PrototypeIngestionResponse, UrlIngestionRequest
from app.application.rag_learning_system import RagLearningSystem
from app.domain.models.source_document import SourceInput, SourceType

router = APIRouter(tags=["sources"])


@router.post("/sources/upload", response_model=IngestionResponse)
async def upload_sources(
    workspace_id: str = Form(...),
    files: list[UploadFile] = File(...),
    system: RagLearningSystem = Depends(get_rag_system),
) -> IngestionResponse:
    inputs = await _save_uploads(system, workspace_id, files)
    result = await system.ingest_sources(workspace_id, inputs)
    return IngestionResponse(**asdict(result))


@router.post("/sources/url", response_model=IngestionResponse)
async def ingest_url(
    request: UrlIngestionRequest,
    system: RagLearningSystem = Depends(get_rag_system),
) -> IngestionResponse:
    result = await system.ingest_sources(
        request.workspace_id,
        [SourceInput(uri=str(request.url), source_type=SourceType.URL, title=str(request.url))],
    )
    return IngestionResponse(**asdict(result))


@router.post("/upload", response_model=PrototypeIngestionResponse)
async def prototype_upload(
    file: UploadFile = File(...),
    system: RagLearningSystem = Depends(get_rag_system),
) -> PrototypeIngestionResponse:
    workspace = system.create_workspace(file.filename or "Prototype Session")
    inputs = await _save_uploads(system, workspace.id, [file])
    result = await system.ingest_sources(workspace.id, inputs)
    workspace = system.get_workspace(workspace.id)
    return PrototypeIngestionResponse(
        session_id=workspace.id,
        token_count=workspace.chunk_count,
        sources_added=result.sources_added,
        chunks_added=result.chunks_added,
        warnings=result.warnings,
    )


@router.post("/scrape", response_model=PrototypeIngestionResponse)
async def prototype_scrape(
    url: str = Form(...),
    system: RagLearningSystem = Depends(get_rag_system),
) -> PrototypeIngestionResponse:
    workspace = system.create_workspace(url)
    result = await system.ingest_sources(workspace.id, [SourceInput(uri=url, source_type=SourceType.URL, title=url)])
    workspace = system.get_workspace(workspace.id)
    return PrototypeIngestionResponse(
        session_id=workspace.id,
        token_count=workspace.chunk_count,
        sources_added=result.sources_added,
        chunks_added=result.chunks_added,
        warnings=result.warnings,
    )


async def _save_uploads(
    system: RagLearningSystem,
    workspace_id: str,
    files: list[UploadFile],
) -> list[SourceInput]:
    storage_dir = system.workspace_storage_dir(workspace_id)
    inputs: list[SourceInput] = []
    for upload in files:
        filename = Path(upload.filename or "uploaded.txt").name
        destination = storage_dir / filename
        with destination.open("wb") as stream:
            shutil.copyfileobj(upload.file, stream)
        inputs.append(SourceInput(uri=filename, path=str(destination), title=filename))
    return inputs
