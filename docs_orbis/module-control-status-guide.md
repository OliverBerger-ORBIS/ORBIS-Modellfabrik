# Module Control & Status Management Guide

## Übersicht
Dieses Dokument beschreibt die aktuellen Erkenntnisse und offenen Fragen zur Steuerung und Status-Abfrage der APS-Module.

## 🎯 Implementierte Features

### ✅ Bestellung-System
- **Browser Order Format:** MQTT Topic `/j1/txt/1/f/o/order`
- **Payload:** `{"type": "COLOR", "ts": "timestamp"}`
- **Dashboard Integration:** Bestellung-Trigger und Bestellung mit HBW-Status
- **Orchestrierung:** CCU koordiniert automatisch alle Module

### ✅ FTS Control (Grundfunktionen)
- **Befehle:** "Docke an", "FTS laden", "Laden beenden"
- **Dashboard Integration:** FTS Control im MQTT-Control Tab
- **MQTT Topics:** `fts/v1/ff/5iO4/instantAction`

## ⚠️ Offene Fragen & To-Do

### 1. HBW Status Management
**Problem:** Wie liest man den Status des HBW aus?

**Fragen:**
- Welche MQTT-Topics für HBW Status-Abfrage?
- Wie werden Werkstück-Positionen abgefragt?
- Welche Parameter in den Status-Nachrichten?

**Vermutete Topics:**
- `module/v1/ff/SVR3QA2098/state` (HBW State)
- `module/v1/ff/SVR3QA2098/factsheet` (HBW Factsheet)

**Benötigte Informationen:**
- Verfügbare Werkstücke (R1-R8, W1-W8, B1-B8)
- Positionen im HBW (B1, B2, B3, etc.)
- Status der einzelnen Plätze

### 2. DPS Status Management
**Problem:** Wie liest man den Status der DPS (Warenein- und -ausgang) aus?

**Fragen:**
- Welche MQTT-Topics für DPS Status?
- Wie werden verfügbare Plätze abgefragt?
- Welche Werkstücke sind aktuell in der DPS?

**Vermutete Topics:**
- `module/v1/ff/SVR4H73275/state` (DPS State)
- `module/v1/ff/SVR4H73275/factsheet` (DPS Factsheet)

**Benötigte Informationen:**
- Verfügbare Ein-/Ausgangsplätze
- Aktuelle Werkstücke in der DPS
- Status der Transportwege

### 3. FTS Navigation
**Problem:** Wie wird die nächste Station bestimmt?

**Fragen:**
- Wie wird die Zielstation für FTS bestimmt?
- Welche Parameter für Navigation?
- Wie funktioniert die Routenplanung?

**Aktuelle Erkenntnisse:**
- FTS wird über CCU gesteuert, nicht direkt über MQTT
- "Docke an" ist Initialisierungsbefehl
- "FTS laden" und "Laden beenden" funktionieren

**Offene Fragen:**
- Wie wird die Zielstation angegeben?
- Welche Stationen sind verfügbar?
- Wie funktioniert die automatische Routenplanung?

## 🔧 Technische Details

### MQTT Message Format
```json
{
  "type": "COLOR",
  "ts": "2024-01-01T12:00:00.000Z"
}
```

### Module Topics
- **HBW:** `module/v1/ff/SVR3QA2098/`
- **MILL:** `module/v1/ff/SVR4H76449/`
- **DRILL:** `module/v1/ff/SVR4H76530/`
- **AIQS:** `module/v1/ff/SVR3QA0022/`
- **DPS:** `module/v1/ff/SVR4H73275/`
- **FTS:** `module/v1/ff/5iO4/`
- **OVEN:** `module/v1/ff/CHRG0/`

### Status-Abfrage Parameter
**Noch zu ermitteln:**
- Welche Parameter für Status-Abfrage?
- Welche Response-Formate?
- Wie werden Werkstück-IDs codiert?

## 📋 Nächste Schritte

### Priorität 1: HBW Status
1. MQTT-Topics für HBW Status identifizieren
2. Response-Format analysieren
3. Werkstück-Position Mapping implementieren

### Priorität 2: DPS Status
1. MQTT-Topics für DPS Status identifizieren
2. Verfügbarkeitsprüfung implementieren
3. Status-Integration in Dashboard

### Priorität 3: FTS Navigation
1. Navigation-Parameter identifizieren
2. Routenplanung verstehen
3. Zielstation-Bestimmung implementieren

## 🔍 Analyse-Methoden

### Session Recording
```bash
python src_orbis/mqtt/loggers/aps_session_logger.py --session-label hbw_status_test --process-type custom --auto-start
```

### MQTT Analysis
- APS Analyse Tab im Dashboard
- Topic-Filter für Module-spezifische Nachrichten
- Payload-Analyse für Status-Formate

### Manual Testing
- Einzelne Module-Befehle testen
- Status-Abfragen über Dashboard
- Response-Analyse in Echtzeit

## 📚 Referenzen

- [Factory Reset and Order Trigger Guide](factory-reset-and-order-trigger.md)
- [Fischertechnik Web Interface Analysis](fischertechnik-web-interface-analysis.md)
- [Project Status](project-status.md)
- [MQTT Message Library](mqtt-message-library-migration.md)
