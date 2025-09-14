# Dashboard-Komponenten-Regeln

## 📋 Übersicht

**Zweck:** Zentrale Regeln für die Entwicklung von OMF Dashboard-Komponenten  
**Zielgruppe:** Entwickler und KI-Assistenten  
**Aktualisiert:** $(date)

## 🏗️ Komponenten-Architektur

### **1. Wrapper-Komponenten (Haupt-Tabs)**
```python
# Beispiel: steering.py
def show_steering():
    """Hauptfunktion für die Steuerung mit Untertabs"""
    st.header("🎮 Steuerung")
    st.markdown("Alle Steuerungsfunktionen der ORBIS Modellfabrik")

    # Untertabs für verschiedene Steuerungsarten
    steering_tab1, steering_tab2, steering_tab3 = st.tabs(
        ["🏭 Factory-Steuerung", "🔧 Generische Steuerung", "🎯 Sequenz-Steuerung"]
    )

    # Tab 1: Factory-Steuerung (Kommando-Zentrale)
    with steering_tab1:
        show_factory_steering()
```

**Regeln:**
- **Funktionsname:** `show_<component_name>()`
- **Header:** `st.header()` mit Icon + Name
- **Beschreibung:** `st.markdown()` mit kurzer Erklärung
- **Tabs:** `st.tabs()` für Unterkomponenten
- **Imports:** Nur die Unterkomponenten importieren

### **2. Unterkomponenten (Spezifische Funktionen)**
```python
# Beispiel: steering_factory.py
def show_factory_steering():
    """Hauptfunktion für die Factory Steuerung"""
    st.subheader("🏭 Factory Steuerung")
    st.markdown("**Traditionelle Steuerungsfunktionen für die Modellfabrik:**")

    # MQTT-Client prüfen
    mqtt_client = st.session_state.get("mqtt_client")
    if not mqtt_client:
        st.error("❌ MQTT-Client nicht verfügbar")
        return

    # Gateway initialisieren
    gateway = MqttGateway(mqtt_client)

    # Expandable Sections
    with st.expander("🏭 Factory Reset", expanded=False):
        _show_factory_reset_section(gateway)
```

**Regeln:**
- **Funktionsname:** `show_<specific_function>()`
- **Subheader:** `st.subheader()` mit Icon + spezifischer Name
- **MQTT-Client:** Immer prüfen und Fehlerbehandlung
- **Gateway:** `MqttGateway(mqtt_client)` verwenden
- **Sections:** `st.expander()` für gruppierte Funktionen
- **Private Funktionen:** `_show_<function>_section()` mit `_` Prefix

### **3. Private Hilfsfunktionen**
```python
def _show_factory_reset_section(gateway):
    """Factory Reset Section"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏭 Factory Reset", key="factory_reset"):
            _send_factory_reset_command(gateway)
    
    with col2:
        st.info("💡 Setzt alle Module zurück")

def _send_factory_reset_command(gateway):
    """Sendet Factory Reset Command"""
    try:
        success = gateway.send(
            topic="ccu/command/reset",
            builder=lambda: {"command": "factory_reset"},
            ensure_order_id=True
        )
        if success:
            st.success("✅ Factory Reset gesendet")
        else:
            st.error("❌ Fehler beim Senden")
    except Exception as e:
        st.error(f"❌ Exception: {e}")
```

**Regeln:**
- **Funktionsname:** `_show_<function>_section()` oder `_send_<action>_command()`
- **Parameter:** Immer `gateway` als Parameter
- **Error-Handling:** Try-catch für alle Gateway-Calls
- **UI-Feedback:** `st.success()`, `st.error()`, `st.info()`
- **Button-Keys:** Eindeutige Keys für alle Buttons

## 🔌 MQTT-Integration

### **1. MQTT-Singleton-Pattern**
```python
# ✅ KORREKT - Singleton-Pattern
mqtt_client = st.session_state.get("mqtt_client")
if not mqtt_client:
    st.error("❌ MQTT-Client nicht verfügbar")
    return

# Gateway aus Session State holen oder erstellen
if "mqtt_gateway" not in st.session_state:
    st.session_state.mqtt_gateway = MqttGateway(mqtt_client)

gateway = st.session_state.mqtt_gateway
```

