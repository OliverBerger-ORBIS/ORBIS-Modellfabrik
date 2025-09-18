# MQTT Pub/Sub Diagrams

## Overview

Graphische Darstellung der MQTT-Kommunikationsmuster in der APS-Modellfabrik basierend auf der Log-Analyse vom 18. September 2025.

## 1. High-Level System Overview

```mermaid
graph TB
    subgraph "APS Hardware"
        DPS["DPS TXT<br/>CCU + Modul"]
        AIQS["AIQS TXT<br/>Qualitätskontrolle"]
        CGW["CGW TXT<br/>Cloud-Gateway"]
        FTS["FTS TXT<br/>Transport"]
        MODULES["HBW, MILL, DRILL<br/>Produktionsmodule"]
    end
    
    subgraph "MQTT Broker"
        MQTT["Mosquitto<br/>192.168.0.100:1883"]
    end
    
    subgraph "Processing"
        NODE["Node-RED<br/>Pub + Sub Instanzen"]
    end
    
    subgraph "Frontend"
        DASH["APS-Dashboard<br/>Web-Interface"]
    end
    
    DPS --> MQTT
    AIQS --> MQTT
    CGW --> MQTT
    FTS --> MQTT
    MODULES --> MQTT
    
    MQTT --> NODE
    NODE --> MQTT
    
    MQTT --> DASH
    DASH --> MQTT
```

## 2. Detailed System Architecture

```mermaid
graph TB
    subgraph "Hardware Layer"
        DPS["DPS TXT Controller<br/>192.168.0.102<br/>CCU + Modul"]
        AIQS["AIQS TXT Controller<br/>192.168.0.103<br/>Qualitätskontrolle"]
        CGW["CGW TXT Controller<br/>192.168.0.104<br/>Cloud-Gateway"]
        FTS["FTS TXT Controller<br/>192.168.0.105<br/>Transport"]
        HBW["HBW Module<br/>SVR4H76449<br/>Lager"]
        MILL["MILL Module<br/>SVR3QA0022<br/>Fräsen"]
        DRILL["DRILL Module<br/>SVR3QA2098<br/>Bohren"]
    end
    
    subgraph "MQTT Broker"
        MQTT["Mosquitto Broker<br/>192.168.0.100:1883"]
    end
    
    subgraph "Processing Layer"
        NRPub["Node-RED(Pub)<br/>Monitoring"]
        NRSub["Node-RED(Sub)<br/>Commands"]
        NRPub2["Node-RED(Pub)<br/>Dashboard-Refresh"]
    end
    
    subgraph "Frontend Layer"
        DASH["APS-Dashboard<br/>mqttjs_17ecbee3<br/>Web-Interface"]
        MAC["MacBook User<br/>192.168.0.106<br/>Analysis"]
    end
    
    %% Hardware to MQTT
    DPS --> MQTT
    AIQS --> MQTT
    CGW --> MQTT
    FTS --> MQTT
    HBW --> MQTT
    MILL --> MQTT
    DRILL --> MQTT
    
    %% MQTT to Processing
    MQTT --> NRPub
    MQTT --> NRSub
    MQTT --> NRPub2
    
    %% Processing to MQTT
    NRSub --> MQTT
    
    %% MQTT to Frontend
    MQTT --> DASH
    MQTT --> MAC
    
    %% Frontend to MQTT
    DASH --> MQTT
```

## 3. High-Level Communication Flow

```mermaid
sequenceDiagram
    participant DPS as DPS (CCU)
    participant MQTT as MQTT Broker
    participant NODE as Node-RED
    participant MOD as Module
    participant DASH as Dashboard
    
    DPS->>MQTT: Sub ccu/state/*
    MQTT->>NODE: Pub ccu/state/*
    NODE->>NODE: Process State
    NODE->>MQTT: Sub module/+/instantAction
    MQTT->>MOD: Pub module/+/instantAction
    MOD->>MQTT: Sub module/+/state
    MQTT->>DASH: Pub module/+/state
```

## 4. Detailed Pub/Sub Communication Flow

