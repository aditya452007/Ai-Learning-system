"""Health endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.infrastructure.config.settings import Settings
from app.api.dependencies import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}

