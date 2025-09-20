# OMF-APS Dashboard Integration Strategy

## Overview
Strategie zur Integration des APS-Dashboard in das bestehende OMF-Dashboard unter Beibehaltung aller bestehenden Funktionalitäten.

## Kompatibilitäts-Analyse

### ✅ **Vollständig Kompatibel**

#### **1. Tab-Struktur**
```python
# Bestehende OMF-Struktur
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📊 Übersicht",           # ✅ Kompatibel
    "🏭 Fertigungsaufträge",  # ✅ Kompatibel  
    "📡 Nachrichten-Zentrale", # ✅ Kompatibel
    "🎮 Steuerung",           # ✅ Kompatibel
    "🏗️ Shopfloor",          # ✅ Kompatibel
    "🚛 FTS",                # ✅ Kompatibel
    "🏢 CCU",                # ✅ Kompatibel
    "⚙️ Einstellungen",      # ✅ Kompatibel
    "🔧 Modul-Steuerung",    # ✅ Kompatibel
    "📋 Logs"                # ✅ Kompatibel
])
```

#### **2. Komponenten-Architektur**
```python
# Bestehende OMF-Pattern
def show_component():
    """Wrapper mit Untertabs"""
    tab1, tab2, tab3 = st.tabs(["Tab1", "Tab2", "Tab3"])
    with tab1:
        show_sub_component1()
    with tab2:
        show_sub_component2()
```

#### **3. MQTT-Integration**
```python
# Bestehende OMF-MQTT-Pattern
mqtt_client = st.session_state.get("mqtt_client")
if mqtt_client:
    # Per-Topic-Buffer Pattern
    messages = mqtt_client.get_buffer("topic_pattern")
    # Logging-System
    logger = get_logger("omf.dashboard.component")
```

#### **4. Icons und UI**
```python
# Bestehende OMF-Icons
MODULE_ICONS = {
    "MILL": "⚙️", "DRILL": "🔩", "AIQS": "🤖", 
    "HBW": "🏬", "DPS": "📦", "FTS": "🚗", "CHRG": "🔋"
}
```

## Integrations-Strategie

### **Phase 1: Parallel-Integration (Empfohlen)**

#### **1.1 Neue APS-Tabs hinzufügen**
```python
# Erweiterte Tab-Struktur
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "📊 Übersicht",           # Bestehend
    "🏭 Fertigungsaufträge",  # Bestehend
    "📡 Nachrichten-Zentrale", # Bestehend
    "🎮 Steuerung",           # Bestehend
    "🏗️ Shopfloor",          # Bestehend
    "🚛 FTS",                # Bestehend
    "🏢 CCU",                # Bestehend
    "⚙️ Einstellungen",      # Bestehend
    "🔧 Modul-Steuerung",    # Bestehend
    "📋 Logs",               # Bestehend
    "🏭 APS-Übersicht",      # NEU: APS-Overview
    "🎮 APS-Steuerung"       # NEU: APS-Steering
])
```

#### **1.2 APS-Komponenten erstellen**
```python
# Neue APS-Komponenten
load_component("aps_overview", "components.aps_overview", "APS Overview")
load_component("aps_steering", "components.aps_steering", "APS Steering")
load_component("aps_orders", "components.aps_orders", "APS Orders")
load_component("aps_configuration", "components.aps_configuration", "APS Configuration")
```

#### **1.3 Wrapper-Pattern für APS-Komponenten**
```python
def show_aps_overview():
    """APS-Übersicht mit Untertabs"""
    st.header("🏭 APS-Übersicht")
    
    # Untertabs für APS-spezifische Funktionen
    aps_tab1, aps_tab2, aps_tab3, aps_tab4, aps_tab5 = st.tabs([
        "🏭 Modul Status",      # APS-Module
        "📋 Kundenaufträge",    # APS-Orders
        "📊 Rohmaterial",       # APS-Materials
        "📦 Lagerbestand",      # APS-Inventory
        "📦 Produktkatalog"     # APS-Catalog
    ])
    
    with aps_tab1:
        show_aps_module_status()
    with aps_tab2:
        show_aps_customer_orders()
    # ... weitere Tabs
```

### **Phase 2: Funktionalitäts-Integration**

#### **2.1 MQTT-Topic-Integration**
```python
# APS-spezifische Topics zu bestehender MQTT-Integration
APS_TOPICS = {
    "orders": "module/v1/ff/NodeRed/{controller_id}/order",
    "instant_actions": "module/v1/ff/NodeRed/{controller_id}/instantActions",
    "state": "module/v1/ff/NodeRed/{controller_id}/state",
    "system_control": "ccu/set/*"
}

# Integration in bestehende MQTT-Client
def setup_aps_mqtt_subscriptions(mqtt_client):
    """APS-spezifische MQTT-Subscriptions"""
    for topic_name, topic_pattern in APS_TOPICS.items():
        mqtt_client.subscribe(topic_pattern, qos=2)
```

#### **2.2 Dashboard-Commands Integration**
```python
def send_aps_order(color):
    """APS-Bestellung senden"""
    order = {
        "orderId": generate_order_id(),
        "timestamp": get_timestamp(),
        "action": "STORAGE",
        "type": color
    }
    
    # VDA5050-konforme Order
    topic = f"module/v1/ff/NodeRed/{controller_id}/order"
    mqtt_client.publish(topic, json.dumps(order), qos=2)

def send_aps_system_command(command):
    """APS-System-Befehl senden"""
    topic = f"ccu/set/{command}"
    mqtt_client.publish(topic, payload, qos=2)
```

