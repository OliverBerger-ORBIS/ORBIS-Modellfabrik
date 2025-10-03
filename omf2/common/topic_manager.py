#!/usr/bin/env python3
"""
Generic Topic Manager - Domain-agnostische Topic-Management-Funktionalität
Kann von allen Domänen (Admin, CCU, Node-RED) verwendet werden
"""

import json
import logging
from typing import Dict, List, Optional, Any
from omf2.common.logger import get_logger
from omf2.registry.manager.registry_manager import get_registry_manager

logger = get_logger(__name__)


class TopicManager:
    """
    Generic Topic Manager - Domain-agnostische Topic-Management-Funktionalität
    
    Verantwortlichkeiten:
    - Topic-Informationen abrufen (alle Domänen)
    - Topic-Schema-Mappings (alle Domänen)
    - Topic-Konfiguration (domain-spezifisch)
    - Topic-Validierung und -Analyse (domain-agnostisch)
    
    Kann von Admin, CCU, Node-RED und anderen Domänen verwendet werden.
    """
    
    def __init__(self, domain: str, registry_manager=None):
        """
        Initialize Generic Topic Manager
        
        Args:
            domain: Domain name (e.g., 'admin', 'ccu', 'nodered')
            registry_manager: Registry Manager instance
        """
        self.domain = domain
        self.registry_manager = registry_manager or get_registry_manager()
        
        logger.info(f"🏗️ {domain.title()} Topic Manager initialized")
    
    def get_all_topics(self) -> List[str]:
        """
        Alle Topics aus Registry abrufen (Domain-agnostisch)
        
        Returns:
            Liste aller Topics
        """
        try:
            all_topics = []
            
            # Topics aus Registry Manager sammeln
            topics_data = self.registry_manager.get_topics()
            for topic, topic_info in topics_data.items():
                all_topics.append(topic)
            
            logger.debug(f"📊 [{self.domain}] Retrieved {len(all_topics)} topics from registry")
            return all_topics
            
        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to get all topics: {e}")
            return []
    
    def get_topic_schemas(self) -> Dict[str, Dict]:
        """
        Topic-Schema Mappings abrufen (Domain-agnostisch)
        
        Returns:
            Dict mit Topic-Schema Mappings
        """
        try:
            # Topic → Schema Beziehung
            all_topics = self.get_all_topics()
            
            topic_schemas = {}
            for topic in all_topics:
                schema = self.registry_manager.get_topic_schema(topic)
                if schema:
                    topic_schemas[topic] = schema
            
            logger.debug(f"📊 [{self.domain}] Retrieved {len(topic_schemas)} topic-schema mappings")
            return topic_schemas
            
        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to get topic schemas: {e}")
            return {}
    
    def get_topic_config(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Topic-Konfiguration abrufen (Domain-agnostisch)
        
        Args:
            topic: MQTT Topic
            
        Returns:
            Topic-Konfiguration oder None
        """
        try:
            config = self.registry_manager.get_topic_config(topic)
            if config:
                logger.debug(f"📊 [{self.domain}] Retrieved config for topic: {topic}")
            else:
                logger.warning(f"⚠️ [{self.domain}] No config found for topic: {topic}")
            return config
            
        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to get config for topic {topic}: {e}")
            return None
    
    def get_topic_schema(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Topic-Schema abrufen (Domain-agnostisch)
        
        Args:
            topic: MQTT Topic
            
        Returns:
            Topic-Schema oder None
        """
        try:
            schema = self.registry_manager.get_topic_schema(topic)
            if schema:
                logger.debug(f"📊 [{self.domain}] Retrieved schema for topic: {topic}")
            else:
                logger.warning(f"⚠️ [{self.domain}] No schema found for topic: {topic}")
            return schema
            
        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to get schema for topic {topic}: {e}")
            return None
    
    def get_domain_topics(self, domain: str = None) -> List[str]:
        """
        Domain-spezifische Topics abrufen
        
        Args:
            domain: Domain name (defaults to self.domain)
            
        Returns:
            Liste der Domain-spezifischen Topics
        """
        try:
            target_domain = domain or self.domain
            domain_topics = []
            
            # Topics aus MQTT-Client-Konfiguration sammeln
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            client_name = f"{target_domain}_mqtt_client"
            client_config = mqtt_clients.get('mqtt_clients', {}).get(client_name, {})
            
            # Subscribed Topics
            subscribed_topics = client_config.get('subscribed_topics', [])
            for topic_info in subscribed_topics:
                if isinstance(topic_info, dict):
                    topic = topic_info.get('topic', '')
                else:
                    topic = str(topic_info)
                if topic and topic not in domain_topics:
                    domain_topics.append(topic)
            
            # Published Topics
            published_topics = client_config.get('published_topics', [])
            for topic_info in published_topics:
                if isinstance(topic_info, dict):
                    topic = topic_info.get('topic', '')
                else:
                    topic = str(topic_info)
                if topic and topic not in domain_topics:
                    domain_topics.append(topic)
            
            logger.debug(f"📊 [{self.domain}] Retrieved {len(domain_topics)} topics for domain: {target_domain}")
            return domain_topics
            
        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to get domain topics for {domain}: {e}")
            return []
    
    def get_published_topics(self, domain: str = None) -> List[str]:
        """
        Domain-spezifische Published Topics abrufen
        
        Args:
            domain: Domain name (defaults to self.domain)
            
        Returns:
            Liste der Published Topics
        """
        try:
            target_domain = domain or self.domain
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            client_name = f"{target_domain}_mqtt_client"
            client_config = mqtt_clients.get('mqtt_clients', {}).get(client_name, {})
            
            published_topics = []
            for topic_info in client_config.get('published_topics', []):
                if isinstance(topic_info, dict):
                    topic = topic_info.get('topic', '')
                else:
                    topic = str(topic_info)
                if topic:
                    published_topics.append(topic)
            
            logger.debug(f"📊 [{self.domain}] Retrieved {len(published_topics)} published topics for domain: {target_domain}")
            return published_topics
            
        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to get published topics for {domain}: {e}")
            return []
    
    def get_subscribed_topics(self, domain: str = None) -> List[str]:
        """
        Domain-spezifische Subscribed Topics abrufen
        
        Args:
            domain: Domain name (defaults to self.domain)
            
        Returns:
            Liste der Subscribed Topics
        """
        try:
            target_domain = domain or self.domain
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            client_name = f"{target_domain}_mqtt_client"
            client_config = mqtt_clients.get('mqtt_clients', {}).get(client_name, {})
            
            subscribed_topics = []
            for topic_info in client_config.get('subscribed_topics', []):
                if isinstance(topic_info, dict):
                    topic = topic_info.get('topic', '')
                else:
                    topic = str(topic_info)
                if topic:
                    subscribed_topics.append(topic)
            
            logger.debug(f"📊 [{self.domain}] Retrieved {len(subscribed_topics)} subscribed topics for domain: {target_domain}")
            return subscribed_topics
            
        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to get subscribed topics for {domain}: {e}")
            return []
    
    def analyze_topic(self, topic: str) -> Dict[str, Any]:
        """
        Topic-Analyse durchführen (Domain-agnostisch)
        
        Args:
            topic: MQTT Topic
            
        Returns:
            Dict mit Topic-Analyse-Informationen
        """
        try:
            analysis = {
                "topic": topic,
                "exists": False,
                "has_schema": False,
                "has_config": False,
                "schema": None,
                "config": None,
                "domains": []
            }
            
            # Prüfe ob Topic existiert
            all_topics = self.get_all_topics()
            if topic in all_topics:
                analysis["exists"] = True
            
            # Prüfe Schema
            schema = self.get_topic_schema(topic)
            if schema:
                analysis["has_schema"] = True
                analysis["schema"] = schema
            
            # Prüfe Konfiguration
            config = self.get_topic_config(topic)
            if config:
                analysis["has_config"] = True
                analysis["config"] = config
            
            # Prüfe welche Domänen diesen Topic verwenden
            domains = ["admin", "ccu", "nodered"]
            for domain in domains:
                domain_topics = self.get_domain_topics(domain)
                if topic in domain_topics:
                    analysis["domains"].append(domain)
            
            logger.debug(f"📊 [{self.domain}] Analyzed topic: {topic}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to analyze topic {topic}: {e}")
            return {"topic": topic, "error": str(e)}
    
    def get_topics_by_pattern(self, pattern: str) -> List[str]:
        """
        Topics nach Pattern filtern (Domain-agnostisch)
        
        Args:
            pattern: Topic-Pattern (z.B. "ccu/*", "*/state")
            
        Returns:
            Liste der passenden Topics
        """
        try:
            all_topics = self.get_all_topics()
            matching_topics = []
            
            # Einfache Pattern-Matching (kann erweitert werden)
            if "*" in pattern:
                prefix = pattern.split("*")[0]
                suffix = pattern.split("*")[-1] if len(pattern.split("*")) > 1 else ""
                
                for topic in all_topics:
                    if topic.startswith(prefix) and topic.endswith(suffix):
                        matching_topics.append(topic)
            else:
                # Exakte Übereinstimmung
                if pattern in all_topics:
                    matching_topics.append(pattern)
            
            logger.debug(f"📊 [{self.domain}] Found {len(matching_topics)} topics matching pattern: {pattern}")
            return matching_topics
            
        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to get topics by pattern {pattern}: {e}")
            return []
    
    def validate_topic_structure(self, topic: str) -> Dict[str, Any]:
        """
        Topic-Struktur validieren (Domain-agnostisch)
        
        Args:
            topic: MQTT Topic
            
        Returns:
            Dict mit Validierungsergebnissen
        """
        try:
            validation = {
                "topic": topic,
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Basis-Validierung
            if not topic:
                validation["valid"] = False
                validation["errors"].append("Topic is empty")
                return validation
            
            # MQTT Topic-Validierung
            if topic.startswith("/") or topic.endswith("/"):
                validation["warnings"].append("Topic starts or ends with slash")
            
            # Wildcard-Validierung
            if "+" in topic and "#" in topic:
                validation["valid"] = False
                validation["errors"].append("Topic contains both + and # wildcards")
            
            if "#" in topic and not topic.endswith("#"):
                validation["valid"] = False
                validation["errors"].append("Multi-level wildcard # must be at the end")
            
            # Schema-Validierung
            schema = self.get_topic_schema(topic)
            if not schema:
                validation["warnings"].append("No schema found for topic")
            
            # Konfiguration-Validierung
            config = self.get_topic_config(topic)
            if not config:
                validation["warnings"].append("No configuration found for topic")
            
            logger.debug(f"📊 [{self.domain}] Validated topic structure: {topic}")
            return validation
            
        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to validate topic structure {topic}: {e}")
            return {"topic": topic, "valid": False, "errors": [str(e)], "warnings": []}


# Domain-specific Factory Functions
def get_admin_topic_manager(registry_manager=None) -> TopicManager:
    """Factory function für Admin Topic Manager"""
    return TopicManager("admin", registry_manager)


def get_ccu_topic_manager(registry_manager=None) -> TopicManager:
    """Factory function für CCU Topic Manager"""
    return TopicManager("ccu", registry_manager)


def get_nodered_topic_manager(registry_manager=None) -> TopicManager:
    """Factory function für Node-RED Topic Manager"""
    return TopicManager("nodered", registry_manager)


def get_topic_manager(domain: str, registry_manager=None) -> TopicManager:
    """
    Generic factory function für Topic Manager
    
    Args:
        domain: Domain name (e.g., 'admin', 'ccu', 'nodered')
        registry_manager: Registry Manager instance
        
    Returns:
        TopicManager instance für die angegebene Domain
    """
    return TopicManager(domain, registry_manager)
