# Dashboard Components Guide

**Zielgruppe:** Dashboard-Entwickler  
**Letzte Aktualisierung:** 20.09.2025

## 🎯 Dashboard-Architektur

### **Wrapper Pattern (Haupt-Tabs)**
```python
def show_steering():
    """Hauptfunktion für die Steuerung mit Untertabs"""
    st.header("🎮 Steuerung")
    st.markdown("Alle Steuerungsfunktionen der ORBIS Modellfabrik")
    
    # Untertabs für verschiedene Steuerungsarten
    steering_tab1, steering_tab2, steering_tab3 = st.tabs(
        ["🏭 Factory-Steuerung", "🔧 Generische Steuerung", "🎯 Sequenz-Steuerung"]
    )
    
    # Tab 1: Factory-Steuerung
    with steering_tab1:
        show_factory_steering()
    
    # Tab 2: Generische Steuerung
    with steering_tab2:
        show_generic_steering()
    
    # Tab 3: Sequenz-Steuerung
    with steering_tab3:
        show_sequence_steering()
```

### **Regeln für Wrapper-Komponenten**
- **Funktionsname:** `show_<component_name>()`
- **Header:** `st.header()` mit Icon + Name
- **Tabs:** `st.tabs()` für Unterkomponenten
- **MQTT-Client:** Immer prüfen und Fehlerbehandlung
- **Gateway:** `MqttGateway(mqtt_client)` verwenden

## 🔧 UI-Refresh Pattern

### **Zentraler Refresh (Empfohlen)**
```python
# ✅ RICHTIG - zentraler Refresh
from omf.dashboard.utils.ui_refresh import request_refresh

def show_my_component():
    if some_condition:
        request_refresh()  # Löst zentralen Refresh aus
```

### **Verboten: st.rerun() in Komponenten**
```python
# ❌ VERBOTEN - führt zu MQTT-Subscription-Verlust
def show_my_component():
    if some_condition:
        st.rerun()  # Verboten!
```

**Warum verboten?**
- **MQTT-Subscription-Verlust** bei st.rerun()
- **Session State** wird nicht korrekt verwaltet
- **Thread-sichere Logging** wird unterbrochen

## 📡 MQTT-Integration

### **Per-Topic-Buffer Pattern (Standard)**
```python
# ✅ RICHTIG - Spezifische Topics für Komponenten
mqtt_client.subscribe_many([
    "module/v1/ff/+/state",
    "module/v1/ff/+/connection",
    "ccu/state"
], qos=1)

# Nachrichten aus Per-Topic-Buffer holen
state_messages = list(mqtt_client.get_buffer("module/v1/ff/+/state"))
connection_messages = list(mqtt_client.get_buffer("module/v1/ff/+/connection"))
```

### **Message Center Ausnahme**
```python
# ✅ ERLAUBT - Nur im Message Center
mqtt_client.subscribe("#", qos=1)  # Wildcard-Subscription
all_messages = list(mqtt_client._history)  # Globale History
```

**Warum Ausnahme?**
- **Message Center** benötigt **alle Nachrichten**
- **Übersichtsfunktion** für Debugging und Monitoring
- **Validierungsregel** erlaubt `subscribe("#")` nur in `message_center.py`

## 🎨 UI-Komponenten

### **Streamlit Widgets**
```python
# Buttons mit eindeutigen Keys
if st.button("🔄 Factory Reset", key="factory_reset"):
    result = manager.send_system_command(client, "ccu/set/reset")
    if result:
        st.success("✅ Factory Reset gesendet")

# Spalten-Layout
col1, col2 = st.columns(2)
with col1:
    st.metric("Controllers", len(controllers))
with col2:
    st.metric("Orders", len(orders))

# Expandable Sections
with st.expander("Debug Information"):
    st.json(debug_data)
```

### **Eindeutige Keys**
```python
# ✅ RICHTIG - Eindeutige Keys für alle Widgets
st.button("Button 1", key="component_button_1")
st.button("Button 2", key="component_button_2")
st.checkbox("Checkbox", key="component_checkbox")
```

## 📊 Manager Pattern

### **Business Logic in Managern**
```python
class OrderManager:
    """Manager für Order-Verwaltung"""
    
    def __init__(self):
        self.orders = []
        self.logger = get_logger("OrderManager")
    
    def create_order(self, order_data):
        """Erstellt eine neue Order"""
        try:
            # Business Logic hier
            order = self._validate_order(order_data)
            self.orders.append(order)
            self.logger.info(f"Order erstellt: {order['id']}")
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Order: {e}")
            return False
    
    def _validate_order(self, order_data):
        """Validiert Order-Daten"""
        # Validierungslogik hier
        pass
```

### **Manager in Session State**
```python
def show_my_component():
    # Manager in Session State initialisieren
    if "order_manager" not in st.session_state:
        st.session_state["order_manager"] = OrderManager()
    
    manager = st.session_state["order_manager"]
    
    # Manager verwenden
    if st.button("Order erstellen"):
        result = manager.create_order(order_data)
        if result:
            st.success("Order erfolgreich erstellt")
```

## 🧪 Testing Dashboard Components

### **Unit Tests**
```python
def test_order_manager():
    """Test für OrderManager"""
    manager = OrderManager()
    
    # Test Order-Erstellung
    order_data = {"id": "test-001", "type": "storage"}
    result = manager.create_order(order_data)
    
    assert result == True
    assert len(manager.orders) == 1
    assert manager.orders[0]["id"] == "test-001"
```

### **Integration Tests**
```python
def test_dashboard_component():
    """Test für Dashboard-Komponente"""
    # Mock MQTT-Client
    mock_client = Mock()
    mock_client.get_buffer.return_value = []
    
    # Komponente testen
    with st.container():
        show_my_component()
    
    # Assertions
    assert mock_client.get_buffer.called
```

### **UI Tests (Manuell)**
- **Dashboard startet** ohne Fehler
- **Alle Tabs** sind bedienbar
- **MQTT-Nachrichten** werden korrekt angezeigt
- **Buttons** funktionieren wie erwartet
- **Keine Runtime-Fehler** in der Konsole

## 📋 Best Practices

### **Komponenten-Entwicklung**
1. **Wrapper Pattern** für Haupt-Tabs verwenden
2. **Manager Pattern** für Business Logic
3. **Eindeutige Keys** für alle Streamlit Widgets
4. **UI-Refresh Pattern** für Updates
5. **MQTT-Integration** mit Per-Topic-Buffer

### **Error Handling**
```python
def show_my_component():
    try:
        # Komponenten-Logik
        pass
    except Exception as e:
        st.error(f"Fehler in Komponente: {e}")
        logger.error(f"Komponenten-Fehler: {e}")
```

### **Logging**
```python
from omf.dashboard.tools.logging_config import get_logger

logger = get_logger("MyComponent")

def show_my_component():
    logger.info("Komponente gestartet")
    # Komponenten-Logik
    logger.debug("Debug-Information")
```

---

*Teil der OMF-Dokumentation | [Zurück zur README](../../README.md)*
