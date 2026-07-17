# Data Contract

The initial visualization contract will be JSON and will remain stable when the backing source changes from mock data to SQLite, Excel, CMDB, or live telemetry.

```json
{
  "room": "S41",
  "rack": "Rack-001",
  "u_position": 12,
  "device_type": "GPU",
  "hostname": "GPU001",
  "status": "running"
}
```

Sprint 2 now exports a list of these records with additional, optional detail fields including
`rack_total_u`, `u_height`, asset, IP, CPU, memory, GPU, and power data. Sprint 3 uses
`rack_total_u`, `u_position`, and `u_height` to generate the physical rack layout.
