# APS Data Flow Architecture

## 📋 Architektur-Phasen

### Phase 1: Ausgangssituation (Fischertechnik Standard)
- **Fischertechnik Cloud** als zentrale Datenquelle
- **Fischertechnik Dashboard** für lokale Visualisierung
- **Keine ORBIS-Integration**

### Phase 2: ORBIS-Integration (Aktuell)
- **OMF Dashboard** für erweiterte Steuerung
- **Session Manager** für Replay/Recording
- **Registry v1** für Template-Management
- **DPS-Modul** hinzugefügt

---

## 📊 Datenfluss-Diagramm (Phase 2: ORBIS-Integration)

```mermaid
flowchart TD
    subgraph "Data Sources"
        CAM[Camera Images<br/>Base64 JPEG]
        SENS[Sensor Data<br/>Quality Checks]
        STATE[Module States<br/>Connection Status]
    end
    
    subgraph "Data Processing"
        CG[Cloud Gateway<br/>~192.168.0.101<br/>Data Aggregation]
        NR[Node-RED<br/>192.168.0.100<br/>Flow Processing]
        MQTT[MQTT Broker<br/>192.168.0.100<br/>Message Routing]
    end
    
    subgraph "Data Storage"
        CLOUD[Fischertechnik Cloud<br/>Dashboard Data]
        LOCAL[Local Logs<br/>Session Data]
    end
    
    subgraph "Data Consumers"
        FT_DASH[Fischertechnik Dashboard<br/>192.168.0.100<br/>Angular PWA]
        OMF_DASH[OMF Dashboard<br/>Streamlit App]
        SESSION[Session Manager<br/>Replay/Recording]
        API[REST API<br/>External Systems]
    end
    
    CAM -->|HTTPS| CG
    SENS -->|OPC-UA| CG
    STATE -->|MQTT| CG
    
    CG -->|Process| NR
    NR -->|Route| MQTT
    MQTT -->|Publish| CLOUD
    MQTT -->|Store| LOCAL
    
    CLOUD -->|Display| FT_DASH
    CLOUD -->|API| API
    LOCAL -->|Analyze| SESSION
    MQTT -->|Real-time| OMF_DASH
    MQTT -->|Record| SESSION
    
    FT_DASH -->|User Interaction| CG
    OMF_DASH -->|Registry Commands| MQTT
    SESSION -->|Replay| MQTT
    API -->|External Commands| CG
    
    classDef fischertechnik fill:#f5f5f5,stroke:#757575,stroke-width:2px
    classDef orbis fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef modules fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    class FT_DASH,API fischertechnik
    class OMF_DASH,SESSION orbis
    class CAM,SENS,STATE,CG,NR,MQTT,CLOUD,LOCAL modules
```

## 🔄 Kommunikations-Protokoll-Diagramm

```mermaid
sequenceDiagram
    participant FTC as Fischertechnik Cloud
    participant CG as Cloud Gateway
    participant MQTT as MQTT Broker
    participant DPS as DPS Module
    participant AIQS as AIQS Module
    participant FTS as FTS Module
    
    Note over FTC,FTS: VDA5050 Standard Communication
    
    FTC->>CG: HTTPS/REST API<br/>Camera Images (Base64)
    CG->>MQTT: Publish Commands<br/>QoS=1, Retain=False
    
    MQTT->>DPS: module/v1/ff/DPS/state
    MQTT->>AIQS: module/v1/ff/AIQS/state
    MQTT->>FTS: fts/v1/ff/FTS/state
    
    DPS->>MQTT: State Updates<br/>QoS=0, Retain=False
    AIQS->>MQTT: Quality Check Results<br/>QoS=0, Retain=False
    FTS->>MQTT: Transport Status<br/>QoS=0, Retain=False
    
    MQTT->>CG: Telemetry Data
    CG->>FTC: Forward to Cloud
    
    Note over AIQS: OPC-UA Communication
    AIQS->>AIQS: Internal OPC-UA<br/>Quality Processing
```

## 🏗️ System-Komponenten-Diagramm