```mermaid
sequenceDiagram
    participant DPS as DPS TXT (CCU)
    participant MQTT1 as MQTT Broker
    participant NRPub as Node-RED(Pub)
    participant MQTT2 as MQTT Broker
    participant NRSub as Node-RED(Sub)
    participant MQTT3 as MQTT Broker
    participant MOD as Module (HBW/MILL/DRILL)
    participant DASH as APS-Dashboard
    
    Note over DPS: CCU-Funktionalität
    DPS->>MQTT1: Sub ccu/state/layout
    DPS->>MQTT1: Sub ccu/pairing/state
    DPS->>MQTT1: Sub ccu/state/stock
    
    MQTT1->>NRPub: Pub ccu/state/*
    MQTT1->>NRPub: Pub module/v1/ff/+/state
    
    Note over NRPub: Monitoring & Processing
    NRPub->>NRPub: Process State Changes
    
    NRPub->>MQTT2: Sub processed data
    MQTT2->>NRSub: Pub processed data
    
    Note over NRSub: Command Generation
    NRSub->>MQTT3: Sub module/v1/ff/SVR4H76449/instantAction
    NRSub->>MQTT3: Sub module/v1/ff/SVR3QA0022/instantAction
    NRSub->>MQTT3: Sub module/v1/ff/SVR3QA2098/instantAction
    
    MQTT3->>MOD: Pub module/v1/ff/+/instantAction
    MOD->>MOD: Execute Command
    
    MOD->>MQTT3: Sub module/v1/ff/+/state
    MQTT3->>DASH: Pub module/v1/ff/+/state
    MQTT3->>DASH: Pub ccu/state/*
```

## 5. Node-RED Dual Role Architecture

```mermaid
graph LR
    subgraph "MQTT Broker 1"
        MQTT1["Mosquitto Broker<br/>192.168.0.100:1883"]
    end
    
    subgraph "Node-RED Pub Instance"
        NRPub["Node-RED(Pub)<br/>nodered_abe9e421b6fe3efd<br/>172.18.0.4"]
        NRPub_Pub["55 Subscriptions<br/>module/v1/ff/+/state<br/>ccu/state/*<br/>fts/v1/ff/+/state"]
    end
    
    subgraph "MQTT Broker 2"
        MQTT2["Mosquitto Broker<br/>192.168.0.100:1883"]
    end
    
    subgraph "Node-RED Sub Instance"
        NRSub["Node-RED(Sub)<br/>nodered_94dca81c69366ec4<br/>172.18.0.4"]
        NRSub_Sub["645 Publications<br/>module/v1/ff/+/instantAction<br/>3x NodeRed-Präfix"]
    end
    
    subgraph "MQTT Broker 3"
        MQTT3["Mosquitto Broker<br/>192.168.0.100:1883"]
    end
    
    subgraph "Hardware Modules"
        DPS["DPS TXT<br/>CCU Functions"]
        AIQS["AIQS TXT<br/>Quality Control"]
        HBW["HBW Module<br/>Storage"]
        MILL["MILL Module<br/>Milling"]
        DRILL["DRILL Module<br/>Drilling"]
    end
    
    %% Pub Flow
    DPS --> MQTT1
    AIQS --> MQTT1
    HBW --> MQTT1
    MILL --> MQTT1
    DRILL --> MQTT1
    
    MQTT1 --> NRPub_Pub
    NRPub_Pub --> NRPub
    
    %% Internal Processing
    NRPub --> NRSub
    
    %% Sub Flow
    NRSub --> NRSub_Sub
    NRSub_Sub --> MQTT2
    
    MQTT2 --> MQTT3
    MQTT3 --> DPS
    MQTT3 --> AIQS
    MQTT3 --> HBW
    MQTT3 --> MILL
    MQTT3 --> DRILL
```

## 6. Node-RED Dual Role Architecture

Das folgende Diagramm verdeutlicht die **duale Rolle von Node-RED** als Pub und Sub mit gerichtetem Graphen von links nach rechts:

