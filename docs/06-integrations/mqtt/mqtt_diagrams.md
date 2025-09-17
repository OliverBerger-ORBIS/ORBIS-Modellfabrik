# MQTT Diagrams

⚠️ **WARNUNG**: Diese Dokumentation wurde automatisch erstellt und enthält fehlerbehaftete Angaben. Die Diagramme zur Node-RED und Order-Processing gehören nicht zur MQTT-Dokumentation und sind an anderer Stelle zu beschreiben.

Diese Dokumentation enthält alle wichtigen Mermaid-Diagramme für das MQTT-System der ORBIS Modellfabrik. Die Diagramme zeigen die Architektur, Datenflüsse, Topic-Struktur und Zustandsübergänge des Systems.

## Übersicht der Diagramme

1. **MQTT Flow Diagram** - Systemarchitektur und Datenflüsse
2. **Topic Hierarchy** - MQTT-Topic-Struktur und -Organisation  
3. **Complete Data Flow Diagram** - Sender/Receiver-Pattern
4. **Order Processing Flow** - Sequenzdiagramm für Bestellabwicklung
5. **Node-RED Architecture** - Node-RED Flows und Modul-Architektur
6. **Module State Machine** - Zustandsübergänge der Verarbeitungsmodule

## MQTT Flow Diagram

```mermaid
graph TB
    subgraph "Hardware Layer"
        FTS["FTS Hardware<br/>192.168.0.105<br/>auto-84E1E526..."]
        TXT["TXT Controller<br/>192.168.0.102<br/>auto-B5711E2C..."]
    end
    
    subgraph "MQTT Broker"
        MQTT["Mosquitto<br/>192.168.0.100:1883<br/>Port 9001 (WebSocket)"]
    end
    
    subgraph "Processing Layer"
        NODERED["Node-RED (CCU)<br/>172.18.0.3<br/>nodered_686f9b8f3f8dbcc7"]
    end
    
    subgraph "Dashboard Layer"
        OMF["OMF Dashboard<br/>192.168.0.103<br/>omf_dashboard_live"]
        WEB["Web Dashboard<br/>172.18.0.5<br/>mqttjs_1802b4e7"]
    end
    
    %% Hardware to MQTT
    FTS -->|"fts/v1/ff/5iO4/state<br/>fts/v1/ff/5iO4/connection"| MQTT
    TXT -->|"/j1/txt/1/i/*<br/>/j1/txt/1/f/o/order"| MQTT
    
    %% MQTT to Node-RED
    MQTT -->|"fts/v1/ff/+/state<br/>ccu/order/request<br/>/j1/txt/1/f/o/order"| NODERED
    
    %% Node-RED to MQTT
    NODERED -->|"module/v1/ff/+/connection<br/>module/v1/ff/+/state<br/>ccu/order/active"| MQTT
    
    %% MQTT to Dashboards
    MQTT -->|"module/v1/ff/+/connection<br/>ccu/order/active"| OMF
    MQTT -->|"module/v1/ff/+/connection<br/>ccu/order/active"| WEB
    
    %% Dashboard to MQTT
    OMF -->|"ccu/order/request"| MQTT
    
    %% Styling
    classDef hardware fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef broker fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef processing fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef dashboard fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class FTS,TXT hardware
    class MQTT broker
    class NODERED processing
    class OMF,WEB dashboard
```

## Topic Hierarchy

