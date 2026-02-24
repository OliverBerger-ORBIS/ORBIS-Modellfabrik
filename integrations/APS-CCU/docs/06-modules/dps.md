# 6.6 Delivery and Pickup Station (DPS)

## Overview

The DPS (Delivery and Pickup Station) serves as the input/output point for the factory. It handles workpiece delivery to the factory and shipping of finished products. It includes an NFC reader/writer for workpiece tracking.

**Module Type**: `DPS`  
**Serial Number**: Cleaned variant of the SPS serial number

## Supported Commands

| Command | Purpose | Metadata | Use Case |
|---------|---------|----------|----------|
| `DROP` | Deliver raw workpiece to factory | `StoreMetadata` (type, workpieceId) | Input new workpiece |
| `PICK` | Ship finished workpiece | `DeliveryMetadata` (history) | Output completed product |

⚠️ **Note**: DPS has inverted logic compared to other modules:
- `DROP` = **Input** to factory (module "drops" a new workpiece onto AGV)
- `PICK` = **Output** from factory (module "picks" finished workpiece from AGV for delivery)

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

## Command Examples

### Example 1: DROP (Input Raw Workpiece)

**Command**:
```json
{
  "timestamp": "2024-12-08T08:00:00.000Z",
  "serialNumber": "DPS001",
  "orderId": "order-input-123",
  "orderUpdateId": 1,
  "action": {
    "id": "drop-action-abc",
    "command": "DROP",
    "metadata": {
      "type": "WHITE",
      "workpieceId": "wp-12345"
    }
  }
}
```

**Behavior**:
1. Module reads NFC tag (if present)
2. Places workpiece on AGV loading bay
3. Writes workpiece metadata to NFC
4. Activates status LED (green)

**State Response** (Finished):
```json
{
  "headerId": 10,
  "timestamp": "2024-12-08T08:00:03.000Z",
  "serialNumber": "DPS001",
  "type": "DPS",
  "orderId": "order-input-123",
  "orderUpdateId": 1,
  "paused": false,
  "actionState": {
    "id": "drop-action-abc",
    "timestamp": "2024-12-08T08:00:03.000Z",
    "state": "FINISHED",
    "command": "DROP"
  },
  "errors": [],
  "loads": []
}
```

### Example 2: PICK (Output Finished Product)

**Command**:
```json
{
  "timestamp": "2024-12-08T08:30:00.000Z",
  "serialNumber": "DPS001",
  "orderId": "order-output-456",
  "orderUpdateId": 1,
  "action": {
    "id": "pick-action-def",
    "command": "PICK",
    "metadata": {
      "workpiece": {
        "workpieceId": "wp-12345",
        "type": "WHITE",
        "state": "PROCESSED",
        "history": [
          {
            "ts": 1702028400,
            "code": 100
          },
          {
            "ts": 1702028460,
            "code": 600
          },
          {
            "ts": 1702028520,
            "code": 700
          },
          {
            "ts": 1702028580,
            "code": 200
          },
          {
            "ts": 1702028640,
            "code": 800
          }
        ]
      }
    }
  }
}
```

**NFC Position Codes** (from metadata.workpiece.history):
- `100` - DPS DROP (Input)
- `200` - AIQS CHECK_QUALITY
- `300` - HBW PICK (Storage retrieval)
- `400` - HBW DROP (Storage deposit)
- `500` - OVEN FIRE
- `600` - MILL MILL
- `700` - DRILL DRILL
- `800` - DPS PICK (Output)

**Behavior**:
1. Module picks workpiece from AGV
2. Writes complete history to NFC tag
3. Outputs workpiece to delivery chute
4. Activates status LED sequence

**State Response** (Finished):
```json
{
  "headerId": 15,
  "timestamp": "2024-12-08T08:30:04.000Z",
  "serialNumber": "DPS001",
  "type": "DPS",
  "orderId": "order-output-456",
  "orderUpdateId": 1,
  "paused": false,
  "actionState": {
    "id": "pick-action-def",
    "timestamp": "2024-12-08T08:30:04.000Z",
    "state": "FINISHED",
    "command": "PICK"
  },
  "errors": [],
  "loads": [
    {
      "loadType": "WHITE",
      "loadPosition": "MODULE"
    }
  ]
}
```