```mermaid
graph LR
    subgraph "Hardware Layer"
        DPS["DPS TXT Controller<br/>192.168.0.102"]
        AIQS["AIQS TXT Controller<br/>192.168.0.103"]
        CGW["CGW TXT Controller<br/>192.168.0.104"]
        FTS["FTS TXT Controller<br/>192.168.0.105"]
        HBW["HBW Module<br/>SVR4H76449"]
        MILL["MILL Module<br/>SVR3QA0022"]
        DRILL["DRILL Module<br/>SVR3QA2098"]
    end
    
    subgraph "MQTT Broker 1"
        MQTT1["Mosquitto Broker<br/>192.168.0.100:1883"]
    end
    
    subgraph "Node-RED Processing"
        NRPub["Node-RED(Pub)<br/>Monitoring<br/>nodered_abe9e421b6fe3efd"]
        NRSub["Node-RED(Sub)<br/>Commands<br/>nodered_94dca81c69366ec4"]
    end
    
    subgraph "MQTT Broker 2"
        MQTT2["Mosquitto Broker<br/>192.168.0.100:1883"]
    end
    
    subgraph "Frontend Layer"
        DASH["APS-Dashboard<br/>mqttjs_17ecbee3"]
        MAC["MacBook User<br/>192.168.0.106"]
    end
    
    %% Hardware to MQTT1 (Pub Flow)
    DPS --> MQTT1
    AIQS --> MQTT1
    CGW --> MQTT1
    FTS --> MQTT1
    HBW --> MQTT1
    MILL --> MQTT1
    DRILL --> MQTT1
    
    %% MQTT1 to Node-RED(Pub) - Monitoring
    MQTT1 --> NRPub
    
    %% Node-RED Internal Processing
    NRPub --> NRSub
    
    %% Node-RED(Sub) to MQTT2 - Commands
    NRSub --> MQTT2
    
    %% MQTT2 to Hardware - Command Distribution
    MQTT2 --> DPS
    MQTT2 --> AIQS
    MQTT2 --> CGW
    MQTT2 --> FTS
    MQTT2 --> HBW
    MQTT2 --> MILL
    MQTT2 --> DRILL
    
    %% MQTT2 to Frontend - Status Updates
    MQTT2 --> DASH
    MQTT2 --> MAC
    
    %% Frontend to MQTT1 - User Commands
    DASH --> MQTT1
    MAC --> MQTT1
    
    %% Styling
    classDef hardware fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef mqtt fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef nodered fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef frontend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class DPS,AIQS,CGW,FTS,HBW,MILL,DRILL hardware
    class MQTT1,MQTT2 mqtt
    class NRPub,NRSub nodered
    class DASH,MAC frontend
```

## 7. Order Processing Flow

Das folgende Sequenzdiagramm zeigt den Ablauf der Bestellabwicklung im System basierend auf den gesicherten MQTT-Analyse-Erkenntnissen:

```mermaid
sequenceDiagram
    participant DASH as APS-Dashboard
    participant DPS as DPS TXT Controller (CCU)
    participant MQTT as MQTT Broker
    participant MODULE as Processing Module
    participant FTS as FTS System
    participant AIQS as AIQS Module (Quality)
    
    Note over DASH,AIQS: Order Processing Flow (Korrigiert)
    
    %% Order Initiation
    DASH->>MQTT: ccu/order/request (Bestellung-BLUE/WHITE/RED)
    MQTT->>DPS: Order Request
    DPS->>DPS: Generate orderId (CCU-Funktion)
    DPS->>MQTT: ccu/order/active (Order mit orderId)
    MQTT->>MODULE: Order Message
    
    Note over MODULE: Order Handling Function
    MODULE->>MODULE: Store orderId & orderUpdateId
    MODULE->>MQTT: module/v1/ff/+/state (PICKBUSY)
    MQTT->>DPS: Status Update
    MQTT->>DASH: Status Update
    
    Note over MODULE: PICK Operation
    MODULE->>MODULE: PICK Command (OPC-UA)
    MODULE->>MODULE: PICK Status Update
    MODULE->>MQTT: module/v1/ff/+/state (PROCESSING)
    MQTT->>DPS: Status Update
    MQTT->>DASH: Status Update
    
    Note over MODULE: PROCESSING Operation
    MODULE->>MODULE: PROCESS Command (OPC-UA)
    MODULE->>MODULE: PROCESS Status Update
    MODULE->>MQTT: module/v1/ff/+/state (DROPBUSY)
    MQTT->>DPS: Status Update
    MQTT->>DASH: Status Update
    
    Note over MODULE: DROP Operation
    MODULE->>MODULE: DROP Command (OPC-UA)
    MODULE->>MODULE: DROP Status Update
    MODULE->>MQTT: module/v1/ff/+/state (IDLE)
    MQTT->>DPS: Status Update
    MQTT->>DASH: Status Update
    
    Note over AIQS: Quality Control (für WHITE Orders)
    AIQS->>AIQS: AI-Bilderkennung
    alt Quality OK
        AIQS->>MQTT: module/v1/ff/SVR4H76530/state (QUALITY_OK)
        MQTT->>DPS: Quality Status
        MQTT->>DASH: Quality Status
    else Quality Not OK
        AIQS->>MQTT: module/v1/ff/SVR4H76530/state (QUALITY_NOT_OK)
        MQTT->>DPS: Quality Status
        MQTT->>DASH: Quality Status
        DPS->>DPS: Generate new Order (wenn Rohware verfügbar)
    end
    
    Note over FTS: Transport System
    FTS->>MQTT: fts/v1/ff/5iO4/state (READY/BLOCKED)
    MQTT->>DPS: FTS Status
    MQTT->>DASH: FTS Status
```

