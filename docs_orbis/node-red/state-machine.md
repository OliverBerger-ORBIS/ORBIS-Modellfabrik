# State Machine Documentation

This document describes the **VDA 5050 compliant state machine** implemented in the Orbis Agile Production Simulation system.

## 🔄 State Machine Overview

The system implements a sophisticated state machine that manages the lifecycle of production actions, module connections, and error conditions. This follows the **VDA 5050 standard** for autonomous mobile robots and industrial automation.

## 📊 Action States

### **Primary Action States**

| State | Description | Color | Next States |
|-------|-------------|-------|-------------|
| **PENDING** | Action received, waiting to start | 🟡 Yellow | RUNNING, FAILED |
| **RUNNING** | Action currently executing | 🟡 Yellow | FINISHED, FAILED |
| **FINISHED** | Action completed successfully | 🟢 Green | PENDING |
| **FAILED** | Action failed with errors | 🔴 Red | PENDING |

### **State Transition Flow**

```
PENDING → RUNNING → FINISHED
    ↓         ↓
  FAILED ← FAILED
```

### **State Implementation**

#### **PENDING State**
```javascript
// Action received and validated
actionState.state = "PENDING";
actionState.command = msg.order ?? msg.instantAction;
actionState.id = msg.actionId;
```

#### **RUNNING State**
```javascript
// Action execution started
actionState.state = "RUNNING";
// Update timestamp and metadata
state.timestamp = new Date().toISOString();
```

#### **FINISHED State**
```javascript
// Action completed successfully
actionState.state = "FINISHED";
// Clear order ID, update loads
flow.set("$parent.orderId", "0");
```

#### **FAILED State**
```javascript
// Action failed
actionState.state = "FAILED";
// Collect errors
state.errors = flowErrors ? Array.isArray(flowErrors) ? flowErrors : [flowErrors] : [];
```

## 🔌 Connection States

### **Connection State Types**

| State | Description | Color | Trigger |
|-------|-------------|-------|---------|
| **ONLINE** | Module connected and operational | 🟢 Green | Successful OPC-UA connection |
| **OFFLINE** | Module disconnected | 🔴 Red | Manual disconnect |
| **CONNECTIONBROKEN** | Connection lost unexpectedly | 🔴 Red | Network timeout |

### **Connection State Implementation**

```javascript
// MQTT Birth/Will messages
birthPayload: "{\"connectionState\":\"ONLINE\"}"
willPayload: "{\"connectionState\":\"CONNECTIONBROKEN\"}"
closePayload: "{\"connectionState\":\"OFFLINE\"}"
```

## 🏭 Module States

### **Module Operating States**

| State | Description | Behavior |
|-------|-------------|----------|
| **IDLE** | Ready for new orders | Accepts new orders |
| **BUSY** | Processing current order | Rejects new orders |
| **ERROR** | Error condition | Requires reset |

### **Module State Transitions**

```
IDLE → BUSY → IDLE
  ↓      ↓
ERROR ← ERROR
```

## 🎯 State Management Functions

### **Action State Update Function**

```javascript
function updateActionState(state, metadata = undefined) {
    const actionState = flow.get("$parent.actionState") ?? {};
    actionState.id = msg.actionId ?? actionState.id;
    actionState.state = state;
    actionState.command = msg.actionCommand ?? actionState.command;
    actionState.metadata = metadata ?? actionState.metadata ?? {};
    flow.set("$parent.actionState", actionState);
    return actionState;
}
```

### **State Creation Function**

```javascript
function createState(actionState, loads = undefined) {
    const state = flow.get("$parent.state");
    const timestamp = new Date().toISOString();
    const headerId = flow.get("$parent.headerId");

    state.headerId = headerId;
    state.loads = loads ?? state.loads ?? [];
    state.actionState = actionState;
    state.timestamp = timestamp;
    state.orderId = flow.get("$parent.orderId");
    state.orderUpdateId = flow.get("$parent.orderUpdateId");
    state.errors = [];
    state.paused = msg.modulePaused ?? state.paused;
    state.operatingMode = msg.operatingMode ?? state.operatingMode;

    // Increment header ID
    flow.set("$parent.headerId", headerId + 1);
    flow.set("$parent.state", state);
    return state;
}
```