**Regeln:**
- **Niemals:** Neuen MQTT-Client erstellen
- **Immer:** `st.session_state.get("mqtt_client")` verwenden
- **Gateway:** Aus Session State holen oder erstellen
- **Fehlerbehandlung:** Bei fehlendem Client sofort return

### **2. Per-Topic Subscription Pattern**
```python
# ✅ KORREKT - Per-topic subscription
def _subscribe_to_module_states(self):
    """Abonniert MQTT-Topics für Modul-Status-Updates (per-topic subscription)"""
    topic_filters = []
    
    # Topic-Filter sammeln
    for module in self._modules.values():
        topic_filter = f"module/v1/ff/{module.serial_number}/state"
        topic_filters.append(topic_filter)
    
    # Per-topic subscription für alle Filter
    self._mqtt_client.subscribe_many(topic_filters, qos=1)

def _process_status_updates(self):
    """Verarbeitet MQTT-Status-Updates"""
    for module in self._modules.values():
        topic_filter = f"module/v1/ff/{module.serial_number}/state"
        buffer = self._mqtt_client.get_buffer(topic_filter, maxlen=10)
        
        for message in buffer:
            self._update_module_state(module, message)
```

**Regeln:**
- **Niemals:** `get_messages()` verwenden
- **Immer:** `subscribe_many()` für mehrere Topics
- **Buffer:** `get_buffer(topic_filter, maxlen=N)` verwenden
- **Filter:** Spezifische Topic-Filter verwenden

## 🎨 UI-Standards

### **1. Konsistente Icons und Farben**
```python
# Status-Icons
def _get_status_icon(state):
    icon_map = {
        "IDLE": "🟢",
        "BUSY": "🟡", 
        "ERROR": "🔴",
        "OFFLINE": "⚫"
    }
    return icon_map.get(state, "⚪")

# Modul-Icons
def _get_module_icon(module_type):
    icon_map = {
        "Processing": "⚙️",
        "Storage": "🏬",
        "Transport": "🚗"
    }
    return icon_map.get(module_type, "❓")
```

### **2. Expandable Sections**
```python
# ✅ KORREKT - Gruppierte Funktionen
with st.expander("🔧 Modul-Sequenzen", expanded=False):
    _show_module_sequences_section(gateway)

with st.expander("🚗 FTS (Fahrerloses Transportsystem) Steuerung", expanded=False):
    _show_fts_commands_section(gateway)
```

**Regeln:**
- **Icon + Name:** Immer Icon vor dem Namen
- **expanded=False:** Sections standardmäßig eingeklappt
- **Gruppierung:** Logisch zusammengehörige Funktionen gruppieren

### **3. Button-Layout**
```python
# ✅ KORREKT - Spalten-Layout
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Sequenz starten", key="start_sequence"):
        _start_sequence()

with col2:
    st.info("💡 Sequenz wird automatisch ausgeführt")
```

**Regeln:**
- **Spalten:** `st.columns()` für Button-Layout
- **Eindeutige Keys:** Alle Buttons brauchen eindeutige Keys
- **Icons:** Buttons mit passenden Icons
- **Info-Text:** Erklärungen neben Buttons

## 📝 Import-Standards

### **1. Absolute Imports (KRITISCH)**
```python
# ✅ KORREKT - Absolute Imports
from src_orbis.omf.tools.mqtt_gateway import MqttGateway
from src_orbis.omf.tools.module_state_manager import get_module_state_manager

# ❌ FALSCH - Relative Imports
from ..tools.mqtt_gateway import MqttGateway
from .module_state_manager import get_module_state_manager
```

### **2. Import-Reihenfolge**
```python
# 1. Standard-Library
from datetime import datetime, timezone
from typing import List

# 2. Third-Party
import streamlit as st
import pandas as pd

# 3. Lokale Imports
from src_orbis.omf.tools.mqtt_gateway import MqttGateway
from src_orbis.omf.tools.module_state_manager import get_module_state_manager
```

