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
