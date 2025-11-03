# ✅ IMPLEMENTIERTE ARCHITEKTUR: Gekapseltes MQTT, Registry Manager & Gateway für Streamlit-Apps

**Status: VOLLSTÄNDIG IMPLEMENTIERT** ✅  
**Datum: 2025-10-10**  
**Tests: 55 Tests erfolgreich** ✅  
**Registry-Migration: ABGESCHLOSSEN** ✅  
**Architektur-Cleanup: ABGESCHLOSSEN** ✅  
**Schema-Validation: SYSTEMATISCH KORRIGIERT** ✅  
**Gateway-Routing: MIT SCHEMA-VALIDIERUNG IMPLEMENTIERT** ✅  
**Meta-Parameter: VOLLSTÄNDIG INTEGRIERT** ✅  
**Order Manager: VOLLSTÄNDIG IMPLEMENTIERT** ✅  
**Log-Rotation: IMPLEMENTIERT** ✅  
**Asymmetrische Architektur: VERIFIED UND DOKUMENTIERT** ✅  
**Gateway-Routing-Hints: KLARGESTELLT** ✅  
**i18n-Implementierung: VOLLSTÄNDIG (DE, EN, FR)** ✅  
**Storage Orders Logic: VOLLSTÄNDIG IMPLEMENTIERT** ✅ NEW!
**UI-Konsistenz zwischen Production und Storage Orders: IMPLEMENTIERT** ✅ NEW!

**Ziel:**  
Weggekapselte, robuste Architektur für MQTT-Kommunikation, Message-Templates und UI-Refresh in einer Streamlit-App, sodass UI- und Business-Logik möglichst einfach bleiben und typische Fehlerquellen (Threading, Race-Conditions, Deadlocks, inkonsistenter State) vermieden werden.

**✅ ERREICHT:** Alle Ziele wurden erfolgreich implementiert und getestet.

**🔧 AKTUELLE ERKENNTNISSE (2025-10-10):**
- **Storage Orders Logic (VOLLSTÄNDIG)**: Storage Orders verarbeiten `ccu/order/active` und `ccu/order/completed` Messages
- **UI-Konsistenz (IMPLEMENTIERT)**: Production und Storage Orders verwenden identische UISymbols und Darstellung
- **Command-Mapping-Korrektur**: Storage Orders verwenden korrekte PICK/DROP → LADEN/ENTLADEN AGV Logik
- **Shopfloor Layout Integration**: Storage Orders zeigen aktive Module und FTS Navigation
- **Navigation Step Enhancement**: UX-Verbesserung für Navigation Steps (IN_PROGRESS wenn kein Production Step aktiv)
- **i18n-Implementierung (VOLLSTÄNDIG)**: 3 Sprachen (DE, EN, FR), 195+ Translation Keys, 18 YAML-Dateien
- **Asymmetrische Architektur (VERIFIED)**: Commands über NodeRed, Telemetry direct für TXT-Module
- **Gateway-Routing-Hints**: `routed_topics` statt `subscribed_topics` - Semantik klargestellt
- **Topic-Semantische Felder**: `observed_publisher_aps`, `semantic_role`, `omf2_usage` für Guidance
- **OMF2 CCU-Domain**: Frontend + Backend in einer Domain (kann parallel zu APS-CCU-Backend laufen)
- **Order Manager**: Order-Lifecycle Management (active → completed) implementiert
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
- **✅ I18nManager** (`omf2/common/i18n.py`)  
  Internationalization Manager mit 3 Sprachen (DE, EN, FR), Lazy Loading und Session State Integration.
- **✅ i18n-Übersetzungen** (`omf2/config/translations/`)  
  18 YAML-Dateien mit 195+ Translation Keys für alle UI-Komponenten.

---

## 2. ✅ IMPLEMENTIERTE ARCHITEKTUR

### **Gateway-Routing-Pattern mit Schema-Validierung (AKTUALISIERT)**

**Command-Versende-Pattern (Architektur-Compliant):**
```
┌─────────────────────┐
│ Business Function   │  ← UI/Manager
│ - send_order()      │  → Gateway.publish_message()
│ - send_command()    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Gateway           │  ← Schema-Validation + Registry-QoS/Retain
│  - publish_message()│  → MessageManager.validate_message()
│  - Registry-Config  │  → QoS/Retain aus Registry
│  - Meta-Separation  │  → Transport-Details ≠ Payload-Daten
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  MQTT Client        │  ← Registry-basierte QoS/Retain
│  - publish()        │  → Registry-Konfiguration
│  - Meta-Parameter   │  → mqtt_timestamp nur in Buffer
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   MQTT Broker       │  ← Clean Transport ohne Meta-Parameter
└─────────────────────┘
```

**Message-Receiving-Pattern:**
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
1. **🔌 MQTT Client:** Raw MQTT → JSON + Meta-Parameter (nur im Buffer)
2. **🛡️ Gateway:** Schema-Validierung + Registry-basierte QoS/Retain
3. **🧠 Business Manager:** Clean Business-Logik ohne Transport-Details
4. **🎨 UI Components:** Manager-Zugriff über Gateway-Pattern

