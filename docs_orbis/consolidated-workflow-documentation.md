# Konsolidierte Workflow-Dokumentation

## 🎯 Übersicht

Diese konsolidierte Dokumentation fasst alle wichtigen Informationen zu den ORBIS-Modellfabrik Workflows zusammen und ersetzt mehrere separate Dokumentationen.

## 🔄 Workflow-Übersicht

### **1. Wareneingang-Workflow**
- **Trigger:** Werkstück in DPS ablegen
- **Ziel:** Werkstück ins HBW einlagern
- **Dauer:** ~54 Sekunden
- **Order-Type:** `STORAGE`

### **2. Auftrags-Workflow (Produktion)**
- **Trigger:** Bestellung über Dashboard
- **Ziel:** Werkstück produzieren und ausliefern
- **Dauer:** ~3-4 Minuten
- **Order-Type:** `PRODUCTION`

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

## 🏷️ Workpiece-Mapping

### **NFC-Code → Friendly-ID Schema**

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

**⚠️ Wichtig:** In MQTT-Nachrichten wird immer der NFC-Code als Workpiece-ID verwendet, niemals die Friendly-ID!

## 📋 Order-Management

### **Order-Triggering (Dashboard)**

#### **APS Dashboard Bestellung:**
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

## 🎛️ ID-Management System

### **ID-Typen**

#### **1. Order-ID**
- **Format:** UUID v4 (z.B. `7752923a-5d49-4ba4-8429-943e6581ef62`)
- **Vergabe:** CCU (Central Control Unit)
- **Verwendung:** Identifiziert einen kompletten Produktionsauftrag

#### **2. Action-ID**
- **Format:** UUID v4 (z.B. `bd0ad42d-7550-4f2b-8b65-d74992f406fc`)
- **Vergabe:** CCU (Central Control Unit)
- **Verwendung:** Identifiziert eine einzelne Aktion innerhalb eines Orders

#### **3. Dependent Action ID**
- **Format:** UUID v4 (z.B. `60a787e9-6579-47d3-8487-b6024e7d42db`)
- **Vergabe:** CCU (Central Control Unit)
- **Verwendung:** Verknüpft Actions in einer Abhängigkeitskette

### **ID-Vergabe Prozess**
```
1. Browser Trigger → CCU
2. CCU erstellt Order-ID
3. CCU erstellt Action-IDs für alle Schritte
4. CCU verknüpft Actions mit Dependencies
5. CCU sendet Commands an Module
```

### **Order-ID Lebenszyklus**
- **Wareneingang:** Jeder Wareneingang erhält eine eigene Order-ID
- **Auftrag:** Jeder Auftrag erhält eine neue Order-ID (NICHT die vom Wareneingang)
- **HBW Storage:** Order-IDs werden NICHT im HBW gespeichert
- **Verknüpfung:** Nur über Werkstück-IDs (NFC-Codes) verknüpft

## 🏗️ Wareneingang-Workflow

### **Workflow-Sequenz**
1. **Werkstück-Erkennung (DPS)** - Lichtschranke + 6-Armroboter + NFC
2. **HBW-Platzprüfung** - Verfügbarkeit für Farbe
3. **FTS-Transport** - Route: DPS → Node 2 → Node 1 → HBW
4. **HBW-Einlagerung** - PICK + Persistierung

### **Timing-Analyse**
```
10:49:53 - Order erstellt (CCU)
10:50:03 - FTS Navigation zu DPS (10s)
10:50:18 - DPS DROP abgeschlossen (15s)
10:50:18 - FTS Navigation zu HBW (11s)
10:50:29 - HBW PICK gestartet
10:50:47 - HBW PICK abgeschlossen (18s)
10:50:47 - Order completed
```

**Gesamtdauer:** ~54 Sekunden

## 🏭 Auftrags-Workflow (Produktion)

### **Workflow-Sequenz**
1. **Auftrag-Auslösung** - Bestellung über Dashboard
2. **HBW PICK nach FIFO** - Älteste Werkstücke zuerst
3. **FTS Transport** - Zu Produktions-Modulen
4. **Produktions-Module** - DRILL/MILL Verarbeitung
5. **AIQS Qualitätsprüfung** - Automatische Kontrolle
6. **DPS Warenausgang** - NFC-Lesung + 6-Arm-Roboter

### **Produktionsplan**
- **⚪ Weiße Werkstücke:** HBW → DRILL → AIQS → DPS
- **🔴 Rote Werkstücke:** HBW → MILL → AIQS → DPS
- **🔵 Blaue Werkstücke:** HBW → DRILL → MILL → AIQS → DPS

### **Timing-Analyse**
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

**Gesamtdauer:** ~3 Minuten 41 Sekunden

## 🚗 FTS (Fahrerloses Transportsystem)

### **FTS Control**
- **"Docke an"** - Initialisierung (findInitialDockPosition)
- **"FTS laden"** - Ladestation anfahren (startCharging)
- **"Laden beenden"** - Ladung stoppen (stopCharging)
- **"Status abfragen"** - Aktuellen Status prüfen

