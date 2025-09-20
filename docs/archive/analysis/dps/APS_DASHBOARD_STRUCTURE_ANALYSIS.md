# APS Dashboard Structure Analysis

## Overview
Analyse der Menüstruktur und Funktionalität des APS-Dashboards basierend auf der OMF-Dashboard-Implementierung und den TXT Controller-Programmen.

## Hauptmenü-Struktur (Tabs)

### **1. 📊 Übersicht (Overview)**
**Funktion**: Zentrale Übersicht über alle Systemkomponenten

#### **Untertabs:**
- **🏭 Modul Status** - Aktuelle Status aller Module
- **📋 Kundenaufträge** - Externe Kundenbestellungen
- **📊 Rohmaterial-Bestellungen** - Purchase Orders
- **📦 Lagerbestand** - Inventory Management
- **📦 Produktkatalog** - Product Catalog

#### **Implementierung:**
```python
def show_overview():
    overview_tab1, overview_tab2, overview_tab3, overview_tab4, overview_tab5 = st.tabs([
        "🏭 Modul Status", 
        "📋 Kundenaufträge", 
        "📊 Rohmaterial-Bestellungen", 
        "📦 Lagerbestand", 
        "📦 Produktkatalog"
    ])
```

### **2. 🏭 Fertigungsaufträge (Production Orders)**
**Funktion**: Interne Fertigungsaufträge und Produktionsplanung

#### **Untertabs:**
- **📋 Produktplanung** - Production Planning
- **📋 Fertigungsauftrags-Verwaltung** - Order Management
- **🔄 Laufende Fertigungsaufträge** - Current Orders

#### **Implementierung:**
```python
def show_production_order():
    order_tab1, order_tab2, order_tab3 = st.tabs([
        "📋 Produktplanung",
        "📋 Fertigungsauftrags-Verwaltung", 
        "🔄 Laufende Fertigungsaufträge"
    ])
```

### **3. 📡 Nachrichten-Zentrale (Message Center)**
**Funktion**: MQTT-Nachrichtenüberwachung und -verwaltung

#### **Features:**
- **Prioritäts-Filter**: 1=Kritisch, 2=Wichtig, 3=Normal, 4=UI, 5=Spezifisch, 6=Alle
- **Live-Monitoring**: Echtzeit-Nachrichtenüberwachung
- **Message Processing**: Nachrichtenverarbeitung und -filterung

### **4. 🎮 Steuerung (Steering)**
**Funktion**: Direkte Steuerung der APS-Module

#### **Unterkomponenten:**
- **Factory Steering**: Gesamte Fabrik-Steuerung
- **Generic Steering**: Allgemeine Steuerungsfunktionen
- **Sequence Steering**: Sequenzielle Steuerung

#### **Commands:**
- **Bestellung RED/BLUE/WHITE**: VDA5050 Order-System
- **Factory Reset**: `ccu/set/reset`
- **FTS Charge**: `ccu/set/charge`
- **Module Control**: Direkte Modulsteuerung

### **5. 🏗️ Shopfloor**
**Funktion**: Shopfloor-Layout und -Management

#### **Unterkomponenten:**
- **Layout Management**: Shopfloor-Layout
- **Positioning**: Modul-Positionierung
- **Routes**: Transport-Routen
- **Utils**: Shopfloor-Utilities

### **6. 🚛 FTS (Fahrerloses Transport-System)**
**Funktion**: FTS-Steuerung und -Überwachung

#### **Unterkomponenten:**
- **FTS Connection**: Verbindungsstatus
- **FTS Factsheet**: FTS-Informationen
- **FTS Instant Action**: Sofort-Aktionen
- **FTS Order**: FTS-Bestellungen
- **FTS State**: FTS-Status

### **7. 🏢 CCU (Central Control Unit)**
**Funktion**: Zentrale Steuerungseinheit (DPS TXT Controller)

#### **Unterkomponenten:**
- **CCU Control**: CCU-Steuerung
- **CCU Pairing**: Modul-Pairing
- **CCU Set**: CCU-Einstellungen
- **CCU State**: CCU-Status
- **CCU Status**: CCU-Status-Überwachung

### **8. ⚙️ Einstellungen (Settings)**
**Funktion**: Systemkonfiguration und -einstellungen

#### **Untertabs:**
- **⚙️ Dashboard** - Dashboard-Einstellungen
- **🏭 Module** - Modul-Konfiguration
- **📱 NFC** - NFC-Konfiguration
- **🔗 MQTT** - MQTT-Konfiguration
- **📡 Topics** - Topic-Konfiguration
- **📋 Templates** - Message-Templates

### **9. 🔧 Modul-Steuerung (Module Control)**
**Funktion**: Direkte Steuerung einzelner Module

