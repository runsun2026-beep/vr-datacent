"""Runnable mock JSON interface for Blender development.

Usage: python -m backend.api.mock_api
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.database.connection import connect
from backend.database.repository import InventoryRepository
from backend.database.schema import create_schema
from backend.services.inventory_service import get_visualization_devices
from mock_data.seed import seed_mock_inventory

DEFAULT_DATABASE = Path("data/dcverse_mock.sqlite3")


def build_mock_payload(database_path: str | Path = DEFAULT_DATABASE) -> list[dict[str, object | None]]:
    """Ensure the local mock database exists, then return its visualization payload."""
    connection = connect(database_path)
    try:
        create_schema(connection)
        seed_mock_inventory(connection)
        return get_visualization_devices(InventoryRepository(connection))
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export DCVerse mock inventory as JSON.")
    parser.add_argument("--database", default=str(DEFAULT_DATABASE), help="SQLite database path")
    args = parser.parse_args()
    print(json.dumps(build_mock_payload(args.database), indent=2))


if __name__ == "__main__":
    main()