## NFC Functionality

### Data Structure (JSON Representation)

When accessing via the standard module or internal `NodeRed` topics, the NFC data is abstracted as JSON:

```json
{
  "workpieceId": "wp-12345",
  "type": "WHITE",
  "state": "PROCESSED",
  "history": [
    {"ts": 1702028400, "code": 100},
    {"ts": 1702028460, "code": 600},
    {"ts": 1702028520, "code": 700},
    {"ts": 1702028580, "code": 200},
    {"ts": 1702028640, "code": 800}
  ]
}
```

### Raw Data Definition (Byte Map)

The NFC chip (NTAG213) memory map is defined as follows:

| Byte Offset | Content | Description |
|-------------|---------|-------------|
| 0 | NFC UID | 7 bytes (NTAG213) or 4 bytes (Mifare) |
| 7 | Byte 0 | **State**: 0=RAW, 1=PROCESSED, 2=REJECTED |
| 8 | Byte 1 | **Type**: 0=NONE, 1=WHITE, 2=RED, 3=BLUE |
| 9 | Byte 2 | Mask timestamps |
| 10 | Byte 3 | Reserved |
| 11 | Byte 4..67| **History**: Array of 8 x int64 (8 bytes each) |

### History Code Mapping

The raw history codes stored on the chip map to the following stations:

| Code | Description | Module |
|------|-------------|--------|
| `100` | Input Raw Material | DPS |
| `300` | Storage In | HBW |
| `400` | Storage Out | HBW |
| `500` | Processing Oven | OVEN |
| `600` | Processing Mill | MILL |
| `601` | Processing Drill | DRILL |
| `700` | Quality Control | AIQS |
| `800` | Dispatch Goods | DPS |

### Low-Level Interface (Direct TXT Access)

This section describes the direct interface to the NFC reader on the internal TXT controller (topics starting with `/j1/txt/...`).

**Topics**:

| Direction | Topic | Purpose |
|-----------|-------|---------|
| Subscribe | `/j1/txt/1/f/o/nfc/ds` | Send Read/Delete commands |
| Publish | `/j1/txt/1/f/i/nfc/ds` | Receive NFC content |

**Commands**:

```json
{
  "ts": "<timestamp>",
  "cmd": "<read/delete>"
}
```

**Response Format (Read)**:

```json
{
  "ts": 1683892857.208132,
  "history": [
    { "ts": 1682342421.8, "code": 100 },
    { "ts": 1682342283.1, "code": 300 }
  ],
  "workpiece": {
    "type": 0,
    "id": "041e9d7adb7281",
    "state": 0
  }
}
```

**Response Format (Delete)**: Returns empty history.

```json
{
  "ts": 1683892857.208132,
  "history": [],
  "workpiece": {
    "type": 0,
    "id": "041e9d7adb7281",
    "state": 0
  }
}
```

## Hardware Details

### PLC I/O
**Inputs**: Light barrier, NFC reader, camera for position detection  
**Outputs**: Conveyor motors (PWM), status LEDs (RGB), NFC writer

## Status LED Control

The DPS has RGB status LEDs that can be controlled via instant action:

**Instant Action**:
```json
{
  "serialNumber": "DPS001",
  "timestamp": "2024-12-08T09:00:00.000Z",
  "actions": [
    {
      "actionType": "setStatusLED",
      "actionId": "led-123",
      "metadata": {
        "red": false,
        "yellow": false,
        "green": true
      }
    }
  ]
}
```

## Calibration

The DPS supports calibration of:
- **Camera Position**: X/Y coordinates for different stations
- **Color Sensor**: RGB thresholds
- **Timing**: Conveyor and NFC operation timings

## Errors

