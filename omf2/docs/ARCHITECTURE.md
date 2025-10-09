# ✅ IMPLEMENTIERTE ARCHITEKTUR: Gekapseltes MQTT, Registry Manager & Gateway für Streamlit-Apps

**Status: VOLLSTÄNDIG IMPLEMENTIERT** ✅  
**Datum: 2025-10-09**  
**Tests: 55 Tests erfolgreich** ✅  
**Registry-Migration: ABGESCHLOSSEN** ✅  
**Architektur-Cleanup: ABGESCHLOSSEN** ✅  
**Schema-Validation: SYSTEMATISCH KORRIGIERT** ✅  
**Gateway-Routing: MIT SCHEMA-VALIDIERUNG IMPLEMENTIERT** ✅  
**Meta-Parameter: VOLLSTÄNDIG INTEGRIERT** ✅  
**Production Order Manager: VOLLSTÄNDIG IMPLEMENTIERT** ✅  
**Log-Rotation: IMPLEMENTIERT** ✅  
**Asymmetrische Architektur: VERIFIED UND DOKUMENTIERT** ✅ NEW!  
**Gateway-Routing-Hints: KLARGESTELLT** ✅ NEW!

**Ziel:**  
Weggekapselte, robuste Architektur für MQTT-Kommunikation, Message-Templates und UI-Refresh in einer Streamlit-App, sodass UI- und Business-Logik möglichst einfach bleiben und typische Fehlerquellen (Threading, Race-Conditions, Deadlocks, inkonsistenter State) vermieden werden.

**✅ ERREICHT:** Alle Ziele wurden erfolgreich implementiert und getestet.

**🔧 AKTUELLE ERKENNTNISSE (2025-10-09):**
- **Asymmetrische Architektur (VERIFIED)**: Commands über NodeRed, Telemetry direct für TXT-Module
- **Gateway-Routing-Hints**: `routed_topics` statt `subscribed_topics` - Semantik klargestellt
- **Topic-Semantische Felder**: `observed_publisher_aps`, `semantic_role`, `omf2_usage` für Guidance
- **OMF2 CCU-Domain**: Frontend + Backend in einer Domain (kann parallel zu APS-CCU-Backend laufen)
- **Production Order Manager**: Order-Lifecycle Management (active → completed) implementiert
- **STORAGE vs PRODUCTION**: Unterschiedliche Workflows korrekt unterschieden
- **Order-ID-basierte Zuordnung**: Dict statt Array für effiziente Lookups
- **Log-Rotation**: RotatingFileHandler (max 10MB, 5 Backups) verhindert 800MB Log-Dateien
- **Zentrale Validierung**: MessageManager übernimmt alle Schema-Validierung (keine Duplikate)
- **UI Refactoring**: CCU Orders Tab mit zwei Subtabs (Production vs Storage)
- **Completed Orders**: Werden aus active_orders entfernt und separat angezeigt (ausgegraut)
- **Schema-Validation Problem gelöst**: Falsche Schema-Zuordnungen in `txt.yml` korrigiert
- **Message Processing Pattern**: Registry Manager für Payload-Validierung statt MessageManager
- **Topic-Schema-Mapping**: Jeder Sensor-Typ hat jetzt sein eigenes Schema (BME680, LDR, CAM)
- **Gateway-Routing mit Schema-Validierung**: MQTT Client → Gateway (Schema-Validierung) → Manager
- **Meta-Parameter-System**: MQTT-Metadaten (timestamp, raw, qos, retain) durch gesamte Architektur
- **Clean Payload-Handling**: Manager erhalten immer Dict/List/Str - NIE raw bytes
- **Best Practice Logging-System**: Level-spezifische Ringbuffer mit Thread-Safety
- **UI-Logging Integration**: Dedicated Error & Warning Tabs mit kritischen Logs

---

## 1. ✅ IMPLEMENTIERTE KOMPONENTEN

- **✅ Registry Manager** (`omf2/registry/manager/registry_manager.py`)  
  Zentrale Singleton-Komponente für alle Registry v2 Daten (Topics, Schemas, MQTT Clients, Workpieces, Modules, Stations, TXT Controllers).
- **✅ Schema-Integration** (`omf2/registry/schemas/`)  
  44 JSON-Schemas für Topic-Validierung und Payload-Validierung.
- **✅ UI-Schema-Integration** (`omf2/ui/admin/admin_settings/schemas_subtab.py`)  
  Schema-Validierung in Admin Settings mit Live-Payload-Testing.
- **✅ Topics mit JSON-Schemas** (`omf2/registry/schemas/`)  
  Direkte JSON-Payloads mit Schema-Validierung für alle Topics.
- **✅ Gateway-Factory** (`omf2/factory/gateway_factory.py`)  
  Thread-sichere Factory für alle Gateway-Instanzen mit Singleton-Pattern.
  **⚠️ KRITISCH:** Admin = direkte Factory | CCU/NodeRED = Session State (verhindert Connection Loops).
- **✅ Environment Switch** (`omf2/ui/utils/environment_switch.py`)  
  Robuster Environment-Switch mit automatischem UI-Refresh. Verhindert Connection Loops durch sauberen Client/Gateway-Cleanup.
- **✅ CcuGateway** (`omf2/ccu/ccu_gateway.py`)  
  Gateway mit Topic-Routing für CCU Business-Operationen. Routet MQTT-Nachrichten an zuständige Manager.
- **✅ NoderedGateway** (`omf2/nodered/nodered_gateway.py`)  
  Fassade für Node-RED Business-Operationen mit Registry v2 Integration.
- **✅ AdminGateway** (`omf2/admin/admin_gateway.py`)  
  Fassade für Admin Business-Operationen mit Registry v2 Integration.
- **✅ UI-Komponenten** (`omf2/ui/`)  
  Vollständige Streamlit-UI mit Tab-Struktur und Registry v2 Integration.
- **✅ CCU Config Loader** (`omf2/ccu/config_loader.py`)  
  Domain-specific configuration loader parallel to Registry Manager for CCU JSON configurations.

---

## 2. ✅ IMPLEMENTIERTE ARCHITEKTUR

### **Gateway-Routing-Pattern mit Schema-Validierung (NEU)**

```
┌─────────────────────┐
│   MQTT Broker       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  mqtt_client        │  ← Raw MQTT Processing
│  - connect()        │
│  - _on_message()    │  → JSON-Parsing + Meta-Parameter
│  - set_gateway()    │  → timestamp, raw, qos, retain
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   gateway           │  ← Schema-Validation + Topic-Routing
│  - on_mqtt_message()│  → Schema aus Registry
│  - _validate_message│  → jsonschema.validate()
│  - _route_message   │  → Validierte Message an Manager
└──────────┬──────────┘
           │
           ├────────────────────┐
           ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│ business_manager │  │ business_manager │  ← Clean Business-Logik
│ - process_*(topic│  │ - process_*(topic│  → Immer Dict/List/Str
│   payload, meta) │  │   payload, meta) │  → NIE raw bytes!
│ - state_holder   │  │ - state_holder   │
└──────────────────┘  └──────────────────┘
```

**Architektur-Ebenen:**
1. **🔌 MQTT Client:** Raw MQTT → JSON + Meta-Parameter
2. **🚪 Gateway:** Schema-Validierung + Topic-Routing  
3. **🏢 Business Manager:** Clean Business-Logik
4. **🖥️ UI Components:** Display & User Interaction

**Domain-Specific Config Loaders (Parallel to Registry Manager):**
- **📁 CCU Config Loader:** Direct access to domain-specific JSON configurations
- **⚡ No Gateway Overhead:** Config display operations bypass Gateway layer
- **🎯 Separation:** Registry Manager (system-technical) vs. Config Loaders (domain-specific)
- **🏭 Shopfloor Layout Component:** Reusable UI component for factory layout visualization
- **⚙️ CCU Configuration UI:** Parameter and Factory configuration with role-based controls

### **Schema-Validierung & Meta-Parameter Konzept**