## 🔍 State Validation

### **Order ID Validation**

```javascript
function isMatchingOrderId() {
    const existingOrderId = flow.get("$parent.orderId");
    const actionState = flow.get("$parent.actionState.state");

    if (actionState == "FINISHED" || actionState == "FAILED") {
        flow.set("$parent.orderId", msg.orderId);
        return msg;
    }

    if (msg.orderId == existingOrderId || existingOrderId == "0") {
        flow.set("$parent.orderId", msg.orderId);
        return msg;
    }

    // Error: OrderId not valid
    return [null, msg];
}
```

### **Serial Number Validation**

```javascript
function matchesSerialNumber() {
    const serialNumber = flow.get("$parent.serialNumber") ?? "MISSING-SERIALNUMBER";
    if (msg.serialNumber != serialNumber) {
        // Error: SerialNumber does not match
        return [null, msg];
    }
    return msg;
}
```

## 🚨 Error Handling

### **Error Types**

| Error Type | Level | Description |
|------------|-------|-------------|
| **Validation** | WARNING | Malformed messages, invalid parameters |
| **Connection** | WARNING | Network issues, OPC-UA failures |
| **Operation** | FATAL | Failed actions, hardware errors |
| **System** | FATAL | Critical system failures |

### **Error Structure**

```javascript
const error = {
    timestamp: new Date().toISOString(),
    errorType: "PICK_failed",
    errorMessage: "PICK failed",
    errorLevel: "FATAL",
    errorReferences: [
        { "topic": "order" },
        { "headerId": flow.get("headerId") },
        { "orderId": msg.orderId },
        { "orderUpdateId": msg.orderUpdateId }
    ]
};
```

## 📡 State Publishing

### **MQTT State Topics**

- `module/v1/ff/{serialNumber}/state` - Action state updates
- `module/v1/ff/{serialNumber}/connection` - Connection state updates

### **State Message Format**

```javascript
{
    "headerId": 123,
    "timestamp": "2024-01-15T10:30:00.000Z",
    "serialNumber": "FF22-001",
    "actionState": {
        "id": "action-456",
        "state": "RUNNING",
        "command": "PICK",
        "metadata": {}
    },
    "loads": [],
    "errors": [],
    "paused": false,
    "operatingMode": "AUTOMATIC"
}
```

## 🔧 State Machine Subflows

### **VDA Status Finished InstantAction**
- **Purpose**: Handle successful action completion
- **Input**: Action completion message
- **Output**: FINISHED state message
- **Color**: 🟢 Green

### **VDA Status Running InstantAction**
- **Purpose**: Handle action execution start
- **Input**: Action start message
- **Output**: RUNNING state message
- **Color**: 🟡 Yellow

### **VDA Status Failed InstantAction**
- **Purpose**: Handle action failures
- **Input**: Error message
- **Output**: FAILED state message
- **Color**: 🔴 Red

## 🎛️ State Monitoring

### **Status Indicators**

- **Node Status**: Visual indicators in Node-RED UI
- **MQTT Messages**: Real-time state updates
- **Error Logs**: Detailed error tracking
- **Performance Metrics**: State transition timing

### **Debug Functions**

```javascript
// Status update
node.status({ 
    shape: "dot", 
    fill: "green", 
    text: `${parentFlowName} / ${actionState.command}: ${actionState.state}` 
});

// Debug output
msg.topic = flow.get("$parent.MQTT_topic") + "/state";
msg.payload = state;
```

## 🔄 State Recovery

### **Recovery Mechanisms**

1. **Automatic Recovery**: Retry failed actions
2. **Manual Reset**: Clear error states
3. **State Reset**: Reset to IDLE state
4. **Connection Recovery**: Reconnect to OPC-UA

### **Recovery Functions**

```javascript
// Reset to IDLE
flow.set("$parent.moduleState", "IDLE");
flow.set("$parent.errors", []);

// Clear action state
flow.set("$parent.actionState", {});
```

---

## 📁 Folder Organization

This documentation is part of the Orbis customizations (`docs-orbis/`) and documents the state machine implementation found in the original Fischertechnik Node-RED flows located in the `Node-RED/` folder.

---

*This state machine implementation follows VDA 5050 standards and provides robust error handling and recovery mechanisms for industrial automation.* 