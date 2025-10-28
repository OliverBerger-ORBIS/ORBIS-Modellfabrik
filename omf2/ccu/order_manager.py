#!/usr/bin/env python3
"""
CCU Production Order Manager - Business Logic für Production Order Management
Verarbeitet Production Orders (active, completed)

⚠️ STUB VERSION - Nur für MQTT-Infrastruktur Testing
"""

import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Singleton Factory - EXAKT wie Order Manager
_order_manager_instance = None


class OrderManager:
    """
    Order Manager für CCU Domain
    Verwaltet PRODUCTION und STORAGE Orders (active, completed)

    Basierend auf Quick Reference:
    - PRODUCTION: HBW → MILL/DRILL → AIQS → DPS
    - STORAGE: START → DPS → HBW (nur FTS Transport!)
    """

    def __init__(self):
        """Initialize Production Order Manager - EXAKT wie Order Manager (kein File I/O!)"""
        # State-Holder für Orders (Order-ID-basiert)
        self.active_orders = {}  # Dict: order_id -> order_data
        self.completed_orders = {}  # Dict: order_id -> order_data

        # MQTT Steps Storage (Order-ID-basiert)
        self.mqtt_steps = {}  # Dict: order_id -> List[Dict] von MQTT Steps

        # Thread-Sicherheit
        self._lock = threading.Lock()

        # Zeitstempel
        self.last_active_update = None
        self.last_completed_update = None

        # Produktionsplan-Konfiguration (lazy loading)
        self._production_workflows = None
        self._shopfloor_layout = None

        logger.info("🏭 Order Manager initialized with Order-ID-based storage")

    def _extract_serial_from_topic(self, topic: str) -> str:
        """Extrahiere Serial Number aus Topic - Registry-basiert"""
        from omf2.registry.manager.registry_manager import get_registry_manager

        registry_manager = get_registry_manager()
        modules = registry_manager.get_modules()

        # Finde Serial-Nr in Topic (modules ist Dict mit Serial-Nr als Key)
        for serial_nr in modules.keys():
            if serial_nr in topic:
                return serial_nr

        return "UNKNOWN"

    def _get_module_name_from_serial(self, serial_nr: str) -> str:
        """Hole Modul Name aus Serial-Nr - Registry-basiert"""
        from omf2.registry.manager.registry_manager import get_registry_manager

        registry_manager = get_registry_manager()
        modules = registry_manager.get_modules()

        # Hole Modul Name aus Registry
        module_info = modules.get(serial_nr)
        if module_info:
            return module_info["name"]

        return "UNKNOWN"

    def process_ccu_order_active(
        self, topic: str, message: Union[Dict[str, Any], List[Dict[str, Any]]], meta: Dict[str, Any]
    ) -> None:
        """
        Verarbeite ccu/order/active Message (CCU Frontend Consumer)

        Die originale CCU konsolidiert alle Module/FTS States und publiziert
        ccu/order/active als Array von Orders - das ist unsere zentrale Quelle!

        Args:
            topic: MQTT Topic (ccu/order/active)
            message: MQTT Message Payload (Array von Orders oder einzelne Order)
            meta: MQTT Meta-Information (timestamp, qos, retain)
        """
        try:
            # Handle sowohl Array als auch einzelne Order
            if isinstance(message, list):
                orders = message
            else:
                orders = [message] if message else []

            if not orders:
                logger.debug(f"📦 No orders in ccu/order/active from {topic}")
                return

            logger.info(f"🏭 Processing ccu/order/active: {len(orders)} orders")

            # Verarbeite jede Order
            for order in orders:
                production_steps = order.get("productionSteps", [])
                order_id = order.get("orderId", "")
                order_type = order.get("type", "")
                order_type_classification = order.get("orderType", "")  # PRODUCTION or STORAGE

                # DEBUG: Log order details
                logger.info(
                    f"📦 Processing order {order_id[:8] if order_id else 'unknown'}: "
                    f"type={order_type}, orderType={order_type_classification}, "
                    f"steps={len(production_steps)}"
                )

                if not production_steps or not order_id:
                    logger.debug(f"📦 No productionSteps or orderId in order {order_id[:8] if order_id else 'unknown'}")
                    continue

                logger.debug(f"🏭 Processing Order {order_id[:8]}... ({order_type})")

                # Speichere Production Steps direkt (kein Matching nötig!)
                self._store_production_steps(order_id, production_steps)

                # KRITISCH: Speichere Order auch in active_orders für UI-Zugriff!
                with self._lock:
                    self.active_orders[order_id] = order

                logger.debug(f"✅ Order {order_id[:8]}... processed: {len(production_steps)} steps")

            logger.info(f"✅ CCU Order Active processed: {len(orders)} orders")
            # Note: UI refresh is already triggered by gateway._trigger_ui_refresh() in the routing layer

        except Exception as e:
            logger.error(f"❌ Error processing ccu/order/active from {topic}: {e}")

    def process_ccu_order_completed(
        self, topic: str, message: Union[Dict[str, Any], List[Dict[str, Any]]], meta: Dict[str, Any]
    ) -> None:
        """
        Verarbeite ccu/order/completed Message (CCU Frontend Consumer)

        Die originale CCU publiziert ccu/order/completed als Array von completed Orders

        Args:
            topic: MQTT Topic (ccu/order/completed)
            message: MQTT Message Payload (Array von Orders oder einzelne Order)
            meta: MQTT Meta-Information (timestamp, qos, retain)
        """
        try:
            # Handle sowohl Array als auch einzelne Order
            if isinstance(message, list):
                orders = message
            else:
                orders = [message] if message else []

            if not orders:
                logger.debug(f"🏁 No orders in ccu/order/completed from {topic}")
                return

            logger.info(f"🏁 Processing ccu/order/completed: {len(orders)} orders")

            # Verarbeite jede completed Order
            for order in orders:
                order_id = order.get("orderId", "")
                order_type = order.get("type", "")
                state = order.get("state", "")
                finished_at = order.get("finishedAt", "")

                if not order_id:
                    logger.debug("🏁 No orderId in completed order")
                    continue

                logger.info(f"🏁 Completed Order {order_id[:8]}... ({order_type}) - State: {state}")

                # KRITISCH: Verschiebe Order von active_orders zu completed_orders
                with self._lock:
                    if order_id in self.active_orders:
                        # Order von active zu completed verschieben
                        completed_order = self.active_orders[order_id].copy()
                        completed_order["state"] = state
                        completed_order["finishedAt"] = finished_at
                        completed_order["completedTimestamp"] = meta.get("timestamp", "")

                        self.completed_orders[order_id] = completed_order
                        del self.active_orders[order_id]

                        logger.info(f"✅ Order {order_id[:8]}... moved from active to completed")
                    else:
                        # Order direkt als completed speichern (falls nicht in active)
                        self.completed_orders[order_id] = order
                        logger.info(f"✅ Order {order_id[:8]}... stored as completed")

                # Markiere Order als completed in mqtt_steps
                if order_id in self.mqtt_steps:
                    # Füge completion info zu den Steps hinzu
                    for step in self.mqtt_steps[order_id]:
                        if "completion" not in step:
                            step["completion"] = {
                                "state": state,
                                "finishedAt": finished_at,
                                "timestamp": meta.get("timestamp", ""),
                            }

                    logger.info(f"✅ Order {order_id[:8]}... marked as completed with state: {state}")
                else:
                    logger.debug(f"🏁 Order {order_id[:8]}... not found in mqtt_steps")

            logger.info(f"✅ CCU Order Completed processed: {len(orders)} orders")
            # Note: UI refresh is already triggered by gateway._trigger_ui_refresh() in the routing layer

        except Exception as e:
            logger.error(f"❌ Error processing ccu/order/completed from {topic}: {e}")

    def _store_production_steps(self, order_id: str, production_steps: List[Dict[str, Any]]) -> None:
        """
        Speichere Production Steps direkt aus ccu/order/active

        Args:
            order_id: Order ID
            production_steps: Production Steps aus ccu/order/active
        """
        if order_id not in self.mqtt_steps:
            self.mqtt_steps[order_id] = []

        # Speichere Production Steps direkt (kein Matching nötig!)
        self.mqtt_steps[order_id] = production_steps
        logger.debug(f"📋 Stored {len(production_steps)} production steps for Order {order_id[:8]}...")

    def process_ccu_response_message(self, topic: str, message: Any, meta: Dict[str, Any]) -> None:
        """
        Verarbeitet CCU Response Messages für Order-Bestätigungen

        Args:
            topic: MQTT Topic (z.B. ccu/order/response)
            message: Message Payload (bereits validiert)
            meta: Message Metadata
        """
        try:
            logger.info(f"📨 [STUB] Processing CCU response message from {topic}")
            logger.debug(f"📦 CCU Response Payload: {message}")

            # TODO: Implement CCU response processing
            # - Extract orderId from message
            # - Update order status
            # - Update global order status

            logger.info(f"✅ [STUB] CCU response message processed from {topic}")

        except Exception as e:
            logger.error(f"❌ [STUB] Error processing CCU response message from {topic}: {e}")

    def get_active_orders(self) -> List[Dict[str, Any]]:
        """
        Gibt die aktiven Orders zurück (als Liste für UI-Kompatibilität)

        Returns:
            Liste von aktiven Orders
        """
        with self._lock:
            orders_list = list(self.active_orders.values())
            logger.debug(f"📋 Getting active orders: {len(orders_list)} orders")
            # DEBUG: Log order types
            for order in orders_list:
                order_id = order.get("orderId", "N/A")[:8]
                order_type = order.get("orderType", "N/A")
                logger.debug(f"  - Active order {order_id}: orderType={order_type}")
            return orders_list

    def get_completed_orders(self) -> List[Dict[str, Any]]:
        """
        Gibt die abgeschlossenen Orders zurück (als Liste für UI-Kompatibilität)

        Returns:
            Liste von abgeschlossenen Orders
        """
        with self._lock:
            orders_list = list(self.completed_orders.values())
            logger.debug(f"✅ [STUB] Getting completed orders: {len(orders_list)} orders")
            return orders_list

    def get_order_statistics(self) -> Dict[str, Any]:
        """
        Gibt Order-Statistiken zurück

        Returns:
            Dict mit Statistiken
        """
        with self._lock:
            active_count = len(self.active_orders)
            completed_count = len(self.completed_orders)

            return {
                "active_count": active_count,
                "completed_count": completed_count,
                "total_count": active_count + completed_count,
                "last_active_update": self.last_active_update.isoformat() if self.last_active_update else None,
                "last_completed_update": self.last_completed_update.isoformat() if self.last_completed_update else None,
                "stub_mode": False,  # Order-ID-basierte Implementierung
            }

    def _load_shopfloor_layout(self) -> Dict[str, Any]:
        """Lädt Shopfloor Layout aus Konfiguration (lazy loading)"""
        if self._shopfloor_layout is None:
            try:
                config_path = Path(__file__).parent.parent / "config" / "ccu" / "shopfloor_layout.json"
                with open(config_path, encoding="utf-8") as f:
                    self._shopfloor_layout = json.load(f)
                logger.debug("🏭 Shopfloor layout loaded from config")
            except Exception as e:
                logger.warning(f"⚠️ Could not load shopfloor layout: {e}")
                self._shopfloor_layout = {}
        return self._shopfloor_layout

    def get_complete_order_plan(self, order: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Gibt den KOMPLETTEN Order-Plan zurück (PRODUCTION oder STORAGE)

        PRODUCTION Orders: HBW → MILL/DRILL → AIQS → DPS
        STORAGE Orders: START → DPS → HBW (nur FTS Transport!)

        Args:
            order: Order-Dict mit workpiece type und orderType

        Returns:
            Kompletter Order-Plan mit aktuellem Status
        """
        workpiece_type = order.get("type", "RED")
        order_type = order.get("orderType", "PRODUCTION")
        order_id = order.get("orderId")

        # Hole Steps aus gespeicherten MQTT-Daten
        if order_id and order_id in self.mqtt_steps:
            order_steps = self.mqtt_steps[order_id]
            logger.debug(f"📋 Using {len(order_steps)} stored MQTT steps for {order_type} Order {order_id[:8]}...")
        else:
            # KEIN FALLBACK! Wenn keine MQTT-Daten, dann leere Liste
            logger.warning(f"⚠️ No MQTT data found for Order {order_id[:8] if order_id else 'unknown'}")
            return []

        # UX-Verbesserung: Navigation Steps als IN_PROGRESS markieren
        self._enhance_navigation_steps(order_steps)

        logger.debug(f"📋 Order Plan: {len(order_steps)} steps for {order_type} order {workpiece_type}")

        return order_steps

    def get_complete_production_plan(self, order: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Backward-Compatibility: Ruft get_complete_order_plan() auf

        DEPRECATED: Verwende get_complete_order_plan() für alle Order-Typen
        """
        return self.get_complete_order_plan(order)

    def get_complete_storage_plan(self, order: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Gibt den STORAGE-Plan zurück (gleiche Logik wie Production)

        Storage Orders: START → DPS → HBW (nur FTS Transport!)
        """
        return self.get_complete_order_plan(order)

    def _enhance_navigation_steps(self, steps: List[Dict[str, Any]]) -> None:
        """
        UX-Verbesserung: Navigation Steps als IN_PROGRESS markieren

        LOGIK: Wenn keine Production Step IN_PROGRESS, dann suche den ersten ENQUEUED.
        Wenn dieser ein NAVIGATION Step ist, dann setze auf IN_PROGRESS.

        Args:
            steps: Liste der Production Steps
        """
        if not steps:
            return

        # 1. Prüfe ob bereits ein Production Step IN_PROGRESS ist
        has_production_in_progress = False
        for step in steps:
            if step.get("state") == "IN_PROGRESS" and step.get("type") == "MANUFACTURE":
                has_production_in_progress = True
                break

        # 2. Wenn KEIN Production Step IN_PROGRESS ist
        if not has_production_in_progress:
            # Suche den ersten ENQUEUED Step
            for i, step in enumerate(steps):
                if step.get("state") == "ENQUEUED":
                    # Wenn es ein NAVIGATION Step ist, setze auf IN_PROGRESS
                    if step.get("type") == "NAVIGATION":
                        step["state"] = "IN_PROGRESS"
                        logger.info(f"🔄 Enhanced Navigation Step {i}: {step.get('source')} → {step.get('target')}")
                    break

    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Gibt eine spezifische Order nach ID zurück

        Args:
            order_id: Order-ID

        Returns:
            Order-Dict oder None wenn nicht gefunden
        """
        with self._lock:
            order = self.active_orders.get(order_id)
            if order:
                logger.debug(f"📋 Order found: {order_id}")
            else:
                logger.debug(f"📋 Order not found: {order_id}")
            return order

    def get_complete_production_plan_by_order_id(self, order_id: str) -> List[Dict[str, Any]]:
        """
        Gibt den KOMPLETTEN Produktionsplan für eine Order-ID zurück

        Args:
            order_id: Order-ID

        Returns:
            Kompletter Produktionsplan mit aktuellem Status oder leere Liste
        """
        order = self.get_order_by_id(order_id)
        if order:
            return self.get_complete_production_plan(order)
        else:
            logger.warning(f"⚠️ No order found for ID: {order_id}")
            return []


def get_order_manager() -> OrderManager:
    """
    Get Order Manager singleton instance - EXAKT wie Stock Manager

    Returns:
        OrderManager: Order Manager Instanz
    """
    global _order_manager_instance
    if _order_manager_instance is None:
        _order_manager_instance = OrderManager()
        logger.info("🏗️ Order Manager singleton created")
    return _order_manager_instance