### **Navigation-Routen**
- **HBW → DRILL:** Für weiße und blaue Werkstücke
- **HBW → MILL:** Für rote und blaue Werkstücke
- **DRILL → MILL:** Für blaue Werkstücke (Sequenz)
- **MILL → AIQS:** Für alle Werkstücke
- **AIQS → DPS:** Für alle Werkstücke

## 📊 Status-Management

### **Module Status**
| Technischer Status | Friendly Status | Bedeutung |
|-------------------|-----------------|-----------|
| `READY` | **Bereit** | Modul bereit für neue Orders |
| `BUSY` | **Beschäftigt** | Modul verarbeitet aktuellen Order |
| `ERROR` | **Fehler** | Fehlerzustand (erfordert Reset) |
| `OFFLINE` | **Offline** | Modul nicht verbunden |

### **Action States**
| Technischer Status | Friendly Status | Bedeutung |
|-------------------|-----------------|-----------|
| `WAITING` | **Wartend** | Aktion wartet auf Ausführung |
| `RUNNING` | **Läuft** | Aktion wird ausgeführt |
| `FINISHED` | **Abgeschlossen** | Aktion erfolgreich beendet |
| `FAILED` | **Fehlgeschlagen** | Aktion fehlgeschlagen |

### **Order States**
| Technischer Status | Friendly Status | Bedeutung |
|-------------------|-----------------|-----------|
| `PENDING` | **Wartend** | Order wartet auf Ausführung |
| `RUNNING` | **Läuft** | Order wird verarbeitet |
| `COMPLETED` | **Abgeschlossen** | Order erfolgreich abgeschlossen |
| `FAILED` | **Fehlgeschlagen** | Order fehlgeschlagen |

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

### **Module Commands**
- `PICK` - Werkstück aufnehmen
- `DROP` - Werkstück ablegen
- `DRILL` - Bohrer-Verarbeitung
- `MILL` - Fräser-Verarbeitung
- `QUALITY` - Qualitätsprüfung
- `NAVIGATION` - FTS Navigation

## 🎯 Dashboard Integration

### **Friendly Names**
- **Workpiece-IDs:** `047389ca341291` → `B1`
- **Module-IDs:** `SVR3QA2098` → `HBW`
- **Order-Types:** `STORAGE` → `Wareneingang`, `PRODUCTION` → `Produktion`

### **Status-Anzeige**
- **Real-time:** Module-Status über MQTT
- **Stock-Overview:** Verfügbare Werkstücke
- **Order-Tracking:** Aktive und abgeschlossene Orders
- **Production Progress:** Fortschritt der Produktionsschritte

## 📝 Zusammenfassung

### **Schlüsselkomponenten:**
1. **CCU:** Zentrale Orchestrierung und ID-Management
2. **HBW:** FIFO-basierte Werkstück-Auswahl
3. **FTS:** Automatisierter Transport
4. **DRILL/MILL:** Produktions-Module
5. **AIQS:** Qualitätsprüfung
6. **DPS:** Warenein- und -ausgang
7. **MQTT:** Kommunikationsprotokoll
8. **Dashboard:** Benutzerfreundliche Visualisierung

### **Wichtige Erkenntnisse:**
- **CCU ist zentraler Orchestrator:** Alle IDs werden von der CCU vergeben
- **Browser Trigger ohne IDs:** Nur `orderType`, `type`, `workpieceId`, `timestamp`
- **NFC-Codes direkt verwenden:** Workpiece-ID = NFC-Code in MQTT-Nachrichten
- **FIFO-Prinzip:** Älteste Werkstücke werden zuerst verarbeitet
- **Parallele Verarbeitung:** Mehrere Orders gleichzeitig möglich
- **Vollständige Verfolgung:** Jede Aktion hat eine eindeutige ID

### **Order-ID Wiederverwendung:**
- **❌ Order-IDs werden NICHT wiederverwendet** - Jeder Workflow erhält eine neue Order-ID
- **📥 Wareneingang:** Eigene Order-ID für Storage-Workflow
- **📤 Auftrag:** Neue Order-ID für Production-Workflow
- **🏗️ HBW Storage:** Order-IDs werden NICHT im HBW gespeichert
- **🔗 Verknüpfung:** Nur über Werkstück-IDs (NFC-Codes) verknüpft
- **📊 Analyse-Ergebnis:** 0 wiederverwendete Order-IDs zwischen Wareneingang und Aufträgen

### **Vorteile der Konsolidierung:**
- **Zentrale Dokumentation:** Alle wichtigen Informationen an einem Ort
- **Reduzierte Redundanz:** Keine doppelten Informationen
- **Bessere Übersicht:** Klare Struktur und Navigation
- **Einfachere Wartung:** Weniger Dateien zu aktualisieren
- **Konsistente Informationen:** Einheitliche Darstellung aller Workflows
