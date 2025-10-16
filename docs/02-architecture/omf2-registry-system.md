# OMF2 Registry System - Complete Implementation Guide

**Version:** 1.0  
**Last updated:** 2025-10-16  
**Author:** OMF Development Team  

---

## 🎯 **Überblick**

Das **OMF2 Registry System** ist die zentrale Datenquelle für alle OMF-Entitäten. Es verwaltet Topics, Schemas, Module, Workpieces, Stations, TXT Controllers und MQTT Clients über einen **RegistryManager Singleton**.

**Keine Versionierung** - direkte Struktur in `omf2/registry/`

---

## 🏗️ **System-Architektur**

### **RegistryManager Singleton Pattern**

```python
from omf2.registry.manager.registry_manager import get_registry_manager

# Singleton Factory - nur eine Instanz pro Anwendung
registry_manager = get_registry_manager("omf2/registry/")
```

### **Registry-Struktur**

```
omf2/registry/
├── manager/
│   └── registry_manager.py          # RegistryManager Singleton
├── topics/                          # Topic-Definitionen (YAML)
│   ├── ccu.yml                      # CCU Topics
│   ├── fts.yml                      # FTS Topics
│   ├── module.yml                   # Module Topics
│   ├── nodered.yml                  # NodeRED Topics
│   └── txt.yml                      # TXT Controller Topics
├── schemas/                         # JSON Schemas (ersetzen Templates)
│   ├── ccu_*.schema.json           # CCU Schemas
│   ├── fts_*.schema.json           # FTS Schemas
│   ├── module_*.schema.json        # Module Schemas
│   ├── nodered_*.schema.json       # NodeRED Schemas
│   └── txt_*.schema.json           # TXT Controller Schemas
├── modules.yml                      # Module-Definitionen
├── mqtt_clients.yml                # MQTT Client-Konfiguration
├── workpieces.yml                  # Workpiece-Definitionen
├── stations.yml                    # Station-Definitionen
├── txt_controllers.yml             # TXT Controller-Definitionen
└── products.yml                    # Product-Definitionen
```

---

## 🔧 **RegistryManager API**

### **Singleton Factory**

```python
from omf2.registry.manager.registry_manager import get_registry_manager

# Registry Manager abrufen (Singleton)
registry = get_registry_manager("omf2/registry/")
```

### **Topics abrufen**

```python
# Alle Topics
topics = registry.get_topics()

# Topics nach Domain
ccu_topics = registry.get_topics_by_domain('ccu')
module_topics = registry.get_topics_by_domain('module')

# Topic-Info für spezifischen Topic
topic_info = registry.get_topic_info("module/v1/ff/SVR4H76449/state")
```

### **Schemas abrufen**

```python
# Alle Schemas
schemas = registry.get_schemas()

# Schemas nach Domain
ccu_schemas = registry.get_schemas_by_domain('ccu')
module_schemas = registry.get_schemas_by_domain('module')

# Schema für spezifischen Topic
schema = registry.get_schema_by_topic("module/v1/ff/SVR4H76449/state")
```

### **Module abrufen**

```python
# Alle Module
modules = registry.get_modules()

# Modul nach Serial Number
drill_module = registry.get_module_by_serial('SVR4H76449')
hbw_module = registry.get_module_by_serial('SVR3QA0022')

# Module nach Typ
drill_modules = registry.get_modules_by_type('drill')
hbw_modules = registry.get_modules_by_type('hbw')
```

### **Workpieces abrufen**

```python
# Alle Workpieces
workpieces = registry.get_workpieces()

# Workpieces nach Status
active_workpieces = registry.get_workpieces_by_status('active')
completed_workpieces = registry.get_workpieces_by_status('completed')

# Workpiece nach ID
workpiece = registry.get_workpiece_by_id('workpiece_001')
```

### **Stations abrufen**

```python
# Alle Stations
stations = registry.get_stations()

# Station nach ID
hbw_station = registry.get_station_by_id('hbw')
drill_station = registry.get_station_by_id('drill')

# Stations nach Typ
processing_stations = registry.get_stations_by_type('processing')
storage_stations = registry.get_stations_by_type('storage')
```

### **TXT Controllers abrufen**

```python
# Alle TXT Controllers
txt_controllers = registry.get_txt_controllers()

# TXT Controller nach ID
controller_1 = registry.get_txt_controller_by_id('controller_1')
controller_2 = registry.get_txt_controller_by_id('controller_2')

# TXT Controllers nach Typ
input_controllers = registry.get_txt_controllers_by_type('input')
output_controllers = registry.get_txt_controllers_by_type('output')
```

### **MQTT Clients abrufen**

```python
# Alle MQTT Clients
mqtt_clients = registry.get_mqtt_clients()

# MQTT Client-Konfiguration
ccu_client = registry.get_mqtt_client_config('ccu_mqtt_client')
admin_client = registry.get_mqtt_client_config('admin_mqtt_client')

# MQTT Client nach Domain
ccu_clients = registry.get_mqtt_clients_by_domain('ccu')
admin_clients = registry.get_mqtt_clients_by_domain('admin')
```

