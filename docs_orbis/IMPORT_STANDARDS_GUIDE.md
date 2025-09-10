# 📋 Import-Standards Guide - OMF Projekt

## 🎯 **ZENTRALE ENTWICKLUNGSREGEL**

**NUR absolute Imports verwenden - KEINE Ausnahmen!**

## ✅ **KORREKTE Imports**

### **Dashboard-Komponenten:**
```python
# ✅ KORREKT
from src_orbis.omf.dashboard.components.dummy_component import show_dummy
from src_orbis.omf.dashboard.assets.html_templates import get_template
from src_orbis.omf.dashboard.omf_dashboard import main
```

### **Tools und Utilities:**
```python
# ✅ KORREKT
from src_orbis.omf.tools.sequence_executor import SequenceExecutor
from src_orbis.omf.tools.sequence_ui import SequenceUI
from src_orbis.omf.tools.message_template_manager import get_message_template_manager
from src_orbis.omf.tools.topic_manager import get_omf_topic_manager
```

### **Konfiguration:**
```python
# ✅ KORREKT
from src_orbis.omf.config.config import config
from src_orbis.omf.config.omf_config import config
from src_orbis.omf.config.sequence_definitions.aiqs_sequence import AIQSSequence
```

### **Helper-Apps:**
```python
# ✅ KORREKT
from src_orbis.helper_apps.replay_station.replay_station_dashboard import main
from src_orbis.analysis_tools.template_analyzers.txt_analyzer import TXTAnalyzer
```

## ❌ **VERBOTENE Imports**

### **Relative Imports:**
```python
# ❌ VERBOTEN
from ..module import Class
from .component import show_component
from ...tools import utility
```

### **Lokale Imports:**
```python
# ❌ VERBOTEN
from module import Class
from component import show_component
from tools import utility
```

### **sys.path.append Hacks:**
```python
# ❌ VERBOTEN
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from module import Class
```

## 🔧 **Praktische Beispiele**

### **Dashboard-Komponente erstellen:**
```python
# ✅ KORREKT
import streamlit as st
from src_orbis.omf.tools.message_template_manager import get_message_template_manager
from src_orbis.omf.dashboard.assets.html_templates import get_template

def show_my_component():
    st.title("Meine Komponente")
    # ...
```

### **Test-Datei erstellen:**
```python
# ✅ KORREKT
import pytest
from src_orbis.omf.tools.sequence_executor import SequenceExecutor
from src_orbis.omf.config.sequence_definitions.aiqs_sequence import AIQSSequence

def test_sequence_execution():
    # ...
```

### **Helper-App erstellen:**
```python
# ✅ KORREKT
import streamlit as st
from src_orbis.omf.tools.mock_mqtt_client import MockMQTTClient
from src_orbis.omf.config.config import config

def main():
    # ...
```

## 🚨 **Häufige Fehler vermeiden**

### **1. Black/Formatter Konflikte:**
```python
# ❌ PROBLEM: Black formatiert relative Imports um
from ..sequence_executor import SequenceExecutor

# ✅ LÖSUNG: Absolute Imports + fmt: off/on
# fmt: off
from src_orbis.omf.tools.sequence_executor import SequenceExecutor
# fmt: on
```

### **2. Test-Imports:**
```python
# ❌ PROBLEM: Tests können Module nicht finden
from omf.tools.sequence_executor import SequenceExecutor

# ✅ LÖSUNG: Vollständige Pfade
from src_orbis.omf.tools.sequence_executor import SequenceExecutor
```

### **3. Dashboard-Komponenten:**
```python
# ❌ PROBLEM: sys.path.append nach Entfernung
import sys
sys.path.append("...")
from components.dummy_component import show_dummy

# ✅ LÖSUNG: Absolute Imports
from src_orbis.omf.dashboard.components.dummy_component import show_dummy
```

## 📋 **Checkliste für neue Dateien**

### **Vor dem Erstellen:**
- [ ] **Import-Pfad geplant:** `from src_orbis.omf.module import Class`
- [ ] **Keine relativen Imports:** `from ..module import Class` ❌
- [ ] **Keine sys.path.append:** `sys.path.append(...)` ❌
- [ ] **Vollständige Pfade:** Alle Imports beginnen mit `src_orbis.`

### **Nach dem Erstellen:**
- [ ] **Syntax-Check:** `python -m py_compile datei.py`
- [ ] **Import-Test:** `python -c "import datei; print('OK')"`
- [ ] **Dashboard-Test:** `streamlit run src_orbis/omf/dashboard/omf_dashboard.py`

## 🔧 **Tools und Automatisierung**

### **Import-Check Script:**
```bash
# Alle relativen Imports finden
grep -r "from \.\." src_orbis/

# Alle sys.path.append finden
grep -r "sys.path.append" src_orbis/

# Alle lokalen Imports finden
grep -r "from [a-zA-Z_][a-zA-Z0-9_]* import" src_orbis/ | grep -v "src_orbis"
```

### **Pre-commit Hook:**
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: check-imports
      name: Check Import Standards
      entry: python scripts/check_imports.py
      language: system
      files: \.py$
```

## 🎯 **Warum diese Regeln?**

### **Vorteile:**
- ✅ **Keine Import-Fehler** mehr
- ✅ **Konsistente Struktur** im gesamten Projekt
- ✅ **Einfache Wartung** und Debugging
- ✅ **Pre-commit Hooks** funktionieren
- ✅ **Tests laufen** ohne Probleme
- ✅ **Black/Formatter** Konflikte vermieden

### **Probleme ohne diese Regeln:**
- ❌ **ModuleNotFoundError** in Tests
- ❌ **Black/Formatter** Konflikte
- ❌ **sys.path.append** Hacks überall
- ❌ **Inkonsistente** Import-Struktur
- ❌ **Schwer wartbarer** Code

## 📚 **Referenz**

### **Projekt-Struktur:**
```
src_orbis/
├── omf/
│   ├── dashboard/
│   │   ├── components/
│   │   ├── assets/
│   │   └── omf_dashboard.py
│   ├── tools/
│   ├── config/
│   └── ...
├── helper_apps/
├── analysis_tools/
└── ...
```

### **Import-Pattern:**
```python
# Immer: from src_orbis.{module_path} import {class/function}
from src_orbis.omf.dashboard.components.{component} import {function}
from src_orbis.omf.tools.{tool} import {class}
from src_orbis.omf.config.{config} import {class}
from src_orbis.helper_apps.{app} import {function}
from src_orbis.analysis_tools.{tool} import {class}
```

---

**Status:** ✅ Import-Standards definiert und dokumentiert  
**Nächster Schritt:** Diese Regeln bei allen zukünftigen Entwicklungen anwenden
