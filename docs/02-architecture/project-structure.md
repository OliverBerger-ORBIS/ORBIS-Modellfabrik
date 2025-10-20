# OMF2 Project Structure

**Status: VOLLSTÄNDIG DOKUMENTIERT** ✅  
**Datum: 2025-10-10**  
**Architektur: Drei-Schichten-Architektur mit Connection Loop Prevention**  
**CCU Overview Tab: KOMPLETT IMPLEMENTIERT** ✅  
**Asset Management: ICON-STYLE SWITCH IMPLEMENTIERT** ✅

## 🎯 Übersicht

Das OMF2 Projekt folgt einer professionellen **Drei-Schichten-Architektur** mit klarer Trennung der Verantwortlichkeiten:

```
┌─────────────────────┐
│   MQTT Broker       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  MQTT CLIENT        │  ← Transport Layer
│  - Raw MQTT         │
│  - JSON Parsing     │
│  - Meta-Parameter   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  GATEWAY            │  ← Validation & Routing Layer
│  - Schema-Validation│
│  - Topic-Routing    │
│  - Error-Handling   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  BUSINESS MANAGER   │  ← Business Logic Layer
│  - State-Holder     │
│  - Business Rules   │
│  - Data Processing  │
└─────────────────────┘
```

## 📁 Detaillierte Projektstruktur

