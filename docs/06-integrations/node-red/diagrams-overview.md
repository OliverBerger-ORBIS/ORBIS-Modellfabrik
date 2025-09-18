# Diagrams Overview - Fischertechnik APS

## Module Status Transition Diagrams

### MILL Module
```mermaid
stateDiagram-v2
    [*] --> IDLE

    %% MILL Module Status Transitions
    IDLE -->|PICK Command| PICKBUSY
    PICKBUSY -->|PICK Complete| WAITING_AFTER_PICK
    WAITING_AFTER_PICK -->|MILL Command| MILLBUSY
    MILLBUSY -->|MILL Complete| WAITING_AFTER_MILL
    WAITING_AFTER_MILL -->|DROP Command| DROPBUSY
    DROPBUSY -->|DROP Complete| IDLE

    %% Error States
    PICKBUSY -->|Error| FAILED
    MILLBUSY -->|Error| FAILED
    DROPBUSY -->|Error| FAILED
    FAILED -->|Reset| IDLE

    %% Calibration
    IDLE -->|Calibration| CALIBRATION
    CALIBRATION -->|Complete| IDLE
```

### DRILL Module
```mermaid
stateDiagram-v2
    [*] --> IDLE

    %% DRILL Module Status Transitions
    IDLE -->|PICK Command| PICKBUSY
    PICKBUSY -->|PICK Complete| WAITING_AFTER_PICK
    WAITING_AFTER_PICK -->|DRILL Command| DRILLBUSY
    DRILLBUSY -->|DRILL Complete| WAITING_AFTER_DRILL
    WAITING_AFTER_DRILL -->|DROP Command| DROPBUSY
    DROPBUSY -->|DROP Complete| IDLE

    %% Error States
    PICKBUSY -->|Error| FAILED
    DRILLBUSY -->|Error| FAILED
    DROPBUSY -->|Error| FAILED
    FAILED -->|Reset| IDLE

    %% Calibration
    IDLE -->|Calibration| CALIBRATION
    CALIBRATION -->|Complete| IDLE
```

### AIQS Module
```mermaid
stateDiagram-v2
    [*] --> IDLE

    %% AIQS Module Status Transitions
    IDLE -->|PICK Command| PICKBUSY
    PICKBUSY -->|PICK Complete| WAITING_AFTER_PICK
    WAITING_AFTER_PICK -->|FIRE Command| FIREBUSY
    FIREBUSY -->|FIRE Complete| WAITING_AFTER_FIRE
    WAITING_AFTER_FIRE -->|DROP Command| DROPBUSY
    DROPBUSY -->|DROP Complete| IDLE

    %% Error States
    PICKBUSY -->|Error| FAILED
    FIREBUSY -->|Error| FAILED
    DROPBUSY -->|Error| FAILED
    FAILED -->|Reset| IDLE

    %% Calibration
    IDLE -->|Calibration| CALIBRATION
    CALIBRATION -->|Complete| IDLE
```

### DPS Module
```mermaid
stateDiagram-v2
    [*] --> IDLE

    %% DPS Module Status Transitions
    IDLE -->|PICK Command| PICKBUSY
    PICKBUSY -->|PICK Complete| WAITING
    WAITING -->|DROP Command| DROPBUSY
    DROPBUSY -->|DROP Complete| IDLE

    %% Error States
    PICKBUSY -->|Error| FAILED
    DROPBUSY -->|Error| FAILED
    FAILED -->|Reset| IDLE

    %% Calibration
    IDLE -->|Calibration| CALIBRATION
    CALIBRATION -->|Complete| IDLE
```

### HBW Module
```mermaid
stateDiagram-v2
    [*] --> IDLE

    %% HBW Module Status Transitions
    IDLE -->|PICK Command| PICKBUSY
    PICKBUSY -->|PICK Complete| WAITING
    WAITING -->|DROP Command| DROPBUSY
    DROPBUSY -->|DROP Complete| IDLE

    %% Error States
    PICKBUSY -->|Error| FAILED
    DROPBUSY -->|Error| FAILED
    FAILED -->|Reset| IDLE

    %% Calibration
    IDLE -->|Calibration| CALIBRATION
    CALIBRATION -->|Complete| IDLE
```