```mermaid
graph TD
    subgraph "MQTT Topic Hierarchy"
        ROOT["MQTT Root"]
        
        subgraph "Module Topics"
            MOD["module/v1/ff/"]
            MOD --> SVR3["SVR3QA0022/"]
            MOD --> SVR4A["SVR4H73275/"]
            MOD --> SVR4B["SVR4H76530/"]
            
            SVR3 --> CONN1["connection"]
            SVR4A --> CONN2["connection"]
            SVR4A --> INST["instantAction"]
            SVR4B --> CONN3["connection"]
        end
        
        subgraph "CCU Topics"
            CCU["ccu/"]
            CCU --> ORDER["order/"]
            CCU --> STATE["state/"]
            CCU --> PAIR["pairing/"]
            
            ORDER --> REQ["request"]
            ORDER --> ACT["active"]
            STATE --> VERSION["version-mismatch"]
            PAIR --> PAIRSTATE["state"]
        end
        
        subgraph "FTS Topics"
            FTS["fts/v1/ff/"]
            FTS --> FTS5["5iO4/"]
            FTS5 --> FTSSTATE["state"]
            FTS5 --> FTSCONN["connection"]
        end
        
        subgraph "TXT Topics"
            TXT["/j1/txt/1/"]
            TXT --> INPUT["i/"]
            TXT --> OUTPUT["f/o/"]
            
            INPUT --> BME["bme680"]
            INPUT --> CAM["cam"]
            INPUT --> LDR["ldr"]
            OUTPUT --> ORDEROUT["order"]
        end
        
        ROOT --> MOD
        ROOT --> CCU
        ROOT --> FTS
        ROOT --> TXT
    end
    
    %% Styling
    classDef root fill:#ffebee,stroke:#c62828,stroke-width:3px
    classDef module fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef ccu fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef fts fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef txt fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class ROOT root
    class MOD,SVR3,SVR4A,SVR4B,CONN1,CONN2,CONN3,INST module
    class CCU,ORDER,STATE,PAIR,REQ,ACT,VERSION,PAIRSTATE ccu
    class FTS,FTS5,FTSSTATE,FTSCONN fts
    class TXT,INPUT,OUTPUT,BME,CAM,LDR,ORDEROUT txt
```

## Complete Data Flow Diagram

Das folgende Diagramm zeigt das Sender/Receiver-Pattern und die vollständigen Datenflüsse im MQTT-System:

```mermaid
graph LR
    subgraph "SENDER"
        TXT["TXT-Controller<br/>192.168.0.102<br/>auto-84E1E526..."]
        CCU["Node-RED (CCU)<br/>172.18.0.3<br/>nodered_686f9b8f3f8dbcc7"]
        OMF["OMF Dashboard<br/>192.168.0.103<br/>omf_dashboard_live"]
        MQTTJS["MQTT.js Dashboard<br/>172.18.0.5<br/>mqttjs_1802b4e7"]
    end
    
    subgraph "MQTT BROKER"
        BROKER["MQTT Broker<br/>192.168.0.100:1883<br/>Mosquitto"]
    end
    
    subgraph "RECEIVER"
        LOGGER["Logger/Recorder<br/>192.168.0.101<br/>auto-B5711E2C..."]
        OMF_RECV["OMF Dashboard<br/>192.168.0.103<br/>omf_dashboard_live"]
        MQTTJS_RECV["MQTT.js Dashboard<br/>172.18.0.5<br/>mqttjs_1802b4e7"]
        CCU_RECV["Node-RED (CCU)<br/>172.18.0.3<br/>nodered_686f9b8f3f8dbcc7"]
    end
    
    %% Sender to Broker
    TXT -->|"/j1/txt/1/i/cam<br/>/j1/txt/1/i/bme680<br/>/j1/txt/1/i/ldr"| BROKER
    CCU -->|"module/v1/ff/*/connection<br/>(Module Status)"| BROKER
    OMF -->|"ccu/order/request<br/>(2x Messages)"| BROKER
    MQTTJS -->|"ccu/order/request<br/>ccu/pairing/state<br/>module/v1/ff/*/instantAction"| BROKER
    
    %% Broker to Receiver
    BROKER -->|"ALLE Topics<br/>(Vollständige Aufzeichnung)"| LOGGER
    BROKER -->|"ccu/order/request<br/>ccu/pairing/state<br/>module/v1/ff/*/connection<br/>/j1/txt/1/i/cam"| OMF_RECV
    BROKER -->|"module/v1/ff/*/connection<br/>ccu/order/request"| MQTTJS_RECV
    BROKER -->|"module/v1/ff/*/instantAction"| CCU_RECV
    
    %% Styling
    classDef sender fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef broker fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef receiver fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class TXT,CCU,OMF,MQTTJS sender
    class BROKER broker
    class LOGGER,OMF_RECV,MQTTJS_RECV,CCU_RECV receiver
```

