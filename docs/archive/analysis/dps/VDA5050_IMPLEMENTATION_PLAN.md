# VDA5050 Implementation Plan

## Overview
Implementierungsplan für VDA5050 Standard-Integration in das OMF-Dashboard ohne bestehende Funktionalität zu beeinträchtigen.

## VDA5050 Standard Analyse

### **1. Order Management (VDA5050)**
```python
# VDA5050 Order Structure (aus FF_DPS_24V.py)
vda_order = {
    "orderId": "string",           # Eindeutige Order-ID
    "timestamp": "ISO8601",        # Zeitstempel
    "action": "STORAGE",           # Order-Typ
    "type": "RED|BLUE|WHITE",      # Werkstück-Farbe
    "workpieceId": "string",       # Werkstück-ID
    "orderUpdateId": 0             # Update-ID für Order-Updates
}
```

### **2. State Management (VDA5050)**
```python
# VDA5050 State Structure (aus FF_DPS_24V.py)
vda_state = {
    "operatingMode": "TEACHIN|AUTOMATIC",
    "headerId": 1,
    "timestamp": "ISO8601",
    "serialNumber": "controller_id",
    "orderId": "current_order_id",
    "orderUpdateId": 0,
    "paused": False,
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

### **3. Instant Actions (VDA5050)**
```python
# APS Instant Actions (aus FF_DPS_24V.py)
INSTANT_ACTIONS = {
    "reset": "reset",
    "announceOutput": "announceOutput", 
    "cancelStorageOrder": "cancelStorageOrder"
}

# System Control Commands
SYSTEM_COMMANDS = [
    "ccu/set/reset",
    "ccu/set/charge",
    "ccu/set/layout", 
    "ccu/set/flows",
    "ccu/set/calibration",
    "ccu/set/park"
]
```

## Implementierungs-Plan

### **Phase 1: VDA5050OrderManager (NEU)**

#### **1.1 Datei: `omf/tools/aps_vda5050_manager.py`**
```python
"""
VDA5050 Order Manager für APS-Integration
Implementiert VDA5050 Standard für Order-Management
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from omf.dashboard.tools.logging_config import get_logger

class VDA5050OrderManager:
    """VDA5050-konformer Order Manager für APS-Integration"""
    
    def __init__(self):
        self.logger = get_logger("omf.tools.aps_vda5050_manager")
        self.active_orders = {}  # orderId -> order_info
        self.order_history = []  # Abgeschlossene Orders
        
    def create_storage_order(self, color: str, workpiece_id: str = None) -> Dict[str, Any]:
        """Erstellt VDA5050-konforme Storage Order"""
        order_id = str(uuid.uuid4())
        workpiece_id = workpiece_id or f"WP_{color}_{int(datetime.now().timestamp())}"
        
        vda_order = {
            "orderId": order_id,
            "timestamp": datetime.now().isoformat(),
            "action": "STORAGE",
            "type": color.upper(),
            "workpieceId": workpiece_id,
            "orderUpdateId": 0
        }
        
        self.logger.info(f"📋 VDA5050 Order erstellt: {color} Werkstück {workpiece_id}")
        return vda_order
    
    def process_order_response(self, response: Dict[str, Any]) -> bool:
        """Verarbeitet VDA5050 Order Response"""
        try:
            order_id = response.get("orderId")
            if not order_id:
                return False
                
            # Order-Status aktualisieren
            if order_id in self.active_orders:
                self.active_orders[order_id].update(response)
                self.logger.info(f"📋 Order {order_id} Response verarbeitet")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Order Response Verarbeitung fehlgeschlagen: {e}")
            return False
    
    def send_instant_action(self, action_type: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sendet VDA5050 Instant Action"""
        if parameters is None:
            parameters = {}
            
        instant_action = {
            "actionType": action_type,
            "timestamp": datetime.now().isoformat(),
            "parameters": parameters
        }
        
        self.logger.info(f"⚡ Instant Action gesendet: {action_type}")
        return instant_action
    
    def get_active_orders(self) -> Dict[str, Dict[str, Any]]:
        """Gibt aktive Orders zurück"""
        return self.active_orders.copy()
    
    def get_order_history(self) -> List[Dict[str, Any]]:
        """Gibt Order-Historie zurück"""
        return self.order_history.copy()
