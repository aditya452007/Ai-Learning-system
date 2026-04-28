"""File-backed workspace repository for local-first persistence."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from app.domain.models.document_chunk import ChunkLocation, DocumentChunk
from app.domain.models.exceptions import WorkspaceNotFoundError
from app.domain.models.source_document import SourceDocument, SourceType
from app.domain.models.workspace import Workspace


class FileWorkspaceRepository:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def save_workspace(self, workspace: Workspace) -> None:
        workspace_dir = self._workspace_dir(workspace.id)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(workspace_dir / "manifest.json", self._workspace_to_dict(workspace))

    def get_workspace(self, workspace_id: str) -> Workspace:
        path = self._workspace_dir(workspace_id) / "manifest.json"
        if not path.exists():
            raise WorkspaceNotFoundError(f"Workspace {workspace_id} was not found")
        return self._workspace_from_dict(self._read_json(path))

    def list_workspaces(self) -> list[Workspace]:
        workspaces: list[Workspace] = []
        for manifest in sorted(self.root_dir.glob("workspace_*/manifest.json")):
            workspaces.append(self._workspace_from_dict(self._read_json(manifest)))
        return workspaces

    def add_source_with_chunks(self, source: SourceDocument, chunks: list[DocumentChunk]) -> None:
        workspace_dir = self._workspace_dir(source.workspace_id)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        sources_path = workspace_dir / "sources.jsonl"
        chunks_path = workspace_dir / "chunks.jsonl"
        with sources_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(self._source_to_dict(source), ensure_ascii=False) + "\n")
        with chunks_path.open("a", encoding="utf-8") as stream:
            for chunk in chunks:
                stream.write(json.dumps(self._chunk_to_dict(chunk), ensure_ascii=False) + "\n")

    def list_sources(self, workspace_id: str) -> list[SourceDocument]:
        self.get_workspace(workspace_id)
        path = self._workspace_dir(workspace_id) / "sources.jsonl"
        if not path.exists():
            return []
        return [self._source_from_dict(item) for item in self._read_jsonl(path)]

    def list_chunks(self, workspace_id: str, source_id: str | None = None) -> list[DocumentChunk]:
        self.get_workspace(workspace_id)
        path = self._workspace_dir(workspace_id) / "chunks.jsonl"
        if not path.exists():
            return []
        chunks = [self._chunk_from_dict(item) for item in self._read_jsonl(path)]
        if source_id:
            return [chunk for chunk in chunks if chunk.source_id == source_id]
        return chunks

    def find_source_by_hash(self, workspace_id: str, content_hash: str) -> SourceDocument | None:
        for source in self.list_sources(workspace_id):
            if source.content_hash == content_hash:
                return source
        return None

    def clear_all(self) -> None:
        if self.root_dir.exists():
            shutil.rmtree(self.root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def workspace_storage_dir(self, workspace_id: str) -> Path:
        directory = self._workspace_dir(workspace_id) / "storage"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def _workspace_dir(self, workspace_id: str) -> Path:
        return self.root_dir / workspace_id

    def _read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, value: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2, default=str), encoding="utf-8")

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _workspace_to_dict(self, workspace: Workspace) -> dict[str, Any]:
        value = asdict(workspace)
        value["created_at"] = workspace.created_at.isoformat()
        value["updated_at"] = workspace.updated_at.isoformat()
        return value

    def _workspace_from_dict(self, value: dict[str, Any]) -> Workspace:
        return Workspace(
            id=value["id"],
            name=value["name"],
            created_at=datetime.fromisoformat(value["created_at"]),
            updated_at=datetime.fromisoformat(value["updated_at"]),
            index_version=int(value.get("index_version", 0)),
            source_count=int(value.get("source_count", 0)),
            chunk_count=int(value.get("chunk_count", 0)),
            metadata=dict(value.get("metadata", {})),
        )

    def _source_to_dict(self, source: SourceDocument) -> dict[str, Any]:
        value = asdict(source)
        value["source_type"] = source.source_type.value
        return value

    def _source_from_dict(self, value: dict[str, Any]) -> SourceDocument:
        return SourceDocument(
            id=value["id"],
            workspace_id=value["workspace_id"],
            title=value["title"],
            source_type=SourceType(value["source_type"]),
            uri=value["uri"],
            content_hash=value["content_hash"],
            metadata=dict(value.get("metadata", {})),
        )

    def _chunk_to_dict(self, chunk: DocumentChunk) -> dict[str, Any]:
        value = asdict(chunk)
        return value

    def _chunk_from_dict(self, value: dict[str, Any]) -> DocumentChunk:
        location = ChunkLocation(**value["location"])
        return DocumentChunk(
            id=value["id"],
            workspace_id=value["workspace_id"],
            source_id=value["source_id"],
            text=value["text"],
            chunk_hash=value["chunk_hash"],
            token_count=int(value["token_count"]),
            location=location,
            metadata=dict(value.get("metadata", {})),
        )

