# System Context - OMF Architecture

## 🏗️ System-Kontextdiagramm

> **🔗 Integration Details:**
> - **[APS Overview](../../06-integrations/aps/README.md)** - Fischertechnik Agile Production Simulation
> - **[Node-RED Integration](../../06-integrations/node-red/README.md)** - Gateway zwischen OPC-UA und MQTT
> - **[FTS VDA 5050](../../06-integrations/fts/README.md)** - Fahrerloses Transportsystem


### Mermaid-Diagramm (Modern)
```mermaid
graph TB
    subgraph "APS Ecosystem"
        subgraph "Control Layer"
            APS_CCU[APS-CCU<br/>Central Control Unit]
        end
        
        subgraph "Communication Layer"
            MQTT[MQTT Broker<br/>Message Routing]
            APS_NODERED[APS-NodeRED<br/>Protocol Translator]
        end
        
        subgraph "Module Layer"
            HBW[HBW<br/>High Bay Warehouse]
            DRILL[DRILL<br/>Drilling Station]
            MILL[MILL<br/>Milling Station]
            AIQS[AIQS<br/>Quality Control]
            DPS[DPS<br/>Distribution Station]
        end
        
        subgraph "TXT-Control Layer"
            FTS_TXT[FTS-TXT<br/>Transport Control]
            AIQS_TXT[AIQS-TXT<br/>Quality Control]
            DPS_TXT[DPS-TXT<br/>Distribution Control]
        end
    end
    
    APS_CCU <-->|MQTT Commands| MQTT
    
    MQTT <-->|Message Routing| APS_NODERED
    APS_NODERED <-->|OPC-UA| HBW
    APS_NODERED <-->|OPC-UA| DRILL
    APS_NODERED <-->|OPC-UA| MILL
    APS_NODERED <-->|OPC-UA| AIQS
    APS_NODERED <-->|OPC-UA| DPS
    
    FTS_TXT <-->|MQTT Transport| MQTT
    AIQS_TXT <-->|MQTT Sensor Data| MQTT
    DPS_TXT <-->|MQTT Control| MQTT
    
    MQTT -->|Module State| APS_CCU
    
    classDef aps fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    classDef aps_highlight fill:#ffecb3,stroke:#f57f17,stroke-width:3px
    classDef external fill:#f5f5f5,stroke:#757575,stroke-width:2px
    class APS_CCU,APS_NODERED aps_highlight
    class MQTT external
    class HBW,DRILL,MILL,AIQS,DPS,FTS_TXT,AIQS_TXT,DPS_TXT aps
```

## 🔄 Message-Flow-Übersicht

### 1. Order-Flow (Outbound)
```
APS-CCU → MQTT Order → APS-NodeRED → OPC-UA → Module
```

**Beispiel: DRILL-Befehl**
- **Topic:** `module/v1/ff/SVR4H76449/order`
- **Payload:** `{"command": "DRILL", "type": "WHITE", "orderId": "123"}`
- **APS-NodeRED:** Übersetzt zu OPC-UA-Call
- **Module:** Führt DRILL-Aktion aus

### 2. State-Flow (Inbound)
```
Module → OPC-UA → APS-NodeRED → MQTT State → APS-CCU
```

**Beispiel: DRILL-Status**
- **Topic:** `module/v1/ff/SVR4H76449/state`
- **Payload:** `{"actionState": {"command": "DRILL", "state": "RUNNING"}}`
- **APS-CCU:** Zeigt Status-Update an

### 3. HBW-Spezialfall
```
HBW → OPC-UA → APS-NodeRED → MQTT State (Full) → APS-CCU
HBW → OPC-UA → APS-NodeRED → MQTT State (Delta) → APS-CCU
```

**Erster State:** Vollständige Inventory-Liste
**Folgende States:** Nur Änderungen (Deltas)

## 🏭 Komponenten-Details

### APS-CCU (Central Control Unit)
- **Rolle:** Zentrale Steuerung und Orchestrierung
- **Plattform:** Raspberry Pi mit Docker-Container
- **MQTT-Topics:** `ccu/order/request`, `ccu/state/*`
- **Verantwortlich:** Workflow-Management, Order-Erstellung
- **UI:** Die Logik der APS-CCU wird über das APS-Dashboard als Benutzer-Interface zur Verfügung gestellt

### APS-NodeRED
- **Rolle:** MQTT ↔ OPC-UA Vermittler
- **Verantwortlich:** 
  - MQTT-Befehle zu OPC-UA-Calls übersetzen
  - OPC-UA-Daten zu MQTT-Status aggregieren
  - Modul-spezifische State-Machine implementieren

### MQTT-Broker
- **Rolle:** Zentrale Message-Routing-Infrastruktur
- **Plattform:** Docker-Container auf Raspberry Pi (gemeinsam mit APS-CCU)
- **Verantwortlich:** Message-Routing zwischen allen APS-Komponenten

### Module (HBW, DRILL, MILL, AIQS, DPS)
- **Rolle:** Physische Produktionsmodule
- **OPC-UA:** Direkte Hardware-Steuerung
- **MQTT:** Status-Updates über APS-NodeRED

### FTS (Fahrerlose Transportsysteme)
- **Rolle:** Material-Transport zwischen Modulen
- **MQTT-Topics:** `fts/v1/ff/5iO4/*`
- **Verantwortlich:** Workpiece-Transport, Navigation

### TXT-Controller (FTS-TXT, AIQS-TXT, DPS-TXT)
- **Rolle:** Fischertechnik-Controller für spezifische Module
- **Verantwortlich:**
  - FTS-TXT: Transport-Steuerung
  - AIQS-TXT: Quality Control
  - DPS-TXT: Distribution Control
  - Sensor-Daten und einfache Steuerung

## 🔗 Kommunikations-Patterns

### MQTT-Topic-Struktur
```
module/v1/ff/{serial_number}/{type}
ccu/{type}/{subtype}
fts/v1/ff/{serial_number}/{type}
/j1/txt/1/f/i/{type}
```

### Message-Directions
- **Outbound:** APS-Dashboard → Module (Orders, Commands)
- **Inbound:** Module → APS-Dashboard (States, Status)
- **Bidirectional:** Connection-Status, Heartbeats

### Registry-Integration
- **Templates:** Definieren Nachrichtenstrukturen
- **Mappings:** Verbinden Topics mit Templates
- **Validierung:** Registry-basierte Message-Validierung

---

**"Alle Steuerung läuft über MQTT, Node-RED ist der intelligente Vermittler zur Hardware."**
