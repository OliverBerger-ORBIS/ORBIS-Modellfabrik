# MQTT Template Analysis System

## 📊 Übersicht

Das **MQTT Template Analysis System** der ORBIS Modellfabrik bietet eine umfassende Analyse und Verwaltung von MQTT-Nachrichten-Templates. Das System analysiert automatisch Session-Daten und extrahiert Template-Strukturen, Validierungsregeln und Beispiel-Nachrichten.

## 🎯 Features

### ✅ Vollständige Template-Analyse
- **67 MQTT-Topics** analysiert und kategorisiert
- **4 Kategorien**: CCU, TXT, MODULE, Node-RED
- **Automatische Sub-Kategorie-Erkennung**
- **Template-Struktur-Extraktion** mit ENUM-Erkennung

### 🔍 Intelligente Filterung
- **4-stufige Filterung**: Kategorie → Sub-Kategorie → Modul → Template
- **Modul-Namen-Filterung**: Benutzerfreundliche Namen (DRILL, AIQS, HBW, etc.)
- **Sub-Kategorie-Filterung**: Spezifische Filter für jede Kategorie
- **Template-Suche**: Volltext-Suche in Template-Beschreibungen

### 📋 Template-Management
- **Zentrale YAML-Konfiguration**: Alle Templates in `message_templates.yml`
- **Validierungsregeln**: Automatisch generierte Regeln für jedes Template
- **Beispiel-Nachrichten**: Echte Nachrichten aus Session-Daten
- **Statistiken**: Detaillierte Analysen und Metriken

## 🏗️ System-Architektur

### Analyzer-Komponenten

#### 1. CCU Template Analyzer
- **Datei**: `src_orbis/mqtt/tools/ccu_template_analyzer.py`
- **Topics**: 16 CCU-Topics analysiert
- **Sub-Kategorien**: Control, Order, State
- **Features**: ORDER-ID Tracking, Workflow-Analyse

#### 2. TXT Template Analyzer
- **Datei**: `src_orbis/mqtt/tools/txt_template_analyzer.py`
- **Topics**: 12 TXT-Topics analysiert
- **Sub-Kategorien**: Control, Input, Output, Function Input, Function Output, General
- **Features**: Sensor/Aktor-Analyse, Funktions-Eingänge/Ausgänge

#### 3. Module Template Analyzer
- **Datei**: `src_orbis/mqtt/tools/module_template_analyzer.py`
- **Topics**: 30 MODULE-Topics analysiert
- **Sub-Kategorien**: Connection, State, Order, Factsheet, InstantAction, Status
- **Features**: Modul-spezifische Analyse, IP-Range-Integration

#### 4. Node-RED Template Analyzer
- **Datei**: `src_orbis/mqtt/tools/nodered_template_analyzer.py`
- **Topics**: 11 Node-RED-Topics analysiert
- **Sub-Kategorien**: Connection, State, Order, Factsheet, InstantAction, Status, Flows, Dashboard, UI
- **Features**: Flow-Analyse, Dashboard/UI-Integration

### Manager-Komponenten

#### Message Template Manager
- **Datei**: `src_orbis/mqtt/tools/message_template_manager.py`
- **Funktionen**: Template-Loading, Statistiken, Filterung
- **Integration**: Dashboard-Integration, YAML-Management

#### Module Manager
- **Datei**: `src_orbis/mqtt/tools/module_manager.py`
- **Funktionen**: Modul-Konfiguration, IP-Range-Management
- **Integration**: Modul-Namen-Mapping, Dashboard-Integration

#### NFC Code Manager
- **Datei**: `src_orbis/mqtt/tools/nfc_code_manager.py`
- **Funktionen**: NFC-Code-Verwaltung, Quality-Check-Status
- **Integration**: Template-Validierung, Dashboard-Anzeige

## 📊 Template-Statistiken

### Gesamt-Übersicht
- **67 Topics** insgesamt analysiert
- **1490+ Nachrichten** aus Session-Daten
- **47 ENUM-Felder** identifiziert
- **26 variable Felder** definiert

### Kategorie-Breakdown

#### CCU (16 Topics)
- **Control**: Steuerungsbefehle und -antworten
- **Order**: Bestellungsverwaltung und -verarbeitung
- **State**: Systemstatus und Zustandsinformationen

#### TXT (12 Topics)
- **Control**: Steuerungsbefehle für Sensoren und Aktoren
- **Input**: Eingangsdaten und Konfiguration
- **Output**: Ausgangsdaten und Status
- **Function Input/Output**: Funktions-Eingangs-/Ausgangsdaten
- **General**: Allgemeine TXT-Funktionen

#### MODULE (20 Topics)
- **Connection**: Verbindungsstatus und Heartbeat
- **State**: Modul-Status und Zustandsinformationen
- **Order**: Bestellungsverarbeitung und -status
- **Factsheet**: Modul-Informationen und Konfiguration
- **InstantAction**: Sofortige Aktionen und Befehle
- **Status**: Allgemeine Status-Informationen

#### Node-RED (19 Topics)
- **Connection**: Verbindungsstatus und Heartbeat
- **State**: Systemstatus und Zustandsinformationen
- **Order**: Bestellungsverarbeitung und -status
- **Factsheet**: Modul-Informationen und Konfiguration
- **InstantAction**: Sofortige Aktionen und Befehle
- **Status**: Allgemeine Status-Informationen
- **Flows**: Node-RED Flow-Status und -Konfiguration
- **Dashboard**: Dashboard-Status und -Konfiguration
- **UI**: UI-Status und -Konfiguration

