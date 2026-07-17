"""Typed records returned by the inventory repository."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceRecord:
    data_center: str
    room: str
    rack: str
    rack_total_u: int
    u_position: int
    u_height: int
    device_type: str
    hostname: str
    status: str
    serial_number: str | None
    asset_tag: str | None
    management_ip: str | None
    business_ip: str | None
    cpu_model: str | None
    memory_gb: int | None
    gpu_count: int | None
    power_watts: int | None
