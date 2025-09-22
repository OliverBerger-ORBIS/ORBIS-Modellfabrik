# Registry Compatibility Analysis

## Overview
Analyse der Kompatibilität der APS-Integration mit der bestehenden Registry-Philosophie und Vorschläge für Erweiterungen.

## Registry-Philosophie Analyse

### **✅ Vollständig Kompatibel**

#### **1. Registry v1 Struktur**
```
registry/
├── model/v1/
│   ├── workpieces.yml          # ✅ NFC Codes → WorkpieceManager
│   ├── modules.yml             # ✅ Module Management
│   ├── topics/                 # ✅ Topic Management
│   │   ├── ccu.yml            # ✅ System Control Topics
│   │   ├── module.yml         # ✅ VDA5050 Topics
│   │   └── txt.yml            # ✅ TXT Controller Topics
│   └── templates/             # ✅ Message Templates
```

#### **2. Schema-basierte Validierung**
- **JSON Schemas** in `registry/schemas/`
- **YAML-basierte Konfiguration**
- **Versionierte Modelle** (v0, v1)
- **Template-Integration**

## Erweiterungsvorschläge

### **1. WorkpieceManager (NFC_codeManager → WorkpieceManager)**

#### **1.1 Registry-Erweiterung**
```yaml
# registry/model/v1/workpieces.yml (erweitert)
metadata:
  version: "4.0.0"
  description: "OMF Workpiece Management mit VDA5050 Integration"
  last_updated: "2025-09-19"
  author: "OMF Development Team"

# Bestehende NFC Codes beibehalten
nfc_codes:
  # ... bestehende NFC Codes

# NEU: VDA5050 Workpiece Types
vda5050_workpiece_types:
  RED:
    description: "Rotes Werkstück"
    process_time: "5 min"
    quality_check_required: true
    storage_positions: ["A1", "A2", "A3"]
    enabled: true
    
  BLUE:
    description: "Blaues Werkstück"
    process_time: "7 min"
    quality_check_required: true
    storage_positions: ["B1", "B2", "B3"]
    enabled: true
    
  WHITE:
    description: "Weißes Werkstück"
    process_time: "10 min"
    quality_check_required: true
    storage_positions: ["C1", "C2", "C3"]
    enabled: true

# NEU: APS-spezifische Workpiece Properties
aps_workpiece_properties:
  order_types:
    - "STORAGE"
    - "RETRIEVAL"
    - "TRANSPORT"
  
  quality_states:
    - "OK"
    - "NOT-OK"
    - "PENDING"
    - "FAILED"
  
  storage_states:
    - "occupied"
    - "empty"
    - "reserved"
    - "maintenance"

# NEU: VDA5050 Template Integration
vda5050_templates:
  order_template:
    orderId: "<orderId>"
    timestamp: "<timestamp>"
    action: "STORAGE"
    type: "<color>"
    workpieceId: "<workpieceId>"
    orderUpdateId: 0
  
  state_template:
    operatingMode: "AUTOMATIC"
    headerId: "<headerId>"
    timestamp: "<timestamp>"
    serialNumber: "<serialNumber>"
    orderId: "<orderId>"
    orderUpdateId: "<orderUpdateId>"
    paused: false
    actionState: "<actionState>"
    actionStates: []
    batteryState: {}
    errors: []
    information: []
```