### OVEN Module
```mermaid
stateDiagram-v2
    [*] --> IDLE

    %% OVEN Module Status Transitions
    IDLE -->|PICK Command| PICKBUSY
    PICKBUSY -->|PICK Complete| WAITING_AFTER_PICK
    WAITING_AFTER_PICK -->|FIRE Command| FIREBUSY
    FIREBUSY -->|FIRE Complete| WAITING_AFTER_FIRE
    WAITING_AFTER_FIRE -->|DROP Command| DROPBUSY
    DROPBUSY -->|DROP Complete| IDLE

    %% Error States
    PICKBUSY -->|Error| FAILED
    FIREBUSY -->|Error| FAILED
    DROPBUSY -->|Error| FAILED
    FAILED -->|Reset| IDLE

    %% Calibration
    IDLE -->|Calibration| CALIBRATION
    CALIBRATION -->|Complete| IDLE
```

## System Architecture

```mermaid
graph TB
    subgraph "Fischertechnik APS System"
        subgraph "Production Layer"
            MILL[MILL Module<br/>192.168.0.40:4840]
            DRILL[DRILL Module<br/>192.168.0.50:4840]
            AIQS[AIQS Module<br/>192.168.0.70:4840]
            DPS[DPS Module<br/>192.168.0.90:4840]
            HBW[HBW Module<br/>192.168.0.80:4840]
            OVEN[OVEN Module<br/>192.168.0.60:4840]
        end

        subgraph "Control Layer"
            CCU[Central Control Unit<br/>Node-RED<br/>192.168.0.100:1880]
            MQTT[MQTT Broker<br/>192.168.2.189:1883]
        end

        subgraph "Network Layer"
            SWITCH[Network Switch<br/>192.168.0.1]
            ROUTER[Router<br/>192.168.2.1]
        end
    end

    %% Production to Control
    MILL -->|OPC-UA| CCU
    DRILL -->|OPC-UA| CCU
    AIQS -->|OPC-UA| CCU
    DPS -->|OPC-UA| CCU
    HBW -->|OPC-UA| CCU
    OVEN -->|OPC-UA| CCU

    %% Control to MQTT
    CCU -->|Publish/Subscribe| MQTT

    %% Network connections
    CCU --> SWITCH
    MILL --> SWITCH
    DRILL --> SWITCH
    AIQS --> SWITCH
    DPS --> SWITCH
    HBW --> SWITCH
    OVEN --> SWITCH

    SWITCH --> ROUTER
    ROUTER --> MQTT
```

## Production Flow

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
```

## OPC-UA Communication

```mermaid
sequenceDiagram
    participant NR as Node-RED
    participant OPC as OPC-UA Server
    participant HW as Hardware Module

    Note over NR,HW: Command Execution Flow

    NR->>OPC: Write Command
    OPC->>HW: Execute PICK Operation
    HW->>OPC: Operation Status
    OPC->>NR: Status Update

    Note over NR,HW: Status Monitoring

    NR->>OPC: Read Status
    OPC->>HW: Get Current State
    HW->>OPC: State Information
    OPC->>NR: State Response

    Note over NR,HW: Error Handling

    HW->>OPC: Error Occurred
    OPC->>NR: Error Status
    NR->>NR: Handle Error State
```

## MQTT Topic Hierarchy

```mermaid
graph TD
    ROOT[ROOT]

    subgraph "Module Topics"
        MODULE["module/v1/ff/"]
        SERIAL["serialNumber"]
        STATE["/state"]
        ORDER["/order"]
        CONNECTION["/connection"]
        INSTANTACTION["/instantAction"]
    end

    subgraph "CCU Topics"
        CCU["ccu/"]
        GLOBAL["global"]
        ORDERREQ["order/request"]
        ORDERACT["order/active"]
    end

    subgraph "System Topics"
        SYSTEM["system/"]
        RACK["rack.positions"]
        SERIALREAD["readSerial"]
    end

    ROOT --> MODULE
    ROOT --> CCU
    ROOT --> SYSTEM

    MODULE --> SERIAL
    SERIAL --> STATE
    SERIAL --> ORDER
    SERIAL --> CONNECTION
    SERIAL --> INSTANTACTION

    CCU --> GLOBAL
    CCU --> ORDERREQ
    CCU --> ORDERACT

    SYSTEM --> RACK
    SYSTEM --> SERIALREAD
```
