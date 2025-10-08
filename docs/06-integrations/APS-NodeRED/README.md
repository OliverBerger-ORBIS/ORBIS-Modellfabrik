# 🔴 Node-RED Integration Documentation

> 📖 **Zentrale Referenz:** [00-REFERENCE](../00-REFERENCE/README.md) - Verifizierte APS-Architektur
> 
> **NodeRed-Rolle:** OPC-UA ↔ MQTT Bridge für MILL/DRILL/HBW Module
> 
> **NICHT:** Order-Management, UUID-Generation (das macht CCU-Backend!)

Diese Sektion enthält die umfassende Dokumentation der Node-RED Flows der Fischertechnik Agile Production Simulation (APS).


## System Overview

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

## 🔗 Integration Management

- **[Node-RED Integration](../../../integrations/APS-NodeRED/README.md)** - Backup, Restore und Management
- **[Integration Guide](./integration-guide.md)** - Detaillierte Setup-Anleitung

> **🔗 Verwandte Systeme:**
> - **[APS-CCU](../APS-CCU/README.md)** - Fischertechnik Agile Production Simulation
> - **[TXT-FTS VDA 5050](../TXT-FTS/README.md)** - Fahrerloses Transportsystem
> - **[System Context](../../02-architecture/system-context.md)** - Gesamtarchitektur

## 📋 Documentation Index

### [Flows](./flows.md)
- Tab structure and organization
- Module-specific flows (MILL, DRILL, OVEN, AIQS, HBW, DPS)
- Flow grouping and organization
- Detailed flow analysis and implementation
- Node-RED flow patterns and best practices
- State diagrams and pseudocode

### [OPC UA Nodes](./opc-ua-nodes.md)
- OPC UA NodeIds and state transitions
- Connection states and error handling
- Module-specific OPC UA implementations

### [State Machine](./state-machine.md)
- VDA 5050 compliant state transitions
- Action states: PENDING → RUNNING → FINISHED/FAILED
- Connection states: ONLINE/OFFLINE/CONNECTIONBROKEN
- Error handling and recovery

### [Integration Guide](./integration-guide.md)
- Backup and restore procedures
- SSH and Admin API management
- Troubleshooting and maintenance

### [System Architecture](../../02-architecture/system-context.md)
- Gesamtarchitektur und System-Kontext
- Verlinkung zur zentralen Architektur-Dokumentation

## 🔧 Quick Reference

### System Components
- **6 Production Modules** (MILL, DRILL, AIQS, DPS, HBW, OVEN)
- **Node-RED Central Control Unit** (Raspberry Pi)
- **MQTT Broker** (Message Routing)
- **OPC-UA Network** (Module Communication)

### Key Files
- `flows.json` - Main Node-RED configuration
- `settings.js` - Node-RED settings
- Environment variables for configuration

### Access Points
- **Node-RED UI**: `http://192.168.0.100:1880/`
- **SSH Access**: `ff22` / `ff22+`
- **MQTT Topics**: `module/v1/ff/{serialNumber}/{action}`

### Network Details
- **Node-RED**: 192.168.0.100:1880
- **MQTT Broker**: 192.168.2.189:1883
- **OPC-UA Modules**: 192.168.0.40-90:4840

## 📊 **MQTT-Topic-Hierarchie**

```mermaid
graph TD
    ROOT["ROOT"]

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

    classDef module fill:#fff8e1,stroke:#ffecb3,stroke-width:2px,color:#0b3d16
    classDef ccu fill:#ffebee,stroke:#ffcdd2,stroke-width:2px,color:#7a1a14
    classDef system fill:#f5f5f5,stroke:#e0e0e0,stroke-width:2px,color:#333

    class MODULE,SERIAL,STATE,ORDER,CONNECTION,INSTANTACTION module
    class CCU,GLOBAL,ORDERREQ,ORDERACT ccu
    class SYSTEM,RACK,SERIALREAD system
```

## 🚀 Getting Started

1. **Review Architecture** - Understand the overall system design
2. **Study Flows** - Learn how modules are organized
3. **Understand States** - Master the state machine logic
4. **Practice Development** - Follow development guidelines

---

## 📁 Current Node-RED Structure

Diese Dokumentation beschreibt die **aktuelle Fischertechnik APS Node-RED Struktur** vor der OMF Dashboard Integration. Die tatsächliche Integration und Anpassungen sind Teil des "großen Projektes" und werden separat dokumentiert.

### Current System Structure
```
integrations/APS-NodeRED/       # Aktuelle Node-RED Backups
├── backups/                    # flows.json Backups
├── project/                    # Node-RED Projekt-Dateien
└── scripts/                    # Management Scripts

docs/06-integrations/APS-NodeRED/  # Dokumentation der IST-Struktur
├── README.md                   # Diese Datei
├── flows.md                    # Alle Flow-Details
├── opc-ua-nodes.md             # OPC UA NodeIds und States
├── state-machine.md            # State Machine Dokumentation
└── integration-guide.md        # Backup/Restore Anleitung
```

> **⚠️ Hinweis:** Diese Dokumentation beschreibt das **IST-System** (Fischertechnik APS). Die zukünftige Integration mit dem OMF Dashboard und eventuelle Anpassungen werden im Rahmen des "großen Projektes" geplant und dokumentiert.

---

*For technical support, contact the ORBIS Development Team*