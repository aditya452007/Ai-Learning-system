# Engineering Principles And Patterns

## Principles

### KISS

Choose the simplest design that satisfies the current known requirements. Do not add distributed queues, microservices, or complex auth before the local product works.

### YAGNI

Do not build features because an enterprise product might need them someday. Build extension points where change is likely:

- LLM provider.
- Vector store.
- Graph store.
- Source loaders.
- Chunking strategy.

### DRY

Avoid repeated logic, but do not create abstractions after one use. Duplicate once if it keeps code readable. Abstract when the third use appears or when provider replacement requires it.

### SOLID, Applied Pragmatically

- Single Responsibility: loaders load, chunkers chunk, retrievers retrieve.
- Open/Closed: add a new loader or vector store by adding an adapter.
- Liskov: all loaders must honor the same contract.
- Interface Segregation: separate ports for vector, keyword, graph, LLM, cache.
- Dependency Inversion: application depends on ports, infrastructure implements them.

### Composition Over Inheritance

Use inheritance where it genuinely standardizes behavior, such as `BaseLoader`.

Prefer composition for workflows:

- `UnifiedLoader` composes specialist loaders.
- `RagLearningSystem` composes use cases.
- `AskQuestion` composes retrievers, fusion, context builder, and generator.

## Design Patterns

### Facade

`RagLearningSystem` provides a simple public interface over many internal services.

Use when:

- The API layer needs one clean entry point.
- Scripts need a simple way to run workflows.

### Strategy

Use for:

- Chunking strategies.
- Retrieval modes.
- Query planning.
- Reranking.

Benefit:

- New strategies can be added without rewriting the query flow.

### Adapter

Use for:

- Gemini.
- Sentence Transformers.
- FAISS.
- Qdrant.
- NetworkX.
- Disk/SQLite cache.

Benefit:

- Third-party SDK changes do not leak into the domain.

### Repository

Use for:

- Workspaces.
- Source manifests.
- Chunk metadata.

Benefit:

- Persistence can change from JSONL to SQLite without rewriting use cases.

### Factory

Use for:

- Loader selection.
- Provider construction from settings.

Benefit:

- Configuration is centralized.

### Template Method, Carefully

Use for:

- Base loader safety flow if all loaders share validation, logging, and document creation.

Avoid:

- Deep inheritance trees.

## Error Handling

Create domain-specific exceptions:

- `SourceLoadError`
- `UnsupportedSourceError`
- `ChunkingError`
- `IndexingError`
- `RetrievalError`
- `GenerationError`
- `WorkspaceNotFoundError`

API layer maps them to HTTP errors. Domain code should not raise `HTTPException`.

## Logging

Every major operation logs:

- `request_id`
- `workspace_id`
- `operation`
- `duration_ms`
- `status`
- `error_type` if failed

Do not log full source text, API keys, or private user content beyond short safe excerpts.

## Async And Resource Management

Use async for:

- API handlers.
- URL fetching.
- Batch loading.
- LLM calls.

Use bounded concurrency:

- Semaphores for batch ingestion.
- Timeouts for URL loading and provider calls.
- Size limits for files and responses.

Add cleanup methods for:

- Provider clients.
- Loaded indexes.
- Temporary files.

## Code Quality Rules

- No function should mix IO, business rules, and formatting.
- No API route should contain retrieval logic.
- No domain model should import a third-party SDK.
- No prompt should be hard-coded inside route handlers.
- No cache should ignore model version or index version.
- No answer should be returned as grounded unless it has citations.

## Documentation Rules

Each major module should have a short docstring explaining responsibility.

Do not comment obvious code. Comment:

- Non-obvious retrieval scoring.
- Cache invalidation rules.
- Provider-specific quirks.
- Security-sensitive decisions.