**Payload-Handling:**
```python
# MQTT Client: Raw → Clean
def _on_message(self, client, userdata, msg):
    topic = msg.topic
    payload_raw = msg.payload.decode('utf-8')
    message = json.loads(payload_raw)  # Dict/List/Str
    
    meta = {
        "timestamp": time.time(),
        "raw": payload_raw,
        "qos": msg.qos,
        "retain": msg.retain
    }
    
    # Gateway mit cleanen Daten aufrufen
    self._gateway.on_mqtt_message(topic, message, meta)

# Gateway: Schema-Validierung + Routing
def on_mqtt_message(self, topic, message, meta=None):
    # 1. Schema aus Registry holen
    schema = self.registry_manager.get_topic_schema(topic)
    
    # 2. Schema-Validierung
    if schema:
        validated_message = self._validate_message(topic, message, schema)
        if not validated_message:
            return False  # Validierung fehlgeschlagen
    
    # 3. Topic-Routing an Manager
    return self._route_message(topic, validated_message, meta)

# Business Manager: Immer cleanen Input
def process_sensor_message(self, topic, payload, meta=None):
    # payload ist immer Dict/List/Str - NIE raw bytes!
    # meta enthält MQTT-Metadaten falls benötigt
```

**Vorteile:**
- **Clean Separation:** MQTT-Client macht Parsing, Gateway macht Validierung
- **Testbarkeit:** Manager können mit echten Dicts getestet werden
- **Robustheit:** Schema-Validierung fängt ungültige Payloads ab
- **Monitoring:** Meta-Parameter für Debugging und Monitoring

**Schema-Validation Troubleshooting:**
Bei Validation Warnings müssen wir zwischen 3 Fällen unterscheiden:

1. **Registry-Topic-Schema Beziehung passt nicht:**
   - Problem: Falsches Schema für Topic in Registry
   - Lösung: Schema-Zuordnung in Registry korrigieren

2. **Schema ist zu streng für echte Nachricht:**
   - Problem: Schema ist zu restriktiv für reale MQTT-Nachrichten
   - Lösung: Schema anpassen (weniger required fields, flexiblere Typen)

3. **Nachricht ist falsch/ungültig:**
   - Problem: MQTT-Nachricht entspricht nicht dem erwarteten Format
   - Lösung: MQTT-Sender korrigieren

**Debugging-Strategie:**
```python
# Gateway Logging für Troubleshooting
if schema:
    logger.debug(f"📋 Found schema for topic {topic}, validating payload")
    validated_message = self._validate_message(topic, message, schema)
    if not validated_message:
        logger.warning(f"⚠️ Schema validation failed for {topic}")
        logger.warning(f"   Schema: {schema}")
        logger.warning(f"   Payload: {str(message)[:200]}...")
        # → Hier entscheiden: Registry, Schema oder Nachricht korrigieren?
```

### **Gesamte Architektur**

```plaintext
Streamlit-UI (omf2/ui/)
    │
    ▼
Business Logic (omf2/ccu/, omf2/admin/, omf2/common/)
    ├── ModuleManager (Schema-basierte Message-Verarbeitung) ✅
    ├── SensorManager (Schema-basierte Sensor-Daten-Verarbeitung mit Registry Manager) ✅
    ├── WorkpieceManager (Registry-basierte Icons) ✅
    ├── MessageManager (Domain-agnostic Message Generation/Validation) ✅
    ├── TopicManager (Domain-agnostic Topic Management) ✅
    └── AdminGateway (System-Verwaltung) ✅
        │
        ▼
Gateway-Factory (Singleton) ✅
    ├── CcuGateway (Topic-Routing) ✅
    ├── NoderedGateway (Registry v2) ✅
    └── AdminGateway (Registry v2) ✅
        │
        ▼
MQTT Clients (Singleton) ✅
    ├── CCU MQTT Client (Gateway-Routing) ✅
    ├── Node-RED MQTT Client ✅
    └── Admin MQTT Client ✅
```

**✅ IMPLEMENTIERTE FEATURES:**
- **Gateway-Routing-Pattern mit Schema-Validierung** für saubere Trennung von Transport und Business-Logik
- **Meta-Parameter-System** für MQTT-Metadaten (timestamp, raw, qos, retain)
- **Schema-Validierung im Gateway** mit jsonschema für alle Topics
- **Clean Payload-Handling:** MQTT Client → Gateway → Manager (NIE raw bytes in Manager)
- **Best Practice Logging-System** mit Level-spezifischen Ringbuffern und Thread-Safety
- **UI-Logging Integration** mit dedizierten Error & Warning Tabs
- Registry Manager als zentrale Komponente für alle Registry-Daten
- Business Logic Manager (ModuleManager, WorkpieceManager) für Entitäts-Verwaltung
- **Domain-agnostic Manager (MessageManager, TopicManager) für wiederverwendbare Logik**
- **SensorManager für Schema-basierte Sensor-Daten-Verarbeitung**
- Schema-basierte Message-Verarbeitung mit direkter Registry-Abfrage
- Thread-sichere Singleton-Pattern für alle Komponenten
- Gateway-Factory für Business-Operationen mit automatischer Gateway-Registrierung
- MQTT Clients als Singleton für sichere Kommunikation
- Registry v2 Integration in allen Gateways
- **Architektur-basierte Log-Management** mit domänen-spezifischen Debug-Controls
- **Gateway Pattern mit Manager-Delegation für saubere Trennung**
- **Topic-Routing im Gateway** (Set-basiert für Sensoren, Präfix-basiert für Module)
- Saubere Architektur ohne redundante Mappings
- Vollständige Test-Abdeckung (55 Tests)
- Error-Handling und Performance-Optimierung

---

## 3. Gateway-Routing-Pattern (NEU) + Asymmetrische Architektur

### **Separation of Concerns:**
- **MQTT Client:** Nur Verbindung & Transport (KEINE Business-Logik)
- **Gateway:** Topic-Routing und Manager-Aufrufe
- **Manager:** Business-Logik und State-Verarbeitung

### **Asymmetrische Architektur (VERIFIED 2025-10-09):**

**KRITISCHE ERKENNTNIS:** APS-System hat asymmetrische Kommunikationswege:

#### **Commands (CCU → Module):**
```
CCU-Backend → MQTT (module/.../order) → NodeRed subscribed → OPC-UA → SPS
```
- ✅ Gilt für **ALLE** Module (HBW, MILL, DRILL, DPS, AIQS)
- ✅ NodeRed ist **ZWINGEND** für Production Commands
- ✅ Verified: NodeRed Function "sub order" subscribes zu `module/.../order`

#### **Telemetry (Module → CCU):**

**A) Module MIT TXT-Controller (DPS, AIQS, FTS):**
```
TXT-Controller → MQTT DIREKT → module/v1/ff/<serial>/state
                              → module/v1/ff/<serial>/connection
                              → module/v1/ff/<serial>/factsheet
```
- ✅ **DIREKT** ohne NodeRed
- ✅ Schnell, zuverlässig
- ✅ Funktioniert auch wenn NodeRed offline!
- ✅ Verified: Live-System zeigt DPS/AIQS online trotz NodeRed-Problem

**B) Module OHNE TXT-Controller (HBW, MILL, DRILL):**
```
SPS → OPC-UA → NodeRed → MQTT → module/v1/ff/NodeRed/<serial>/state
```
- ✅ **NUR** über NodeRed möglich
- ❌ Wenn NodeRed offline → Module offline!
- ✅ Verified: Live-System zeigt HBW/MILL/DRILL offline bei NodeRed-Problem

**C) NodeRed State-Enrichment (PARALLEL für DPS/AIQS):**
```
SPS → OPC-UA → NodeRed → enriches mit orderId → MQTT
```
- ✅ Parallel zu TXT-MQTT
- ✅ Fügt orderId aus Workflow-Context hinzu
- ✅ `module/v1/ff/NodeRed/<serial>/state` (enriched version)

