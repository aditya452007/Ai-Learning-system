"""Placeholder for a future SQLite metadata adapter.

The MVP stores manifests and chunks as JSON/JSONL so the data remains easy to
inspect during demos. This class exists as the named extension point from the
architecture docs.
"""


class SqliteMetadataStore:
    def __init__(self) -> None:
        raise NotImplementedError("Use FileWorkspaceRepository for the MVP.")