#### **2.3 Lagerbestand-Integration**
```python
def show_aps_inventory():
    """APS-Lagerbestand (basiert auf bestehender overview_inventory.py)"""
    # Bestehende OrderManager-Klasse erweitern
    order_manager = OrderManager()
    
    # APS-spezifische Inventory-Daten
    aps_inventory = {
        "A1": {"type": "RED", "count": 5},
        "A2": {"type": "BLUE", "count": 3},
        "A3": {"type": "WHITE", "count": 2},
        # ... weitere Positionen
    }
    
    # Bestehende UI-Komponenten verwenden
    for position, data in aps_inventory.items():
        st.metric(f"Position {position}", f"{data['count']} {data['type']}")
```

### **Phase 3: UI-Adaptation**

#### **3.1 Icons und Styling**
```python
# Bestehende Icons erweitern
APS_MODULE_ICONS = {
    "DPS": "📦",      # DPS TXT Controller
    "AIQS": "🤖",     # AIQS TXT Controller  
    "CGW": "☁️",      # Cloud Gateway
    "FTS": "🚗",      # FTS TXT Controller
    "HBW": "🏬",      # HBW Module
    "MILL": "⚙️",     # MILL Module
    "DRILL": "🔩",    # DRILL Module
    "CHRG": "🔋"      # Charging Station
}

# Bestehende Status-Icons verwenden
def get_aps_status_icon(status):
    """APS-Status-Icons (basiert auf bestehender Logik)"""
    return get_status_icon(status)  # Bestehende Funktion
```

#### **3.2 Logging-Integration**
```python
def show_aps_component():
    """APS-Komponente mit bestehendem Logging"""
    logger = get_logger("omf.dashboard.aps")
    
    logger.info("🏭 APS-Komponente geladen")
    
    # Bestehende Logging-Pattern verwenden
    if st.button("APS-Bestellung senden"):
        logger.info("📋 APS-Bestellung wird gesendet")
        send_aps_order("RED")
        logger.info("✅ APS-Bestellung gesendet")
```

## Implementierungs-Plan

### **Schritt 1: APS-Komponenten erstellen**
```bash
# Neue Komponenten-Dateien
omf/dashboard/components/
├── aps_overview.py              # APS-Übersicht
├── aps_steering.py              # APS-Steuerung
├── aps_orders.py                # APS-Bestellungen
├── aps_configuration.py         # APS-Konfiguration
└── aps_module_status.py         # APS-Modul-Status
```

### **Schritt 2: MQTT-Integration erweitern**
```python
# Erweiterte MQTT-Client-Funktionen
def setup_aps_integration(mqtt_client):
    """APS-Integration in bestehenden MQTT-Client"""
    # VDA5050 Topics
    mqtt_client.subscribe("module/v1/ff/NodeRed/+/order", qos=2)
    mqtt_client.subscribe("module/v1/ff/NodeRed/+/instantActions", qos=2)
    mqtt_client.subscribe("module/v1/ff/NodeRed/+/state", qos=2)
    
    # System Control Topics
    mqtt_client.subscribe("ccu/set/+", qos=2)
```

### **Schritt 3: Dashboard erweitern**
```python
# Erweiterte Tab-Struktur in omf_dashboard.py
def display_tabs():
    """Erweiterte Tabs mit APS-Integration"""
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
        "📊 Übersicht",           # Bestehend
        "🏭 Fertigungsaufträge",  # Bestehend
        "📡 Nachrichten-Zentrale", # Bestehend
        "🎮 Steuerung",           # Bestehend
        "🏗️ Shopfloor",          # Bestehend
        "🚛 FTS",                # Bestehend
        "🏢 CCU",                # Bestehend
        "⚙️ Einstellungen",      # Bestehend
        "🔧 Modul-Steuerung",    # Bestehend
        "📋 Logs",               # Bestehend
        "🏭 APS-Übersicht",      # NEU
        "🎮 APS-Steuerung"       # NEU
    ])
    
    # Bestehende Tabs unverändert
    with tab1:
        components["overview"]()
    # ... bestehende Tabs
    
    # Neue APS-Tabs
    with tab11:
        components["aps_overview"]()
    with tab12:
        components["aps_steering"]()
```

## Vorteile dieser Strategie

### **✅ Bestehende Funktionalität erhalten**
- Alle bestehenden Tabs und Komponenten bleiben unverändert
- Bestehende MQTT-Integration bleibt funktional
- Bestehende Logging- und UI-Patterns werden wiederverwendet

### **✅ Parallele Entwicklung möglich**
- APS-Funktionalität kann parallel entwickelt werden
- Bestehende OMF-Funktionen bleiben verfügbar
- Schrittweise Migration möglich

### **✅ Einfache Übernahme**
- APS-Tabs können später in bestehende Tabs integriert werden
- Komponenten können schrittweise migriert werden
- Rollback möglich bei Problemen

### **✅ Konsistente UI**
- Bestehende Icons und Styling werden wiederverwendet
- Konsistente Benutzererfahrung
- Bestehende Logging-Patterns

## Nächste Schritte

1. **APS-Komponenten erstellen** - Neue Komponenten-Dateien
2. **MQTT-Integration erweitern** - APS-Topics hinzufügen
3. **Dashboard erweitern** - Neue Tabs hinzufügen
4. **Testing** - Integration mit realer APS testen
5. **Migration** - Schrittweise Integration in bestehende Tabs

## Dateien für Implementierung

1. **omf/dashboard/omf_dashboard.py** - Tab-Struktur erweitern
2. **omf/dashboard/components/aps_*.py** - Neue APS-Komponenten
3. **omf/tools/omf_mqtt_factory.py** - MQTT-Integration erweitern
4. **omf/dashboard/components/overview_inventory.py** - Lagerbestand-Integration
