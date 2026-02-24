# 6.7 High-Bay Warehouse (HBW)

## Overview

The HBW (High-Bay Warehouse) is a storage system that stores and retrieves workpieces. It has multiple storage positions organized in a grid and uses an automated retrieval system.

**Module Type**: `HBW`  
**Serial Number**: Cleaned variant of the SPS serial number  
**Storage Capacity**: Typically 9 positions (3x3 grid)

## Supported Commands

| Command | Purpose | Metadata | Duration |
|---------|---------|----------|----------|
| `PICK` | Store workpiece from AGV into warehouse | `StoreMetadata` (type, workpieceId) | ~10-15 seconds |
| `DROP` | Retrieve workpiece from warehouse to AGV | None | ~10-15 seconds |

⚠️ **Note**: Like DPS, HBW has inverted command logic:
- `PICK` = **Store** (take from AGV, put in warehouse)
- `DROP` = **Retrieve** (take from warehouse, put on AGV)

## Supported Instant Actions

| Action | Purpose | Metadata | Description |
|--------|---------|----------|-------------|
| `factsheetRequest` | Request module info | None | Triggers publication of factsheet message |
| `reset` | Reset module | None | Return module to initial state |
| `SET_STORAGE` | Update storage contents | `contents` map | Manually set inventory state (e.g. after intervention) |
| `startCalibration` | Enter calibration mode | None | Switch operating mode to TEACHIN |
| `stopCalibration` | Exit calibration mode | None | Switch operating mode to AUTOMATIC |
| `setCalibrationValues`| Update calibration | Calibration data | Update internal position values |

## MQTT Topics

Standard module topics:
- Subscribe: `module/v1/ff/<serial>/order`, `module/v1/ff/<serial>/instantAction`
- Publish: `module/v1/ff/<serial>/state`, `module/v1/ff/<serial>/connection`, `module/v1/ff/<serial>/factsheet`

## Command Examples

### Example 1: PICK (Store Workpiece)

**Command**:
```json
{
  "timestamp": "2024-12-08T10:00:00.000Z",
  "serialNumber": "HBW001",
  "orderId": "order-store-123",
  "orderUpdateId": 1,
  "action": {
    "id": "pick-action-abc",
    "command": "PICK",
    "metadata": {
      "type": "BLUE",
      "workpieceId": "wp-67890"
    }
  }
}
```

**Behavior**:
1. System identifies free storage position
2. Picks workpiece from AGV
3. Transports workpiece to storage position
4. Stores workpiece in identified slot
5. Updates internal storage map

**State Response** (Finished):
```json
{
  "headerId": 25,
  "timestamp": "2024-12-08T10:00:12.000Z",
  "serialNumber": "HBW001",
  "type": "HBW",
  "orderId": "order-store-123",
  "orderUpdateId": 1,
  "paused": false,
  "actionState": {
    "id": "pick-action-abc",
    "timestamp": "2024-12-08T10:00:12.000Z",
    "state": "FINISHED",
    "command": "PICK"
  },
  "errors": [],
  "loads": [
    {
      "loadType": "BLUE",
      "loadPosition": "2-1",
      "loadId": "wp-67890"
    }
  ]
}
```

The `loadPosition` indicates storage location (e.g., "2-1" = column 2, row 1).

### Example 2: DROP (Retrieve Workpiece)

**Command**:
```json
{
  "timestamp": "2024-12-08T10:30:00.000Z",
  "serialNumber": "HBW001",
  "orderId": "order-retrieve-456",
  "orderUpdateId": 1,
  "action": {
    "id": "drop-action-def",
    "command": "DROP"
  }
}
```

⚠️ **Note**: The CCU determines which workpiece to retrieve based on order requirements and FIFO/LIFO logic.

**Behavior**:
1. System locates requested workpiece type
2. Retrieves workpiece from storage position
3. Transports to AGV interface
4. Places on AGV loading bay
5. Updates internal storage map

**State Response** (Finished):
```json
{
  "headerId": 30,
  "timestamp": "2024-12-08T10:30:14.000Z",
  "serialNumber": "HBW001",
  "type": "HBW",
  "orderId": "order-retrieve-456",
  "orderUpdateId": 1,
  "paused": false,
  "actionState": {
    "id": "drop-action-def",
    "timestamp": "2024-12-08T10:30:14.000Z",
    "state": "FINISHED",
    "command": "DROP"
  },
  "errors": [],
  "loads": []
}
```

## Storage Management

### Storage Position Naming

Storage positions follow the format: `<column>-<row>`

Example 3x3 grid:
```
1-3  2-3  3-3  (Top row)
1-2  2-2  3-2  (Middle row)
1-1  2-1  3-1  (Bottom row)
```