**Zusammenfassung:**
- **DPS/AIQS** haben ZWEI State-Quellen:
  - `module/v1/ff/SVR4H73275/state` ← TXT direkt (schnell, zuverlässig)
  - `module/v1/ff/NodeRed/SVR4H73275/state` ← NodeRed enriched (mit orderId)
- **HBW/MILL/DRILL** haben EINE State-Quelle:
  - `module/v1/ff/NodeRed/SVR3QA0022/state` ← NUR NodeRed (REQUIRED)

### **Topic-Routing-Strategie:**
```python
# Sensor-Topics (Set-basiert, O(1) Lookup)
sensor_topics = {
    '/j1/txt/1/i/bme680',  # BME680 Sensor
    '/j1/txt/1/i/ldr',     # LDR Sensor
    '/j1/txt/1/i/cam'      # Camera
}

# Module-Topics (Präfix-basiert, flexibel)
module_topic_prefixes = [
    'module/v1/ff/',       # Direkte Module (TXT-Telemetry)
    'module/v1/ff/NodeRed/', # NodeRed-Enriched (OPC-UA-Bridge)
    'fts/v1/ff/',          # FTS Topics (TXT-Direct)
    'ccu/pairing/state'    # CCU Pairing
]
```

### **Routing-Logik:**
```python
def on_mqtt_message(self, topic: str, payload: Dict[str, Any]):
    # Routing 1: Sensor Topics (Set-basiert, O(1))
    if topic in self.sensor_topics:
        sensor_manager = self._get_sensor_manager()
        sensor_manager.process_sensor_message(topic, payload)
        return
    
    # Routing 2: Module Topics (Präfix-basiert)
    for prefix in self.module_topic_prefixes:
        if topic.startswith(prefix):
            module_manager = self._get_module_manager()
            module_manager.process_module_message(topic, payload)
            return
```

### **Vorteile:**
- ✅ **Separation of Concerns:** Client ≠ Gateway ≠ Manager
- ✅ **Wartbarkeit:** Zentrale Topic-Listen, einfach erweiterbar
- ✅ **Testbarkeit:** Komponenten isoliert testbar
- ✅ **Performance:** O(1) Lookup für Sensor-Topics
- ✅ **Singleton-kompatibel:** Lazy-Loading der Manager

---

## 4. Business Logic Manager (Entitäts-Verwaltung)

### 3.1 ModuleManager (Schema-basierte Message-Verarbeitung)

**Datei:** `omf2/ccu/module_manager.py`

**Funktionen:**
- **Schema-basierte Message-Verarbeitung:** Verwendet Registry-Schemas für korrekte Daten-Extraktion
- **Status-Management:** Connection, Availability, Configuration Status
- **Icon-Verwaltung:** Registry-basierte Module-Icons
- **Gateway-Pattern:** Nutzt CCU Gateway für MQTT-Zugriff

**Beispiel:**
```python
from omf2.ccu.module_manager import get_ccu_module_manager

module_manager = get_ccu_module_manager()
modules = module_manager.get_all_modules()

for module_id, module_data in modules.items():
    icon = module_manager.get_module_icon(module_id)  # Registry-basiert
    connection = module_manager.get_connection_display(module_data)  # UISymbols
    availability = module_manager.get_availability_display(module_data)  # UISymbols
    configuration = module_manager.get_configuration_display(module_data)  # UISymbols
```

### 3.2 WorkpieceManager (Registry-basierte Icons)

**Datei:** `omf2/common/workpiece_manager.py`

**Funktionen:**
- **Workpiece-Icons:** Lädt Icons aus `registry/workpieces.yml`
- **Farb-spezifische Icons:** 🔵⚪🔴 für blue/white/red
- **Singleton-Pattern:** Zentrale Icon-Verwaltung
- **UISymbols-Integration:** Über `UISymbols.get_workpiece_icon()`

**Beispiel:**
```python
from omf2.common.workpiece_manager import get_workpiece_manager

workpiece_manager = get_workpiece_manager()
blue_icon = workpiece_manager.get_workpiece_icon('blue')  # 🔵
white_icon = workpiece_manager.get_workpiece_icon('white')  # ⚪
red_icon = workpiece_manager.get_workpiece_icon('red')  # 🔴
all_workpieces_icon = workpiece_manager.get_all_workpieces_icon()  # 🔵⚪🔴
```

---

## 4. Business Logic Manager (Schema-basierte Daten-Verarbeitung)

### 4.1 SensorManager (Schema-basierte Sensor-Daten-Verarbeitung)

**Zweck:** Verarbeitet Sensor-Messages aus MQTT-Buffers mit Schema-basierter Feld-Extraktion (BME680, LDR, CAM).

**🔧 KORRIGIERTES PATTERN (2025-10-04):**
```python
# UI Component → Business Logic Manager → Gateway → Registry Manager
class SensorManager:
    def process_sensor_messages(self, ccu_gateway) -> Dict[str, Any]:
        # 1. Get all buffers via Gateway
        all_buffers = ccu_gateway.get_all_message_buffers()
        
        # 2. Process each sensor topic
        for topic, messages in all_buffers.items():
            if self._is_sensor_topic(topic):
                processed_data = self._extract_sensor_data(topic, messages)
        
        return sensor_data
    
    def _extract_sensor_data(self, topic: str, messages: List[Dict]) -> Dict[str, Any]:
        # 1. Extract payload from message (remove metadata)
        payload = latest_message.copy()
        metadata_fields = ['timestamp', 'ts']
        sensor_payload = {k: v for k, v in payload.items() if k not in metadata_fields}
        
        # 2. Use Registry Manager for schema-based payload validation
        validation_result = self.registry_manager.validate_topic_payload(topic, sensor_payload)
        
        # 3. Extract validated sensor fields
        if validation_result.get("valid", False):
            validated_payload = sensor_payload
            
            if "/bme680" in topic:
                return {
                    "temperature": validated_payload.get("t", 0.0),      # ✅ Korrekt
                    "humidity": validated_payload.get("h", 0.0),         # ✅ Korrekt
                    "pressure": validated_payload.get("p", 0.0),         # ✅ Korrekt
                    "air_quality": validated_payload.get("iaq", 0.0)     # ✅ Korrekt: "iaq"
                }
            elif "/ldr" in topic:
                return {"light": validated_payload.get("ldr", 0.0)}      # ✅ Korrekt: "ldr"
            elif "/cam" in topic:
                return {"image_data": validated_payload.get("data", "")} # ✅ Korrekt
```

**Usage:**
```python
# UI Component
sensor_manager = get_ccu_sensor_manager()
sensor_data = sensor_manager.process_sensor_messages(ccu_gateway)
bme680_data = sensor_data.get("/j1/txt/1/i/bme680", {})
temperature = bme680_data.get("temperature", 0.0)
```

**Vorteile:**
- **Registry Manager Validation:** Korrekte Schema-Validierung für jeden Sensor-Typ
- **Payload-Extraktion:** Metadaten werden korrekt entfernt vor Validierung
- **Topic-spezifische Schemas:** BME680, LDR, CAM haben jeweils eigene Schemas
- **Korrekte Feld-Namen:** `iaq` (nicht `aq`), `ldr` (nicht `l`) entsprechend echten MQTT-Daten
- **Gateway-Pattern:** UI interagiert nur mit Manager, nicht direkt mit Gateway
- **Message Processing Pattern:** Standardisiertes Debug-Logging und Feld-Extraktion
- **Wiederverwendbar:** Gleiche Logik für alle Sensor-Topics

---

### 4.2 OrderManager (Inventory & Order Management)

**Zweck:** Verarbeitet Stock-Messages (Lagerbestand) und verwaltet Kundenaufträge/Rohmaterial-Bestellungen.

**Datei:** `omf2/ccu/order_manager.py`

**🔧 WICHTIGE ARCHITEKTUR-PATTERNS:**

