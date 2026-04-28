import asyncio
from pathlib import Path

from app.application.rag_learning_system import RagLearningSystem
from app.domain.models.retrieval import RetrievalMode
from app.domain.models.source_document import SourceInput
from app.infrastructure.config.settings import Settings


def test_facade_ingests_and_answers_with_citations(tmp_path: Path) -> None:
    asyncio.run(_run_facade_flow(tmp_path))


async def _run_facade_flow(tmp_path: Path) -> None:
    source_path = tmp_path / "rag_notes.md"
    source_path.write_text(
        "# Retrieval\n\nHybrid retrieval combines semantic search with BM25 keyword search for exact terms.",
        encoding="utf-8",
    )
    settings = Settings(data_dir=tmp_path / "workspaces", cache_dir=tmp_path / "cache")
    system = RagLearningSystem.from_settings(settings)
    workspace = system.create_workspace("Test Workspace")

    ingestion = await system.ingest_sources(
        workspace.id,
        [SourceInput(uri="rag_notes.md", path=str(source_path), title="rag_notes.md")],
    )
    answer = await system.ask(workspace.id, "What does hybrid retrieval combine?", RetrievalMode.HYBRID)

    assert ingestion.sources_added == 1
    assert ingestion.chunks_added >= 1
    assert answer.citations
    assert "cite_" in answer.answer
    assert answer.diagnostics.semantic_hits >= 1
    assert answer.diagnostics.keyword_hits >= 1