#### **Features:**
- **Module State Control**: Modul-Status-Steuerung
- **Individual Module Control**: Einzelne Modulsteuerung
- **Module Configuration**: Modul-Konfiguration

### **10. 📋 Logs**
**Funktion**: System-Logs und -Überwachung

#### **Features:**
- **Live Logs**: Echtzeit-Log-Überwachung
- **Log Filtering**: Log-Filterung
- **Log Analysis**: Log-Analyse

## Sidebar-Funktionen

### **1. Umgebungsauswahl**
```python
env_options = ["live", "replay", "mock"]
env = st.sidebar.radio("Umgebung", env_options, ...)
```

### **2. Nachrichten-Zentrale**
```python
priority = st.sidebar.select_slider(
    "Priorität",
    options=[1, 2, 3, 4, 5, 6],
    help="1=Kritisch, 2=Wichtig, 3=Normal, 4=UI, 5=Spezifisch, 6=Alle"
)
```

### **3. MQTT Status**
- **Verbindungsstatus**: Live/Replay/Mock
- **Statistiken**: Empfangen/Gesendet
- **Client-ID**: MQTT-Client-Identifikation

### **4. Aktualisierung**
- **Seite aktualisieren**: `st.rerun()`
- **MQTT-Refresh**: Subscription-Refresh

## MQTT-Integration

### **Order-System (VDA5050)**
```python
# Order Topics
order_topic = f"module/v1/ff/NodeRed/{controller_id}/order"
instant_action_topic = f"module/v1/ff/NodeRed/{controller_id}/instantActions"

# System Control Topics
ccu_topics = [
    "ccu/set/reset",
    "ccu/set/charge", 
    "ccu/set/layout",
    "ccu/set/flows",
    "ccu/set/calibration"
]
```

### **Dashboard Commands**
```python
# Bestellung Commands
def send_order(color):
    order = {
        "orderId": generate_order_id(),
        "timestamp": get_timestamp(),
        "action": "STORAGE",
        "type": color
    }
    mqtt_client.publish(order_topic, json.dumps(order))

# System Commands  
def send_system_command(command):
    mqtt_client.publish(f"ccu/set/{command}", payload)
```

## Komponenten-Architektur

### **Wrapper-Pattern**
```python
def show_component():
    """Hauptfunktion mit Untertabs"""
    tab1, tab2, tab3 = st.tabs(["Tab1", "Tab2", "Tab3"])
    
    with tab1:
        show_sub_component1()
    with tab2:
        show_sub_component2()
```

### **Fehlertolerante Komponenten**
```python
def load_component(component_name, import_path, display_name=None):
    """Lädt eine Komponente fehlertolerant"""
    try:
        module = __import__(import_path, fromlist=[f"show_{component_name}"])
        show_function = getattr(module, f"show_{component_name}")
        components[component_name] = show_function
    except ImportError as e:
        components[component_name] = lambda: show_dummy_component(display_name, str(e))
```

## Implementierung für OMF Dashboard

### **1. Menüstruktur beibehalten**
- **Haupttabs**: 10 Hauptkategorien
- **Untertabs**: Detaillierte Funktionsbereiche
- **Sidebar**: Umgebung, Priorität, MQTT-Status

### **2. MQTT-Integration**
- **VDA5050-konforme Orders**: Für Bestellungen
- **System Control Topics**: Für Steuerungsbefehle
- **Live-Monitoring**: Echtzeit-Überwachung

### **3. Komponenten-Architektur**
- **Wrapper-Pattern**: Hauptkomponenten mit Untertabs
- **Fehlertoleranz**: Graceful degradation
- **Modularität**: Einzelne Komponenten austauschbar

### **4. Dashboard-Commands Mapping**
- **"Bestellung RED/BLUE/WHITE"** → VDA5050 Order-System
- **"Factory Reset"** → `ccu/set/reset`
- **"FTS Charge"** → `ccu/set/charge`
- **"Module Control"** → Direkte Modulsteuerung

## Nächste Schritte

1. **Komponenten-Mapping**: OMF-Komponenten zu APS-Funktionen
2. **MQTT-Topic-Mapping**: Korrekte Topic-Zuordnung
3. **Command-Implementation**: Dashboard-Commands implementieren
4. **UI-Adaptation**: APS-Dashboard-UI nachbauen
5. **Testing**: Integration mit realer APS testen

## Dateien für weitere Analyse

1. **omf/dashboard/omf_dashboard.py** - Hauptnavigation
2. **omf/dashboard/components/overview.py** - Overview-Implementierung
3. **omf/dashboard/components/production_order.py** - Production Orders
4. **omf/dashboard/components/settings.py** - Settings-Implementierung
5. **omf/dashboard/components/steering.py** - Steering-Implementierung
