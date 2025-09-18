# DPS TXT Controller Analyse - Plan

## 🎯 Ziel
Analyse des DPS TXT Controllers (192.168.0.102) für:
- Order-ID-Management
- MQTT-Kommunikation
- Prozesssteuerung (Warenein- und -ausgang)

## 📋 Vorgehensweise

### Phase 1: Browser-Interface erkunden
- **URL:** `http://192.168.0.102`
- **Login:** `ft` / `fischertechnik`
- **Hauptordner:** `FF_DPS_24V`

### Phase 2: Dateien identifizieren
- **`.project.json`** - Konfiguration (121 Bytes)
- **`FF_DPS_24V.py`** - Haupt-Script (5.96 KB)
- **`data/`** - Verzeichnis (Logs und Daten)
- **`lib/`** - Verzeichnis (Bibliotheken)

### Phase 3: Inhalte analysieren
- **Konfiguration** - MQTT-Settings, Order-ID-Settings
- **Python-Script** - Order-ID-Logik, MQTT-Kommunikation
- **Daten-Verzeichnis** - Logs, Order-Daten

### Phase 4: Dokumentation erstellen
- **DPS-Architektur** - Komponenten und Funktionen
- **Order-ID-Management** - Wie werden Order-IDs verwaltet?
- **MQTT-Integration** - Topics, Publisher/Subscriber
- **Prozess-Flow** - Warenein-/ausgang, Bestellungen

## 🔍 Erwartete Erkenntnisse

### Order-ID-Management
- Wie werden Order-IDs generiert?
- Wo werden sie gespeichert?
- Wie werden sie an andere Komponenten übertragen?

### MQTT-Kommunikation
- Welche Topics werden verwendet?
- Publisher oder Subscriber?
- Client-ID und Konfiguration

### Prozesssteuerung
- Warenein- und -ausgang
- Bestellungsverwaltung
- Integration mit anderen TXT-Controllern

## 📁 Dateien-Struktur

```
docs/analysis/dps/
├── DPS_ANALYSIS_PLAN.md          # Dieser Plan
├── DPS_ARCHITECTURE.md           # Architektur-Übersicht
├── DPS_ORDER_MANAGEMENT.md       # Order-ID-Management
├── DPS_MQTT_INTEGRATION.md       # MQTT-Integration
└── DPS_PROCESS_FLOW.md           # Prozess-Flow
```

## ⚠️ Herausforderungen

### Browser-Interface
- **Keine Download-Funktion** - Inhalte müssen manuell kopiert werden
- **Screenshot-Analyse** - Bilder für Dokumentation
- **Text-Extraktion** - Code und Konfiguration manuell übertragen

### Analyse-Methoden
- **Code-Review** - Python-Script analysieren
- **Konfiguration** - JSON-Settings verstehen
- **Log-Analyse** - Daten-Verzeichnis durchsuchen

## 🚀 Nächste Schritte

1. **Browser-Interface erkunden** - Screenshots und Text-Inhalte sammeln
2. **Dateien analysieren** - Code und Konfiguration verstehen
3. **Dokumentation erstellen** - Strukturierte Analyse-Ergebnisse
4. **Integration** - Mit MQTT-Analyse verknüpfen

---
*Erstellt: 18. September 2025*  
*Status: Vorbereitung - Bereit für Browser-Analyse*
