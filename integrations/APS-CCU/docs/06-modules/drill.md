# 6.3 Drilling Station (DRILL)

## Overview

The Drilling Station performs drilling operations on workpieces. Similar to the Milling Station, it can pick up workpieces from the AGV, drill holes, and return them.

**Module Type**: `DRILL`  
**Serial Number**: Cleaned variant of the SPS serial number

## Supported Commands

| Command | Purpose | Metadata | Typical Duration |
|---------|---------|----------|------------------|
| `PICK` | Pick workpiece from AGV | None | ~3 seconds |
| `DRILL` | Perform drilling operation | `duration` (seconds) | Configurable (default 5s) |
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

Same structure as MILL module:
- Subscribe: `module/v1/ff/<serial>/order`, `module/v1/ff/<serial>/instantAction`
- Publish: `module/v1/ff/<serial>/state`, `module/v1/ff/<serial>/connection`, `module/v1/ff/<serial>/factsheet`

## Command Example: DRILL Operation

**Command**:
```json
{
  "timestamp": "2024-12-08T10:30:00.000Z",
  "serialNumber": "DRILL001",
  "orderId": "order-xyz-456",
  "orderUpdateId": 2,
  "action": {
    "id": "drill-action-123",
    "command": "DRILL",
    "metadata": {
      "duration": 6
    }
  }
}
```

**State Response** (Running):
```json
{
  "headerId": 15,
  "timestamp": "2024-12-08T10:30:01.000Z",
  "serialNumber": "DRILL001",
  "type": "DRILL",
  "orderId": "order-xyz-456",
  "orderUpdateId": 2,
  "paused": false,
  "actionState": {
    "id": "drill-action-123",
    "timestamp": "2024-12-08T10:30:01.000Z",
    "state": "RUNNING",
    "command": "DRILL"
  },
  "errors": [],
  "loads": [{"loadType": "BLUE", "loadPosition": "MODULE"}]
}
```

**State Response** (Finished):
```json
{
  "headerId": 16,
  "timestamp": "2024-12-08T10:30:07.000Z",
  "serialNumber": "DRILL001",
  "type": "DRILL",
  "orderId": "order-xyz-456",
  "orderUpdateId": 2,
  "paused": false,
  "actionState": {
    "id": "drill-action-123",
    "timestamp": "2024-12-08T10:30:07.000Z",
    "state": "FINISHED",
    "command": "DRILL"
  },
  "errors": [],
  "loads": [{"loadType": "BLUE", "loadPosition": "MODULE"}]
}
```

## Hardware Details

### PLC I/O
**Inputs**: Light barriers (entrance, processing position), suction cup sensors  
**Outputs**: Conveyor motors (PWM), suction actuators (PWM), drill motor, vacuum pump, compressor

## Errors

- `DRILL_ERROR` - Drilling motor fault or timeout
- `PICK_ERROR` - Failed to pick workpiece
- `DROP_ERROR` - Failed to drop workpiece

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
| `cmd__drill` | Command: Drill operation | BOOL |
| `stat__pickFinished` | Status: Pick process finished | BOOL |
| `stat__dropFinished` | Status: Drop process finished | BOOL |
| `stat__drillFinished` | Status: Drill process finished | BOOL |
| `cmd__drillDuration` | Command: Drill duration | INT |
| `stat__pickFailed` | Status: Pick process failed | BOOL |
| `stat__dropFailed` | Status: Drop process failed | BOOL |
| `stat__pickActive` | Status: Pick process active | BOOL |
| `stat__dropActive` | Status: Drop process active | BOOL |
| `stat__drillActive` | Status: Drill process active | BOOL |
| `cal__processEndTime` | Calibration time for process end | TIME |
| `cal__gripperDownTime` | Calibration time for gripper down | TIME |
| `cal__vacuumReleaseTime` | Calibration time for vacuum release | TIME |
| `cal__preFaultCheckTime` | Calibration time before fault check | TIME |
| `version` | Versioning | STRING |
| `cal__postDrillTime` | Calibration time after drilling | TIME |
| `cal__vacuumGenerateTime` | Calibration time for vacuum generation by compressor | TIME |
| `cal__midLightGateTime` | Calibration time to position the workpiece centrally in the light gate | TIME |
