# Implementation Roadmap

## Phase 0 - Current Prototype Audit

Goal: preserve useful prototype behavior.

Tasks:

- Confirm current endpoints and frontend expectations.
- Extract reusable logic from notebook.
- Identify environment variables.
- Prepare one reliable demo document.

Exit criteria:

- We know exactly what behavior must survive extraction.

## Phase 1 - Backend Skeleton

Goal: create the real service foundation.

Tasks:

- Create backend package.
- Add FastAPI app and health route.
- Add settings, logging, and exception mapping.
- Add domain models and ports.
- Add `RagLearningSystem` facade.

Exit criteria:

- Service starts.
- Health endpoint works.
- Unit tests run.

## Phase 2 - Source Loading And Chunking

Goal: implement the document highway.

Tasks:

- Add `BaseLoader`.
- Add `UnifiedLoader`.
- Add PDF, markdown, text, and URL loaders.
- Add chunking strategies.
- Add content hashing.
- Add source extraction and chunk caches.

Exit criteria:

- Uploading files produces persisted `SourceDocument` and `DocumentChunk` records.

## Phase 3 - Vector Retrieval

Goal: recreate semantic search properly.

Tasks:

- Add embedding provider port.
- Add sentence-transformer adapter.
- Add embedding cache.
- Add FAISS vector store adapter.
- Persist vector indexes by workspace.

Exit criteria:

- Semantic retrieval returns cited chunks after restart.

## Phase 4 - BM25 And Hybrid Retrieval

Goal: build the first true MultiRAG version.

Tasks:

- Add keyword store port.
- Add BM25 implementation.
- Add retrieval fusion service.
- Add retrieval diagnostics.
- Make hybrid default.

Exit criteria:

- Exact terms improve compared with vector-only retrieval.
- Chat response shows semantic and keyword contributions.

## Phase 5 - Grounded Chat

Goal: produce trustworthy answers.

Tasks:

- Add generation provider port.
- Add Gemini adapter.
- Add prompt templates.
- Add context builder.
- Add citation verifier.
- Add answer cache.

Exit criteria:

- Answers cite source chunks.
- Unsupported questions trigger insufficient-evidence behavior.

## Phase 6 - Graph Layer

Goal: add relationship exploration.

Tasks:

- Add graph store port.
- Add NetworkX graph adapter.
- Extract concepts from chunks.
- Build source/chunk/concept graph.
- Add graph endpoint.

Exit criteria:

- Frontend can render graph nodes and inspect evidence.

## Phase 7 - Frontend Workspace

Goal: make the product usable.

Tasks:

- Add workspace selector.
- Add ingestion progress.
- Add chat retrieval mode selector.
- Add evidence panel.
- Add graph panel.
- Add source guide panel.

Exit criteria:

- A user can complete the demo from the browser.

## Phase 8 - Evaluation And Hardening

Goal: make the system credible.

Tasks:

- Add golden question set.
- Add retrieval tests.
- Add API integration tests.
- Add logging and metrics.
- Add demo seed script.

Exit criteria:

- The team can measure retrieval quality and demo reliability.

## Hackathon Priority Order

1. Backend skeleton.
2. Loaders and chunks.
3. Vector retrieval.
4. BM25 and hybrid retrieval.
5. Grounded chat with citations.
6. Evidence panel.
7. Graph explorer.
8. Source guide.
9. Polish and demo script.

## Do Not Start With

- Authentication.
- Hosted vector database.
- Microservices.
- Streaming UI.
- Advanced graph extraction.
- Agentic multi-step research.

These are future improvements after the core loop is reliable.