**Kritische Architektur-Prinzipien:**
- ✅ **Meta-Parameter-Trennung:** Transport-Details ≠ Payload-Daten
- ✅ **Zentrale Validierung:** MessageManager.validate_message() in allen Gateways
- ✅ **Registry-basierte QoS/Retain:** Keine hardcodierten Werte
- ✅ **Schema-Compliance:** Alle Messages validiert vor Publishing

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

### 4.2 StockManager (Inventory & Order Management)

**Zweck:** Verarbeitet Stock-Messages (Lagerbestand) und verwaltet Kundenaufträge/Rohmaterial-Bestellungen.

**Datei:** `omf2/ccu/stock_manager.py`

**🔧 WICHTIGE ARCHITEKTUR-PATTERNS:**

**1. Non-Blocking Initialization (KRITISCH):**
```python
class StockManager:
    def __init__(self):
        """Initialize Stock Manager - EXAKT wie Sensor Manager (kein File I/O!)"""
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
_stock_manager_instance = None

def get_stock_manager() -> StockManager:
    global _stock_manager_instance
    if _stock_manager_instance is None:
        _stock_manager_instance = StockManager()
        logger.info("🏗️ Stock Manager singleton created")
    return _stock_manager_instance
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
    stock_manager = get_stock_manager()  # Non-Blocking Singleton
    inventory_status = stock_manager.get_inventory_status()  # Non-Blocking
    
    # Display inventory with direct SVG rendering via Asset-Manager
    for position, workpiece in inventory_status["inventory"].items():
        if workpiece is None:
            palett = asset_manager.get_workpiece_palett()
            st.markdown(f"<div style=\"border:1px solid #ccc; padding:10px; text-align:center;\">{palett}</div>", unsafe_allow_html=True)
        else:
            svg = asset_manager.get_workpiece_svg(workpiece, "instock_unprocessed")
            st.markdown(f"<div style=\"border:1px solid #ccc; padding:10px; text-align:center;\">{svg}</div>", unsafe_allow_html=True)
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
- ✅ **Gateway-Pattern:** MQTT → Gateway → Stock Manager → UI
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
- `tests/test_omf2/test_comprehensive_architecture.py` - 14 Tests ✅
- `tests/test_omf2/test_gateway_factory.py` - 14 Tests ✅
- `tests/test_omf2/test_registry_v2_integration_simple.py` - 10 Tests ✅
- `tests/test_omf2/test_registry_manager_comprehensive.py` - 20 Tests ✅
- `tests/test_omf2/test_sensor_manager.py` - SensorManager Tests (geplant)
- `tests/test_omf2/test_message_manager.py` - MessageManager Tests ✅
- `tests/test_omf2/test_topic_manager.py` - TopicManager Tests ✅
- `tests/test_omf2/test_admin_message_manager.py` - AdminMessageManager Tests ✅

### **📊 TEST-STATISTIK:**
- **55 Tests erfolgreich** ✅
- **0 Fehler** ✅
- **Thread-Safety** getestet ✅
- **Registry v2 Integration** getestet ✅
- **Registry Manager** getestet ✅
- **Performance** optimiert ✅

### **🚀 VERWENDUNG (Centralized MQTT Connect):**

> FORBIDDEN: MQTT-Connect/Disconnect direkt in Tabs oder Komponenten ausführen.
> MQTT-Connect/Disconnect erfolgt zentral in `omf.py` beim Render.

- Verbindliche Anleitung: `docs/04-howto/mqtt_client_connection.md`
- Kernpunkte:
  - Keine direkten `client.connect()` Aufrufe in Tabs/Komponenten
  - MQTT-Connect erfolgt zentral in `omf.py` beim Render (wenn nicht verbunden)
  - Refresh-Buttons können überall sein (Sidebar, Header, etc.), solange sie `request_refresh()` verwenden
  - Beim Environment-Switch nur Disconnect; kein Auto-Reconnect

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
      
      stock_manager:
        routed_topics:  # Topics die an StockManager.onMessage() geroutet werden
          - "/j1/txt/1/f/i/stock"      # HBW Inventory FROM TXT (Stock-Management)
      
      order_manager:
        routed_topics:  # Topics die an OrderManager.onMessage() geroutet werden
          - "ccu/order/request"         # PRIMARY trigger for new orders
          - "ccu/order/response"        # Order confirmation with UUID
          - "ccu/order/active"          # Active orders queue
          - "ccu/order/completed"       # Completed orders log
```

#### **Wichtige Architektur-Details:**

**🔑 Gateway-Routing-Hints vs. Subscriptions:**
1. **`subscribed_topics`** (Haupt-Liste): MQTT Client subscribed diese Topics am Broker
2. **`gateway_routing_hints.xxx.routed_topics`** (Routing-Info): Gateway routet an Business Functions

