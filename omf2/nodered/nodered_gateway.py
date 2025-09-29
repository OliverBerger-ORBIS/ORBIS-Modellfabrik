#!/usr/bin/env python3
"""
Node-RED Gateway - Fassade für Node-RED Business-Operationen
"""

import logging
from typing import Dict, List, Optional, Any
from omf2.common.message_templates import get_message_templates

logger = logging.getLogger(__name__)


class NoderedGateway:
    """
    Gateway für Node-RED-spezifische Business-Operationen
    
    Nutzt MessageTemplates und beide MQTT-Clients (pub/sub) für Node-RED-Operationen.
    Stellt Methoden für die UI bereit.
    """
    
    def __init__(self, pub_mqtt_client=None, sub_mqtt_client=None, **kwargs):
        """
        Initialisiert Node-RED Gateway
        
        Args:
            pub_mqtt_client: Node-RED Publisher MQTT-Client
            sub_mqtt_client: Node-RED Subscriber MQTT-Client
        """
        self.pub_mqtt_client = pub_mqtt_client
        self.sub_mqtt_client = sub_mqtt_client
        self.message_templates = get_message_templates()
        
        logger.info("🏗️ NoderedGateway initialized")
    
    def get_normalized_module_states(self) -> List[Dict]:
        """
        Normalisierte Module States abrufen (von Node-RED Publisher)
        
        Returns:
            Liste der normalisierten Module States
        """
        try:
            # Registry v2 Integration: Topics aus Registry laden
            pub_topics = self.get_pub_topics()
            module_state_topics = [topic for topic in pub_topics if "module" in topic and "state" in topic]
            
            states = []
            for topic in module_state_topics:
                # TODO: MQTT-Client Integration implementieren
                # state = self.pub_mqtt_client.get_buffer(topic)
                # if state:
                #     states.append(state)
                pass
            
            logger.info(f"📊 Normalized Module States requested for {len(module_state_topics)} topics (TODO: MQTT integration)")
            return states
            
        except Exception as e:
            logger.error(f"❌ Normalized Module States retrieval failed: {e}")
            return []
    
    def get_ccu_commands(self) -> List[Dict]:
        """
        CCU Commands abrufen (von Node-RED Subscriber)
        
        Returns:
            Liste der CCU Commands
        """
        try:
            # TODO: MQTT-Client Integration implementieren
            # topics = self._get_sub_topics_for_pattern("ccu/*")
            # commands = []
            # for topic in topics:
            #     command = self.sub_mqtt_client.get_buffer(topic)
            #     if command:
            #         commands.append(command)
            # return commands
            
            logger.info("📊 CCU Commands requested (TODO: MQTT integration)")
            return []
            
        except Exception as e:
            logger.error(f"❌ CCU Commands retrieval failed: {e}")
            return []
    
    def get_opc_ua_states(self) -> List[Dict]:
        """
        OPC-UA States abrufen (von Node-RED Subscriber)
        
        Returns:
            Liste der OPC-UA States
        """
        try:
            # TODO: MQTT-Client Integration implementieren
            # topics = self._get_sub_topics_for_pattern("opc_ua/*")
            # states = []
            # for topic in topics:
            #     state = self.sub_mqtt_client.get_buffer(topic)
            #     if state:
            #         states.append(state)
            # return states
            
            logger.info("📊 OPC-UA States requested (TODO: MQTT integration)")
            return []
            
        except Exception as e:
            logger.error(f"❌ OPC-UA States retrieval failed: {e}")
            return []
    
    def send_ccu_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """
        CCU Feedback senden (über Node-RED Publisher)
        
        Args:
            feedback_data: Feedback-Daten
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            # TODO: MQTT-Client Integration implementieren
            # topic = "ccu/global"
            # message = self.message_templates.render_message(topic, feedback_data)
            # if message:
            #     self.pub_mqtt_client.publish(topic, message)
            #     return True
            
            logger.info(f"📤 CCU Feedback: {feedback_data} (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ CCU Feedback failed: {e}")
            return False
    
    def send_order_completed(self, order_data: Dict[str, Any]) -> bool:
        """
        Order Completed senden (über Node-RED Publisher)
        
        Args:
            order_data: Order-Daten
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            # TODO: MQTT-Client Integration implementieren
            # topic = "ccu/order/completed"
            # message = self.message_templates.render_message(topic, order_data)
            # if message:
            #     self.pub_mqtt_client.publish(topic, message)
            #     return True
            
            logger.info(f"📤 Order Completed: {order_data} (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Order Completed failed: {e}")
            return False
    
    def get_pub_topics(self) -> List[str]:
        """
        Node-RED Publisher Topics aus Registry abrufen
        
        Returns:
            Liste der Publisher Topics
        """
        try:
            mqtt_clients = self.message_templates.mqtt_clients
            nodered_pub_client = mqtt_clients.get('mqtt_clients', {}).get('nodered_pub_mqtt_client', {})
            return nodered_pub_client.get('published_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to get Node-RED pub topics: {e}")
            return []
    
    def get_sub_topics(self) -> List[str]:
        """
        Node-RED Subscriber Topics aus Registry abrufen
        
        Returns:
            Liste der Subscriber Topics
        """
        try:
            mqtt_clients = self.message_templates.mqtt_clients
            nodered_sub_client = mqtt_clients.get('mqtt_clients', {}).get('nodered_sub_mqtt_client', {})
            return nodered_sub_client.get('subscribed_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to get Node-RED sub topics: {e}")
            return []
    
    def _get_pub_topics_for_pattern(self, pattern: str) -> List[str]:
        """
        Publisher Topics für Pattern abrufen
        
        Args:
            pattern: Topic-Pattern
            
        Returns:
            Liste der passenden Topics
        """
        try:
            all_topics = self.get_pub_topics()
            # TODO: Pattern-Matching implementieren
            return [topic for topic in all_topics if pattern.replace('*', '') in topic]
        except Exception as e:
            logger.error(f"❌ Failed to get pub topics for pattern {pattern}: {e}")
            return []
    
    def _get_sub_topics_for_pattern(self, pattern: str) -> List[str]:
        """
        Subscriber Topics für Pattern abrufen
        
        Args:
            pattern: Topic-Pattern
            
        Returns:
            Liste der passenden Topics
        """
        try:
            all_topics = self.get_sub_topics()
            # TODO: Pattern-Matching implementieren
            return [topic for topic in all_topics if pattern.replace('*', '') in topic]
        except Exception as e:
            logger.error(f"❌ Failed to get sub topics for pattern {pattern}: {e}")
            return []