#### **1.2 WorkpieceManager Implementation**
```python
# omf/tools/workpiece_manager.py (NEU)
"""
WorkpieceManager - Erweiterte Werkstück-Verwaltung
Ersetzt NFCCodeManager mit VDA5050-Integration
"""

from omf.tools.registry_manager import get_registry
from omf.dashboard.tools.logging_config import get_logger

class WorkpieceManager:
    """Erweiterte Werkstück-Verwaltung mit VDA5050-Integration"""
    
    def __init__(self):
        self.logger = get_logger("omf.tools.workpiece_manager")
        self.registry = get_registry()
        
        # Bestehende NFC-Funktionalität beibehalten
        self.nfc_codes = self.registry.workpieces().get("nfc_codes", {})
        
        # NEU: VDA5050 Workpiece Types
        self.vda5050_types = self.registry.workpieces().get("vda5050_workpiece_types", {})
        
        # NEU: APS Properties
        self.aps_properties = self.registry.workpieces().get("aps_workpiece_properties", {})
    
    # Bestehende NFC-Funktionalität beibehalten
    def get_nfc_code_by_friendly_id(self, friendly_id: str) -> Optional[Dict[str, Any]]:
        """Gibt NFC-Code nach Friendly ID zurück (bestehend)"""
        for nfc_code, data in self.nfc_codes.items():
            if data.get("friendly_id") == friendly_id:
                return {"nfc_code": nfc_code, **data}
        return None
    
    def get_workpiece_by_color(self, color: str) -> List[Dict[str, Any]]:
        """Gibt alle Werkstücke einer Farbe zurück (bestehend)"""
        return [{"nfc_code": nfc_code, **data} 
                for nfc_code, data in self.nfc_codes.items() 
                if data.get("color") == color]
    
    # NEU: VDA5050-Integration
    def create_vda5050_order(self, color: str, workpiece_id: str = None) -> Dict[str, Any]:
        """Erstellt VDA5050-konforme Order"""
        if color not in self.vda5050_types:
            raise ValueError(f"Unbekannte Werkstück-Farbe: {color}")
        
        workpiece_type = self.vda5050_types[color]
        
        order = {
            "orderId": self._generate_order_id(),
            "timestamp": self._get_timestamp(),
            "action": "STORAGE",
            "type": color,
            "workpieceId": workpiece_id or self._generate_workpiece_id(color),
            "orderUpdateId": 0
        }
        
        self.logger.info(f"📋 VDA5050 Order erstellt: {color} Werkstück")
        return order
    
    def get_workpiece_type_info(self, color: str) -> Optional[Dict[str, Any]]:
        """Gibt Werkstück-Typ-Informationen zurück"""
        return self.vda5050_types.get(color)
    
    def get_available_colors(self) -> List[str]:
        """Gibt verfügbare Werkstück-Farben zurück"""
        return list(self.vda5050_types.keys())
    
    def get_storage_positions(self, color: str) -> List[str]:
        """Gibt verfügbare Lagerpositionen für Farbe zurück"""
        workpiece_type = self.vda5050_types.get(color, {})
        return workpiece_type.get("storage_positions", [])
    
    # NEU: APS-spezifische Funktionen
    def get_order_types(self) -> List[str]:
        """Gibt verfügbare Order-Typen zurück"""
        return self.aps_properties.get("order_types", [])
    
    def get_quality_states(self) -> List[str]:
        """Gibt verfügbare Quality-States zurück"""
        return self.aps_properties.get("quality_states", [])
    
    def get_storage_states(self) -> List[str]:
        """Gibt verfügbare Storage-States zurück"""
        return self.aps_properties.get("storage_states", [])
```

### **2. TopicManager Erweiterung für APS-Topics**

