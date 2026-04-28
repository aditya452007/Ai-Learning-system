"""Domain-specific exceptions mapped by API adapters."""


class MultiRagError(Exception):
    code = "multi_rag_error"


class SourceLoadError(MultiRagError):
    code = "source_load_error"


class UnsupportedSourceError(SourceLoadError):
    code = "unsupported_source"


class ChunkingError(MultiRagError):
    code = "chunking_error"


class IndexingError(MultiRagError):
    code = "indexing_error"


class RetrievalError(MultiRagError):
    code = "retrieval_error"


class GenerationError(MultiRagError):
    code = "generation_error"


class WorkspaceNotFoundError(MultiRagError):
    code = "workspace_not_found"

