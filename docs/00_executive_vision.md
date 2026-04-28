# Executive Vision

## Product

**MultiRAG Learning System** is a source-grounded AI learning workspace. A user imports PDFs, markdown notes, text files, web pages, and later code repositories. The system indexes the material, answers questions with citations, generates source guides, and lets the user explore relationships through a graph.

The project is inspired by NotebookLM, but it is not a clone. The differentiator is retrieval transparency:

- Semantic search for meaning.
- BM25 keyword search for exact terms.
- Graph retrieval for relationships.
- Citations and source cards for trust.
- A graph explorer for learning by movement through concepts.

## Engineering Goal

Build the project as if it may survive beyond the hackathon:

- Fast enough on a laptop.
- Memory-aware.
- Modular enough to replace vector databases, LLMs, graph stores, and embedding providers.
- Simple enough that a small team can understand it.
- Tested around the contracts that matter.

## Senior Engineering Interpretation

The system should be designed like a small production AI product:

- Public entry points are clear.
- Core domain models are stable.
- External tools are behind adapters.
- Loading, chunking, indexing, retrieval, graphing, and generation have separate responsibilities.
- Caching is deliberate, versioned, and invalidated correctly.
- Observability exists from the first useful version.
- The UI explains what happened without exposing unnecessary complexity.

## What We Already Have

The `MultRAG System` folder contains a prototype:

- Vanilla HTML/CSS/JS frontend.
- FastAPI backend inside a notebook.
- PDF, markdown, text, and URL ingestion.
- FAISS vector search.
- Local `sentence-transformers/all-MiniLM-L6-v2` embeddings.
- Gemini generation.
- In-memory session store.

This is a valuable spike. The production-style project should extract its useful behavior into a real backend service.

## Strategic Decisions

1. Use a **multi-index retrieval architecture**, not three vector databases.
2. Keep the domain independent from infrastructure providers.
3. Prefer local-first open-source infrastructure for the hackathon.
4. Make hybrid retrieval the default.
5. Add graph retrieval as a focused relationship layer.
6. Cache expensive stages: extraction, chunking, embeddings, retrieval, graph, source guides, and answers.
7. Build the frontend as a practical workspace, not a marketing page.
8. Keep agent instructions close to the codebase so future AI agents preserve architecture.

## Definition Of Success

A successful demo should show:

1. Import sources.
2. Build indexes.
3. Ask a question.
4. Receive a grounded answer with citations.
5. Inspect source cards.
6. Open the graph explorer.
7. Ask a relationship question.
8. Generate a source guide.

The user should feel: "This system helps me understand my material, and I can see why it answered the way it did."
