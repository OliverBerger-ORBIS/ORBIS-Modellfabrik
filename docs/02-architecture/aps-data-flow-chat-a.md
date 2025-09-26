# APS Data Flow Architecture - Chat-A Version

> **Chat-A Bearbeitung:** Formale Bereinigung mit korrekten Phasen-Informationen  
> **Datum:** 2025-09-25  
> **Status:** Neue Version mit OMF-Style-Guide und korrekten Phasen

---

## 📋 Architektur-Phasen (Korrekte Definition)

### **Phase 0: APS "as IS" - Fischertechnik-System verstehen**
- **Status:** ✅ Abgeschlossen
- **Ziel:** Das bestehende Fischertechnik APS-System vollständig verstehen
- **Erreicht:** APS-Ecosystem dokumentiert, Mosquitto-Analyse, APS-NodeRED Flows analysiert

### **Phase 1: OMF-Dashboard mit APS-CCU Frontend-Funktionalität**
- **Status:** 🔄 In Bearbeitung
- **Ziel:** APS-Dashboard Funktionalität im OMF-Dashboard nachbauen
- **Erreicht:** APS Overview Tab, APS Control Tab, APS Steering Tab, APS Orders Tab
- **Aktuell:** Sensor-Daten Integration testen, APS Configuration Tab implementieren

### **Phase 2: OMF-Dashboard mit APS-NodeRED Funktionalität**
- **Status:** ⏳ Geplant
- **Ziel:** APS-NodeRED Gateway-Funktionalität im OMF-Dashboard integrieren
- **Geplant:** MQTT ↔ OPC-UA Gateway, VDA 5050 FTS-Standard, Registry-basierte Konfiguration

### **Phase 3: Erweiterungen (Zukünftige Entwicklung)**
- **Status:** ⏳ Geplant
- **Ziel:** OMF-System um erweiterte Funktionalitäten ausbauen
- **Geplant:** DSP-Anbindung, ORBIS Cloud, SAP/ERP, KI-Use-cases, erweiterte Analytics

---

## 📊 Datenfluss-Diagramm (Phase 1: OMF-Dashboard Integration)

```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TD
classDef orbis fill:#e3f2fd,stroke:#bbdefb,stroke-width:2px,color:#0b2e59;
classDef fthardware fill:#fff8e1,stroke:#ffecb3,stroke-width:2px,color:#0b3d16;
classDef ftsoftware fill:#ffebee,stroke:#ffcdd2,stroke-width:2px,color:#7a1a14;
classDef external fill:#f5f5f5,stroke:#e0e0e0,stroke-width:2px,color:#333;

    subgraph "Data Sources"
        CAM[Camera Images<br/>Base64 JPEG]:::fthardware
        SENS[Sensor Data<br/>Quality Checks]:::fthardware
        STATE[Module States<br/>Connection Status]:::fthardware
    end
    
    subgraph "Data Processing"
        CG[Cloud Gateway<br/>~192.168.0.101<br/>Data Aggregation]:::ftsoftware
        NR[APS-NodeRED<br/>192.168.0.100<br/>Flow Processing]:::ftsoftware
        MQTT[mosquitto<br/>192.168.0.100<br/>Message Routing]:::external
    end
    
    subgraph "Data Storage"
        CLOUD[Fischertechnik Cloud<br/>Dashboard Data]:::external
        LOCAL[Local Logs<br/>Session Data]:::external
    end
    
    subgraph "Data Consumers"
        FT_DASH[Fischertechnik Dashboard<br/>192.168.0.100<br/>Angular PWA]:::ftsoftware
        OMF_DASH[OMF Dashboard<br/>Streamlit App]:::orbis
        SESSION[Session Manager<br/>Replay/Recording]:::orbis
        API[REST API<br/>External Systems]:::external
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
```

## 🔄 Kommunikations-Protokoll-Diagramm (VDA 5050 Standard)

