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

This is a target contract only; validation and persistence arrive in the mock database sprint.
