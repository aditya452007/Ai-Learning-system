# Data Contracts And API Specification

## Core Domain Contracts

### Workspace

```json
{
  "id": "workspace_123",
  "name": "RAG Research",
  "created_at": "2026-04-28T10:00:00Z",
  "updated_at": "2026-04-28T10:00:00Z",
  "index_version": 4,
  "source_count": 3,
  "chunk_count": 420
}
```

### SourceDocument

```json
{
  "id": "source_123",
  "workspace_id": "workspace_123",
  "title": "research.md",
  "source_type": "markdown",
  "uri": "research.md",
  "content_hash": "sha256...",
  "metadata": {
    "size_bytes": 20437
  }
}
```

### DocumentChunk

```json
{
  "id": "chunk_123",
  "workspace_id": "workspace_123",
  "source_id": "source_123",
  "text": "chunk text",
  "chunk_hash": "sha256...",
  "token_count": 620,
  "location": {
    "page": null,
    "heading": "Architecture",
    "line_start": 10,
    "line_end": 42
  },
  "metadata": {}
}
```

### RetrievalResult

```json
{
  "chunk_id": "chunk_123",
  "source_id": "source_123",
  "score": 0.83,
  "rank": 1,
  "retriever": "semantic",
  "excerpt": "short safe excerpt"
}
```

### Citation

```json
{
  "citation_id": "cite_1",
  "chunk_id": "chunk_123",
  "source_id": "source_123",
  "title": "research.md",
  "location_label": "Architecture",
  "excerpt": "short source excerpt"
}
```

## API Endpoints

### GET /health

Returns service status.

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### POST /workspaces

Request:

```json
{
  "name": "RAG Research"
}
```

Response:

```json
{
  "workspace": {
    "id": "workspace_123",
    "name": "RAG Research",
    "index_version": 0
  }
}
```

### POST /sources/upload

Multipart form:

- `workspace_id`
- `files[]`

Response:

```json
{
  "job_id": "job_123",
  "status": "completed",
  "sources_added": 2,
  "chunks_added": 180,
  "index_version": 1,
  "warnings": []
}
```

### POST /sources/url

Request:

```json
{
  "workspace_id": "workspace_123",
  "url": "https://example.com/article",
  "max_depth": 1
}
```

Response uses the same ingestion job shape as upload.

### POST /chat

Request:

```json
{
  "workspace_id": "workspace_123",
  "query": "What retrieval architecture should we use?",
  "retrieval_mode": "hybrid",
  "top_k": 6
}
```

Response:

```json
{
  "answer": "Use a multi-index RAG architecture...",
  "retrieval_mode": "hybrid",
  "citations": [
    {
      "citation_id": "cite_1",
      "chunk_id": "chunk_123",
      "source_id": "source_123",
      "title": "research.md",
      "location_label": "Architecture",
      "excerpt": "Vector search finds meaning..."
    }
  ],
  "diagnostics": {
    "semantic_hits": 12,
    "keyword_hits": 12,
    "graph_hits": 0,
    "fused_hits": 6,
    "retrieval_cache_hit": false,
    "answer_cache_hit": false,
    "latency_ms": 2430
  }
}
```

### GET /graph

Query params:

- `workspace_id`
- optional `focus_node_id`
- optional `depth`

Response:

```json
{
  "nodes": [
    {
      "id": "concept_graphrag",
      "label": "GraphRAG",
      "type": "concept",
      "weight": 12
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "chunk_123",
      "target": "concept_graphrag",
      "type": "mentions",
      "weight": 1
    }
  ]
}
```

### GET /source-guide

Query params:

- `workspace_id`
- optional `source_id`

Response:

```json
{
  "summary": "This source explains...",
  "key_topics": ["Hybrid retrieval", "GraphRAG"],
  "glossary": [
    {
      "term": "BM25",
      "definition": "A keyword retrieval algorithm..."
    }
  ],
  "suggested_questions": [
    "Why combine semantic and keyword search?"
  ],
  "cache_hit": true
}
```

## Compatibility Aliases

Keep these while migrating the current frontend:

- `POST /upload` maps to `POST /sources/upload`.
- `POST /scrape` maps to `POST /sources/url`.

## API Rules

- Responses must be structured; avoid plain strings except in health/debug routes.
- Every chat response must include diagnostics.
- Every cited answer must include citations.
- Every error response must include a user-readable message and a machine-readable code.
