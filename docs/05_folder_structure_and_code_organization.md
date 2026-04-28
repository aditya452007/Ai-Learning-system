# Folder Structure And Code Organization

## Organization Style

Use a **hybrid domain-feature structure**:

- Domain and application layers are organized by responsibility.
- API and frontend are organized by feature.
- Infrastructure adapters are organized by provider type.

This avoids two common problems:

- Pure technical folders that scatter a feature across too many places.
- Pure feature folders that duplicate shared domain concepts.

## Proposed Repository Structure

```text
multi-rag-learning-system/
  backend/
    pyproject.toml
    app/
      __init__.py
      main.py
      api/
        __init__.py
        dependencies.py
        routes/
          workspaces.py
          sources.py
          chat.py
          graph.py
          source_guides.py
          health.py
        schemas/
          workspace_schemas.py
          source_schemas.py
          chat_schemas.py
          graph_schemas.py
      application/
        rag_learning_system.py
        use_cases/
          create_workspace.py
          ingest_sources.py
          ask_question.py
          generate_source_guide.py
          get_graph.py
        services/
          query_planner.py
          context_builder.py
          citation_verifier.py
      domain/
        models/
          base.py
          workspace.py
          source_document.py
          document_chunk.py
          retrieval.py
          graph.py
          answer.py
        ports/
          source_loader.py
          chunker.py
          embedding_provider.py
          vector_store.py
          keyword_store.py
          graph_store.py
          generation_provider.py
          cache_store.py
          workspace_repository.py
        services/
          chunk_hashing.py
          retrieval_fusion.py
      infrastructure/
        config/
          settings.py
          logging.py
        loaders/
          base_loader.py
          unified_loader.py
          pdf_loader.py
          markdown_loader.py
          text_loader.py
          web_loader.py
          code_loader.py
        chunkers/
          recursive_text_chunker.py
          markdown_chunker.py
          code_chunker.py
        embeddings/
          sentence_transformer_embeddings.py
          embedding_cache.py
        retrieval/
          faiss_vector_store.py
          qdrant_vector_store.py
          bm25_store.py
          graph_networkx_store.py
        generation/
          gemini_provider.py
          prompt_templates.py
        persistence/
          file_workspace_repository.py
          sqlite_metadata_store.py
          disk_cache_store.py
      tests/
        unit/
        integration/
        fixtures/
  frontend/
    package.json
    src/
      app/
      features/
        workspace/
        sources/
        chat/
        evidence/
        graph/
        source-guide/
      shared/
        api/
        components/
        types/
        styles/
  data/
    workspaces/
  docs/
  scripts/
    dev.ps1
    seed_demo_workspace.py
```

## Public Package Entry Point

The backend package should expose only stable objects in `backend/app/__init__.py`.

Example intent:

```python
from app.application.rag_learning_system import RagLearningSystem
from app.infrastructure.config.settings import Settings

__all__ = ["RagLearningSystem", "Settings"]
```

This follows the "reception desk" pattern from the reference PDF: users of the package should not need to know every internal room.

## Main Orchestrator

`RagLearningSystem` is the application facade:

- It coordinates use cases.
- It receives dependencies through constructor injection.
- It does not directly parse PDFs, call Gemini, run FAISS, or render graph data.

This class is allowed to know workflow order. It is not allowed to become a giant utility class.

## Domain Models

Domain models should be stable and provider-free.

Use:

- Dataclasses or Pydantic-free domain models.
- Enums for controlled values.
- Explicit ids and timestamps.
- Metadata dictionaries only for truly flexible fields.

API schemas can use Pydantic separately.

## Ports And Adapters

Ports define what the application needs:

- `VectorStorePort`
- `KeywordStorePort`
- `GraphStorePort`
- `GenerationProviderPort`
- `EmbeddingProviderPort`
- `CacheStorePort`

Adapters implement those ports:

- `FaissVectorStore`
- `QdrantVectorStore`
- `Bm25Store`
- `GeminiProvider`
- `DiskCacheStore`

Rule: application code imports ports, not adapters.

## Tests Structure

Unit tests:

- Domain services.
- Fusion.
- Cache key generation.
- Chunking.
- Query planning.

Integration tests:

- API with fake providers.
- Ingestion pipeline with local fixture files.
- Workspace persistence.

Fixture files:

- Small PDF.
- Markdown article.
- Text file.
- Tiny code sample.

## Naming Rules

- Classes are nouns: `UnifiedLoader`, `RetrievalFusionService`.
- Use cases are verbs: `AskQuestion`, `IngestSources`.
- Ports end with `Port`.
- Infrastructure implementations name the provider: `FaissVectorStore`.
- API schemas end with `Request` or `Response`.

## Files To Avoid

Avoid catch-all files:

- `utils.py`
- `helpers.py`
- `common.py`
- `manager.py` without a specific domain meaning.

If a utility is needed, name it by responsibility:

- `chunk_hashing.py`
- `token_counting.py`
- `cache_keys.py`
