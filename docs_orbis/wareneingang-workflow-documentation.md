# Wareneingang-Workflow Dokumentation

## 🎯 Übersicht

Dieses Dokument beschreibt den vollständigen Wareneingang-Workflow der ORBIS-Modellfabrik basierend auf der Analyse von MQTT-Sessions. Der Workflow wird durch das Ablegen eines Werkstücks in die Wareneingangs-Position der DPS (Delivery and Pickup Station) ausgelöst.

## 🔄 Workflow-Sequenz

### **1. Werkstück-Erkennung (DPS)**
- **Trigger:** Lichtschranke erkennt Werkstück in DPS
- **6-Armroboter:** Farberkennung + NFC-Code Auslesung
- **Werkstück-ID:** `047389ca341291` → **Friendly-ID:** `B1` (Blau, Position 1)
- **Farbe:** `BLUE` (erkannt durch Farbsensor)

### **2. HBW-Platzprüfung**
- **Prüfung:** Freie Positionen für Farbe `BLUE` im HBW
- **Verfügbare Plätze:** `C1`, `C2`, `C3` (Blau-Bereich)
- **Entscheidung:** Platz verfügbar → FTS-Transport starten

### **3. FTS-Transport**
- **Route:** `DPS` → `Node 2` → `Node 1` → `HBW`
- **Befehle:** `PASS` → `DOCK` → `clearLoadHandler`
- **Transport-Zeit:** ~11 Sekunden

### **4. HBW-Einlagerung**
- **Position:** Nächste freie Position `C1`
- **Befehl:** `PICK` (Werkstück aufnehmen)
- **Speicherung:** Werkstück-ID + Position persistiert

## 🏭 Modul-Mapping

| Modul-ID | Friendly Name | Funktion | IP-Adresse |
|----------|---------------|----------|------------|
| `SVR4H73275` | **DPS** | Delivery and Pickup Station | `192.168.0.90` |
| `SVR3QA0022` | **HBW** | Hochregallager | `192.168.0.80` |
| `5iO4` | **FTS** | Fahrerloses Transportsystem | `192.168.0.104` |
| `SVR4H76449` | **DRILL** | Bohrer | `192.168.0.50` |
| `SVR3QA2098` | **MILL** | Fräse | `192.168.0.40` |
| `SVR4H76530` | **AIQS** | Qualitätsprüfung | `192.168.0.70` |
| `CHRG0` | **CHARGING** | Ladestation | - |

## 📋 Order-Management

### **Order-ID Erstellung**
- **Order-ID:** `7752923a-5d49-4ba4-8429-943e6581ef62`
- **Order-Type:** `STORAGE` (Wareneingang)
- **Workpiece-ID:** `047389ca341291` → **Friendly-ID:** `B1`
- **Farbe:** `BLUE`
- **Erstellt durch:** CCU (Central Control Unit)

### **Production Steps**
```json
{
  "orderType": "STORAGE",
  "type": "BLUE",
  "workpieceId": "047389ca341291",
  "productionSteps": [
    {
      "type": "NAVIGATION",
      "source": "START",
      "target": "DPS",
      "state": "FINISHED"
    },
    {
      "type": "MANUFACTURE",
      "command": "DROP",
      "moduleType": "DPS",
      "state": "FINISHED"
    },
    {
      "type": "NAVIGATION",
      "source": "DPS",
      "target": "HBW",
      "state": "FINISHED"
    },
    {
      "type": "MANUFACTURE",
      "command": "PICK",
      "moduleType": "HBW",
      "state": "FINISHED"
    }
  ]
}
```

## 🎛️ CCU (Central Control Unit) Orchestrierung

### **Zentrale Rolle**
- **Orchestrator:** CCU koordiniert alle Module
- **State Machine:** VDA 5050 kompatibel
- **Order Management:** Erstellt und verwaltet Orders
- **Status Monitoring:** Überwacht alle Module-Status

### **CCU Topics**
- `ccu/order/active` - Aktive Orders
- `ccu/order/completed` - Abgeschlossene Orders
- `ccu/pairing/state` - Module-Verbindungsstatus
- `ccu/state/stock` - Lagerbestand

