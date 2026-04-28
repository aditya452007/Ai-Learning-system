# RAG Engineering Skill

Use this skill when implementing or modifying retrieval, ingestion, indexing, graph, caching, or grounded generation.

## Mental Model

A RAG system is a pipeline:

```text
Source -> Document -> Chunk -> Indexes -> Retrieval -> Context -> Generation -> Citation Verification
```

Each stage must preserve traceability back to the source.

## Retrieval Concepts

### Vector Search

Purpose:

- Find semantically similar chunks.

Key rules:

- Embed chunks and queries with the same model.
- Include embedding model in cache keys.
- Store chunk ids with vectors.
- Keep metadata outside FAISS if using FAISS.

### BM25 Search

Purpose:

- Find exact terms.

Best for:

- Function names.
- Error messages.
- Technical terms.
- Product names.
- Commands.

Key rules:

- Build BM25 from the same chunk corpus as vector search.
- Return the same `RetrievalResult` shape as vector search.

### Graph Retrieval

Purpose:

- Find relationships.

MVP graph:

- Source nodes.
- Chunk nodes.
- Concept nodes.
- `contains`, `mentions`, and `related_to` edges.

Key rules:

- Graph should enhance retrieval and exploration.
- Graph failure must not break chat.

### Hybrid Search

Purpose:

- Combine semantic and keyword strengths.

MVP algorithm:

- Query vector retriever.
- Query BM25 retriever.
- Fuse with Reciprocal Rank Fusion.
- Return top fused chunks.

## Grounded Generation Rules

The LLM receives:

- User query.
- Retrieved context.
- Citation ids.
- Instruction to answer only from context.

The LLM must not receive:

- Entire raw workspace.
- API keys.
- Unbounded chat history.

If evidence is weak:

- Return an insufficient-evidence answer.
- Suggest adding sources or trying another retrieval mode.

## Cache Rules

Cache keys must include the parts that change behavior:

- workspace id.
- source hash.
- chunk hash.
- embedding model.
- prompt version.
- index version.
- retrieval mode.
- model name.

Never reuse cached answers after index version changes.

## Frontend Interaction

The frontend should show:

- Answer.
- Citations.
- Evidence cards.
- Retrieval mode.
- Diagnostics.
- Graph nodes when relevant.

The frontend should not know:

- FAISS internals.
- Gemini prompt internals.
- BM25 implementation details.

## Senior Engineer Checklist

Before committing retrieval work:

- Can this provider be replaced?
- Are citations preserved?
- Is cache invalidation correct?
- Does the result shape match other retrievers?
- Are errors typed and user-readable?
- Is there at least one test or fixture proving behavior?
