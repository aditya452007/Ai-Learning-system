"""FastAPI application factory for the MultiRAG backend."""

from __future__ import annotations

import asyncio
import logging
import os
import shutil

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import chat, graph, health, source_guides, sources, system, workspaces
from app.domain.models.exceptions import MultiRagError
from app.infrastructure.config.logging import configure_logging
from app.infrastructure.config.settings import Settings


def create_app() -> FastAPI:
    settings = Settings.from_env()
    configure_logging()
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event() -> None:
        logger = logging.getLogger("app.startup")
        
        # 1. Clean data on startup if requested
        if os.getenv("MULTIRAG_CLEAN_START", "false").lower() == "true":
            logger.info("MULTIRAG_CLEAN_START is enabled. Wiping all local data to start fresh...")
            for directory in [settings.data_dir, settings.chroma_persist_dir, settings.cache_dir]:
                if directory.exists():
                    shutil.rmtree(directory, ignore_errors=True)
                    
        # 2. Warm up embedding model and ChromaDB in background to speed up first request
        async def warmup_task() -> None:
            logger.info("Warming up embedding model and vector store in background...")
            try:
                from app.api.dependencies import get_rag_system
                system = get_rag_system()
                
                # Pre-initialize vector store and embeddings
                vector_store = system._ask_question.vector_store
                if hasattr(vector_store, "_get_client"):
                    vector_store._get_client()
                if hasattr(vector_store, "_get_embeddings"):
                    vector_store._get_embeddings()
                    
                logger.info("Warmup complete. Embedding models are loaded and system is fast.")
            except Exception as e:
                logger.error(f"Background warmup failed: {e}")
                
        asyncio.create_task(warmup_task())

    @app.exception_handler(MultiRagError)
    async def multi_rag_exception_handler(request: Request, exc: MultiRagError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"code": exc.code, "message": str(exc)})

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"code": "bad_request", "message": str(exc)})

    app.include_router(health.router)
    app.include_router(workspaces.router)
    app.include_router(sources.router)
    app.include_router(chat.router)
    app.include_router(graph.router)
    app.include_router(source_guides.router)
    app.include_router(system.router)
    return app


app = create_app()

