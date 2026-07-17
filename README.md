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

1. Project skeleton (complete)
2. Mock database: data center, room, rack, and device (complete)
3. Blender rack generation
4. Device placement and data-driven status visualization
5. Selection, editing, fault injection, and refresh workflows
6. Integration with real asset and telemetry sources

See [docs/architecture.md](docs/architecture.md) for ownership boundaries and the future data contract.

## Run the Sprint 2 mock interface

No third-party dependencies are required. From the repository root:

```bash
python3 -m backend.api.mock_api
python3 -m unittest discover -s tests -v
```

The first command creates `data/dcverse_mock.sqlite3` locally and prints the stable JSON
contract that Blender will consume in Sprint 3. The database is intentionally ignored by Git.

## Run the Sprint 3 Blender generator

First export the mock data to a JSON file:

```bash
python3 -m backend.api.mock_api > /tmp/dcverse-devices.json
```

In Blender, open `blender/scripts/create_datacenter.py`, set `JSON_PATH` to the absolute
path of that file, then select **Run Script**. The script creates a `DCVerse_Scene` collection
containing one 42U rack per JSON rack and places each device according to its U position.
