# Code Review Checklist

Use this checklist for every implementation pass.

## Architecture

- Domain layer does not import infrastructure or API frameworks.
- API routes are thin.
- Use cases orchestrate but do not contain provider-specific details.
- Third-party SDKs are behind adapters.
- New abstractions solve a real repeated problem.

## Retrieval

- All retrievers return the same result shape.
- Hybrid fusion is deterministic.
- Scores and ranks are exposed in diagnostics.
- Retrieval mode is explicit.
- Empty retrieval is handled safely.

## Citations

- Every grounded answer includes citations.
- Citation metadata includes source id, title, location, chunk id, and excerpt.
- Citation verifier catches missing or invalid chunk ids.

## Caching

- Cache key includes model/provider/config versions.
- Cache invalidates on workspace index version change.
- Cache has a size or lifecycle plan.
- Cached answers are not served when citations cannot be verified.

## Performance

- Batch operations use bounded concurrency.
- Large files are not fully retained after chunking unless needed.
- Index handles are lazy-loaded or released.
- No unnecessary embedding recomputation.

## Frontend

- UI shows ingestion progress.
- UI shows evidence, not only final answer.
- Graph is useful and inspectable.
- Errors are understandable.
- Text fits on small screens.

## Testing

- Unit tests cover changed pure logic.
- Integration tests use fake providers where possible.
- Fixtures are small and deterministic.
- Manual demo path is still valid.

## Maintainability

- Names reveal responsibility.
- No catch-all utility files.
- No duplicate prompt or cache key logic.
- Comments explain non-obvious decisions only.
