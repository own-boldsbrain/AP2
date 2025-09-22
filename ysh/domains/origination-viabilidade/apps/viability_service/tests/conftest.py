"""Pytest configuration for the viability service tests."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_app_on_path() -> None:
    root = Path(__file__).resolve().parents[1]
    app_dir = root / "app"
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(root))


_ensure_app_on_path()

__all__ = []
