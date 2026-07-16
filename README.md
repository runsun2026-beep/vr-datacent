# DCVerse

DCVerse is a data-driven data-center digital twin. Blender is the visualization layer; the backend owns business rules and data, while the data layer can begin with mock JSON and SQLite and later be replaced by real infrastructure sources.

## Architecture

```text
Mock data / real infrastructure
            |
SQLite / JSON data layer
            |
Python backend and API
            |
Blender visualization layer
```

## Project layout

```text
backend/       Python API, domain models, services, and data access
blender/       Blender assets, scripts, UI, and animations
mock_data/     Deterministic development fixtures and JSON examples
docs/          Architecture and integration documentation
tests/         Automated tests, mirroring the backend layout
```

## Roadmap

1. Project skeleton (current)
2. Mock database: data center, room, rack, and device
3. Blender rack generation
4. Device placement and data-driven status visualization
5. Selection, editing, fault injection, and refresh workflows
6. Integration with real asset and telemetry sources

See [docs/architecture.md](docs/architecture.md) for ownership boundaries and the future data contract.