**🚨 KRITISCHE ERKENNTNIS (2025-10-16):**
- **Tests vs. Echte Architektur:** Tests testen direkte Manager-Instanzen, aber die echte Architektur verwendet Registry-basiertes Topic-Routing über `mqtt_clients.yml`
- **Manager Renaming:** Bei Manager-Renaming müssen ALLE Referenzen aktualisiert werden: Datei, Klasse, Singleton, Gateway, Registry, UI-Komponenten, Tests
- **Registry-basierte Architektur:** Das Gateway liest `mqtt_clients.yml` und routet Topics basierend auf `routed_topics` an die entsprechenden Manager

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

## 11. ✅ i18n-ARCHITEKTUR (VOLLSTÄNDIG IMPLEMENTIERT)

**Status: VOLLSTÄNDIG IMPLEMENTIERT** ✅  
**Datum: 2025-10-10**  
**Pattern: Lazy Loading mit Session State Integration**

### **🎯 ARCHITEKTUR-PRINZIP:**

```
UI Component → I18nManager (Session State) → YAML Files → Translated Text
```

### **📋 KOMPONENTEN:**

#### **I18nManager:**
- **Lazy Loading:** Kein File I/O im `__init__()` - Non-Blocking
- **Session State Integration:** Zentrale Sprach-Instanz pro Session
- **3 Sprachen:** Deutsch (DE), English (EN), Français (FR)
- **Fallback-Mechanismus:** Inline-Übersetzungen als Backup
- **Thread-Safety:** Sichere Zugriffe aus MQTT-Callbacks

#### **YAML-Übersetzungsdateien:**
- **18 YAML-Dateien** in `omf2/config/translations/`
- **195+ Translation Keys** für alle UI-Texte
- **Flache Struktur:** Keine tiefen Verschachtelungen
- **Domain-Aufteilung:** CCU, Admin, Node-RED, Common

### **🔧 IMPLEMENTIERUNG:**

#### **I18nManager-Initialisierung:**
```python
# omf2/common/i18n.py
class I18nManager:
    def __init__(self, session_state=None):
        """Initialize I18nManager - KEIN File I/O hier!"""
        self.session_state = session_state
        self.translations = None  # Lazy Loading
        self.supported_languages = ['de', 'en', 'fr']
        self.translations_path = Path(__file__).parent.parent / "config" / "translations"
        # Kein _load_translations() mehr beim Init - Lazy Loading!
    
    def _get_translations(self):
        """Lazy Loading für Translations - wird beim ersten Zugriff geladen"""
        if self.translations is None:
            self._load_translations()
        return self.translations
```

#### **Session State Integration:**
```python
# omf2/omf.py - Application Startup
if 'i18n_manager' not in st.session_state:
    from omf2.common.i18n import I18nManager
    st.session_state['i18n_manager'] = I18nManager(st.session_state)
```

#### **UI-Integration:**
```python
# UI Component
def render_ccu_overview_tab():
    # Zentrale Instanz aus Session State
    i18n = st.session_state.get("i18n_manager")
    if i18n:
        title = i18n.t("ccu_overview.title")
        st.header(f"{UISymbols.get_functional_icon('ccu')} {title}")
    
    # Hardcodierte Texte durch i18n.t() ersetzen
    workpieces_text = i18n.t("ccu_overview.purchase_orders.workpieces").format(workpiece_type=workpiece_type)
    st.markdown(f"#### {icons.get(workpiece_type, '📦')} {workpieces_text}")
```

### **🎯 KRITISCHE REGELN:**

#### **1. Session State Pattern:**
```python
# ✅ KORREKT: Zentrale Instanz aus Session State
i18n = st.session_state.get("i18n_manager")
if i18n:
    title = i18n.t("ccu_overview.title")

# ❌ FALSCH: Lokale Instanz erstellen
i18n = I18nManager("de")  # Verursacht Sprachinkonsistenzen
```

#### **2. Lazy Loading:**
```python
# ✅ KORREKT: Kein File I/O im __init__
def __init__(self):
    self.translations = None  # Lazy Loading

# ❌ FALSCH: File I/O im __init__
def __init__(self):
    self.translations = self._load_translations()  # ← BLOCKIERT UI!
```

#### **3. Fallback-Mechanismus:**
```python
# ✅ KORREKT: Fallback zu inline-Übersetzungen
def t(self, key: str, **kwargs) -> str:
    translations = self._get_translations()
    if key in translations:
        return translations[key].format(**kwargs)
    else:
        # Fallback zu inline-Übersetzungen
        return self._get_fallback_translation(key, **kwargs)
```

### **📊 IMPLEMENTIERTE BEREICHE:**

