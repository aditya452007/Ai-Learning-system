# Golden Evaluation Set

## Factual

- Question: What does hybrid retrieval combine?
  Expected answer: Semantic search and BM25 keyword search.
  Expected source/chunk: demo_notes.md / retrieval chunk.
  Expected retrieval mode: hybrid.
  Notes: Baseline exact answer.

## Exact Keyword

- Question: Where is BM25 mentioned?
  Expected answer: In the hybrid retrieval notes.
  Expected source/chunk: demo_notes.md / retrieval chunk.
  Expected retrieval mode: keyword.
  Notes: Confirms lexical retrieval.

## Relationship

- Question: What does graph retrieval connect?
  Expected answer: Source nodes, chunk nodes, and concept nodes.
  Expected source/chunk: demo_notes.md / graph retrieval chunk.
  Expected retrieval mode: graph.
  Notes: Confirms graph explorer evidence.

## Synthesis

- Question: Why use hybrid retrieval in a learning system?
  Expected answer: It covers conceptual and exact-term questions.
  Expected source/chunk: demo_notes.md / retrieval chunk.
  Expected retrieval mode: hybrid.
  Notes: Requires combining two sentences.

## Unsupported

- Question: Who won yesterday's match?
  Expected answer: Insufficient evidence.
  Expected source/chunk: none.
  Expected retrieval mode: hybrid.
  Notes: Should refuse without source evidence.

