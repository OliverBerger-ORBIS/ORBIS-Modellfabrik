# OMF-APS Data Model Analysis

## Overview
Analyse der Datenmodelle und Entitäten, die das APS-Dashboard benötigt, im Vergleich zu unserem bestehenden OMF-System.

## APS Dashboard Datenmodelle (aus FF_DPS_24V.py)

### **1. VDA5050 Standard-Datenmodelle**

#### **Order Management**
```python
# VDA5050 Order Structure
vda_data = {
    "stateId": 0,
    "orderId": "",
    "orderUpdateId": 0,
    "lastOrderId": "",
    "lastOrderTimestamp": 0,
    "actions": [],
    "errors": []
}

# Order Processing
order = {
    "orderId": "string",
    "timestamp": "ISO8601",
    "action": "STORAGE",
    "type": "RED|BLUE|WHITE",
    "workpieceId": "string"
}
```

#### **State Management**
```python
# VDA5050 State Structure
state = {
    "operatingMode": "TEACHIN|AUTOMATIC",
    "headerId": 1,
    "timestamp": "ISO8601",
    "serialNumber": "controller_id",
    "orderId": "current_order_id",
    "orderUpdateId": 0,
    "paused": false,
    "actionState": {
        "command": "string",
        "id": "string",
        "state": "WAITING|RUNNING|FINISHED|FAILED",
        "timestamp": "ISO8601",
        "result": {}
    },
    "actionStates": [],
    "batteryState": {},
    "errors": [],
    "information": []
}
```

#### **Instant Actions**
```python
# APS Instant Actions
INSTANT_ACTION_RESET = 'reset'
INSTANT_ACTION_ACCOUNCE_OUTPUT = 'announceOutput'
INSTANT_ACTION_CANCEL_STORAGE_ORDER = 'cancelStorageOrder'

# System Control Commands
system_commands = [
    "ccu/set/reset",
    "ccu/set/charge",
    "ccu/set/layout",
    "ccu/set/flows",
    "ccu/set/calibration",
    "ccu/set/park"
]
```

### **2. APS-spezifische Entitäten**

#### **Module Management (Dynamische IP-Erkennung)**
```python
# TXT Controller Modules - IP-Adressen werden dynamisch erkannt
# Über Factsheet Messages (retained) + Module State Messages (live)
txt_controllers = {
    "SVR4H73275": {  # DPS - Serial Number als eindeutiger Identifier
        "role": "CCU", 
        "functions": ["warehouse", "nfc", "camera"],
        "ip_address": "dynamisch_erkannt",  # 192.168.0.102 (variabel)
        "discovery_method": "factsheet + state_messages"
    },
    "SVR4H76530": {  # AIQS
        "role": "quality_control", 
        "functions": ["ai_recognition", "camera"],
        "ip_address": "dynamisch_erkannt",  # 192.168.0.103 (variabel)
        "discovery_method": "factsheet + state_messages"
    },
    "SVR4H76449": {  # HBW
        "role": "warehouse", 
        "functions": ["storage", "retrieval"],
        "ip_address": "dynamisch_erkannt",  # 192.168.0.104 (variabel)
        "discovery_method": "factsheet + state_messages"
    },
    "SVR3QA0022": {  # MILL
        "role": "machining", 
        "functions": ["milling"],
        "ip_address": "dynamisch_erkannt",  # 192.168.0.105 (variabel)
        "discovery_method": "factsheet + state_messages"
    }
}

# Physical Modules
physical_modules = {
    "HBW": {"serial": "SVR4H76449", "type": "warehouse", "functions": ["storage", "retrieval"]},
    "MILL": {"serial": "SVR3QA0022", "type": "milling", "functions": ["machining"]},
    "DRILL": {"serial": "SVR3QA2098", "type": "drilling", "functions": ["machining"]},
    "CHRG": {"serial": "CHRG0", "type": "charging", "functions": ["passive_charging"]}
}
```

#### **Inventory Management**
```python
# HBW Storage Positions
inventory_positions = {
    "A1": {"loadType": "RED|BLUE|WHITE", "loadPosition": "A1", "status": "occupied|empty"},
    "A2": {"loadType": "RED|BLUE|WHITE", "loadPosition": "A2", "status": "occupied|empty"},
    "A3": {"loadType": "RED|BLUE|WHITE", "loadPosition": "A3", "status": "occupied|empty"},
    "B1": {"loadType": "RED|BLUE|WHITE", "loadPosition": "B1", "status": "occupied|empty"},
    "B2": {"loadType": "RED|BLUE|WHITE", "loadPosition": "B2", "status": "occupied|empty"},
    "B3": {"loadType": "RED|BLUE|WHITE", "loadPosition": "B3", "status": "occupied|empty"},
    "C1": {"loadType": "RED|BLUE|WHITE", "loadPosition": "C1", "status": "occupied|empty"},
    "C2": {"loadType": "RED|BLUE|WHITE", "loadPosition": "C2", "status": "occupied|empty"},
    "C3": {"loadType": "RED|BLUE|WHITE", "loadPosition": "C3", "status": "occupied|empty"}
}
```