## 🧪 Test-Standards

### **1. Test-Struktur**
```python
# tests_orbis/test_omf/test_module_state_manager.py
class TestModuleStateManager:
    def setup_method(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        from src_orbis.omf.tools.module_state_manager import ModuleStateManager
        ModuleStateManager._instance = None
        
        # Mock MQTT-Client und Gateway
        self.mock_mqtt_client = Mock()
        self.mock_mqtt_client.get_buffer.return_value = []
        self.mock_gateway = Mock()
        
        # ModuleStateManager initialisieren
        self.state_manager = get_module_state_manager()
        self.state_manager.initialize(self.mock_mqtt_client, self.mock_gateway)
```

**Regeln:**
- **Test-Datei:** `test_<component_name>.py`
- **Test-Klasse:** `Test<ComponentName>`
- **Setup:** Singleton zurücksetzen zwischen Tests
- **Mocks:** MQTT-Client und Gateway mocken
- **Absolute Imports:** Auch in Tests verwenden

## 🚨 Häufige Fehler

### **1. MQTT-Client Fehler**
```python
# ❌ FALSCH - Neuen Client erstellen
mqtt_client = OmfMqttClient(config)

# ✅ KORREKT - Singleton verwenden
mqtt_client = st.session_state.get("mqtt_client")
```

### **2. Import-Fehler**
```python
# ❌ FALSCH - Relative Imports
from ..tools.mqtt_gateway import MqttGateway

# ✅ KORREKT - Absolute Imports
from src_orbis.omf.tools.mqtt_gateway import MqttGateway
```

### **3. Per-Topic Subscription Fehler**
```python
# ❌ FALSCH - get_messages verwenden
messages = self._mqtt_client.get_messages(topic, limit=10)

# ✅ KORREKT - get_buffer verwenden
buffer = self._mqtt_client.get_buffer(topic_filter, maxlen=10)
```

## 🔄 UI-Refresh-Regeln

### **R015: Zentraler UI-Refresh**

**Problem:** `st.rerun()` in Komponenten führt zu MQTT-Subscription-Verlust

**Lösung:** Zentraler Refresh-Mechanismus über `request_refresh()`

#### **Verboten in Komponenten:**
```python
# ❌ FALSCH - führt zu Subscription-Verlust
st.rerun()
```

#### **Erlaubt in Komponenten:**
```python
# ✅ RICHTIG - zentraler Refresh
from src_orbis.omf.dashboard.utils.ui_refresh import request_refresh

def show_my_component():
    # ... Komponenten-Logik ...
    if some_condition:
        request_refresh()  # Löst zentralen Refresh aus
```

#### **Zentraler Refresh im Dashboard:**
```python
# In omf_dashboard.py
from src_orbis.omf.dashboard.utils.ui_refresh import consume_refresh

def main():
    # ... Dashboard-Logik ...
    if consume_refresh():
        st.rerun()  # Nur hier erlaubt!
```

## 📋 Checkliste für neue Komponenten

### **Vor der Implementierung:**
- [ ] Bestehende Komponenten analysieren
- [ ] Wrapper-Komponente oder Unterkomponente?
- [ ] MQTT-Integration geplant?
- [ ] Tests geplant?

### **Während der Implementierung:**
- [ ] Absolute Imports verwenden
- [ ] MQTT-Singleton-Pattern befolgen
- [ ] Per-topic subscription verwenden
- [ ] Error-Handling implementieren
- [ ] UI-Standards befolgen
- [ ] Private Funktionen mit `_` Prefix
- [ ] **UI-Refresh:** `request_refresh()` statt `st.rerun()` verwenden

### **Nach der Implementierung:**
- [ ] Tests schreiben und ausführen
- [ ] Linting prüfen (`black`, `ruff`)
- [ ] Pre-commit Hooks ausführen
- [ ] Dokumentation aktualisieren
- [ ] Commit mit aussagekräftiger Message

---

**Erstellt:** $(date)  
**Status:** ✅ **AKTIV**  
**Nächste Überprüfung:** Bei jeder neuen Komponente