#### **CCU-Domain (100% mehrsprachig):**
- **CCU Overview Tab:** Product Catalog, Customer Orders, Purchase Orders, Inventory, Sensor Data
- **CCU Orders Tab:** Production Orders, Storage Orders
- **CCU Modules Tab:** Module Overview, Statistics, Controls
- **CCU Configuration Tab:** Factory Configuration, Parameter Configuration
- **CCU Process Tab:** Production Plan, Monitoring

#### **Admin-Domain (100% mehrsprachig):**
- **Admin Settings Tab:** System Settings, Schemas
- **Generic Steering Tab:** Factory Steering, FTS Control
- **Message Center Tab:** Message Monitoring, Filtering
- **System Logs Tab:** Error & Warning Logs, System Logs

#### **Node-RED-Domain (100% mehrsprachig):**
- **Node-RED Overview Tab:** Process Overview, Status
- **Node-RED Processes Tab:** Process Management, Controls

### **📚 DOKUMENTATION:**

#### **Entwicklungsregeln:**
- **`I18N_DEVELOPMENT_RULES.md`** - Entwicklungsregeln für i18n
- **Code-Beispiele** für korrekte Implementierung
- **Best Practices** für Performance und Wartbarkeit

#### **Implementierungsstatus:**
- **`I18N_IMPLEMENTATION_COMPLETE.md`** - Vollständige Implementierungsdokumentation
- **195+ Translation Keys** dokumentiert
- **18 YAML-Dateien** aufgelistet
- **Domain-Aufteilung** (CCU, Admin, Node-RED) beschrieben

### **🧪 TESTING:**

```python
# Test der i18n-Integration
i18n = I18nManager()
assert i18n.t("ccu_overview.title") == "CCU Overview"
assert i18n.t("common.buttons.order") == "Bestellen"

# Test der Session State Integration
st.session_state['i18n_manager'] = I18nManager(st.session_state)
i18n = st.session_state.get("i18n_manager")
assert i18n is not None
```

### **📊 VORTEILE:**

- **Konsistente Mehrsprachigkeit:** Alle UI-Texte über i18n-System
- **Wartbarkeit:** Flache YAML-Struktur, keine tiefen Verschachtelungen
- **Performance:** Lazy Loading, Session State Integration
- **Entwicklerfreundlichkeit:** Automatische Validierung via Pre-commit Hooks
- **Non-Blocking:** Kein File I/O beim Initialisieren
- **Thread-Safety:** Sichere Zugriffe aus MQTT-Callbacks

**Status:** ✅ VOLLSTÄNDIG IMPLEMENTIERT UND DOKUMENTIERT  
**UI-Integration:** ✅ ALLE TABS MEHRSPRACHIG  
**Performance:** ✅ LAZY LOADING OPTIMIERT  

---

## 12. ✅ ANLEITUNG: Neuen Business-Manager hinzufügen

**Status: KRITISCH - MUSS FÜR JEDEN NEUEN MANAGER BEFOLGT WERDEN**  
**Datum: 2025-10-09**  
**Ziel: Konsistente Implementierung neuer Business-Funktionalität**

---

### **🎯 ZWEI PERSPEKTIVEN:**

#### **A) ANALYSE & PLANUNG (Top-Down):**
1. **Requirements analysieren** - Was soll der Manager tun?
2. **Topics identifizieren** - Welche MQTT-Topics werden benötigt?
3. **Gateway-Routing planen** - Wie werden Messages geroutet?
4. **Manager-API definieren** - Welche Methoden braucht die UI?
5. **Registry-Konfiguration planen** - Welche Topics subscribed?

#### **B) IMPLEMENTIERUNG (Bottom-Up - EMPFOHLEN):**
1. **MQTT-Client erweitern** - Topics in `mqtt_clients.yml` hinzufügen
2. **Test 1** - Subscriptions testen
3. **Gateway-Routing** - Routing-Logik in `ccu_gateway.py` hinzufügen
4. **Test 2** - Gateway-Routing testen
5. **Manager implementieren** - Business-Logic in neuem Manager
6. **Test 3** - Manager-Methoden testen
7. **UI-Wrapper** - Leere UI-Komponente für Display
8. **Test 4** - End-to-End Test

---

### **📋 SCHRITT-FÜR-SCHRITT-ANLEITUNG (Implementierung):**

#### **Schritt 1: Topics in Registry hinzufügen**

**Datei:** `omf2/registry/mqtt_clients.yml`

```yaml
mqtt_clients:
  ccu_mqtt_client:
    subscribed_topics:
      # ... bestehende Topics ...
      
      # NEU: Topics für XyzManager
      - "domain/xyz/topic1"        # Beschreibung
      - "domain/xyz/topic2"        # Beschreibung
    
    gateway_routing_hints:
      # ... bestehende Hints ...
      
      xyz_manager:  # NEU
        routed_topics:  # Topics die an XyzManager.onMessage() geroutet werden
          - "domain/xyz/topic1"    # Beschreibung
          - "domain/xyz/topic2"    # Beschreibung
```

