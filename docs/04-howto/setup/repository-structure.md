# Repository Structure Guide

**Zielgruppe:** Entwickler  
**Letzte Aktualisierung:** 20.09.2025

## 📁 Projekt-Struktur

```
ORBIS-Modellfabrik/
├── omf/                          # Hauptpaket
│   ├── dashboard/                # Streamlit Dashboard
│   │   ├── components/           # UI-Komponenten
│   │   └── omf_dashboard.py      # Haupt-Dashboard
│   ├── tools/                    # Business Logic
│   │   ├── omf_mqtt_client.py   # MQTT-Client
│   │   ├── logging_config.py     # Logging-System
│   │   └── aps_*.py             # APS-Integration
│   ├── config/                   # Konfiguration
│   │   └── *.yml                # YAML-Configs
│   └── helper_apps/              # Separate Anwendungen
│       └── session_manager/      # Session Manager
├── registry/                     # Registry-System
│   └── model/                    # Schema-Definitionen
├── data/                         # Nutzdaten
│   └── omf-data/sessions/        # Session-Daten
├── docs/                         # Dokumentation
│   ├── 01-strategy/              # Strategie
│   ├── 02-architecture/          # Architektur
│   ├── 03-decision-records/      # ADRs
│   ├── 04-howto/                 # Anleitungen
│   └── sprints/                  # Sprint-Dokumentation
└── tests_orbis/                  # Tests
    └── test_omf/                 # OMF-Tests
```

## 🎯 Wichtige Verzeichnisse

### **omf/dashboard/**
- **Haupt-Dashboard:** `omf_dashboard.py`
- **Komponenten:** `components/` (Wrapper-Pattern)
- **UI-Refresh:** `utils/ui_refresh.py`

### **omf/tools/**
- **MQTT-Client:** `omf_mqtt_client.py` (Singleton)
- **Logging:** `logging_config.py`
- **APS-Integration:** `aps_*.py`

### **registry/model/**
- **Schemas:** JSON-Schema-Definitionen
- **Versionierung:** v0, v1, etc.
- **Topics:** MQTT-Topic-Definitionen

### **data/omf-data/sessions/**
- **Session-Daten:** SQLite + Log-Dateien
- **Replay-Daten:** Für Dashboard-Tests
- **Analyse-Daten:** Session-Analysen

## 🔧 Konfigurationsdateien

### **omf/config/**
- **module_config.yml:** Modul-Zuordnung
- **nfc_config.yml:** NFC-Code-Mapping
- **topic_config.yml:** MQTT-Topic-Struktur
- **message_templates/:** Nachrichten-Templates

### **registry/model/**
- **manifest.yml:** Registry-Version
- **topics/:** MQTT-Topic-Schemas
- **templates/:** Message-Templates
- **txt_controllers.yml:** TXT-Controller-Definitionen

## 📋 Development Rules

### **Import-Standards**
```python
# ✅ Absolute Imports
from omf.dashboard.tools.logging_config import get_logger
from omf.dashboard.components.overview import show_overview

# ❌ Relative Imports
from ..module import Class
from .component import show_component
```

### **Pfad-Standards**
```python
# ✅ Source-Pfade (Paket-relativ)
Path(__file__).parent

# ✅ Data-Pfade (Projekt-root-relativ)
project_root / "data/omf-data/sessions"

# ❌ Absolute Pfade
"/Users/oliver/Projects/ORBIS-Modellfabrik/path/to/file"
```

## 🧪 Testing Structure

### **tests_orbis/**
- **test_omf/:** OMF-spezifische Tests
- **test_helper_apps/:** Helper-App-Tests
- **Mock-Objekte:** Für MQTT-Client-Tests

### **Test-Ausführung**
```bash
# Alle Tests
python -m pytest tests_orbis/

# Nur OMF-Tests
python -m pytest tests_orbis/test_omf/

# Mit Coverage
python -m pytest tests_orbis/ --cov=omf
```

## 📚 Dokumentation

### **docs/04-howto/**
- **setup/:** Setup-Anleitungen
- **development/:** Entwicklungs-Anleitungen
- **communication/:** MQTT-Kommunikation
- **configuration/:** Konfiguration
- **testing/:** Test-Strategien

### **docs/03-decision-records/**
- **Architektur-Entscheidungen:** ADRs
- **Entwicklungsregeln:** Patterns und Standards
- **MQTT-Integration:** Kommunikations-Entscheidungen

---

*Teil der OMF-Dokumentation | [Zurück zur README](../../README.md)*