## Order Processing Flow

Das folgende Sequenzdiagramm zeigt den Ablauf der Bestellabwicklung im System:

```mermaid
sequenceDiagram
    participant TXT as TXT Controller
    participant CCU as Central Control Unit
    participant MQTT as MQTT Broker
    participant MODULE as Processing Module
    participant OPCUA as OPC-UA Server
    participant FTS as FTS System
    
    Note over TXT,FTS: Order Processing Flow
    
    TXT->>CCU: Order Request (without orderId)
    CCU->>FTS: Forward Order
    FTS->>FTS: Generate orderId
    FTS->>CCU: Order with orderId
    CCU->>MQTT: Publish Order
    MQTT->>MODULE: Order Message
    
    Note over MODULE: Order Handling Function
    MODULE->>MODULE: Store orderId & orderUpdateId
    MODULE->>MODULE: Set moduleState = PICKBUSY
    
    Note over MODULE: PICK Operation
    MODULE->>OPCUA: Write PICK Command
    OPCUA->>MODULE: PICK Status Update
    MODULE->>MODULE: Set moduleState = PROCESSING
    
    Note over MODULE: PROCESSING Operation
    MODULE->>OPCUA: Write PROCESS Command
    OPCUA->>MODULE: PROCESS Status Update
    MODULE->>MODULE: Set moduleState = DROPBUSY
    
    Note over MODULE: DROP Operation
    MODULE->>OPCUA: Write DROP Command
    OPCUA->>MODULE: DROP Status Update
    MODULE->>MODULE: Set moduleState = IDLE
    
    Note over MODULE: Status Publishing
    MODULE->>MQTT: Publish VDA Status
    MQTT->>CCU: Status Update
    MQTT->>TXT: Status Update
```

## Node-RED Architecture

Das folgende Diagramm zeigt die Node-RED Architektur mit allen 25 Tabs und Modulen:

