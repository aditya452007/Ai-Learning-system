import pytest
import asyncio
from pathlib import Path
from app.application.rag_learning_system import RagLearningSystem
from app.domain.models.retrieval import RetrievalMode
from app.domain.models.source_document import SourceInput
from app.infrastructure.config.settings import Settings
from pydantic import ValidationError

@pytest.fixture
def rag_system(tmp_path):
    # Setup a clean environment for each test
    settings = Settings(
        data_dir=tmp_path / "workspaces",
        cache_dir=tmp_path / "cache",
        chroma_persist_dir=tmp_path / "chroma"
    )
    return RagLearningSystem.from_settings(settings)

@pytest.mark.asyncio
async def test_end_to_end_happy_path(rag_system, tmp_path):
    """Verify complete flow: Workspace -> Ingestion -> Query -> Answer"""
    # 1. Create Workspace
    workspace = rag_system.create_workspace("Integration Test")
    assert workspace.name == "Integration Test"
    assert workspace.id is not None

    # 2. Ingest Data
    source_file = tmp_path / "test_doc.txt"
    source_file.write_text("The secret key of the vault is GOLDEN-TICKET-123.", encoding="utf-8")
    
    await rag_system.ingest_sources(workspace.id, [
        SourceInput(uri="test_doc.txt", path=str(source_file), title="Test Doc")
    ])

    # 3. Query Data
    answer = await rag_system.ask(workspace.id, "What is the secret key?", RetrievalMode.HYBRID)
    
    assert "GOLDEN-TICKET-123" in answer.answer
    assert len(answer.citations) > 0
    assert answer.diagnostics.fused_hits > 0

@pytest.mark.asyncio
async def test_query_empty_workspace(rag_system):
    """Verify behavior when querying a workspace with no data"""
    workspace = rag_system.create_workspace("Empty Workspace")
    
    # Should not crash, should return a graceful "no information" response
    answer = await rag_system.ask(workspace.id, "What is the capital of France?")
    
    assert answer.answer is not None
    assert len(answer.citations) == 0
    assert answer.diagnostics.fused_hits == 0

@pytest.mark.asyncio
async def test_invalid_workspace_id(rag_system):
    """Verify that invalid workspace IDs are handled gracefully"""
    with pytest.raises(Exception): # Should raise FileNotFoundError or similar
        await rag_system.ask("non_existent_id", "Hello?")

@pytest.mark.asyncio
async def test_ingest_invalid_path(rag_system):
    """Verify ingestion with non-existent file paths"""
    workspace = rag_system.create_workspace("Fail Workspace")
    
    # Attempt to ingest a file that doesn't exist
    with pytest.raises(Exception):
        await rag_system.ingest_sources(workspace.id, [
            SourceInput(uri="ghost.txt", path="/tmp/does_not_exist.txt", title="Ghost")
        ])

def test_workspace_listing(rag_system):
    """Verify workspace creation and listing consistency"""
    rag_system.create_workspace("WS1")
    rag_system.create_workspace("WS2")
    
    workspaces = rag_system.list_workspaces()
    assert len(workspaces) >= 2
    names = [ws.name for ws in workspaces]
    assert "WS1" in names
    assert "WS2" in names