```
omf2/
├── omf.py                           # 🚀 Streamlit Dashboard Entry Point
├── config/                          # ⚙️ Konfigurationsdateien
│   ├── mqtt_settings.yml           # MQTT-Verbindungseinstellungen
│   ├── logging_config.yml          # Logging-Konfiguration
│   ├── translations/               # 🌐 i18n Übersetzungsdateien ✅ NEW!
│   │   ├── de/                     # Deutsche Übersetzungen (195+ Keys)
│   │   │   ├── admin.yml           # Admin-Domain Übersetzungen
│   │   │   ├── ccu_*.yml           # CCU-Domain Übersetzungen (5 Tabs)
│   │   │   └── common.yml          # Gemeinsame Übersetzungen
│   │   ├── en/                     # English Übersetzungen
│   │   └── fr/                     # Français Übersetzungen
│   └── ccu/                        # 🏭 CCU Domain Configurations
│       ├── production_workflows.json # Production workflows (BLUE, WHITE, RED)
│       ├── production_settings.json  # Production durations and settings
│       └── shopfloor_layout.json     # Factory layout (3×4 grid)
│
├── admin/                          # 🔧 ADMIN DOMAIN
│   ├── admin_mqtt_client.py        # MQTT Client (Transport Layer)
│   └── admin_gateway.py            # Gateway (Validation & Routing)
│
├── ccu/                            # 🏭 CCU DOMAIN
│   ├── ccu_mqtt_client.py          # MQTT Client (Connection Loop Prevention)
│   ├── ccu_gateway.py              # Gateway (Validation & Routing + Order Management)
│   ├── config_loader.py            # CCU Config Loader (Domain-specific JSON configs)
│   ├── sensor_manager.py           # Business Manager (Sensor-Daten)
│   ├── module_manager.py           # Business Manager (Module-Daten)
│   ├── order_manager.py            # Business Manager (Inventory & Customer Orders) ✅
│   └── production_order_manager.py # Business Manager (Production & Storage Orders) ✅ NEW!
│
├── nodered/                        # 🔄 NODE-RED DOMAIN
│   ├── nodered_gateway.py          # Gateway (Validation & Routing)
│   └── nodered_manager.py          # Business Manager (Node-RED-Daten)
│
├── assets/                         # 🎨 ASSET MANAGEMENT
│   ├── __init__.py                # Asset Manager Package
│   ├── asset_manager.py           # SVG-Icon Management & HTML Generation
│   └── svgs/                      # SVG-Icon Library
│       ├── warehouse_40dp_*.svg   # HBW Module Icon
│       ├── tools_power_drill_40dp_*.svg # DRILL Module Icon
│       ├── construction_40dp_*.svg # MILL Module Icon
│       ├── robot_40dp_*.svg       # AIQS Module Icon
│       ├── conveyor_belt_40dp_*.svg # DPS Module Icon
│       ├── ev_station_40dp_*.svg  # CHRG Module Icon
│       └── add_2_40dp_*.svg       # Intersection Icon
│
├── common/                         # 🔗 SHARED COMPONENTS
│   ├── logger.py                   # Best Practice Logging-System
│   ├── registry_manager.py         # Registry Manager (Singleton)
│   ├── message_manager.py          # Domain-agnostic Message Manager
│   ├── topic_manager.py            # Domain-agnostic Topic Manager
│   ├── workpiece_manager.py        # Workpiece Icon Manager
│   └── i18n.py                     # 🌐 Internationalization Manager (DE, EN, FR) ✅ NEW!
│
├── factory/                        # 🏭 FACTORY PATTERN
│   ├── gateway_factory.py          # Gateway Factory (Singleton + Session State)
│   └── client_factory.py           # Client Factory (Singleton)
│
├── ui/                             # 🖥️ STREAMLIT UI COMPONENTS
│   ├── main_dashboard.py           # Haupt-Dashboard
│   ├── utils/                      # UI Utilities
│   │   ├── environment_switch.py   # Environment Switch mit automatischem UI-Refresh
│   │   └── ui_refresh.py           # UI Refresh Pattern
│   ├── admin/                      # Admin UI Components
│   │   ├── admin_dashboard.py      # Admin Dashboard
│   │   ├── message_center/         # Message Center UI
│   │   └── system_logs/            # System Logs UI
│   ├── ccu/                        # CCU UI Components
│   │   ├── ccu_dashboard.py        # CCU Dashboard
│   │   ├── ccu_message_monitor/    # CCU Message Monitor
│   │   ├── ccu_overview/           # CCU Overview Tab ✅ KOMPLETT
│   │   │   ├── ccu_overview_tab.py          # Main Tab (5 Subtabs)
│   │   │   ├── customer_order_subtab.py     # Customer Orders (BLUE→WHITE→RED, UISymbols, DRY)
│   │   │   ├── purchase_order_subtab.py     # Purchase Orders (Raw Material, Left-aligned)
│   │   │   ├── inventory_subtab.py          # Inventory (3x3 Grid A1-C3, Bucket Display)
│   │   │   ├── product_catalog_subtab.py    # Product Workflows (BLUE, WHITE, RED)
│   │   │   └── sensor_data_subtab.py        # Sensor Data Display (Temp, Pressure, Status)
│   │   ├── ccu_orders/             # CCU Orders Tab ✅ KOMPLETT REFACTORED
│   │   │   ├── ccu_orders_tab.py            # Main Tab (Wrapper mit 2 Subtabs)
│   │   │   ├── production_orders_subtab.py  # Production Orders (Active + Completed, 2-Spalten-Layout)
│   │   │   └── storage_orders_subtab.py     # Storage Orders (Active + Completed, 2-Spalten-Layout, UISymbols-konsistent)
│   │   ├── ccu_configuration/      # CCU Configuration UI
│   │   │   ├── ccu_configuration_tab.py
│   │   │   ├── ccu_parameter_configuration_subtab.py
│   │   │   └── ccu_factory_configuration_subtab.py # 🏗️ Shopfloor Layout Integration
│   │   ├── common/                 # 🏭 SHARED CCU COMPONENTS
│   │   │   └── shopfloor_layout.py # 🎯 Shopfloor Layout System (3×4 Grid, SVG-Icons)
│   │   ├── ccu_process/            # CCU Process UI
│   │   │   ├── ccu_process_tab.py
│   │   │   ├── ccu_production_plan_subtab.py
│   │   │   └── ccu_production_monitoring_subtab.py
│   │       └── shopfloor_layout.py # Reusable Shopfloor Layout Component
│   ├── nodered/                    # Node-RED UI Components
│   │   └── nodered_dashboard.py    # Node-RED Dashboard
│   └── common/                     # Shared UI Components
│       ├── symbols.py              # UI Symbols (UISymbols)
│       └── ui_refresh.py           # UI Refresh Pattern
│
├── assets/                         # 🎨 UI ASSETS
│   └── (legacy entfernt)           # HTML-Templates wurden ersetzt durch direkte SVG-Darstellung
│
├── registry/                       # 📋 REGISTRY V2 (Single Source of Truth)
│   ├── topics/                     # Topic-Definitionen
│   │   ├── admin.yml               # Admin Topics
│   │   ├── ccu.yml                 # CCU Topics
│   │   └── nodered.yml             # Node-RED Topics
│   ├── schemas/                    # JSON-Schemas für Validierung
│   │   ├── sensor_schemas/         # Sensor-Schemas (BME680, LDR, CAM)
│   │   ├── module_schemas/         # Module-Schemas
│   │   └── admin_schemas/          # Admin-Schemas
│   └── mqtt_clients.yml            # MQTT Client-Konfiguration
│
├── docs/                           # 📚 DOKUMENTATION
│   ├── ARCHITECTURE.md             # Vollständige Architektur-Dokumentation
│   ├── I18N_DEVELOPMENT_RULES.md   # 🌐 i18n Entwicklungsregeln ✅ NEW!
│   └── I18N_IMPLEMENTATION_COMPLETE.md # 🌐 i18n Implementierungsstatus ✅ NEW!
│
└── tests/                          # 🧪 TEST SUITE (55+ Tests)
    ├── test_comprehensive_architecture.py    # Architektur-Tests
    ├── test_gateway_factory.py               # Gateway Factory Tests
    ├── test_registry_manager_comprehensive.py # Registry Manager Tests
    ├── test_ccu_config_loader.py             # CCU Config Loader Tests
    ├── test_ccu_parameter_configuration_subtab.py # UI Component Tests
    ├── test_message_manager.py               # Message Manager Tests
    ├── test_topic_manager.py                 # Topic Manager Tests
    └── test_payloads_for_topics.py           # Schema-Validation Tests
```