## 8. High-Level Topic Flow

```mermaid
graph LR
    subgraph "CCU (DPS)"
        CCU["CCU Topics<br/>Layout, Config, Stock"]
    end
    
    subgraph "Modules"
        MOD["Module Topics<br/>State, Actions"]
    end
    
    subgraph "FTS"
        FTS_TOPICS["FTS Topics<br/>Transport, Status"]
    end
    
    CCU --> MOD
    MOD --> FTS_TOPICS
    FTS_TOPICS --> MOD
```

## 9. Topic Flow Patterns

```mermaid
graph TD
    subgraph "CCU Topics (DPS as Central Controller)"
        CCU_LAYOUT[ccu/state/layout]
        CCU_PAIRING[ccu/pairing/state]
        CCU_STOCK[ccu/state/stock]
        CCU_ORDER[ccu/order/request]
    end
    
    subgraph "Module Topics"
        MOD_STATE[module/v1/ff/+/state]
        MOD_CONN[module/v1/ff/+/connection]
        MOD_ACTION[module/v1/ff/+/instantAction]
        MOD_FACT[module/v1/ff/+/factsheet]
    end
    
    subgraph "NodeRed Topics (DPS & AIQS only)"
        NR_STATE[module/v1/ff/NodeRed/+/state]
        NR_ACTION[module/v1/ff/NodeRed/+/instantAction]
        NR_FACT[module/v1/ff/NodeRed/+/factsheet]
    end
    
    subgraph "FTS Topics"
        FTS_STATE[fts/v1/ff/5iO4/state]
        FTS_CONN[fts/v1/ff/5iO4/connection]
        FTS_ACTION[fts/v1/ff/5iO4/instantAction]
    end
    
    subgraph "TXT Topics"
        TXT_ORDER["j1/txt/1/f/i/order"]
        TXT_STOCK["j1/txt/1/f/i/stock"]
    end
    
    %% Flow connections
    CCU_LAYOUT --> MOD_STATE
    CCU_PAIRING --> MOD_CONN
    CCU_STOCK --> MOD_STATE
    CCU_ORDER --> MOD_ACTION
    
    MOD_STATE --> NR_STATE
    MOD_ACTION --> NR_ACTION
    MOD_FACT --> NR_FACT
    
    FTS_STATE --> MOD_STATE
    TXT_ORDER --> CCU_ORDER
    TXT_STOCK --> CCU_STOCK
```

## 10. High-Level Load Type Flow

```mermaid
graph LR
    subgraph "Load Types"
        L1["WHITE"]
        L2["RED"]
        L3["BLUE"]
    end
    
    subgraph "Universal Support"
        ALL["All Modules<br/>Support All Types"]
    end
    
    subgraph "Production Flows"
        F1["WHITE: DRILL → AIQS"]
        F2["RED: MILL → AIQS"]
        F3["BLUE: DRILL → MILL → AIQS"]
    end
    
    L1 --> ALL
    L2 --> ALL
    L3 --> ALL
    
    ALL --> F1
    ALL --> F2
    ALL --> F3
```

## 11. Load Type Processing Flow

```mermaid
graph LR
    subgraph "Load Types"
        WHITE["WHITE Workpieces"]
        RED["RED Workpieces"]
        BLUE["BLUE Workpieces"]
    end
    
    subgraph "Universal Module Support"
        DPS_SUP["DPS Module<br/>SVR4H73275<br/>All Load Types"]
        AIQS_SUP["AIQS Module<br/>SVR4H76530<br/>All Load Types"]
        HBW_SUP["HBW Module<br/>SVR4H76449<br/>All Load Types"]
        MILL_SUP["MILL Module<br/>SVR3QA0022<br/>All Load Types"]
        DRILL_SUP["DRILL Module<br/>SVR3QA2098<br/>All Load Types"]
    end
    
    subgraph "Production Flows"
        FLOW_WHITE["WHITE Flow<br/>DRILL → AIQS"]
        FLOW_RED["RED Flow<br/>MILL → AIQS"]
        FLOW_BLUE["BLUE Flow<br/>DRILL → MILL → AIQS"]
    end
    
    WHITE --> DPS_SUP
    RED --> DPS_SUP
    BLUE --> DPS_SUP
    
    WHITE --> AIQS_SUP
    RED --> AIQS_SUP
    BLUE --> AIQS_SUP
    
    WHITE --> HBW_SUP
    RED --> HBW_SUP
    BLUE --> HBW_SUP
    
    WHITE --> MILL_SUP
    RED --> MILL_SUP
    BLUE --> MILL_SUP
    
    WHITE --> DRILL_SUP
    RED --> DRILL_SUP
    BLUE --> DRILL_SUP
    
    DPS_SUP --> FLOW_WHITE
    DPS_SUP --> FLOW_RED
    DPS_SUP --> FLOW_BLUE
```

