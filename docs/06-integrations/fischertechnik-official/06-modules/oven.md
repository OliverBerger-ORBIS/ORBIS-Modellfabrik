# 6.4 Hardening Furnace (OVEN)

## Overview

The Hardening Furnace performs heat treatment operations on workpieces. It heats workpieces for a specified duration.

**Module Type**: `OVEN`  
**Serial Number**: Cleaned variant of the SPS serial number

## Supported Commands

| Command | Purpose | Metadata | Typical Duration |
|---------|---------|----------|------------------|
| `PICK` | Pick workpiece from AGV | None | ~3 seconds |
| `FIRE` | Perform heating operation | `duration` (seconds) | Configurable (default 10s) |
| `DROP` | Return workpiece to AGV | None | ~3 seconds |

## Supported Instant Actions

| Action | Purpose | Metadata | Description |
|--------|---------|----------|-------------|
| `factsheetRequest` | Request module info | None | Triggers publication of factsheet message |
| `reset` | Reset module | None | Return module to initial state |
| `startCalibration` | Enter calibration mode | None | Switch operating mode to TEACHIN |
| `stopCalibration` | Exit calibration mode | None | Switch operating mode to AUTOMATIC |
| `setCalibrationValues`| Update calibration | Calibration data | Update internal position values |

## MQTT Topics

Standard module topics:
- Subscribe: `module/v1/ff/<serial>/order`, `module/v1/ff/<serial>/instantAction`
- Publish: `module/v1/ff/<serial>/state`, `module/v1/ff/<serial>/connection`, `module/v1/ff/<serial>/factsheet`

## Command Example: FIRE Operation

**Command**:
```json
{
  "timestamp": "2024-12-08T11:00:00.000Z",
  "serialNumber": "OVEN001",
  "orderId": "order-heat-789",
  "orderUpdateId": 2,
  "action": {
    "id": "fire-action-abc",
    "command": "FIRE",
    "metadata": {
      "duration": 12
    }
  }
}
```

**State Response** (Running):
```json
{
  "headerId": 28,
  "timestamp": "2024-12-08T11:00:02.000Z",
  "serialNumber": "OVEN001",
  "type": "OVEN",
  "orderId": "order-heat-789",
  "orderUpdateId": 2,
  "paused": false,
  "actionState": {
    "id": "fire-action-abc",
    "timestamp": "2024-12-08T11:00:02.000Z",
    "state": "RUNNING",
    "command": "FIRE"
  },
  "errors": [],
  "loads": [{"loadType": "RED", "loadPosition": "MODULE"}]
}
```

**State Response** (Finished after 12 seconds):
```json
{
  "headerId": 29,
  "timestamp": "2024-12-08T11:00:14.000Z",
  "serialNumber": "OVEN001",
  "type": "OVEN",
  "orderId": "order-heat-789",
  "orderUpdateId": 2,
  "paused": false,
  "actionState": {
    "id": "fire-action-abc",
    "timestamp": "2024-12-08T11:00:14.000Z",
    "state": "FINISHED",
    "command": "FIRE"
  },
  "errors": [],
  "loads": [{"loadType": "RED", "loadPosition": "MODULE"}]
}
```

## Hardware Details

### PLC I/O
**Inputs**: Light barrier, suction cup position sensors, oven door sensors  
**Outputs**: Suction actuators, oven door actuator, oven heating lamp, vacuum pump, compressor

## Errors

- `FIRE_ERROR` - Heating timeout or temperature fault
- `PICK_ERROR` - Failed to pick workpiece
- `DROP_ERROR` - Failed to drop workpiece

## Special Behavior

The FIRE operation involves:
1. Opening oven door
2. Moving workpiece into oven
3. Closing door
4. Activating heating lamp for specified duration
5. Opening door
6. Moving workpiece out
7. Closing door

## Related Documentation

- [System Architecture](../02-architecture.md)
- [General Module Overview](../06-modules.md)
- [Message Structure](../05-message-structure.md)
- [Calibration](../07-calibration.md)
- [Manual Intervention](../08-manual-intervention.md)

## OPC UA Variables

| Variable Name | Description | Type |
|---|---|---|
| `model` | Model name | STRING |
| `stat__idle` | Status: System is idle | BOOL |
| `cmd__pick` | Command: Pick operation | BOOL |
| `cmd__drop` | Command: Drop operation | BOOL |
| `cmd__fire` | Command: Fire operation | BOOL |
| `cmd__fireDuration` | Command: Duration of fire operation | INT |
| `stat__pickFinished` | Status: Pick process finished | BOOL |
| `stat__dropFinished` | Status: Drop process finished | BOOL |
| `stat__fireFinished` | Status: Fire process finished | BOOL |
| `stat__pickFailed` | Status: Pick process failed | BOOL |
| `stat__dropFailed` | Status: Drop process failed | BOOL |
| `cal__processEndTime` | Calibration time for process end | TIME |
| `cal__gripperDownTime` | Calibration time for gripper down | TIME |
| `cal__vacuumReleaseTime` | Calibration time for vacuum release | TIME |
| `stat__dropActive` | Status: Drop process active | BOOL |
| `stat__pickActive` | Status: Pick process active | BOOL |
| `stat__fireActive` | Status: Fire process active | BOOL |
| `version` | Versioning | STRING |