---

## 🎨 **Verwendung in Komponenten**

### **1. Gateway-Pattern**

```python
from omf2.registry.manager.registry_manager import get_registry_manager

class CCUGateway:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.registry_manager = get_registry_manager()
        
    def process_message(self, topic: str, payload: dict):
        # Topic-Info abrufen
        topic_info = self.registry_manager.get_topic_info(topic)
        if not topic_info:
            logger.warning(f"Unknown topic: {topic}")
            return
        
        # Schema-Validierung
        schema = self.registry_manager.get_schema_by_topic(topic)
        if schema:
            # JSON Schema-Validierung
            self._validate_payload(payload, schema)
        
        # Business Logic
        self._process_business_logic(topic_info, payload)
```

### **2. UI-Komponenten**

```python
from omf2.registry.manager.registry_manager import get_registry_manager

def render_module_overview():
    registry = get_registry_manager()
    
    # Module für UI abrufen
    modules = registry.get_modules()
    
    st.subheader("Module Overview")
    
    for serial, module_info in modules.items():
        with st.expander(f"{module_info['name']} ({serial})"):
            st.write(f"**Type:** {module_info['type']}")
            st.write(f"**Status:** {module_info['status']}")
            st.write(f"**Location:** {module_info['location']}")
            
            # Module-spezifische Topics
            module_topics = registry.get_topics_by_domain('module')
            for topic in module_topics:
                if serial in topic:
                    st.write(f"**Topic:** {topic}")
```

### **3. Business Manager**

```python
from omf2.registry.manager.registry_manager import get_registry_manager

class ModuleManager:
    def __init__(self, registry_manager=None):
        self.registry_manager = registry_manager or get_registry_manager()
        self._initialized = False
        
    def initialize(self):
        """Initialize Module Manager with Registry data"""
        modules = self.registry_manager.get_modules()
        
        for serial, module_info in modules.items():
            self._setup_module(serial, module_info)
        
        self._initialized = True
        logger.info(f"Module Manager initialized with {len(modules)} modules")
    
    def get_module_status(self, serial: str) -> dict:
        """Get module status from Registry"""
        module = self.registry_manager.get_module_by_serial(serial)
        if not module:
            raise ValueError(f"Module {serial} not found in Registry")
        
        return {
            'serial': serial,
            'name': module['name'],
            'type': module['type'],
            'status': module['status'],
            'location': module['location']
        }
```

### **4. Topic-Routing**

```python
from omf2.registry.manager.registry_manager import get_registry_manager

def route_message(topic: str, payload: dict):
    """Route message based on Registry configuration"""
    registry = get_registry_manager()
    
    # Topic-Info abrufen
    topic_info = registry.get_topic_info(topic)
    if not topic_info:
        logger.warning(f"Unknown topic: {topic}")
        return
    
    # Domain-basierte Weiterleitung
    domain = topic_info.get('domain')
    
    if domain == 'ccu':
        ccu_gateway.process_message(topic, payload)
    elif domain == 'module':
        module_gateway.process_message(topic, payload)
    elif domain == 'txt':
        txt_gateway.process_message(topic, payload)
    else:
        logger.warning(f"Unknown domain: {domain}")
```

---

## 🧪 **Testing**

### **Registry Manager Tests**

```python
import unittest
from omf2.registry.manager.registry_manager import get_registry_manager, RegistryManager

class TestRegistryManager(unittest.TestCase):
    def setUp(self):
        """Setup für jeden Test"""
        # Reset Singleton für saubere Tests
        RegistryManager._instance = None
        RegistryManager._initialized = False
    
    def test_singleton_pattern(self):
        """Test Singleton Pattern"""
        registry1 = get_registry_manager()
        registry2 = get_registry_manager()
        
        self.assertIs(registry1, registry2)
    
    def test_topics_loading(self):
        """Test Topics loading"""
        registry = get_registry_manager()
        topics = registry.get_topics()
        
        self.assertIsInstance(topics, dict)
        self.assertGreater(len(topics), 0)
    
    def test_schemas_loading(self):
        """Test Schemas loading"""
        registry = get_registry_manager()
        schemas = registry.get_schemas()
        
        self.assertIsInstance(schemas, dict)
        self.assertGreater(len(schemas), 0)
    
    def test_modules_loading(self):
        """Test Modules loading"""
        registry = get_registry_manager()
        modules = registry.get_modules()
        
        self.assertIsInstance(modules, dict)
        self.assertGreater(len(modules), 0)
    
    def test_module_by_serial(self):
        """Test Module by Serial Number"""
        registry = get_registry_manager()
        
        # Test existing module
        drill_module = registry.get_module_by_serial('SVR4H76449')
        self.assertIsNotNone(drill_module)
        self.assertEqual(drill_module['type'], 'drill')
        
        # Test non-existing module
        non_existing = registry.get_module_by_serial('NON_EXISTING')
        self.assertIsNone(non_existing)
```

---

## 📊 **Performance & Monitoring**

### **Registry Loading Performance**

