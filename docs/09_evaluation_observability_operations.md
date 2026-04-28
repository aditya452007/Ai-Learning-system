# Evaluation, Observability, And Operations

## Why Evaluation Matters

RAG systems can sound correct while retrieving weak evidence. Evaluation must check retrieval and generation separately.

## Golden Evaluation Set

Create `eval/questions.md` with:

- 10 factual questions.
- 5 exact keyword questions.
- 5 relationship questions.
- 5 synthesis questions.
- 5 questions where the answer is not in the source.

Each item should include:

- Question.
- Expected answer.
- Expected source/chunk.
- Expected retrieval mode.
- Notes.

## Retrieval Metrics

Track:

- Hit@K.
- MRR if expected chunk is known.
- Number of semantic hits.
- Number of keyword hits.
- Number of graph hits.
- Fusion score distribution.
- Retrieval latency.
- Cache hit rate.

## Answer Metrics

Track:

- Citation count.
- Citation coverage.
- Unsupported-answer refusal accuracy.
- User feedback.
- Generation latency.
- Provider error rate.

## Observability

### Logs

Use structured logs:

```json
{
  "request_id": "req_123",
  "workspace_id": "workspace_123",
  "operation": "ask_question",
  "duration_ms": 2430,
  "status": "success",
  "retrieval_mode": "hybrid",
  "retrieval_cache_hit": false,
  "answer_cache_hit": false
}
```

### Metrics

Minimum:

- `ingestion_duration_ms`
- `chunks_created_total`
- `embedding_cache_hit_total`
- `retrieval_duration_ms`
- `generation_duration_ms`
- `chat_errors_total`
- `workspace_index_version`

### Tracing Later

If the project grows, add simple spans:

- load source.
- chunk source.
- embed chunks.
- index chunks.
- retrieve.
- generate.
- verify citations.

## Operational Rules

### API Keys

- Load from `.env` or environment variables.
- Never commit secrets.
- Fail fast at startup if required provider keys are missing for configured provider.

### Local Data

- Store workspaces under `data/workspaces`.
- Add `.gitignore` rules for generated indexes and caches.
- Keep demo fixtures separate from user data.

### Backup Demo

Before every demo:

- Pre-index one workspace.
- Keep one small file upload ready.
- Verify Gemini key.
- Verify graph endpoint.
- Verify reset does not delete demo fixture files.

## Failure Modes

### Provider Down

Behavior:

- Retrieval still returns evidence.
- Generation returns clear error.
- UI offers "show retrieved sources" fallback.

### Vector Index Corrupt

Behavior:

- Detect on load.
- Rebuild from chunks if possible.
- Do not lose source/chunk metadata.

### URL Ingestion Fails

Behavior:

- Return readable error.
- Keep other sources from the batch.
- Show timeout or unsupported content type.

### No Evidence Found

Behavior:

- Do not hallucinate.
- Return insufficient-evidence message.
- Suggest adding sources or changing retrieval mode.

## Production Evolution

When moving beyond hackathon:

- Add authentication.
- Add workspace permissions.
- Add background job queue.
- Add persistent database migrations.
- Add reranking.
- Add stronger graph extraction.
- Add deployment scripts.

Only add these after the local product is stable.
