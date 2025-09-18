#!/usr/bin/env python3
"""
Order Tracking Manager für APS Bestellungsverfolgung
Verwaltet Order-Status und -Historie
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

class OrderTrackingManager:
    """Verwaltet Order-Tracking für APS Bestellungen"""

    def __init__(self):
        self.active_orders = {}  # orderId -> order_info
        self.order_history = []  # Liste aller abgeschlossenen Orders

    def start_order_tracking(self, workpiece_id: str, color: str, order_type: str = "STORAGE") -> str:
        """Startet das Tracking für eine neue Order"""
        order_id = str(uuid.uuid4())

        tracking_info = {
            "orderId": order_id,
            "workpieceId": workpiece_id,
            "color": color,
            "orderType": order_type,
            "startTime": datetime.now().isoformat(),
            "status": "WAITING_FOR_ORDER_ID",
            "messages": [],
            "ccuResponse": None,
            "endTime": None,
            "errorTime": None,
        }

        self.active_orders[order_id] = tracking_info
        print(f"📊 Order Tracking gestartet für {color} Werkstück {workpiece_id} (Order ID: {order_id})")
        return order_id

    def update_order_status(self, order_id: str, status: str, message: Dict[str, Any] = None):
        """Aktualisiert den Status einer Order"""
        if order_id in self.active_orders:
            order_info = self.active_orders[order_id]
            order_info["status"] = status

            if message:
                order_info["messages"].append({"timestamp": datetime.now().isoformat(), "data": message})

            print(f"📊 Order {order_id} Status: {status}")

            # Wenn Order abgeschlossen, in Historie verschieben
            if status in ["COMPLETED", "ERROR", "CANCELLED"]:
                order_info["endTime"] = datetime.now().isoformat()
                if status == "ERROR":
                    order_info["errorTime"] = datetime.now().isoformat()

                self.order_history.append(order_info)
                del self.active_orders[order_id]
                print(f"📊 Order {order_id} abgeschlossen und in Historie verschoben")

    def handle_ccu_response(self, order_id: str, response_data: Dict[str, Any]):
        """Behandelt CCU Response und aktualisiert Order"""
        if order_id in self.active_orders:
            order_info = self.active_orders[order_id]
            order_info["ccuResponse"] = response_data
            order_info["status"] = "ACTIVE"

            # Production Steps aus CCU Response extrahieren
            if "productionSteps" in response_data:
                order_info["productionSteps"] = response_data["productionSteps"]

            print(f"✅ CCU Response für Order {order_id} verarbeitet")
            return True
        else:
            print(f"⚠️ Keine aktive Order gefunden für Order ID {order_id}")
            return False

    def get_active_orders(self) -> Dict[str, Any]:
        """Gibt alle aktiven Orders zurück"""
        return self.active_orders

    def get_order_history(self) -> List[Dict[str, Any]]:
        """Gibt Order-Historie zurück"""
        return self.order_history

    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Gibt eine spezifische Order zurück"""
        if order_id in self.active_orders:
            return self.active_orders[order_id]

        # In Historie suchen
        for order in self.order_history:
            if order.get("orderId") == order_id:
                return order

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Order-Statistiken zurück"""
        active_count = len(self.active_orders)
        completed_count = len([o for o in self.order_history if o.get("status") == "COMPLETED"])
        error_count = len([o for o in self.order_history if o.get("status") == "ERROR"])
        total_count = active_count + len(self.order_history)

        # Farb-Verteilung
        color_distribution = {}
        for order in list(self.active_orders.values()) + self.order_history:
            color = order.get("color", "UNKNOWN")
            color_distribution[color] = color_distribution.get(color, 0) + 1

        return {
            "active_orders": active_count,
            "completed_orders": completed_count,
            "error_orders": error_count,
            "total_orders": total_count,
            "color_distribution": color_distribution,
        }

    def clear_history(self):
        """Löscht die Order-Historie"""
        self.order_history = []
        print("🗑️ Order-Historie gelöscht")

    def export_orders(self) -> str:
        """Exportiert alle Orders als JSON"""
        export_data = {
            "active_orders": self.active_orders,
            "order_history": self.order_history,
            "export_timestamp": datetime.now().isoformat(),
        }
        return json.dumps(export_data, indent=2, default=str)
