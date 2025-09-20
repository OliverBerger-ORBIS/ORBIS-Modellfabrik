# Project Setup Guide

**Zielgruppe:** Neue Entwickler  
**Letzte Aktualisierung:** 20.09.2025

## 🎯 Voraussetzungen

- **Python:** 3.8+ mit virtual environment
- **MQTT Broker:** Mosquitto oder ähnlich
- **Node-RED:** Für MQTT-OPC-UA Gateway
- **Streamlit:** Für Dashboard-Entwicklung

## 📦 Installation

```bash
# Virtual Environment aktivieren
source .venv

# Dependencies installieren
make install

# Validierung durchführen
make validate
```

## 🔧 Development Environment

### **Python Setup**
```bash
# Virtual Environment erstellen
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# oder
.venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### **MQTT Broker Setup**
- **Mosquitto** für lokale Entwicklung
- **Port:** 1883 (Standard)
- **Authentication:** Optional für Produktion

### **Node-RED Setup**
- **Port:** 1880 (Standard)
- **Flows:** Import aus `integrations/node_red/`

## 🚨 Critical Development Rules

### **Import Standards (KRITISCH)**
```python
# ✅ KORREKTE Imports
from omf.tools.logging_config import get_logger
from omf.dashboard.components.overview import show_overview

# ❌ VERBOTENE Imports
from ..module import Class  # Relative Imports
from module import Class    # Lokale Imports
import sys; sys.path.append(...)  # sys.path.append Hacks
```

### **Pfad Standards (KRITISCH)**
```python
# ✅ Source-Pfade (Paket-relativ)
Path(__file__).parent

# ✅ Data-Pfade (Projekt-root-relativ)
project_root / "data/omf-data/sessions"

# ❌ Absolute Pfade
"/Users/oliver/Projects/ORBIS-Modellfabrik/path/to/file"
```

## 🧪 Testing Strategy

### **Test-First Development**
1. **Implementierung** → Test → Fix → Test → Commit
2. **Nur bei 100% funktionierenden Features** committen
3. **UI-Tests** haben absolute Priorität

### **Test-Kategorien**
- **Unit-Tests:** Automatische Tests für einzelne Funktionen
- **Integration-Tests:** Tests für Komponenten-Interaktion
- **UI-Tests:** Manuelle Tests der Benutzeroberfläche

### **Test-Checkliste**
- [ ] Dashboard startet ohne Fehler
- [ ] Features funktionieren wie erwartet
- [ ] Keine Runtime-Fehler
- [ ] UI ist bedienbar

## 📋 Next Steps

Nach erfolgreichem Setup:
1. [Repository Structure](repository-structure.md) verstehen
2. [Development Workflow](development/workflow.md) lernen
3. [Dashboard Components](development/dashboard-components.md) entwickeln
4. [MQTT Integration](communication/mqtt/) implementieren

---

*Teil der OMF-Dokumentation | [Zurück zur README](../../README.md)*
