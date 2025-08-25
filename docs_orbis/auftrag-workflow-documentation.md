# Auftrags-Workflow Dokumentation

## 🎯 Übersicht

Dieses Dokument beschreibt den vollständigen Auftrags-Workflow (Produktions-Workflow) der ORBIS-Modellfabrik basierend auf der Analyse von MQTT-Sessions. Der Workflow wird durch eine Bestellung über das Fischertechnik-Dashboard ausgelöst und führt zur vollständigen Produktion und Auslieferung von Werkstücken.

## 🔄 Workflow-Sequenz (Happy Path)

### **1. Auftrag-Auslösung (Fischertechnik Dashboard)**
- **Trigger:** Bestellung über Web-Interface
- **Topic:** `/j1/txt/1/f/o/order`
- **Order-Type:** `PRODUCTION`
- **Voraussetzung:** Werkstücke müssen im HBW verfügbar sein

### **2. HBW PICK nach FIFO-Prinzip**
- **Modul:** HBW (Hochregallager)
- **Prinzip:** First-In-First-Out (älteste Werkstücke zuerst)
- **Befehl:** `PICK` mit `orderId` und `workpieceId`
- **Position:** Automatische Auswahl der nächsten freien Position

### **3. FTS Transport zu Produktions-Modulen**
- **Route:** HBW → Produktions-Module (DRILL/MILL)
- **Navigation:** Automatische Routenplanung
- **Load Handling:** Koordinierte Übergabe an Module
- **Transport-Zeit:** ~2-3 Minuten pro Werkstück

### **4. Produktions-Module Verarbeitung**
- **Weiße Werkstücke:** DRILL (Bohren)
- **Rote Werkstücke:** MILL (Fräsen)
- **Blaue Werkstücke:** DRILL + MILL (Bohren + Fräsen)
- **Parallele Verarbeitung:** Freie Module werden automatisch angesteuert

### **5. AIQS Qualitätsprüfung**
- **Modul:** AIQS (Qualitätsprüfung)
- **Prüfung:** Automatische Qualitätskontrolle
- **Ergebnis:** OK/NOT-OK Entscheidung
- **Happy Path:** Nur OK-Werkstücke werden weiterverarbeitet

### **6. DPS Warenausgang**
- **Modul:** DPS (Delivery and Pickup Station)
- **NFC-Lesung:** Werkstück-Identifikation
- **6-Arm-Roboter:** Automatischer Transport zum Warenausgang
- **Order-Abschluss:** Prozess erfolgreich beendet

## 🏭 Modul-Mapping

| Modul-ID | Friendly Name | Funktion | IP-Adresse |
|----------|---------------|----------|------------|
| `SVR3QA0022` | **HBW** | Hochregallager | `192.168.0.80` |
| `SVR4H76449` | **DRILL** | Bohrer | `192.168.0.50` |
| `SVR3QA2098` | **MILL** | Fräse | `192.168.0.40` |
| `SVR4H76530` | **AIQS** | Qualitätsprüfung | `192.168.0.70` |
| `SVR4H73275` | **DPS** | Delivery and Pickup Station | `192.168.0.90` |
| `5iO4` | **FTS** | Fahrerloses Transportsystem | `192.168.0.104` |
| `CHRG0` | **CHARGING** | Ladestation | - |

## 📋 Order-Management

### **Order-Triggering**

#### **Dashboard-Bestellung (APS Dashboard):**
```json
{
  "orderType": "PRODUCTION",
  "type": "BLUE",
  "workpieceId": "047389ca341291",
  "timestamp": "2024-01-18T10:49:53.123Z"
}
```

#### **Fischertechnik Dashboard:**
```json
{
  "orderType": "PRODUCTION", 
  "type": "BLUE",
  "workpieceId": "047389ca341291",
  "timestamp": "2024-01-18T10:49:53.123Z"
}
```

**Topic:** `/j1/txt/1/f/o/order` (identisch für beide Dashboards)

**⚠️ Wichtig:** 
- **Order-IDs werden NICHT im Trigger vergeben** (werden von der CCU erstellt)
- **Action-IDs werden NICHT im Trigger vergeben** (werden von der CCU erstellt)
- **Dependent Action IDs werden von der CCU verwaltet**