```mermaid
graph TB
    subgraph "Node-RED Flows (25 Tabs)"
        subgraph "Processing Modules"
            MILL1[MILL #1<br/>192.168.0.40]
            MILL2[MILL #2<br/>192.168.0.41]
            MILL3[MILL #3<br/>192.168.0.42]
            MILL4[MILL #4<br/>192.168.0.43]
            MILL5[MILL #5<br/>192.168.0.44]
            
            DRILL1[DRILL #1<br/>192.168.0.50]
            DRILL2[DRILL #2<br/>192.168.0.51]
            DRILL3[DRILL #3<br/>192.168.0.52]
            DRILL4[DRILL #4<br/>192.168.0.53]
            DRILL5[DRILL #5<br/>192.168.0.54]
            
            OVEN1[OVEN #1<br/>192.168.0.60]
            OVEN2[OVEN #2<br/>192.168.0.61]
            OVEN3[OVEN #3<br/>192.168.0.62]
            OVEN4[OVEN #4<br/>192.168.0.63]
            OVEN5[OVEN #5<br/>192.168.0.64]
        end
        
        subgraph "Quality & Storage"
            AIQS1[AIQS #1<br/>192.168.0.70]
            AIQS2[AIQS #2<br/>192.168.0.71]
            AIQS3[AIQS #3<br/>192.168.0.72]
            AIQS4[AIQS #4<br/>192.168.0.73]
            AIQS5[AIQS #5<br/>192.168.0.74]
            
            HBW1[HBW #1<br/>192.168.0.80]
            HBW2[HBW #2<br/>192.168.0.81]
            HBW3[HBW #3<br/>192.168.0.82]
        end
        
        subgraph "Distribution"
            DPS[DPS<br/>192.168.0.90]
        end
        
        subgraph "Control"
            INIT[NodeRed Init<br/>Global Control]
        end
    end
    
    subgraph "OPC-UA Servers"
        MILL_OPC[MILL OPC-UA<br/>Port 4840]
        DRILL_OPC[DRILL OPC-UA<br/>Port 4840]
        OVEN_OPC[OVEN OPC-UA<br/>Port 4840]
        AIQS_OPC[AIQS OPC-UA<br/>Port 4840]
        HBW_OPC[HBW OPC-UA<br/>Port 4840]
        DPS_OPC[DPS OPC-UA<br/>Port 4840]
    end
    
    subgraph "MQTT Broker"
        MQTT[Local MQTT<br/>Port 1883/9001]
    end
    
    subgraph "External Systems"
        TXT[TXT Controllers]
        CCU[Central Control Unit]
        FRONTEND[Frontend<br/>Port 80]
    end
    
    %% OPC-UA Connections
    MILL1 -.-> MILL_OPC
    MILL2 -.-> MILL_OPC
    MILL3 -.-> MILL_OPC
    MILL4 -.-> MILL_OPC
    MILL5 -.-> MILL_OPC
    
    DRILL1 -.-> DRILL_OPC
    DRILL2 -.-> DRILL_OPC
    DRILL3 -.-> DRILL_OPC
    DRILL4 -.-> DRILL_OPC
    DRILL5 -.-> DRILL_OPC
    
    OVEN1 -.-> OVEN_OPC
    OVEN2 -.-> OVEN_OPC
    OVEN3 -.-> OVEN_OPC
    OVEN4 -.-> OVEN_OPC
    OVEN5 -.-> OVEN_OPC
    
    AIQS1 -.-> AIQS_OPC
    AIQS2 -.-> AIQS_OPC
    AIQS3 -.-> AIQS_OPC
    AIQS4 -.-> AIQS_OPC
    AIQS5 -.-> AIQS_OPC
    
    HBW1 -.-> HBW_OPC
    HBW2 -.-> HBW_OPC
    HBW3 -.-> HBW_OPC
    
    DPS -.-> DPS_OPC
    
    %% MQTT Connections
    MILL1 --> MQTT
    DRILL1 --> MQTT
    OVEN1 --> MQTT
    AIQS1 --> MQTT
    HBW1 --> MQTT
    DPS --> MQTT
    INIT --> MQTT
    
    %% External Connections
    TXT --> MQTT
    CCU --> MQTT
    FRONTEND --> MQTT
    
    %% Styling
    classDef processing fill:#e1f5fe
    classDef quality fill:#f3e5f5
    classDef storage fill:#e8f5e8
    classDef distribution fill:#fff3e0
    classDef control fill:#ffebee
    
    class MILL1,MILL2,MILL3,MILL4,MILL5,DRILL1,DRILL2,DRILL3,DRILL4,DRILL5,OVEN1,OVEN2,OVEN3,OVEN4,OVEN5 processing
    class AIQS1,AIQS2,AIQS3,AIQS4,AIQS5 quality
    class HBW1,HBW2,HBW3 storage
    class DPS distribution
    class INIT control
```

## Module State Machine

Das folgende State-Diagramm zeigt die Zustandsübergänge der Verarbeitungsmodule:

```mermaid
stateDiagram-v2
    [*] --> IDLE : Module Start
    
    IDLE --> PICKBUSY : Order Received
    PICKBUSY --> PROCESSING : Pick Completed
    PROCESSING --> DROPBUSY : Processing Completed
    DROPBUSY --> IDLE : Drop Completed
    
    IDLE --> ERROR : Error Occurred
    PICKBUSY --> ERROR : Pick Failed
    PROCESSING --> ERROR : Processing Failed
    DROPBUSY --> ERROR : Drop Failed
    ERROR --> IDLE : Error Cleared
    
    note right of IDLE
        Module ready for new order
        State: IDLE
    end note
    
    note right of PICKBUSY
        Picking workpiece from input
        State: PICKBUSY
    end note
    
    note right of PROCESSING
        Processing workpiece
        (MILL/DRILL/OVEN specific)
        State: PROCESSING
    end note
    
    note right of DROPBUSY
        Dropping workpiece to output
        State: DROPBUSY
    end note
```

