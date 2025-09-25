# Node-RED Flows - Fischertechnik APS

## Overview

Die Node-RED Flows der Fischertechnik Agile Production Simulation (APS) sind in Tabs organisiert.
Jeder Tab repräsentiert ein Produktionsmodul oder eine Systemkomponente.

## Tab Structure

### Production Modules

### System Components

- **NodeRed Init** - System initialization
- **Global Functions** - Shared functionality
- **MQTT Configuration** - Message broker setup

## Flow Organization

### Module-Specific Flows

Jedes Produktionsmodul hat eigene Flows für:
- State management
- Command processing
- OPC-UA communication
- MQTT messaging

### Shared Flows

- Order processing
- Status monitoring
- Error handling
- System configuration

## 📊 **Detailed Flow Analysis**

### System Statistics
- **Total Flows**: 1428
- **Function Nodes**: 402
- **Tabs**: 25

### Flow Patterns

#### State Management Pattern
```javascript
// State transition example
if (flow.get('moduleState') == 'IDLE') {
    flow.set('moduleState', 'PICKBUSY');
    // Execute PICK operation
}
```

#### OPC-UA Communication Pattern
```javascript
// OPC-UA write example
msg.payload = {
    nodeId: 'ns=4;i=5',
    value: 'PICK'
};
return msg;
```

#### MQTT Messaging Pattern
```javascript
// MQTT topic construction
msg.topic = flow.get('$parent.MQTT_topic') + '/state';
msg.payload = flow.get('moduleState');
return msg;
```

## 🔄 **Production Flow Diagram**

```mermaid
graph TD
    subgraph "Production Module Flow"
        START([Order Received])
        IDLE[IDLE State]
        PICK[PICK Operation]
        PROCESS[PROCESS Operation]
        DROP[DROP Operation]
        END([Order Complete])

        START --> IDLE
        IDLE -->|PICK Command| PICK
        PICK -->|PICK Complete| PROCESS
        PROCESS -->|PROCESS Complete| DROP
        DROP -->|DROP Complete| IDLE
        IDLE -->|No More Orders| END
    end

    subgraph "State Details"
        PICKBUSY[PICKBUSY]
        MILLBUSY[MILLBUSY]
        DRILLBUSY[DRILLBUSY]
        DROPBUSY[DROPBUSY]
    end

    PICK -.-> PICKBUSY
    PROCESS -.-> MILLBUSY
    PROCESS -.-> DRILLBUSY
    DROP -.-> DROPBUSY

    classDef start fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef process fill:#fff8e1,stroke:#ff9800,stroke-width:2px
    classDef state fill:#e3f2fd,stroke:#2196f3,stroke-width:2px

    class START,END start
    class PICK,PROCESS,DROP process
    class IDLE,PICKBUSY,MILLBUSY,DRILLBUSY,DROPBUSY state
```

## System Architecture

```mermaid
graph TB
    subgraph "APS-Ecosystem (Phase 0)"
        subgraph "Production Layer"
            MILL["MILL Module<br/>192.168.0.40:4840"]
            DRILL["DRILL Module<br/>192.168.0.50:4840"]
            AIQS["AIQS Module<br/>192.168.0.70:4840"]
            DPS["DPS Module<br/>192.168.0.90:4840"]
            HBW["HBW Module<br/>192.168.0.80:4840"]
            OVEN["OVEN Module<br/>192.168.0.60:4840"]
        end

        subgraph "Control Layer"
            NODERED["Node-RED<br/>192.168.0.100:1880"]
            MQTT["MQTT Broker<br/>192.168.2.189:1883"]
        end

        subgraph "Network Layer"
            SWITCH["Network Switch<br/>192.168.0.1"]
            ROUTER["Router<br/>192.168.2.1"]
        end
    end

    %% Production to Control
    MILL -->|OPC-UA| NODERED
    DRILL -->|OPC-UA| NODERED
    AIQS -->|OPC-UA| NODERED
    DPS -->|OPC-UA| NODERED
    HBW -->|OPC-UA| NODERED
    OVEN -->|OPC-UA| NODERED

    %% Control to MQTT
    NODERED -->|Publish/Subscribe| MQTT

    %% Network connections
    NODERED --> SWITCH
    MILL --> SWITCH
    DRILL --> SWITCH
    AIQS --> SWITCH
    DPS --> SWITCH
    HBW --> SWITCH
    OVEN --> SWITCH

    SWITCH --> ROUTER
    ROUTER --> MQTT

    classDef fthardware fill:#fff8e1,stroke:#ffecb3,stroke-width:2px,color:#0b3d16
    classDef ftsoftware fill:#ffebee,stroke:#ffcdd2,stroke-width:2px,color:#7a1a14
    classDef external fill:#f5f5f5,stroke:#e0e0e0,stroke-width:2px,color:#333

    class MILL,DRILL,AIQS,DPS,HBW,OVEN fthardware
    class NODERED ftsoftware
    class MQTT,SWITCH,ROUTER external
```