### **Production Steps**
```json
{
  "orderType": "PRODUCTION",
  "type": "BLUE",
  "workpieceId": "047389ca341291",
  "productionSteps": [
    {
      "type": "NAVIGATION",
      "source": "HBW",
      "target": "DRILL",
      "state": "FINISHED"
    },
    {
      "type": "MANUFACTURE",
      "command": "DRILL",
      "moduleType": "DRILL",
      "state": "FINISHED"
    },
    {
      "type": "NAVIGATION",
      "source": "DRILL",
      "target": "MILL",
      "state": "FINISHED"
    },
    {
      "type": "MANUFACTURE",
      "command": "MILL",
      "moduleType": "MILL",
      "state": "FINISHED"
    },
    {
      "type": "NAVIGATION",
      "source": "MILL",
      "target": "AIQS",
      "state": "FINISHED"
    },
    {
      "type": "MANUFACTURE",
      "command": "QUALITY",
      "moduleType": "AIQS",
      "state": "FINISHED"
    },
    {
      "type": "NAVIGATION",
      "source": "AIQS",
      "target": "DPS",
      "state": "FINISHED"
    },
    {
      "type": "MANUFACTURE",
      "command": "DROP",
      "moduleType": "DPS",
      "state": "FINISHED"
    }
  ]
}
```

## 🎛️ CCU (Central Control Unit) Orchestrierung

### **Zentrale Rolle**
- **Orchestrator:** CCU koordiniert alle Produktionsschritte
- **Order Management:** Erstellt und verwaltet Production Orders
- **Module Coordination:** Steuert parallele Verarbeitung
- **Status Monitoring:** Überwacht alle Module-Status

### **CCU Topics**
- `ccu/order/active` - Aktive Production Orders
- `ccu/order/completed` - Abgeschlossene Orders
- `ccu/pairing/state` - Module-Verbindungsstatus
- `ccu/state/stock` - Lagerbestand

### **Production Order Management**
```json
{
  "activeOrders": [
    {
      "orderId": "7752923a-5d49-4ba4-8429-943e6581ef62",
      "orderType": "PRODUCTION",
      "workpieceId": "047389ca341291",
      "type": "BLUE",
      "status": "RUNNING",
      "currentStep": 3,
      "totalSteps": 8
    }
  ]
}
```

## 🏗️ HBW (Hochregallager) FIFO-Prinzip

### **FIFO-Logik**
- **Prinzip:** First-In-First-Out
- **Auswahl:** Älteste Werkstücke werden zuerst verarbeitet
- **Position:** Automatische Auswahl der nächsten freien Position
- **Tracking:** Vollständige Verfolgung der Einlagerungsreihenfolge

### **HBW PICK Command**
```json
{
  "serialNumber": "SVR3QA0022",
  "orderId": "7752923a-5d49-4ba4-8429-943e6581ef62",
  "orderUpdateId": 1,
  "action": {
    "id": "bd0ad42d-7550-4f2b-8b65-d74992f406fc",
    "command": "PICK",
    "metadata": {
      "workpiece": {
        "workpieceId": "047389ca341291",
        "type": "BLUE",
        "position": "C1"
      }
    }
  }
}
```

