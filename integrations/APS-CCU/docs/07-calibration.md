# 7. Calibration and System Actions

## 7.1 Calibration Overview

Calibration is the process of adjusting module parameters to compensate for physical changes in the factory hardware. While the PLC handles low-level motor control, the high-level positioning logic for storage and sorting relies on calibrated values stored in the system.

**Factors requiring recalibration:**
*   **Mechanical Drift:** Wear and tear on belts, gears, and motors over specific runtime periods.
*   **Environmental Impact:** Micro-expansions or sensor sensitivity changes due to temperature fluctuations.
*   **Maintenance:** Any physical intervention (e.g., tightening a screw or moving a module) invalidates previous coordinates.

In the APS MQTT system, **only AIQS, HBW and DPS modules support remote calibration commands**, as these rely on precise coordinate systems (HBW, DPS axes) and color sensor thresholds (AIQS, DPS sorting) that must be aligned with the physical reality.

> **Note**: Calibration affects the physical coordinate systems of the storage mechanisms (High-Bay Warehouse, Delivery & Pickup Station) and the sorting logic (Quality Control with AI, Delivery & Pickup Station). Incorrect values will lead to mechanical failures (collisions, missed pick-ups).

### Prerequisites

Calibration should be performed when:
1.  Setting up a new module.
2.  Mechanical maintenance has altered component positions.
3.  Positioning errors (e.g., missed slots) are observed.

> **Warning**: Never calibrate while a production order is active. Calibration changes the operating mode to `TEACHIN`, causing any active `AUTOMATIC` processes to fail.

## 7.2 Calibration Process

### Entering Calibration Mode

Send the `startCalibration` instant action:

**Instant Action**:
```json
{
  "serialNumber": "HBW001",
  "timestamp": "2024-12-08T14:00:00.000Z",
  "actions": [
    {
      "actionType": "startCalibration",
      "actionId": "calib-start-123"
    }
  ]
}
```

**Module Response**:
```json
{
  "serialNumber": "HBW001",
  "operatingMode": "TEACHIN",
  "actionState": null,
  "information": [
    {
      "infoType": "calibration_status",
      "infoLevel": "INFO",
      "infoReferences": [
        {
          "referenceKey": "POSITIONS.CURRENT",
          "referenceValue": "HOME"
        },
        {
          "referenceKey": "POSITIONS.AVAILABLE",
          "referenceValue": "1-1,1-2,2-1,2-2"
        }
      ]
    }
  ]
}
```

### Exiting Calibration Mode

Send the `stopCalibration` instant action:

```json
{
  "serialNumber": "HBW001",
  "timestamp": "2024-12-08T14:30:00.000Z",
  "actions": [
    {
      "actionType": "stopCalibration",
      "actionId": "calib-stop-456"
    }
  ]
}
```

**Module Response**:
```json
{
  "serialNumber": "HBW001",
  "operatingMode": "AUTOMATIC",
  "actionState": null
}
```

## 7.3 Calibration Instant Actions

### Available Calibration Actions

| Action Type | Purpose | Metadata |
|-------------|---------|----------|
| `startCalibration` | Enter calibration mode | None |
| `stopCalibration` | Exit calibration mode | None |
| `setCalibrationValues` | Update calibration parameters | `references` array |
| `selectCalibrationPosition` | Move to specific position | `position` |
| `testCalibrationPosition` | Test current position | `position` |
| `storeCalibrationValues` | Save parameters to persistent storage | None |
| `resetCalibration` | Reset to factory defaults | `factory: true` |

### Setting Calibration Values

**Example: Adjust HBW position parameters**

```json
{
  "serialNumber": "HBW001",
  "timestamp": "2024-12-08T14:05:00.000Z",
  "actions": [
    {
      "actionType": "setCalibrationValues",
      "actionId": "set-calib-789",
      "metadata": {
        "references": [
          {
            "referenceKey": "cal__colA",
            "referenceValue": 1500
          },
          {
            "referenceKey": "cal__row1",
            "referenceValue": 2000
          }
        ]
      }
    }
  ]
}
```

### Selecting a Position (HBW/DPS)

For modules with positioning systems:

```json
{
  "serialNumber": "DPS001",
  "timestamp": "2024-12-08T14:10:00.000Z",
  "actions": [
    {
      "actionType": "selectCalibrationPosition",
      "actionId": "select-pos-123",
      "metadata": {
        "position": "HBW"
      }
    }
  ]
}
```

**Available Positions**:
- DPS: `HOME`, `HBW`, custom positions
- HBW: Storage grid positions like `1-1`, `2-3`

