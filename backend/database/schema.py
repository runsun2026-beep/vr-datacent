"""Database schema for the DCVerse inventory hierarchy."""

from __future__ import annotations

import sqlite3


SCHEMA = """
CREATE TABLE IF NOT EXISTS data_centers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    data_center_id INTEGER NOT NULL REFERENCES data_centers(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    UNIQUE(data_center_id, code)
);

CREATE TABLE IF NOT EXISTS racks (
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    total_u INTEGER NOT NULL DEFAULT 42 CHECK(total_u > 0),
    UNIQUE(room_id, name)
);

CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY,
    rack_id INTEGER NOT NULL REFERENCES racks(id) ON DELETE CASCADE,
    hostname TEXT NOT NULL UNIQUE,
    device_type TEXT NOT NULL,
    u_position INTEGER NOT NULL CHECK(u_position > 0),
    u_height INTEGER NOT NULL DEFAULT 1 CHECK(u_height > 0),
    status TEXT NOT NULL CHECK(status IN ('running', 'warning', 'offline')),
    serial_number TEXT,
    asset_tag TEXT,
    management_ip TEXT,
    business_ip TEXT,
    cpu_model TEXT,
    memory_gb INTEGER CHECK(memory_gb IS NULL OR memory_gb >= 0),
    gpu_count INTEGER CHECK(gpu_count IS NULL OR gpu_count >= 0),
    power_watts INTEGER CHECK(power_watts IS NULL OR power_watts >= 0)
);

CREATE INDEX IF NOT EXISTS idx_rooms_data_center ON rooms(data_center_id);
CREATE INDEX IF NOT EXISTS idx_racks_room ON racks(room_id);
CREATE INDEX IF NOT EXISTS idx_devices_rack_position ON devices(rack_id, u_position);
"""


def create_schema(connection: sqlite3.Connection) -> None:
    """Create all tables and indexes. Safe to call repeatedly."""
    connection.executescript(SCHEMA)
    connection.commit()
