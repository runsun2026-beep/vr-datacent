"""Repository operations for the data-center inventory."""

from __future__ import annotations

import sqlite3
from typing import Any

from backend.models.entities import DeviceRecord


class InventoryRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create_data_center(self, name: str, code: str) -> int:
        return self._insert("data_centers", {"name": name, "code": code})

    def create_room(self, data_center_id: int, name: str, code: str) -> int:
        return self._insert("rooms", {"data_center_id": data_center_id, "name": name, "code": code})

    def create_rack(self, room_id: int, name: str, total_u: int = 42) -> int:
        return self._insert("racks", {"room_id": room_id, "name": name, "total_u": total_u})

    def create_device(self, rack_id: int, **device: Any) -> int:
        """Insert a device after enforcing rack bounds and non-overlap."""
        required = {"hostname", "device_type", "u_position", "status"}
        missing = required - device.keys()
        if missing:
            raise ValueError(f"Missing required device fields: {', '.join(sorted(missing))}")
        device.setdefault("u_height", 1)
        self._validate_placement(rack_id, device["u_position"], device["u_height"])
        return self._insert("devices", {"rack_id": rack_id, **device})

    def list_devices(self) -> list[DeviceRecord]:
        rows = self.connection.execute(
            """
            SELECT dc.code AS data_center, room.code AS room, rack.name AS rack,
                   rack.total_u AS rack_total_u, device.u_position, device.u_height,
                   device.device_type, device.hostname, device.status,
                   device.serial_number, device.asset_tag, device.management_ip,
                   device.business_ip, device.cpu_model, device.memory_gb,
                   device.gpu_count, device.power_watts
            FROM devices AS device
            JOIN racks AS rack ON rack.id = device.rack_id
            JOIN rooms AS room ON room.id = rack.room_id
            JOIN data_centers AS dc ON dc.id = room.data_center_id
            ORDER BY room.code, rack.name, device.u_position
            """
        ).fetchall()
        return [DeviceRecord(**dict(row)) for row in rows]

    def _validate_placement(self, rack_id: int, u_position: int, u_height: int) -> None:
        if u_position < 1 or u_height < 1:
            raise ValueError("u_position and u_height must both be positive")
        rack = self.connection.execute("SELECT total_u FROM racks WHERE id = ?", (rack_id,)).fetchone()
        if rack is None:
            raise ValueError(f"Rack {rack_id} does not exist")
        if u_position + u_height - 1 > rack["total_u"]:
            raise ValueError("Device exceeds the rack U capacity")
        new_start, new_end = u_position, u_position + u_height - 1
        for device in self.connection.execute(
            "SELECT u_position, u_height FROM devices WHERE rack_id = ?", (rack_id,)
        ):
            start, end = device["u_position"], device["u_position"] + device["u_height"] - 1
            if new_start <= end and start <= new_end:
                raise ValueError("Device U positions overlap")

    def _insert(self, table: str, values: dict[str, Any]) -> int:
        columns = ", ".join(values)
        placeholders = ", ".join("?" for _ in values)
        cursor = self.connection.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", tuple(values.values())
        )
        self.connection.commit()
        return int(cursor.lastrowid)