**✅ Validierung:**
- Alle `routed_topics` MÜSSEN in `subscribed_topics` sein
- Pre-commit Hook prüft Topic-Validität

**Test 1:** MQTT-Client kann Topics subscribieren
```bash
streamlit run omf2/omf.py
# → Prüfe in Admin → System Logs ob Subscriptions erfolgreich
```

---

#### **Schritt 2: Gateway-Routing implementieren**

**Datei:** `omf2/ccu/ccu_gateway.py`

```python
class CcuGateway:
    def __init__(self, mqtt_client=None, **kwargs):
        # ... bestehende Topic-Listen ...
        
        # NEU: XYZ Topics für XyzManager
        self.xyz_topics = {
            'domain/xyz/topic1',
            'domain/xyz/topic2'
        }
        
        # Manager-Instanz (Lazy Loading)
        self._xyz_manager = None
    
    def _get_xyz_manager(self):
        """Lazy Loading für XyzManager (Singleton)"""
        if self._xyz_manager is None:
            from omf2.ccu.xyz_manager import get_xyz_manager
            self._xyz_manager = get_xyz_manager()
            logger.info("🏗️ XyzManager initialized via Gateway")
        return self._xyz_manager
    
    def _route_ccu_message(self, topic, message, meta=None):
        # ... bestehende Routing-Logik ...
        
        # NEU: Routing für XyzManager
        if topic in self.xyz_topics:
            logger.debug(f"🔀 Routing to xyz_manager: {topic}")
            xyz_manager = self._get_xyz_manager()
            if xyz_manager:
                xyz_manager.process_xyz_message(topic, message, meta)
            else:
                logger.warning(f"⚠️ XyzManager not available for topic: {topic}")
            return True
```

**Test 2:** Gateway routet Messages korrekt
```bash
# 1. Streamlit starten
# 2. Test-Message senden über Session Manager
# 3. Logs prüfen: "🔀 Routing to xyz_manager"
```

---

#### **Schritt 3: Business-Manager implementieren**

**Datei:** `omf2/ccu/xyz_manager.py`

```python
#!/usr/bin/env python3
"""
CCU XYZ Manager - Business Logic für XYZ Management
Verarbeitet XYZ-Nachrichten vom Topic domain/xyz/*
"""

import threading
from datetime import datetime, timezone
from typing import Dict, Any
from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Singleton Factory - EXAKT wie Stock Manager
_xyz_manager_instance = None


class XyzManager:
    """
    XYZ Manager für CCU Domain
    Verwaltet XYZ-Daten und Business-Logic
    """

    def __init__(self):
        """Initialize XYZ Manager - EXAKT wie Stock Manager (kein File I/O!)"""
        # State-Holder (wie sensor_data beim Sensor Manager)
        self.xyz_data = {}
        
        # Thread-Sicherheit
        self._lock = threading.Lock()
        
        # Zeitstempel
        self.last_update = None
        
        logger.info("🏗️ XYZ Manager initialized with State-Holder (no file I/O)")

    def process_xyz_message(self, topic: str, message: Dict[str, Any], meta: Dict[str, Any]) -> None:
        """
        Verarbeitet XYZ-Nachrichten vom Topic domain/xyz/*
        
        Args:
            topic: MQTT Topic
            message: Message payload (Dict/List/Str - NIE raw bytes!)
            meta: Meta-Informationen (timestamp, qos, retain)
        """
        try:
            with self._lock:
                logger.debug(f"📋 Processing XYZ message from {topic}: {message}")
                
                # Message Processing Pattern verwenden (siehe MESSAGE_PROCESSING_PATTERN.md)
                # STEP 1: Log message structure
                logger.info(f"Raw message keys: {list(message.keys())}")
                
                # STEP 2: Extract data
                processed_data = self._extract_xyz_data(topic, message)
                
                # STEP 3: Update State-Holder
                self.xyz_data[topic] = processed_data
                
                # Zeitstempel aktualisieren
                self.last_update = datetime.now(timezone.utc)
                
                logger.info(f"✅ XYZ data updated from {topic}")
                
        except Exception as e:
            logger.error(f"❌ Error processing XYZ message from {topic}: {e}")

    def _extract_xyz_data(self, topic: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrahiert XYZ-Daten aus Message
        
        WICHTIG: Message Processing Pattern befolgen!
        - Keine Annahmen über Message-Struktur
        - Debug-Logging für Sichtbarkeit
        - Echte Feld-Namen verwenden (aus MQTT-Daten)
        """
        # TODO: Implementierung basierend auf echten MQTT-Daten
        return {}

    def get_xyz_data(self) -> Dict[str, Any]:
        """
        Gibt XYZ-Daten zurück (für UI)
        
        Returns:
            Dict mit XYZ-Daten
        """
        with self._lock:
            return {
                "data": self.xyz_data.copy(),
                "last_update": self.last_update.isoformat() if self.last_update else None
            }


def get_xyz_manager() -> XyzManager:
    """
    Get XYZ Manager singleton instance - EXAKT wie Stock Manager
    
    Returns:
        XyzManager: XYZ Manager Instanz
    """
    global _xyz_manager_instance
    if _xyz_manager_instance is None:
        _xyz_manager_instance = XyzManager()
        logger.info("🏗️ XYZ Manager singleton created")
    return _xyz_manager_instance
```