### Testing a Position

Test if a position works correctly:

```json
{
  "serialNumber": "HBW001",
  "timestamp": "2024-12-08T14:15:00.000Z",
  "actions": [
    {
      "actionType": "testCalibrationPosition",
      "actionId": "test-pos-456",
      "metadata": {
        "position": "2-2"
      }
    }
  ]
}
```

The module moves to the position and reports success/failure.

### Storing Calibration Values

Save current calibration to persistent storage (EEPROM/file):

```json
{
  "serialNumber": "HBW001",
  "timestamp": "2024-12-08T14:25:00.000Z",
  "actions": [
    {
      "actionType": "storeCalibrationValues",
      "actionId": "store-calib-789"
    }
  ]
}
```

⚠️ **Important**: Values are typically stored in volatile memory until explicitly saved with this command.

### Reset to Factory Defaults

Reset all calibration parameters to factory defaults:

```json
{
  "serialNumber": "DPS001",
  "timestamp": "2024-12-08T14:28:00.000Z",
  "actions": [
    {
      "actionType": "resetCalibration",
      "actionId": "reset-calib-123",
      "metadata": {
        "factory": true
      }
    }
  ]
}
```

## 7.4 Module-Specific Calibration

### DPS Module

**Calibratable Parameters**:
- Camera position coordinates (X/Y encoder values)
- Color sensor thresholds
- NFC reader positioning

**Calibration Procedure**:
1. Enter calibration mode
2. Use `selectCalibrationPosition` to move camera
3. Visually verify correct position
4. Use `setCalibrationValues` to store coordinates
5. Use `storeCalibrationValues` to save permanently

### HBW Module

**Calibratable Parameters**:
- Storage grid position coordinates (X/Y encoder values for each slot)
- Gripper extend/retract positions
- Movement speeds

**Critical for HBW**: Incorrect position calibration leads to:
- Failed storage/retrieval
- Mechanical collisions
- Dropped workpieces

**Calibration Procedure**:
1. Home all axes (move to reference positions)
2. Use `selectCalibrationPosition` to jog to each storage position
3. Use `setCalibrationValues` to record encoder values for that slot
4. Use `testCalibrationPosition` to verify each position
5. Use `storeCalibrationValues` to save permanently

### Other Modules

**MILL, DRILL, OVEN, AIQS**: Calibration is handled via PLC configuration, not through MQTT. Use the PLC programming interface or manufacturer tools to adjust timing and sensor parameters for these modules.

## 7.5 Calibration Best Practices

### Do's ✅

1. **Document Original Values**: Record default values before changing
2. **Change One Parameter at a Time**: Isolate effects
3. **Test Thoroughly**: Run multiple cycles after calibration
4. **Store Values**: Use `storeCalibrationValues` to persist changes
5. **Calibrate When Idle**: No active production during calibration
6. **Use Small Increments**: Adjust gradually, not drastically

### Don'ts ❌

1. **Don't Calibrate Blindly**: Understand parameter effects
2. **Don't Skip Testing**: Always verify after changes
3. **Don't Forget to Store**: Values may be lost on restart
4. **Don't Calibrate During Production**: Causes module unavailability
5. **Don't Use Extreme Values**: Can damage hardware
6. **Don't Mix Manual and MQTT Calibration**: Choose one method

### Troubleshooting Calibration Issues

| Symptom | Possible Cause | Solution |
|---------|----------------|----------|
| Changes don't persist | Not stored | Send `storeCalibrationValues` |
| Can't enter calibration mode | Module busy | Cancel active orders first |
| Position test fails | Wrong coordinates | Re-measure encoder values |
| Sensor readings unstable | Environmental factors | Shield sensors, adjust thresholds |
| Module crashes | Invalid parameter value | Reset to factory defaults |

## 7.6 Calibration Data Topics

### Publishing Calibration Data

The CCU can publish calibration data during calibration:

**Topic**: `ccu/state/calibration/<serial>`

**Example**:
```json
{
  "timestamp": "2024-12-08T14:20:00.000Z",
  "serialNumber": "HBW001",
  "parameters": {
    "cal__colA": 1250,
    "cal__colB": 2500,
    "cal__colC": 3750,
    "cal__row1": 500,
    "cal__row2": 1500,
    "cal__row3": 2500
  }
}
```

This allows external tools to monitor and log calibration activities.

## Next Steps

- See [Manual Intervention](08-manual-intervention.md) for warnings about manual control
- Review [Module Documentation](06-modules.md) for module-specific calibration details
- Consult module-specific source documentation for advanced calibration
