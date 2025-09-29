#!/usr/bin/env python3
"""
CCU Gateway - Fassade für CCU Business-Operationen
"""

import logging
from typing import Dict, List, Optional, Any
from omf2.common.message_templates import get_message_templates

logger = logging.getLogger(__name__)


class CcuGateway:
    """
    Gateway für CCU-spezifische Business-Operationen
    
    Nutzt MessageTemplates und MQTT-Client für CCU-Operationen.
    Stellt Methoden für die UI bereit.
    """
    
    def __init__(self, mqtt_client=None, **kwargs):
        """
        Initialisiert CCU Gateway
        
        Args:
            mqtt_client: MQTT-Client für CCU (wird später implementiert)
        """
        self.mqtt_client = mqtt_client
        self.message_templates = get_message_templates()
        
        logger.info("🏗️ CcuGateway initialized")
    
    def reset_factory(self) -> bool:
        """
        Factory Reset ausführen
        
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            # Registry v2 Integration: Topic aus Registry laden
            topic = "ccu/set/reset"
            topic_config = self.message_templates.get_topic_config(topic)
            
            if topic_config:
                # Message aus Template rendern
                message = self.message_templates.render_message(topic, {"reset": True})
                if message:
                    # TODO: MQTT-Client Integration implementieren
                    # qos = topic_config.get('qos', 1)
                    # retain = topic_config.get('retain', False)
                    # self.mqtt_client.publish(topic, message, qos=qos, retain=retain)
                    
                    logger.info(f"🔄 Factory Reset message rendered: {message}")
                    return True
            else:
                logger.warning(f"⚠️ No topic configuration found for {topic}")
            
            logger.info("🔄 Factory Reset requested (TODO: MQTT integration)")
            return True
            
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
            topic_config = self.message_templates.get_topic_config(topic)
            
            if topic_config:
                # Message aus Template rendern
                message = self.message_templates.render_message(topic, {
                    "command": command,
                    "params": params or {}
                })
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
            # topics = self.message_templates.get_all_topic_patterns("module/v1/ff/*/state")
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
            # message = self.message_templates.render_message(topic, order_data)
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
            mqtt_clients = self.message_templates.mqtt_clients
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
            mqtt_clients = self.message_templates.mqtt_clients
            ccu_client = mqtt_clients.get('mqtt_clients', {}).get('ccu_mqtt_client', {})
            return ccu_client.get('subscribed_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to get CCU subscribed topics: {e}")
            return []