## 🎨 Dashboard-Features

### Template Library Tab
- **Vollständige Template-Übersicht** mit Strukturen und Beispielen
- **4-stufige Filterung** für präzise Navigation
- **Modul-Namen-Anzeige** statt technische IDs
- **Zweispaltige Layout** für bessere Übersicht

### Einstellungen Tab
- **Dashboard**: Dashboard-Konfiguration
- **Module**: Modul-Übersicht und -Konfiguration
- **NFC-Codes**: NFC-Code-Verwaltung
- **Topic-Konfiguration**: MQTT-Topic-Mappings
- **MQTT-Templates**: Template-Management

### Filter-Features
- **Kategorie-Filter**: CCU, TXT, MODULE, Node-RED
- **Sub-Kategorie-Filter**: Spezifisch für jede Kategorie
- **Modul-Filter**: Benutzerfreundliche Modul-Namen
- **Template-Suche**: Volltext-Suche

## 🔧 Technische Details

### Template-Struktur-Format
```yaml
topic_name:
  category: "CCU|TXT|MODULE|Node-RED"
  sub_category: "Control|State|Order|..."
  module: "Module-ID oder Name"
  description: "Template-Beschreibung"
  template_structure:
    field_name: "<type>|[enum_values]"
  examples:
    - field_name: "example_value"
  validation_rules:
    - "Validierungsregel"
```

### Type Recognition Strategy
1. **Booleans** → `<boolean>`
2. **Numbers** → `<number>`
3. **Datetime** → `<datetime>`
4. **UUIDs** → `<uuid>`
5. **Module IDs** → `<moduleId>`
6. **NFC Codes** → `<nfcCode>`
7. **Specific ENUMs** → `[value1, value2, ...]`
8. **Generic ENUMs** → `[value1, value2, ...]`
9. **Strings** → `<string>`

### Validierungsregeln
- **ENUM-Validierung**: `field muss in [values] sein`
- **Format-Validierung**: `field muss ISO 8601 Format haben`
- **Type-Validierung**: `field muss gültige Modul-ID sein`
- **Custom-Validierung**: Spezifische Regeln für komplexe Felder

## 🚀 Verwendung

### Dashboard starten
```bash
source .venv/bin/activate
streamlit run src_orbis/mqtt/dashboard/aps_dashboard.py --server.port 8501
```

### Template-Analyse ausführen
```bash
# CCU Templates analysieren
python src_orbis/mqtt/tools/ccu_template_analyzer.py

# TXT Templates analysieren
python src_orbis/mqtt/tools/txt_template_analyzer.py

# Module Templates analysieren
python src_orbis/mqtt/tools/module_template_analyzer.py

# Node-RED Templates analysieren
python src_orbis/mqtt/tools/nodered_template_analyzer.py
```

### Unit Tests ausführen
```bash
# Alle Tests
python -m pytest tests_orbis/ -v

# Spezifische Tests
python -m pytest tests_orbis/test_module_template_analyzer.py -v
python -m pytest tests_orbis/test_nodered_template_analyzer.py -v
```

## 📁 Datei-Struktur

```
src_orbis/mqtt/
├── tools/
│   ├── ccu_template_analyzer.py
│   ├── txt_template_analyzer.py
│   ├── module_template_analyzer.py
│   ├── nodered_template_analyzer.py
│   ├── message_template_manager.py
│   ├── module_manager.py
│   └── nfc_code_manager.py
├── dashboard/
│   └── aps_dashboard.py
└── config/
    ├── message_templates.yml
    ├── module_config.yml
    └── nfc_codes.yml

tests_orbis/
├── test_module_template_analyzer.py
├── test_nodered_template_analyzer.py
└── test_message_template_manager.py

mqtt-data/
├── sessions/
│   └── *.db (Session-Datenbanken)
└── template_library/
    ├── ccu_template_analysis.json
    ├── txt_template_analysis.json
    ├── module_template_analysis.json
    └── nodered_template_analysis.json
```

## 🔮 Zukünftige Erweiterungen

### Template Export (geplant)
- **JSON Schema Export**: Für API-Validierung
- **Code-Generierung**: TypeScript, Python, Java
- **OpenAPI/Swagger**: Für REST-API-Dokumentation
- **MQTT-Client-Code**: Für verschiedene Sprachen

### Template-Validierung (geplant)
- **Live-Validierung**: Echte MQTT-Nachrichten validieren
- **Template-Generierung**: Automatische Nachrichten-Generierung
- **Template-Vergleich**: Differenzierung zwischen Templates

### Dashboard-Erweiterungen (geplant)
- **Template-Export-Tab**: Bulk-Export-Funktionen
- **Inline-Export-Buttons**: Schnell-Export für einzelne Templates
- **Template-Statistiken**: Erweiterte Analytics

## 📞 Support

Bei Fragen oder Problemen mit dem MQTT Template Analysis System:

1. **Dokumentation**: Siehe [Project Status](./project-status.md)
2. **Unit Tests**: Führen Sie die Tests aus, um Probleme zu identifizieren
3. **Dashboard**: Nutzen Sie das Dashboard für visuelle Analyse
4. **Logs**: Überprüfen Sie die Session-Logs für Details

---

**Version**: 1.0  
**Letzte Aktualisierung**: 2025-08-28  
**Status**: ✅ Produktionsbereit
