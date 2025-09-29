#!/usr/bin/env python3
"""
MessageTemplates Singleton - Zentrale Utility für Registry v2 Templates
"""

import logging
import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


class MessageTemplates:
    """
    Singleton für Message Template Management
    
    Lädt Registry v2 Templates, Mappings und Topics.
    Bietet Methoden zum Rendern, Validieren und Loggen von Nachrichten.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, registry_path: str = "omf2/registry/model/v2/"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, registry_path: str = "omf2/registry/model/v2/"):
        if MessageTemplates._initialized:
            return
            
        self.registry_path = Path(registry_path)
        self.templates = {}
        self.mappings = {}
        self.topics = {}
        self.modules = {}
        self.mqtt_clients = {}
        
        # Registry v2 laden
        self._load_registry()
        MessageTemplates._initialized = True
        
        logger.info("🏗️ MessageTemplates Singleton initialized")
    
    def _load_registry(self):
        """Lädt alle Registry v2 Komponenten"""
        try:
            # Templates laden
            templates_dir = self.registry_path / "templates"
            if templates_dir.exists():
                for template_file in templates_dir.glob("*.yml"):
                    template_name = template_file.stem
                    with open(template_file, 'r', encoding='utf-8') as f:
                        self.templates[template_name] = yaml.safe_load(f)
            
            # Mappings laden
            mappings_file = self.registry_path / "mappings" / "topic_templates.yml"
            if mappings_file.exists():
                with open(mappings_file, 'r', encoding='utf-8') as f:
                    self.mappings = yaml.safe_load(f)
            
            # Topics laden
            topics_dir = self.registry_path / "topics"
            if topics_dir.exists():
                for topic_file in topics_dir.glob("*.yml"):
                    topic_name = topic_file.stem
                    with open(topic_file, 'r', encoding='utf-8') as f:
                        self.topics[topic_name] = yaml.safe_load(f)
            
            # Modules laden
            modules_file = self.registry_path / "modules.yml"
            if modules_file.exists():
                with open(modules_file, 'r', encoding='utf-8') as f:
                    self.modules = yaml.safe_load(f)
            
            # MQTT Clients laden
            mqtt_clients_file = self.registry_path / "mqtt_clients.yml"
            if mqtt_clients_file.exists():
                with open(mqtt_clients_file, 'r', encoding='utf-8') as f:
                    self.mqtt_clients = yaml.safe_load(f)
            
            logger.info(f"📚 Registry v2 loaded: {len(self.templates)} templates, {len(self.mappings.get('mappings', []))} mappings")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Registry v2: {e}")
            raise
    
    def get_template_for_topic(self, topic: str) -> Optional[str]:
        """
        Findet Template für einen Topic
        
        Args:
            topic: MQTT Topic (z.B. "module/v1/ff/SVR3QA0022/state")
            
        Returns:
            Template-Key oder None
        """
        mappings = self.mappings.get('mappings', [])
        
        # 1. Exact Match
        for mapping in mappings:
            if mapping.get('topic') == topic:
                return mapping.get('template')
        
        # 2. Pattern Match
        for mapping in mappings:
            pattern = mapping.get('pattern')
            if pattern and self._match_pattern(topic, pattern):
                return mapping.get('template')
        
        logger.warning(f"⚠️ No template found for topic: {topic}")
        return None
    
    def _match_pattern(self, topic: str, pattern: str) -> bool:
        """Prüft ob Topic dem Pattern entspricht"""
        # Einfache Pattern-Matching Implementierung
        # Erweitert für komplexere Patterns bei Bedarf
        import re
        
        # Konvertiere Pattern zu Regex
        regex_pattern = pattern.replace('{module_id}', r'[^/]+')
        regex_pattern = regex_pattern.replace('{function}', r'[^/]+')
        regex_pattern = regex_pattern.replace('{control}', r'[^/]+')
        regex_pattern = regex_pattern.replace('{input}', r'[^/]+')
        regex_pattern = regex_pattern.replace('{output}', r'[^/]+')
        
        return bool(re.match(regex_pattern, topic))
    
    def get_template(self, template_key: str) -> Optional[Dict]:
        """
        Lädt Template nach Key
        
        Args:
            template_key: Template-Key (z.B. "module.state")
            
        Returns:
            Template-Dict oder None
        """
        return self.templates.get(template_key)
    
    def render_message(self, topic: str, params: Dict[str, Any]) -> Optional[Dict]:
        """
        Rendert Message basierend auf Topic und Parametern
        
        Args:
            topic: MQTT Topic
            params: Parameter für Message-Generierung
            
        Returns:
            Gerenderte Message oder None
        """
        template_key = self.get_template_for_topic(topic)
        if not template_key:
            return None
        
        template = self.get_template(template_key)
        if not template:
            logger.warning(f"⚠️ Template not found: {template_key}")
            return None
        
        try:
            # Message basierend auf Template-Schema generieren
            message = self._generate_message_from_template(template, params)
            return message
        except Exception as e:
            logger.error(f"❌ Failed to render message for topic {topic}: {e}")
            return None
    
    def _generate_message_from_template(self, template: Dict, params: Dict) -> Dict:
        """Generiert Message basierend auf Template-Schema"""
        schema = template.get('template', {}).get('schema', {})
        properties = schema.get('properties', {})
        
        message = {}
        
        # Required Fields aus Template
        required_fields = schema.get('required', [])
        
        for field in required_fields:
            if field in params:
                message[field] = params[field]
            else:
                # Default-Werte aus Template
                field_schema = properties.get(field, {})
                if 'example' in field_schema:
                    message[field] = field_schema['example']
                else:
                    logger.warning(f"⚠️ Missing required field: {field}")
        
        # Optional Fields aus params
        for field, value in params.items():
            if field not in message:
                message[field] = value
        
        return message
    
    def validate_message(self, topic: str, message: Dict) -> Dict[str, List[str]]:
        """
        Validiert Message gegen Template-Schema
        
        Args:
            topic: MQTT Topic
            message: Message zum Validieren
            
        Returns:
            {"errors": [...], "warnings": [...]}
        """
        result = {"errors": [], "warnings": []}
        
        template_key = self.get_template_for_topic(topic)
        if not template_key:
            result["errors"].append(f"No template found for topic: {topic}")
            return result
        
        template = self.get_template(template_key)
        if not template:
            result["errors"].append(f"Template not found: {template_key}")
            return result
        
        schema = template.get('template', {}).get('schema', {})
        if not schema:
            result["warnings"].append("No schema defined for template")
            return result
        
        try:
            validate(instance=message, schema=schema)
            logger.debug(f"✅ Message validated for topic: {topic}")
        except ValidationError as e:
            result["errors"].append(f"Schema validation failed: {e.message}")
        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")
        
        return result
    
    def log_message(self, topic: str, message: Dict, direction: str):
        """
        Loggt Message für Debugging
        
        Args:
            topic: MQTT Topic
            message: Message
            direction: "SEND" oder "RECEIVE"
        """
        logger.info(f"📤 {direction} message on topic {topic}: {message}")
    
    def get_all_templates(self) -> Dict:
        """Gibt alle geladenen Templates zurück"""
        return self.templates
    
    def get_all_mappings(self) -> Dict:
        """Gibt alle Mappings zurück"""
        return self.mappings
    
    def get_topic_config(self, topic: str) -> tuple[int, bool]:
        """
        Gibt QoS/Retain für Topic zurück
        
        Args:
            topic: MQTT Topic
            
        Returns:
            (qos, retain) Tupel
        """
        # Suche in topics/ nach QoS/Retain
        for topic_file, topic_data in self.topics.items():
            topics_list = topic_data.get(f"{topic_file}_topics", [])
            for topic_config in topics_list:
                if topic_config.get('topic') == topic:
                    return topic_config.get('qos', 1), topic_config.get('retain', False)
        
        # Default-Werte
        return 1, False


# Singleton Factory
def get_message_templates(registry_path: str = "omf2/registry/model/v2/") -> MessageTemplates:
    """
    Factory-Funktion für MessageTemplates Singleton
    
    Args:
        registry_path: Pfad zur Registry v2
        
    Returns:
        MessageTemplates Singleton Instance
    """
    return MessageTemplates(registry_path)
