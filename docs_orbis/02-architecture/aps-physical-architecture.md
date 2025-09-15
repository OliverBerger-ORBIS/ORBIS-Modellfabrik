# APS Physical Architecture - Fischertechnik System

## 📋 Architektur-Phasen

### Phase 1: Ausgangssituation (Fischertechnik Standard)
- **Fischertechnik Cloud** → **Cloud Gateway** → **Module**
- **Zentrale Steuerung** über Fischertechnik Dashboard
- **Keine OMF-Integration**

```mermaid
graph TB
    subgraph "Internet"
        FTC[Fischertechnik Cloud<br/>fischertechnik-cloud.com]
    end
    
    subgraph "Raspberry Pi 4B (192.168.0.100)"
        subgraph "Docker Container (192.168.0.100)"
            FT_APP[Fischertechnik App<br/>Angular PWA]
            MQTT[MQTT Broker<br/>Port 1883]
            NR[Node-RED<br/>Port 1880]
        end
    end
    
    subgraph "WLAN-Netzwerk"
        CG[Cloud Gateway<br/>~192.168.0.**101**<br/>TXT 4.0]
        DPS_TXT[DPS TXT Controller<br/>192.168.0.**102**<br/>TXT 4.0]
        AIQS_TXT[AIQS TXT Controller<br/>192.168.0.**103**<br/>TXT 4.0]
        FTS[FTS<br/>192.168.0.**104**<br/>TXT 4.0]
    end
    
    subgraph "LAN-Netzwerk (Statische IPs)"
        AIQS[AIQS<br/>192.168.0.70<br/>SPS S7-1200]
        DPS[DPS<br/>192.168.0.90<br/>SPS S7-1200]
        HBW[HBW<br/>192.168.0.80<br/>SPS S7-1200]
        MILL[MILL<br/>192.168.0.40<br/>SPS S7-1200]
        DRILL[DRILL<br/>192.168.0.50<br/>SPS S7-1200]
    end
    
    FTC -.->|HTTPS/REST| CG
    CG -->|WLAN| FT_APP
    FT_APP -->|MQTT| MQTT
    MQTT -->|Route| NR
    NR -->|OPC-UA| AIQS
    NR -->|OPC-UA| DPS
    NR -->|OPC-UA| HBW
    NR -->|OPC-UA| MILL
    NR -->|OPC-UA| DRILL
    DPS_TXT -->|MQTT| MQTT
    AIQS_TXT -->|MQTT| MQTT
    FTS -->|MQTT| MQTT
    
    classDef fischertechnik fill:#f5f5f5,stroke:#757575,stroke-width:2px
    classDef modules fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    class FTC,FT_APP fischertechnik
    class MQTT,NR,CG,DPS_TXT,AIQS_TXT,FTS,AIQS,DPS,HBW,MILL,DRILL modules
```

### Phase 2: ORBIS-Integration (Aktuell)
- **OMF Dashboard** ergänzt **Fischertechnik Dashboard**
- **Session Manager** für Replay/Recording
- **Registry-basierte** Steuerung
- **DPS-Modul** bereits vorhanden (nicht hinzugefügt)

#### 🔄 Was wird ersetzt/erweitert:
- **Fischertechnik Dashboard** → **OMF Dashboard** (Streamlit) - **Ersetzt**
- **Manuelle Steuerung** → **Registry-basierte** Steuerung - **Erweitert**
- **Keine Replay-Funktion** → **Session Manager** für Tests - **Hinzugefügt**
- **Cloud-only** → **Lokale + Cloud** Steuerung - **Erweitert**

---

## 🏭 Netzwerk-Architektur (Phase 2: ORBIS-Integration)