**1. Non-Blocking Initialization (KRITISCH):**
```python
class OrderManager:
    def __init__(self):
        """Initialize Order Manager - EXAKT wie Sensor Manager (kein File I/O!)"""
        # ✅ Nur Dicts/Listen setzen - KEIN File I/O!
        self.inventory = {f"{chr(65+i)}{j+1}": None for i in range(3) for j in range(3)}
        self.workpiece_types = ["RED", "BLUE", "WHITE"]
        self.max_capacity = 3
        self._lock = threading.Lock()
        # ❌ NIEMALS: config_loader.load_production_settings() im __init__!
```

**2. Lock-Hierarchie (Deadlock-Vermeidung):**
```python
# ✅ RICHTIG: Nur äußerste Methode mit Lock
def get_inventory_status(self) -> Dict[str, Any]:
    with self._lock:
        available = self.get_available_workpieces()  # ← OHNE Lock!
        need = self.get_workpiece_need()             # ← OHNE Lock!
        return {"inventory": self.inventory.copy(), ...}

# ✅ RICHTIG: Interne Methoden OHNE Lock
def get_available_workpieces(self) -> Dict[str, int]:
    # KEIN self._lock hier! Wird von get_inventory_status() aufgerufen
    available = {"RED": 0, "BLUE": 0, "WHITE": 0}
    for position, workpiece in self.inventory.items():
        if workpiece in available:
            available[workpiece] += 1
    return available

# ❌ FALSCH: Verschachtelte Locks führen zu DEADLOCK
def get_inventory_status_WRONG(self):
    with self._lock:                                # ← Lock erworben
        available = self.get_available_workpieces() # ← Versucht Lock nochmal!
        # → DEADLOCK!
```

**3. Singleton Pattern (wie SensorManager):**
```python
_order_manager_instance = None

def get_order_manager() -> OrderManager:
    global _order_manager_instance
    if _order_manager_instance is None:
        _order_manager_instance = OrderManager()
        logger.info("🏗️ Order Manager singleton created")
    return _order_manager_instance
```

**4. MQTT Message Processing:**
```python
def process_stock_message(self, topic: str, message: Dict[str, Any], meta: Dict[str, Any]) -> None:
    """Verarbeitet Stock-Nachrichten vom Topic /j1/txt/1/f/i/stock"""
    try:
        with self._lock:  # ← Lock nur für State-Updates
            stock_items = message.get("stockItems", [])
            for item in stock_items:
                location = item.get("location")  # e.g., "A1", "B2"
                workpiece_type = item.get("workpiece", {}).get("type")
                if location in self.inventory:
                    self.inventory[location] = workpiece_type
```

**5. UI Integration (Non-Blocking):**
```python
# UI Component
def render_inventory_subtab(ccu_gateway, registry_manager):
    # ✅ Direkter Manager-Zugriff (wie SensorManager)
    order_manager = get_order_manager()  # Non-Blocking Singleton
    inventory_status = order_manager.get_inventory_status()  # Non-Blocking
    
    # Display inventory with Bucket-Templates (aus omf/dashboard)
    for position, workpiece in inventory_status["inventory"].items():
        st.markdown(get_bucket_template(position, workpiece), unsafe_allow_html=True)
```

**⚠️ KRITISCHE LEKTIONEN (für andere Agents):**

1. **NIEMALS File I/O im `__init__`** → Blockiert Streamlit UI!
2. **NIEMALS verschachtelte Locks** → Deadlock!
3. **NIEMALS blocking Imports** → `config_loader` Import war Blocker!
4. **Lock-Hierarchie:** Nur äußerste Methode mit Lock, interne Methoden OHNE Lock
5. **Templates von omf/dashboard wiederverwenden** → Konsistentes Design

**Vorteile:**
- ✅ **Non-Blocking:** Kein File I/O, keine verschachtelten Locks
- ✅ **Thread-Safe:** Korrekte Lock-Hierarchie
- ✅ **State-Holder Pattern:** Inventory als Dict (wie sensor_data)
- ✅ **Gateway-Pattern:** MQTT → Gateway → Order Manager → UI
- ✅ **Live-Updates:** MQTT-Nachrichten aktualisieren Inventory in Echtzeit

---

## 5. Domain-agnostic Manager (Wiederverwendbare Logik)

### 5.1 MessageManager (Domain-agnostic Message Generation/Validation)

**Datei:** `omf2/common/message_manager.py`

**Funktionen:**
- **Schema-driven Message Generation:** Generiert Schema-konforme Messages für alle Domänen
- **Message Validation:** Validiert Messages gegen JSON-Schemas
- **Domain-agnostic:** Wiederverwendbar für admin, ccu, nodered
- **Buffer Management:** Verwaltet Message-Buffer für alle Domänen
- **Deep Merge:** Intelligente Payload-Zusammenführung

**Pattern:**
```python
# Factory Functions für Domain-spezifische Manager
from omf2.common.message_manager import get_admin_message_manager, get_ccu_message_manager

# Admin Domain
admin_message_manager = get_admin_message_manager()
message = admin_message_manager.generate_message("admin/topic", {"param": "value"})
valid = admin_message_manager.validate_message("admin/topic", payload)

# CCU Domain  
ccu_message_manager = get_ccu_message_manager()
message = ccu_message_manager.generate_message("ccu/topic", {"param": "value"})
valid = ccu_message_manager.validate_message("ccu/topic", payload)
```

### 5.2 TopicManager (Domain-agnostic Topic Management)

**Datei:** `omf2/common/topic_manager.py`

**Funktionen:**
- **Topic Discovery:** Findet Topics nach Patterns für alle Domänen
- **Schema Management:** Lädt und verwaltet Topic-Schemas
- **Domain Filtering:** Filtert Topics nach Domäne (admin, ccu, nodered)
- **Topic Analysis:** Analysiert Topic-Struktur und Verfügbarkeit
- **Validation:** Validiert Topic-Strukturen

**Pattern:**
```python
# Factory Functions für Domain-spezifische Manager
from omf2.common.topic_manager import get_admin_topic_manager, get_ccu_topic_manager

# Admin Domain
admin_topic_manager = get_admin_topic_manager()
admin_topics = admin_topic_manager.get_domain_topics()
schemas = admin_topic_manager.get_topic_schemas()

# CCU Domain
ccu_topic_manager = get_ccu_topic_manager()
ccu_topics = ccu_topic_manager.get_domain_topics()
analysis = ccu_topic_manager.analyze_topic("ccu/orders/send")
```

### 4.3 Gateway Pattern mit Manager-Delegation

**Pattern:**
```python
# Gateway delegiert an Domain-agnostic Manager
class AdminGateway:
    def __init__(self):
        self.message_manager = get_admin_message_manager()
        self.topic_manager = get_admin_topic_manager()
    
    def generate_message(self, topic, params):
        return self.message_manager.generate_message(topic, params)
    
    def get_all_topics(self):
        return self.topic_manager.get_all_topics()

class CcuGateway:
    def __init__(self):
        self.message_manager = get_ccu_message_manager()
        self.topic_manager = get_ccu_topic_manager()
    
    def generate_message(self, topic, params):
        return self.message_manager.generate_message(topic, params)
    
    def get_all_topics(self):
        return self.topic_manager.get_all_topics()
```

**Vorteile:**
- **Code-Duplikation eliminiert:** Gemeinsame Logik in Domain-agnostic Manager
- **Konsistente Implementierung:** Alle Domänen verwenden dieselbe Logik
- **Einfache Wartung:** Änderungen nur in einem Manager
- **Testbarkeit:** Manager können isoliert getestet werden

---

## 5. Registry Manager (zentral, Singleton)

- Zentrale Komponente für alle Registry v2 Daten
- Lädt Topics, Templates, MQTT Clients, Workpieces, Modules, Stations, TXT Controllers
- Bietet einheitliche API für alle Registry-Entitäten
- Name-Mapping zwischen verwandten Entitäten (Module → Station → TXT Controller)

