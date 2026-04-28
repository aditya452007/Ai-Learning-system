# Architecture Blueprint

## Architecture Style

Use **hexagonal-lite architecture**:

- Domain models and use cases live at the center.
- API, databases, vector stores, graph stores, and LLMs are adapters.
- The application depends on interfaces, not concrete vendor SDKs.

This gives us serious engineering discipline without building a maze of abstractions.

## High-Level Flow

```text
User
  -> Frontend Workspace
  -> FastAPI API Layer
  -> Application Use Cases
  -> Domain Services
  -> Provider Ports
  -> Infrastructure Adapters
```

## Ingestion Flow

```text
Source Input
  -> UnifiedSourceLoader
  -> Specialist Loader
  -> SourceDocument
  -> Chunking Strategy
  -> DocumentChunk[]
  -> Embedding Cache
  -> Vector Index
  -> BM25 Index
  -> Graph Builder
  -> Workspace Manifest
```

## Query Flow

```text
User Query
  -> Query Normalizer
  -> Query Planner
  -> Retrieval Cache Check
  -> Semantic Retriever
  -> Keyword Retriever
  -> Graph Retriever
  -> Fusion / Rerank
  -> Context Builder
  -> Answer Cache Check
  -> LLM Adapter
  -> Citation Verifier
  -> Response DTO
```

## Core Components

### 1. API Layer

Responsibilities:

- HTTP request validation.
- Authentication later, not in MVP.
- Mapping API schemas to application commands.
- Returning structured responses.

Must not contain:

- Retrieval algorithms.
- Prompt construction logic.
- Direct vector database calls.

### 2. Application Layer

Use cases:

- `CreateWorkspace`
- `IngestSources`
- `BuildIndexes`
- `AskQuestion`
- `GenerateSourceGuide`
- `GetGraph`

Responsibilities:

- Orchestrate domain services.
- Manage transactions at workspace level.
- Call ports/interfaces.
- Enforce workflow order.

### 3. Domain Layer

Contains stable concepts:

- `Workspace`
- `SourceDocument`
- `DocumentChunk`
- `Citation`
- `RetrievalQuery`
- `RetrievalResult`
- `GraphNode`
- `GraphEdge`
- `Answer`

Domain code should use standard Python types and should not know about FastAPI, Qdrant, Chroma, Gemini, OpenAI, NetworkX, or any SDK.

### 4. Infrastructure Layer

Contains adapters:

- PDF loader.
- Markdown loader.
- Web loader.
- Vector store adapter.
- BM25 adapter.
- Graph store adapter.
- LLM adapter.
- Cache adapter.
- File workspace repository.

Adapters are replaceable.

## Caching Architecture

Caching is not optional. It is a first-class performance feature.

### Cache Layers

1. **Source extraction cache**
   - Key: `source_uri + source_hash + loader_version`
   - Value: extracted text and metadata.

2. **Chunk cache**
   - Key: `source_hash + chunker_version + chunk_config`
   - Value: chunks with citation metadata.

3. **Embedding cache**
   - Key: `embedding_model + chunk_hash`
   - Value: embedding vector.
   - Store in SQLite or disk-backed key-value files.

4. **Index cache**
   - Key: `workspace_id + index_version + retriever_type`
   - Value: persisted vector/BM25/graph index.

5. **Retrieval cache**
   - Key: `workspace_id + normalized_query + retrieval_mode + index_version`
   - Value: top retrieval results.
   - TTL: short, because index changes invalidate it anyway.

6. **Answer cache**
   - Key: `workspace_id + normalized_query + index_version + prompt_version + model_name`
   - Value: generated answer and citations.
   - Only cache when citations pass verification.

7. **Source guide cache**
   - Key: `source_hash + prompt_version + model_name`
   - Value: generated guide.

### Cache Invalidation

Increment `workspace.index_version` when:

- A source is added.
- A source is removed.
- Chunks are regenerated.
- Embedding model changes.
- Retrieval configuration changes.

Never serve cached answers across index versions.

## Vector Store Decision

For a fast, low-RAM MVP:

- Keep a FAISS adapter as the simplest local path.
- Store chunk metadata in SQLite/JSONL, not inside FAISS.
- Use normalized embeddings and inner product search.
- Persist FAISS indexes per workspace.

For stronger post-MVP persistence and filtering:

- Add a Qdrant adapter.
- Qdrant gives HNSW search, payload filtering, persistence, and quantization options.
- It can run locally and avoids tying the domain to a hosted provider.

Chroma is acceptable for prototyping, but Qdrant or FAISS plus SQLite is cleaner for performance and memory control.

## Graph Store Decision

MVP:

- Build graph with NetworkX in infrastructure.
- Persist as JSON.
- Serve frontend graph DTOs from this JSON.

Post-MVP:

- Add Kuzu for embedded graph persistence if graph queries become important.
- Add Neo4j only if advanced graph tooling is required.

## LLM Provider Decision

Start with Gemini because the prototype uses it.

Protect the codebase with a `GenerationPort` interface:

```text
generate_answer(request) -> GeneratedAnswer
generate_source_guide(request) -> SourceGuide
rewrite_query(request) -> QueryRewrite
```

If Gemini changes, only the Gemini adapter should change.

## Orchestrator

Create a high-level application facade:

```text
RagLearningSystem
  create_workspace()
  ingest_sources()
  ask()
  get_graph()
  generate_source_guide()
```

This mirrors the "main bot class" pattern from the reference PDF: one friendly entry point coordinates specialist components, but it does not do their work directly.