**Test 3:** Manager empfängt und verarbeitet Messages
```bash
# 1. Session Manager: Test-Message senden
# 2. Logs prüfen: "✅ XYZ data updated from domain/xyz/topic1"
# 3. Python-Shell: get_xyz_manager().get_xyz_data()
```

---

#### **Schritt 4: Gateway-Methoden für UI**

**Datei:** `omf2/ccu/ccu_gateway.py`

```python
class CcuGateway:
    # ... Manager-Routing bereits in Schritt 2 ...
    
    # NEU: Public API für UI
    def get_xyz_data(self) -> Dict[str, Any]:
        """
        XYZ-Daten abrufen - Non-Blocking
        
        Returns:
            Dict mit XYZ-Daten
        """
        try:
            xyz_manager = self._get_xyz_manager()
            if xyz_manager is None:
                logger.warning("⚠️ XYZ Manager not available")
                return {}
            
            return xyz_manager.get_xyz_data()
        except Exception as e:
            logger.error(f"❌ Error getting XYZ data: {e}")
            return {}
```

---

#### **Schritt 5: UI-Komponente (Leerer Wrapper)**

**Datei:** `omf2/ui/ccu/ccu_xyz/ccu_xyz_tab.py`

```python
"""
CCU XYZ Tab - Zeigt XYZ-Daten an
"""
import streamlit as st
from omf2.factory.gateway_factory import get_ccu_gateway
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_ccu_xyz_tab():
    """Rendert CCU XYZ Tab"""
    st.header("🔀 XYZ Management")
    
    try:
        # Gateway holen
        ccu_gateway = get_ccu_gateway()
        
        # XYZ-Daten vom Manager holen
        xyz_data = ccu_gateway.get_xyz_data()
        
        # Anzeige
        if xyz_data.get("data"):
            st.json(xyz_data["data"])
            st.caption(f"Last Update: {xyz_data.get('last_update', 'Never')}")
        else:
            st.info("No XYZ data available")
            
    except Exception as e:
        st.error(f"❌ Error rendering XYZ tab: {e}")
        logger.error(f"❌ XYZ tab error: {e}")
```

**Test 4:** UI zeigt Daten an
```bash
streamlit run omf2/omf.py
# → CCU → XYZ Tab öffnen
# → Sollte "No XYZ data available" zeigen
# → Test-Message senden → Daten sollten erscheinen
```

---

### **📋 CHECKLISTE für neuen Business-Manager:**

#### **Analyse & Planung:**
- [ ] Requirements definiert (Was soll der Manager tun?)
- [ ] Topics aus Registry identifiziert (Welche Topics werden benötigt?)
- [ ] APS "as-IS" verstanden (observed_publisher_aps, semantic_role)
- [ ] OMF2-Rolle geklärt (omf2_usage, omf2_note)

#### **Registry-Konfiguration:**
- [ ] Topics in `ccu_mqtt_client.subscribed_topics` hinzugefügt
- [ ] `gateway_routing_hints.xyz_manager.routed_topics` definiert
- [ ] Alle `routed_topics` sind in `subscribed_topics` enthalten
- [ ] Pre-commit Hook erfolgreich

#### **Gateway-Integration:**
- [ ] Topic-Liste als Set/Präfix in `__init__()` definiert
- [ ] `_get_xyz_manager()` Lazy-Loading implementiert
- [ ] Routing-Logik in `_route_ccu_message()` hinzugefügt
- [ ] Public API-Methoden für UI implementiert (z.B. `get_xyz_data()`)

#### **Manager-Implementierung:**
- [ ] Singleton Factory Pattern (`get_xyz_manager()`)
- [ ] **KEIN File I/O im `__init__()`** (Non-Blocking!)
- [ ] State-Holder Pattern (z.B. `self.xyz_data = {}`)
- [ ] Thread-Safety (`threading.Lock()`)
- [ ] `process_xyz_message()` implementiert
- [ ] Message Processing Pattern befolgt (siehe MESSAGE_PROCESSING_PATTERN.md)
- [ ] Public API für UI (z.B. `get_xyz_data()`)

#### **Testing:**
- [ ] Test 1: MQTT-Client Subscriptions funktionieren
- [ ] Test 2: Gateway routet Messages korrekt
- [ ] Test 3: Manager empfängt und verarbeitet Messages
- [ ] Test 4: UI zeigt Daten korrekt an
- [ ] End-to-End Test: Echte MQTT-Message → UI-Anzeige