```python
# omf2/registry/manager/registry_manager.py

import logging
import yaml
from pathlib import Path

class RegistryManager:
    _instance = None

    def __new__(cls, registry_path="omf2/registry/model/v2/"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all_registry_data(registry_path)
        return cls._instance

    def _load_all_registry_data(self, registry_path):
        # Lädt alle Registry-Daten
        self._load_topics()
        self._load_schemas()
        self._load_mqtt_clients()
        self._load_workpieces()
        self._load_modules()
        self._load_stations()
        self._load_txt_controllers()

    def get_topics(self):
        return self.topics

    def get_schemas(self):
        return self.schemas

    def get_mqtt_clients(self):
        return self.mqtt_clients

    def get_workpieces(self):
        return self.workpieces

    def get_modules(self):
        return self.modules

    def get_stations(self):
        return self.stations

    def get_txt_controllers(self):
        return self.txt_controllers

    def get_registry_stats(self):
        return {
            'topics_count': len(self.topics),
            'schemas_count': len(self.schemas),
            'mqtt_clients_count': len(self.mqtt_clients),
            'workpieces_count': len(self.workpieces),
            'modules_count': len(self.modules),
            'stations_count': len(self.stations),
            'txt_controllers_count': len(self.txt_controllers)
        }
```

---

## 4. Topic-Payload-Schema Beziehung (Schema-driven)

- **Gateway verwendet** - Zentrale Funktionalität für Senden/Empfangen
- **Schema-driven Payload-Generierung** - PayloadGenerator erstellt Schema-konforme Payloads
- **Registry-basierte Schemas** - Topics haben zugeordnete JSON-Schemas
- **Keine hardcodierten Payloads** - Ausnahme: Kurz-Hacks für schnelle Entwicklung (mit TODO-Kommentaren)

```python
# ✅ KORREKTES PATTERN (topic_steering):
# Schema-driven Payload-Generierung über Registry

def render_topic_steering_subtab(admin_gateway, registry_manager):
    """Korrekte Implementierung mit Schema-driven Approach"""
    
    # Topic-Payload-Schema Beziehung
    topic_selector = TopicSelector(registry_manager)
    payload_generator = PayloadGenerator(registry_manager)
    
    # Schema-driven UI
    selected_topic = st.selectbox("Select Topic:", all_topics)
    
    if selected_topic:
        # Schema-konforme Payload generieren
        payload = payload_generator.generate_example_payload(selected_topic)
        
        if st.button("Send Message"):
            # Gateway verwenden für zentrale Funktionalität
            success = admin_gateway.publish_message(selected_topic, payload)
            if success:
                st.success("Message sent successfully!")

# ❌ FALSCHES PATTERN (factory_steering - Kurz-Hack):
# Hardcodierte Payloads (nur in Ausnahmefällen erlaubt)
# TODO: Replace hardcoded payload with schema-driven approach
# TODO: Use PayloadGenerator.generate_example_payload(topic) instead
# TODO: Integrate with Registry Manager for proper schema validation
payload = {
    "timestamp": datetime.now().isoformat(),
    "serialNumber": fts_serial,
    "actions": [{"actionType": "findInitialDockPosition", ...}]
}
```

---

## 5. Thread-sicherer MQTT-Client (Singleton)

- Eine Instanz pro Domäne.
- Alle Methoden (publish, subscribe, etc.) arbeiten thread-safe via Lock.
- Empfangene Nachrichten werden in eine threadsichere Queue geschrieben (z.B. für Streamlit-UI).

```python
# omf2/ccu/ccu_mqtt_client.py

import threading
import paho.mqtt.client as mqtt
from queue import Queue

class CcuMqttClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._client = mqtt.Client()
                cls._instance._client_lock = threading.Lock()
                cls._instance._msg_queue = Queue()
                # ... weitere Initialisierung, z.B. Connect, Callback-Setup ...
            return cls._instance

    def publish(self, topic, msg):
        with self._client_lock:
            self._client.publish(topic, msg)

    def subscribe(self, topic):
        with self._client_lock:
            self._client.subscribe(topic)

    def on_message(self, client, userdata, message):
        # Callback von paho-mqtt
        self._msg_queue.put((message.topic, message.payload))

    def get_next_message(self):
        try:
            return self._msg_queue.get_nowait()
        except Exception:
            return None
```

---

## 6. Gateway (Fassade, pro Domäne)

- Kapselt Message-Erstellung, Validierung, Logging und MQTT-Kommunikation.
- Bietet Methoden wie `send_order(params)` für die UI.
- Die UI sieht niemals Templates, MQTT, Threads oder Queue!

```python
# omf2/ccu/ccu_gateway.py

from omf2.ccu.ccu_mqtt_client import CcuMqttClient

class CCUGateway:
    """CCU Gateway - Fassade für CCU Business-Operationen"""
    
    def __init__(self):
        self.mqtt_client = CcuMqttClient()

    def send_order(self, topic, payload):
        """Send Order - Schema-driven über Gateway"""
        try:
            # Gateway verwendet zentrale Funktionalität
            success = self.mqtt_client.publish(topic, payload)
            if success:
                return True, "Order gesendet"
            else:
                return False, "MQTT-Publish fehlgeschlagen"
        except Exception as e:
            return False, f"Order-Send Fehler: {e}"

    def get_last_incoming_message(self):
        return self.mqtt_client.get_next_message()
```

---

## 7. Streamlit-UI: Nur Gateway nutzen, State/Refresh per Session

```python
# Im Streamlit-Tab (z.B. ui/ccu/ccu_orders/ccu_orders_tab.py)
import streamlit as st
from omf2.factory.gateway_factory import get_ccu_gateway

gateway = get_ccu_gateway()

if "order_refresh" not in st.session_state:
    st.session_state["order_refresh"] = 0

if st.button("Order senden"):
    # ✅ KORREKT: Schema-driven Payload-Generierung
    topic = "ccu/orders/send"
    payload = payload_generator.generate_example_payload(topic)
    
    ok, result = gateway.send_order(topic, payload)
    if ok:
        st.session_state["order_refresh"] += 1
        st.success(result)
    else:
        st.error(result)

# Polling für neue Nachrichten (optional)
msg = gateway.get_last_incoming_message()
if msg:
    topic, payload = msg
    st.info(f"Neue Nachricht: {topic}: {payload}")
```

---

## 8. UI-Refresh-Pattern (Streamlit)

- Nach Aktionen: Zähler in `st.session_state` erhöhen, z.B. `order_refresh`.
- UI-Komponenten können an diesen Zähler gekoppelt werden (z.B. mit `key=f"orders_{st.session_state['order_refresh']}"`).
- Eingehende Nachrichten werden aus Queue gelesen und angezeigt, kein expliziter Thread in Streamlit nötig.

---

## 9. ✅ BEST PRACTICE LOGGING-SYSTEM

### **Multi-Level Ring Buffer Logging (Thread-Safe)**

**Zweck:** Zentrale Log-Sammlung für UI-Display mit Level-spezifischen Buffern und Thread-Safety.

**Architektur:**
```python
# omf2/common/logger.py

class MultiLevelRingBufferHandler(logging.Handler):
    """Thread-sicherer Handler mit Level-spezifischen Ring-Buffern"""
    
    def __init__(self):
        super().__init__()
        self.buffers = {
            'ERROR': deque(maxlen=200),      # Kritische Errors
            'WARNING': deque(maxlen=200),    # Wichtige Warnings  
            'INFO': deque(maxlen=500),       # Standard Info-Logs
            'DEBUG': deque(maxlen=300)       # Debug-Logs
        }
        self._lock = threading.Lock()
    
    def emit(self, record):
        """Thread-sichere Log-Speicherung in Level-spezifische Buffer"""
        with self._lock:
            level = record.levelname
            if level in self.buffers:
                formatted = self.format(record)
                self.buffers[level].append(formatted)
```

**Initialisierung (omf2/omf.py):**
```python
# 1. ZUERST Handler setzen (noch vor allen anderen Imports, die loggen)!
from omf2.common.logger import setup_multilevel_ringbuffer_logging
from omf2.common.logger import heal_all_loggers
from omf2.common.logger import ensure_ringbufferhandler_attached

# BEST PRACTICE: Frühe Initialisierung vor erstem logger.info()
if 'log_handler' not in st.session_state:
    handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler
    st.session_state['log_buffers'] = buffers
    ensure_ringbufferhandler_attached()
    heal_all_loggers()

# 2. DANN restliche Imports (jetzt bekommen alle Logger propagate=True!)
```

