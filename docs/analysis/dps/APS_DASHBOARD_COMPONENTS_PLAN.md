# APS Dashboard Components Plan

## Overview
Plan für APS-Dashboard-Komponenten ohne bestehende OMF-Dashboard-Funktionalität zu beeinträchtigen.

## APS Dashboard Komponenten-Struktur

### **1. Hauptkomponenten (Wrapper-Pattern)**

#### **1.1 APS Overview (`aps_overview.py`)**
```python
"""
APS Overview - Hauptkomponente für APS-Übersicht
Wrapper für alle APS-Übersichtsfunktionen mit Untertabs
"""

import streamlit as st
from omf.tools.aps_vda5050_manager import VDA5050OrderManager
from omf.tools.aps_txt_controller_manager import APSTXTControllerManager

def show_aps_overview():
    """Hauptfunktion für APS-Übersicht mit Untertabs"""
    st.header("🏭 APS-Übersicht")
    st.markdown("Übersicht über alle APS-Systemkomponenten")
    
    # Untertabs für verschiedene APS-Übersichtsbereiche
    aps_tab1, aps_tab2, aps_tab3, aps_tab4, aps_tab5 = st.tabs([
        "🏭 Modul Status",      # APS-Module
        "📋 Kundenaufträge",    # APS-Orders
        "📊 Rohmaterial",       # APS-Materials
        "📦 Lagerbestand",      # APS-Inventory
        "📦 Produktkatalog"     # APS-Catalog
    ])
    
    # Tab 1: APS Modul Status
    with aps_tab1:
        show_aps_module_status()
    
    # Tab 2: APS Kundenaufträge
    with aps_tab2:
        show_aps_customer_orders()
    
    # Tab 3: APS Rohmaterial
    with aps_tab3:
        show_aps_materials()
    
    # Tab 4: APS Lagerbestand
    with aps_tab4:
        show_aps_inventory()
    
    # Tab 5: APS Produktkatalog
    with aps_tab5:
        show_aps_product_catalog()

def show_aps_module_status():
    """APS-Modul-Status mit TXT Controllern"""
    st.subheader("🏭 APS-Modul-Status")
    
    # TXT Controller Manager
    txt_manager = APSTXTControllerManager()
    controllers = txt_manager.get_controllers()
    
    # TXT Controller Status
    for controller_id, controller in controllers.items():
        col1, col2, col3 = st.columns([1, 2, 3])
        
        with col1:
            st.metric("Controller", controller_id)
        with col2:
            st.metric("IP", controller["ip"])
        with col3:
            st.metric("Rolle", controller["role"])
    
    # Physical Modules
    st.subheader("🔧 Physical Modules")
    physical_modules = txt_manager.get_physical_modules()
    
    for module_id, module in physical_modules.items():
        col1, col2, col3 = st.columns([1, 2, 3])
        
        with col1:
            st.metric("Module", module_id)
        with col2:
            st.metric("Serial", module["serial"])
        with col3:
            st.metric("Typ", module["type"])

def show_aps_customer_orders():
    """APS-Kundenaufträge"""
    st.subheader("📋 APS-Kundenaufträge")
    
    # VDA5050 Order Manager
    vda_manager = VDA5050OrderManager()
    active_orders = vda_manager.get_active_orders()
    
    if active_orders:
        st.metric("Aktive Orders", len(active_orders))
        
        for order_id, order_info in active_orders.items():
            with st.expander(f"Order {order_id}"):
                st.json(order_info)
    else:
        st.info("Keine aktiven Orders")

def show_aps_inventory():
    """APS-Lagerbestand (basiert auf bestehender overview_inventory.py)"""
    st.subheader("📦 APS-Lagerbestand")
    
    # Bestehende OrderManager-Struktur verwenden
    from omf.dashboard.components.overview_inventory import OrderManager
    
    order_manager = OrderManager()
    
    # APS-spezifische Inventory-Daten
    aps_inventory = {
        "A1": {"type": "RED", "count": 5, "status": "occupied"},
        "A2": {"type": "BLUE", "count": 3, "status": "occupied"},
        "A3": {"type": "WHITE", "count": 2, "status": "occupied"},
        "B1": {"type": None, "count": 0, "status": "empty"},
        "B2": {"type": None, "count": 0, "status": "empty"},
        "B3": {"type": None, "count": 0, "status": "empty"},
        "C1": {"type": None, "count": 0, "status": "empty"},
        "C2": {"type": None, "count": 0, "status": "empty"},
        "C3": {"type": None, "count": 0, "status": "empty"}
    }
    
    # Inventory-Grid anzeigen
    cols = st.columns(3)
    for i, (position, data) in enumerate(aps_inventory.items()):
        with cols[i % 3]:
            if data["status"] == "occupied":
                st.metric(f"Position {position}", f"{data['count']} {data['type']}", "🟢")
            else:
                st.metric(f"Position {position}", "Leer", "⚪")

def show_aps_materials():
    """APS-Rohmaterial"""
    st.subheader("📊 APS-Rohmaterial")
    
    materials = {
        "RED": {"count": 15, "status": "available"},
        "BLUE": {"count": 12, "status": "available"},
        "WHITE": {"count": 8, "status": "available"}
    }
    
    for material, data in materials.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(f"Material {material}", data["count"])
        with col2:
            st.metric("Status", data["status"])

def show_aps_product_catalog():
    """APS-Produktkatalog"""
    st.subheader("📦 APS-Produktkatalog")
    
    products = {
        "RED": {"description": "Rotes Werkstück", "process_time": "5 min"},
        "BLUE": {"description": "Blaues Werkstück", "process_time": "7 min"},
        "WHITE": {"description": "Weißes Werkstück", "process_time": "10 min"}
    }
    
    for product, info in products.items():
        with st.expander(f"Produkt {product}"):
            st.write(f"**Beschreibung:** {info['description']}")
            st.write(f"**Bearbeitungszeit:** {info['process_time']}")
```

