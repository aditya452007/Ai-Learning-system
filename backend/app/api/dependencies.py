"""FastAPI dependency construction for the application facade."""

from __future__ import annotations

from functools import lru_cache

from app.application.rag_learning_system import RagLearningSystem
from app.infrastructure.config.settings import Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()


@lru_cache(maxsize=1)
def get_rag_system() -> RagLearningSystem:
    return RagLearningSystem.from_settings(get_settings())