```mermaid
graph TB
    subgraph "Internet"
        FTC[Fischertechnik Cloud<br/>fischertechnik-cloud.com]
    end
    
    subgraph "TP-Link Router (192.168.0.1)"
        WLAN[WLAN Access Point<br/>DHCP Server]
        LAN[LAN Switch]
    end
    
    subgraph "Raspberry Pi 4B (192.168.0.100)"
        subgraph "Docker Container (192.168.0.100)"
            NR[Node-RED<br/>Port 1880<br/>Admin API]
            MQTT[MQTT Broker<br/>Port 1883]
            FT_APP[Fischertechnik App<br/>Angular PWA]
        end
    end
    
    subgraph "OMF System (ORBIS-Integration)"
        OMF_DASH[OMF Dashboard<br/>Streamlit App]
        SESSION[Session Manager<br/>Replay/Recording]
        REGISTRY[Registry v1<br/>Templates & Mappings]
    end
    
    subgraph "WLAN-Netzwerk (Dynamische IPs)"
        CG[Cloud Gateway<br/>~192.168.0.**101**<br/>TXT 4.0<br/>ft/fischertechnik]
        DPS_TXT[DPS TXT Controller<br/>192.168.0.**102**<br/>TXT 4.0<br/>ft/fischertechnik]
        AIQS_TXT[AIQS TXT Controller<br/>192.168.0.**103**<br/>TXT 4.0<br/>ft/fischertechnik]
        FTS[FTS<br/>192.168.0.**104**<br/>TXT 4.0<br/>ft/fischertechnik]
    end
    
    subgraph "LAN-Netzwerk (Statische IPs)"
        AIQS[AIQS<br/>192.168.0.70<br/>SPS S7-1200<br/>OPC-UA Server]
        DPS[DPS<br/>192.168.0.90<br/>SPS S7-1200<br/>OPC-UA Server]
        HBW[HBW<br/>192.168.0.80<br/>SPS S7-1200<br/>OPC-UA Server]
        MILL[MILL<br/>192.168.0.40<br/>SPS S7-1200<br/>OPC-UA Server]
        DRILL[DRILL<br/>192.168.0.50<br/>SPS S7-1200<br/>OPC-UA Server]
    end
    
    FTC -.->|HTTPS/REST| CG
    CG -->|WLAN| WLAN
    DPS_TXT -->|WLAN| WLAN
    AIQS_TXT -->|WLAN| WLAN
    FTS -->|WLAN| WLAN
    
    AIQS -->|LAN| LAN
    DPS -->|LAN| LAN
    HBW -->|LAN| LAN
    MILL -->|LAN| LAN
    DRILL -->|LAN| LAN
    
    WLAN -.->|MQTT| MQTT
    LAN -.->|OPC-UA| AIQS
    LAN -.->|OPC-UA| DPS
    LAN -.->|OPC-UA| HBW
    LAN -.->|OPC-UA| MILL
    LAN -.->|OPC-UA| DRILL
    DPS_TXT -->|MQTT| MQTT
    AIQS_TXT -->|MQTT| MQTT
    
    OMF_DASH -->|MQTT| MQTT
    SESSION -->|MQTT| MQTT
    REGISTRY -->|Templates| OMF_DASH
    
    classDef fischertechnik fill:#f5f5f5,stroke:#757575,stroke-width:2px
    classDef orbis fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef modules fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    class FTC,FT_APP fischertechnik
    class OMF_DASH,SESSION,REGISTRY orbis
    class MQTT,NR,CG,DPS_TXT,AIQS_TXT,FTS,AIQS,DPS,HBW,MILL,DRILL modules
```

## 🔐 Zugangsdaten & Sicherheit

### SSH-Zugang (alle TXT Controller)
- **Username**: `ft`
- **Password**: `fischertechnik`

### Node-RED Admin API
- **URL**: `http://192.168.0.101:1880`
- **Backup-Endpoint**: `/flows` (JSON-Export)

### MQTT-Broker
- **Host**: `192.168.0.101` (Cloud Gateway)
- **Port**: `1883`

## ⚠️ Sicherheitshinweise
- WLAN ist unverschlüsselt
- SSH-Passwörter sind Standard
- MQTT läuft unverschlüsselt
- Keine Firewall-Regeln konfiguriert

## 📡 Kommunikations-Protokolle

### MQTT (Message Queuing Telemetry Transport)
- **Port**: 1883 (unverschlüsselt)
- **QoS**: 0 für Telemetrie, 1 für Befehle
- **Retain**: False (keine persistenten Nachrichten)

### OPC-UA (Open Platform Communications Unified Architecture)
- **Port**: 4840 (Standard)
- **Sicherheit**: Keine Verschlüsselung
- **Verwendung**: Modul-spezifische Steuerung

### HTTPS/REST
- **Port**: 443 (verschlüsselt)
- **Verwendung**: Cloud-Kommunikation, API-Zugriff

## 🏗️ Hardware-Übersicht

### TXT 4.0 Controller
- **Betriebssystem**: Linux
- **SSH**: Port 22
- **Web-Interface**: Port 80
- **Verwendung**: Cloud Gateway, DPS, FTS

### SPS S7-1200 Controller
- **Betriebssystem**: Siemens TIA Portal
- **OPC-UA Server**: Port 4840
- **Verwendung**: AIQS-Module (6x)

### TP-Link TL-WR902AC Router
- **WLAN**: Unverschlüsselt
- **LAN**: Statische IPs für Module
- **DHCP**: Dynamische IPs für TXT Controller

## 🔄 IP-Adress-Management

### Raspberry Pi 4B (Zentral)
```
Raspberry Pi: 192.168.0.100 (statisch)
├── Docker Container: 192.168.0.100
│   ├── Node-RED: Port 1880
│   ├── MQTT Broker: Port 1883
│   └── Fischertechnik App: Angular PWA
└── TP-Link Router: 192.168.0.1 (Gateway)
```

### Statische IPs (LAN)
```
AIQS: 192.168.0.70 (1 Modul)
DPS: 192.168.0.90 (1 Modul)
HBW: 192.168.0.80 (1 Modul)
MILL: 192.168.0.40 (1 Modul)
DRILL: 192.168.0.50 (1 Modul)
```

### Dynamische IPs (WLAN)
```
Cloud Gateway: ~192.168.0.101 (normalerweise, kann sich ändern)
DPS TXT Controller: 192.168.0.102 (normalerweise, wenn kein anderer Client)
AIQS TXT Controller: 192.168.0.103 (normalerweise, wenn kein anderer Client)
FTS: 192.168.0.104 (normalerweise, wenn kein anderer Client)
```

**Hinweis**: 
- **Statische IPs** sind fest zugewiesen und ändern sich nicht
- **Dynamische IPs** können sich durch DHCP und Race Conditions ändern
- **`~`** bedeutet "normalerweise" oder "häufig"
- **TXT Controller** bekommen normalerweise 192.168.0.102-104, wenn kein anderer Client sich anmeldet

---

**"Alle Steuerung läuft über MQTT, Node-RED ist der intelligente Vermittler zur Hardware."**
