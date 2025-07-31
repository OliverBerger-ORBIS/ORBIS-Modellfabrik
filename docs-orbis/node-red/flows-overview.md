# Node-RED Flows Overview

This document provides a comprehensive overview of the Node-RED flows structure in the Orbis Agile Production Simulation system.

## 📋 System Architecture

The Node-RED system consists of **25 main tabs** plus initialization and utility flows, implementing a **VDA 5050 compliant state machine** for industrial automation.

### **Flow Categories**

1. **Initialization** (1 tab)
2. **Production Modules** (23 tabs)
3. **Central Systems** (1 tab)

## 🏭 Production Modules

### **MILL Modules** (5 units)
| Module | Tab ID | OPC-UA Endpoint | Function |
|--------|--------|-----------------|----------|
| MILL #1 | `9810df827082ae56` | `192.168.0.40:4840` | Primary milling operations |
| MILL #2 | `f6c8f50b75376b12` | `192.168.0.41:4840` | Secondary milling operations |
| MILL #3 | `05a427a07096ebdb` | `192.168.0.42:4840` | Tertiary milling operations |
| MILL #4 | `a0e5f985232949c9` | `192.168.0.43:4840` | Quaternary milling operations |
| MILL #5 | `5fc4fbd01fd96575` | `192.168.0.44:4840` | Quinary milling operations |

**Key Features:**
- Milling operation control
- Tool management
- Quality monitoring
- Error handling

### **DRILL Modules** (5 units)
| Module | Tab ID | OPC-UA Endpoint | Function |
|--------|--------|-----------------|----------|
| DRILL #1 | `74c49629fbf36c6c` | `192.168.0.50:4840` | Primary drilling operations |
| DRILL #2 | `4b7639b8a17bacd0` | `192.168.0.51:4840` | Secondary drilling operations |
| DRILL #3 | `b8be3e0d96a62731` | `192.168.0.52:4840` | Tertiary drilling operations |
| DRILL #4 | `4cb2aa8b5e3c04ee` | `192.168.0.53:4840` | Quaternary drilling operations |
| DRILL #5 | `490d04c5383c1492` | `192.168.0.54:4840` | Quinary drilling operations |

**Key Features:**
- Drilling operation control
- Depth management
- Tool wear monitoring
- Safety interlocks

### **OVEN Modules** (5 units)
| Module | Tab ID | OPC-UA Endpoint | Function |
|--------|--------|-----------------|----------|
| OVEN #1 | `2edb0a9a7b9b6718` | `192.168.0.60:4840` | Primary heat treatment |
| OVEN #2 | `306206362e6386f0` | `192.168.0.61:4840` | Secondary heat treatment |
| OVEN #3 | `38289fd68fd11ff8` | `192.168.0.62:4840` | Tertiary heat treatment |
| OVEN #4 | `173ad22f4bdd0609` | `192.168.0.63:4840` | Quaternary heat treatment |
| OVEN #5 | `717abb2ca5ab1654` | `192.168.0.64:4840` | Quinary heat treatment |

**Key Features:**
- Temperature control
- Heating cycles
- Safety monitoring
- Energy management

### **AIQS Modules** (5 units) - Quality Inspection
| Module | Tab ID | OPC-UA Endpoint | Function |
|--------|--------|-----------------|----------|
| AIQS #1 | `e811f976a7becb7c` | `192.168.0.70:4840` | Primary quality inspection |
| AIQS #2 | `5983ec78decb4bc7` | `192.168.0.71:4840` | Secondary quality inspection |
| AIQS #3 | `8464a92f18f7bec3` | `192.168.0.72:4840` | Tertiary quality inspection |
| AIQS #4 | `1b1092be024196cd` | `192.168.0.73:4840` | Quaternary quality inspection |
| AIQS #5 | `2a102a482beaf61c` | `192.168.0.74:4840` | Quinary quality inspection |

**Key Features:**
- Automated quality inspection
- Image processing
- Defect detection
- Quality reporting
- Calibration management

### **HBW Modules** (3 units) - High Bay Warehouse
| Module | Tab ID | OPC-UA Endpoint | Function |
|--------|--------|-----------------|----------|
| HBW #1 | `2ad740b531e49822` | `192.168.0.80:4840` | Primary storage |
| HBW #2 | `fd2a2507d5769687` | `192.168.0.81:4840` | Secondary storage |
| HBW #3 | `814355edd4de93bc` | `192.168.0.82:4840` | Tertiary storage |

**Key Features:**
- Storage and retrieval
- Inventory management
- Position tracking
- Load handling

## 🎛️ Central Systems

### **DPS** - Digital Production System
| Component | Tab ID | OPC-UA Endpoint | Function |
|-----------|--------|-----------------|----------|
| DPS | `616d25e29ffaadda` | `192.168.0.90:4840` | Central coordination |

**Key Features:**
- Order management
- Production scheduling
- Resource allocation
- System monitoring
- Data collection

## 🔧 Initialization & Utilities

### **NodeRed Init** (`f39c18cc6f60e7a0`)
- **Global Reset** functionality
- **MQTT Broker** configuration
- **Dynamic Connection** management
- **System Initialization**

## 📊 Flow Organization

### **Grouping Structure**
Each module flow contains organized groups:

1. **CHECK_QUALITY Groups** (AIQS modules)
   - TXT controller integration
   - Calibration image processing
   - Quality assessment

2. **Communication Groups**
   - OPC-UA message handling
   - MQTT topic management
   - Error handling

3. **State Management Groups**
   - Action state tracking
   - Load management
   - Error collection

## 🔄 Common Flow Patterns

### **Standard Module Flow**
```
Input → Validation → Processing → State Update → Output
```

### **Error Handling Pattern**
```
Error Detection → Error Classification → Error Reporting → Recovery
```

### **State Transition Pattern**
```
PENDING → RUNNING → FINISHED/FAILED
```

## 📈 Data Flow

1. **Order Reception** via MQTT
2. **Validation** of serial number, action type, order ID
3. **Processing** according to module capabilities
4. **State Updates** published to MQTT
5. **Error Handling** if required

## 🔍 Key Components

### **MQTT Topics**
- `module/v1/ff/{serialNumber}/order` - Order reception
- `module/v1/ff/{serialNumber}/state` - State updates
- `module/v1/ff/{serialNumber}/connection` - Connection status
- `module/v1/ff/{serialNumber}/instantAction` - Instant actions

### **OPC-UA Integration**
- Each module has dedicated OPC-UA endpoint
- Standard port 4840
- Security disabled for development
- Real-time data exchange

### **Error Handling**
- **Validation Errors** - Malformed messages
- **Connection Errors** - Network issues
- **Operation Errors** - Failed actions
- **Error Levels** - WARNING, FATAL

---

## 📁 Folder Organization

This documentation is part of the Orbis customizations (`docs-orbis/`) and analyzes the original Fischertechnik Node-RED flows located in the `Node-RED/` folder.

---

*This documentation is based on the Fischertechnik Agile Production Simulation 24V system, customized for Orbis development.* 