## 🏗️ Architektur-Komponenten

### **🔌 MQTT CLIENT LAYER (Transport)**

**Verantwortlichkeiten:**
- Raw MQTT-Kommunikation
- JSON-Parsing und -Dekodierung
- Meta-Parameter-Extraktion (timestamp, qos, retain)
- Buffer-Management für UI-Monitoring
- Thread-sichere Operationen

**Implementierung:**
```python
# omf2/admin/admin_mqtt_client.py
class AdminMqttClient:
    def _on_message(self, client, userdata, msg):
        # Raw MQTT → Clean JSON
        topic = msg.topic
        payload_raw = msg.payload.decode('utf-8')
        message = json.loads(payload_raw)  # Dict/List/Str
        
        # Meta-Parameter
        meta = {
            "mqtt_timestamp": time.time(),
            "qos": msg.qos,
            "retain": msg.retain
        }
        
        # Gateway mit cleanen Daten aufrufen
        self._gateway.on_mqtt_message(topic, message, meta)
```

### **🚪 GATEWAY LAYER (Validation & Routing)**

**Verantwortlichkeiten:**
- Schema-Validierung mit Registry-Schemas
- Topic-Routing (Set-basiert + Präfix-basiert)
- Error-Handling mit detailliertem Logging
- Clean Data Contract (NIE raw bytes an Manager)
- Domain-spezifische Logik

**Implementierung:**
```python
# omf2/admin/admin_gateway.py
class AdminGateway:
    def on_mqtt_message(self, topic, message, meta=None):
        # 1. Schema-Validierung
        schema = self.registry_manager.get_topic_schema(topic)
        if schema:
            validated_message = self._validate_message(topic, message, schema)
            if not validated_message:
                return False
        
        # 2. Topic-Routing
        return self._route_message(topic, validated_message, meta)
```

### **🏢 BUSINESS MANAGER LAYER (Business Logic)**

**Verantwortlichkeiten:**
- Business-Logik und State-Management
- Schema-basierte Datenverarbeitung
- Clean API für UI-Komponenten
- Thread-safe State-Holder Pattern
- Domain-spezifische Business Rules

**Implementierung:**
```python
# omf2/ccu/sensor_manager.py
class SensorManager:
    def __init__(self):
        self.sensor_data = {}  # State-Holder
    
    def process_sensor_message(self, topic, payload):
        # Direkte Payload-Verarbeitung
        processed_data = self._extract_sensor_data(topic, payload)
        self.sensor_data[topic] = processed_data
    
    def get_sensor_data(self, sensor_id=None):
        # UI liest aus State-Holder
        return self.sensor_data.get(sensor_id) if sensor_id else self.sensor_data
```

## 🎯 Architektur-Prinzipien

### **1. Separation of Concerns**
- **MQTT Client:** Nur Transport und Parsing
- **Gateway:** Nur Validierung und Routing
- **Business Manager:** Nur Business-Logik und State

### **2. Clean Data Contract**
- Manager erhalten immer Dict/List/Str - NIE raw bytes
- Meta-Parameter getrennt von Business-Daten
- Schema-Validierung im Gateway, nicht im Manager

### **3. Thread-Safety**
- Alle Komponenten sind thread-safe
- Singleton Pattern für zentrale Instanzen
- Threading.Lock() für kritische Bereiche

### **4. Schema-Driven Architecture**
- Registry v2 als Single Source of Truth
- JSON-Schema-Validierung für alle Topics
- Topic-Schema-Mapping für automatische Validierung

