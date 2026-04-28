# Agent SOP

This SOP tells AI coding agents how to build this project without damaging the architecture.

## Mission

Build a performant, maintainable, source-grounded RAG learning system. Preserve separation between domain logic and third-party infrastructure.

## Before Writing Code

1. Read `docs/README.md`.
2. Read the relevant spec for the task.
3. Identify which layer owns the change:
   - API
   - application
   - domain
   - infrastructure
   - frontend
4. Check existing patterns before creating a new abstraction.
5. Write down the acceptance criteria for the slice.

## Coding Rules

- Keep domain code provider-free.
- Do not import FastAPI outside the API layer.
- Do not import Gemini/OpenAI/Qdrant/FAISS SDKs outside infrastructure adapters.
- Do not put business logic in route handlers.
- Do not duplicate chunk, citation, cache key, or fusion logic.
- Do not return uncited grounded answers.
- Do not add a new dependency when the standard library or existing dependency is enough.

## File Placement Rules

- New API route: `backend/app/api/routes/`.
- New request/response model: `backend/app/api/schemas/`.
- New workflow: `backend/app/application/use_cases/`.
- New stable business object: `backend/app/domain/models/`.
- New interface: `backend/app/domain/ports/`.
- New provider implementation: `backend/app/infrastructure/`.
- New frontend user-facing feature: `frontend/src/features/`.

## Design Rules

Use:

- Facade for top-level workflow.
- Strategy for interchangeable algorithms.
- Adapter for third-party tools.
- Repository for persistence.
- Factory for provider/loader construction.

Avoid:

- Deep inheritance.
- Giant managers.
- Utility dumping grounds.
- Hidden global state.
- Unversioned caches.

## Function And Class Quality

Classes should have one responsibility.

Functions should:

- Have clear inputs and outputs.
- Be small enough to test.
- Avoid hidden IO.
- Return structured results instead of ambiguous tuples when data grows.

Acceptable inheritance:

- `BaseLoader` for common loader contract and safety behavior.

Preferred composition:

- `UnifiedLoader` contains specialist loaders.
- Use cases contain ports/services.

## Testing Expectations

Every meaningful change should include at least one of:

- Unit test.
- Integration test.
- Fixture-based manual test documented in final response.

Always test:

- Cache key changes.
- Retrieval fusion changes.
- Chunking changes.
- API schema changes.
- Citation behavior.

## Performance Rules

- Cache embeddings by model and chunk hash.
- Do not recompute indexes for unchanged sources.
- Use bounded concurrency for batch ingestion.
- Do not keep raw document bodies in query-time memory.
- Prefer persisted indexes and metadata.

## Final Response Requirements

When finishing a coding task, report:

- Files changed.
- Behavior added or changed.
- Tests run.
- Any known gaps.

Keep final responses concise but specific.
