"""File system scanner with strict fail-closed exclusion rules."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator, Set

EXCLUDED_DIR_NAMES: Set[str] = {
    ".git", ".hg", ".svn", ".bzr",
    ".venv", "venv", "env", ".env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", "dist", "build", "target", "eggs", ".eggs",
}

class FileScanner:
    """Safe, recursive file scanner that ignores caches, environments, and hidden metadata."""

    def __init__(self, root: Path, max_depth: int = 15, max_files: int = 5000) -> None:
        self.root = root.resolve()
        self.max_depth = max_depth
        self.max_files = max_files

    def scan_python_files(self) -> list[Path]:
        """Collect all .py files within boundaries."""
        results: list[Path] = []
        for path in self._walk(self.root, current_depth=0):
            if path.suffix == ".py":
                results.append(path)
                if len(results) >= self.max_files:
                    break
        return sorted(results)

    def _walk(self, current: Path, current_depth: int) -> Iterator[Path]:
        if current_depth > self.max_depth:
            return

        try:
            entries = sorted(current.iterdir(), key=lambda p: p.name)
        except (PermissionError, OSError):
            return

        for entry in entries:
            name = entry.name
            if name.startswith(".") and name != ".":
                continue
            if name in EXCLUDED_DIR_NAMES:
                continue

            if entry.is_symlink():
                continue

            if entry.is_dir():
                yield from self._walk(entry, current_depth + 1)
            elif entry.is_file():
                yield entry
