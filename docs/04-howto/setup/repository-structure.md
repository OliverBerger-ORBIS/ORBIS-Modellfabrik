# Repository Structure Guide

**Zielgruppe:** Entwickler  
**Letzte Aktualisierung:** 16.10.2025

## 📁 Projekt-Struktur

```
ORBIS-Modellfabrik/
├── omf2/                         # OMF2 Hauptanwendung
│   ├── omf.py                    # Streamlit Dashboard Entry Point
│   ├── admin/                    # Admin Domain (MQTT Client + Gateway + Manager)
│   ├── ccu/                      # CCU Domain (MQTT Client + Gateway + Manager)
│   ├── nodered/                  # Node-RED Domain (Gateway + Manager)
│   ├── common/                   # Shared Components (Logger, Registry, Manager)
│   ├── factory/                  # Factory Pattern für Singleton-Erstellung
│   ├── ui/                       # Streamlit UI Components
│   ├── registry/                 # Registry v2 (Topics, Schemas, MQTT Clients)
│   ├── config/                   # Konfigurationsdateien (MQTT, Logging)
│   ├── docs/                     # OMF2-spezifische Dokumentation
│   └── tests/                    # OMF2 Test Suite
├── session_manager/              # Helper-Anwendung
│   ├── app.py                    # Session Manager Entry Point
│   ├── components/               # UI-Komponenten
│   ├── mqtt/                     # MQTT-Integration
│   └── utils/                    # Utilities
├── data/                         # Nutzdaten
│   ├── omf-data/sessions/        # OMF Session-Daten
│   └── mqtt-data/                # MQTT Session-Daten
├── docs/                         # Dokumentation
│   ├── 01-strategy/              # Strategie
│   ├── 02-architecture/          # Architektur
│   ├── 03-decision-records/      # ADRs
│   ├── 04-howto/                 # Anleitungen
│   └── sprints/                  # Sprint-Dokumentation
└── tests/                        # Tests
    └── test_helper_apps/         # Helper Apps Tests
```

## 🎯 Wichtige Verzeichnisse

### **omf2/ui/**
- **Haupt-Dashboard:** `omf2/omf.py`
- **UI-Komponenten:** `ui/` (Wrapper-Pattern)
- **UI-Refresh:** `ui/utils/ui_refresh.py`

### **omf2/common/**
- **MQTT-Client:** `common/mqtt_client.py` (Singleton)
- **Logging:** `common/logging_config.py`
- **Registry:** `registry/` (Topics, Schemas, MQTT Clients)

### **omf2/registry/**
- **Schemas:** JSON-Schema-Definitionen
- **Topics:** MQTT-Topic-Definitionen
- **MQTT Clients:** Client-Konfiguration

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

### **tests/**
- **test_helper_apps/:** Helper-App-Tests
- **OMF3 Tests:** In `omf3/apps/ccu-ui/src/app/.../__tests__/`

### **Test-Ausführung**
```bash
# OMF3 Tests (Angular/Jest)
nx test ccu-ui

# Helper Apps Tests
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
