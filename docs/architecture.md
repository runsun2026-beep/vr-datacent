# Architecture

## Principle

DCVerse treats Blender as a renderer and interaction surface, not as the source of truth. Every visual object must be reproducible from data supplied by the backend.

```text
Data sources -> data access -> services -> API/JSON contract -> Blender
```

## Ownership

| Layer | Responsibility | Must not own |
| --- | --- | --- |
| `mock_data/` | Versioned fixtures for local simulation | Runtime business logic |
| `backend/database/` | SQLite connections, migrations, repositories | Blender-specific behavior |
| `backend/models/` | Data-center domain entities and validation | Rendering code |
| `backend/services/` | Status, placement, fault, and workflow rules | UI object manipulation |
| `backend/api/` | JSON endpoints and request handling | Persistent storage details |
| `blender/` | Scene generation, display, interaction, animation | Authoritative infrastructure data |

## Planned data hierarchy

```text
DataCenter -> Room -> Rack -> Device -> Component
```

The first API contract will expose device records independently of Blender implementation details. A device needs, at minimum, its room, rack, U position, device type, hostname, and status.