#### **1.2 APS Steering (`aps_steering.py`)**
```python
"""
APS Steering - Hauptkomponente für APS-Steuerung
Wrapper für alle APS-Steuerungsfunktionen mit Untertabs
"""

import streamlit as st
from omf.tools.aps_vda5050_manager import VDA5050OrderManager
from omf.tools.aps_system_control_manager import APSSystemControlManager

def show_aps_steering():
    """Hauptfunktion für APS-Steuerung mit Untertabs"""
    st.header("🎮 APS-Steuerung")
    st.markdown("Steuerung aller APS-Systemkomponenten")
    
    # Untertabs für verschiedene APS-Steuerungsbereiche
    steering_tab1, steering_tab2, steering_tab3 = st.tabs([
        "🏭 Factory Control",   # Factory-Steuerung
        "📋 Order Control",     # Order-Steuerung
        "🔧 Module Control"     # Modul-Steuerung
    ])
    
    # Tab 1: Factory Control
    with steering_tab1:
        show_aps_factory_control()
    
    # Tab 2: Order Control
    with steering_tab2:
        show_aps_order_control()
    
    # Tab 3: Module Control
    with steering_tab3:
        show_aps_module_control()

def show_aps_factory_control():
    """APS-Factory-Steuerung"""
    st.subheader("🏭 Factory-Steuerung")
    
    system_control = APSSystemControlManager()
    
    # System Commands
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏭 Factory Reset", type="primary"):
            result = system_control.reset_factory()
            st.success("Factory Reset gesendet")
            st.json(result)
    
    with col2:
        if st.button("🔋 FTS Charge", type="secondary"):
            result = system_control.charge_fts()
            st.success("FTS Charge gesendet")
            st.json(result)
    
    with col3:
        if st.button("🅿️ Park Factory", type="secondary"):
            result = system_control.send_system_command("park")
            st.success("Park Factory gesendet")
            st.json(result)
    
    # Weitere System Commands
    st.subheader("⚙️ Weitere System Commands")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📐 Layout"):
            result = system_control.send_system_command("layout")
            st.success("Layout Command gesendet")
    
    with col2:
        if st.button("🔄 Flows"):
            result = system_control.send_system_command("flows")
            st.success("Flows Command gesendet")
    
    with col3:
        if st.button("🎯 Calibration"):
            result = system_control.send_system_command("calibration")
            st.success("Calibration Command gesendet")

def show_aps_order_control():
    """APS-Order-Steuerung"""
    st.subheader("📋 Order-Steuerung")
    
    vda_manager = VDA5050OrderManager()
    
    # Order Commands
    st.subheader("🔴 Bestellungen")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔴 Bestellung RED", type="primary"):
            order = vda_manager.create_storage_order("RED")
            st.success("Bestellung RED erstellt")
            st.json(order)
    
    with col2:
        if st.button("🔵 Bestellung BLUE", type="primary"):
            order = vda_manager.create_storage_order("BLUE")
            st.success("Bestellung BLUE erstellt")
            st.json(order)
    
    with col3:
        if st.button("⚪ Bestellung WHITE", type="primary"):
            order = vda_manager.create_storage_order("WHITE")
            st.success("Bestellung WHITE erstellt")
            st.json(order)
    
    # Instant Actions
    st.subheader("⚡ Instant Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reset"):
            action = vda_manager.send_instant_action("reset")
            st.success("Reset Action gesendet")
            st.json(action)
    
    with col2:
        if st.button("📢 Announce Output"):
            action = vda_manager.send_instant_action("announceOutput")
            st.success("Announce Output Action gesendet")
            st.json(action)
    
    with col3:
        if st.button("❌ Cancel Storage Order"):
            action = vda_manager.send_instant_action("cancelStorageOrder")
            st.success("Cancel Storage Order Action gesendet")
            st.json(action)
    
    # Active Orders
    st.subheader("📊 Aktive Orders")
    active_orders = vda_manager.get_active_orders()
    
    if active_orders:
        for order_id, order_info in active_orders.items():
            with st.expander(f"Order {order_id}"):
                st.json(order_info)
    else:
        st.info("Keine aktiven Orders")

def show_aps_module_control():
    """APS-Modul-Steuerung"""
    st.subheader("🔧 Modul-Steuerung")
    
    from omf.tools.aps_txt_controller_manager import APSTXTControllerManager
    txt_manager = APSTXTControllerManager()
    
    # TXT Controller Control
    st.subheader("🖥️ TXT Controller")
    controllers = txt_manager.get_controllers()
    
    for controller_id, controller in controllers.items():
        with st.expander(f"TXT {controller_id} - {controller['role']}"):
            st.write(f"**IP:** {controller['ip']}")
            st.write(f"**Funktionen:** {', '.join(controller['functions'])}")
            
            # Controller-spezifische Aktionen
            if controller_id == "DPS":
                if st.button(f"🔄 {controller_id} Reset"):
                    st.success(f"{controller_id} Reset gesendet")
            elif controller_id == "FTS":
                if st.button(f"🔋 {controller_id} Charge"):
                    st.success(f"{controller_id} Charge gesendet")
    
    # Physical Module Control
    st.subheader("🔧 Physical Modules")
    physical_modules = txt_manager.get_physical_modules()
    
    for module_id, module in physical_modules.items():
        with st.expander(f"Module {module_id} - {module['type']}"):
            st.write(f"**Serial:** {module['serial']}")
            st.write(f"**Funktionen:** {', '.join(module['functions'])}")
            st.write(f"**TXT Controller:** {module['txt_controller'] or 'None'}")
```