#### **Dokumentation:**
- [ ] Manager in `ARCHITECTURE.md` dokumentiert
- [ ] Manager in `PROJECT_STRUCTURE.md` aufgeführt
- [ ] Gateway-Routing-Hints in `mqtt_clients.yml` dokumentiert

---

### **🚨 KRITISCHE REGELN (NIEMALS VERLETZEN):**

#### **1. Manager-Implementierung:**
```python
# ✅ KORREKT: Non-Blocking __init__
class XyzManager:
    def __init__(self):
        self.xyz_data = {}  # State-Holder
        self._lock = threading.Lock()
        # KEIN File I/O hier!

# ❌ FALSCH: Blocking __init__
class XyzManager:
    def __init__(self):
        self.config = load_config_file()  # ← BLOCKIERT Streamlit UI!
```

#### **2. Lock-Hierarchie (Deadlock-Vermeidung):**
```python
# ✅ KORREKT: Nur äußerste Methode mit Lock
def get_xyz_status(self):
    with self._lock:
        data = self._process_internal()  # ← OHNE Lock!
        return data

def _process_internal(self):
    # KEIN self._lock hier!
    return {}

# ❌ FALSCH: Verschachtelte Locks → DEADLOCK
def get_xyz_status(self):
    with self._lock:
        data = self._process_internal()  # ← Versucht Lock nochmal!
        return data

def _process_internal(self):
    with self._lock:  # ← DEADLOCK!
        return {}
```

#### **3. Message Processing Pattern:**
```python
# ✅ KORREKT: Message Processing Pattern befolgen
def process_xyz_message(self, topic, message, meta):
    # STEP 1: Log message structure
    logger.info(f"Raw message keys: {list(message.keys())}")
    
    # STEP 2: Extract data (keine Annahmen!)
    data = self._extract_xyz_data(topic, message)
    
    # STEP 3: Update State-Holder
    with self._lock:
        self.xyz_data[topic] = data

# ❌ FALSCH: Annahmen über Message-Struktur
def process_xyz_message(self, topic, message, meta):
    # KEINE Logs!
    temperature = message["temperature"]  # ← Kann KeyError sein!
```

#### **4. Gateway-Routing-Reihenfolge:**
```python
# ✅ KORREKT: Spezifische Topics VOR Präfix-Matching
def _route_ccu_message(self, topic, message, meta):
    # 1. Sensor Topics (Set-basiert) - O(1) Lookup
    if topic in self.sensor_topics:
        # ...
    
    # 2. Order Topics (Set-basiert) - O(1) Lookup
    if topic in self.order_topics:
        # ...
    
    # 3. Module Topics (Präfix-basiert) - Flexibel aber langsamer
    for prefix in self.module_topic_prefixes:
        if topic.startswith(prefix):
            # ...
```

---

### **🎯 TEMPLATE-CODE (Copy & Paste Ready):**

#### **Manager Template:**
```python
#!/usr/bin/env python3
"""
CCU XYZ Manager - Business Logic für XYZ Management
"""

import threading
from datetime import datetime, timezone
from typing import Dict, Any
from omf2.common.logger import get_logger

logger = get_logger(__name__)
_xyz_manager_instance = None


class XyzManager:
    """XYZ Manager für CCU Domain"""

    def __init__(self):
        """Initialize XYZ Manager - KEIN File I/O!"""
        self.xyz_data = {}
        self._lock = threading.Lock()
        self.last_update = None
        logger.info("🏗️ XYZ Manager initialized")

    def process_xyz_message(self, topic: str, message: Dict[str, Any], meta: Dict[str, Any]) -> None:
        """Verarbeitet XYZ-Nachrichten"""
        try:
            with self._lock:
                logger.debug(f"📋 Processing XYZ message from {topic}")
                # TODO: Implementierung
                self.last_update = datetime.now(timezone.utc)
                logger.info(f"✅ XYZ data updated from {topic}")
        except Exception as e:
            logger.error(f"❌ Error processing XYZ message: {e}")

    def get_xyz_data(self) -> Dict[str, Any]:
        """Gibt XYZ-Daten zurück (für UI)"""
        with self._lock:
            return {
                "data": self.xyz_data.copy(),
                "last_update": self.last_update.isoformat() if self.last_update else None
            }


def get_xyz_manager() -> XyzManager:
    """Get XYZ Manager singleton instance"""
    global _xyz_manager_instance
    if _xyz_manager_instance is None:
        _xyz_manager_instance = XyzManager()
        logger.info("🏗️ XYZ Manager singleton created")
    return _xyz_manager_instance
```

---

### **🧪 TESTING-STRATEGIE:**

#### **Test 1: MQTT-Client Subscriptions**
```bash
# Starte Streamlit
streamlit run omf2/omf.py

# Prüfe Logs:
# - "📡 Subscribed to topic: domain/xyz/topic1"
# - Keine Subscription-Fehler
```

#### **Test 2: Gateway-Routing**
```bash
# Session Manager: Test-Message an domain/xyz/topic1 senden
# Prüfe Logs:
# - "🔀 Routing to xyz_manager: domain/xyz/topic1"
# - "🏗️ XYZ Manager initialized via Gateway"
```

