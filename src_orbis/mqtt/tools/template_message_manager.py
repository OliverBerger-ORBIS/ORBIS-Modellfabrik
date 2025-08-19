#!/usr/bin/env python3
"""
Template Message Manager für APS MQTT Control
Verwaltet Template Messages für Wareneingang und Order Tracking
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

# Optional MQTT import
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    mqtt = None
    MQTT_AVAILABLE = False


class TemplateMessageManager:
    """Verwaltet Template Messages für MQTT Control"""
    
    def __init__(self, mqtt_client=None):
        self.mqtt_client = mqtt_client
        self.templates = self._load_templates()
        self.active_orders = {}  # orderId -> order_info
        self.order_history = []  # Liste aller abgeschlossenen Orders
        
    def _load_templates(self) -> Dict[str, Dict]:
        """Lädt die Template Library"""
        return {
            "wareneingang_trigger": {
                "name": "wareneingang_trigger",
                "description": "Startet Wareneingang-Prozess",
                "topic": "ccu/order/request",
                "payload": {
                    "timestamp": "{{timestamp}}",
                    "orderType": "STORAGE",
                    "type": "{{color}}",
                    "workpieceId": "{{workpieceId}}"
                },
                "parameters": {
                    "color": ["RED", "WHITE", "BLUE"],
                    "workpieceId": "string (NFC)",
                    "timestamp": "ISO 8601"
                }
            },
            "dps_drop_template": {
                "name": "dps_drop_template",
                "description": "DPS DROP Command Template",
                "topic": "module/v1/ff/SVR4H73275/order",
                "payload": {
                    "timestamp": "{{timestamp}}",
                    "serialNumber": "SVR4H73275",
                    "orderId": "{{orderId}}",
                    "orderUpdateId": 1,
                    "action": {
                        "id": "{{actionId}}",
                        "command": "DROP",
                        "metadata": {
                            "workpiece": {
                                "workpieceId": "{{workpieceId}}",
                                "type": "{{color}}",
                                "history": [],
                                "state": "PROCESSED"
                            }
                        }
                    }
                },
                "parameters": {
                    "timestamp": "ISO 8601",
                    "orderId": "UUID v4",
                    "actionId": "UUID v4",
                    "workpieceId": "string (NFC)",
                    "color": ["RED", "WHITE", "BLUE"]
                }
            },
            "hbw_pick_template": {
                "name": "hbw_pick_template",
                "description": "HBW PICK Command Template",
                "topic": "module/v1/ff/SVR3QA0022/order",
                "payload": {
                    "timestamp": "{{timestamp}}",
                    "serialNumber": "SVR3QA0022",
                    "orderId": "{{orderId}}",
                    "orderUpdateId": 3,
                    "action": {
                        "id": "{{actionId}}",
                        "command": "PICK",
                        "metadata": {
                            "type": "{{color}}",
                            "workpieceId": "{{workpieceId}}"
                        }
                    }
                },
                "parameters": {
                    "timestamp": "ISO 8601",
                    "orderId": "UUID v4",
                    "actionId": "UUID v4",
                    "color": ["RED", "WHITE", "BLUE"],
                    "workpieceId": "string (NFC)"
                }
            }
        }
    
    def set_mqtt_client(self, mqtt_client):
        """Setzt den MQTT Client"""
        self.mqtt_client = mqtt_client
    
    def send_wareneingang_trigger(self, color: str, workpiece_id: str) -> bool:
        """Sendet Wareneingang-Trigger an CCU"""
        try:
            template = self.templates["wareneingang_trigger"]
            
            # Parameter validieren
            if color not in template["parameters"]["color"]:
                raise ValueError(f"Ungültige Farbe: {color}. Erlaubt: {template['parameters']['color']}")
            
            if not workpiece_id or len(workpiece_id) < 10:
                raise ValueError(f"Ungültige Werkstück-ID: {workpiece_id}")
            
            # Payload erstellen
            payload = template["payload"].copy()
            payload["timestamp"] = datetime.now().isoformat()
            payload["type"] = color
            payload["workpieceId"] = workpiece_id
            
            # MQTT senden
            if self.mqtt_client:
                self.mqtt_client.publish(template["topic"], json.dumps(payload))
                print(f"✅ Wareneingang-Trigger gesendet: {color} Werkstück {workpiece_id}")
                
                # Tracking starten
                self._start_order_tracking(workpiece_id, color)
                return True
            else:
                print("❌ MQTT Client nicht verfügbar")
                return False
                
        except Exception as e:
            print(f"❌ Fehler beim Senden des Wareneingang-Triggers: {e}")
            return False
    
    def _start_order_tracking(self, workpiece_id: str, color: str):
        """Startet das Tracking für eine neue Order"""
        tracking_info = {
            "workpieceId": workpiece_id,
            "color": color,
            "startTime": datetime.now(),
            "status": "WAITING_FOR_ORDER_ID",
            "orderId": None,
            "messages": []
        }
        
        # Temporär speichern bis ORDER-ID empfangen wird
        self.active_orders[f"pending_{workpiece_id}"] = tracking_info
        print(f"📊 Order Tracking gestartet für {color} Werkstück {workpiece_id}")
    
    def handle_ccu_response(self, order_id: str, color: str, workpiece_id: str, 
                          response_data: Dict[str, Any]) -> bool:
        """Behandelt CCU Response und speichert ORDER-ID"""
        try:
            # Pending Order finden und aktualisieren
            pending_key = f"pending_{workpiece_id}"
            if pending_key in self.active_orders:
                order_info = self.active_orders[pending_key]
                order_info["orderId"] = order_id
                order_info["status"] = "ACTIVE"
                order_info["ccuResponse"] = response_data
                
                # Umbenennen zu ORDER-ID
                self.active_orders[order_id] = order_info
                del self.active_orders[pending_key]
                
                print(f"✅ ORDER-ID empfangen: {order_id} für {color} Werkstück {workpiece_id}")
                return True
            else:
                print(f"⚠️ Keine pending Order gefunden für Werkstück {workpiece_id}")
                return False
                
        except Exception as e:
            print(f"❌ Fehler beim Verarbeiten der CCU Response: {e}")
            return False
    
    def track_order_progress(self, order_id: str, message_data: Dict[str, Any]) -> bool:
        """Verfolgt Fortschritt einer ORDER-ID"""
        try:
            if order_id in self.active_orders:
                order_info = self.active_orders[order_id]
                order_info["messages"].append({
                    "timestamp": datetime.now(),
                    "data": message_data
                })
                
                # Status aktualisieren basierend auf Message
                if "state" in message_data:
                    state = message_data["state"]
                    if "FINISHED" in state:
                        order_info["status"] = "COMPLETED"
                        order_info["endTime"] = datetime.now()
                        
                        # Zur Historie verschieben
                        self.order_history.append(order_info)
                        del self.active_orders[order_id]
                        
                        print(f"✅ Order {order_id} abgeschlossen")
                    elif "ERROR" in state:
                        order_info["status"] = "ERROR"
                        order_info["errorTime"] = datetime.now()
                        
                        print(f"❌ Order {order_id} fehlgeschlagen")
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Fehler beim Tracking der Order {order_id}: {e}")
            return False
    
    def get_active_orders(self) -> Dict[str, Dict]:
        """Gibt alle aktiven Orders zurück"""
        return self.active_orders.copy()
    
    def get_order_history(self) -> List[Dict]:
        """Gibt die Order-Historie zurück"""
        return self.order_history.copy()
    
    def get_order_info(self, order_id: str) -> Optional[Dict]:
        """Gibt Informationen zu einer spezifischen Order zurück"""
        if order_id in self.active_orders:
            return self.active_orders[order_id]
        else:
            # In Historie suchen
            for order in self.order_history:
                if order.get("orderId") == order_id:
                    return order
        return None
    
    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """Gibt Informationen zu einem Template zurück"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """Gibt alle verfügbaren Templates zurück"""
        return list(self.templates.keys())
    
    def validate_parameters(self, template_name: str, parameters: Dict[str, Any]) -> bool:
        """Validiert Parameter für ein Template"""
        try:
            template = self.templates.get(template_name)
            if not template:
                return False
            
            template_params = template.get("parameters", {})
            
            for param_name, param_value in parameters.items():
                if param_name in template_params:
                    expected_type = template_params[param_name]
                    
                    # Einfache Validierung
                    if isinstance(expected_type, list):
                        if param_value not in expected_type:
                            return False
                    elif expected_type == "string (NFC)":
                        if not isinstance(param_value, str) or len(param_value) < 10:
                            return False
                    elif expected_type == "ISO 8601":
                        try:
                            datetime.fromisoformat(param_value.replace('Z', '+00:00'))
                        except:
                            return False
            
            return True
            
        except Exception:
            return False
    
    def create_custom_template(self, name: str, topic: str, payload: Dict, 
                             parameters: Dict) -> bool:
        """Erstellt ein benutzerdefiniertes Template"""
        try:
            self.templates[name] = {
                "name": name,
                "description": f"Benutzerdefiniertes Template: {name}",
                "topic": topic,
                "payload": payload,
                "parameters": parameters
            }
            print(f"✅ Benutzerdefiniertes Template '{name}' erstellt")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Templates '{name}': {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über Orders zurück"""
        active_count = len(self.active_orders)
        completed_count = len(self.order_history)
        error_count = sum(1 for order in self.order_history if order.get("status") == "ERROR")
        
        # Farb-Statistiken
        color_stats = {}
        for order in self.order_history:
            color = order.get("color", "UNKNOWN")
            color_stats[color] = color_stats.get(color, 0) + 1
        
        return {
            "active_orders": active_count,
            "completed_orders": completed_count,
            "error_orders": error_count,
            "total_orders": active_count + completed_count,
            "color_distribution": color_stats
        }