### **Module Status Management**
```json
{
  "modules": [
    {
      "serialNumber": "SVR3QA0022",
      "type": "MODULE",
      "subType": "HBW",
      "available": "READY",
      "assigned": false,
      "connected": true
    }
  ],
  "transports": [
    {
      "serialNumber": "5iO4",
      "type": "FTS",
      "available": "READY",
      "connected": true,
      "batteryPercentage": 107
    }
  ]
}
```

## 🚗 FTS (Fahrerloses Transportsystem) Navigation

### **Navigation-Parameter**
- **Route:** Vordefinierte Node-Sequenz
- **Nodes:** `SVR4H73275` → `2` → `1` → `SVR3QA0022`
- **Befehle:** `PASS`, `DOCK`, `clearLoadHandler`
- **Load Handling:** Koordiniert mit Ziel-Modul

### **FTS State Machine**
```json
{
  "actionStates": [
    {
      "command": "PASS",
      "state": "FINISHED"
    },
    {
      "command": "DOCK",
      "state": "FINISHED"
    },
    {
      "command": "clearLoadHandler",
      "state": "FINISHED"
    }
  ],
  "driving": false,
  "waitingForLoadHandling": false,
  "load": [
    {
      "loadPosition": "1",
      "loadId": "047389ca341291",
      "loadType": "BLUE"
    }
  ]
}
```

### **Battery Management**
- **Spannung:** 9.2V
- **Prozent:** 107% (sehr gut)
- **Laden:** `false`
- **Min/Max:** 7.84V / 9.1V

## 🏗️ HBW (Hochregallager) Speicherung

### **Lagerstruktur**
```
A1: R1 (Rot)     A2: Leer     A3: Leer
B1: W1 (Weiß)    B2: Leer     B3: Leer
C1: B1 (Blau)    C2: Leer     C3: Leer
```

### **Workpiece Mapping**
| Position | Workpiece-ID (NFC-Code) | Friendly-ID | Farbe |
|----------|-------------------------|-------------|-------|
| `A1` | `040a8dca341291` | `R1` | `RED` |
| `B1` | `04798eca341290` | `W1` | `WHITE` |
| `C1` | `047389ca341291` | `B1` | `BLUE` |

### **Vollständiges NFC-Workpiece Mapping**

**⚠️ Wichtig:** In MQTT-Nachrichten wird immer der NFC-Code als Workpiece-ID verwendet, niemals die Friendly-ID!

| Friendly-ID | Workpiece-ID (NFC-Code) | Farbe |
|-------------|-------------------------|-------|
| **R1** | `040a8dca341291` | Rot |
| **R2** | `04d78cca341290` | Rot |
| **R3** | `04808dca341291` | Rot |
| **R4** | `04f08dca341290` | Rot |
| **R5** | `04158cca341291` | Rot |
| **R6** | `04fa8cca341290` | Rot |
| **R7** | `047f8cca341290` | Rot |
| **R8** | `048a8cca341290` | Rot |
| **W1** | `04798eca341290` | Weiß |
| **W2** | `047c8bca341291` | Weiß |
| **W3** | `047b8bca341291` | Weiß |
| **W4** | `04c38bca341290` | Weiß |
| **W5** | `04ab8bca341290` | Weiß |
| **W6** | `04368bca341291` | Weiß |
| **W7** | `04c090ca341290` | Weiß |
| **W8** | `042c8aca341291` | Weiß |
| **B1** | `04a189ca341290` | Blau |
| **B2** | `048989ca341290` | Blau |
| **B3** | `047389ca341291` | Blau |
| **B4** | `040c89ca341291` | Blau |
| **B5** | `04a289ca341290` | Blau |
| **B6** | `04c489ca341290` | Blau |
| **B7** | `048089ca341290` | Blau |
| **B8** | `042c88ca341291` | Blau |