**Handler-Persistenz nach Environment-Switch:**
```python
# omf2/ui/main_dashboard.py

def _reconnect_logging_system(self):
    """Reconnect logging system to UI buffers after environment switch"""
    try:
        from omf2.common.logger import setup_multilevel_ringbuffer_logging, MultiLevelRingBufferHandler
        import logging
        
        # CRITICAL: Remove ALL existing handlers first
        root_logger = logging.getLogger()
        for handler_to_remove in root_logger.handlers[:]:
            root_logger.removeHandler(handler_to_remove)
        
        # CRITICAL: Create new handler and attach to root logger
        handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
        
        # Update session state with new handler and buffers
        st.session_state['log_handler'] = handler
        st.session_state['log_buffers'] = buffers
        
        # CRITICAL: Force UI refresh to pick up new handler
        from omf2.ui.utils.ui_refresh import request_refresh
        request_refresh()
        
    except Exception as e:
        logger.error(f"❌ Failed to reconnect logging system: {e}")
```

**UI-Integration (omf2/ui/admin/system_logs/):**
```python
# system_logs_tab.py

def render_system_logs_tab():
    """System Logs Tab mit Multi-Level Buffer Integration"""
    
    # Handler aus Session State holen
    log_handler = st.session_state.get('log_handler')
    if not log_handler:
        st.error("❌ No log handler available")
        return
    
    # Level-spezifische Logs aus Buffern holen
    all_logs = []
    for level in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
        level_logs = log_handler.get_buffer(level)
        all_logs.extend(level_logs)
    
    # Sort by timestamp (newest first)
    all_logs.sort(key=lambda x: x.split(']')[0] if ']' in x else x, reverse=True)
    
    # Display mit Toggle (Table View / Console View)
    display_mode = st.session_state.get('log_display_mode', 'Console View')
    if display_mode == 'Table View':
        _render_log_table(all_logs)
    else:
        _render_log_console(all_logs)
```

### **Logging-System Best Practices:**

**1. Handler-Persistenz:**
- ✅ **`ensure_ringbufferhandler_attached()`** - Stellt sicher, dass Handler am Root-Logger ist
- ✅ **`heal_all_loggers()`** - Entfernt alle eigenen Handler und setzt `propagate=True`
- ✅ **Reihenfolge:** Zuerst Handler sicherstellen, dann Logger "heilen"

**2. Environment-Switch Handling:**
- ✅ **Handler-Removal:** Alle alten Handler entfernen vor Neu-Initialisierung
- ✅ **Session State Update:** Handler und Buffers in `st.session_state` aktualisieren
- ✅ **UI-Refresh:** `request_refresh()` nach Handler-Update

**3. Thread-Safety:**
- ✅ **Lock-basierte Buffer:** Alle Buffer-Operationen sind thread-safe
- ✅ **Singleton Pattern:** Ein Handler pro Session
- ✅ **Propagate=True:** Alle Logger senden an Root-Logger

**4. UI-Integration:**
- ✅ **Level-spezifische Display:** ERROR, WARNING, INFO, DEBUG getrennt
- ✅ **Display Modes:** Table View (strukturiert) / Console View (einzeilig)
- ✅ **Real-time Updates:** Logs erscheinen sofort in UI

**5. Debugging & Troubleshooting:**
- ✅ **Handler-Verification:** Prüfung, dass genau ein Handler am Root-Logger ist
- ✅ **Buffer-Size Monitoring:** Debug-Ausgaben für Buffer-Größen
- ✅ **Session State Consistency:** Handler-ID-Verifikation

### **Wichtige Regeln:**

**❌ VERBOTEN:**
- Mehrere `MultiLevelRingBufferHandler` am Root-Logger
- Handler ohne Thread-Safety
- Logger ohne `propagate=True`
- Handler-Verlust nach Environment-Switch

**✅ ERFORDERLICH:**
- Ein Handler pro Session
- Thread-sichere Buffer-Operationen
- Handler-Persistenz nach Environment-Switch
- UI-Refresh nach Handler-Update

---

## 10. Vorteile & Best Practices

- **UI bleibt einfach:** Keine Threading-Probleme, keine MQTT-Details, kein Deadlock-Risiko.
- **Gateways sind "schlanke Fassade":** Testbar, erweiterbar, keine Redundanz.
- **Domain-agnostic Manager:** Wiederverwendbare Logik, Code-Duplikation eliminiert.
- **Gateway Pattern mit Manager-Delegation:** Saubere Trennung von Verantwortlichkeiten.
- **Message Processing Pattern:** Standardisiertes Pattern für alle Manager (verhindert wiederkehrende Fehler).
- **MQTT und Schemas sind zentral und thread-safe gekapselt.**
- **UI-Refresh wird zentral gesteuert, keine Race-Conditions mit Session-State.**
- **Das Pattern ist in allen Domänen wiederverwendbar und hält die Komplexität im Griff.**

---

## 10. Erweiterungsmöglichkeiten

- Validierung per JSON Schema (in validate_message).
- Abstrakte Basisklassen für Gateway/MQTTClient, falls wirklich notwendig.
- Weitere Methoden für Subscriptions, Message-Buffering, etc.

---

**Diskussionspunkte für den Coding Agent:**
- Welche Events sollen den UI-Refresh triggern?
- Sollen eingehende Nachrichten persistent in Session-State, DB oder nur temporär (Queue)?
- Wie werden Fehler/Erfolg zentral im UI gemeldet?
- Wie werden komplexe Payloads (z.B. JSON) gemappt/gerendert?

---

---

## ✅ IMPLEMENTIERUNGSÜBERSICHT

### **📁 IMPLEMENTIERTE DATEIEN:**

**Core-Architektur:**
- `omf2/registry/manager/registry_manager.py` - Registry Manager Singleton ✅
- `omf2/factory/gateway_factory.py` - Gateway-Factory ✅
- `omf2/ccu/ccu_gateway.py` - CcuGateway ✅
- `omf2/nodered/nodered_gateway.py` - NoderedGateway ✅
- `omf2/admin/admin_gateway.py` - AdminGateway ✅

**Business Logic Manager:**
- `omf2/ccu/sensor_manager.py` - SensorManager (Schema-basierte Sensor-Daten-Verarbeitung) ✅

**Domain-agnostic Manager:**
- `omf2/common/message_manager.py` - MessageManager (Domain-agnostic) ✅
- `omf2/common/topic_manager.py` - TopicManager (Domain-agnostic) ✅
- `omf2/admin/admin_message_manager.py` - AdminMessageManager (Wrapper) ✅

**Dokumentation:**
- `omf2/docs/MESSAGE_PROCESSING_PATTERN.md` - Standard-Pattern für alle Manager ✅

**Registry v2 Integration:**
- `omf2/registry/model/v2/` - Vollständige Registry v2 ✅
- Topics, Templates, Mappings - Alle implementiert ✅

**UI-Komponenten:**
- `omf2/ui/ccu/` - CCU Tabs und Subtabs ✅
- `omf2/ui/nodered/` - Node-RED Tabs ✅
- `omf2/ui/admin/` - Admin Tabs und Subtabs ✅

**Tests:**
- `omf2/tests/test_comprehensive_architecture.py` - 14 Tests ✅
- `omf2/tests/test_gateway_factory.py` - 14 Tests ✅
- `omf2/tests/test_registry_v2_integration_simple.py` - 10 Tests ✅
- `omf2/tests/test_registry_manager_comprehensive.py` - 20 Tests ✅
- `omf2/tests/test_sensor_manager.py` - SensorManager Tests (geplant)
- `omf2/tests/test_message_manager.py` - MessageManager Tests ✅
- `omf2/tests/test_topic_manager.py` - TopicManager Tests ✅
- `omf2/tests/test_admin_message_manager.py` - AdminMessageManager Tests ✅

