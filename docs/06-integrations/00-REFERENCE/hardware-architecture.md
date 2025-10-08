# 🏗️ APS Hardware-Architektur - "as IS"

**Verifiziert durch:** Netzwerk-Scans, Session-Logs, Integration-Tests  
**Datum:** 2025-10-08

---

## 🗺️ System-Architektur-Übersicht

```mermaid
graph TB
    subgraph "APS-Ecosystem"
        subgraph "Raspberry Pi 4B (192.168.0.100)"
            subgraph "Docker Container"
                MQTT["MQTT Broker<br/>Mosquitto<br/>172.18.0.4:1883"]
                NODERED["Node-RED<br/>OPC-UA Bridge<br/>Port 1880"]
                CCU["CCU-Backend<br/>ff-central-control<br/>Order-Management"]
                DASH["APS Dashboard<br/>Angular PWA<br/>172.18.0.5:80"]
            end
        end
        
        subgraph "TXT-Controller (WLAN, MQTT only)"
            TXT_FTS["TXT-FTS<br/>5iO4<br/>192.168.0.104"]
            TXT_DPS["TXT-DPS<br/>SVR4H73275<br/>192.168.0.102"]
            TXT_AIQS["TXT-AIQS<br/>SVR4H76530<br/>192.168.0.103"]
        end
        
        subgraph "Production Modules (LAN, OPC-UA only)"
            HBW["HBW<br/>SVR3QA0022<br/>192.168.0.80:4840"]
            DRILL["DRILL<br/>SVR4H76449<br/>192.168.0.50:4840"]
            MILL["MILL<br/>SVR3QA2098<br/>192.168.0.40:4840"]
            DPS_SPS["DPS SPS<br/>SVR4H73275<br/>192.168.0.90:4840"]
            AIQS_SPS["AIQS SPS<br/>SVR4H76530<br/>192.168.0.70:4840"]
        end
    end
    
    %% MQTT Connections
    TXT_FTS <-->|MQTT| MQTT
    TXT_DPS <-->|MQTT| MQTT
    TXT_AIQS <-->|MQTT| MQTT
    CCU <-->|MQTT| MQTT
    NODERED <-->|MQTT| MQTT
    DASH <-->|MQTT| MQTT
    
    %% OPC-UA Connections
    NODERED <-->|OPC-UA| HBW
    NODERED <-->|OPC-UA| DRILL
    NODERED <-->|OPC-UA| MILL
    NODERED <-->|OPC-UA| DPS_SPS
    NODERED <-->|OPC-UA| AIQS_SPS
    
    classDef docker fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef txt fill:#fff8e1,stroke:#f57c00,stroke-width:2px
    classDef sps fill:#f5f5f5,stroke:#757575,stroke-width:2px
    
    class MQTT,NODERED,CCU,DASH docker
    class TXT_FTS,TXT_DPS,TXT_AIQS txt
    class HBW,DRILL,MILL,DPS_SPS,AIQS_SPS sps
```

**Wichtig:**
- 🔵 **Docker-Container** (blau) - Raspberry Pi
- 🟡 **TXT-Controller** (gelb) - MQTT-fähig
- ⚪ **SPS-Module** (grau) - Nur OPC-UA

---

## 🖥️ Zentrale Steuerung: Raspberry Pi 4B

### Hardware
- **Model:** Raspberry Pi 4 Model B
- **IP:** 192.168.0.100 (statisch)
- **OS:** Linux (Raspbian)
- **Rolle:** Zentrale Fabrik-Steuerung

### Docker-Container
```
Raspberry Pi: 192.168.0.100
├── MQTT Broker (Mosquitto)
│   └── Port: 1883
├── Node-RED
│   └── Port: 1880 (Admin API)
├── CCU-Backend (ff-central-control)
│   └── Source: integrations/APS-CCU/ff-central-control-unit/central-control/
└── APS Dashboard Frontend (Angular PWA)
    └── Port: 80
```

### Docker-Networking
```
172.18.0.4 → MQTT Broker
172.18.0.5 → Dashboard Frontend
192.168.0.100 → External Access
```

---

## 🤖 TXT-Controller (Fischertechnik TXT 4.0)

