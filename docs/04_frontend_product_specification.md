# Frontend Product Specification

## Frontend Philosophy

The frontend should feel like a learning workspace, not a landing page. It should make the system's intelligence visible through sources, citations, retrieval diagnostics, and graph exploration.

Do not overengineer the UI. Build the screens that make the RAG workflow understandable.

## Recommended Frontend Stack

If continuing from the current prototype:

- Keep vanilla HTML/CSS/JS for the immediate MVP.
- Add graph visualization with Cytoscape.js or Sigma.js.

If starting the real project structure:

- Use Vite + React + TypeScript.
- Keep state local until complexity demands a state library.
- Use a small API client module.
- Use component folders by feature.

React is not required for the hackathon, but TypeScript helps protect API contracts as the app grows.

## Layout

Use a three-zone workspace:

```text
Left Panel        Center Panel              Right Panel
Sources          Chat / Source Guide        Evidence / Graph / Diagnostics
Workspaces       User questions             Citations
Index status     Answers                    Graph explorer
```

## Primary Views

### 1. Workspace View

Purpose:

- Create/select workspace.
- See source count, chunk count, index status.

Required elements:

- Workspace selector.
- Add source button.
- Index status indicator.
- Cache/index version only in diagnostics, not primary UI.

### 2. Source Ingestion View

Purpose:

- Upload files or add URL.
- Show progress.
- Show partial success/failure.

Required elements:

- Drag-and-drop file area.
- URL input.
- Supported source labels.
- Progress timeline: loading, chunking, embedding, indexing, graphing.

### 3. Chat View

Purpose:

- Ask grounded questions.
- Show answer with citations.

Required elements:

- Message stream.
- Retrieval mode selector: Auto, Hybrid, Semantic, Keyword, Graph.
- Answer cards with citation markers.
- "Not enough evidence" state.

### 4. Evidence Panel

Purpose:

- Make retrieved context visible.

Required elements:

- Source cards.
- Chunk excerpts.
- Score/relevance bucket.
- Retriever contribution labels: semantic, keyword, graph.
- Open source location when available.

### 5. Graph Explorer

Purpose:

- Let the user move through sources, chunks, and concepts.

Required elements:

- Pan/zoom graph.
- Node search.
- Click node to inspect evidence.
- Expand neighbors.
- Highlight nodes used in current answer.

### 6. Source Guide

Purpose:

- Give immediate learning value after ingestion.

Required sections:

- Summary.
- Key topics.
- Glossary.
- Suggested questions.
- Source coverage notes.

## Visual Design

Tone:

- Modern but calm.
- Technical but not intimidating.
- More workspace than sci-fi dashboard.

Avoid:

- Decorative clutter.
- Giant hero sections.
- Hidden retrieval details.
- Animations that slow work.

Use:

- Dense source cards.
- Clear status badges.
- Tabs for Evidence, Graph, Diagnostics.
- Compact buttons with icons.
- Responsive layout that keeps chat usable on small screens.

## Frontend API Contract

The frontend should not know provider details. It should know:

- Workspaces.
- Sources.
- Ingestion jobs.
- Chat answers.
- Citations.
- Graph nodes/edges.
- Diagnostics.

It should not know:

- Which SDK generated embeddings.
- Which exact vector database is used.
- How BM25 is implemented.
- Prompt internals.

## UX Acceptance Criteria

- User can complete the demo without reading documentation.
- Every answer exposes evidence.
- Retrieval mode is visible but not mandatory.
- Graph explorer adds understanding, not decoration.
- Errors are written in human language.