## 12. High-Level Camera System

```mermaid
graph LR
    subgraph "DPS Camera"
        DPS_CAM["Überwachungskamera<br/>Gesamte APS-Fabrik"]
    end
    
    subgraph "AIQS Camera"
        AIQS_CAM["Produktkamera<br/>Qualitätskontrolle"]
    end
    
    subgraph "AI Processing"
        AI["AI-Bilderkennung<br/>Qualitäts-Entscheidung"]
    end
    
    DPS_CAM --> AIQS_CAM
    AIQS_CAM --> AI
```

## 13. Camera System Architecture

```mermaid
graph TB
    subgraph "DPS Camera System"
        DPS_CAM["DPS Camera<br/>192.168.0.102"]
        DPS_TXT["DPS TXT Controller<br/>Kamera-Steuerung"]
        DPS_TOPIC["module/v1/ff/SVR4H73275/instantAction<br/>Kamera-Justierung"]
    end
    
    subgraph "AIQS Camera System"
        AIQS_CAM["AIQS Camera<br/>192.168.0.103"]
        AIQS_TXT["AIQS TXT Controller<br/>Produktkamera"]
        AIQS_TOPIC["module/v1/ff/SVR4H76530/instantAction<br/>Qualitätskontrolle"]
    end
    
    subgraph "AI Processing"
        AI_IMG["AI-Bilderkennung<br/>Produktqualität"]
        AI_DECISION{"Qualitäts-Entscheidung"}
        AI_OK["Produktion OK<br/>Weiter im Prozess"]
        AI_NOK["Produktion NOK<br/>Aussortierung + Neuer Auftrag"]
    end
    
    subgraph "MQTT Topics"
        MQTT_CAM["module/v1/ff/+/instantAction<br/>Kamera-Befehle"]
    end
    
    %% DPS Camera Flow
    DPS_TOPIC --> MQTT_CAM
    MQTT_CAM --> DPS_TXT
    DPS_TXT --> DPS_CAM
    
    %% AIQS Camera Flow
    AIQS_TOPIC --> MQTT_CAM
    MQTT_CAM --> AIQS_TXT
    AIQS_TXT --> AIQS_CAM
    AIQS_CAM --> AI_IMG
    AI_IMG --> AI_DECISION
    AI_DECISION --> AI_OK
    AI_DECISION --> AI_NOK
```

## 14. High-Level FTS States

```mermaid
stateDiagram-v2
    [*] --> READY
    READY --> BUSY : Order
    BUSY --> CHARGING : Low Battery
    CHARGING --> BLOCKED : At Station
    BLOCKED --> READY : Charged
    BUSY --> READY : Complete
```

## 15. FTS State Management

```mermaid
stateDiagram-v2
    [*] --> READY : System Start
    
    READY --> BUSY : Order Received
    BUSY --> CHARGING : Battery Low
    CHARGING --> BLOCKED : At CHRG0 Station
    BLOCKED --> READY : Charging Complete
    
    READY --> READY : No Orders
    BUSY --> READY : Order Complete
    
    state READY {
        [*] --> Available
        Available --> Processing : New Order
    }
    
    state BUSY {
        [*] --> Transporting
        Transporting --> Loading : At Module
        Loading --> Unloading : Process Complete
    }
    
    state CHARGING {
        [*] --> MovingToStation
        MovingToStation --> AtStation : Arrived
    }
    
    state BLOCKED {
        [*] --> Charging
        Charging --> ReadyToLeave : Battery Full
    }
```

---

*Erstellt: 18. September 2025*  
*Basiert auf: Mosquitto-Log-Analyse (15:59-16:24)*  
*Status: Vollständige Pub/Sub-Diagramme erstellt*
