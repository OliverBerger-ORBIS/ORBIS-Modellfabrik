#!/usr/bin/env python3
"""
APS MQTT Integration
Erweitert OmfMqttClient für APS-spezifische Funktionalität
Version: 1.0.0
"""

import json
from typing import Any, Callable, Dict, List, Optional

from omf.tools.logging_config import get_logger
from omf.tools.omf_mqtt_client import OmfMqttClient
from omf.tools.aps_vda5050_manager import VDA5050OrderManager
from omf.tools.aps_txt_controller_manager import APSTXTControllerManager
from omf.tools.aps_system_control_manager import APSSystemControlManager


class APSMqttIntegration:
    """APS-spezifische MQTT-Integration"""
    
    def __init__(self, mqtt_client: OmfMqttClient):
        self.logger = get_logger("omf.tools.aps_mqtt_integration")
        self.mqtt_client = mqtt_client
        
        # APS Manager
        self.vda5050_manager = VDA5050OrderManager()
        self.txt_controller_manager = APSTXTControllerManager()
        self.system_control_manager = APSSystemControlManager()
        
        # APS-spezifische Topics
        self.aps_topics = self._setup_aps_topics()
        
        # Message Handlers
        self._setup_message_handlers()
        
        self.logger.info("APSMqttIntegration initialisiert")
    
    def _setup_aps_topics(self) -> Dict[str, List[str]]:
        """Setup APS-spezifische Topics"""
        return {
            "factsheet_topics": [
                "module/v1/ff/+/factsheet",
                "module/v1/ff/NodeRed/+/factsheet"
            ],
            "state_topics": [
                "module/v1/ff/+/state",
                "module/v1/ff/NodeRed/+/state"
            ],
            "order_topics": [
                "module/v1/ff/+/order",
                "module/v1/ff/NodeRed/+/order"
            ],
            "instant_action_topics": [
                "module/v1/ff/+/instantAction",
                "module/v1/ff/NodeRed/+/instantAction"
            ],
            "system_control_topics": [
                "ccu/set/+"
            ],
            "fts_topics": [
                "fts/v1/ff/+/state",
                "fts/v1/ff/+/order",
                "fts/v1/ff/+/instantAction"
            ]
        }
    
    def _setup_message_handlers(self):
        """Setup Message Handlers für APS-Topics"""
        # Alle APS-Topics sammeln
        all_topics = []
        all_topics.extend(self.aps_topics["factsheet_topics"])
        all_topics.extend(self.aps_topics["state_topics"])
        all_topics.extend(self.aps_topics["order_topics"])
        all_topics.extend(self.aps_topics["instant_action_topics"])
        all_topics.extend(self.aps_topics["fts_topics"])
        
        # Alle Topics auf einmal subscriben (per-Topic-Buffer-Pattern)
        self.mqtt_client.subscribe_many(all_topics, qos=2)
    
    def process_messages(self):
        """Public method to process messages from per-Topic-Buffers"""
        self._process_messages()
    
    def _process_messages(self):
        """Process Messages aus per-Topic-Buffers (OMF-Pattern)"""
        # Factsheet Messages verarbeiten
        for topic_filter in self.aps_topics["factsheet_topics"]:
            messages = self.mqtt_client.get_buffer(topic_filter)
            for msg in messages:
                self._handle_factsheet_message(msg["topic"], msg["payload"])
        
        # State Messages verarbeiten
        for topic_filter in self.aps_topics["state_topics"]:
            messages = self.mqtt_client.get_buffer(topic_filter)
            for msg in messages:
                self._handle_state_message(msg["topic"], msg["payload"])
        
        # Order Messages verarbeiten
        for topic_filter in self.aps_topics["order_topics"]:
            messages = self.mqtt_client.get_buffer(topic_filter)
            for msg in messages:
                self._handle_order_message(msg["topic"], msg["payload"])
        
        # Instant Action Messages verarbeiten
        for topic_filter in self.aps_topics["instant_action_topics"]:
            messages = self.mqtt_client.get_buffer(topic_filter)
            for msg in messages:
                self._handle_instant_action_message(msg["topic"], msg["payload"])
        
        # FTS Messages verarbeiten
        for topic_filter in self.aps_topics["fts_topics"]:
            messages = self.mqtt_client.get_buffer(topic_filter)
            for msg in messages:
                self._handle_fts_message(msg["topic"], msg["payload"])
    
    def _handle_factsheet_message(self, topic: str, payload):
        """Handler für Factsheet Messages"""
        try:
            payload_str = payload if isinstance(payload, str) else payload.decode('utf-8')
            self.txt_controller_manager.process_factsheet_message(topic, payload_str)
        except Exception:
            pass  # Kein Logging in Callbacks (OMF-Regel)
    
    def _handle_state_message(self, topic: str, payload):
        """Handler für State Messages"""
        try:
            payload_str = payload if isinstance(payload, str) else payload.decode('utf-8')
            state_data = json.loads(payload_str)
            
            # TXT Controller IP-Update
            self.txt_controller_manager.process_state_message(topic, payload_str)
            
            # VDA5050 State Processing
            self.vda5050_manager.process_state_message(state_data)
            
        except Exception:
            pass  # Kein Logging in Callbacks (OMF-Regel)
    
    def _handle_order_message(self, topic: str, payload):
        """Handler für Order Messages"""
        try:
            payload_str = payload if isinstance(payload, str) else payload.decode('utf-8')
            order_data = json.loads(payload_str)
            
            # VDA5050 Order Processing
            self.vda5050_manager.process_order_response(order_data)
            
        except Exception:
            pass  # Kein Logging in Callbacks (OMF-Regel)
    
    def _handle_instant_action_message(self, topic: str, payload):
        """Handler für Instant Action Messages"""
        try:
            payload_str = payload if isinstance(payload, str) else payload.decode('utf-8')
            action_data = json.loads(payload_str)
            # Instant Action Processing (ohne Logging in Callback)
            pass
        except Exception:
            pass  # Kein Logging in Callbacks (OMF-Regel)
    
    def _handle_fts_message(self, topic: str, payload):
        """Handler für FTS Messages"""
        try:
            payload_str = payload if isinstance(payload, str) else payload.decode('utf-8')
            fts_data = json.loads(payload_str)
            # FTS Message Processing (ohne Logging in Callback)
            pass
        except Exception:
            pass  # Kein Logging in Callbacks (OMF-Regel)
    
    # VDA5050 Order Management
    def create_storage_order(self, color: str, workpiece_id: str = None, target_module: str = None) -> Dict[str, Any]:
        """Erstellt VDA5050 Storage Order"""
        return self.vda5050_manager.create_storage_order(color, workpiece_id, target_module)
    
    def create_retrieval_order(self, color: str, workpiece_id: str = None, source_module: str = None) -> Dict[str, Any]:
        """Erstellt VDA5050 Retrieval Order"""
        return self.vda5050_manager.create_retrieval_order(color, workpiece_id, source_module)
    
    def send_instant_action(self, action_type: str, parameters: Dict[str, Any] = None, target_module: str = None) -> Dict[str, Any]:
        """Sendet VDA5050 Instant Action"""
        return self.vda5050_manager.send_instant_action(action_type, parameters, target_module)
    
    def get_active_orders(self) -> Dict[str, Dict[str, Any]]:
        """Gibt aktive Orders zurück"""
        return self.vda5050_manager.get_active_orders()
    
    def get_order_history(self) -> List[Dict[str, Any]]:
        """Gibt Order-Historie zurück"""
        return self.vda5050_manager.get_order_history()
    
    # TXT Controller Management
    def get_discovered_controllers(self) -> Dict[str, Dict[str, Any]]:
        """Gibt entdeckte Controller zurück"""
        return self.txt_controller_manager.get_discovered_controllers()
    
    def get_controller_by_serial(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Gibt Controller nach Serial Number zurück"""
        return self.txt_controller_manager.get_controller_by_serial(serial_number)
    
    def get_controller_by_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Gibt Controller nach IP-Adresse zurück"""
        return self.txt_controller_manager.get_controller_by_ip(ip_address)
    
    def get_online_controllers(self) -> Dict[str, Dict[str, Any]]:
        """Gibt online Controller zurück"""
        return self.txt_controller_manager.get_online_controllers()
    
    # System Control
    def send_system_command(self, command: str, parameters: Dict[str, Any] = None) -> bool:
        """Sendet System Control Command"""
        try:
            cmd_data = self.system_control_manager.send_system_command(command, parameters)
            if cmd_data:
                # Command über MQTT senden
                topic = cmd_data["topic"]
                payload = json.dumps(cmd_data["parameters"])
                qos = cmd_data["qos"]
                retain = cmd_data["retain"]
                
                success = self.mqtt_client.publish(topic, payload, qos=qos, retain=retain)
                if success:
                    self.logger.info(f"🎮 System Command gesendet: {command}")
                else:
                    self.logger.error(f"❌ System Command fehlgeschlagen: {command}")
                
                return success
            return False
            
        except Exception as e:
            self.logger.error(f"❌ System Command Sendung fehlgeschlagen: {e}")
            return False
    
    def reset_factory(self) -> bool:
        """Factory Reset Command"""
        return self.send_system_command("reset")
    
    def charge_fts(self) -> bool:
        """FTS Charge Command"""
        return self.send_system_command("charge")
    
    def park_factory(self) -> bool:
        """Park Factory Command"""
        return self.send_system_command("park")
    
    def calibrate_system(self) -> bool:
        """System Calibration Command"""
        return self.send_system_command("calibration")
    
    # VDA5050 Order Publishing
    def publish_order(self, order: Dict[str, Any], target_module: str = None) -> bool:
        """Publiziert VDA5050 Order"""
        try:
            if target_module:
                # Spezifisches Modul
                topic = f"module/v1/ff/{target_module}/order"
            else:
                # DPS als Standard (CCU)
                topic = "module/v1/ff/SVR4H73275/order"
            
            payload = json.dumps(order)
            success = self.mqtt_client.publish(topic, payload, qos=2, retain=False)
            
            if success:
                self.logger.info(f"📋 VDA5050 Order publiziert: {order.get('orderId', 'UNKNOWN')}")
            else:
                self.logger.error(f"❌ Order Publikation fehlgeschlagen: {order.get('orderId', 'UNKNOWN')}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Order Publikation fehlgeschlagen: {e}")
            return False
    
    def publish_instant_action(self, action: Dict[str, Any], target_module: str = None) -> bool:
        """Publiziert VDA5050 Instant Action"""
        try:
            if target_module:
                # Spezifisches Modul
                topic = f"module/v1/ff/{target_module}/instantAction"
            else:
                # DPS als Standard (CCU)
                topic = "module/v1/ff/SVR4H73275/instantAction"
            
            payload = json.dumps(action)
            success = self.mqtt_client.publish(topic, payload, qos=2, retain=False)
            
            if success:
                self.logger.info(f"⚡ Instant Action publiziert: {action.get('actionType', 'UNKNOWN')}")
            else:
                self.logger.error(f"❌ Instant Action Publikation fehlgeschlagen: {action.get('actionType', 'UNKNOWN')}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Instant Action Publikation fehlgeschlagen: {e}")
            return False
    
    # Status und Monitoring
    def get_aps_status(self) -> Dict[str, Any]:
        """Gibt APS-System-Status zurück"""
        return {
            "controllers": self.txt_controller_manager.get_controller_status_summary(),
            "orders": self.vda5050_manager.get_order_statistics(),
            "system_commands": self.system_control_manager.get_command_statistics(),
            "mqtt_connected": self.mqtt_client.connected,
            "subscribed_topics": len(self.mqtt_client._subscribed)
        }
    
    def get_aps_topics(self) -> Dict[str, List[str]]:
        """Gibt alle APS-Topics zurück"""
        return self.aps_topics.copy()
    
    def get_expected_topics(self) -> List[str]:
        """Gibt erwartete Topics für Discovery zurück"""
        return self.txt_controller_manager.get_expected_topics()
    
    # Utility Functions
    def is_controller_online(self, serial_number: str) -> bool:
        """Prüft ob Controller online ist"""
        return self.txt_controller_manager.is_controller_online(serial_number)
    
    def get_controller_ip(self, serial_number: str) -> Optional[str]:
        """Gibt Controller IP zurück"""
        return self.txt_controller_manager.get_controller_ip(serial_number)
    
    def get_orders_by_color(self, color: str) -> List[Dict[str, Any]]:
        """Gibt Orders nach Farbe zurück"""
        return self.vda5050_manager.get_orders_by_color(color)
    
    def get_orders_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Gibt Orders nach Status zurück"""
        return self.vda5050_manager.get_orders_by_status(status)
    
    def complete_order(self, order_id: str, result: Dict[str, Any] = None) -> bool:
        """Schließt Order ab"""
        return self.vda5050_manager.complete_order(order_id, result)
    
    def cancel_order(self, order_id: str, reason: str = None) -> bool:
        """Bricht Order ab"""
        return self.vda5050_manager.cancel_order(order_id, reason)