### Übersicht
- **OS:** Linux
- **MQTT:** ✅ Nativ
- **OPC-UA:** ❌ Nicht verfügbar
- **Netzwerk:** WLAN (DHCP)
- **SSH:** ft / fischertechnik

### TXT-FTS (Fahrerloses Transportsystem)
- **IP:** 192.168.0.104 (normalerweise)
- **Client-ID:** `auto-F6DFC829`
- **Serial:** 5iO4
- **Will Topic:** `fts/v1/ff/5iO4/connection`
- **Rolle:** AGV-Navigation nach VDA 5050

### TXT-DPS (Delivery & Pickup Station)
- **IP:** 192.168.0.102 (normalerweise)
- **Client-ID:** `auto-AC941349`
- **Serial:** SVR4H73275
- **Will Topic:** `module/v1/ff/NodeRed/SVR4H73275/connection`
- **Rolle:** Warenein-/ausgang, Roboter-Arm
- **Zusatz:** OPC-UA @ 192.168.0.90

### TXT-AIQS (AI Quality System)
- **IP:** 192.168.0.103 (normalerweise)
- **Client-ID:** `auto-B9109AD9`
- **Serial:** SVR4H76530
- **Will Topic:** `module/v1/ff/NodeRed/SVR4H76530/connection`
- **Rolle:** Qualitätskontrolle, Kamera, AI
- **Zusatz:** OPC-UA @ 192.168.0.70

---

## 🏭 Produktions-Module (Siemens S7-1200 SPS)

### Übersicht
- **Protokoll:** Nur OPC-UA (kein MQTT)
- **Netzwerk:** LAN (statische IPs)
- **MQTT-Bridge:** NodeRed übernimmt Kommunikation

### HBW (High Bay Warehouse)
- **Serial:** SVR3QA0022
- **IP:** 192.168.0.80:4840 (OPC-UA)
- **Version:** 1.3.0
- **Firmware:** MOD-FF22+HBW+24V
- **MQTT:** Via NodeRed (`module/v1/ff/SVR3QA0022/*`)

### DRILL (Bohrstation)
- **Serial:** SVR4H76449
- **IP:** 192.168.0.50:4840 (OPC-UA)
- **Version:** 1.3.0
- **Production Duration:** 5s
- **MQTT:** Via NodeRed (`module/v1/ff/SVR4H76449/*`)

### MILL (Frässtation)
- **Serial:** SVR3QA2098
- **IP:** 192.168.0.40:4840 (OPC-UA)
- **Version:** 1.3.0
- **Production Duration:** 5s
- **MQTT:** Via NodeRed (`module/v1/ff/SVR3QA2098/*`)

---

## 🌐 Netzwerk-Architektur

```mermaid
graph TB
    subgraph "Netzwerk-Topologie"
        ROUTER["TP-Link Router<br/>192.168.0.1<br/>DHCP + Switch"]
        
        subgraph "Raspberry Pi 4B - 192.168.0.100"
            RASP["Raspberry Pi<br/>Statische IP"]
            
            subgraph "Docker (172.18.0.x)"
                MQTT["MQTT Broker<br/>172.18.0.4:1883"]
                CCU["CCU-Backend<br/>Order-Mgmt"]
                NR["NodeRed<br/>1880"]
                DASH["Dashboard<br/>172.18.0.5"]
            end
        end
        
        subgraph "WLAN - Dynamische IPs"
            TXT_FTS["TXT-FTS<br/>192.168.0.104"]
            TXT_DPS["TXT-DPS<br/>192.168.0.102"]
            TXT_AIQS["TXT-AIQS<br/>192.168.0.103"]
        end
        
        subgraph "LAN - Statische IPs"
            MILL["MILL SPS<br/>192.168.0.40:4840"]
            DRILL["DRILL SPS<br/>192.168.0.50:4840"]
            AIQS["AIQS SPS<br/>192.168.0.70:4840"]
            HBW["HBW SPS<br/>192.168.0.80:4840"]
            DPS["DPS SPS<br/>192.168.0.90:4840"]
        end
    end
    
    ROUTER --- RASP
    ROUTER --- TXT_FTS
    ROUTER --- TXT_DPS
    ROUTER --- TXT_AIQS
    ROUTER --- MILL
    ROUTER --- DRILL
    ROUTER --- AIQS
    ROUTER --- HBW
    ROUTER --- DPS
    
    TXT_FTS -.->|MQTT| MQTT
    TXT_DPS -.->|MQTT| MQTT
    TXT_AIQS -.->|MQTT| MQTT
    
    NR -->|OPC-UA| MILL
    NR -->|OPC-UA| DRILL
    NR -->|OPC-UA| AIQS
    NR -->|OPC-UA| HBW
    NR -->|OPC-UA| DPS
    
    classDef rasp fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef txt fill:#fff8e1,stroke:#f57c00,stroke-width:2px
    classDef sps fill:#f5f5f5,stroke:#757575,stroke-width:2px
    
    class RASP,MQTT,CCU,NR,DASH rasp
    class TXT_FTS,TXT_DPS,TXT_AIQS txt
    class MILL,DRILL,AIQS,HBW,DPS sps
```

