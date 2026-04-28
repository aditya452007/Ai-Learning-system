"""Source guide generation use case."""

from __future__ import annotations

from dataclasses import asdict

from app.domain.models.answer import SourceGuide
from app.domain.ports.cache_store import CacheStorePort
from app.domain.ports.generation_provider import GenerationProviderPort
from app.domain.ports.workspace_repository import WorkspaceRepositoryPort
from app.domain.services.chunk_hashing import stable_json_hash
from app.infrastructure.generation.prompt_templates import SOURCE_GUIDE_PROMPT_VERSION


class GenerateSourceGuide:
    def __init__(
        self,
        repository: WorkspaceRepositoryPort,
        generation_provider: GenerationProviderPort,
        cache_store: CacheStorePort,
    ) -> None:
        self.repository = repository
        self.generation_provider = generation_provider
        self.cache_store = cache_store

    async def execute(self, workspace_id: str, source_id: str | None = None) -> SourceGuide:
        workspace = self.repository.get_workspace(workspace_id)
        chunks = self.repository.list_chunks(workspace_id, source_id=source_id)
        sources = self.repository.list_sources(workspace_id)
        title = next((source.title for source in sources if source.id == source_id), None)
        key = stable_json_hash(
            {
                "workspace_id": workspace_id,
                "source_id": source_id,
                "index_version": workspace.index_version,
                "prompt_version": SOURCE_GUIDE_PROMPT_VERSION,
                "model_name": self.generation_provider.model_name,
            }
        )
        cached = self.cache_store.get_json("source_guides", key)
        if isinstance(cached, dict):
            cached_value = dict(cached)
            cached_value["cache_hit"] = True
            return SourceGuide(**cached_value)
        guide = await self.generation_provider.generate_source_guide(chunks, title)
        self.cache_store.set_json("source_guides", key, asdict(guide) | {"cache_hit": False})
        return guide
