# FF_DPS_24V.py - DPS TXT Controller Analysis

## Overview
**FF_DPS_24V.py** is the central control unit (CCU) of the APS Modellfabrik. It runs on the DPS TXT Controller (192.168.0.102) and serves as the main interface for the APS Dashboard.

## Key Components

### 1. **Main Program Structure**
```python
# Core imports
from fischertechnik.mqtt.MqttClient import MqttClient
from lib.vda5050 import *  # VDA5050 AGV communication standard
from lib.mqtt_utils import *  # MQTT utilities
from lib.Factory import *  # Factory-wide functions
from lib.DPS import *  # DPS-specific functions
```

### 2. **Order Management System**
- **Order State**: `has_order` (global variable)
- **Order Processing**: `order_callback(message)` function
- **Order ID Management**: Via VDA5050 standard
- **Order Types**: "STORAGE" orders for workpiece processing

### 3. **Instant Actions (Dashboard Commands)**
```python
INSTANT_ACTION_RESET = 'reset'
INSTANT_ACTION_ACCOUNCE_OUTPUT = 'announceOutput'  
INSTANT_ACTION_CANCEL_STORAGE_ORDER = 'cancelStorageOrder'
```

## MQTT Integration

### **Subscribed Topics**
1. **VDA5050 Order Topic**: `module/v1/ff/NodeRed/{controller_id}/order`
2. **VDA5050 Instant Action Topic**: `module/v1/ff/NodeRed/{controller_id}/instantActions`
3. **Sensor Data Topics**:
   - `/j1/txt/1/c/bme680` (BME680 sensor)
   - `/j1/txt/1/c/ldr` (Light sensor)
   - `/j1/txt/1/c/cam` (Camera data)
   - `/j1/txt/1/c/broadcast` (Broadcast messages)

### **Published Topics**
1. **VDA5050 State**: `module/v1/ff/NodeRed/{controller_id}/state`
2. **VDA5050 Connection**: `module/v1/ff/NodeRed/{controller_id}/connection`
3. **VDA5050 Factsheet**: `module/v1/ff/NodeRed/{controller_id}/factsheet`
4. **System Control**: `ccu/set/*` (reset, charge, layout, etc.)
5. **NFC Commands**: `/j1/txt/1/f/i/nfc/ds`

## Order Processing Flow

### **1. Order Reception**
```python
def order_callback(message):
    has_order = vda_process_order(message.payload.decode("utf-8"))
    vda_publish_status()
```

### **2. Order Validation**
- **Required Fields**: `orderId`, `timestamp`, `action`
- **Order ID Management**: Prevents duplicate orders
- **Update ID Handling**: Manages order updates

### **3. Order Execution**
- **Order Type**: "STORAGE" for workpiece processing
- **Color Detection**: Workpiece color identification
- **NFC Integration**: Workpiece ID management
- **VDA5050 Compliance**: Standard AGV communication

## Dashboard Command Mapping

### **"Bestellung RED/BLUE/WHITE" Commands**
1. **Order Creation**: Via VDA5050 order topic
2. **Order Processing**: `vda_process_order()` function
3. **Status Updates**: `vda_publish_status()` function
4. **Order Completion**: Order ID reset after completion

### **"Factory Reset" Command**
1. **Reset Request**: `reset_set_request()` function
2. **State Reset**: All modules return to initial state
3. **Order Clearing**: Active orders are cancelled

### **"FTS Charge" Commands**
1. **FTS Control**: Via `ccu/set/charge` topic (System Control)
2. **Charging Station**: CHRG0 module interaction  
3. **Status Management**: FTS state tracking
4. **Publisher**: APS-Dashboard → `ccu/set/charge`

## Key Functions for OMF Dashboard

### **1. Order Management**
```python
def order_callback(message):
    # Process incoming orders from dashboard
    has_order = vda_process_order(message.payload.decode("utf-8"))
    vda_publish_status()
```

### **2. Instant Actions**
```python
def mqtt_instant_action_callback(message):
    # Handle dashboard commands (reset, announce output, etc.)
    for i in vda_handle_instant_actions_get_custom(message.payload.decode("utf-8"), ...):
        if i['actionType'] == INSTANT_ACTION_RESET:
            reset_set_request()
```

### **3. Status Publishing**
```python
def vda_publish_status():
    # Publish current module status to dashboard
    mqtt_get_client().publish(topic=str(vda_namespace) + 'state', ...)
```

## VDA5050 Integration

### **Namespace Pattern**
```
module/v1/ff/NodeRed/{controller_id}/
```

### **Message Types**
1. **State Messages**: Current module status
2. **Order Messages**: Workpiece processing orders
3. **Instant Action Messages**: Dashboard commands
4. **Connection Messages**: Online/offline status

## Threading Architecture

### **Main Threads**
1. **VGR Thread**: `thread_VGR()` - Robotic arm control
2. **DPS Thread**: `thread_DPS()` - DPS module control
3. **MQTT Threads**: Background MQTT communication

### **Sensor Threads**
- **BME680**: Environmental sensor data
- **LDR**: Light sensor data  
- **Camera**: Image processing data
- **Broadcast**: System-wide messages

## Configuration Files

### **1. .project.json**
```json
{
  "uuid": "e2679fc1-bbd2-5142-2ec8-ad7e1cab3590",
  "name": "FF_DPS_24V",
  "mode": "ADVANCED", 
  "version": "1.0",
  "controller": "TXT4"
}
```

### **2. data/config.json**
- Module configuration parameters
- Calibration data
- Factory settings

## Implications for OMF Dashboard

### **1. Order System**
- **Order Creation**: Must send VDA5050-compliant orders
- **Order Tracking**: Monitor order status via state messages
- **Order Completion**: Handle order completion notifications

### **2. Command System**
- **Instant Actions**: Send commands via instant action topic
- **Reset Commands**: Factory reset functionality
- **Status Monitoring**: Subscribe to state messages

### **3. MQTT Topics**
- **Use VDA5050 Namespace**: `module/v1/ff/NodeRed/{controller_id}/`
- **QoS 2**: Reliable message delivery
- **Retain Messages**: State persistence

### **4. Integration Points**
- **Order Management**: Replace dashboard order system
- **Status Display**: Real-time module status
- **Command Interface**: Unified command system
- **Error Handling**: VDA5050 error reporting

## Next Steps

1. **Extract MQTT Topics**: Complete topic mapping
2. **Analyze VDA5050 Messages**: Message format understanding
3. **Map Dashboard Commands**: Command-to-function mapping
4. **Design OMF Integration**: OMF dashboard adaptation
5. **Test Integration**: Validate with real hardware

## Files to Analyze Next

1. **lib/vda5050.py**: Complete VDA5050 implementation
2. **lib/mqtt_utils.py**: MQTT utility functions
3. **lib/Factory.py**: Factory-wide functions
4. **lib/DPS.py**: DPS-specific logic
5. **data/config.json**: Configuration parameters
