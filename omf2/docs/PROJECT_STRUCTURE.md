# OMF2 Project Structure

**Status: VOLLSTÄNDIG DOKUMENTIERT** ✅  
**Datum: 2025-10-08**  
**Architektur: Drei-Schichten-Architektur mit Connection Loop Prevention**  
**CCU Overview Tab: KOMPLETT IMPLEMENTIERT** ✅

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
│   └── order_manager.py            # Business Manager (Inventory & Order Management) ✅
│
├── nodered/                        # 🔄 NODE-RED DOMAIN
│   ├── nodered_gateway.py          # Gateway (Validation & Routing)
│   └── nodered_manager.py          # Business Manager (Node-RED-Daten)
│
├── common/                         # 🔗 SHARED COMPONENTS
│   ├── logger.py                   # Best Practice Logging-System
│   ├── registry_manager.py         # Registry Manager (Singleton)
│   ├── message_manager.py          # Domain-agnostic Message Manager
│   ├── topic_manager.py            # Domain-agnostic Topic Manager
│   └── workpiece_manager.py        # Workpiece Icon Manager
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
│   │   ├── ccu_configuration/      # CCU Configuration UI
│   │   │   ├── ccu_configuration_tab.py
│   │   │   ├── ccu_parameter_configuration_subtab.py
│   │   │   └── ccu_factory_configuration_subtab.py
│   │   ├── ccu_process/            # CCU Process UI
│   │   │   ├── ccu_process_tab.py
│   │   │   ├── ccu_production_plan_subtab.py
│   │   │   └── ccu_production_monitoring_subtab.py
│   │   └── common/                 # CCU Shared UI Components
│   │       └── shopfloor_layout.py # Reusable Shopfloor Layout Component
│   ├── nodered/                    # Node-RED UI Components
│   │   └── nodered_dashboard.py    # Node-RED Dashboard
│   └── common/                     # Shared UI Components
│       ├── symbols.py              # UI Symbols (UISymbols)
│       └── ui_refresh.py           # UI Refresh Pattern
│
├── assets/                         # 🎨 UI ASSETS
│   └── html_templates.py           # HTML Templates (Bucket, Workpiece Box) ✅
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
│   └── ARCHITECTURE.md             # Vollständige Architektur-Dokumentation
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
python -m pytest omf2/tests/ -v

# Spezifische Test-Suites
python -m pytest omf2/tests/test_comprehensive_architecture.py -v
python -m pytest omf2/tests/test_gateway_factory.py -v
python -m pytest omf2/tests/test_registry_manager_comprehensive.py -v
python -m pytest omf2/tests/test_ccu_config_loader.py -v
python -m pytest omf2/tests/test_ccu_parameter_configuration_subtab.py -v
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

### **Robustheit:**
- Thread-sichere Operationen
- Schema-Validierung
- Umfassendes Error-Handling

---

**Letzte Aktualisierung:** 2025-10-06  
**Status:** VOLLSTÄNDIG IMPLEMENTIERT ✅  
**Architektur:** DREI-SCHICHTEN-ARCHITEKTUR ✅  
**Tests:** 55 ERFOLGREICHE TESTS ✅  
**Dokumentation:** VOLLSTÄNDIG ✅