#### **2.1 Registry-Erweiterung**
```yaml
# registry/model/v1/topics/aps.yml (NEU)
metadata:
  version: "1.0.0"
  description: "APS-spezifische MQTT-Topics"
  last_updated: "2025-09-19"
  author: "OMF Development Team"

topics:
  # VDA5050 Standard Topics
  vda5050:
    order:
      pattern: "module/v1/ff/NodeRed/{controller_id}/order"
      description: "VDA5050 Order Messages"
      qos: 2
      retain: false
      direction: "pub/sub"
      
    instant_actions:
      pattern: "module/v1/ff/NodeRed/{controller_id}/instantActions"
      description: "VDA5050 Instant Action Messages"
      qos: 2
      retain: false
      direction: "pub/sub"
      
    state:
      pattern: "module/v1/ff/NodeRed/{controller_id}/state"
      description: "VDA5050 State Messages"
      qos: 2
      retain: true
      direction: "pub"
      
    connection:
      pattern: "module/v1/ff/NodeRed/{controller_id}/connection"
      description: "VDA5050 Connection Messages"
      qos: 1
      retain: true
      direction: "pub"
      
    factsheet:
      pattern: "module/v1/ff/NodeRed/{controller_id}/factsheet"
      description: "VDA5050 Factsheet Messages"
      qos: 2
      retain: true
      direction: "pub"

  # System Control Topics
  system_control:
    reset:
      pattern: "ccu/set/reset"
      description: "Factory Reset Command"
      qos: 2
      retain: false
      direction: "pub"
      
    charge:
      pattern: "ccu/set/charge"
      description: "FTS Charge Command"
      qos: 2
      retain: false
      direction: "pub"
      
    layout:
      pattern: "ccu/set/layout"
      description: "Layout Management Command"
      qos: 2
      retain: false
      direction: "pub"
      
    flows:
      pattern: "ccu/set/flows"
      description: "Flow Control Command"
      qos: 2
      retain: false
      direction: "pub"
      
    calibration:
      pattern: "ccu/set/calibration"
      description: "Calibration Command"
      qos: 2
      retain: false
      direction: "pub"
      
    park:
      pattern: "ccu/set/park"
      description: "Park Factory Command"
      qos: 2
      retain: false
      direction: "pub"

  # TXT Controller Topics
  txt_controller:
    bme680:
      pattern: "/j1/txt/1/c/bme680"
      description: "BME680 Sensor Data"
      qos: 2
      retain: false
      direction: "pub"
      
    ldr:
      pattern: "/j1/txt/1/c/ldr"
      description: "Light Sensor Data"
      qos: 2
      retain: false
      direction: "pub"
      
    camera:
      pattern: "/j1/txt/1/c/cam"
      description: "Camera Data"
      qos: 2
      retain: false
      direction: "pub"
      
    broadcast:
      pattern: "/j1/txt/1/c/broadcast"
      description: "Broadcast Messages"
      qos: 2
      retain: false
      direction: "pub"
      
    nfc:
      pattern: "/j1/txt/1/f/i/nfc/ds"
      description: "NFC Commands"
      qos: 2
      retain: false
      direction: "pub"
```