### **📊 TEST-STATISTIK:**
- **55 Tests erfolgreich** ✅
- **0 Fehler** ✅
- **Thread-Safety** getestet ✅
- **Registry v2 Integration** getestet ✅
- **Registry Manager** getestet ✅
- **Performance** optimiert ✅

### **🚀 VERWENDUNG:**

```python
# 🎯 ZENTRALE INITIALISIERUNG in omf.py (beim App-Start):
# 1. Registry Manager wird initialisiert
# 2. Admin MQTT Client wird initialisiert
# 3. MQTT Verbindung wird hergestellt

# In Tabs/Components: Registry Manager aus Session State holen
registry_manager = st.session_state.get('registry_manager')
if registry_manager:
    # Alle Registry-Daten laden
    topics = registry_manager.get_topics()
    schemas = registry_manager.get_schemas()
    mqtt_clients = registry_manager.get_mqtt_clients()
    workpieces = registry_manager.get_workpieces()
    modules = registry_manager.get_modules()
    stations = registry_manager.get_stations()
    txt_controllers = registry_manager.get_txt_controllers()

# In Tabs/Components: Admin MQTT Client aus Session State holen
admin_client = st.session_state.get('admin_mqtt_client')
if admin_client:
    # Reconnect nur bei Verbindungsverlust
    if not admin_client.connected:
        current_env = st.session_state.get('current_environment', 'mock')
        admin_client.connect(current_env)
    
    # Connection Info holen
    conn_info = admin_client.get_connection_info()

# Gateway-Factory verwenden
from omf2.factory.gateway_factory import get_ccu_gateway, get_nodered_gateway, get_admin_gateway

# Gateways erstellen
ccu_gateway = get_ccu_gateway()
nodered_gateway = get_nodered_gateway()
admin_gateway = get_admin_gateway()

# Business-Operationen ausführen
ccu_gateway.reset_factory()
ccu_gateway.send_global_command("start", {"line": "1"})
```

---

## 8. ✅ BUSINESS-MANAGER PATTERN (NEU IMPLEMENTIERT)

**Status: IMPLEMENTIERT UND GETESTET** ✅  
**Datum: 2025-10-04**  
**Pattern: Business-Manager als State-Holder mit direkter Payload-Verarbeitung**

### **🎯 ARCHITEKTUR-PRINZIP:**

```
MQTT-Client (Transport) → Business-Manager (State-Holder) → UI (Konsument)
```

### **📋 KOMPONENTEN:**

#### **MQTT-Client (Transport-Layer):**
- **Verantwortlichkeit:** Transport, Topic-Management, Message-Dispatch
- **NICHT:** Zentraler State-Holder für Business-Daten
- **Callback-Pattern:** Übergibt `topic` + `payload` an Business-Manager

#### **Business-Manager (State-Layer):**
- **Verantwortlichkeit:** Business-Logic, State-Holder, Schema-Validierung
- **Pattern:** `process_xxx_message(topic: str, payload: Dict)`
- **State-Holder:** Hält aktuellen Business-State im Speicher
- **Schema-Validierung:** Über MessageManager gegen Registry-Schemas

#### **UI (Presentation-Layer):**
- **Verantwortlichkeit:** Anzeige, Benutzer-Interaktion
- **Pattern:** Liest nur aus Manager-State, nie direkt aus MQTT-Client
- **Refresh:** `request_refresh()` Pattern (nie `st.rerun()`)

### **🔧 IMPLEMENTIERUNG:**

#### **Registry-Konfiguration:**
```yaml
# omf2/registry/mqtt_clients.yml
mqtt_clients:
  ccu_mqtt_client:
    # HAUPT-LISTE: MQTT Client subscribed diese Topics
    subscribed_topics:
      - "/j1/txt/1/i/bme680"
      - "/j1/txt/1/i/ldr"
      - "module/v1/ff/SVR3QA0022/state"
      - "module/v1/ff/SVR3QA0022/connection"
      - "module/v1/ff/SVR3QA0022/factsheet"
      - "ccu/pairing/state"
    
    # GATEWAY-ROUTING-HINTS: Topics die vom Gateway an Business-Functions geroutet werden
    # WICHTIG: Business-Functions machen KEINE eigene MQTT-Subscription!
    #          Sie erhalten Topics vom Gateway via onMessage()
    gateway_routing_hints:
      sensor_manager:
        routed_topics:  # Topics die an SensorManager.onMessage() geroutet werden
          - "/j1/txt/1/i/bme680"    # BME680 Sensor-Daten (TXT-AIQS)
          - "/j1/txt/1/i/ldr"       # LDR Sensor-Daten (TXT-AIQS)
          - "/j1/txt/1/i/cam"       # Camera-Daten (TXT-AIQS)
      
      module_manager:
        routed_topics:  # Topics die an ModuleManager.onMessage() geroutet werden
          - "module/v1/ff/SVR3QA0022/state"
          - "module/v1/ff/SVR3QA0022/connection"
          - "module/v1/ff/SVR3QA0022/factsheet"
          - "ccu/pairing/state"
      
      order_manager:
        routed_topics:  # Topics die an OrderManager.onMessage() geroutet werden
          - "/j1/txt/1/f/o/stock"      # HBW Inventory FROM TXT (Stock-Management)
      
      production_order_manager:
        routed_topics:  # Topics die an ProductionOrderManager.onMessage() geroutet werden
          - "ccu/order/request"         # PRIMARY trigger for new orders
          - "ccu/order/response"        # Order confirmation with UUID
          - "ccu/order/active"          # Active orders queue
          - "ccu/order/completed"       # Completed orders log
```

#### **Wichtige Architektur-Details:**

**🔑 Gateway-Routing-Hints vs. Subscriptions:**
1. **`subscribed_topics`** (Haupt-Liste): MQTT Client subscribed diese Topics am Broker
2. **`gateway_routing_hints.xxx.routed_topics`** (Routing-Info): Gateway routet an Business Functions

**📋 Semantik-Klarstellung:**
- **MQTT Client** subscribed Topics am Broker (MQTT-Protokoll-Ebene)
- **Gateway** empfängt Messages via `onMessage()` und routet an Business Functions
- **Business Functions** machen KEINE eigene MQTT-Subscription, sondern bekommen Messages vom Gateway
- **Routing-Hints** sind Entwicklungs-Hilfe, finale Logik ist im Gateway-Code

**✅ Validierung:**
- Alle `routed_topics` MÜSSEN in `ccu_mqtt_client.subscribed_topics` sein
- Gateway prüft Topics und routet nur, wenn Topic subscribed ist

#### **MQTT-Client Callback:**
```python
def _on_message(self, client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode('utf-8'))
    
    # Business-Function Callbacks
    self._notify_business_functions(topic, payload)
```

#### **Business-Manager:**
```python
class SensorManager:
    def __init__(self):
        self.sensor_data = {}  # State-Holder
    
    def process_sensor_message(self, topic: str, payload: Dict[str, Any]):
        # Direkte Payload-Verarbeitung (kein JSON-Parsing)
        processed_data = self._extract_sensor_data(topic, payload)
        self.sensor_data[topic] = processed_data
    
    def get_sensor_data(self, sensor_id: str = None):
        # UI liest aus State-Holder
        return self.sensor_data.get(sensor_id) if sensor_id else self.sensor_data
```

#### **UI-Komponente:**
```python
def render_sensor_data_subtab():
    sensor_manager = get_ccu_sensor_manager()
    sensor_data = sensor_manager.get_sensor_data()  # Liest aus State-Holder
    
    # Anzeige der Daten
    for topic, data in sensor_data.items():
        st.metric(f"Sensor {topic}", data['temperature'])
```

### **🎯 KRITISCHE REGELN:**