#### **Test 3: Manager Message-Processing**
```bash
# Test-Message senden
# Prüfe Logs:
# - "📋 Processing XYZ message from domain/xyz/topic1"
# - "✅ XYZ data updated from domain/xyz/topic1"
# - Keine Processing-Fehler
```

#### **Test 4: UI-Integration**
```python
# Python-Shell oder Streamlit
from omf2.factory.gateway_factory import get_ccu_gateway
gateway = get_ccu_gateway()
xyz_data = gateway.get_xyz_data()
print(xyz_data)  # Sollte Daten zeigen
```

---

### **📚 REFERENZ-BEISPIELE:**

**Einfacher Manager (State-Holder):**
- `omf2/ccu/sensor_manager.py` - Sensor-Daten sammeln
- `omf2/ccu/order_manager.py` - Inventory-Management

**Komplexer Manager (Lifecycle-Management):**
- `omf2/ccu/production_order_manager.py` - Order Tracking (active → completed)

**Gateway-Integration:**
- `omf2/ccu/ccu_gateway.py` - Zeilen 51-129 (Topic-Listen + Lazy Loading)
- `omf2/ccu/ccu_gateway.py` - Zeilen 173-243 (Routing-Logik)

**Registry-Konfiguration:**
- `omf2/registry/mqtt_clients.yml` - Zeilen 105-190 (subscribed_topics + gateway_routing_hints)

**Message Processing Pattern:**
- `omf2/docs/MESSAGE_PROCESSING_PATTERN.md` - Standard-Pattern für alle Manager

---

### **⚠️ HÄUFIGE FEHLER (VERMEIDEN):**

#### **1. File I/O im `__init__()`:**
```python
# ❌ FALSCH
def __init__(self):
    self.config = json.load(open("config.json"))  # ← BLOCKIERT UI!

# ✅ KORREKT
def __init__(self):
    self.config = {}  # Lazy Loading später
```

#### **2. Verschachtelte Locks:**
```python
# ❌ FALSCH
def get_data(self):
    with self._lock:
        return self._internal_method()  # ← Versucht Lock nochmal!

def _internal_method(self):
    with self._lock:  # ← DEADLOCK!
        return {}
```

#### **3. Manager subscribed selbst Topics:**
```python
# ❌ FALSCH
class XyzManager:
    def __init__(self):
        mqtt_client.subscribe("domain/xyz/topic1")  # ← NIEMALS!

# ✅ KORREKT: Nur in mqtt_clients.yml!
```

#### **4. Message-Struktur Annahmen:**
```python
# ❌ FALSCH
def process_message(self, topic, message, meta):
    value = message["temperature"]  # ← KeyError möglich!

# ✅ KORREKT
def process_message(self, topic, message, meta):
    logger.info(f"Message keys: {list(message.keys())}")  # ← Debug first!
    value = message.get("t", 0.0)  # ← Echtes Feld-Name + Fallback
```

---

### **📖 ZUSAMMENFASSUNG:**

**Implementierungs-Reihenfolge (Bottom-Up):**
1. **MQTT-Client** → Test Subscriptions
2. **Gateway-Routing** → Test Routing
3. **Manager** → Test Message-Processing
4. **UI-Wrapper** → Test End-to-End

**Kritische Erfolgsfaktoren:**
- ✅ Non-Blocking `__init__()` (kein File I/O!)
- ✅ Korrekte Lock-Hierarchie (keine verschachtelten Locks!)
- ✅ Message Processing Pattern befolgen (Debug-Logging!)
- ✅ Gateway-Pattern verwenden (Manager subscribed NICHT selbst!)
- ✅ Singleton Factory Pattern (ein Manager pro Domain!)

**Dokumentation-Must-Haves:**
- ✅ Topics in `mqtt_clients.yml` (subscribed + routing_hints)
- ✅ Gateway-Integration in `ccu_gateway.py` dokumentiert
- ✅ Manager in `ARCHITECTURE.md` aufgeführt
- ✅ Template-Code als Referenz

---

**Letzte Aktualisierung:** 2025-10-10  
**Status:** VOLLSTÄNDIG IMPLEMENTIERT ✅  
**Message Processing Pattern:** DOKUMENTIERT ✅  
**Schema-Validation:** SYSTEMATISCH KORRIGIERT ✅  
**Business-Manager Pattern:** IMPLEMENTIERT UND DOKUMENTIERT ✅  
**Best Practice Logging-System:** IMPLEMENTIERT UND DOKUMENTIERT ✅  
**Asymmetrische Architektur:** VERIFIED UND DOKUMENTIERT ✅  
**Gateway-Routing-Hints:** KLARGESTELLT UND DOKUMENTIERT ✅  
**i18n-Implementierung:** VOLLSTÄNDIG (DE, EN, FR) ✅ NEW!