#### **2.2 TopicManager Erweiterung**
```python
# omf/tools/topic_manager.py (erweitert)
class OmfTopicManager:
    """Erweiterte Topic-Verwaltung mit APS-Integration"""
    
    def __init__(self, config_path: str = None):
        # Bestehende Initialisierung beibehalten
        # ...
        
        # NEU: APS-Topics laden
        self.aps_topics = self._load_aps_topics()
    
    def _load_aps_topics(self) -> Dict[str, Any]:
        """Lädt APS-spezifische Topics aus Registry"""
        try:
            topics_dir = self.project_root / "registry" / "model" / "v1" / "topics"
            aps_topic_file = topics_dir / "aps.yml"
            
            if aps_topic_file.exists():
                with open(aps_topic_file, encoding="utf-8") as f:
                    return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"APS-Topics konnten nicht geladen werden: {e}")
        
        return {}
    
    # NEU: APS-spezifische Topic-Funktionen
    def get_aps_topics(self, category: str = None) -> Dict[str, Any]:
        """Gibt APS-Topics zurück"""
        if category:
            return self.aps_topics.get("topics", {}).get(category, {})
        return self.aps_topics.get("topics", {})
    
    def get_vda5050_topics(self) -> Dict[str, Any]:
        """Gibt VDA5050-Topics zurück"""
        return self.get_aps_topics("vda5050")
    
    def get_system_control_topics(self) -> Dict[str, Any]:
        """Gibt System Control Topics zurück"""
        return self.get_aps_topics("system_control")
    
    def get_txt_controller_topics(self) -> Dict[str, Any]:
        """Gibt TXT Controller Topics zurück"""
        return self.get_aps_topics("txt_controller")
    
    def get_aps_topic_patterns(self, category: str = None) -> List[str]:
        """Gibt APS-Topic-Patterns zurück"""
        topics = self.get_aps_topics(category)
        patterns = []
        
        for topic_category, topic_data in topics.items():
            if isinstance(topic_data, dict):
                for topic_name, topic_info in topic_data.items():
                    if isinstance(topic_info, dict) and "pattern" in topic_info:
                        patterns.append(topic_info["pattern"])
        
        return patterns
    
    def get_aps_subscription_topics(self) -> List[str]:
        """Gibt alle APS-Subscription-Topics zurück"""
        patterns = []
        
        # VDA5050 Topics (pub/sub)
        vda5050_topics = self.get_vda5050_topics()
        for topic_name, topic_info in vda5050_topics.items():
            if topic_info.get("direction") in ["pub/sub", "sub"]:
                patterns.append(topic_info["pattern"])
        
        # TXT Controller Topics (pub)
        txt_topics = self.get_txt_controller_topics()
        for topic_name, topic_info in txt_topics.items():
            if topic_info.get("direction") in ["pub/sub", "sub"]:
                patterns.append(topic_info["pattern"])
        
        return patterns
    
    def get_aps_publication_topics(self) -> List[str]:
        """Gibt alle APS-Publication-Topics zurück"""
        patterns = []
        
        # VDA5050 Topics (pub/sub)
        vda5050_topics = self.get_vda5050_topics()
        for topic_name, topic_info in vda5050_topics.items():
            if topic_info.get("direction") in ["pub/sub", "pub"]:
                patterns.append(topic_info["pattern"])
        
        # System Control Topics (pub)
        system_topics = self.get_system_control_topics()
        for topic_name, topic_info in system_topics.items():
            if topic_info.get("direction") in ["pub/sub", "pub"]:
                patterns.append(topic_info["pattern"])
        
        return patterns
```

### **3. Messages Menü Erweiterung**