### **HBW State**
```json
{
  "loads": [
    {
      "loadType": "RED",
      "loadId": "040a8dca341291",
      "loadPosition": "A1",
      "loadTimestamp": 1755593140416
    },
    {
      "loadType": "WHITE",
      "loadId": "04798eca341290",
      "loadPosition": "B1",
      "loadTimestamp": 1755593289564
    },
    {
      "loadType": "BLUE",
      "loadId": "047389ca341291",
      "loadPosition": "C1",
      "loadTimestamp": 1755593429137
    }
  ],
  "actionState": {
    "command": "PICK",
    "state": "FINISHED"
  }
}
```

## 📊 Status-Management

### **Module Status**
- **READY:** Modul bereit für neue Orders
- **BUSY:** Modul verarbeitet aktuellen Order
- **ERROR:** Fehlerzustand (erfordert Reset)

### **Action States**
- **WAITING:** Aktion wartet auf Ausführung
- **RUNNING:** Aktion wird ausgeführt
- **FINISHED:** Aktion erfolgreich abgeschlossen
- **FAILED:** Aktion fehlgeschlagen

### **LED Status (DPS)**
- **Grün:** Bereit für neue Werkstücke
- **Gelb:** Verarbeitung läuft
- **Rot:** Fehlerzustand

## 💾 Persistierung

### **CCU Stock State**
```json
{
  "stockItems": [
    {
      "workpiece": {
        "id": "047389ca341291",
        "type": "BLUE",
        "state": "RAW"
      },
      "location": "C1",
      "hbw": "SVR3QA0022"
    }
  ]
}
```

### **Persistierungsebenen**
1. **CCU:** Globaler Stock-State (überlebt Neustarts)
2. **HBW:** Lokale Position-Mapping
3. **FTS:** Temporäre Load-Informationen

## ⏱️ Timing-Analyse

### **Workflow-Zeitlinie**
```
10:49:53 - Order erstellt (CCU)
10:50:03 - FTS Navigation zu DPS (10s)
10:50:18 - DPS DROP abgeschlossen (15s)
10:50:18 - FTS Navigation zu HBW (11s)
10:50:29 - HBW PICK gestartet
10:50:47 - HBW PICK abgeschlossen (18s)
10:50:47 - Order completed
```

### **Gesamtdauer:** ~54 Sekunden

## 🔧 Technische Details

### **MQTT Topics**
- `module/v1/ff/SVR4H73275/state` - DPS Status
- `module/v1/ff/SVR3QA0022/state` - HBW Status
- `fts/v1/ff/5iO4/state` - FTS Status
- `ccu/order/active` - Aktive Orders
- `ccu/pairing/state` - Module-Verbindungen

### **Dependent Actions**
- **Action-ID:** `bd0ad42d-7550-4f2b-8b65-d74992f406fc`
- **Dependency:** `60a787e9-6579-47d3-8487-b6024e7d42db`
- **Kette:** Navigation → Manufacture → Navigation → Manufacture

### **Error Handling**
- **Module Errors:** Über `errors` Array in State
- **FTS Errors:** Battery, Navigation, Load Handling
- **HBW Errors:** Position, Pick/Drop Operationen

## 🎯 Dashboard Integration

### **Friendly Names**
- **Workpiece-IDs:** `047389ca341291` → `B1`
- **Module-IDs:** `SVR3QA0022` → `HBW`
- **Order-Types:** `STORAGE` → `Wareneingang`

### **Status-Anzeige**
- **Real-time:** Module-Status über MQTT
- **Stock-Overview:** Verfügbare Werkstücke
- **Order-Tracking:** Aktive und abgeschlossene Orders

## 📝 Zusammenfassung

Der Wareneingang-Workflow ist ein hochautomatisierter Prozess, der durch die CCU orchestriert wird. Das System verwendet eine VDA 5050 kompatible State Machine und bietet umfassende Persistierung und Status-Überwachung. Die Integration von friendly IDs im Dashboard verbessert die Benutzerfreundlichkeit erheblich.

### **Schlüsselkomponenten:**
1. **CCU:** Zentrale Orchestrierung
2. **DPS:** Werkstück-Erkennung und -Aufnahme
3. **FTS:** Automatisierter Transport
4. **HBW:** Intelligente Lagerung
5. **MQTT:** Kommunikationsprotokoll
6. **Dashboard:** Benutzerfreundliche Visualisierung