### **HBW State nach PICK**
```json
{
  "loads": [
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

## 🚗 FTS (Fahrerloses Transportsystem) Transport

### **Transport-Routen**
- **HBW → DRILL:** Für weiße und blaue Werkstücke
- **HBW → MILL:** Für rote und blaue Werkstücke
- **DRILL → MILL:** Für blaue Werkstücke (Sequenz)
- **MILL → AIQS:** Für alle Werkstücke
- **AIQS → DPS:** Für alle Werkstücke

### **Navigation Commands**
```json
{
  "type": "NAVIGATION",
  "source": "HBW",
  "target": "DRILL",
  "state": "RUNNING",
  "route": ["HBW", "Node1", "Node2", "DRILL"]
}
```

### **Load Handling**
```json
{
  "load": [
    {
      "loadPosition": "1",
      "loadId": "047389ca341291",
      "loadType": "BLUE"
    }
  ],
  "driving": true,
  "waitingForLoadHandling": false
}
```

## 🏭 Produktions-Module

### **DRILL (Bohrer)**
- **Modul-ID:** `SVR4H76449`
- **Verarbeitung:** Weiße und blaue Werkstücke
- **Befehl:** `DRILL`
- **Dauer:** ~30-60 Sekunden

### **MILL (Fräse)**
- **Modul-ID:** `SVR3QA2098`
- **Verarbeitung:** Rote und blaue Werkstücke
- **Befehl:** `MILL`
- **Dauer:** ~45-90 Sekunden

### **Parallele Verarbeitung**
- **Freie Module:** Automatische Ansteuerung
- **Load Balancing:** Gleichmäßige Verteilung
- **Status Monitoring:** Real-time Überwachung

### **Module Commands**
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "7752923a-5d49-4ba4-8429-943e6581ef62",
  "orderUpdateId": 1,
  "action": {
    "id": "bd0ad42d-7550-4f2b-8b65-d74992f406fc",
    "command": "DRILL",
    "metadata": {
      "workpiece": {
        "workpieceId": "047389ca341291",
        "type": "BLUE"
      }
    }
  }
}
```

## 🔍 AIQS (Qualitätsprüfung)

### **Qualitätsprüfung**
- **Modul-ID:** `SVR4H76530`
- **Prüfung:** Automatische Qualitätskontrolle
- **Befehl:** `QUALITY`
- **Ergebnis:** OK/NOT-OK

### **Quality Check Command**
```json
{
  "serialNumber": "SVR4H76530",
  "orderId": "7752923a-5d49-4ba4-8429-943e6581ef62",
  "orderUpdateId": 1,
  "action": {
    "id": "bd0ad42d-7550-4f2b-8b65-d74992f406fc",
    "command": "QUALITY",
    "metadata": {
      "workpiece": {
        "workpieceId": "047389ca341291",
        "type": "BLUE"
      }
    }
  }
}
```

### **Qualitätsergebnis**
```json
{
  "qualityResult": "OK",
  "workpieceId": "047389ca341291",
  "timestamp": "2024-01-18T10:55:23.456Z",
  "details": {
    "measurements": {...},
    "tolerance": "within_spec"
  }
}
```

## 📤 DPS (Delivery and Pickup Station) Warenausgang

### **Warenausgang-Prozess**
- **NFC-Lesung:** Werkstück-Identifikation
- **6-Arm-Roboter:** Automatischer Transport
- **DROP Command:** Werkstück wird abgelegt
- **Order Completion:** Prozess erfolgreich beendet

### **DROP Command**
```json
{
  "serialNumber": "SVR4H73275",
  "orderId": "7752923a-5d49-4ba4-8429-943e6581ef62",
  "orderUpdateId": 1,
  "action": {
    "id": "bd0ad42d-7550-4f2b-8b65-d74992f406fc",
    "command": "DROP",
    "metadata": {
      "workpiece": {
        "workpieceId": "047389ca341291",
        "type": "BLUE"
      }
    }
  }
}
```

### **NFC-Lesung**
```json
{
  "nfcCode": "047389ca341291",
  "workpieceType": "BLUE",
  "timestamp": "2024-01-18T10:56:45.789Z",
  "location": "DPS_WARENAUSGANG"
}
```

## 📊 Status-Management

### **Module Status**
- **READY:** Modul bereit für neue Orders
- **BUSY:** Modul verarbeitet aktuellen Order
- **ERROR:** Fehlerzustand (erfordert Reset)
- **OFFLINE:** Modul nicht verbunden

### **Action States**
- **WAITING:** Aktion wartet auf Ausführung
- **RUNNING:** Aktion wird ausgeführt
- **FINISHED:** Aktion erfolgreich abgeschlossen
- **FAILED:** Aktion fehlgeschlagen

### **Order States**
- **PENDING:** Order wartet auf Ausführung
- **RUNNING:** Order wird verarbeitet
- **COMPLETED:** Order erfolgreich abgeschlossen
- **FAILED:** Order fehlgeschlagen

## ⏱️ Timing-Analyse