```mermaid
graph TB
    subgraph "Cloud Layer"
        FTC[Fischertechnik Cloud<br/>fischertechnik-cloud.com<br/>Angular PWA]
        API[Cloud API<br/>REST/HTTPS]
    end
    
    subgraph "Gateway Layer"
        CG[Cloud Gateway<br/>~192.168.0.101<br/>TXT 4.0 Controller]
        NR[Node-RED<br/>192.168.0.100<br/>Docker Container]
        MQTT[MQTT Broker<br/>192.168.0.100<br/>Port 1883]
    end
    
    subgraph "Module Layer"
        DPS[DPS Module<br/>TXT 4.0]
        FTS[FTS Module<br/>TXT 4.0]
        AIQS[AIQS Modules<br/>SPS S7-1200]
    end
    
    subgraph "Network Layer"
        WLAN[WLAN Access Point<br/>Unverschlüsselt]
        LAN[LAN Switch<br/>Statische IPs]
    end
    
    subgraph "Data Layer"
        LOGS[Session Logs<br/>SQLite + JSON]
        CACHE[Cloud Cache<br/>Service Worker]
    end
    
    FTC -->|HTTPS| API
    API -->|REST| CG
    CG -->|Docker| NR
    CG -->|Docker| MQTT
    NR -->|MQTT| MQTT
    
    MQTT -->|WLAN| WLAN
    WLAN -->|MQTT| DPS
    WLAN -->|MQTT| FTS
    LAN -->|OPC-UA| AIQS
    
    MQTT -->|Store| LOGS
    FTC -->|Cache| CACHE
    
    DPS -->|MQTT| MQTT
    FTS -->|MQTT| MQTT
    AIQS -->|OPC-UA| NR
```

## 🔐 Sicherheits-Architektur-Diagramm

```mermaid
graph TB
    subgraph "Internet (Unsicher)"
        FTC[Fischertechnik Cloud<br/>HTTPS/TLS]
    end
    
    subgraph "Local Network (Teilweise unsicher)"
        CG[Cloud Gateway<br/>SSH: ft/fischertechnik]
        WLAN[WLAN Access Point<br/>Unverschlüsselt]
        LAN[LAN Switch<br/>Statische IPs]
    end
    
    subgraph "Module Layer (Unverschlüsselt)"
        DPS[DPS Module<br/>MQTT unverschlüsselt]
        FTS[FTS Module<br/>MQTT unverschlüsselt]
        AIQS[AIQS Modules<br/>OPC-UA unverschlüsselt]
    end
    
    subgraph "Sicherheitsrisiken"
        RISK1[WLAN unverschlüsselt<br/>⚠️ Sniffing möglich]
        RISK2[SSH Standard-Passwörter<br/>⚠️ Brute Force möglich]
        RISK3[MQTT unverschlüsselt<br/>⚠️ Man-in-the-Middle]
        RISK4[OPC-UA unverschlüsselt<br/>⚠️ Industrial Spoofing]
    end
    
    FTC -.->|HTTPS/TLS| CG
    CG -->|WLAN| WLAN
    WLAN -->|MQTT| DPS
    WLAN -->|MQTT| FTS
    LAN -->|OPC-UA| AIQS
    
    WLAN -.->|Risiko| RISK1
    CG -.->|Risiko| RISK2
    MQTT -.->|Risiko| RISK3
    AIQS -.->|Risiko| RISK4
```

## 📈 Datenverarbeitungs-Pipeline

### 1. **Datenaufnahme**
- **Camera Images**: Base64-kodierte JPEG-Daten
- **Sensor Data**: Qualitätsprüfungen, Temperatur, Druck
- **Module States**: Verbindungsstatus, Fehlerzustände

### 2. **Datenverarbeitung**
- **Cloud Gateway**: Aggregation und Routing
- **Node-RED**: Flow-basierte Verarbeitung
- **MQTT Broker**: Message Queuing und Distribution

### 3. **Datenspeicherung**
- **Fischertechnik Cloud**: Dashboard-Daten, Caching
- **Local Logs**: Session-Daten, Debug-Informationen

### 4. **Datenverbrauch**
- **Dashboard UI**: Echtzeit-Visualisierung
- **REST API**: Externe System-Integration
- **Log Analysis**: Debugging und Optimierung

## 🔄 Message Flow Patterns

### **Command Flow (Outbound)**
```
Cloud → Gateway → MQTT → Module
```

### **Telemetry Flow (Inbound)**
```
Module → MQTT → Gateway → Cloud
```

### **Local Processing Flow**
```
Module → MQTT → Session Manager → Logs
```

---

**"Daten fließen über MQTT, werden in Node-RED verarbeitet und in der Cloud visualisiert."**