1. **Direkte Payload-Verarbeitung:** Manager bekommen `topic` + `payload`, nicht Message-Struktur
2. **Kein JSON-Parsing in Manager:** Payload ist bereits Dict
3. **State-Holder Pattern:** Manager halten aktuellen Business-State
4. **UI liest nur aus Manager:** Nie direkt aus MQTT-Client oder Gateway-Buffers
5. **request_refresh() Pattern:** Nie `st.rerun()` verwenden
6. **Schema-Validierung:** Über MessageManager gegen Registry-Schemas

### **📊 VORTEILE:**

- **Trennung der Verantwortlichkeiten:** Transport vs. Business vs. Presentation
- **Testbarkeit:** Manager können unabhängig getestet werden
- **Skalierbarkeit:** Einfache Erweiterung um neue Business-Manager
- **Konsistenz:** Klarer Datenfluss ohne Race-Conditions
- **Performance:** Kein unnötiges JSON-Parsing oder Message-Wrapping

### **🧪 TESTING:**

```python
# Verwendet echte Test-Payloads aus test_payloads_for_topic/
def test_sensor_manager_process_message():
    sensor_manager = get_ccu_sensor_manager()
    topic = "/j1/txt/1/i/bme680"
    payload = {"t": 26.2, "h": 29.2, "p": 1003.9, "iaq": 34}
    
    sensor_manager.process_sensor_message(topic, payload)
    sensor_data = sensor_manager.get_sensor_data()
    assert topic in sensor_data
```

**Status:** ✅ IMPLEMENTIERT FÜR SENSOR-DATEN  
**Nächste Schritte:** Erweitern auf Module-Manager und weitere Business-Manager

---

---

## 9. ✅ BEST PRACTICE LOGGING-SYSTEM (NEU IMPLEMENTIERT)

**Status: VOLLSTÄNDIG IMPLEMENTIERT** ✅  
**Datum: 2025-10-06**  
**Pattern: Level-spezifische Ringbuffer mit Thread-Safety**

### **🎯 ARCHITEKTUR-PRINZIP:**

```
Application Startup → Multi-Level Ringbuffer Handler → UI Log Tabs
```

### **📋 KOMPONENTEN:**

#### **MultiLevelRingBufferHandler:**
- **Thread-sicherer Handler** für alle Log-Level
- **Separate Ringbuffer** für ERROR, WARNING, INFO, DEBUG
- **Level-spezifische Buffer-Größen** (ERROR/WARNING größer für wichtige Logs)
- **Thread-Safety** mit `threading.Lock()` für MQTT-Callbacks

#### **Setup-Funktion:**
- **Frühe Initialisierung** vor erstem `logger.info()`
- **Handler nur EINMAL** anhängen (verhindert Duplikate)
- **DEBUG Level** um alle Logs zu erfassen
- **Session State** Integration für Streamlit

### **🔧 IMPLEMENTIERUNG:**

#### **Handler-Initialisierung:**
```python
# omf2/common/logger.py
class MultiLevelRingBufferHandler(logging.Handler):
    def __init__(self, buffer_sizes=None):
        super().__init__()
        self.buffer_sizes = buffer_sizes or {
            "ERROR": 200,      # Größer für wichtige Errors
            "WARNING": 200,    # Größer für wichtige Warnings  
            "INFO": 500,       # Standard für Info-Logs
            "DEBUG": 300       # Kleinere für Debug-Logs
        }
        self.buffers = {
            level: deque(maxlen=size)
            for level, size in self.buffer_sizes.items()
        }
        self._lock = threading.Lock()

    def emit(self, record):
        msg = self.format(record)
        level = record.levelname
        with self._lock:
            self.buffers.get(level, self.buffers["INFO"]).append(msg)

    def get_buffer(self, level=None):
        with self._lock:
            if level:
                return list(self.buffers.get(level, []))
            return {lvl: list(buf) for lvl, buf in self.buffers.items()}
```

#### **Setup-Funktion:**
```python
def setup_multilevel_ringbuffer_logging():
    """
    Initialisiert einen MultiLevelRingBufferHandler und hängt ihn an den Root-Logger.
    Gibt das Handler-Objekt und die Referenz auf die Buffers zurück.
    """
    logger = logging.getLogger()
    # Prüfe, ob schon vorhanden
    if not any(isinstance(h, MultiLevelRingBufferHandler) for h in logger.handlers):
        handler = MultiLevelRingBufferHandler()
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    else:
        handler = next(h for h in logger.handlers if isinstance(h, MultiLevelRingBufferHandler))
    return handler, handler.buffers
```

#### **Application Startup (omf.py):**
```python
# BEST PRACTICE: Frühe Initialisierung vor erstem logger.info()
from omf2.common.logger import setup_multilevel_ringbuffer_logging

if 'log_handler' not in st.session_state:
    handler, buffers = setup_multilevel_ringbuffer_logging()
    st.session_state['log_handler'] = handler
    st.session_state['log_buffers'] = buffers
```

#### **UI-Integration:**
```python
# System Logs Tab
log_handler = st.session_state.get('log_handler')
if log_handler:
    # Kombiniere alle Level-spezifischen Buffer
    all_logs = []
    for level in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
        all_logs.extend(log_handler.get_buffer(level))
    
    # Sortiere nach Timestamp (neueste zuerst)
    all_logs.sort(key=lambda x: x.split(']')[0] if ']' in x else x, reverse=True)

# Error & Warning Tab
error_logs = log_handler.get_buffer('ERROR')
warning_logs = log_handler.get_buffer('WARNING')
```

### **🎯 KRITISCHE REGELN:**

1. **Frühe Initialisierung:** Handler wird vor erstem `logger.info()` erstellt
2. **Handler nur EINMAL:** Prüfung auf existierende Handler, keine Duplikate
3. **Thread-Safety:** `threading.Lock()` für sichere Buffer-Zugriffe
4. **Level-spezifische Buffer:** Separate Buffer schützen wichtige Logs
5. **Session State:** Handler und Buffer in `st.session_state` gespeichert
6. **DEBUG Level:** Handler erfasst alle Log-Level

### **📊 VORTEILE:**

- **Schutz wichtiger Logs:** ERROR/WARNING werden nicht von DEBUG/INFO verdrängt
- **Thread-Safety:** Sichere Zugriffe aus MQTT-Callbacks
- **UI-Integration:** Dedicated Tabs für kritische Logs
- **Performance:** Optimierte Buffer-Größen pro Level
- **Wartbarkeit:** Zentrale Logging-Konfiguration

### **🧪 TESTING:**

```python
# Test der kompletten Integration
handler, buffers = setup_multilevel_ringbuffer_logging()

# Simuliere echte OMF2 Logs
logger = logging.getLogger('omf2.admin.admin_gateway')
logger.error('❌ Schema validation failed for module/v1/ff/SVR3QA2098/factsheet: headerId is a required property')

logger = logging.getLogger('omf2.ccu.ccu_mqtt_client')  
logger.error('❌ CCU Message processing error: list indices must be integers or slices, not str')

# Prüfe Ergebnisse
error_logs = handler.get_buffer('ERROR')
warning_logs = handler.get_buffer('WARNING')

assert len(error_logs) == 2
assert len(warning_logs) == 0
```

**Status:** ✅ VOLLSTÄNDIG IMPLEMENTIERT UND GETESTET  
**UI-Integration:** ✅ ERROR & WARNING TABS FUNKTIONAL  
**Thread-Safety:** ✅ MQTT-CALLBACKS GETESTET  

---

**Letzte Aktualisierung:** 2025-10-09  
**Status:** VOLLSTÄNDIG IMPLEMENTIERT ✅  
**Message Processing Pattern:** DOKUMENTIERT ✅  
**Schema-Validation:** SYSTEMATISCH KORRIGIERT ✅  
**Business-Manager Pattern:** IMPLEMENTIERT UND DOKUMENTIERT ✅  
**Best Practice Logging-System:** IMPLEMENTIERT UND DOKUMENTIERT ✅  
**Asymmetrische Architektur:** VERIFIED UND DOKUMENTIERT ✅  
**Gateway-Routing-Hints:** KLARGESTELLT UND DOKUMENTIERT ✅