### Set Storage Instant Action

To manually configure storage contents (e.g., after manual intervention or system reset):

**Instant Action**:
```json
{
  "serialNumber": "HBW001",
  "timestamp": "2024-12-08T09:00:00.000Z",
  "actions": [
    {
      "actionType": "SET_STORAGE",
      "actionId": "set-storage-123",
      "metadata": {
        "contents": {
          "1-1": {
            "type": "WHITE",
            "workpieceId": "wp-111"
          },
          "2-1": {
            "type": "BLUE",
            "workpieceId": "wp-222"
          },
          "3-1": {
            "type": "RED",
            "workpieceId": "wp-333"
          }
        }
      }
    }
  ]
}
```

Empty positions can be omitted or explicitly set to `{}`.

## Hardware Details

### Physical Components

The HBW consists of:
- **X-Axis**: Horizontal movement (columns)
- **Y-Axis**: Vertical movement (rows)
- **RBG** (Regalbediengerät): Storage/retrieval unit with gripper
- **Encoders**: Position tracking for X and Y axes
- **Light Barriers**: Workpiece detection

### PLC I/O

**Inputs**:
- Y-axis reference switch
- X-axis encoder (A/B)
- Y-axis encoder (A/B)
- Gripper front light barrier
- Gripper rear light barrier

**Outputs**:
- X-axis motor (to storage rack)
- X-axis motor (to conveyor)
- Y-axis motor (down)
- Y-axis motor (up)
- Gripper motor (extend)
- Gripper motor (retract)
- PWM signals (X-axis, Y-axis, Gripper)

## Calibration

The HBW requires precise calibration of:
- **X-axis Positions**: Exact encoder values for each column
- **Y-axis Positions**: Exact encoder values for each row
- **Gripper Positions**: Extend/retract distances
- **Timing Parameters**: Movement speeds

See [Calibration Documentation](../07-calibration.md) for procedures.

## Errors

- `PICK_ERROR` - Failed to store workpiece (storage full, position error, gripper fault)
- `DROP_ERROR` - Failed to retrieve workpiece (no workpiece in requested position, gripper fault)
- Storage full errors are reported via error messages

## Storage State Tracking

The CCU tracks HBW storage state via:
- **Topic**: `ccu/state/stock`
- **Contents**: All workpieces in storage with positions

Example:
```json
{
  "ts": "2024-12-08T10:00:00.000Z",
  "stockItems": [
    {
      "workpiece": {
        "id": "wp-111",
        "type": "WHITE",
        "state": "RAW"
      },
      "location": "HBW",
      "hbw": "1-1"
    },
    {
      "workpiece": {
        "id": "wp-222",
        "type": "BLUE",
        "state": "RAW"
      },
      "location": "HBW",
      "hbw": "2-1"
    }
  ]
}
```

## Special Considerations

### Inverted Command Logic
- **PICK** = Store into warehouse (take from AGV)
- **DROP** = Retrieve from warehouse (give to AGV)

### Storage Strategy
- CCU implements FIFO (First In, First Out) by default
- Alternative strategies can be configured

