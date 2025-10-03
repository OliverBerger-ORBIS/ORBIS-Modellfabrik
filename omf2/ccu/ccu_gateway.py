#!/usr/bin/env python3
"""
CCU Gateway - Fassade für CCU Business-Operationen
"""

import logging
import json
from typing import Dict, List, Optional, Any
from omf2.registry.manager.registry_manager import get_registry_manager

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
        
        logger.info("🏗️ CcuGateway initialized")
    
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
        Alle CCU Topics aus Registry abrufen
        
        Returns:
            Liste aller CCU Topics
        """
        try:
            all_topics = []
            
            # CCU Topics aus Registry Manager sammeln
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            ccu_client = mqtt_clients.get('ccu_mqtt_client', {})
            subscribed_topics = ccu_client.get('subscribed_topics', [])
            
            for topic_info in subscribed_topics:
                if isinstance(topic_info, dict):
                    topic = topic_info.get('topic', '')
                else:
                    topic = str(topic_info)
                if topic:
                    all_topics.append(topic)
            
            logger.debug(f"📡 Retrieved {len(all_topics)} CCU topics from registry")
            return all_topics
            
        except Exception as e:
            logger.error(f"❌ Failed to get CCU topics: {e}")
            return []
    
    def get_all_message_buffers(self) -> Dict[str, Any]:
        """
        Alle Message-Buffer abrufen - CCU-spezifische Buffers
        
        Returns:
            Dict mit allen CCU Message-Buffers
        """
        try:
            if not self.mqtt_client:
                logger.warning("⚠️ No MQTT client available")
                return {}
            
            # Get all buffers from CCU MQTT client
            all_buffers = self.mqtt_client.get_all_buffers()
            logger.info(f"📊 Retrieved {len(all_buffers)} CCU message buffers")
            return all_buffers
            
        except Exception as e:
            logger.error(f"❌ Failed to get CCU message buffers: {e}")
            return {}
    
    def get_message_buffers(self) -> Dict[str, Dict]:
        """
        Alle Message Buffers abrufen
        
        Returns:
            Dict mit allen Message Buffers
        """
        try:
            if not self.mqtt_client:
                logger.warning("⚠️ No MQTT client available")
                return {}
            
            buffers = self.mqtt_client.get_all_buffers()
            logger.debug(f"📊 Retrieved {len(buffers)} message buffers")
            return buffers
            
        except Exception as e:
            logger.error(f"❌ Failed to get message buffers: {e}")
            return {}
    
    def clear_message_history(self) -> bool:
        """
        Komplette Message-Historie löschen
        
        Returns:
            True wenn erfolgreich
        """
        try:
            if not self.mqtt_client:
                logger.warning("⚠️ No MQTT client available")
                return False
            
            # MQTT-Client hat clear_buffers() Methode
            self.mqtt_client.clear_buffers()
            logger.info("🗑️ Message history cleared")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to clear message history: {e}")
            return False
    
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
        Factory Reset ausführen
        
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            # Registry v2 Integration: Topic aus Registry laden
            topic = "ccu/set/reset"
            topic_config = self.registry_manager.get_topic_config(topic)
            
            if topic_config:
                # Message aus Template rendern
                # TODO: Implement message rendering from registry manager
                message = {"reset": True}
                if message:
                    # MQTT-Client Integration
                    success = self.publish_message(topic, message)
                    if success:
                        logger.info("🏭 Factory reset executed")
                        return True
            else:
                logger.warning(f"⚠️ No topic configuration found for {topic}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Factory Reset failed: {e}")
            return False
    
    def send_global_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """
        Global Command senden
        
        Args:
            command: Command-String
            params: Zusätzliche Parameter
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            # Registry v2 Integration: Topic aus Registry laden
            topic = "ccu/global"
            topic_config = self.registry_manager.get_topic_config(topic)
            
            if topic_config:
                # Message aus Template rendern
                # TODO: Implement message rendering from registry manager
                message = {
                    "command": command,
                    "params": params or {}
                }
                if message:
                    # TODO: MQTT-Client Integration implementieren
                    # qos = topic_config.get('qos', 1)
                    # retain = topic_config.get('retain', False)
                    # self.mqtt_client.publish(topic, message, qos=qos, retain=retain)
                    
                    logger.info(f"📤 Global Command message rendered: {message}")
                    return True
            else:
                logger.warning(f"⚠️ No topic configuration found for {topic}")
            
            logger.info(f"📤 Global Command: {command} (TODO: MQTT integration)")
            return True
            
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
        CCU Published Topics aus Registry abrufen
        
        Returns:
            Liste der Published Topics
        """
        try:
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            ccu_client = mqtt_clients.get('mqtt_clients', {}).get('ccu_mqtt_client', {})
            return ccu_client.get('published_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to get CCU published topics: {e}")
            return []
    
    def get_subscribed_topics(self) -> List[str]:
        """
        CCU Subscribed Topics aus Registry abrufen
        
        Returns:
            Liste der Subscribed Topics
        """
        try:
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            ccu_client = mqtt_clients.get('mqtt_clients', {}).get('ccu_mqtt_client', {})
            return ccu_client.get('subscribed_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to get CCU subscribed topics: {e}")
            return []