#### **3.1 Bestehende Nachrichten-Zentrale erweitern**
```python
# omf/dashboard/components/message_center.py (erweitert)
def show_message_center():
    """Erweiterte Nachrichten-Zentrale mit APS-Integration"""
    st.header("📡 Nachrichten-Zentrale")
    
    # Bestehende Funktionalität beibehalten
    # ...
    
    # NEU: APS-spezifische Tabs
    message_tab1, message_tab2, message_tab3, message_tab4 = st.tabs([
        "📡 Alle Topics",        # Bestehend: Alle Topics
        "🏭 APS Topics",         # NEU: APS-spezifische Topics
        "📋 VDA5050 Messages",   # NEU: VDA5050 Messages
        "🎮 System Commands"     # NEU: System Commands
    ])
    
    # Tab 1: Alle Topics (bestehend)
    with message_tab1:
        show_all_topics()
    
    # Tab 2: APS Topics (NEU)
    with message_tab2:
        show_aps_topics()
    
    # Tab 3: VDA5050 Messages (NEU)
    with message_tab3:
        show_vda5050_messages()
    
    # Tab 4: System Commands (NEU)
    with message_tab4:
        show_system_commands()

def show_aps_topics():
    """APS-spezifische Topics anzeigen"""
    st.subheader("🏭 APS Topics")
    
    topic_manager = get_omf_topic_manager()
    
    # VDA5050 Topics
    st.subheader("📋 VDA5050 Topics")
    vda5050_topics = topic_manager.get_vda5050_topics()
    
    for topic_name, topic_info in vda5050_topics.items():
        with st.expander(f"VDA5050 {topic_name}"):
            st.write(f"**Pattern:** `{topic_info['pattern']}`")
            st.write(f"**Description:** {topic_info['description']}")
            st.write(f"**QoS:** {topic_info['qos']}")
            st.write(f"**Direction:** {topic_info['direction']}")
    
    # System Control Topics
    st.subheader("🎮 System Control Topics")
    system_topics = topic_manager.get_system_control_topics()
    
    for topic_name, topic_info in system_topics.items():
        with st.expander(f"System {topic_name}"):
            st.write(f"**Pattern:** `{topic_info['pattern']}`")
            st.write(f"**Description:** {topic_info['description']}")
            st.write(f"**QoS:** {topic_info['qos']}")
            st.write(f"**Direction:** {topic_info['direction']}")

def show_vda5050_messages():
    """VDA5050 Messages anzeigen"""
    st.subheader("📋 VDA5050 Messages")
    
    # VDA5050 Message Templates
    st.subheader("📋 Message Templates")
    
    vda5050_templates = {
        "Order": {
            "orderId": "<orderId>",
            "timestamp": "<timestamp>",
            "action": "STORAGE",
            "type": "<color>",
            "workpieceId": "<workpieceId>",
            "orderUpdateId": 0
        },
        "State": {
            "operatingMode": "AUTOMATIC",
            "headerId": "<headerId>",
            "timestamp": "<timestamp>",
            "serialNumber": "<serialNumber>",
            "orderId": "<orderId>",
            "orderUpdateId": "<orderUpdateId>",
            "paused": False,
            "actionState": "<actionState>",
            "actionStates": [],
            "batteryState": {},
            "errors": [],
            "information": []
        }
    }
    
    for template_name, template_data in vda5050_templates.items():
        with st.expander(f"VDA5050 {template_name} Template"):
            st.json(template_data)

def show_system_commands():
    """System Commands anzeigen"""
    st.subheader("🎮 System Commands")
    
    system_commands = {
        "Factory Reset": {
            "topic": "ccu/set/reset",
            "description": "Komplette Fabrik zurücksetzen",
            "parameters": {}
        },
        "FTS Charge": {
            "topic": "ccu/set/charge",
            "description": "FTS aufladen",
            "parameters": {"charge": True}
        },
        "Layout Management": {
            "topic": "ccu/set/layout",
            "description": "Layout verwalten",
            "parameters": {}
        }
    }
    
    for command_name, command_info in system_commands.items():
        with st.expander(f"Command: {command_name}"):
            st.write(f"**Topic:** `{command_info['topic']}`")
            st.write(f"**Description:** {command_info['description']}")
            st.write(f"**Parameters:** {command_info['parameters']}")
```

## Schema-Erweiterungen

### **1. Workpieces Schema erweitern**
```json
// registry/schemas/workpieces.schema.json (erweitert)
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OMF Workpieces Schema",
  "version": "4.0.0",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "version": {"type": "string"},
        "description": {"type": "string"},
        "last_updated": {"type": "string"},
        "author": {"type": "string"}
      }
    },
    "nfc_codes": {
      "type": "object",
      "patternProperties": {
        "^[0-9a-fA-F]+$": {
          "type": "object",
          "properties": {
            "friendly_id": {"type": "string"},
            "color": {"enum": ["RED", "BLUE", "WHITE"]},
            "quality_check": {"enum": ["OK", "NOT-OK", "PENDING", "FAILED"]},
            "description": {"type": "string"},
            "enabled": {"type": "boolean"}
          }
        }
      }
    },
    "vda5050_workpiece_types": {
      "type": "object",
      "patternProperties": {
        "^(RED|BLUE|WHITE)$": {
          "type": "object",
          "properties": {
            "description": {"type": "string"},
            "process_time": {"type": "string"},
            "quality_check_required": {"type": "boolean"},
            "storage_positions": {
              "type": "array",
              "items": {"type": "string"}
            },
            "enabled": {"type": "boolean"}
          }
        }
      }
    },
    "aps_workpiece_properties": {
      "type": "object",
      "properties": {
        "order_types": {
          "type": "array",
          "items": {"enum": ["STORAGE", "RETRIEVAL", "TRANSPORT"]}
        },
        "quality_states": {
          "type": "array",
          "items": {"enum": ["OK", "NOT-OK", "PENDING", "FAILED"]}
        },
        "storage_states": {
          "type": "array",
          "items": {"enum": ["occupied", "empty", "reserved", "maintenance"]}
        }
      }
    }
  }
}
```