```python
# Registry Loading Statistics
registry = get_registry_manager()

# Lade-Statistiken
load_timestamp = registry._load_timestamp
topics_count = len(registry.get_topics())
schemas_count = len(registry.get_schemas())
modules_count = len(registry.get_modules())

logger.info(f"Registry loaded: {topics_count} topics, {schemas_count} schemas, {modules_count} modules")
```

### **Memory Usage**

```python
# Registry Memory Usage
import sys

registry = get_registry_manager()
memory_usage = sys.getsizeof(registry)

logger.info(f"Registry memory usage: {memory_usage} bytes")
```

---

## 🎯 **Best Practices**

### **1. Registry Manager verwenden**

```python
# ✅ KORREKT: RegistryManager verwenden
from omf2.registry.manager.registry_manager import get_registry_manager

registry = get_registry_manager()
modules = registry.get_modules()
```

```python
# ❌ FALSCH: Direkte Datei-Zugriffe
import yaml
with open('omf2/registry/modules.yml') as f:
    modules = yaml.safe_load(f)
```

### **2. Singleton Pattern respektieren**

```python
# ✅ KORREKT: Singleton Factory verwenden
registry = get_registry_manager()

# ❌ FALSCH: Direkte Instanziierung
registry = RegistryManager()
```

### **3. Error Handling**

```python
# ✅ KORREKT: Error Handling
def get_module_info(serial: str):
    registry = get_registry_manager()
    
    module = registry.get_module_by_serial(serial)
    if not module:
        logger.error(f"Module {serial} not found in Registry")
        return None
    
    return module
```

### **4. Domain-basierte Zugriffe**

```python
# ✅ KORREKT: Domain-basierte Zugriffe
def process_ccu_messages():
    registry = get_registry_manager()
    
    ccu_topics = registry.get_topics_by_domain('ccu')
    ccu_schemas = registry.get_schemas_by_domain('ccu')
    
    for topic in ccu_topics:
        schema = registry.get_schema_by_topic(topic)
        # Process topic with schema
```

---

## 🚨 **Troubleshooting**

### **Problem: Registry nicht geladen**

```python
# Debug: Registry-Status prüfen
registry = get_registry_manager()

if not registry._initialized:
    logger.error("Registry not initialized")
    return

topics = registry.get_topics()
if not topics:
    logger.error("No topics loaded from Registry")
    return
```

### **Problem: Modul nicht gefunden**

```python
# Debug: Alle Module auflisten
registry = get_registry_manager()
modules = registry.get_modules()

logger.info(f"Available modules: {list(modules.keys())}")

# Spezifisches Modul suchen
target_serial = 'SVR4H76449'
if target_serial in modules:
    logger.info(f"Module {target_serial} found: {modules[target_serial]}")
else:
    logger.error(f"Module {target_serial} not found in Registry")
```

### **Problem: Topic nicht gefunden**

```python
# Debug: Alle Topics auflisten
registry = get_registry_manager()
topics = registry.get_topics()

logger.info(f"Available topics: {list(topics.keys())}")

# Spezifisches Topic suchen
target_topic = "module/v1/ff/SVR4H76449/state"
if target_topic in topics:
    logger.info(f"Topic {target_topic} found: {topics[target_topic]}")
else:
    logger.error(f"Topic {target_topic} not found in Registry")
```

---

## 📚 **Referenz-Implementierungen**

### **Gateway-Pattern:**
- `omf2/ccu/ccu_gateway.py` - CCU Gateway mit Registry
- `omf2/admin/admin_gateway.py` - Admin Gateway mit Registry

### **UI-Komponenten:**
- `omf2/ui/ccu/ccu_modules/ccu_modules_tab.py` - Module UI mit Registry
- `omf2/ui/admin/admin_settings/` - Admin Settings mit Registry

### **Business Manager:**
- `omf2/ccu/module_manager.py` - Module Manager mit Registry
- `omf2/ccu/sensor_manager.py` - Sensor Manager mit Registry

### **Tests:**
- `omf2/tests/test_registry_manager_comprehensive.py` - Registry Manager Tests
- `omf2/tests/test_schema_integration.py` - Schema Integration Tests

---

## 🎯 **Zusammenfassung**

### **Das Wichtigste:**

1. **RegistryManager Singleton verwenden** - `get_registry_manager()`
2. **Keine direkten Datei-Zugriffe** - immer über RegistryManager
3. **Domain-basierte Zugriffe** - `get_topics_by_domain()`, `get_schemas_by_domain()`
4. **Error Handling** - prüfen ob Entitäten existieren
5. **Singleton Pattern respektieren** - nur eine Instanz pro Anwendung

### **Verifikation:**

- ✅ Registry Manager lädt alle Entitäten korrekt
- ✅ Topics, Schemas, Module, Workpieces, Stations, TXT Controllers verfügbar
- ✅ Domain-basierte Zugriffe funktionieren
- ✅ Singleton Pattern wird eingehalten
- ✅ Error Handling für nicht-existierende Entitäten

---

*Letzte Aktualisierung: 2025-10-16*
