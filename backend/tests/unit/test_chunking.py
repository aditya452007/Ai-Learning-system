from app.domain.models.source_document import LoadedSource, SourceDocument, SourceType
from app.infrastructure.chunkers.markdown_chunker import MarkdownChunker


def test_markdown_chunker_preserves_heading_metadata() -> None:
    source = SourceDocument(
        id="source_1",
        workspace_id="workspace_1",
        title="notes.md",
        source_type=SourceType.MARKDOWN,
        uri="notes.md",
        content_hash="hash",
    )
    loaded = LoadedSource(
        title="notes.md",
        source_type=SourceType.MARKDOWN,
        uri="notes.md",
        text="# Architecture\n\nHybrid retrieval combines semantic and keyword search.",
        content_hash="hash",
    )

    chunks = MarkdownChunker(chunk_size_tokens=20, overlap_tokens=4).chunk(source, loaded)

    assert chunks
    assert chunks[0].location.heading == "Architecture"
    assert "Hybrid retrieval" in chunks[0].text