#### **1.3 APS Orders (`aps_orders.py`)**
```python
"""
APS Orders - Hauptkomponente für APS-Bestellungen
Wrapper für alle APS-Bestellungsfunktionen mit Untertabs
"""

import streamlit as st
from omf.tools.aps_vda5050_manager import VDA5050OrderManager

def show_aps_orders():
    """Hauptfunktion für APS-Bestellungen mit Untertabs"""
    st.header("📋 APS-Bestellungen")
    st.markdown("Verwaltung aller APS-Bestellungen und -Aufträge")
    
    # Untertabs für verschiedene APS-Bestellungsbereiche
    orders_tab1, orders_tab2, orders_tab3 = st.tabs([
        "📋 Aktive Orders",     # Active Orders
        "📊 Order-Historie",    # Order History
        "⚙️ Order-Konfiguration" # Order Configuration
    ])
    
    # Tab 1: Aktive Orders
    with orders_tab1:
        show_aps_active_orders()
    
    # Tab 2: Order-Historie
    with orders_tab2:
        show_aps_order_history()
    
    # Tab 3: Order-Konfiguration
    with orders_tab3:
        show_aps_order_configuration()

def show_aps_active_orders():
    """Aktive APS-Orders"""
    st.subheader("📋 Aktive Orders")
    
    vda_manager = VDA5050OrderManager()
    active_orders = vda_manager.get_active_orders()
    
    if active_orders:
        st.metric("Anzahl aktive Orders", len(active_orders))
        
        for order_id, order_info in active_orders.items():
            with st.expander(f"Order {order_id}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.json(order_info)
                
                with col2:
                    if st.button(f"❌ Order {order_id} abbrechen"):
                        st.warning(f"Order {order_id} wird abgebrochen...")
    else:
        st.info("Keine aktiven Orders")

def show_aps_order_history():
    """APS-Order-Historie"""
    st.subheader("📊 Order-Historie")
    
    vda_manager = VDA5050OrderManager()
    order_history = vda_manager.get_order_history()
    
    if order_history:
        st.metric("Anzahl abgeschlossene Orders", len(order_history))
        
        for order in order_history:
            with st.expander(f"Order {order.get('orderId', 'Unknown')}"):
                st.json(order)
    else:
        st.info("Keine Order-Historie verfügbar")

def show_aps_order_configuration():
    """APS-Order-Konfiguration"""
    st.subheader("⚙️ Order-Konfiguration")
    
    st.write("**VDA5050 Standard-Konfiguration**")
    
    # Order-Typen
    st.subheader("📋 Order-Typen")
    order_types = ["STORAGE", "RETRIEVAL", "TRANSPORT"]
    
    for order_type in order_types:
        st.write(f"• **{order_type}** - {get_order_type_description(order_type)}")
    
    # Werkstück-Typen
    st.subheader("🎨 Werkstück-Typen")
    workpiece_types = ["RED", "BLUE", "WHITE"]
    
    for workpiece_type in workpiece_types:
        st.write(f"• **{workpiece_type}** - {get_workpiece_type_description(workpiece_type)}")

def get_order_type_description(order_type):
    """Gibt Beschreibung für Order-Typ zurück"""
    descriptions = {
        "STORAGE": "Werkstück einlagern",
        "RETRIEVAL": "Werkstück auslagern", 
        "TRANSPORT": "Werkstück transportieren"
    }
    return descriptions.get(order_type, "Unbekannter Typ")

def get_workpiece_type_description(workpiece_type):
    """Gibt Beschreibung für Werkstück-Typ zurück"""
    descriptions = {
        "RED": "Rotes Werkstück (5 min Bearbeitung)",
        "BLUE": "Blaues Werkstück (7 min Bearbeitung)",
        "WHITE": "Weißes Werkstück (10 min Bearbeitung)"
    }
    return descriptions.get(workpiece_type, "Unbekannter Typ")
```