### WLAN-Netzwerk (192.168.0.x)
```
Router: 192.168.0.1 (TP-Link TL-WR902AC)
├── Raspberry Pi: 192.168.0.100 (statisch)
├── TXT-FTS: 192.168.0.104 (DHCP)
├── TXT-DPS: 192.168.0.102 (DHCP)
└── TXT-AIQS: 192.168.0.103 (DHCP)
```

**Hinweis:** TXT-Controller IPs können variieren (DHCP)

### LAN-Netzwerk (192.168.0.x)
```
Switch: 192.168.0.1
├── MILL (S7-1200): 192.168.0.40:4840 (statisch)
├── DRILL (S7-1200): 192.168.0.50:4840 (statisch)
├── AIQS (S7-1200): 192.168.0.70:4840 (statisch)
├── HBW (S7-1200): 192.168.0.80:4840 (statisch)
└── DPS (S7-1200): 192.168.0.90:4840 (statisch)
```

### Docker-Netzwerk (172.18.0.x)
```
Docker Bridge: 172.18.0.x
├── MQTT Broker: 172.18.0.4:1883
└── Dashboard: 172.18.0.5
```

---

## 🔄 Kommunikations-Protokolle

### MQTT (Message Queuing Telemetry Transport)
- **Broker:** 192.168.0.100:1883 (Mosquitto)
- **QoS:** 0 (Test), 1 (Sensor), 2 (Commands)
- **Encryption:** Keine
- **Authentication:** Keine
- **Verwendet von:** TXT-Controller, CCU-Backend, NodeRed, Dashboard

### OPC-UA (Open Platform Communications)
- **Port:** 4840 (Standard)
- **Encryption:** Keine
- **Security:** None
- **Verwendet von:** S7-1200 Module → NodeRed

### SSH
- **Port:** 22
- **User:** ft
- **Password:** fischertechnik
- **Verwendet für:** TXT-Controller Remote-Access

---

## 📦 Software-Komponenten

### CCU-Backend (ff-central-control)
- **Location:** Raspberry Pi Docker
- **Source:** `integrations/APS-CCU/ff-central-control-unit/central-control/`
- **Sprache:** JavaScript (kompiliert von TypeScript)
- **Rolle:** Order-Management, UUID-Generation, FTS-Orchestration

### NodeRed
- **Location:** Raspberry Pi Docker
- **Port:** 1880
- **Rolle:** OPC-UA ↔ MQTT Bridge
- **Flows:** `integrations/APS-NodeRED/backups/*/flows.json`
- **Instances:** 2 (SUB + PUB)

### MQTT Broker (Mosquitto)
- **Location:** Raspberry Pi Docker
- **Port:** 1883
- **Config:** `integrations/mosquitto/config/mosquitto.conf`

---

## 🔗 Siehe auch

- [Module Serial Mapping](module-serial-mapping.md) - Detaillierte Serial-Number-Zuordnung
- [MQTT Topic Conventions](mqtt-topic-conventions.md) - Topic-Naming-Patterns
- [CCU-Backend Orchestration](ccu-backend-orchestration.md) - Order-Flow Details

---

**Status:** Verifizierte Hardware-Architektur "as IS" ✅

