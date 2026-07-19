"""Build a DCVerse data-center scene from a Sprint 2 JSON export.

In Blender: open this script, set JSON_PATH below, then click Run Script.
From a terminal: blender --background --python blender/scripts/create_datacenter.py -- --json /path/devices.json --blend-output /path/scene.blend
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import bpy

# Set this in Blender's Text Editor for the simplest interactive workflow.
JSON_PATH = ""

RACK_WIDTH = 0.60
RACK_DEPTH = 1.00
RACK_U_HEIGHT = 0.04445  # 1U = 1.75 inches
RACK_GAP = 0.35
ROOM_GAP = 1.40

STATUS_COLORS = {
    "running": (0.05, 0.80, 0.25, 1.0),
    "warning": (1.00, 0.62, 0.04, 1.0),
    "offline": (0.95, 0.06, 0.04, 1.0),
}


class DCVERSE_PT_device_inspector(bpy.types.Panel):
    """Show backend-supplied inventory for the selected device."""

    bl_idname = "DCVERSE_PT_device_inspector"
    bl_label = "DCVerse Device Inspector"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "DCVerse"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        selected = context.active_object
        return selected is not None and bool(selected.get("dcverse_device"))

    def draw(self, context: bpy.types.Context) -> None:
        device = context.active_object
        layout = self.layout
        layout.label(text=str(device.get("hostname", device.name)))
        layout.separator()

        placement = layout.box()
        placement.label(text="Placement")
        placement.label(text=f"Room: {device.get('room', '—')}")
        placement.label(text=f"Rack: {device.get('rack', '—')}")
        placement.label(text=f"U position: {device.get('u_position', '—')} ({device.get('u_height', '—')}U)")

        identity = layout.box()
        identity.label(text="Asset")
        identity.label(text=f"Type: {device.get('device_type', '—')}")
        identity.label(text=f"Status: {str(device.get('status', 'unknown')).upper()}")
        identity.label(text=f"Serial number: {device.get('serial_number', '—')}")
        identity.label(text=f"Asset tag: {device.get('asset_tag', '—')}")

        network = layout.box()
        network.label(text="Network")
        network.label(text=f"Management IP: {device.get('management_ip', '—')}")
        network.label(text=f"Business IP: {device.get('business_ip', '—')}")

        configuration = layout.box()
        configuration.label(text="Configuration")
        configuration.label(text=f"CPU: {device.get('cpu_model', '—')}")
        memory = device.get("memory_gb")
        configuration.label(text=f"Memory: {str(memory) + ' GB' if memory is not None else '—'}")
        gpu_count = device.get("gpu_count")
        configuration.label(text=f"GPU count: {gpu_count if gpu_count is not None else '—'}")
        power = device.get("power_watts")
        configuration.label(text=f"Power: {str(power) + ' W' if power is not None else '—'}")


INSPECTOR_CLASSES = (DCVERSE_PT_device_inspector,)


def register_inspector() -> None:
    """Register safely when this Text Editor script is run more than once."""
    for panel_class in INSPECTOR_CLASSES:
        try:
            bpy.utils.unregister_class(panel_class)
        except RuntimeError:
            pass
        bpy.utils.register_class(panel_class)


def script_arguments() -> argparse.Namespace:
    """Read only arguments placed after Blender's `--` separator."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--json", dest="json_path")
    parser.add_argument("--blend-output", dest="blend_output")
    arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(arguments)


def source_path() -> Path:
    args = script_arguments()
    value = args.json_path or JSON_PATH or os.environ.get("DCVERSE_JSON")
    if not value:
        raise RuntimeError(
            "Set JSON_PATH in create_datacenter.py or run Blender with -- --json /path/devices.json"
        )
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise RuntimeError(f"DCVerse JSON file was not found: {path}")
    return path