### **5. Best Practice Logging**
- Level-spezifische Ringbuffer (ERROR, WARNING, INFO, DEBUG)
- Thread-sichere Log-Zugriffe
- UI-Integration mit dedizierten Error & Warning Tabs

## 🧪 Testing-Strategie

### **Test-Abdeckung:**
- **55 erfolgreiche Tests** für die gesamte Architektur
- **Unit Tests** für alle Komponenten
- **Integration Tests** für Architektur-Schichten
- **Schema-Validation Tests** mit echten Payloads

### **Test-Ausführung:**
```bash
# Alle Tests
python -m pytest tests/test_omf2 -v

# Spezifische Test-Suites
python -m pytest tests/test_omf2/test_comprehensive_architecture.py -v
python -m pytest tests/test_omf2/test_gateway_factory.py -v
python -m pytest tests/test_omf2/test_registry_manager_comprehensive.py -v
python -m pytest tests/test_omf2/test_ccu_config_loader.py -v
python -m pytest tests/test_omf2/test_ccu_parameter_configuration_subtab.py -v
```

## 🚀 Deployment

### **Schnellstart:**
```bash
# Virtual Environment aktivieren
source .venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# OMF2 Dashboard starten
streamlit run omf2/omf.py
```

### **Konfiguration:**
- **MQTT-Settings:** `omf2/config/mqtt_settings.yml`
- **Logging-Config:** `omf2/config/logging_config.yml`
- **Registry-Schemas:** `omf2/registry/schemas/`

## 📊 Vorteile der Architektur

### **Wartbarkeit:**
- Klare Trennung der Verantwortlichkeiten
- Modulare Komponenten
- Zentrale Konfiguration

### **Skalierbarkeit:**
- Domain-spezifische Komponenten
- Factory Pattern für Singleton-Management
- Registry-basierte Konfiguration

### **Testbarkeit:**
- Isolierte Komponenten
- Clean APIs
- Mock-freundliche Architektur

## 🧪 Test-Struktur

```
tests/test_omf2/
├── __init__.py
├── test_shopfloor/              # 🏭 Shopfloor Layout Tests
│   ├── __init__.py
│   ├── test_aspect_ratio_test.py
│   ├── test_clean_test.py
│   ├── test_debug.py
│   ├── test_demo.py
│   ├── test_fixed_aspect_test.py
│   ├── test_html_test.py
│   ├── test_shopfloor_test.py
│   └── test_shopfloor_verification.py
└── test_helper_apps/            # Helper App Tests
```

### **Robustheit:**
- Thread-sichere Operationen
- Schema-Validierung
- Umfassendes Error-Handling

---

## 🆕 Neue Features (2025-10-08)

### **Production Order Manager:**
- ✅ **Order-Lifecycle Management** (active → completed)
- ✅ **STORAGE vs PRODUCTION** Unterscheidung
- ✅ **Order-ID-basierte Zuordnung** (Dict statt Array)
- ✅ **Kompletter Produktionsplan** mit MQTT-Status-Overlay
- ✅ **Zentrale Validierung** über MessageManager
- ✅ **Log-Rotation** (max 10MB pro Datei, 5 Backups)

### **Storage Orders Implementation:**
- ✅ **Storage Orders Logic** vollständig implementiert
- ✅ **UI-Konsistenz** zwischen Production und Storage Orders
- ✅ **Command-Mapping-Korrektur** (PICK/DROP → LADEN/ENTLADEN AGV)
- ✅ **Shopfloor Layout Integration** für Storage Orders
- ✅ **Navigation Step Enhancement** (UX-Verbesserung)
- ✅ **UISymbols-Konsistenz** (🟠 statt 🔄 für IN_PROGRESS)

### **UI Refactoring:**
- ✅ **CCU Orders Tab** mit zwei Subtabs (Production vs Storage)
- ✅ **Completed Orders Anzeige** (ausgegraut unterhalb Active)
- ✅ **Unterschiedliche Darstellung** für STORAGE (4 Steps) vs PRODUCTION (11+ Steps)

---

**Letzte Aktualisierung:** 2025-10-10  
**Status:** VOLLSTÄNDIG IMPLEMENTIERT ✅  
**Architektur:** DREI-SCHICHTEN-ARCHITEKTUR ✅  
**Tests:** 55 ERFOLGREICHE TESTS ✅  
**Dokumentation:** VOLLSTÄNDIG ✅  
**Production Order Manager:** ✅ VOLLSTÄNDIG ✅  
**i18n-Implementierung:** ✅ VOLLSTÄNDIG (DE, EN, FR) ✅ NEW!