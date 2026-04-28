"""Seed a small demo workspace from the bundled fixture."""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.application.rag_learning_system import RagLearningSystem  # noqa: E402
from app.domain.models.source_document import SourceInput  # noqa: E402
from app.infrastructure.config.settings import Settings  # noqa: E402


async def main() -> None:
    settings = Settings.from_env()
    system = RagLearningSystem.from_settings(settings)
    workspace = system.create_workspace("Demo Workspace")
    fixture = BACKEND / "tests" / "fixtures" / "demo_notes.md"
    result = await system.ingest_sources(
        workspace.id,
        [SourceInput(uri="demo_notes.md", path=str(fixture), title="demo_notes.md")],
    )
    print(
        f"Seeded {workspace.id}: {result.sources_added} source(s), "
        f"{result.chunks_added} chunk(s), index version {result.index_version}"
    )


if __name__ == "__main__":
    asyncio.run(main())