## OMF System Datenmodelle (bestehend)

### **1. Module Management**

#### **OmfModuleManager**
```python
# Bestehende OMF Module-Struktur
class OmfModuleManager:
    def get_all_modules(self) -> Dict[str, Any]
    def get_module_by_id(self, module_id: str) -> Dict[str, Any]
    def get_module_serial_numbers(self) -> List[str]
    def get_module_types(self) -> List[str]
    def get_module_functions(self, module_id: str) -> List[str]
```

#### **ModuleStateManager**
```python
# Bestehende Module State-Struktur
class ModuleStateManager:
    def get_module_state(self, module_id: str) -> Dict[str, Any]
    def update_module_state(self, module_id: str, state: Dict[str, Any])
    def get_all_module_states(self) -> Dict[str, Dict[str, Any]]
```

### **2. Order Management**

#### **OrderTrackingManager**
```python
# Bestehende Order-Struktur
class OrderTrackingManager:
    def start_order_tracking(self, workpiece_id: str, color: str, order_type: str) -> str
    def update_order_status(self, order_id: str, status: str, message: Dict[str, Any])
    def get_active_orders(self) -> Dict[str, Dict[str, Any]]
    def get_order_history(self) -> List[Dict[str, Any]]
```

#### **OrderManager (Dashboard)**
```python
# Bestehende Dashboard Order-Struktur
class OrderManager:
    def __init__(self):
        self.inventory = {
            "A1": None, "A2": None, "A3": None,
            "B1": None, "B2": None, "B3": None,
            "C1": None, "C2": None, "C3": None
        }
        self.workpiece_types = ["RED", "BLUE", "WHITE"]
        self.orders = []
```

### **3. MQTT Integration**

#### **OmfMqttClient**
```python
# Bestehende MQTT-Client-Struktur
class OmfMqttClient:
    def subscribe_many(self, topics: List[str], qos: int = 1)
    def get_buffer(self, pattern: str) -> List[Dict[str, Any]]
    def publish(self, topic: str, payload: str, qos: int = 1)
```

#### **TopicManager**
```python
# Bestehende Topic-Management-Struktur
class OmfTopicManager:
    def get_topic_patterns(self, category: str) -> List[str]
    def get_all_topics(self) -> Dict[str, List[str]]
    def get_module_topics(self, module_id: str) -> List[str]
```

## Vergleichsanalyse

### **✅ Vollständig Kompatibel**

#### **1. Module Management**
- **OMF**: `OmfModuleManager` + `ModuleStateManager`
- **APS**: TXT Controller + Physical Modules
- **Kompatibilität**: ✅ OMF kann APS-Module verwalten

#### **2. Order Management**
- **OMF**: `OrderTrackingManager` + `OrderManager`
- **APS**: VDA5050 Order System
- **Kompatibilität**: ✅ OMF kann VDA5050 Orders verarbeiten

#### **3. Inventory Management**
- **OMF**: `OrderManager.inventory` (A1-C3 Positions)
- **APS**: HBW Storage Positions (A1-C3)
- **Kompatibilität**: ✅ Identische Struktur

#### **4. MQTT Integration**
- **OMF**: `OmfMqttClient` + `TopicManager`
- **APS**: VDA5050 Topics + System Control Topics
- **Kompatibilität**: ✅ OMF kann APS-Topics verwalten

### **⚠️ Erweiterungsbedarf**

#### **1. VDA5050 Standard**
```python
# FEHLT: VDA5050-konforme Datenstrukturen
class VDA5050OrderManager:
    def create_vda5050_order(self, color: str, workpiece_id: str) -> Dict[str, Any]
    def process_vda5050_state(self, state_message: Dict[str, Any])
    def send_instant_action(self, action_type: str, parameters: Dict[str, Any])
```

#### **2. APS-spezifische Module (Dynamische Discovery)**
```python
# FEHLT: APS TXT Controller Management mit dynamischer IP-Erkennung
class APSTXTControllerManager:
    def process_factsheet_message(self, topic: str, payload: str) -> bool
    def process_state_message(self, topic: str, payload: str) -> bool
    def get_discovered_controllers(self) -> Dict[str, Dict[str, Any]]
    def get_controller_by_serial(self, serial: str) -> Dict[str, Any]
    def get_controller_by_ip(self, ip: str) -> Dict[str, Any]
    def get_controller_ip(self, serial: str) -> str
    def get_online_controllers(self) -> Dict[str, Dict[str, Any]]
    def get_expected_topics(self) -> List[str]
```

