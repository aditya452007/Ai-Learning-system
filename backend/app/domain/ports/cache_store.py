"""Cache store port for versioned workflow caches."""

from __future__ import annotations

from typing import Any, Protocol


class CacheStorePort(Protocol):
    def get_json(self, namespace: str, key: str) -> dict[str, Any] | list[Any] | None:
        ...

    def set_json(self, namespace: str, key: str, value: dict[str, Any] | list[Any]) -> None:
        ...

    def delete_namespace(self, namespace: str) -> None:
        ...

