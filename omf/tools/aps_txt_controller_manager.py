#!/usr/bin/env python3
"""
APS TXT Controller Manager mit dynamischer IP-Erkennung
Verwendet Factsheet + Module State Messages für Controller Discovery
Version: 1.0.0
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from omf.tools.logging_config import get_logger
from omf.tools.registry_manager import get_registry


class APSTXTControllerManager:
    """TXT Controller Management mit dynamischer IP-Erkennung"""
    
    def __init__(self):
        self.logger = get_logger("omf.tools.aps_txt_controller_manager")
        self.registry = get_registry()
        
        # Dynamische Controller-Erkennung
        self.discovered_controllers = {}  # serial -> controller_info
        self.controller_ip_mapping = {}   # serial -> current_ip
        self.last_discovery_update = 0
        
        # Registry-basierte Konfiguration
        self.load_controller_config()
        
        self.logger.info("APSTXTControllerManager initialisiert")
    
    def load_controller_config(self):
        """Lädt Controller-Konfiguration aus Registry"""
        try:
            # Bestehende Konfiguration aus Registry
            controller_config = self.registry.workpieces().get("txt_controllers", {})
            
            # Fallback-Konfiguration basierend auf Registry-Templates
            self.default_controllers = {
                "SVR4H73275": {  # DPS
                    "role": "CCU",
                    "functions": ["warehouse", "nfc", "camera", "order_management"],
                    "module_type": "DPS",
                    "expected_topics": [
                        "module/v1/ff/SVR4H73275/factsheet",
                        "module/v1/ff/SVR4H73275/state",
                        "module/v1/ff/NodeRed/SVR4H73275/factsheet",
                        "module/v1/ff/NodeRed/SVR4H73275/state"
                    ]
                },
                "SVR4H76530": {  # AIQS
                    "role": "quality_control",
                    "functions": ["ai_recognition", "camera", "quality_check"],
                    "module_type": "AIQS",
                    "expected_topics": [
                        "module/v1/ff/SVR4H76530/factsheet",
                        "module/v1/ff/SVR4H76530/state",
                        "module/v1/ff/NodeRed/SVR4H76530/factsheet",
                        "module/v1/ff/NodeRed/SVR4H76530/state"
                    ]
                },
                "SVR4H76449": {  # HBW
                    "role": "warehouse",
                    "functions": ["storage", "retrieval"],
                    "module_type": "HBW",
                    "expected_topics": [
                        "module/v1/ff/SVR4H76449/factsheet",
                        "module/v1/ff/SVR4H76449/state"
                    ]
                },
                "SVR3QA0022": {  # MILL
                    "role": "machining",
                    "functions": ["milling"],
                    "module_type": "MILL",
                    "expected_topics": [
                        "module/v1/ff/SVR3QA0022/factsheet",
                        "module/v1/ff/SVR3QA0022/state"
                    ]
                },
                "SVR3QA2098": {  # DRILL
                    "role": "machining",
                    "functions": ["drilling"],
                    "module_type": "DRILL",
                    "expected_topics": [
                        "module/v1/ff/SVR3QA2098/factsheet",
                        "module/v1/ff/SVR3QA2098/state"
                    ]
                }
            }
            
        except Exception as e:
            self.logger.warning(f"Registry-Konfiguration nicht verfügbar: {e}")
            self.default_controllers = {}
    
    def process_factsheet_message(self, topic: str, payload: str) -> bool:
        """Verarbeitet Factsheet Message und erkennt Controller"""
        try:
            # Topic parsen: module/v1/ff/{serial}/factsheet
            topic_parts = topic.split('/')
            if len(topic_parts) < 5 or topic_parts[-1] != 'factsheet':
                return False
            
            serial_number = topic_parts[3]
            factsheet_data = json.loads(payload)
            
            # Controller-Info aus Factsheet extrahieren
            controller_info = {
                "serial_number": serial_number,
                "module_type": factsheet_data.get("moduleType", "UNKNOWN"),
                "version": factsheet_data.get("version", "UNKNOWN"),
                "capabilities": factsheet_data.get("capabilities", []),
                "functions": factsheet_data.get("functions", []),
                "role": self._determine_role(serial_number, factsheet_data),
                "factsheet_topic": topic,
                "discovered_at": time.time(),
                "last_seen": time.time()
            }
            
            # Controller registrieren
            self.discovered_controllers[serial_number] = controller_info
            
            self.logger.info(f"🔍 TXT Controller entdeckt: {serial_number} ({controller_info['module_type']})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Factsheet-Verarbeitung fehlgeschlagen: {e}")
            return False
    
    def process_state_message(self, topic: str, payload: str) -> bool:
        """Verarbeitet Module State Message und aktualisiert IP-Adresse"""
        try:
            # Topic parsen: module/v1/ff/{serial}/state
            topic_parts = topic.split('/')
            if len(topic_parts) < 5 or topic_parts[-1] != 'state':
                return False
            
            serial_number = topic_parts[3]
            state_data = json.loads(payload)
            
            # IP-Adresse aus State extrahieren
            ip_address = self._extract_ip_from_state(state_data)
            
            if ip_address and serial_number in self.discovered_controllers:
                # IP-Adresse aktualisieren
                self.controller_ip_mapping[serial_number] = ip_address
                self.discovered_controllers[serial_number]["last_seen"] = time.time()
                self.discovered_controllers[serial_number]["ip_address"] = ip_address
                
                self.logger.debug(f"📍 IP aktualisiert: {serial_number} -> {ip_address}")
                return True
            
        except Exception as e:
            self.logger.error(f"❌ State-Verarbeitung fehlgeschlagen: {e}")
            return False
    
    def _extract_ip_from_state(self, state_data: Dict[str, Any]) -> Optional[str]:
        """Extrahiert IP-Adresse aus State Message"""
        # Verschiedene mögliche Pfade für IP-Adresse
        ip_paths = [
            ["ipAddress"],
            ["connection", "ipAddress"],
            ["network", "ipAddress"],
            ["system", "ipAddress"],
            ["metadata", "ipAddress"]
        ]
        
        for path in ip_paths:
            current = state_data
            try:
                for key in path:
                    current = current[key]
                if isinstance(current, str) and self._is_valid_ip(current):
                    return current
            except (KeyError, TypeError):
                continue
        
        return None
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validiert IP-Adresse"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False
    
    def _determine_role(self, serial_number: str, factsheet_data: Dict[str, Any]) -> str:
        """Bestimmt Controller-Rolle basierend auf Serial Number und Factsheet"""
        # Serial Number basierte Erkennung
        if serial_number in self.default_controllers:
            return self.default_controllers[serial_number]["role"]
        
        # Factsheet basierte Erkennung
        module_type = factsheet_data.get("moduleType", "").upper()
        functions = factsheet_data.get("functions", [])
        
        if "CCU" in module_type or "warehouse" in functions:
            return "CCU"
        elif "quality" in module_type or "ai" in functions:
            return "quality_control"
        elif "transport" in module_type or "line_following" in functions:
            return "transport"
        elif "cloud" in module_type or "gateway" in functions:
            return "cloud_gateway"
        else:
            return "unknown"
    
    def get_discovered_controllers(self) -> Dict[str, Dict[str, Any]]:
        """Gibt alle entdeckten Controller zurück"""
        return self.discovered_controllers.copy()
    
    def get_controller_by_serial(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Gibt Controller nach Serial Number zurück"""
        return self.discovered_controllers.get(serial_number)
    
    def get_controller_by_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Gibt Controller nach IP-Adresse zurück"""
        for serial, controller in self.discovered_controllers.items():
            if controller.get("ip_address") == ip_address:
                return controller
        return None
    
    def get_controller_ip(self, serial_number: str) -> Optional[str]:
        """Gibt aktuelle IP-Adresse eines Controllers zurück"""
        return self.controller_ip_mapping.get(serial_number)
    
    def get_online_controllers(self) -> Dict[str, Dict[str, Any]]:
        """Gibt alle online Controller zurück"""
        current_time = time.time()
        online_controllers = {}
        
        for serial, controller in self.discovered_controllers.items():
            # Controller gilt als online wenn er in den letzten 30 Sekunden gesehen wurde
            if current_time - controller.get("last_seen", 0) < 30:
                online_controllers[serial] = controller
        
        return online_controllers
    
    def get_expected_topics(self) -> List[str]:
        """Gibt alle erwarteten Topics für Discovery zurück"""
        topics = []
        
        for serial, config in self.default_controllers.items():
            topics.extend(config.get("expected_topics", []))
        
        return topics
    
    def get_controller_status_summary(self) -> Dict[str, Any]:
        """Gibt Status-Übersicht aller Controller zurück"""
        online_controllers = self.get_online_controllers()
        
        return {
            "total_discovered": len(self.discovered_controllers),
            "total_online": len(online_controllers),
            "controllers": {
                serial: {
                    "module_type": controller.get("module_type", "UNKNOWN"),
                    "role": controller.get("role", "unknown"),
                    "ip_address": controller.get("ip_address", "UNKNOWN"),
                    "online": serial in online_controllers,
                    "last_seen": controller.get("last_seen", 0)
                }
                for serial, controller in self.discovered_controllers.items()
            }
        }
    
    def get_controllers_by_role(self, role: str) -> Dict[str, Dict[str, Any]]:
        """Gibt alle Controller einer bestimmten Rolle zurück"""
        return {
            serial: controller
            for serial, controller in self.discovered_controllers.items()
            if controller.get("role") == role
        }
    
    def get_controllers_by_module_type(self, module_type: str) -> Dict[str, Dict[str, Any]]:
        """Gibt alle Controller eines bestimmten Modul-Typs zurück"""
        return {
            serial: controller
            for serial, controller in self.discovered_controllers.items()
            if controller.get("module_type") == module_type
        }
    
    def get_controller_functions(self, serial_number: str) -> List[str]:
        """Gibt Funktionen eines Controllers zurück"""
        controller = self.discovered_controllers.get(serial_number)
        if controller:
            return controller.get("functions", [])
        return []
    
    def is_controller_online(self, serial_number: str) -> bool:
        """Prüft ob ein Controller online ist"""
        return serial_number in self.get_online_controllers()
    
    def get_controller_uptime(self, serial_number: str) -> Optional[float]:
        """Gibt Uptime eines Controllers in Sekunden zurück"""
        controller = self.discovered_controllers.get(serial_number)
        if controller and controller.get("discovered_at"):
            return time.time() - controller["discovered_at"]
        return None
    
    def clear_offline_controllers(self, offline_threshold_seconds: int = 300) -> int:
        """Entfernt Controller die länger offline sind"""
        current_time = time.time()
        removed_count = 0
        
        offline_controllers = []
        for serial, controller in self.discovered_controllers.items():
            last_seen = controller.get("last_seen", 0)
            if current_time - last_seen > offline_threshold_seconds:
                offline_controllers.append(serial)
        
        for serial in offline_controllers:
            del self.discovered_controllers[serial]
            if serial in self.controller_ip_mapping:
                del self.controller_ip_mapping[serial]
            removed_count += 1
        
        if removed_count > 0:
            self.logger.info(f"🗑️ {removed_count} offline Controller entfernt")
        
        return removed_count
