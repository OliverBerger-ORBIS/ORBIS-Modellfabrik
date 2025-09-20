#!/usr/bin/env python3
"""
VDA5050 Order Manager für APS-Integration
Implementiert VDA5050 Standard für Order-Management basierend auf Registry-Templates
Version: 1.0.0
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from omf.tools.logging_config import get_logger
from omf.tools.registry_manager import get_registry


class VDA5050OrderManager:
    """VDA5050-konformer Order Manager für APS-Integration"""
    
    def __init__(self):
        self.logger = get_logger("omf.tools.aps_vda5050_manager")
        self.registry = get_registry()
        
        # Order Management
        self.active_orders = {}  # orderId -> order_info
        self.order_history = []  # Abgeschlossene Orders
        self.order_counter = 0   # Für orderUpdateId
        
        # VDA5050 Standard-Konfiguration
        self.vda5050_config = self._load_vda5050_config()
        
        self.logger.info("VDA5050OrderManager initialisiert")
    
    def _load_vda5050_config(self) -> Dict[str, Any]:
        """Lädt VDA5050-Konfiguration aus Registry"""
        try:
            # Bestehende Registry-Konfiguration nutzen
            config = {
                "workpiece_types": ["RED", "BLUE", "WHITE"],
                "order_types": ["STORAGE", "RETRIEVAL", "TRANSPORT"],
                "action_states": ["WAITING", "RUNNING", "FINISHED", "FAILED"],
                "operating_modes": ["TEACHIN", "AUTOMATIC"],
                "quality_states": ["OK", "NOT-OK", "PENDING", "FAILED"]
            }
            
            # Registry-basierte Konfiguration erweitern
            if self.registry:
                workpieces = self.registry.workpieces()
                if workpieces:
                    config["workpiece_types"] = workpieces.get("colors", config["workpiece_types"])
                    config["quality_states"] = workpieces.get("quality_check_options", config["quality_states"])
            
            return config
            
        except Exception as e:
            self.logger.warning(f"Registry-Konfiguration nicht verfügbar, verwende Standard: {e}")
            return {
                "workpiece_types": ["RED", "BLUE", "WHITE"],
                "order_types": ["STORAGE", "RETRIEVAL", "TRANSPORT"],
                "action_states": ["WAITING", "RUNNING", "FINISHED", "FAILED"],
                "operating_modes": ["TEACHIN", "AUTOMATIC"],
                "quality_states": ["OK", "NOT-OK", "PENDING", "FAILED"]
            }
    
    def create_storage_order(self, color: str, workpiece_id: str = None, target_module: str = None) -> Dict[str, Any]:
        """Erstellt VDA5050-konforme Storage Order"""
        try:
            # Validierung
            if color not in self.vda5050_config["workpiece_types"]:
                available = self.vda5050_config['workpiece_types']
                raise ValueError(f"Unbekannte Werkstück-Farbe: {color}. Verfügbar: {available}")
            
            # Order-ID generieren
            order_id = str(uuid.uuid4())
            workpiece_id = workpiece_id or f"WP_{color}_{int(datetime.now().timestamp())}"
            
            # VDA5050-konforme Order-Struktur
            vda_order = {
                "orderId": order_id,
                "timestamp": datetime.now().isoformat(),
                "action": "STORAGE",
                "type": color.upper(),
                "workpieceId": workpiece_id,
                "orderUpdateId": 0
            }
            
            # Target Module hinzufügen falls spezifiziert
            if target_module:
                vda_order["targetModule"] = target_module
            
            # Order registrieren
            self.active_orders[order_id] = {
                "order": vda_order,
                "status": "CREATED",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            self.logger.info(f"📋 VDA5050 Order erstellt: {color} Werkstück {workpiece_id} "
                           f"(Order: {order_id})")
            return vda_order
            
        except Exception as e:
            self.logger.error(f"❌ Order-Erstellung fehlgeschlagen: {e}")
            raise
    
    def create_retrieval_order(self, color: str, workpiece_id: str = None, source_module: str = None) -> Dict[str, Any]:
        """Erstellt VDA5050-konforme Retrieval Order"""
        try:
            # Validierung
            if color not in self.vda5050_config["workpiece_types"]:
                available = self.vda5050_config['workpiece_types']
                raise ValueError(f"Unbekannte Werkstück-Farbe: {color}. Verfügbar: {available}")
            
            # Order-ID generieren
            order_id = str(uuid.uuid4())
            workpiece_id = workpiece_id or f"WP_{color}_{int(datetime.now().timestamp())}"
            
            # VDA5050-konforme Order-Struktur
            vda_order = {
                "orderId": order_id,
                "timestamp": datetime.now().isoformat(),
                "action": "RETRIEVAL",
                "type": color.upper(),
                "workpieceId": workpiece_id,
                "orderUpdateId": 0
            }
            
            # Source Module hinzufügen falls spezifiziert
            if source_module:
                vda_order["sourceModule"] = source_module
            
            # Order registrieren
            self.active_orders[order_id] = {
                "order": vda_order,
                "status": "CREATED",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            self.logger.info(f"📋 VDA5050 Retrieval Order erstellt: {color} Werkstück {workpiece_id} "
                           f"(Order: {order_id})")
            return vda_order
            
        except Exception as e:
            self.logger.error(f"❌ Retrieval Order-Erstellung fehlgeschlagen: {e}")
            raise
    
    def process_order_response(self, response: Dict[str, Any]) -> bool:
        """Verarbeitet VDA5050 Order Response"""
        try:
            order_id = response.get("orderId")
            if not order_id:
                self.logger.warning("Order Response ohne orderId erhalten")
                return False
            
            # Order-Status aktualisieren
            if order_id in self.active_orders:
                self.active_orders[order_id].update({
                    "response": response,
                    "last_updated": datetime.now().isoformat()
                })
                
                # Status aus Response extrahieren
                status = response.get("status", "UNKNOWN")
                self.active_orders[order_id]["status"] = status
                
                self.logger.info(f"📋 Order {order_id} Response verarbeitet: {status}")
                return True
            else:
                self.logger.warning(f"Order {order_id} nicht in aktiven Orders gefunden")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Order Response Verarbeitung fehlgeschlagen: {e}")
            return False
    
    def process_state_message(self, state_message: Dict[str, Any]) -> bool:
        """Verarbeitet VDA5050 State Message"""
        try:
            order_id = state_message.get("orderId")
            if not order_id:
                return False
            
            # State-Informationen extrahieren
            action_state = state_message.get("actionState", {})
            action_states = state_message.get("actionStates", [])
            errors = state_message.get("errors", [])
            
            # Order-Status aktualisieren falls Order aktiv
            if order_id in self.active_orders:
                self.active_orders[order_id].update({
                    "state": state_message,
                    "action_state": action_state,
                    "action_states": action_states,
                    "errors": errors,
                    "last_updated": datetime.now().isoformat()
                })
                
                # Status aus Action State ableiten
                if action_state:
                    command_state = action_state.get("state", "UNKNOWN")
                    self.active_orders[order_id]["status"] = command_state
                
                self.logger.debug(f"📊 State für Order {order_id} aktualisiert")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ State Message Verarbeitung fehlgeschlagen: {e}")
            return False
    
    def send_instant_action(self, action_type: str, parameters: Dict[str, Any] = None, target_module: str = None) -> Dict[str, Any]:
        """Sendet VDA5050 Instant Action"""
        try:
            if parameters is None:
                parameters = {}
            
            # Action-ID generieren
            action_id = str(uuid.uuid4())
            
            # VDA5050-konforme Instant Action
            instant_action = {
                "actionType": action_type,
                "actionId": action_id,
                "timestamp": datetime.now().isoformat(),
                "parameters": parameters
            }
            
            # Target Module hinzufügen falls spezifiziert
            if target_module:
                instant_action["targetModule"] = target_module
            
            self.logger.info(f"⚡ VDA5050 Instant Action gesendet: {action_type} (ID: {action_id})")
            return instant_action
            
        except Exception as e:
            self.logger.error(f"❌ Instant Action Erstellung fehlgeschlagen: {e}")
            raise
    
    def complete_order(self, order_id: str, result: Dict[str, Any] = None) -> bool:
        """Schließt Order ab und verschiebt in Historie"""
        try:
            if order_id not in self.active_orders:
                self.logger.warning(f"Order {order_id} nicht in aktiven Orders gefunden")
                return False
            
            # Order in Historie verschieben
            order_info = self.active_orders[order_id].copy()
            order_info.update({
                "status": "COMPLETED",
                "completed_at": datetime.now().isoformat(),
                "result": result or {}
            })
            
            self.order_history.append(order_info)
            del self.active_orders[order_id]
            
            self.logger.info(f"✅ Order {order_id} abgeschlossen und in Historie verschoben")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Order-Abschluss fehlgeschlagen: {e}")
            return False
    
    def cancel_order(self, order_id: str, reason: str = None) -> bool:
        """Bricht Order ab"""
        try:
            if order_id not in self.active_orders:
                self.logger.warning(f"Order {order_id} nicht in aktiven Orders gefunden")
                return False
            
            # Order-Status aktualisieren
            self.active_orders[order_id].update({
                "status": "CANCELLED",
                "cancelled_at": datetime.now().isoformat(),
                "cancellation_reason": reason or "User cancelled"
            })
            
            self.logger.info(f"❌ Order {order_id} abgebrochen: {reason or 'Kein Grund angegeben'}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Order-Abbruch fehlgeschlagen: {e}")
            return False
    
    def get_active_orders(self) -> Dict[str, Dict[str, Any]]:
        """Gibt aktive Orders zurück"""
        return self.active_orders.copy()
    
    def get_order_history(self) -> List[Dict[str, Any]]:
        """Gibt Order-Historie zurück"""
        return self.order_history.copy()
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Gibt Order nach ID zurück"""
        # Zuerst in aktiven Orders suchen
        if order_id in self.active_orders:
            return self.active_orders[order_id]
        
        # Dann in Historie suchen
        for order in self.order_history:
            if order.get("order", {}).get("orderId") == order_id:
                return order
        
        return None
    
    def get_orders_by_color(self, color: str) -> List[Dict[str, Any]]:
        """Gibt alle Orders einer Farbe zurück"""
        matching_orders = []
        
        # Aktive Orders durchsuchen
        for order_info in self.active_orders.values():
            order = order_info.get("order", {})
            if order.get("type") == color.upper():
                matching_orders.append(order_info)
        
        # Historie durchsuchen
        for order_info in self.order_history:
            order = order_info.get("order", {})
            if order.get("type") == color.upper():
                matching_orders.append(order_info)
        
        return matching_orders
    
    def get_orders_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Gibt alle Orders mit einem bestimmten Status zurück"""
        matching_orders = []
        
        # Aktive Orders durchsuchen
        for order_info in self.active_orders.values():
            if order_info.get("status") == status:
                matching_orders.append(order_info)
        
        # Historie durchsuchen
        for order_info in self.order_history:
            if order_info.get("status") == status:
                matching_orders.append(order_info)
        
        return matching_orders
    
    def get_order_statistics(self) -> Dict[str, Any]:
        """Gibt Order-Statistiken zurück"""
        total_active = len(self.active_orders)
        total_history = len(self.order_history)
        
        # Status-Verteilung
        status_counts = {}
        for order_info in self.active_orders.values():
            status = order_info.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Farb-Verteilung
        color_counts = {}
        for order_info in self.active_orders.values():
            order = order_info.get("order", {})
            color = order.get("type", "UNKNOWN")
            color_counts[color] = color_counts.get(color, 0) + 1
        
        return {
            "total_active_orders": total_active,
            "total_completed_orders": total_history,
            "status_distribution": status_counts,
            "color_distribution": color_counts,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_vda5050_config(self) -> Dict[str, Any]:
        """Gibt VDA5050-Konfiguration zurück"""
        return self.vda5050_config.copy()
    
    def validate_order(self, order: Dict[str, Any]) -> List[str]:
        """Validiert VDA5050 Order-Struktur"""
        errors = []
        
        # Erforderliche Felder prüfen
        required_fields = ["orderId", "timestamp", "action", "type", "workpieceId"]
        for field in required_fields:
            if field not in order:
                errors.append(f"Erforderliches Feld fehlt: {field}")
        
        # Action-Typ validieren
        if "action" in order and order["action"] not in self.vda5050_config["order_types"]:
            errors.append(f"Ungültiger Action-Typ: {order['action']}")
        
        # Werkstück-Typ validieren
        if "type" in order and order["type"] not in self.vda5050_config["workpiece_types"]:
            errors.append(f"Ungültiger Werkstück-Typ: {order['type']}")
        
        return errors
    
    def clear_completed_orders(self, older_than_hours: int = 24) -> int:
        """Löscht abgeschlossene Orders älter als X Stunden"""
        try:
            cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
            removed_count = 0
            
            # Historie durchsuchen und alte Orders entfernen
            self.order_history = [
                order for order in self.order_history
                if datetime.fromisoformat(order.get("completed_at", "1970-01-01T00:00:00")).timestamp() > cutoff_time
            ]
            
            removed_count = len(self.order_history) - len(self.order_history)
            
            if removed_count > 0:
                self.logger.info(f"🗑️ {removed_count} alte Orders aus Historie entfernt")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"❌ Order-Bereinigung fehlgeschlagen: {e}")
            return 0
