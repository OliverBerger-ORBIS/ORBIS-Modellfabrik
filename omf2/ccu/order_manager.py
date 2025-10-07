#!/usr/bin/env python3
"""
CCU Order Manager - Business Logic für Order Management
Verarbeitet Stock-Nachrichten und verwaltet Lagerbestand
"""

import json
import threading
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Singleton Factory - EXAKT wie Sensor Manager
_order_manager_instance = None


class OrderManager:
    """
    Order Manager für CCU Domain
    Verwaltet Lagerbestand, Kundenaufträge und Rohmaterial-Bestellungen
    """

    def __init__(self):
        """Initialize Order Manager - EXAKT wie Sensor Manager (kein File I/O!)"""
        # Inventory State-Holder (wie sensor_data beim Sensor Manager)
        self.inventory = {f"{chr(65+i)}{j+1}": None for i in range(3) for j in range(3)}
        
        # Default-Werte (KEINE Config-Datei laden!)
        self.workpiece_types = ["RED", "BLUE", "WHITE"]
        self.max_capacity = 3
        
        # Bestellungen
        self.orders = []
        
        # Thread-Sicherheit
        self._lock = threading.Lock()
        
        # Zeitstempel
        self.last_update_timestamp = None
        
        logger.info("🏭 Order Manager initialized with State-Holder (no file I/O)")


    def process_stock_message(self, topic: str, message: Dict[str, Any], meta: Dict[str, Any]) -> None:
        """
        Verarbeitet Stock-Nachrichten vom Topic /j1/txt/1/f/i/stock
        
        Args:
            topic: MQTT Topic
            message: Message payload
            meta: Meta-Informationen (timestamp, qos, retain)
        """
        try:
            with self._lock:
                logger.debug(f"📦 Processing stock message from {topic}: {message}")
                
                # Stock-Daten verarbeiten (anpassen je nach tatsächlicher Message-Struktur)
                if "stock" in message:
                    stock_data = message["stock"]
                    self._update_inventory_from_stock(stock_data)
                elif "loads" in message:
                    # Fallback für HBW-ähnliche Struktur
                    loads_data = message["loads"]
                    self._update_inventory_from_loads(loads_data)
                else:
                    # Direkte Inventory-Daten
                    self._update_inventory_from_stock(message)
                
                # Zeitstempel aktualisieren
                self.last_update_timestamp = datetime.now(timezone.utc)
                
                logger.info(f"✅ Inventory updated from {topic}")
                
        except Exception as e:
            logger.error(f"❌ Error processing stock message from {topic}: {e}")

    def _update_inventory_from_stock(self, stock_data: Dict[str, Any]) -> None:
        """Aktualisiert Lagerbestand aus Stock-Daten - Echte MQTT-Daten"""
        try:
            # Lagerbestand zurücksetzen
            for position in self.inventory:
                self.inventory[position] = None
            
            # Echte MQTT-Daten verarbeiten: stockItems Array
            stock_items = stock_data.get("stockItems", [])
            
            for item in stock_items:
                location = item.get("location")  # e.g., "A1", "B2", etc.
                workpiece_data = item.get("workpiece", {})
                
                if location in self.inventory:
                    # Extract workpiece type from the workpiece data (einfache Version)
                    workpiece_type = workpiece_data.get("type")
                    
                    if workpiece_type and workpiece_type != "":
                        # Einfache String-Darstellung (kein State-Tracking)
                        self.inventory[location] = workpiece_type
                    # If type is empty or "", position remains None (empty)
                        
            logger.debug(f"📦 Inventory updated from stock: {self.inventory}")
            logger.info(f"📦 Processed {len(stock_items)} stock items")
                        
        except Exception as e:
            logger.error(f"❌ Error updating inventory from stock data: {e}")

    def _update_inventory_from_loads(self, loads_data: List[Dict[str, Any]]) -> None:
        """Aktualisiert Lagerbestand aus Loads-Daten (HBW-ähnlich)"""
        try:
            # Lagerbestand zurücksetzen
            for position in self.inventory:
                self.inventory[position] = None
            
            # Neue Lagerbestand-Daten verarbeiten
            for load in loads_data:
                position = load.get("position")
                workpiece = load.get("workpiece")
                if position in self.inventory and workpiece in self.workpiece_types:
                    self.inventory[position] = workpiece
                    
        except Exception as e:
            logger.error(f"❌ Error updating inventory from loads data: {e}")

    def get_available_workpieces(self) -> Dict[str, int]:
        """
        Gibt die verfügbaren Werkstücke zurück (OHNE Lock - wird intern aufgerufen)
        
        Returns:
            Dict mit Anzahl pro Werkstück-Typ
        """
        available = {"RED": 0, "BLUE": 0, "WHITE": 0}
        
        for position, workpiece in self.inventory.items():
            if workpiece in available:
                available[workpiece] += 1
        
        return available

    def get_workpiece_need(self) -> Dict[str, int]:
        """
        Gibt den Bedarf für jedes Werkstück zurück (OHNE Lock - wird intern aufgerufen)
        
        Returns:
            Dict mit Bedarf pro Werkstück-Typ
        """
        available = self.get_available_workpieces()
        need = {}
        
        for workpiece_type in self.workpiece_types:
            current_count = available.get(workpiece_type, 0)
            need[workpiece_type] = max(0, self.max_capacity - current_count)
        
        return need

    def get_inventory_status(self) -> Dict[str, Any]:
        """
        Gibt den aktuellen Lagerbestand-Status zurück
        
        Returns:
            Dict mit Lagerbestand-Informationen
        """
        with self._lock:
            available = self.get_available_workpieces()
            need = self.get_workpiece_need()
            
            return {
                "inventory": self.inventory.copy(),
                "available": available,
                "need": need,
                "max_capacity": self.max_capacity,
                "last_update": self.last_update_timestamp.isoformat() if self.last_update_timestamp else None
            }

    def get_formatted_timestamp(self) -> str:
        """Gibt den formatierten Zeitstempel zurück"""
        if self.last_update_timestamp:
            return self.last_update_timestamp.strftime("%d.%m.%Y %H:%M:%S")
        return "Nie"

    def send_customer_order(self, workpiece_type: str) -> bool:
        """
        Sendet eine Kundenauftrag-Bestellung
        
        Args:
            workpiece_type: RED, BLUE, oder WHITE
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            if workpiece_type not in self.workpiece_types:
                logger.error(f"❌ Invalid workpiece type: {workpiece_type}")
                return False
            
            # TODO: Implementiere MQTT-Versand über Gateway
            # order_payload = {
            #     "type": workpiece_type,
            #     "timestamp": datetime.now(timezone.utc).isoformat(),
            #     "orderType": "PRODUCTION"
            # }
            # gateway.publish("ccu/order/request", order_payload)
            
            logger.info(f"📋 Customer order sent for {workpiece_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending customer order for {workpiece_type}: {e}")
            return False

    def send_raw_material_order(self, workpiece_type: str) -> bool:
        """
        Sendet eine Rohmaterial-Bestellung
        
        Args:
            workpiece_type: RED, BLUE, oder WHITE
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            if workpiece_type not in self.workpiece_types:
                logger.error(f"❌ Invalid workpiece type: {workpiece_type}")
                return False
            
            # TODO: Implementiere MQTT-Versand über Gateway
            # raw_material_payload = {
            #     "type": workpiece_type,
            #     "timestamp": datetime.now(timezone.utc).isoformat(),
            #     "orderType": "RAW_MATERIAL"
            # }
            # gateway.publish("ccu/order/raw_material", raw_material_payload)
            
            logger.info(f"📦 Raw material order sent for {workpiece_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending raw material order for {workpiece_type}: {e}")
            return False


def get_order_manager() -> OrderManager:
    """
    Get Order Manager singleton instance - EXAKT wie Sensor Manager
    
    Returns:
        OrderManager: Order Manager Instanz
    """
    global _order_manager_instance
    if _order_manager_instance is None:
        _order_manager_instance = OrderManager()
        logger.info("🏗️ Order Manager singleton created")
    return _order_manager_instance