```mermaid
sequenceDiagram
    participant FTC as Fischertechnik Cloud
    participant CG as Cloud Gateway
    participant MQTT as mosquitto
    participant DPS as TXT-DPS
    participant AIQS as TXT-AIQS
    participant FTS as TXT-FTS
    
    Note over FTC,FTS: VDA 5050 Standard Communication
    
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

## 🏗️ System-Komponenten-Diagramm (Phase 1)

```mermaid
%%{init: {'theme':'neutral'}}%%
graph TB
classDef orbis fill:#e3f2fd,stroke:#bbdefb,stroke-width:2px,color:#0b2e59;
classDef fthardware fill:#fff8e1,stroke:#ffecb3,stroke-width:2px,color:#0b3d16;
classDef ftsoftware fill:#ffebee,stroke:#ffcdd2,stroke-width:2px,color:#7a1a14;
classDef external fill:#f5f5f5,stroke:#e0e0e0,stroke-width:2px,color:#333;

    subgraph "Cloud Layer"
        FTC[Fischertechnik Cloud<br/>fischertechnik-cloud.com<br/>Angular PWA]:::external
        API[Cloud API<br/>REST/HTTPS]:::external
    end
    
    subgraph "Gateway Layer"
        CG[Cloud Gateway<br/>~192.168.0.101<br/>TXT 4.0 Controller]:::fthardware
        NR[APS-NodeRED<br/>192.168.0.100<br/>Docker Container]:::ftsoftware
        MQTT[mosquitto<br/>192.168.0.100<br/>Port 1883]:::external
    end
    
    subgraph "Module Layer"
        DPS[TXT-DPS<br/>TXT 4.0]:::fthardware
        FTS[TXT-FTS<br/>TXT 4.0]:::fthardware
        AIQS[TXT-AIQS<br/>SPS S7-1200]:::fthardware
    end
    
    subgraph "Network Layer"
        WLAN[WLAN Access Point<br/>Unverschlüsselt]:::external
        LAN[LAN Switch<br/>Statische IPs]:::external
    end
    
    subgraph "Data Layer"
        LOGS[Session Logs<br/>SQLite + JSON]:::external
        CACHE[Cloud Cache<br/>Service Worker]:::external
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
%%{init: {'theme':'neutral'}}%%
graph TB
classDef orbis fill:#e3f2fd,stroke:#bbdefb,stroke-width:2px,color:#0b2e59;
classDef fthardware fill:#fff8e1,stroke:#ffecb3,stroke-width:2px,color:#0b3d16;
classDef ftsoftware fill:#ffebee,stroke:#ffcdd2,stroke-width:2px,color:#7a1a14;
classDef external fill:#f5f5f5,stroke:#e0e0e0,stroke-width:2px,color:#333;
classDef risk fill:#ffebee,stroke:#ef5350,stroke-dasharray: 5 3,color:#7a1a14;

    subgraph "Internet (Unsicher)"
        FTC[Fischertechnik Cloud<br/>HTTPS/TLS]:::external
    end
    
    subgraph "Local Network (Teilweise unsicher)"
        CG[Cloud Gateway<br/>SSH: ft/fischertechnik]:::fthardware
        WLAN[WLAN Access Point<br/>Unverschlüsselt]:::external
        LAN[LAN Switch<br/>Statische IPs]:::external
    end
    
    subgraph "Module Layer (Unverschlüsselt)"
        DPS[TXT-DPS<br/>MQTT unverschlüsselt]:::fthardware
        FTS[TXT-FTS<br/>MQTT unverschlüsselt]:::fthardware
        AIQS[TXT-AIQS<br/>OPC-UA unverschlüsselt]:::fthardware
    end
    
    subgraph "Sicherheitsrisiken"
        RISK1[WLAN unverschlüsselt<br/>⚠️ Sniffing möglich]:::risk
        RISK2[SSH Standard-Passwörter<br/>⚠️ Brute Force möglich]:::risk
        RISK3[MQTT unverschlüsselt<br/>⚠️ Man-in-the-Middle]:::risk
        RISK4[OPC-UA unverschlüsselt<br/>⚠️ Industrial Spoofing]:::risk
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
- **APS-NodeRED**: Flow-basierte Verarbeitung
- **mosquitto**: Message Queuing und Distribution

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

## 📋 Chat-A Änderungen

### ✅ **Formale Bereinigung:**
- **Phasen-Definition korrigiert** - Phase 0/1/2/3 statt Phase 1/2
- **OMF-Style-Guide angewendet** - Konsistente Farben (Blau=ORBIS, Gelb=FT-Hardware, Rot=FT-Software, Grau=External)
- **Namenskonventionen standardisiert** - APS-NodeRED, TXT-DPS, TXT-AIQS, TXT-FTS, mosquitto
- **Mermaid-Diagramme standardisiert** - classDef-Definitionen, konsistente Farbzuordnung

### ❌ **NICHT geändert (Chat-B Aufgabe):**
- Inhaltliche Architektur-Updates
- Aktuelle Implementierungsdetails
- Technische Korrekturen

---

**"Daten fließen über MQTT, werden in APS-NodeRED verarbeitet und in der Cloud visualisiert."** 🚀