#### **1.4 APS Configuration (`aps_configuration.py`)**
```python
"""
APS Configuration - Hauptkomponente für APS-Konfiguration
Wrapper für alle APS-Konfigurationsfunktionen mit Untertabs
"""

import streamlit as st
from omf.tools.aps_txt_controller_manager import APSTXTControllerManager

def show_aps_configuration():
    """Hauptfunktion für APS-Konfiguration mit Untertabs"""
    st.header("⚙️ APS-Konfiguration")
    st.markdown("Konfiguration aller APS-Systemkomponenten")
    
    # Untertabs für verschiedene APS-Konfigurationsbereiche
    config_tab1, config_tab2, config_tab3, config_tab4 = st.tabs([
        "🖥️ TXT Controller",    # TXT Controller Config
        "🔧 Physical Modules",  # Physical Modules Config
        "🔗 MQTT Topics",       # MQTT Topics Config
        "📋 VDA5050 Settings"   # VDA5050 Settings
    ])
    
    # Tab 1: TXT Controller
    with config_tab1:
        show_aps_txt_controller_config()
    
    # Tab 2: Physical Modules
    with config_tab2:
        show_aps_physical_modules_config()
    
    # Tab 3: MQTT Topics
    with config_tab3:
        show_aps_mqtt_topics_config()
    
    # Tab 4: VDA5050 Settings
    with config_tab4:
        show_aps_vda5050_settings()

def show_aps_txt_controller_config():
    """TXT Controller Konfiguration"""
    st.subheader("🖥️ TXT Controller Konfiguration")
    
    txt_manager = APSTXTControllerManager()
    controllers = txt_manager.get_controllers()
    
    for controller_id, controller in controllers.items():
        with st.expander(f"TXT {controller_id} - {controller['role']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**IP-Adresse:** {controller['ip']}")
                st.write(f"**Rolle:** {controller['role']}")
            
            with col2:
                st.write("**Funktionen:**")
                for function in controller['functions']:
                    st.write(f"• {function}")
            
            # Konfiguration bearbeiten
            if st.button(f"⚙️ {controller_id} konfigurieren"):
                st.info(f"Konfiguration für {controller_id} wird geöffnet...")

def show_aps_physical_modules_config():
    """Physical Modules Konfiguration"""
    st.subheader("🔧 Physical Modules Konfiguration")
    
    txt_manager = APSTXTControllerManager()
    physical_modules = txt_manager.get_physical_modules()
    
    for module_id, module in physical_modules.items():
        with st.expander(f"Module {module_id} - {module['type']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Serial Number:** {module['serial']}")
                st.write(f"**Typ:** {module['type']}")
            
            with col2:
                st.write("**Funktionen:**")
                for function in module['functions']:
                    st.write(f"• {function}")
                
                st.write(f"**TXT Controller:** {module['txt_controller'] or 'None'}")

def show_aps_mqtt_topics_config():
    """MQTT Topics Konfiguration"""
    st.subheader("🔗 MQTT Topics Konfiguration")
    
    # VDA5050 Topics
    st.subheader("📡 VDA5050 Topics")
    vda5050_topics = [
        "module/v1/ff/NodeRed/{controller_id}/order",
        "module/v1/ff/NodeRed/{controller_id}/instantActions",
        "module/v1/ff/NodeRed/{controller_id}/state",
        "module/v1/ff/NodeRed/{controller_id}/connection",
        "module/v1/ff/NodeRed/{controller_id}/factsheet"
    ]
    
    for topic in vda5050_topics:
        st.code(topic)
    
    # System Control Topics
    st.subheader("🎮 System Control Topics")
    system_control_topics = [
        "ccu/set/reset",
        "ccu/set/charge",
        "ccu/set/layout",
        "ccu/set/flows",
        "ccu/set/calibration",
        "ccu/set/park"
    ]
    
    for topic in system_control_topics:
        st.code(topic)

def show_aps_vda5050_settings():
    """VDA5050 Settings"""
    st.subheader("📋 VDA5050 Settings")
    
    st.write("**VDA5050 Standard-Konfiguration**")
    
    # Operating Modes
    st.subheader("🔄 Operating Modes")
    operating_modes = ["TEACHIN", "AUTOMATIC"]
    
    for mode in operating_modes:
        st.write(f"• **{mode}** - {get_operating_mode_description(mode)}")
    
    # Action States
    st.subheader("⚡ Action States")
    action_states = ["WAITING", "RUNNING", "FINISHED", "FAILED"]
    
    for state in action_states:
        st.write(f"• **{state}** - {get_action_state_description(state)}")

def get_operating_mode_description(mode):
    """Gibt Beschreibung für Operating Mode zurück"""
    descriptions = {
        "TEACHIN": "Lernmodus für manuelle Konfiguration",
        "AUTOMATIC": "Automatischer Betriebsmodus"
    }
    return descriptions.get(mode, "Unbekannter Modus")

def get_action_state_description(state):
    """Gibt Beschreibung für Action State zurück"""
    descriptions = {
        "WAITING": "Aktion wartet auf Ausführung",
        "RUNNING": "Aktion wird ausgeführt",
        "FINISHED": "Aktion erfolgreich abgeschlossen",
        "FAILED": "Aktion fehlgeschlagen"
    }
    return descriptions.get(state, "Unbekannter Status")
```