```

#### **1.2 Integration in bestehende OrderManager**
```python
# Erweiterung der bestehenden OrderManager-Klasse
class OrderManager:
    def __init__(self):
        # Bestehende Struktur beibehalten
        self.inventory = {
            "A1": None, "A2": None, "A3": None,
            "B1": None, "B2": None, "B3": None, 
            "C1": None, "C2": None, "C3": None
        }
        self.workpiece_types = ["RED", "BLUE", "WHITE"]
        self.orders = []
        
        # NEU: VDA5050 Integration
        self.vda5050_manager = VDA5050OrderManager()
    
    def create_aps_order(self, color: str, workpiece_id: str = None) -> Dict[str, Any]:
        """Erstellt APS-Order über VDA5050"""
        return self.vda5050_manager.create_storage_order(color, workpiece_id)
    
    def send_aps_instant_action(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sendet APS Instant Action über VDA5050"""
        return self.vda5050_manager.send_instant_action(action, params)
```

### **Phase 2: APSTXTControllerManager (NEU)**

#### **2.1 Datei: `omf/tools/aps_txt_controller_manager.py`**
```python
"""
APS TXT Controller Manager
Verwaltet TXT Controller und deren Funktionen
"""

from typing import Any, Dict, List, Optional
from omf.dashboard.tools.logging_config import get_logger

class APSTXTControllerManager:
    """Verwaltet APS TXT Controller"""
    
    def __init__(self):
        self.logger = get_logger("omf.tools.aps_txt_controller_manager")
        
        # TXT Controller Konfiguration
        self.txt_controllers = {
            "DPS": {
                "ip": "192.168.0.102",
                "role": "CCU",
                "functions": ["warehouse", "nfc", "camera", "order_management"],
                "mqtt_namespace": "module/v1/ff/NodeRed/{controller_id}/"
            },
            "AIQS": {
                "ip": "192.168.0.103", 
                "role": "quality_control",
                "functions": ["ai_recognition", "camera", "quality_check"],
                "mqtt_namespace": "module/v1/ff/NodeRed/{controller_id}/"
            },
            "CGW": {
                "ip": "192.168.0.104",
                "role": "cloud_gateway", 
                "functions": ["external_communication", "cloud_sync"],
                "mqtt_namespace": "module/v1/ff/NodeRed/{controller_id}/"
            },
            "FTS": {
                "ip": "192.168.0.105",
                "role": "transport",
                "functions": ["line_following", "charging", "navigation"],
                "mqtt_namespace": "module/v1/ff/NodeRed/{controller_id}/"
            }
        }
        
        # Physical Modules
        self.physical_modules = {
            "HBW": {
                "serial": "SVR4H76449",
                "type": "warehouse",
                "functions": ["storage", "retrieval"],
                "txt_controller": "DPS"
            },
            "MILL": {
                "serial": "SVR3QA0022", 
                "type": "milling",
                "functions": ["machining"],
                "txt_controller": None
            },
            "DRILL": {
                "serial": "SVR3QA2098",
                "type": "drilling", 
                "functions": ["machining"],
                "txt_controller": None
            },
            "CHRG": {
                "serial": "CHRG0",
                "type": "charging",
                "functions": ["passive_charging"],
                "txt_controller": "FTS"
            }
        }
    
    def get_controllers(self) -> Dict[str, Dict[str, Any]]:
        """Gibt alle TXT Controller zurück"""
        return self.txt_controllers.copy()
    
    def get_controller_by_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """Gibt TXT Controller nach IP zurück"""
        for controller_id, controller in self.txt_controllers.items():
            if controller["ip"] == ip:
                return controller
        return None
    
    def get_controller_functions(self, controller_id: str) -> List[str]:
        """Gibt Funktionen eines TXT Controllers zurück"""
        controller = self.txt_controllers.get(controller_id)
        return controller["functions"] if controller else []
    
    def get_physical_modules(self) -> Dict[str, Dict[str, Any]]:
        """Gibt alle Physical Modules zurück"""
        return self.physical_modules.copy()
    
    def get_module_by_serial(self, serial: str) -> Optional[Dict[str, Any]]:
        """Gibt Physical Module nach Serial zurück"""
        for module_id, module in self.physical_modules.items():
            if module["serial"] == serial:
                return module
        return None
```

### **Phase 3: APSSystemControlManager (NEU)**

#### **3.1 Datei: `omf/tools/aps_system_control_manager.py`**
```python
"""
APS System Control Manager
Verwaltet System Control Commands für APS
"""

from typing import Any, Dict, List, Optional
from omf.dashboard.tools.logging_config import get_logger

class APSSystemControlManager:
    """Verwaltet APS System Control Commands"""
    
    def __init__(self):
        self.logger = get_logger("omf.tools.aps_system_control_manager")
        
        # System Control Commands
        self.system_commands = {
            "reset": {
                "topic": "ccu/set/reset",
                "description": "Factory Reset",
                "parameters": {}
            },
            "charge": {
                "topic": "ccu/set/charge", 
                "description": "FTS Charge",
                "parameters": {"charge": True}
            },
            "layout": {
                "topic": "ccu/set/layout",
                "description": "Layout Management", 
                "parameters": {}
            },
            "flows": {
                "topic": "ccu/set/flows",
                "description": "Flow Control",
                "parameters": {}
            },
            "calibration": {
                "topic": "ccu/set/calibration",
                "description": "System Calibration",
                "parameters": {}
            },
            "park": {
                "topic": "ccu/set/park",
                "description": "Park Factory",
                "parameters": {}
            }
        }
    
    def send_system_command(self, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sendet System Control Command"""
        if command not in self.system_commands:
            self.logger.error(f"❌ Unbekanntes System Command: {command}")
            return {}
        
        cmd_info = self.system_commands[command]
        if parameters is None:
            parameters = cmd_info["parameters"]
        
        command_data = {
            "command": command,
            "topic": cmd_info["topic"],
            "parameters": parameters,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"🎮 System Command gesendet: {command}")
        return command_data
    
    def get_available_commands(self) -> List[str]:
        """Gibt verfügbare System Commands zurück"""
        return list(self.system_commands.keys())
    
    def get_command_info(self, command: str) -> Optional[Dict[str, Any]]:
        """Gibt Command-Informationen zurück"""
        return self.system_commands.get(command)
    
    def reset_factory(self) -> Dict[str, Any]:
        """Factory Reset Command"""
        return self.send_system_command("reset")
    
    def charge_fts(self) -> Dict[str, Any]:
        """FTS Charge Command"""
        return self.send_system_command("charge")
```

## Integration in bestehende Systeme

### **1. MQTT-Integration erweitern**
```python
# Erweiterung der bestehenden MQTT-Client-Funktionalität
class OmfMqttClient:
    def __init__(self):
        # Bestehende Initialisierung beibehalten
        # ...
        
        # NEU: APS-Integration
        self.aps_vda5050_manager = VDA5050OrderManager()
        self.aps_txt_controller_manager = APSTXTControllerManager()
        self.aps_system_control_manager = APSSystemControlManager()
    
    def setup_aps_subscriptions(self):
        """APS-spezifische MQTT-Subscriptions"""
        aps_topics = [
            "module/v1/ff/NodeRed/+/order",
            "module/v1/ff/NodeRed/+/instantActions", 
            "module/v1/ff/NodeRed/+/state",
            "ccu/set/+"
        ]
        
        for topic in aps_topics:
            self.subscribe(topic, qos=2)
    
    def send_aps_order(self, color: str, workpiece_id: str = None):
        """Sendet APS-Order über MQTT"""
        order = self.aps_vda5050_manager.create_storage_order(color, workpiece_id)
        topic = f"module/v1/ff/NodeRed/{self.get_controller_id()}/order"
        self.publish(topic, json.dumps(order), qos=2)
    
    def send_aps_system_command(self, command: str, parameters: Dict[str, Any] = None):
        """Sendet APS System Command über MQTT"""
        cmd_data = self.aps_system_control_manager.send_system_command(command, parameters)
        self.publish(cmd_data["topic"], json.dumps(cmd_data["parameters"]), qos=2)
```

### **2. Dashboard-Integration erweitern**
```python
# Neue APS-Komponenten (ohne bestehende zu ändern)
def show_aps_overview():
    """APS-Übersicht Komponente"""
    st.header("🏭 APS-Übersicht")
    
    # VDA5050 Manager verwenden
    vda_manager = VDA5050OrderManager()
    txt_manager = APSTXTControllerManager()
    
    # TXT Controller Status
    controllers = txt_manager.get_controllers()
    for controller_id, controller in controllers.items():
        st.metric(f"TXT {controller_id}", f"{controller['ip']} - {controller['role']}")
    
    # Active Orders
    active_orders = vda_manager.get_active_orders()
    st.metric("Aktive Orders", len(active_orders))

def show_aps_steering():
    """APS-Steuerung Komponente"""
    st.header("🎮 APS-Steuerung")
    
    system_control = APSSystemControlManager()
    
    # System Commands
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏭 Factory Reset"):
            system_control.reset_factory()
            st.success("Factory Reset gesendet")
    
    with col2:
        if st.button("🔋 FTS Charge"):
            system_control.charge_fts()
            st.success("FTS Charge gesendet")
    
    with col3:
        if st.button("🅿️ Park Factory"):
            system_control.send_system_command("park")
            st.success("Park Factory gesendet")
    
    # Order Commands
    st.subheader("📋 Bestellungen")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔴 Bestellung RED"):
            # Order über MQTT senden
            st.success("Bestellung RED gesendet")
    
    with col2:
        if st.button("🔵 Bestellung BLUE"):
            # Order über MQTT senden
            st.success("Bestellung BLUE gesendet")
    
    with col3:
        if st.button("⚪ Bestellung WHITE"):
            # Order über MQTT senden
            st.success("Bestellung WHITE gesendet")
```

## Nächste Schritte

### **1. Implementierung (nach Live-Demo)**
1. **VDA5050OrderManager** erstellen
2. **APSTXTControllerManager** erstellen  
3. **APSSystemControlManager** erstellen
4. **MQTT-Integration** erweitern
5. **Dashboard-Komponenten** erstellen

### **2. Testing**
1. **Unit Tests** für neue Manager
2. **Integration Tests** mit MQTT
3. **Dashboard Tests** mit APS-Simulation
4. **Live Tests** mit realer APS

### **3. Dokumentation**
1. **API-Dokumentation** für neue Manager
2. **Integration Guide** für APS
3. **User Guide** für APS-Dashboard
4. **Troubleshooting Guide**

## Sicherheitshinweise

### **✅ Bestehende Funktionalität bleibt unberührt**
- **Keine Änderungen** an bestehenden Dateien
- **Neue Manager** als separate Module
- **Optionale Integration** über Konfiguration
- **Rollback möglich** bei Problemen

### **🛡️ Live-Demo Sicherheit**
- **Keine automatischen Reloads**
- **Keine Import-Änderungen**
- **Keine Tab-Struktur-Änderungen**
- **Bestehende MQTT-Integration unverändert**
