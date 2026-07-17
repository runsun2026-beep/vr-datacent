"""SQLite connection helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(database_path: str | Path = ":memory:") -> sqlite3.Connection:
    """Open a SQLite connection with foreign-key enforcement enabled."""
    if database_path != ":memory:":
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        database_path = path

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
