"""Convert inventory records into the Blender-facing JSON contract."""

from __future__ import annotations

from backend.database.repository import InventoryRepository


def get_visualization_devices(repository: InventoryRepository) -> list[dict[str, object | None]]:
    """Return stable, JSON-serializable device objects for a rendering client."""
    return [{
        "data_center": device.data_center, "room": device.room, "rack": device.rack,
        "rack_total_u": device.rack_total_u, "u_position": device.u_position,
        "u_height": device.u_height, "device_type": device.device_type,
        "hostname": device.hostname, "status": device.status,
        "serial_number": device.serial_number, "asset_tag": device.asset_tag,
        "management_ip": device.management_ip, "business_ip": device.business_ip,
        "cpu_model": device.cpu_model, "memory_gb": device.memory_gb,
        "gpu_count": device.gpu_count, "power_watts": device.power_watts,
    } for device in repository.list_devices()]