- `DROP_ERROR` - Failed to deliver workpiece (NFC write error, conveyor jam)
- `PICK_ERROR` - Failed to retrieve workpiece (NFC read error, no workpiece detected)

## Special Considerations

### Command Logic
Unlike other modules where PICK takes from AGV and DROP places on AGV:
- **DPS DROP**: Places NEW workpiece onto AGV (factory input)
- **DPS PICK**: Takes FINISHED workpiece from AGV (factory output)

### NFC Tag Management
- Raw workpieces may not have NFC tags initially
- Tags are written during DROP operation
- Complete history is written during PICK operation
- NFC data enables traceability and ROBO Pro Coding integration

## Related Documentation

- [System Architecture](../02-architecture.md)
- [General Module Overview](../06-modules.md)
- [Message Structure](../05-message-structure.md)
- [Calibration](../07-calibration.md)
- [Manual Intervention](../08-manual-intervention.md)

## Internal Communication (Node-RED to TXT)

The DPS module uses an internal TXT controller specifically for **controlling the robot arm** (movement) and the **NFC reader/writer**. Other sensors (like the RGB color sensor and light barriers) are connected to the main 24V PLC. This controller communicates with the main Node-RED instance via MQTT.

### Topic Structure

The internal communication uses the specific prefix `NodeRed` to identify the bridge:
`module/v1/ff/NodeRed/{DEVICEID}/...`

Where `{DEVICEID}` is the 4-character ID of the internal TXT controller (e.g., from `config.json`).

### Topics

| Direction | Topic | Purpose |
|-----------|-------|---------|
| Subscribe | `module/v1/ff/NodeRed/{DEVICEID}/order` | Receive commands (`INPUT_RGB`, `RGB_NFC`, `DROP`, `PICK`) |
| Subscribe | `module/v1/ff/NodeRed/{DEVICEID}/instantAction` | Receive immediate commands (`reset`, `announceOutput`) |
| Publish | `module/v1/ff/NodeRed/{DEVICEID}/state` | Publish current status and action results |

### Internal Order Messages

**Topic**: `module/v1/ff/NodeRed/{DEVICEID}/order`

#### Supported Commands

1.  **`INPUT_RGB`**
    *   **Description**: Move workpiece from input belt to RGB color sensor. (Note: RGB conversion happens on the 24V PLC side).
    *   **Result**: None (Updates state).

2.  **`RGB_NFC`**
    *   **Description**: Move from RGB sensor to NFC reader. Reads NFC ID.
    *   **Metadata**: `{'type': 'RED' | 'WHITE' | 'BLUE'}` (Workpiece color).
    *   **Result**: NFC ID.

3.  **`DROP`**
    *   **Description**: Move from NFC reader to FTS (AGV).
    *   **Result**: None.

4.  **`PICK`**
    *   **Description**: Receive workpiece from FTS, write NFC data, and move to Output or NIO bin.
    *   **Metadata**: `{'workpiece': { 'history': ..., 'workpieceId': ..., 'type': ..., 'state': ...}}` (NFC data to write).
    *   **Result**: `PASSED` or `FAILED` (depending on NFC write success and target).

**Example Order**:
```json
{
  "orderId": "SOME_ID",
  "orderUpdateId": 1,
  "timestamp": "2023-02-02T13:58:06Z",
  "action": {
    "command": "DROP",
    "id": "ID#2",
    "metadata": {
      "type": "WHITE"
    }
  }
}
```

### Internal State Messages

**Topic**: `module/v1/ff/NodeRed/{DEVICEID}/state`

```json
{
  "orderId": "SOME_ID",
  "orderUpdateId": 1,
  "timestamp": "2023-02-02T13:57:06Z",
  "action": {
    "command": "DROP",
    "id": "ID#1",
    "metadata": {
      "result": null
    }
  }
}
```

### Internal Instant Actions

**Topic**: `module/v1/ff/NodeRed/{DEVICEID}/instantAction`

#### Supported Actions

