#!/usr/bin/env python3
"""
CCU Production Order Manager - Business Logic für Production Order Management
Verarbeitet Production Orders (active, completed)

⚠️ STUB VERSION - Nur für MQTT-Infrastruktur Testing
"""

import threading
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Singleton Factory - EXAKT wie Order Manager
_production_order_manager_instance = None


class ProductionOrderManager:
    """
    Production Order Manager für CCU Domain
    Verwaltet Production Orders (active, completed)
    
    ⚠️ STUB VERSION - Nur für Testing
    """

    def __init__(self):
        """Initialize Production Order Manager - EXAKT wie Order Manager (kein File I/O!)"""
        # State-Holder für Orders (Order-ID-basiert)
        self.active_orders = {}  # Dict: order_id -> order_data
        self.completed_orders = {}  # Dict: order_id -> order_data
        
        # Thread-Sicherheit
        self._lock = threading.Lock()
        
        # Zeitstempel
        self.last_active_update = None
        self.last_completed_update = None
        
        # Produktionsplan-Konfiguration (lazy loading)
        self._production_workflows = None
        self._shopfloor_layout = None
        
        logger.info("🏭 Production Order Manager initialized with Order-ID-based storage")

    def process_active_order_message(self, topic: str, message: Any, meta: Dict[str, Any]) -> None:
        """
        Verarbeitet Active Order Messages vom Topic ccu/order/active
        
        Order-ID-basierte Zuordnung: Jede Order wird nach orderId gespeichert
        
        Args:
            topic: MQTT Topic
            message: Message payload (Array oder null)
            meta: Meta-Informationen (timestamp, qos, retain)
        """
        try:
            with self._lock:
                logger.info(f"📋 Processing active order message from {topic}")
                logger.debug(f"📋 Message type: {type(message)}, content: {message}")
                
                if message is None:
                    logger.info("📋 Active orders: None (empty)")
                    self.active_orders = {}
                elif isinstance(message, list):
                    logger.info(f"📋 Processing {len(message)} active orders")
                    
                    # Order-ID-basierte Zuordnung
                    for order in message:
                        order_id = order.get('orderId')
                        if order_id:
                            # Warning bei doppelten UUIDs (Test-Daten)
                            if order_id in self.active_orders:
                                logger.warning(f"⚠️ UUID ALREADY EXISTS: Order {order_id} already in active_orders! (Test data with identical UUIDs?)")
                            self.active_orders[order_id] = order
                            order_type = order.get('orderType', 'UNKNOWN')
                            workpiece_type = order.get('type', 'N/A')
                            logger.debug(f"📋 Order stored: {order_id} ({order_type}/{workpiece_type})")
                            
                            # Log Order-Typ für Debugging
                            if order_type == 'STORAGE':
                                logger.info(f"📦 STORAGE Order: {order_id} ({workpiece_type})")
                            elif order_type == 'PRODUCTION':
                                logger.info(f"🏭 PRODUCTION Order: {order_id} ({workpiece_type})")
                        else:
                            logger.warning(f"⚠️ Order without orderId: {order}")
                else:
                    logger.warning(f"⚠️ Unexpected message type: {type(message)}")
                
                self.last_active_update = datetime.now(timezone.utc)
                logger.info(f"✅ Active orders updated from {topic}: {len(self.active_orders)} orders")
                
        except Exception as e:
            logger.error(f"❌ Error processing active order message from {topic}: {e}")

    def process_completed_order_message(self, topic: str, message: Any, meta: Dict[str, Any]) -> None:
        """
        Verarbeitet Completed Order Messages vom Topic ccu/order/completed
        
        Args:
            topic: MQTT Topic
            message: Message payload (Array oder null)
            meta: Meta-Informationen (timestamp, qos, retain)
        """
        try:
            with self._lock:
                logger.info(f"✅ [STUB] Processing completed order message from {topic}")
                logger.debug(f"✅ [STUB] Message type: {type(message)}, content: {message}")
                
                # Order-ID-basierte Zuordnung für Completed Orders
                if message is None:
                    logger.info("✅ [STUB] Completed orders: None (empty)")
                    self.completed_orders.clear()
                elif isinstance(message, list):
                    logger.info(f"✅ [STUB] Processing {len(message)} completed orders")
                    
                    # Order-ID-basierte Zuordnung
                    for order in message:
                        order_id = order.get('orderId')
                        if order_id:
                            # Warning bei doppelten UUIDs (Test-Daten)
                            if order_id in self.completed_orders:
                                logger.warning(f"⚠️ UUID ALREADY EXISTS: Order {order_id} already in completed_orders! (Test data with identical UUIDs?)")
                            
                            # Order in completed_orders speichern
                            self.completed_orders[order_id] = order
                            
                            # WICHTIG: Order aus active_orders entfernen!
                            if order_id in self.active_orders:
                                del self.active_orders[order_id]
                                logger.info(f"✅ Order {order_id} moved from active to completed ({order.get('type', 'N/A')})")
                            else:
                                logger.debug(f"✅ Order completed: {order_id} ({order.get('type', 'N/A')}) (was not in active_orders)")
                        else:
                            logger.warning(f"⚠️ Completed order without orderId: {order}")
                else:
                    logger.warning(f"⚠️ [STUB] Unexpected message type: {type(message)}")
                
                self.last_completed_update = datetime.now(timezone.utc)
                logger.info(f"✅ [STUB] Completed orders updated from {topic}")
                
        except Exception as e:
            logger.error(f"❌ [STUB] Error processing completed order message from {topic}: {e}")

    def process_fts_state_message(self, topic: str, message: Any, meta: Dict[str, Any]) -> None:
        """
        Verarbeitet FTS State Messages für Transport-Updates
        
        Args:
            topic: MQTT Topic (z.B. fts/v1/ff/5iO4/state)
            message: Message Payload (bereits validiert)
            meta: Message Metadata
        """
        try:
            logger.info(f"🚛 [STUB] Processing FTS state message from {topic}")
            logger.debug(f"📦 FTS State Payload: {message}")
            
            # TODO: Implement FTS state processing
            # - Extract orderId from message
            # - Update transport steps in production plan
            # - Update AGV navigation steps
            
            logger.info(f"✅ [STUB] FTS state message processed from {topic}")
            
        except Exception as e:
            logger.error(f"❌ [STUB] Error processing FTS state message from {topic}: {e}")

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

    def process_module_state_message(self, topic: str, message: Any, meta: Dict[str, Any]) -> None:
        """
        Verarbeitet Module State Messages für HBW, AIQS, DPS Status-Updates
        
        Args:
            topic: MQTT Topic (z.B. module/v1/ff/SVR3QA0022/state)
            message: Message Payload (bereits validiert)
            meta: Message Metadata
        """
        try:
            logger.info(f"🏭 [STUB] Processing module state message from {topic}")
            logger.debug(f"📦 Module State Payload: {message}")
            
            # TODO: Implement module state processing
            # - Extract orderId from message
            # - Update module-specific steps in production plan
            # - Update HBW PICK/DROP, AIQS PICK/AIQS/DROP, DPS DROP steps
            # - Update global order status when all steps completed
            
            logger.info(f"✅ [STUB] Module state message processed from {topic}")
            
        except Exception as e:
            logger.error(f"❌ [STUB] Error processing module state message from {topic}: {e}")

    def get_active_orders(self) -> List[Dict[str, Any]]:
        """
        Gibt die aktiven Orders zurück (als Liste für UI-Kompatibilität)
        
        Returns:
            Liste von aktiven Orders
        """
        with self._lock:
            orders_list = list(self.active_orders.values())
            logger.debug(f"📋 Getting active orders: {len(orders_list)} orders")
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
                "stub_mode": False  # Order-ID-basierte Implementierung
            }

    def _load_production_workflows(self) -> Dict[str, Any]:
        """Lädt Production Workflows aus Konfiguration (lazy loading)"""
        if self._production_workflows is None:
            try:
                config_path = Path(__file__).parent.parent / "config" / "ccu" / "production_workflows.json"
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._production_workflows = json.load(f)
                logger.debug("📋 Production workflows loaded from config")
            except Exception as e:
                logger.warning(f"⚠️ Could not load production workflows: {e}")
                self._production_workflows = {}
        return self._production_workflows

    def _load_shopfloor_layout(self) -> Dict[str, Any]:
        """Lädt Shopfloor Layout aus Konfiguration (lazy loading)"""
        if self._shopfloor_layout is None:
            try:
                config_path = Path(__file__).parent.parent / "config" / "ccu" / "shopfloor_layout.json"
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._shopfloor_layout = json.load(f)
                logger.debug("🏭 Shopfloor layout loaded from config")
            except Exception as e:
                logger.warning(f"⚠️ Could not load shopfloor layout: {e}")
                self._shopfloor_layout = {}
        return self._shopfloor_layout

    def _generate_complete_production_plan(self, workpiece_type: str) -> List[Dict[str, Any]]:
        """
        Generiert den FESTEN Produktionsplan basierend auf Workpiece Type
        
        Fester Plan: HBW → MILL/DRILL → AIQS → DPS
        Pro Station: PICK → PROCESS → DROP
        
        Args:
            workpiece_type: RED, BLUE, WHITE
            
        Returns:
            Liste aller Production Steps (fester Plan)
        """
        workflows = self._load_production_workflows()
        
        # Workflow für Workpiece Type laden
        workflow = workflows.get(workpiece_type.upper(), {})
        steps = workflow.get('steps', [])
        
        if not steps:
            logger.warning(f"⚠️ No workflow found for workpiece type: {workpiece_type}")
            return []
        
        complete_plan = []
        
        # FESTER PRODUKTIONSPLAN (immer gleich):
        # 1. HBW → PICK
        complete_plan.append({
            "id": "hbw_pick",
            "type": "MANUFACTURE",
            "state": "PENDING",
            "command": "PICK",
            "moduleType": "HBW",
            "source": "HBW",
            "target": "HBW",
            "description": "High-Bay Warehouse : PICK"
        })
        
        # 2. Für jeden Processing-Step (MILL, DRILL, AIQS)
        for step_module in steps:
            # Navigation zu Station
            complete_plan.append({
                "id": f"nav_to_{step_module.lower()}",
                "type": "NAVIGATION",
                "state": "PENDING",
                "source": "HBW" if step_module == steps[0] else steps[steps.index(step_module)-1],
                "target": step_module,
                "description": f"Automated Guided Vehicle (AGV) > {step_module}"
            })
            
            # PICK an Station
            complete_plan.append({
                "id": f"{step_module.lower()}_pick",
                "type": "MANUFACTURE",
                "state": "PENDING",
                "command": "PICK",
                "moduleType": step_module,
                "description": f"{step_module} : PICK"
            })
            
            # PROCESS an Station
            complete_plan.append({
                "id": f"{step_module.lower()}_process",
                "type": "MANUFACTURE",
                "state": "PENDING",
                "command": step_module,
                "moduleType": step_module,
                "description": f"{step_module} : {step_module}"
            })
            
            # DROP an Station
            complete_plan.append({
                "id": f"{step_module.lower()}_drop",
                "type": "MANUFACTURE",
                "state": "PENDING",
                "command": "DROP",
                "moduleType": step_module,
                "description": f"{step_module} : DROP"
            })
        
        # 3. Navigation zu DPS (Delivery Station)
        last_station = steps[-1] if steps else "HBW"
        complete_plan.append({
            "id": "nav_to_dps",
            "type": "NAVIGATION",
            "state": "PENDING",
            "source": last_station,
            "target": "DPS",
            "description": "Automated Guided Vehicle (AGV) > DPS"
        })
        
        # 4. DPS → DROP (Final)
        complete_plan.append({
            "id": "dps_drop",
            "type": "MANUFACTURE",
            "state": "PENDING",
            "command": "DROP",
            "moduleType": "DPS",
            "description": "DPS : DROP"
        })
        
        logger.info(f"📋 Generated FIXED production plan for {workpiece_type}: {len(complete_plan)} steps")
        return complete_plan

    def _merge_mqtt_status_with_plan(self, complete_plan: List[Dict[str, Any]], mqtt_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mergt MQTT-Status mit kompletten Produktionsplan
        
        Intelligentes Matching nach Inhalt (source, target, moduleType, command)
        
        Args:
            complete_plan: Kompletter Produktionsplan
            mqtt_steps: Aktuelle Steps aus MQTT
            
        Returns:
            Merged Plan mit aktuellem Status
        """
        merged_plan = []
        used_mqtt_indices = set()  # Verhindert doppelte Verwendung
        
        for plan_step in complete_plan:
            merged_step = plan_step.copy()
            matched_mqtt_step = None
            
            # Intelligentes Matching nach Inhalt
            for i, mqtt_step in enumerate(mqtt_steps):
                if i in used_mqtt_indices:
                    continue
                
                # Match-Kriterien
                plan_type = plan_step.get('type')
                plan_module = plan_step.get('moduleType')
                plan_command = plan_step.get('command')
                plan_source = plan_step.get('source')
                plan_target = plan_step.get('target')
                
                mqtt_type = mqtt_step.get('type')
                mqtt_module = mqtt_step.get('moduleType')
                mqtt_command = mqtt_step.get('command')
                mqtt_source = mqtt_step.get('source')
                mqtt_target = mqtt_step.get('target')
                
                # Exakte Matches
                if (plan_type == mqtt_type and 
                    plan_module == mqtt_module and 
                    plan_command == mqtt_command and
                    plan_source == mqtt_source and
                    plan_target == mqtt_target):
                    matched_mqtt_step = mqtt_step
                    used_mqtt_indices.add(i)
                    logger.debug(f"📋 EXACT MATCH: {plan_step.get('id')} ← {mqtt_step.get('id')} ({mqtt_step.get('state')})")
                    break
                
                # Fallback: Module + Command Match
                elif (plan_type == mqtt_type and 
                      plan_module == mqtt_module and 
                      plan_command == mqtt_command):
                    matched_mqtt_step = mqtt_step
                    used_mqtt_indices.add(i)
                    logger.debug(f"📋 MODULE+COMMAND MATCH: {plan_step.get('id')} ← {mqtt_step.get('id')} ({mqtt_step.get('state')})")
                    break
            
            # MQTT-Status übernehmen wenn Match gefunden
            if matched_mqtt_step:
                merged_step.update({
                    'state': matched_mqtt_step.get('state', 'PENDING'),
                    'startedAt': matched_mqtt_step.get('startedAt'),
                    'stoppedAt': matched_mqtt_step.get('stoppedAt'),
                    'serialNumber': matched_mqtt_step.get('serialNumber'),
                    'dependentActionId': matched_mqtt_step.get('dependentActionId'),
                    # Original MQTT-Daten für Debugging
                    'mqtt_id': matched_mqtt_step.get('id'),
                    'mqtt_source': matched_mqtt_step.get('source'),
                    'mqtt_target': matched_mqtt_step.get('target'),
                    'mqtt_moduleType': matched_mqtt_step.get('moduleType'),
                    'mqtt_command': matched_mqtt_step.get('command')
                })
            else:
                logger.debug(f"📋 NO MATCH: {plan_step.get('id')} - PENDING (no MQTT data)")
            
            merged_plan.append(merged_step)
        
        matched_count = len(used_mqtt_indices)
        logger.info(f"📋 Merged plan: {len(merged_plan)} steps ({matched_count}/{len(mqtt_steps)} MQTT steps matched)")
        return merged_plan

    def get_complete_production_plan(self, order: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Gibt den KOMPLETTEN Produktionsplan für eine Order zurück
        
        PRODUCTION Orders: HBW → MILL/DRILL → AIQS → DPS
        STORAGE Orders: START → DPS → HBW (nur FTS Transport!)
        
        Args:
            order: Order-Dict mit workpiece type und orderType
            
        Returns:
            Kompletter Produktionsplan mit aktuellem Status
        """
        workpiece_type = order.get('type', 'RED')
        order_type = order.get('orderType', 'PRODUCTION')
        mqtt_steps = order.get('productionSteps', [])
        
        # Unterschiedliche Pläne für PRODUCTION vs STORAGE
        if order_type == 'STORAGE':
            # STORAGE: Nur DPS → HBW (direkt aus MQTT-Steps)
            # Kein fester Plan nötig, MQTT hat bereits alle Steps
            merged_plan = mqtt_steps
            logger.info(f"📦 Storage plan for {workpiece_type}: {len(merged_plan)} steps (direkt aus MQTT)")
        else:
            # PRODUCTION: Kompletten Plan generieren
            complete_plan = self._generate_complete_production_plan(workpiece_type)
            
            # MQTT-Status überlagern
            merged_plan = self._merge_mqtt_status_with_plan(complete_plan, mqtt_steps)
            
            logger.info(f"🏭 Production plan for {workpiece_type}: {len(merged_plan)} steps (MQTT: {len(mqtt_steps)})")
        
        return merged_plan

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


def get_production_order_manager() -> ProductionOrderManager:
    """
    Get Production Order Manager singleton instance - EXAKT wie Order Manager
    
    Returns:
        ProductionOrderManager: Production Order Manager Instanz
    """
    global _production_order_manager_instance
    if _production_order_manager_instance is None:
        _production_order_manager_instance = ProductionOrderManager()
        logger.info("🏗️ Production Order Manager STUB singleton created")
    return _production_order_manager_instance