### **2. APS Topics Schema erstellen**
```json
// registry/schemas/aps-topics.schema.json (NEU)
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "APS Topics Schema",
  "version": "1.0.0",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "version": {"type": "string"},
        "description": {"type": "string"},
        "last_updated": {"type": "string"},
        "author": {"type": "string"}
      }
    },
    "topics": {
      "type": "object",
      "properties": {
        "vda5050": {
          "type": "object",
          "patternProperties": {
            "^(order|instant_actions|state|connection|factsheet)$": {
              "type": "object",
              "properties": {
                "pattern": {"type": "string"},
                "description": {"type": "string"},
                "qos": {"type": "integer", "minimum": 0, "maximum": 2},
                "retain": {"type": "boolean"},
                "direction": {"enum": ["pub", "sub", "pub/sub"]}
              }
            }
          }
        },
        "system_control": {
          "type": "object",
          "patternProperties": {
            "^(reset|charge|layout|flows|calibration|park)$": {
              "type": "object",
              "properties": {
                "pattern": {"type": "string"},
                "description": {"type": "string"},
                "qos": {"type": "integer", "minimum": 0, "maximum": 2},
                "retain": {"type": "boolean"},
                "direction": {"enum": ["pub", "sub", "pub/sub"]}
              }
            }
          }
        }
      }
    }
  }
}
```

## Migration Plan

### **Phase 1: Registry-Erweiterung**
1. **workpieces.yml** erweitern für VDA5050
2. **aps.yml** in topics/ erstellen
3. **Schemas** erweitern/erstellen
4. **Validierung** testen

### **Phase 2: Manager-Erweiterung**
1. **WorkpieceManager** erstellen (NFCCodeManager → WorkpieceManager)
2. **TopicManager** erweitern für APS-Topics
3. **MessageCenter** erweitern für APS-Messages
4. **Backward Compatibility** sicherstellen

### **Phase 3: Dashboard-Integration**
1. **APS-Komponenten** mit erweiterten Managern
2. **Message Center** mit APS-Tabs
3. **Topic Management** mit APS-Support
4. **Testing** und Validierung

## Vorteile der Registry-Integration

### **✅ Vollständige Kompatibilität**
- **Bestehende Struktur** bleibt unverändert
- **Versionierte Modelle** (v0, v1)
- **Schema-basierte Validierung**
- **Template-Integration**

### **✅ Erweiterte Funktionalität**
- **VDA5050 Standard** in Registry
- **APS-spezifische Topics** verwaltet
- **Workpiece Management** erweitert
- **Message Templates** für APS

### **✅ Konsistente Architektur**
- **Einheitliche Konfiguration**
- **Zentrale Verwaltung**
- **Wiederverwendbare Komponenten**
- **Einfache Wartung**

## Fazit

### **✅ Vollständig kompatibel mit Registry-Philosophie**
- **Alle Erweiterungen** folgen bestehenden Patterns
- **Schema-basierte Validierung** beibehalten
- **Versionierte Modelle** erweitert
- **Template-Integration** funktional

### **🔧 Erweiterungsbedarf minimal**
- **workpieces.yml** erweitern
- **aps.yml** erstellen
- **WorkpieceManager** erstellen
- **TopicManager** erweitern

### **📈 Vorteile**
- **Konsistente Architektur**
- **Erweiterte Funktionalität**
- **Bestehende Kompatibilität**
- **Einfache Wartung**
