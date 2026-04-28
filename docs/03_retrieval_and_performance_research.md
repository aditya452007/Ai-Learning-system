# Retrieval And Performance Research

## Retrieval Strategy

The project should use multi-index retrieval:

- **Semantic retrieval**: finds concepts and paraphrases.
- **Keyword retrieval**: finds exact names, functions, commands, and errors.
- **Graph retrieval**: finds relationships and neighboring concepts.
- **Hybrid retrieval**: combines semantic and keyword results.
- **Auto retrieval**: chooses or combines modes based on query shape.

## Query Type Matrix

| Query Type | Example | Best Retriever |
| --- | --- | --- |
| Conceptual | "Explain the architecture" | Semantic or hybrid |
| Exact term | "Where is GraphRAG mentioned?" | BM25 |
| Error/code | "NullPointerException" | BM25 |
| Relationship | "What depends on the loader?" | Graph |
| Broad research | "Compare retrieval strategies" | Hybrid plus graph |
| Not in source | "Who won yesterday?" | Refusal or external search later |

## Fusion

Use Reciprocal Rank Fusion for MVP:

```text
score = sum(1 / (k + rank))
```

Defaults:

- `k = 60`
- semantic top_k = 12
- BM25 top_k = 12
- fused top_k = 6

Why RRF:

- Simple.
- Stable.
- Works without score normalization.
- Rewards chunks found by multiple retrievers.

## Reranking

Do not add reranking before hybrid retrieval works.

Post-MVP options:

- Local cross-encoder reranker for quality.
- API reranker for stronger relevance.
- LLM reranker only for small candidate sets because it is slower and costlier.

## Chunking

### Text And Markdown

Use structure-aware splitting:

- Prefer headings and paragraphs.
- Preserve heading path.
- Keep chunks around 500 to 900 tokens.
- Use overlap around 80 to 120 tokens.

### PDF

Extract page text and keep page number metadata.

Chunk rules:

- Do not mix many distant pages into one chunk.
- Include page number in citation.
- Clean repeated headers/footers if obvious.

### Code

For MVP, basic file/function chunks are acceptable.

Post-MVP:

- Use tree-sitter.
- Keep functions/classes intact.
- Store line ranges.
- Extract imports, definitions, calls, and class relationships.

## Embeddings

MVP default:

- `sentence-transformers/all-MiniLM-L6-v2`
- Fast, local, low memory.
- Good enough for hackathon-sized datasets.

Post-MVP options:

- BGE small/base models for stronger local retrieval.
- OpenAI/Cohere embeddings through adapters if quality is more important than local-only execution.

## Vector Index Performance

### FAISS Local Adapter

Use when:

- Dataset is small to medium.
- Metadata filtering can be handled outside the vector store.
- You want the fastest local hackathon path.

Implementation notes:

- Normalize embeddings.
- Use `IndexFlatIP` for small datasets.
- Move to HNSW or IVF only after measuring.
- Persist index to workspace folder.
- Keep chunk metadata in SQLite or JSONL.

### Qdrant Adapter

Use when:

- Persistent metadata filtering matters.
- Workspaces may grow.
- You want quantization and HNSW tuning.

Performance controls:

- HNSW parameters.
- Payload indexing only for useful fields.
- Scalar or binary quantization later.
- On-disk storage for larger collections.

## Memory Controls

Required:

- Stream file reads when possible.
- Do not keep all raw document content in query-time memory.
- Store chunks on disk.
- Keep only active workspace indexes loaded.
- Add an LRU cache for workspace index handles.
- Provide a `release_workspace(workspace_id)` operation.

Optional:

- Quantize vectors for larger workspaces.
- Lazy-load graph data.
- Background index compaction.

## Caching For Speed

Expected high-value caches:

- Embedding cache: prevents expensive recomputation.
- Retrieval cache: speeds repeated questions.
- Source guide cache: avoids repeated LLM calls.
- Answer cache: useful for demos and repeated study questions.

Cache keys must include:

- Workspace id.
- Source hash or chunk hash.
- Model name.
- Prompt version.
- Index version.

## Performance Budget

For the hackathon target:

| Operation | Target |
| --- | --- |
| Health check | under 100 ms |
| Retrieval only | under 500 ms for small workspace |
| Cached answer | under 1 second |
| Uncached answer | under 5 seconds, provider dependent |
| 1,000 chunk indexing | under 60 seconds on CPU |
| Graph endpoint | under 1 second for MVP graph |

## Reliability Rules

- Retrieval failure should not crash the app.
- Graph failure should not block chat.
- LLM failure should return retrieved citations plus a clear error.
- Partial ingestion is better than all-or-nothing failure.
