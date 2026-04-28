# Software Requirements Specification

## 1. Purpose

Define the functional and nonfunctional requirements for a hackathon-ready but enterprise-minded RAG learning system.

## 2. Scope

The system ingests user-provided knowledge sources, builds retrieval indexes, answers questions from those sources, exposes citations, and visualizes relationships.

## 3. User Personas

### Student

Wants to upload course material and ask questions, generate study guides, and understand relationships between topics.

### Developer

Wants to ingest a small codebase and ask how modules, functions, or flows work.

### Judge Or Evaluator

Wants to see that the project is more than a chatbot wrapper and has a real retrieval architecture.

## 4. Functional Requirements

### FR-001 Workspace Management

- The system shall create a workspace.
- The system shall persist workspace metadata.
- The system shall isolate sources, indexes, caches, and graph data per workspace.

### FR-002 Source Ingestion

- The system shall ingest PDF, markdown, text, and URL sources.
- The system should support local code folder ingestion after the MVP foundation.
- The system shall calculate a content hash for every source.
- The system shall avoid reprocessing an unchanged source.

### FR-003 Document Loading

- The system shall provide a unified loader interface.
- The system shall route sources to specialist loaders based on type.
- The system shall validate source type, size, and availability.
- The system shall return partial success when batch ingestion contains some bad sources.

### FR-004 Chunking

- The system shall split documents into retrievable chunks.
- The system shall preserve source citation metadata.
- The system shall support chunking strategies by source type.
- The system should support AST-aware code chunking for code repositories.

### FR-005 Indexing

- The system shall build a semantic vector index.
- The system shall build a BM25 keyword index.
- The system shall build a graph index of sources, chunks, and concepts.
- The system shall version indexes so caches can be invalidated safely.

### FR-006 Retrieval

- The system shall support retrieval modes: `semantic`, `keyword`, `hybrid`, `graph`, and `auto`.
- The system shall use hybrid retrieval as the default.
- The system shall return retrieved chunks, scores, and retriever diagnostics.
- The system shall support metadata filtering by source, source type, and date when available.

### FR-007 Answer Generation

- The system shall generate answers from retrieved context.
- The system shall cite source chunks in the response.
- The system shall refuse or qualify answers when evidence is insufficient.
- The system shall support provider replacement for LLMs.

### FR-008 Source Guide

- The system shall generate a source guide with summary, topics, glossary, and suggested questions.
- The system shall cache source guides by source hash and prompt version.

### FR-009 Graph Explorer

- The system shall expose graph nodes and edges for visualization.
- The system shall support click-to-inspect source evidence.
- The system should highlight graph nodes used by the latest answer.

### FR-010 Diagnostics

- The system shall expose retrieval mode, latency, cache hit status, and citation count for each answer.
- The system shall log ingestion, indexing, retrieval, and generation events.

## 5. Nonfunctional Requirements

### NFR-001 Performance

- A small workspace of 1,000 to 10,000 chunks should answer typical questions in under 5 seconds after indexing.
- Retrieval-only latency should target under 500 ms for cached or small local indexes.
- Indexing should run asynchronously or provide progress status.

### NFR-002 Memory Efficiency

- The system shall avoid loading all raw sources into memory during normal query flow.
- The system shall store chunks and metadata on disk.
- Embedding and retrieval caches shall have size limits.
- The vector store shall support persistence and incremental updates.

### NFR-003 Reliability

- One failed source shall not crash a batch ingestion job.
- External provider failures shall produce clear user-facing errors.
- The system shall degrade gracefully if graph extraction fails.

### NFR-004 Maintainability

- Core domain code shall not import FastAPI, vector database clients, or LLM SDKs.
- External providers shall be accessed through interfaces and adapters.
- Each module shall have one reason to change.
- Public APIs shall be documented with request and response schemas.

### NFR-005 Testability

- Retrieval, chunking, caching, and fusion logic shall be unit tested.
- API routes shall be integration tested with fake providers.
- LLM-dependent behavior shall be tested with deterministic fixtures where possible.

### NFR-006 Security And Privacy

- API keys shall come from environment variables or a local `.env`.
- Source files shall remain local unless the selected LLM provider requires remote calls.
- The UI shall indicate when an answer uses a remote model provider.
- URL ingestion shall enforce timeouts and size limits.

### NFR-007 Observability

- Logs shall include workspace id, request id, operation, duration, and outcome.
- Metrics should include cache hit rate, retrieval latency, generation latency, indexed chunks, and error counts.

## 6. Constraints

- Hackathon MVP must be achievable by a small team.
- Current prototype uses Gemini and FAISS; migration should be incremental.
- Avoid distributed infrastructure unless it directly improves the demo.

## 7. Acceptance Criteria

- Upload a PDF or markdown file and ask a grounded question.
- See citations attached to the answer.
- Ask an exact keyword question and see BM25 contribute.
- Ask a conceptual question and see semantic retrieval contribute.
- Open graph explorer and inspect related concepts.
- Restart backend and keep a persisted workspace available.
