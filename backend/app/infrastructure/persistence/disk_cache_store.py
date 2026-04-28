"""Small JSON disk cache with namespaced keys."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any


class DiskCacheStore:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def get_json(self, namespace: str, key: str) -> dict[str, Any] | list[Any] | None:
        path = self._path(namespace, key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set_json(self, namespace: str, key: str, value: dict[str, Any] | list[Any]) -> None:
        path = self._path(namespace, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2, default=str), encoding="utf-8")

    def delete_namespace(self, namespace: str) -> None:
        directory = self.root_dir / self._safe(namespace)
        if directory.exists():
            shutil.rmtree(directory)

    def _path(self, namespace: str, key: str) -> Path:
        return self.root_dir / self._safe(namespace) / f"{self._safe(key)}.json"

    def _safe(self, value: str) -> str:
        return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)[:180]

