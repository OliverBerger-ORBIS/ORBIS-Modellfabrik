#!/usr/bin/env python3
"""
CCU Gateway - Fassade für CCU Business-Operationen
"""

import logging
import json
from typing import Dict, List, Optional, Any
from omf2.registry.manager.registry_manager import get_registry_manager
from omf2.common.message_manager import get_ccu_message_manager
from omf2.common.topic_manager import get_ccu_topic_manager

logger = logging.getLogger(__name__)


class CcuGateway:
    """
    Gateway für CCU-spezifische Business-Operationen
    
    Nutzt Registry Manager und Topic-Schema-Payload Beziehung für CCU-Operationen.
    Stellt Methoden für die UI bereit.
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
        
        # Setup Manager Integration (State-Holder Pattern)
        self._setup_manager_integration()
        
        logger.info("🏗️ CcuGateway initialized")
    
    def _setup_manager_integration(self):
        """Setup Manager Integration with MQTT Client callbacks"""
        try:
            # Import managers
            from omf2.ccu.sensor_manager import get_ccu_sensor_manager
            from omf2.ccu.module_manager import get_ccu_module_manager
            
            # Get manager instances
            sensor_manager = get_ccu_sensor_manager()
            module_manager = get_ccu_module_manager()
            
            # Register callbacks with MQTT Client
            if self.mqtt_client:
                self.mqtt_client.register_message_callback(sensor_manager.process_sensor_message)
                self.mqtt_client.register_message_callback(module_manager.process_module_message)
                logger.info("✅ Manager integration setup complete (callbacks registered)")
            else:
                logger.warning("⚠️ MQTT Client not available for manager integration")
                
        except Exception as e:
            logger.error(f"❌ Failed to setup manager integration: {e}")
    
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
            
            # MQTT-Client publish_message nutzen (mit QoS und Retain)
            success = self.mqtt_client.publish_message(
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