### Empty Storage Handling
- System must handle "no workpiece available" scenarios
- Orders may be delayed waiting for retrieval

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
| `stat__busy` | Status: System in use | BOOL |
| `stat__pickActive` | Status: Pick process active | BOOL |
| `stat__pickFinished` | Status: Pick process finished | BOOL |
| `cmd__pick` | Command: Pick operation | BOOL |
| `cmd__pickTargetRack` | Target rack for pick operation | STRING |
| `stat__dropActive` | Status: Drop process active | BOOL |
| `stat__dropFinished` | Status: Drop process finished | BOOL |
| `cmd__dropTargetRack` | Target rack for drop operation | STRING |
| `cmd__drop` | Command: Drop operation | BOOL |
| `stat__calibActive` | Status: Calibration active | BOOL |
| `cmd__calibrate` | Command: Calibrate | BOOL |
| `cmd__movePosX` | Target position in X direction for move, only during calibration | DINT |
| `cmd__movePosY` | Target position in Y direction for move, only during calibration | DINT |
| `cmd__movePosRot` | Target position in rotational direction for move, only during calibration | DINT |
| `cmd__default` | Command: Reset to default values | BOOL |
| `stat__defaultFinished` | Status: Reset to default values finished | BOOL |
| `cmd__move` | Command: Move operation | BOOL |
| `stat__moveFinished` | Status: Move operation finished | BOOL |
| `cmd__endCal` | Command: End calibration | BOOL |
| `stat__endCalFinished` | Status: Calibration ended | BOOL |
| `rack__A1_workpieceId` | Workpiece ID at position A1 in rack (Same for A2-C3) | STRING |
| `rack__A1_occupied` | Status: Position A1 in rack occupied (Same for A2-C3) | BOOL |
| `rack__A1_type` | Type of position A1 in rack (Same for A2-C3) | STRING |
| `cal__row1` | Calibration value for row 1 | DINT |
| `cal__row2` | Calibration value for row 2 | DINT |
| `cal__row3` | Calibration value for row 3 | DINT |
| `cal__rackOffset` | Calibration value for rack offset | DINT |
| `cal__colA` | Calibration value for column A | DINT |
| `cal__colB` | Calibration value for column B | DINT |
| `cal__colC` | Calibration value for column C | DINT |
| `cal__rampPositionX` | Calibration value for ramp position in X | DINT |
| `cal__rampPositionY` | Calibration value for ramp position in Y | DINT |
| `cal__rampPositionRot` | Calibration value for ramp position in rotational direction | DINT |
| `cal__rampPositionRotCheck` | Calibration value for rotational check position of ramp in rotational direction | DINT |
| `cal__rampOffset` | Calibration value for ramp offset | DINT |
| `cal__AGVPositionRot` | Calibration value of FTS rotation | DINT |
| `cal__upperLimitX` | Calibration upper limit for X | DINT |
| `cal__lowerLimitX` | Calibration lower limit for X | DINT |
| `cal__upperLimitY` | Calibration upper limit for Y | DINT |
| `cal__lowerLimitY` | Calibration lower limit for Y | DINT |
| `cal__upperLimitRot` | Calibration upper limit for rotational direction | DINT |
| `cal__lowerLimitRot` | Calibration lower limit for rotational direction | DINT |
| `cal__timeProcessEnd` | Calibration time at process end | TIME |
| `stat__referencedRotationalAxis` | Status: Rotational axis referenced | BOOL |
| `stat__referencedXAxis` | Status: X-axis referenced | BOOL |
| `stat__referencedYAxis` | Status: Y-axis referenced | BOOL |
| `cal__timeGripperValveOpen` | Time for opening the gripper valve | TIME |
| `cal__timeGripperValveClose` | Time for closing the gripper valve | TIME |
| `cal__timeCompressor` | Time for the compressor | TIME |
| `cmd__park` | Command: Park operation | BOOL |
| `cal__parkPositionX` | Park position in X direction for calibration | DINT |
| `cal__parkPositionY` | Park position in Y direction for calibration | DINT |
| `cal__parkPositionRot` | Park position for rotation in calibration | DINT |
| `stat__parkActive` | Status: Park operation active | BOOL |
| `rack__A1_ts` | Timestamp for position A1 in rack (Same for A2-C3) | STRING |
| `cal__defRowA` | Default value for row A | DINT |
| `cal__defRowB` | Default value for row B | DINT |
| `cal__defRowC` | Default value for row C | DINT |
| `cal__defOffset` | Default value for offset | DINT |
| `cal__defParkPositionX` | Default park position in X direction | DINT |
| `cal__defParkPositionY` | Default park position in Y direction | DINT |
| `cal__defParkPositionRot` | Default park position for rotation | DINT |
| `cal__defCol1` | Default value for column 1 | DINT |
| `cal__defCol2` | Default value for column 2 | DINT |
| `cal__defCol3` | Default value for column 3 | DINT |
| `cal__defRampPositionX` | Default value for ramp position in X | DINT |
| `cal__defRampPositionY` | Default value for ramp position in Y | DINT |
| `cal__defRampPositionRot` | Default value for ramp position in rotational direction | DINT |
| `cal__defRampPositionRotCheck` | Default value for rotational check position of ramp in rotational direction | DINT |
| `cal__defRampOffset` | Default value for ramp offset | DINT |
| `cal__defAGVPositionRot` | Default value of FTS rotation | DINT |
| `cal__defUpperLimitX` | Default upper limit for X | DINT |
| `cal__defLowerLimitX` | Default lower limit for X | DINT |
| `cal__defUpperLimitY` | Default upper limit for Y | DINT |
| `cal__defLowerLimitY` | Default lower limit for Y | DINT |
| `cal__defUpperLimitRot` | Default upper limit for rotational direction | DINT |
| `cal__defLowerLimitRot` | Default lower limit for rotational direction | DINT |
| `cal__defTimeProcessEnd` | Default time at process end | TIME |
| `cal__defTimeGripperValveOpen` | Default time for opening the gripper valve | TIME |
| `cal__defTimeGripperValveClose` | Default time for closing the gripper valve | TIME |
| `cal__defTimeCompressor` | Default time for the compressor | TIME |