def load_devices(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        devices = json.load(file)
    if not isinstance(devices, list):
        raise ValueError("DCVerse JSON must be a list of device objects")
    required = {"room", "rack", "rack_total_u", "u_position", "u_height", "hostname", "status"}
    for index, device in enumerate(devices):
        missing = required - device.keys()
        if missing:
            raise ValueError(f"Device at index {index} is missing: {', '.join(sorted(missing))}")
    return devices


def clear_previous_scene() -> bpy.types.Collection:
    collection = bpy.data.collections.get("DCVerse_Scene")
    if collection:
        bpy.data.collections.remove(collection, do_unlink=True)
    collection = bpy.data.collections.new("DCVerse_Scene")
    bpy.context.scene.collection.children.link(collection)
    return collection


def material(name: str, color: tuple[float, float, float, float], emission: float = 0.0) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    result = bpy.data.materials.new(name)
    result.diffuse_color = color
    result.use_nodes = True
    principled = result.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = 0.35
    emission_color = principled.inputs.get("Emission Color") or principled.inputs.get("Emission")
    emission_strength = principled.inputs.get("Emission Strength")
    if emission_color:
        emission_color.default_value = color
    if emission_strength:
        emission_strength.default_value = emission
    return result


FRAME_MATERIAL = None
LABEL_MATERIAL = None
GLASS_MATERIAL = None
DETAIL_MATERIAL = None
FAN_MATERIAL = None


def add_box(collection: bpy.types.Collection, name: str, location: tuple[float, float, float], dimensions: tuple[float, float, float], mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    for linked_collection in list(obj.users_collection):
        linked_collection.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def add_cylinder(collection: bpy.types.Collection, name: str, location: tuple[float, float, float], radius: float, depth: float, mat: bpy.types.Material, rotation: tuple[float, float, float] = (0, 0, 0)) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    for linked_collection in list(obj.users_collection):
        linked_collection.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def add_text(collection: bpy.types.Collection, body: str, location: tuple[float, float, float], size: float, name: str) -> bpy.types.Object:
    bpy.ops.object.text_add(location=location, rotation=(1.5708, 0, 0))
    text = bpy.context.object
    text.name = name
    text.data.body = body
    text.data.align_x = "CENTER"
    text.data.size = size
    text.data.extrude = 0.002
    text.data.materials.append(LABEL_MATERIAL)
    for linked_collection in list(text.users_collection):
        linked_collection.objects.unlink(text)
    collection.objects.link(text)
    return text


def build_rack(collection: bpy.types.Collection, room: str, rack: str, total_u: int, x: float) -> None:
    height = total_u * RACK_U_HEIGHT
    bottom = height / 2
    for side in (-1, 1):
        add_box(collection, f"{room}_{rack}_post_{side}", (x + side * RACK_WIDTH / 2, 0, bottom), (0.025, RACK_DEPTH, height), FRAME_MATERIAL)
    add_box(collection, f"{room}_{rack}_top", (x, 0, height), (RACK_WIDTH, RACK_DEPTH, 0.025), FRAME_MATERIAL)
    add_box(collection, f"{room}_{rack}_bottom", (x, 0, 0), (RACK_WIDTH, RACK_DEPTH, 0.025), FRAME_MATERIAL)
    for unit in range(total_u + 1):
        z = unit * RACK_U_HEIGHT
        add_box(collection, f"{room}_{rack}_u_{unit}", (x, -RACK_DEPTH / 2, z), (RACK_WIDTH, 0.012, 0.003), FRAME_MATERIAL)
    # A framed, blue-tinted front glass door makes the rack readable as an enclosure.
    add_box(collection, f"{room}_{rack}_glass_door", (x, -RACK_DEPTH / 2 - 0.018, bottom), (RACK_WIDTH * 0.86, 0.010, height * 0.94), GLASS_MATERIAL)
    for side in (-1, 1):
        add_box(collection, f"{room}_{rack}_door_frame_{side}", (x + side * RACK_WIDTH * 0.45, -RACK_DEPTH / 2 - 0.025, bottom), (0.018, 0.025, height * 0.97), FRAME_MATERIAL)
    for fan_x in (-RACK_WIDTH * 0.22, RACK_WIDTH * 0.22):
        add_cylinder(collection, f"{room}_{rack}_top_fan_{fan_x:+.2f}", (x + fan_x, 0, height + 0.035), 0.075, 0.025, FAN_MATERIAL)
    add_text(collection, rack, (x, -RACK_DEPTH / 2 - 0.03, height + 0.07), 0.07, f"{room}_{rack}_label")


def build_device_details(collection: bpy.types.Collection, device: dict, rack_x: float, z: float, height: float) -> None:
    """Add a distinct front panel for GPU, CPU, and network devices."""
    hostname = device["hostname"]
    front_y = -RACK_DEPTH * 0.46 - 0.008
    device_type = device["device_type"].lower()
    if "switch" in device_type:
        for index in range(12):
            port_x = rack_x - 0.22 + index * 0.04
            add_box(collection, f"{hostname}_port_{index + 1}", (port_x, front_y, z), (0.025, 0.012, min(0.018, height * 0.45)), material("DCVerse_port", (0.06, 0.35, 0.65, 1.0), 0.08))
    else:
        fan_count = 4 if "gpu" in device_type else 3
        for index in range(fan_count):
            fan_x = rack_x - 0.18 + index * (0.36 / max(1, fan_count - 1))
            add_cylinder(collection, f"{hostname}_fan_{index + 1}", (fan_x, front_y, z), min(0.028, height * 0.30), 0.014, FAN_MATERIAL, (1.5708, 0, 0))
    label = "GPU SERVER" if "gpu" in device_type else "CPU SERVER" if "cpu" in device_type else device["device_type"].upper()
    add_text(collection, label, (rack_x - 0.08, front_y - 0.010, z), min(0.035, height * 0.40), f"{hostname}_type_label")


def build_device(collection: bpy.types.Collection, device: dict, rack_x: float) -> None:
    height = device["u_height"] * RACK_U_HEIGHT * 0.88
    z = (device["u_position"] - 1) * RACK_U_HEIGHT + height / 2
    status = device["status"].lower()
    device_type = device["device_type"].lower()
    chassis_color = (0.06, 0.10, 0.16, 1.0) if "gpu" in device_type else (0.16, 0.17, 0.19, 1.0) if "cpu" in device_type else (0.04, 0.05, 0.06, 1.0)
    device_material = material(f"DCVerse_chassis_{device_type}", chassis_color)
    hostname = device["hostname"]
    obj = add_box(collection, hostname, (rack_x, 0, z), (RACK_WIDTH * 0.90, RACK_DEPTH * 0.90, height), device_material)
    obj["dcverse_device"] = True
    for key, value in device.items():
        # Blender custom properties do not support JSON null; omit absent values.
        if value is not None:
            obj[key] = value
    led_color = STATUS_COLORS.get(status, (0.35, 0.35, 0.35, 1.0))
    add_box(collection, f"{hostname}_status_led", (rack_x + RACK_WIDTH * 0.35, -RACK_DEPTH * 0.46 - 0.010, z), (0.026, 0.012, min(0.022, height * 0.5)), material(f"DCVerse_led_{status}", led_color, 3.0))
    build_device_details(collection, device, rack_x, z, height)
    add_text(collection, hostname, (rack_x, -RACK_DEPTH / 2 - 0.025, z), 0.045, f"{hostname}_label")


def build_scene(devices: list[dict]) -> None:
    global FRAME_MATERIAL, LABEL_MATERIAL, GLASS_MATERIAL, DETAIL_MATERIAL, FAN_MATERIAL
    collection = clear_previous_scene()
    FRAME_MATERIAL = material("DCVerse_frame", (0.05, 0.06, 0.08, 1.0))
    LABEL_MATERIAL = material("DCVerse_labels", (0.85, 0.90, 1.00, 1.0), 0.05)
    DETAIL_MATERIAL = material("DCVerse_detail", (0.015, 0.02, 0.03, 1.0))
    FAN_MATERIAL = material("DCVerse_fan", (0.11, 0.13, 0.16, 1.0), 0.04)
    GLASS_MATERIAL = material("DCVerse_glass", (0.07, 0.25, 0.40, 0.20))
    glass_principled = GLASS_MATERIAL.node_tree.nodes.get("Principled BSDF")
    alpha = glass_principled.inputs.get("Alpha")
    if alpha:
        alpha.default_value = 0.20
    if hasattr(GLASS_MATERIAL, "surface_render_method"):
        GLASS_MATERIAL.surface_render_method = "DITHERED"
    grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for device in devices:
        grouped[device["room"]][device["rack"]].append(device)
    x = 0.0
    for room, racks in sorted(grouped.items()):
        room_start = x
        for rack, rack_devices in sorted(racks.items()):
            total_u = rack_devices[0]["rack_total_u"]
            build_rack(collection, room, rack, total_u, x)
            for device in rack_devices:
                build_device(collection, device, x)
            x += RACK_WIDTH + RACK_GAP
        add_text(collection, room, ((room_start + x - RACK_GAP) / 2, -0.75, 2.1), 0.12, f"{room}_label")
        x += ROOM_GAP
    add_box(collection, "DCVerse_floor", ((x - ROOM_GAP) / 2, 0, -0.04), (max(3.0, x), 2.8, 0.05), material("DCVerse_floor", (0.025, 0.03, 0.04, 1.0)))
    bpy.context.scene["dcverse_source"] = str(source_path())
    print(f"DCVerse: created {len(grouped)} room(s) and {len(devices)} device(s).")


def main() -> None:
    register_inspector()
    build_scene(load_devices(source_path()))
    output = script_arguments().blend_output
    if output:
        output_path = Path(output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
        print(f"DCVerse: saved Blender scene to {output_path}")


if __name__ == "__main__":
    main()