### **Workflow-Zeitlinie (Beispiel: auftrag-B1B2B3)**
```
10:49:53 - Order erstellt (Browser)
10:50:03 - HBW PICK gestartet (10s)
10:50:18 - HBW PICK abgeschlossen (15s)
10:50:18 - FTS Transport zu DRILL (11s)
10:50:29 - DRILL Verarbeitung gestartet
10:51:15 - DRILL Verarbeitung abgeschlossen (46s)
10:51:15 - FTS Transport zu MILL (11s)
10:51:26 - MILL Verarbeitung gestartet
10:52:45 - MILL Verarbeitung abgeschlossen (79s)
10:52:45 - FTS Transport zu AIQS (11s)
10:52:56 - AIQS Qualitätsprüfung gestartet
10:53:23 - AIQS Qualitätsprüfung abgeschlossen (27s)
10:53:23 - FTS Transport zu DPS (11s)
10:53:34 - DPS DROP abgeschlossen (11s)
10:53:34 - Order completed
```

### **Gesamtdauer:** ~3 Minuten 41 Sekunden

## 🔧 Technische Details

### **MQTT Topics**
- `/j1/txt/1/f/o/order` - Browser Order Trigger
- `ccu/order/active` - Aktive Orders
- `ccu/order/completed` - Abgeschlossene Orders
- `module/v1/ff/SVR3QA0022/order` - HBW Commands
- `module/v1/ff/SVR4H76449/order` - DRILL Commands
- `module/v1/ff/SVR3QA2098/order` - MILL Commands
- `module/v1/ff/SVR4H76530/order` - AIQS Commands
- `module/v1/ff/SVR4H73275/order` - DPS Commands
- `fts/v1/ff/5iO4/order` - FTS Commands

### **Dependent Actions**
- **Action-ID:** `bd0ad42d-7550-4f2b-8b65-d74992f406fc`
- **Dependency:** `60a787e9-6579-47d3-8487-b6024e7d42db`
- **Kette:** Navigation → Manufacture → Navigation → Manufacture

### **ID-Vergabe System:**
- **Order-IDs:** Werden von der CCU vergeben (UUID v4)
- **Action-IDs:** Werden von der CCU vergeben (UUID v4)
- **Dependent Action IDs:** Werden von der CCU verwaltet
- **Browser Trigger:** Enthält nur `orderType`, `type`, `workpieceId`, `timestamp`

### **Parallel Processing**
- **Mehrere Orders:** Gleichzeitige Verarbeitung möglich
- **Module Availability:** Freie Module werden automatisch angesteuert
- **Load Balancing:** Intelligente Verteilung der Workload

## 🎯 Dashboard Integration

### **Friendly Names**
- **Workpiece-IDs:** `047389ca341291` → `B1`
- **Module-IDs:** `SVR3QA0022` → `HBW`
- **Order-Types:** `PRODUCTION` → `Produktion`

### **Status-Anzeige**
- **Real-time:** Module-Status über MQTT
- **Order-Tracking:** Aktive und abgeschlossene Orders
- **Production Progress:** Fortschritt der Produktionsschritte

## 📝 Zusammenfassung

Der Auftrags-Workflow ist ein hochautomatisierter Produktionsprozess, der durch die CCU orchestriert wird. Das System verwendet eine VDA 5050 kompatible State Machine und bietet umfassende Persistierung und Status-Überwachung. Die Integration von friendly IDs im Dashboard verbessert die Benutzerfreundlichkeit erheblich.

### **Schlüsselkomponenten:**
1. **CCU:** Zentrale Orchestrierung
2. **HBW:** FIFO-basierte Werkstück-Auswahl
3. **FTS:** Automatisierter Transport
4. **DRILL/MILL:** Produktions-Module
5. **AIQS:** Qualitätsprüfung
6. **DPS:** Warenausgang
7. **MQTT:** Kommunikationsprotokoll
8. **Dashboard:** Benutzerfreundliche Visualisierung

### **Produktionsplan:**
- **⚪ Weiße Werkstücke:** HBW → DRILL → AIQS → DPS
- **🔴 Rote Werkstücke:** HBW → MILL → AIQS → DPS
- **🔵 Blaue Werkstücke:** HBW → DRILL → MILL → AIQS → DPS