## Integration in OMF Dashboard

### **1. Tab-Struktur erweitern (nach Live-Demo)**
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
        "🏭 APS-Übersicht",      # NEU: APS Overview
        "🎮 APS-Steuerung"       # NEU: APS Steering
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

### **2. Komponenten-Loading erweitern**
```python
# Erweiterte Komponenten-Loading in omf_dashboard.py
def load_component(component_name, import_path, display_name=None):
    """Lädt eine Komponente fehlertolerant"""
    if display_name is None:
        display_name = component_name.replace("_", " ").title()

    try:
        module = __import__(import_path, fromlist=[f"show_{component_name}"])
        show_function = getattr(module, f"show_{component_name}")
        components[component_name] = show_function
    except ImportError as e:
        error_msg = str(e)
        components[component_name] = lambda: show_dummy_component(display_name, error_msg)

# Bestehende Komponenten
load_component("overview", "components.overview", "Overview")
load_component("production_order", "components.production_order", "Production Order")
# ... bestehende Komponenten

# NEU: APS-Komponenten
load_component("aps_overview", "components.aps_overview", "APS Overview")
load_component("aps_steering", "components.aps_steering", "APS Steering")
load_component("aps_orders", "components.aps_orders", "APS Orders")
load_component("aps_configuration", "components.aps_configuration", "APS Configuration")
```

## Sicherheitshinweise

### **✅ Bestehende Funktionalität bleibt unberührt**
- **Keine Änderungen** an bestehenden Komponenten
- **Neue Komponenten** als separate Module
- **Wrapper-Pattern** für konsistente Struktur
- **Fehlertolerante** Komponenten-Loading

### **🛡️ Live-Demo Sicherheit**
- **Keine automatischen Reloads**
- **Keine Import-Änderungen**
- **Keine Tab-Struktur-Änderungen**
- **Bestehende Dashboard-Funktionalität unverändert**

## Nächste Schritte

### **1. Nach Live-Demo**
1. **APS-Komponenten** erstellen
2. **Tab-Struktur** erweitern
3. **Komponenten-Loading** erweitern
4. **Integration** testen

### **2. Testing**
1. **Unit Tests** für neue Komponenten
2. **Integration Tests** mit MQTT
3. **Dashboard Tests** mit APS-Simulation
4. **Live Tests** mit realer APS

### **3. Dokumentation**
1. **Komponenten-Dokumentation**
2. **Integration Guide**
3. **User Guide**
4. **Troubleshooting Guide**
