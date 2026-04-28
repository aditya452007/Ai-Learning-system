# MultiRAG Learning System Backend

This backend implements the documented hexagonal-lite RAG architecture:

- FastAPI route adapters.
- Application use cases and `RagLearningSystem` facade.
- Provider-free domain models and ports.
- Local file-backed workspace persistence.
- PDF, markdown, text, URL, and basic code loaders.
- Chunking, local embeddings, semantic search, BM25, hybrid RRF, graph DTOs.
- Gemini adapter with a deterministic extractive fallback.

## Run

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/health`.

## Test

```powershell
cd backend
python -m pytest
```

## Demo Seed

```powershell
python ..\scripts\seed_demo_workspace.py
```

