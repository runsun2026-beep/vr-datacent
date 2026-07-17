"""Regression tests for the Sprint 2 mock inventory."""

from __future__ import annotations

import unittest

from backend.api.mock_api import build_mock_payload
from backend.database.connection import connect
from backend.database.repository import InventoryRepository
from backend.database.schema import create_schema
from mock_data.seed import seed_mock_inventory


class InventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = connect()
        create_schema(self.connection)
        seed_mock_inventory(self.connection)
        self.repository = InventoryRepository(self.connection)

    def tearDown(self) -> None:
        self.connection.close()

    def test_mock_data_exports_standard_contract(self) -> None:
        payload = build_mock_payload(":memory:")
        self.assertEqual(4, len(payload))
        gpu_001 = next(device for device in payload if device["hostname"] == "GPU001")
        self.assertEqual("S41", gpu_001["room"])
        self.assertEqual("Rack-001", gpu_001["rack"])
        self.assertEqual(12, gpu_001["u_position"])
        self.assertEqual("GPU", gpu_001["device_type"])
        self.assertEqual("running", gpu_001["status"])

    def test_rejects_overlap_and_rack_overflow(self) -> None:
        rack_id = self.connection.execute("SELECT id FROM racks WHERE name = 'Rack-001'").fetchone()["id"]
        with self.assertRaisesRegex(ValueError, "overlap"):
            self.repository.create_device(rack_id, hostname="OVERLAP", device_type="CPU", u_position=12, status="running")
        with self.assertRaisesRegex(ValueError, "capacity"):
            self.repository.create_device(rack_id, hostname="TOO-TALL", device_type="CPU", u_position=42, u_height=2, status="running")

    def test_seed_is_idempotent(self) -> None:
        seed_mock_inventory(self.connection)
        count = self.connection.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
        self.assertEqual(4, count)


if __name__ == "__main__":
    unittest.main()
