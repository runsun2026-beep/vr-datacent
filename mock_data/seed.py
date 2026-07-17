"""Deterministic mock inventory used by development and demos."""

from __future__ import annotations

import sqlite3

from backend.database.repository import InventoryRepository


def seed_mock_inventory(connection: sqlite3.Connection) -> None:
    """Load the small S41 fixture once; safe to call repeatedly."""
    if connection.execute("SELECT 1 FROM data_centers LIMIT 1").fetchone():
        return
    repository = InventoryRepository(connection)
    data_center_id = repository.create_data_center("Singapore Data Center 01", "DC-SG-01")
    room_id = repository.create_room(data_center_id, "Server Hall 41", "S41")
    rack_001 = repository.create_rack(room_id, "Rack-001")
    rack_002 = repository.create_rack(room_id, "Rack-002")
    repository.create_device(rack_001, hostname="GPU001", device_type="GPU", u_position=12, u_height=2, status="running", serial_number="SN-GPU-001", asset_tag="AST-1001", management_ip="10.41.0.11", business_ip="172.16.41.11", cpu_model="AMD EPYC 9354", memory_gb=512, gpu_count=8, power_watts=2200)
    repository.create_device(rack_001, hostname="GPU002", device_type="GPU", u_position=16, u_height=2, status="warning", serial_number="SN-GPU-002", asset_tag="AST-1002", management_ip="10.41.0.12", business_ip="172.16.41.12", cpu_model="AMD EPYC 9354", memory_gb=512, gpu_count=8, power_watts=2200)
    repository.create_device(rack_001, hostname="SW001", device_type="Switch", u_position=40, u_height=1, status="running", serial_number="SN-SW-001", asset_tag="AST-1101", management_ip="10.41.0.21", business_ip=None, cpu_model=None, memory_gb=None, gpu_count=None, power_watts=180)
    repository.create_device(rack_002, hostname="CPU001", device_type="CPU", u_position=10, u_height=1, status="offline", serial_number="SN-CPU-001", asset_tag="AST-2001", management_ip="10.41.0.31", business_ip="172.16.41.31", cpu_model="Intel Xeon Gold 6430", memory_gb=256, gpu_count=0, power_watts=700)
