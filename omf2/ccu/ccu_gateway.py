#!/usr/bin/env python3
"""
CCU Gateway - Fassade für CCU Business-Operationen mit Topic-Routing
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union
from omf2.registry.manager.registry_manager import get_registry_manager
from omf2.common.message_manager import get_ccu_message_manager
from omf2.common.topic_manager import get_ccu_topic_manager
from omf2.common.logger import get_logger
from omf2.ccu.order_manager import get_order_manager
from omf2.ccu.production_order_manager import get_production_order_manager

logger = get_logger("omf2.ccu.ccu_gateway")


class CcuGateway:
    """
    Gateway für CCU-spezifische Business-Operationen mit Topic-Routing
    
    Verantwortlichkeiten:
    - Empfängt ALLE MQTT-Nachrichten vom ccu_mqtt_client
    - Routet Nachrichten anhand von Topic-Präfixen an die zuständigen Manager
    - Nutzt Registry Manager und Topic-Schema-Payload Beziehung für CCU-Operationen
    - Stellt Methoden für die UI bereit
    """
    
    def __init__(self, mqtt_client=None, **kwargs):
        """
        Initialisiert CCU Gateway
        
        Args:
            mqtt_client: MQTT-Client für CCU
        """
        self.mqtt_client = mqtt_client
        self.registry_manager = get_registry_manager()
        
        # Initialize Message Manager
        self.message_manager = get_ccu_message_manager(
            registry_manager=self.registry_manager,
            mqtt_client=self.mqtt_client
        )
        
        # Initialize Topic Manager
        self.topic_manager = get_ccu_topic_manager(
            registry_manager=self.registry_manager
        )
        
        # Explizite Topic-Listen für Manager-Routing
        # Diese Listen definieren, welche Topics an welchen Manager weitergeleitet werden
        self.sensor_topics = {
            '/j1/txt/1/i/bme680',  # BME680 Sensor-Daten
            '/j1/txt/1/i/ldr',     # LDR Sensor-Daten
            '/j1/txt/1/i/cam'      # Camera-Daten
        }
        
        # Module Topics: Präfix-basierte Matching für dynamische Module-IDs
        self.module_topic_prefixes = [
            'module/v1/ff/',       # Direkte Module Topics
            'fts/v1/ff/',          # FTS Topics
            'ccu/pairing/state'    # CCU Pairing State (für globale Status-Updates)
        ]

        # Order Topics: Set-basiertes Lookup für Order Manager (Inventory)
        self.order_topics = {
            '/j1/txt/1/f/i/stock'       # HBW Lager-info (INPUT TO TXT)
        }
        
        # Production Order Topics: Set-basiertes Lookup für Production Order Manager
        self.production_order_topics = {
            'ccu/order/request',        # Order Request
            'ccu/order/active',         # Active Orders
            'ccu/order/completed',      # Completed Orders
            'ccu/order/response',       # CCU Bestätigung für Production Orders
            'fts/v1/ff/5iO4/state',     # FTS Transport-Updates für Production Orders
            'module/v1/ff/SVR3QA0022/state',  # HBW Status für PICK/DROP
            'module/v1/ff/SVR4H76530/state',  # AIQS Status für PICK/AIQS/DROP
            'module/v1/ff/SVR4H73275/state'   # DPS Status für DROP
        }
        
        # Initialisiere Manager (Lazy Loading)
        self._sensor_manager = None
        self._module_manager = None
        self._order_manager = None
        self._production_order_manager = None
        
        logger.info("🏗️ CcuGateway initialized with Topic-Routing")
    
    def _get_sensor_manager(self):
        """Lazy Loading für SensorManager (Singleton)"""
        if self._sensor_manager is None:
            from omf2.ccu.sensor_manager import get_ccu_sensor_manager
            self._sensor_manager = get_ccu_sensor_manager()
        return self._sensor_manager
    
    def _get_module_manager(self):
        """Lazy Loading für ModuleManager (Singleton)"""
        if self._module_manager is None:
            from omf2.ccu.module_manager import get_ccu_module_manager
            self._module_manager = get_ccu_module_manager()
        return self._module_manager
    
    def _get_order_manager(self):
        """Lazy Loading für OrderManager (Singleton) - wie Sensor Manager"""
        if self._order_manager is None:
            try:
                from omf2.ccu.order_manager import get_order_manager
                self._order_manager = get_order_manager()
                logger.info("🏗️ Order Manager initialized via Gateway")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Order Manager: {e}")
                # Fallback: Return None to avoid blocking
                return None
        return self._order_manager
    
    def _get_production_order_manager(self):
        """Lazy Loading für ProductionOrderManager (Singleton) - wie Order Manager"""
        if self._production_order_manager is None:
            try:
                from omf2.ccu.production_order_manager import get_production_order_manager
                self._production_order_manager = get_production_order_manager()
                logger.info("🏗️ Production Order Manager initialized via Gateway")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Production Order Manager: {e}")
                # Fallback: Return None to avoid blocking
                return None
        return self._production_order_manager
    
    def on_mqtt_message(self, topic: str, message: Union[Dict, List, str], meta: Optional[Dict] = None):
        """
        Gateway-Routing mit Schema-Validierung für CCU Messages
        
        Diese Methode wird vom ccu_mqtt_client im on_message Callback aufgerufen.
        Sie implementiert das Gateway-Pattern für Topic-Routing mit Schema-Validierung.
        
        Args:
            topic: MQTT Topic (String)
            message: Payload-Daten (Dict, List, str) - NIE raw bytes!
            meta: Metadaten (timestamp, raw, qos, retain)
        
        Returns:
            bool: True wenn Message verarbeitet wurde, False bei Fehler
        """
        try:
            logger.debug(f"🔀 CCU Gateway processing message for topic: {topic}")
            
            # 1. Schema aus Registry holen
            schema = self.registry_manager.get_topic_schema(topic)
            
            # 2. Schema-Validierung über MessageManager (zentrale Validierung)
            if schema:
                logger.debug(f"📋 Found schema for topic {topic}, validating payload via MessageManager")
                validation_result = self.message_manager.validate_message(topic, message)
                if validation_result.get("errors"):
                    logger.warning(f"⚠️ Message rejected due to schema validation failure: {topic}")
                    logger.warning(f"   Validation errors: {validation_result['errors']}")
                    return False  # Validierung fehlgeschlagen
                validated_message = message  # Message ist validiert
            else:
                validated_message = message
                logger.debug(f"📋 No schema for topic {topic}, skipping validation")
            
            # 3. Gateway-Routing mit validierter Message
            logger.debug(f"📤 Routing validated message to managers: {topic}")
            return self._route_ccu_message(topic, validated_message, meta)
            
        except Exception as e:
            logger.error(f"❌ CCU Gateway processing failed for topic {topic}: {e}")
            return False
    
    def _route_ccu_message(self, topic: str, message: Union[Dict, List, str], meta: Optional[Dict] = None) -> bool:
        """
        CCU Message-Routing - Routet Messages an zuständige Manager
        
        Args:
            topic: MQTT Topic
            message: Validierte Message
            meta: Metadaten
        
        Returns:
            True wenn Message verarbeitet wurde
        """
        try:
            logger.debug(f"📋 CCU Gateway routing message: {topic}")
            
            # Routing 1: Sensor Topics (Set-basiertes Lookup)
            if topic in self.sensor_topics:
                logger.debug(f"📡 Routing to sensor_manager: {topic}")
                sensor_manager = self._get_sensor_manager()
                sensor_manager.process_sensor_message(topic, message, meta)
                return True
            
            # Routing 2: Module Topics (Präfix-basiertes Matching) - REAKTIVIERT
            for prefix in self.module_topic_prefixes:
                if topic.startswith(prefix):
                    logger.debug(f"🏭 Routing to module_manager: {topic}")
                    module_manager = self._get_module_manager()
                    if module_manager:
                        module_manager.process_module_message(topic, message, meta)
                    return True
            
            # Routing 3: Order Topics (Set-basiertes Lookup) - EXAKT wie Sensor Manager
            if topic in self.order_topics:
                logger.debug(f"📦 Routing to order_manager: {topic}")
                order_manager = self._get_order_manager()
                if order_manager:
                    order_manager.process_stock_message(topic, message, meta)
                else:
                    logger.warning(f"⚠️ Order Manager not available for topic: {topic}")
                return True
            
            # Routing 4: Production Order Topics (Set-basiertes Lookup)
            if topic in self.production_order_topics:
                logger.debug(f"📋 Routing to production_order_manager: {topic}")
                production_order_manager = self._get_production_order_manager()
                if production_order_manager:
                    # Route basierend auf Topic-Typ
                    if topic == 'ccu/order/active':
                        production_order_manager.process_active_order_message(topic, message, meta)
                    elif topic == 'ccu/order/completed':
                        production_order_manager.process_completed_order_message(topic, message, meta)
                    elif topic == 'ccu/order/request':
                        # Request wird nur geloggt (für später)
                        logger.info(f"📋 Order request received: {topic}")
                    elif topic == 'fts/v1/ff/5iO4/state':
                        production_order_manager.process_fts_state_message(topic, message, meta)
                    elif topic == 'ccu/order/response':
                        production_order_manager.process_ccu_response_message(topic, message, meta)
                    elif topic in ['module/v1/ff/SVR3QA0022/state', 'module/v1/ff/SVR4H76530/state', 'module/v1/ff/SVR4H73275/state']:
                        production_order_manager.process_module_state_message(topic, message, meta)
                else:
                    logger.warning(f"⚠️ Production Order Manager not available for topic: {topic}")
                return True
            
            # Unbekanntes Topic: Nur Debug-Logging
            logger.debug(f"❓ No routing for topic: {topic}")
            return True  # Nicht als Fehler behandeln
            
        except Exception as e:
            logger.error(f"❌ CCU message routing failed for {topic}: {e}")
            return False
    
    def publish_message(self, topic: str, message: Dict[str, Any], qos: int = 1, retain: bool = False) -> bool:
        """
        Message über MQTT publizieren
        
        Args:
            topic: MQTT Topic
            message: Message Payload
            qos: Quality of Service Level (0, 1, 2)
            retain: Retain Flag
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            if not self.mqtt_client:
                logger.warning("⚠️ No MQTT client available")
                return False
            
            # MQTT-Client publish nutzen (mit QoS und Retain)
            success = self.mqtt_client.publish(
                topic=topic,
                message=message,
                qos=qos,
                retain=retain
            )
            
            if success:
                # Log detailed message information
                payload_str = json.dumps(message, indent=2) if isinstance(message, dict) else str(message)
                logger.info(f"📤 Published message to {topic} (QoS: {qos}, Retain: {retain})")
                logger.info(f"📦 Payload: {payload_str}")
                # TODO: Implement message logging from registry manager
                logger.info(f"📤 Message logged: {topic}")
            else:
                logger.error(f"❌ Failed to publish message to {topic}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Publish message failed for topic {topic}: {e}")
            return False
    
    def get_all_topics(self) -> List[str]:
        """
        Alle CCU Topics aus Registry abrufen - Delegiert an Topic Manager
        
        Returns:
            Liste aller CCU Topics
        """
        return self.topic_manager.get_domain_topics("ccu")
    
    def get_all_message_buffers(self) -> Dict[str, Any]:
        """
        Alle Message-Buffer abrufen - Delegiert an Message Manager
        
        Returns:
            Dict mit allen CCU Message-Buffers
        """
        return self.message_manager.get_all_message_buffers()
    
    def get_message_buffers(self) -> Dict[str, Dict]:
        """
        Alle Message Buffers abrufen - Delegiert an Message Manager
        
        Returns:
            Dict mit allen Message Buffers
        """
        return self.message_manager.get_all_message_buffers()
    
    def clear_message_history(self) -> bool:
        """
        Komplette Message-Historie löschen - Delegiert an Message Manager
        
        Returns:
            True wenn erfolgreich
        """
        return self.message_manager.clear_message_history()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        MQTT Connection Info abrufen
        
        Returns:
            Dict mit Connection Info (client_id, connected, environment, etc.)
        """
        try:
            if not self.mqtt_client:
                logger.warning("⚠️ No MQTT client available")
                return {
                    "connected": False,
                    "client_id": "unknown",
                    "environment": "unknown"
                }
            
            conn_info = self.mqtt_client.get_connection_info()
            logger.debug(f"🔌 Retrieved connection info: {conn_info}")
            return conn_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get connection info: {e}")
            return {
                "connected": False,
                "client_id": "unknown",
                "environment": "unknown"
            }
    
    def is_connected(self) -> bool:
        """
        MQTT Connection Status prüfen
        
        Returns:
            True wenn verbunden, False wenn nicht
        """
        try:
            if not self.mqtt_client:
                return False
            
            return self.mqtt_client.connected
            
        except Exception as e:
            logger.error(f"❌ Failed to check connection status: {e}")
            return False
    
    def reset_factory(self) -> bool:
        """
        Factory Reset ausführen - Schema-driven Message Generation
        
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            topic = "ccu/set/reset"
            # Schema-driven Message Generation
            message = self.message_manager.generate_message(topic, {"reset": True})
            
            if message:
                success = self.publish_message(topic, message)
                if success:
                    logger.info("🏭 Factory reset executed")
                    return True
            else:
                logger.warning(f"⚠️ Failed to generate message for {topic}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Factory Reset failed: {e}")
            return False
    
    def send_global_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """
        Global Command senden - Schema-driven Message Generation
        
        Args:
            command: Command-String
            params: Zusätzliche Parameter
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            topic = "ccu/global"
            # Schema-driven Message Generation
            message = self.message_manager.generate_message(topic, {
                "command": command,
                "params": params or {}
            })
            
            if message:
                success = self.publish_message(topic, message)
                if success:
                    logger.info(f"📤 Global Command sent: {command}")
                    return True
            else:
                logger.warning(f"⚠️ Failed to generate message for {topic}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Global Command failed: {e}")
            return False
    
    def get_ccu_state(self) -> Optional[Dict]:
        """
        CCU State abrufen
        
        Returns:
            CCU State Dict oder None
        """
        try:
            # TODO: MQTT-Client Integration implementieren
            # topic = "ccu/state"
            # state = self.mqtt_client.get_buffer(topic)
            # return state
            
            logger.info("📊 CCU State requested (TODO: MQTT integration)")
            return {"status": "idle", "timestamp": "2025-09-28T16:24:55Z"}
            
        except Exception as e:
            logger.error(f"❌ CCU State retrieval failed: {e}")
            return None
    
    def get_module_states(self) -> List[Dict]:
        """
        Alle Module States abrufen
        
        Returns:
            Liste der Module States
        """
        try:
            # TODO: MQTT-Client Integration implementieren
            # topics = self.registry_manager.get_topic_patterns("module/v1/ff/*/state")
            # states = []
            # for topic in topics:
            #     state = self.mqtt_client.get_buffer(topic)
            #     if state:
            #         states.append(state)
            # return states
            
            logger.info("📊 Module States requested (TODO: MQTT integration)")
            return []
            
        except Exception as e:
            logger.error(f"❌ Module States retrieval failed: {e}")
            return []
    
    def send_order_request(self, order_data: Dict[str, Any]) -> bool:
        """
        Order Request senden
        
        Args:
            order_data: Order-Daten
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            # TODO: MQTT-Client Integration implementieren
            # topic = "ccu/order/request"
            # message = self.registry_manager.render_message(topic, order_data)
            # if message:
            #     self.mqtt_client.publish(topic, message)
            #     return True
            
            logger.info(f"📤 Order Request: {order_data} (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Order Request failed: {e}")
            return False
    
    def get_published_topics(self) -> List[str]:
        """
        CCU Published Topics aus Registry abrufen - Delegiert an Topic Manager
        
        Returns:
            Liste der Published Topics
        """
        return self.topic_manager.get_published_topics("ccu")
    
    def get_subscribed_topics(self) -> List[str]:
        """
        CCU Subscribed Topics aus Registry abrufen - Delegiert an Topic Manager
        
        Returns:
            Liste der Subscribed Topics
        """
        return self.topic_manager.get_subscribed_topics("ccu")
    
    # ===== New Manager-based Functionality =====
    
    def generate_message(self, topic: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Message für Topic generieren - Delegiert an Message Manager
        
        Args:
            topic: MQTT Topic
            params: Parameter für Message-Generierung
            
        Returns:
            Generierte Message oder None
        """
        return self.message_manager.generate_message(topic, params)
    
    def validate_message(self, topic: str, message: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Message gegen Schema validieren - Delegiert an Message Manager
        
        Args:
            topic: MQTT Topic
            message: Message zum Validieren
            
        Returns:
            {"errors": [...], "warnings": [...]}
        """
        return self.message_manager.validate_message(topic, message)
    
    def get_topic_schemas(self) -> Dict[str, Dict]:
        """
        CCU Topic-Schema Mappings abrufen - Delegiert an Topic Manager
        
        Returns:
            Dict mit Topic-Schema Mappings
        """
        return self.topic_manager.get_topic_schemas()
    
    def analyze_topic(self, topic: str) -> Dict[str, Any]:
        """
        CCU Topic-Analyse durchführen - Delegiert an Topic Manager
        
        Args:
            topic: MQTT Topic
            
        Returns:
            Dict mit Topic-Analyse-Informationen
        """
        return self.topic_manager.analyze_topic(topic)
    
    def get_topics_by_pattern(self, pattern: str) -> List[str]:
        """
        CCU Topics nach Pattern filtern - Delegiert an Topic Manager
        
        Args:
            pattern: Topic-Pattern (z.B. "ccu/*", "*/state")
            
        Returns:
            Liste der passenden Topics
        """
        return self.topic_manager.get_topics_by_pattern(pattern)
    
    # Order Manager Methods
    def get_inventory_status(self) -> Dict[str, Any]:
        """
        Lagerbestand-Status abrufen - Non-Blocking
        
        Returns:
            Dict mit Lagerbestand-Informationen
        """
        # Direkter Zugriff auf Order Manager (wie Sensor Manager)
        try:
            order_manager = self._get_order_manager()
            if order_manager is None:
                logger.warning("⚠️ Order Manager not available, using fallback data")
                raise Exception("Order Manager not available")
            
            inventory_status = order_manager.get_inventory_status()
            logger.debug(f"📦 Returning real inventory status: {inventory_status}")
            return inventory_status
        except Exception as e:
            logger.error(f"❌ Error getting inventory status: {e}")
            # Fallback: Placeholder-Daten bei Fehler
            return {
                "inventory": {
                    "A1": None, "A2": None, "A3": None,
                    "B1": None, "B2": None, "B3": None,
                    "C1": None, "C2": None, "C3": None
                },
                "last_update": None,
                "available": {"RED": 0, "BLUE": 0, "WHITE": 0},
                "need": {"RED": 3, "BLUE": 3, "WHITE": 3}
            }
    
    def get_available_workpieces(self) -> Dict[str, int]:
        """
        Verfügbare Werkstücke abrufen - Non-Blocking
        
        Returns:
            Dict mit Anzahl pro Werkstück-Typ
        """
        # Direkter Zugriff auf Order Manager (wie Sensor Manager)
        try:
            order_manager = self._get_order_manager()
            return order_manager.get_available_workpieces()
        except Exception as e:
            logger.error(f"❌ Error getting available workpieces: {e}")
            return {"RED": 0, "BLUE": 0, "WHITE": 0}
    
    def get_workpiece_need(self) -> Dict[str, int]:
        """
        Werkstück-Bedarf abrufen - Non-Blocking
        
        Returns:
            Dict mit Bedarf pro Werkstück-Typ
        """
        # Direkter Zugriff auf Order Manager (wie Sensor Manager)
        try:
            order_manager = self._get_order_manager()
            return order_manager.get_workpiece_need()
        except Exception as e:
            logger.error(f"❌ Error getting workpiece need: {e}")
            return {"RED": 3, "BLUE": 3, "WHITE": 3}
    
    def send_customer_order(self, workpiece_type: str) -> bool:
        """
        Kundenauftrag senden
        
        Args:
            workpiece_type: RED, BLUE, oder WHITE
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        order_manager = get_order_manager()
        return order_manager.send_customer_order(workpiece_type)
    
    def send_raw_material_order(self, workpiece_type: str) -> bool:
        """
        Rohmaterial-Bestellung senden
        
        Args:
            workpiece_type: RED, BLUE, oder WHITE
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        order_manager = get_order_manager()
        return order_manager.send_raw_material_order(workpiece_type)