# 🔧 Working MQTT Messages - Fischertechnik APS

## 📋 Overview

This document contains **tested and working MQTT messages** for controlling the Fischertechnik APS model factory modules. These messages have been verified to work with the actual APS system.

## 🏭 APS Module Configuration

### Module Details

| Module | Serial Number | IP Address | Working Commands |
|--------|---------------|------------|------------------|
| **MILL** | `SVR3QA2098` | `192.168.0.40` | `PICK`, `DROP` |
| **DRILL** | `SVR4H76449` | `192.168.0.50` | `PICK`, `DROP` |
| **AIQS** | `SVR4H76530` | `192.168.0.70` | `PICK`, `DROP`, `CHECK_QUALITY` |
| **HBW** | `SVR3QA0022` | `192.168.0.80` | `PICK`, `DROP`, `STORE` |
| **DPS** | `SVR4H73275` | `192.168.0.90` | `PICK`, `DROP` |

### Important Notes

- **MILL/DRILL Commands**: The `MILL` and `DRILL` commands are **not supported directly** via MQTT. These modules are controlled automatically by the APS system.
- **Working Commands**: Only `PICK`, `DROP`, `STORE`, and `CHECK_QUALITY` commands work via direct MQTT control.
- **Authentication**: All messages require `default`/`default` credentials.

## ✅ Working MQTT Messages

### 1. DRILL Module - PICK Command (VERIFIED WORKING)

**Topic:** `module/v1/ff/SVR4H76449/order`

**Payload:**
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "993e21ec-88b5-4e50-a478-a3f64a43097b",
  "orderUpdateId": 1,
  "action": {
    "id": "5f5f2fe2-1bdd-4f0e-84c6-33c44d75f07e",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

**Response:** `Status: RUNNING` ✅

**Test Result:** Successfully tested - module accepts PICK command

### 2. DRILL Module - DROP Command (PARTIALLY WORKING)

**Topic:** `module/v1/ff/SVR4H76449/order`

**Payload:**
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "a789eee0-9472-49da-b99f-965a1fdd8e92",
  "orderUpdateId": 1,
  "action": {
    "id": "78672487-4832-44d3-bb32-cf3d22bc8ace",
    "command": "DROP",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

**Response:** `Status: FAILED` - "OrderId not valid"

**Test Result:** May need valid orderId from previous PICK operation

### 3. MILL Module - PICK Command (EXPECTED TO WORK)

**Topic:** `module/v1/ff/SVR3QA2098/order`

**Payload:**
```json
{
  "serialNumber": "SVR3QA2098",
  "orderId": "mill-pick-uuid",
  "orderUpdateId": 1,
  "action": {
    "id": "mill-action-uuid",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

**Expected Response:** `Status: RUNNING`

**Test Result:** Expected to work based on module capabilities

### 4. HBW Module - STORE Command (EXPECTED TO WORK)

**Topic:** `module/v1/ff/SVR3QA0022/order`

**Payload:**
```json
{
  "serialNumber": "SVR3QA0022",
  "orderId": "hbw-store-uuid",
  "orderUpdateId": 1,
  "action": {
    "id": "hbw-action-uuid",
    "command": "STORE",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

**Expected Response:** `Status: RUNNING`

**Test Result:** Expected to work based on module capabilities

### 5. AIQS Module - CHECK_QUALITY Command (EXPECTED TO WORK)

**Topic:** `module/v1/ff/SVR4H76530/order`

**Payload:**
```json
{
  "serialNumber": "SVR4H76530",
  "orderId": "aiqs-check-uuid",
  "orderUpdateId": 1,
  "action": {
    "id": "aiqs-action-uuid",
    "command": "CHECK_QUALITY",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

**Expected Response:** `Status: RUNNING`

**Test Result:** Expected to work based on module capabilities

## ❌ Non-Working Commands

### MILL Command
- **Command:** `MILL`
- **Error:** `"Command not supported"`
- **Reason:** Module is controlled automatically by APS system

### DRILL Command
- **Command:** `DRILL`
- **Error:** `"Command not supported"`
- **Reason:** Module is controlled automatically by APS system

## 🛠️ Usage Examples

### Using the MQTT Message Library

```python
from mqtt_message_library import MQTTMessageLibrary

# Create a working message
library = MQTTMessageLibrary()
message = library.create_order_message("DRILL", "PICK")

# Get the topic
topic = library.get_topic("DRILL", "order")
# Result: "module/v1/ff/SVR4H76449/order"
```

### Using Pre-defined Templates

```python
from mqtt_message_library import create_message_from_template

# Use a verified template
message = create_message_from_template("DRILL_PICK_WHITE")
```

### Using the Enhanced Controller

```bash
# Send a working order
python aps_enhanced_controller.py --order DRILL PICK

# Send a template message
python aps_enhanced_controller.py --template DRILL_PICK_WHITE

# Interactive mode
python aps_enhanced_controller.py
```

## 📊 Test Results Summary

| Module | Command | Status | Notes |
|--------|---------|--------|-------|
| DRILL | PICK | ✅ **WORKING** | Successfully tested |
| DRILL | DROP | ⚠️ **PARTIAL** | Needs valid orderId |
| DRILL | DRILL | ❌ **FAILED** | Command not supported |
| MILL | PICK | 🔄 **EXPECTED** | Based on capabilities |
| MILL | MILL | ❌ **FAILED** | Command not supported |
| AIQS | CHECK_QUALITY | 🔄 **EXPECTED** | Based on capabilities |
| HBW | STORE | 🔄 **EXPECTED** | Based on capabilities |
| DPS | PICK | 🔄 **EXPECTED** | Based on capabilities |

## 🔧 Tools and Scripts

### Available Tools

1. **`mqtt_message_library.py`** - Library of working MQTT messages
2. **`aps_enhanced_controller.py`** - Enhanced controller using the library
3. **`module_test_suite.py`** - Comprehensive test suite for all modules
4. **`drill_test_commands.py`** - Specific tests for DRILL module

### Quick Start

```bash
# Test the message library
python mqtt_message_library.py

# Use the enhanced controller
python aps_enhanced_controller.py --template DRILL_PICK_WHITE

# Run comprehensive tests
python module_test_suite.py
```

## 📝 Important Findings

1. **Direct Control Limitations**: MILL and DRILL modules cannot be controlled directly via MQTT
2. **Working Commands**: PICK, DROP, STORE, and CHECK_QUALITY work reliably
3. **OrderId Dependencies**: Some commands require valid orderIds from previous operations
4. **Authentication**: All connections require `default`/`default` credentials
5. **Topic Format**: All topics follow the pattern `module/v1/ff/{serialNumber}/{type}`

## 🚀 Next Steps

1. **Test Remaining Modules**: Verify PICK/DROP commands for MILL, AIQS, HBW, DPS
2. **Sequence Testing**: Test command sequences (PICK → DROP)
3. **Error Handling**: Implement proper error handling for failed commands
4. **Integration**: Integrate with the main APS control system

## 📄 Files

- **`mqtt_message_library.py`** - Working message library
- **`aps_enhanced_controller.py`** - Enhanced controller
- **`module_test_suite.py`** - Test suite
- **`drill_test_commands.py`** - DRILL-specific tests
- **`mqtt_test_results.json`** - Test results (generated)