# Hilfsfunktionen für Dashboard Integration
def create_template_manager_with_mqtt(mqtt_client) -> TemplateMessageManager:
    """Erstellt einen Template Manager mit MQTT Client"""
    manager = TemplateMessageManager()
    manager.set_mqtt_client(mqtt_client)
    return manager


def format_order_display(order_info: Dict) -> str:
    """Formatiert Order-Info für Dashboard-Anzeige"""
    order_id = order_info.get("orderId", "PENDING")
    color = order_info.get("color", "UNKNOWN")
    status = order_info.get("status", "UNKNOWN")
    workpiece_id = order_info.get("workpieceId", "UNKNOWN")
    
    return f"Order {order_id[:8]}... ({color}) - {status} - {workpiece_id}"


if __name__ == "__main__":
    # Test des Template Managers
    manager = TemplateMessageManager()
    
    print("🧪 Template Message Manager Test")
    print("=" * 50)
    
    # Templates auflisten
    templates = manager.list_templates()
    print(f"📋 Verfügbare Templates: {templates}")
    
    # Template Info anzeigen
    for template_name in templates:
        info = manager.get_template_info(template_name)
        print(f"\n📄 {template_name}:")
        print(f"   Beschreibung: {info['description']}")
        print(f"   Topic: {info['topic']}")
        print(f"   Parameter: {list(info['parameters'].keys())}")
    
    # Parameter validieren
    test_params = {
        "color": "RED",
        "workpieceId": "04798eca341290",
        "timestamp": datetime.now().isoformat()
    }
    
    is_valid = manager.validate_parameters("wareneingang_trigger", test_params)
    print(f"\n✅ Parameter Validierung: {'ERFOLGREICH' if is_valid else 'FEHLGESCHLAGEN'}")
    
    # Statistiken
    stats = manager.get_statistics()
    print(f"\n📊 Statistiken: {stats}")
    
    print("\n✅ Template Message Manager Test abgeschlossen")