*   `factsheetRequest`: Publishes to `.../factsheet`.
*   `reset`: Resets module to known idle state.
*   `announceOutput`: Announces intent to output. Aborts current input, changes `orderId`, resets `orderUpdateId`.
*   `startCalibration`, `testCalibrationPosition`, `stopCalibration`, etc.

**example `announceOutput`**:
```json
{
   "serialNumber": "serial",
   "timestamp":"2022-03-03T12:12:12Z",
   "actions":[
      {
         "actionType": "announceOutput",
         "actionId": "3234567890abcdee",
         "metadata": {
          "orderId": "NEW_ORDER_ID"
         }
      }
   ]
}
```

### Internal State Machine

The internal controller follows this state logic:

| State | Description | Transitions To |
|-------|-------------|----------------|
| `STATE_IDLE` | Waiting for workpiece | `STATE_INPUT_RUNNING`, `STATE_PICK_NFC_RUNNING` |
| `STATE_INPUT_RUNNING` | Processing input | `STATE_RGB_IDLE` |
| `STATE_RGB_IDLE` | Waiting for recognition | `STATE_RGB_NFC_RUNNING` |
| `STATE_RGB_NFC_RUNNING` | Moving to NFC | `STATE_NFC_IDLE` |
| `STATE_NFC_IDLE` | Waiting for decision | `STATE_DROP_RUNNING` |
| `STATE_DROP_RUNNING` | Loading to AGV | `STATE_IDLE` |
| `STATE_PICK_NFC_RUNNING` | Unloading from AGV | `STATE_IDLE` (via Reset) |

**Internal Action Mappings**:
*   `INPUT_RGB` → `STATE_INPUT_RUNNING`
*   `RGB_NFC` → `STATE_RGB_NFC_RUNNING`
*   `DROP` → `STATE_DROP_RUNNING`
*   `PICK` → `STATE_PICK_NFC_RUNNING`

## OPC UA Variables

| Variable Name | Description | Type |
|---|---|---|
| `cal__colorBlueSetpoint` | Setpoint for blue color in calibration | INT |
| `cal__colorWhiteSetpoint` | Setpoint for white color in calibration | INT |
| `cal__shortProcessWaitTime` | Short waiting time during process | TIME |
| `cal__colorValue` | Color value (live) | INT |
| `stat__input` | Input status | BOOL |
| `stat__output` | Output status | BOOL |
| `cal__colorRange` | Color range in calibration | INT |
| `stat__colorRangeRed` | Status: Red color range | BOOL |
| `stat__colorRangeWhite` | Status: White color range | BOOL |
| `stat__colorRangeBlue` | Status: Blue color range | BOOL |
| `version` | Versioning | STRING |
| `cmd__calibDefault` | Command: Reset to factory settings | BOOL |
| `stat__calibDefaultFinished` | Status: Reset to factory settings finished | BOOL |
| `cal__parkPosX` | Park position in X direction for calibration | DINT |
| `cal__parkPosY` | Park position in Y direction for calibration | DINT |
| `cmd__park` | Command: Park | BOOL |
| `stat__parkActive` | Status: Park active | BOOL |
| `cal__defUpperLimitX` | Default upper limit in X direction | DINT |
| `cal__defLowerLimitX` | Default lower limit in X direction | DINT |
| `cal__defUpperLimitY` | Default upper limit in Y direction | DINT |
| `cal__defLowerLimitY` | Default lower limit in Y direction | DINT |
| `cal__defHomePosX` | Default home position in X direction | DINT |
| `cal__defHomePosY` | Default home position in Y direction | DINT |
| `cal__defCustomPosX` | Default custom position in X direction | DINT |
| `cal__defCustomPosY` | Default custom position in Y direction | DINT |
| `cal__defColorRedSetpoint` | Default setpoint for red color in calibration | INT |
| `cal__defColorBlueSetpoint` | Default setpoint for blue color in calibration | INT |
| `cal__defColorWhiteSetpoint` | Default setpoint for white color in calibration | INT |
| `cal__defColorRange` | Default color range in calibration | INT |
| `cal__defShortProcessWaitTime` | Default short waiting time during process | TIME |
