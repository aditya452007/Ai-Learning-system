"""JSON graph adapter with NetworkX-compatible responsibilities."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict, deque
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.domain.models.document_chunk import DocumentChunk
from app.domain.models.graph import GraphEdge, GraphNode, GraphNodeType, GraphSnapshot
from app.domain.models.retrieval import RetrievalResult
from app.domain.models.source_document import SourceDocument
from app.domain.services.chunk_hashing import sha256_text


class GraphNetworkxStore:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def build(self, workspace_id: str, sources: list[SourceDocument], chunks: list[DocumentChunk]) -> None:
        nodes: dict[str, GraphNode] = {}
        edges: dict[str, GraphEdge] = {}
        concept_weights: Counter[str] = Counter()

        for source in sources:
            nodes[source.id] = GraphNode(source.id, source.title, GraphNodeType.SOURCE, weight=1)

        for chunk in chunks:
            chunk_label = chunk.location.label()
            nodes[chunk.id] = GraphNode(chunk.id, chunk_label, GraphNodeType.CHUNK, weight=1)
            edge_id = f"edge_{sha256_text(chunk.source_id + chunk.id)[:12]}"
            edges[edge_id] = GraphEdge(edge_id, chunk.source_id, chunk.id, "contains", 1)
            for concept in self._concepts(chunk.text):
                concept_id = self._concept_id(concept)
                concept_weights[concept_id] += 1
                nodes[concept_id] = GraphNode(concept_id, concept, GraphNodeType.CONCEPT, weight=concept_weights[concept_id])
                mention_id = f"edge_{sha256_text(chunk.id + concept_id)[:12]}"
                edges[mention_id] = GraphEdge(mention_id, chunk.id, concept_id, "mentions", 1)

        self._write(
            self._path(workspace_id),
            {
                "nodes": [asdict(node) | {"type": node.type.value} for node in nodes.values()],
                "edges": [asdict(edge) for edge in edges.values()],
            },
        )

    def snapshot(self, workspace_id: str, focus_node_id: str | None = None, depth: int = 1) -> GraphSnapshot:
        data = self._read(self._path(workspace_id))
        nodes = [self._node_from_dict(item) for item in data.get("nodes", [])]
        edges = [GraphEdge(**item) for item in data.get("edges", [])]
        if not focus_node_id:
            return GraphSnapshot(nodes=nodes[:250], edges=edges[:500])

        allowed = self._neighborhood(focus_node_id, edges, depth)
        return GraphSnapshot(
            nodes=[node for node in nodes if node.id in allowed],
            edges=[edge for edge in edges if edge.source in allowed and edge.target in allowed],
        )

    def search(self, workspace_id: str, query: str, top_k: int) -> list[RetrievalResult]:
        data = self._read(self._path(workspace_id))
        query_tokens = set(self._concept_tokens(query))
        concept_ids = {
            item["id"]
            for item in data.get("nodes", [])
            if item.get("type") == GraphNodeType.CONCEPT.value
            and query_tokens.intersection(self._concept_tokens(item.get("label", "")))
        }
        chunk_scores: Counter[str] = Counter()
        chunk_to_source: dict[str, str] = {}
        for edge in data.get("edges", []):
            if edge["type"] == "contains":
                chunk_to_source[edge["target"]] = edge["source"]
            if edge["type"] == "mentions" and edge["target"] in concept_ids:
                chunk_scores[edge["source"]] += 1

        ordered = chunk_scores.most_common(top_k)
        return [
            RetrievalResult(
                chunk_id=chunk_id,
                source_id=chunk_to_source.get(chunk_id, ""),
                score=float(score),
                rank=rank,
                retriever="graph",
                excerpt=f"Graph match through {score} related concept(s).",
                metadata={"matched_concepts": sorted(concept_ids)},
            )
            for rank, (chunk_id, score) in enumerate(ordered, start=1)
        ]

    def _concepts(self, text: str) -> list[str]:
        words = re.findall(r"\b[A-Za-z][A-Za-z0-9_-]{3,}\b", text)
        stop = {
            "that",
            "with",
            "from",
            "this",
            "have",
            "will",
            "should",
            "source",
            "chunk",
            "retrieval",
        }
        counts = Counter(word.strip("-_").lower() for word in words if word.lower() not in stop)
        return [term.title() for term, _ in counts.most_common(12)]

    def _concept_tokens(self, value: str) -> list[str]:
        return re.findall(r"[A-Za-z0-9_]+", value.lower())

    def _concept_id(self, concept: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", concept.lower()).strip("_")
        return f"concept_{slug[:80]}"

    def _neighborhood(self, focus_node_id: str, edges: list[GraphEdge], depth: int) -> set[str]:
        adjacency: dict[str, set[str]] = defaultdict(set)
        for edge in edges:
            adjacency[edge.source].add(edge.target)
            adjacency[edge.target].add(edge.source)
        allowed = {focus_node_id}
        queue: deque[tuple[str, int]] = deque([(focus_node_id, 0)])
        while queue:
            node_id, distance = queue.popleft()
            if distance >= depth:
                continue
            for neighbor in adjacency[node_id]:
                if neighbor not in allowed:
                    allowed.add(neighbor)
                    queue.append((neighbor, distance + 1))
        return allowed

    def _path(self, workspace_id: str) -> Path:
        return self.root_dir / workspace_id / "graph.json"

    def _read(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {"nodes": [], "edges": []}
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, path: Path, value: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def _node_from_dict(self, item: dict[str, Any]) -> GraphNode:
        return GraphNode(
            id=item["id"],
            label=item["label"],
            type=GraphNodeType(item["type"]),
            weight=float(item.get("weight", 1)),
        )