#### **3. System Control Commands**
```python
# FEHLT: APS System Control
class APSSystemControlManager:
    def send_system_command(self, command: str, parameters: Dict[str, Any])
    def get_system_status(self) -> Dict[str, Any]
    def reset_factory(self)
    def charge_fts(self)
```

## Verzeichnisstruktur-Analyse

### **✅ Bestehende Struktur ist geeignet**

#### **1. Tools-Verzeichnis**
```
omf/tools/
├── module_manager.py          # ✅ Module Management
├── module_state_manager.py    # ✅ State Management
├── order_tracking_manager.py  # ✅ Order Management
├── mqtt_client.py             # ✅ MQTT Integration
├── topic_manager.py           # ✅ Topic Management
└── message_template_manager.py # ✅ Message Templates
```

#### **2. Dashboard Components**
```
omf/dashboard/components/
├── overview_inventory.py      # ✅ Inventory Management
├── overview_module_status.py  # ✅ Module Status
├── production_order.py        # ✅ Order Management
└── steering.py                # ✅ Control Interface
```

#### **3. Analysis Tools**
```
omf/analysis_tools/
├── module_manager.py          # ✅ Module Analysis
├── order_tracking_manager.py  # ✅ Order Analysis
└── nfc_code_manager.py        # ✅ NFC Management
```

### **🔧 Erweiterungsbedarf**

#### **1. Neue APS-spezifische Manager**
```
omf/tools/
├── aps_vda5050_manager.py     # NEU: VDA5050 Standard
├── aps_txt_controller_manager.py # NEU: TXT Controller Management
└── aps_system_control_manager.py # NEU: System Control
```

#### **2. APS Dashboard Components**
```
omf/dashboard/components/
├── aps_overview.py            # NEU: APS Overview
├── aps_steering.py            # NEU: APS Steering
├── aps_orders.py              # NEU: APS Orders
└── aps_configuration.py       # NEU: APS Configuration
```

## Implementierungs-Plan

### **Phase 1: VDA5050 Integration**
```python
# 1. VDA5050 Manager erstellen
class VDA5050OrderManager:
    def create_storage_order(self, color: str, workpiece_id: str) -> Dict[str, Any]
    def process_order_response(self, response: Dict[str, Any])
    def send_instant_action(self, action: str, params: Dict[str, Any])

# 2. Bestehende OrderManager erweitern
class OrderManager:
    def __init__(self):
        self.vda5050_manager = VDA5050OrderManager()
        # ... bestehende Struktur
```

### **Phase 2: APS Module Integration**
```python
# 1. APS TXT Controller Manager
class APSTXTControllerManager:
    def get_controllers(self) -> Dict[str, Dict[str, Any]]
    def get_controller_status(self, controller_id: str) -> Dict[str, Any]

# 2. Bestehende ModuleManager erweitern
class OmfModuleManager:
    def __init__(self):
        self.aps_controller_manager = APSTXTControllerManager()
        # ... bestehende Struktur
```

### **Phase 3: System Control Integration**
```python
# 1. APS System Control Manager
class APSSystemControlManager:
    def send_system_command(self, command: str, params: Dict[str, Any])
    def get_system_status(self) -> Dict[str, Any]

# 2. Bestehende MQTT-Client erweitern
class OmfMqttClient:
    def __init__(self):
        self.aps_system_control = APSSystemControlManager()
        # ... bestehende Struktur
```

## Fazit

### **✅ OMF-System ist gut vorbereitet**
- **Bestehende Manager** können APS-Funktionalität erweitern
- **Verzeichnisstruktur** ist geeignet für APS-Integration
- **MQTT-Integration** ist bereits vorhanden
- **Dashboard-Komponenten** können erweitert werden

### **🔧 Erweiterungsbedarf minimal**
- **VDA5050 Standard** implementieren
- **APS-spezifische Manager** hinzufügen
- **Dashboard-Komponenten** für APS erweitern
- **MQTT-Topics** für APS erweitern

### **📈 Migrationsstrategie**
1. **Bestehende Struktur beibehalten**
2. **APS-Funktionalität parallel entwickeln**
3. **Schrittweise Integration**
4. **Rollback möglich**

## Nächste Schritte

1. **VDA5050OrderManager** implementieren
2. **APSTXTControllerManager** implementieren
3. **APSSystemControlManager** implementieren
4. **APS Dashboard Components** erstellen
5. **Integration testen**
