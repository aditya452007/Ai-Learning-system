"""FastAPI application factory for the MultiRAG backend."""

from __future__ import annotations

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

