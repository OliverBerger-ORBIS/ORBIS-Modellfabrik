#!/usr/bin/env python3
"""
Registry Manager - Zentrale Komponente für Registry-Daten
Lädt alle Registry-Entitäten in den Speicher und stellt sie über eine einheitliche API bereit
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RegistryManager:
    """
    Zentrale Komponente für Registry-Daten
    Singleton Pattern - nur eine Instanz pro Anwendung
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, registry_path: str = "omf2/registry/"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, registry_path: str = "omf2/registry/"):
        if RegistryManager._initialized:
            return
            
        self.registry_path = Path(registry_path)
        self._load_timestamp = datetime.now()
        
        # Registry-Entitäten im Speicher
        self.topics = {}
        self.schemas = {}  # Ersetzt templates
        self.topic_schema_mappings = {}  # Ersetzt topic_template_mappings
        self.mqtt_clients = {}
        self.workpieces = {}
        self.modules = {}
        self.stations = {}
        self.txt_controllers = {}
        
        # Lade alle Registry-Daten
        self._load_all_registry_data()
        
        RegistryManager._initialized = True
        logger.info("🏗️ Registry Manager Singleton initialized")
    
    def _load_all_registry_data(self):
        """Lädt alle Registry-Daten in den Speicher"""
        try:
            # Topics laden
            self._load_topics()
            
            # Schemas laden (ersetzt Templates)
            self._load_schemas()
            
            # Topic-Schema-Mappings laden
            self._load_topic_schema_mappings()
            
            # MQTT Clients laden
            self._load_mqtt_clients()
            
            # Workpieces laden
            self._load_workpieces()
            
            # Modules laden
            self._load_modules()
            
            # Stations laden
            self._load_stations()
            
            # TXT Controllers laden
            self._load_txt_controllers()
            
            logger.info(f"📚 Registry v2 loaded: {len(self.topics)} topics, {len(self.schemas)} schemas, {len(self.workpieces)} workpieces")
            
        except Exception as e:
            logger.error(f"❌ Failed to load registry data: {e}")
            raise
    
    def _load_topics(self):
        """Lädt alle Topics aus den Unterordnern"""
        topics_dir = self.registry_path / "topics"
        if not topics_dir.exists():
            logger.warning(f"⚠️ Topics directory not found: {topics_dir}")
            return
        
        for topic_file in topics_dir.glob("*.yml"):
            try:
                with open(topic_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    
                # Extrahiere Category aus metadata
                file_category = data.get('category', 'unknown')
                
                # Extrahiere Topics aus verschiedenen Kategorien
                for category, topics_list in data.items():
                    if category not in ['metadata', 'category'] and isinstance(topics_list, list):
                        for topic_data in topics_list:
                            if isinstance(topic_data, dict) and 'topic' in topic_data:
                                topic_name = topic_data['topic']
                                self.topics[topic_name] = {
                                    'topic': topic_name,
                                    'qos': topic_data.get('qos', 1),
                                    'retain': topic_data.get('retain', 0),
                                    'schema': topic_data.get('schema'),
                                    'description': topic_data.get('description'),
                                    'category': file_category,
                                    'file': topic_file.name
                                }
                                
                logger.info(f"📡 Loaded topics from {topic_file.name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to load topics from {topic_file}: {e}")
    
    def _load_templates(self):
        """Lädt alle Templates aus dem templates Unterordner"""
        templates_dir = self.registry_path / "templates"
        if not templates_dir.exists():
            logger.warning(f"⚠️ Templates directory not found: {templates_dir}")
            return
        
        for template_file in templates_dir.glob("*.yml"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    
                if 'template' in data:
                    template_data = data['template']
                    template_name = template_data.get('name', template_file.stem)
                    
                    self.schemas[template_name] = {
                        'name': template_name,
                        'template_category': template_data.get('template_category', 'UNKNOWN'),
                        'template_sub_category': template_data.get('template_sub_category', 'UNKNOWN'),
                        'schema': template_data.get('schema', {}),
                        'file': template_file.name
                    }
                    
                logger.info(f"📝 Loaded template {template_name} from {template_file.name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to load template from {template_file}: {e}")
    
    def _load_topic_template_mappings(self):
        """Lädt Topic-Template-Mappings"""
        mappings_file = self.registry_path / "mappings" / "topic_templates.yml"
        if not mappings_file.exists():
            logger.warning(f"⚠️ Topic-Template mappings file not found: {mappings_file}")
            return
        
        try:
            with open(mappings_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
            mappings = data.get('mappings', [])
            for mapping in mappings:
                if isinstance(mapping, dict) and 'topic' in mapping:
                    topic = mapping['topic']
                    self.topic_schema_mappings[topic] = {
                        'topic': topic,
                        'template': mapping.get('template'),
                        'direction': mapping.get('direction', 'unknown')
                    }
                    
            logger.info(f"🔗 Loaded {len(mappings)} topic-template mappings")
            
        except Exception as e:
            logger.error(f"❌ Failed to load topic-template mappings: {e}")
    
    def _load_schemas(self):
        """Lädt alle Schemas aus dem schemas Unterordner"""
        schemas_dir = self.registry_path / "schemas"
        if not schemas_dir.exists():
            logger.warning(f"⚠️ Schemas directory not found: {schemas_dir}")
            return
        
        for schema_file in schemas_dir.glob("*.schema.json"):
            try:
                import json
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                    
                schema_name = schema_file.stem
                self.schemas[schema_name] = {
                    'name': schema_name,
                    'file': schema_file.name,
                    'schema': schema_data,
                    'title': schema_data.get('title', ''),
                    'description': schema_data.get('description', ''),
                    'category': schema_data.get('category', 'unknown')
                }
                    
                logger.info(f"📝 Loaded schema from {schema_file.name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to load schema from {schema_file}: {e}")
    
    def _load_topic_schema_mappings(self):
        """Lädt Topic-Schema-Mappings"""
        # Schema-Mappings werden automatisch aus Topics generiert
        # da Topics jetzt direkt Schema-Referenzen haben
        for topic, topic_info in self.topics.items():
            if topic_info.get('schema'):
                self.topic_schema_mappings[topic] = {
                    'topic': topic,
                    'schema': topic_info['schema'],
                    'description': topic_info.get('description', ''),
                    'category': topic_info.get('category', 'unknown')
                }
        
        logger.info(f"🔗 Generated {len(self.topic_schema_mappings)} topic-schema mappings")
    
    def _load_mqtt_clients(self):
        """Lädt MQTT Clients Konfiguration"""
        mqtt_file = self.registry_path / "mqtt_clients.yml"
        if not mqtt_file.exists():
            logger.warning(f"⚠️ MQTT clients file not found: {mqtt_file}")
            return
        
        try:
            with open(mqtt_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
            # Extrahiere MQTT Clients (ignoriere metadata, qos_patterns, retain_patterns)
            mqtt_clients_data = data.get('mqtt_clients', {})
            for client_name, client_data in mqtt_clients_data.items():
                if isinstance(client_data, dict):
                    self.mqtt_clients[client_name] = {
                        'name': client_name,
                        'active': client_data.get('active', False),
                        'client_class': client_data.get('client_class', ''),
                        'client_id': client_data.get('client_id', client_name),
                        'subscribed_topics': client_data.get('subscribed_topics', []),
                        'published_topics': client_data.get('published_topics', []),
                        'qos': client_data.get('qos', 1),
                        'retain': client_data.get('retain', 0)
                    }
                    
            logger.info(f"📡 Loaded {len(self.mqtt_clients)} MQTT clients")
            
        except Exception as e:
            logger.error(f"❌ Failed to load MQTT clients: {e}")
    
    def _load_workpieces(self):
        """Lädt Workpieces Konfiguration"""
        workpieces_file = self.registry_path / "workpieces.yml"
        if not workpieces_file.exists():
            logger.warning(f"⚠️ Workpieces file not found: {workpieces_file}")
            return
        
        try:
            with open(workpieces_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
            # Workpieces sind jetzt als Liste
            workpieces_list = data.get('workpieces', [])
            for workpiece_data in workpieces_list:
                if isinstance(workpiece_data, dict) and 'id' in workpiece_data:
                    workpiece_id = workpiece_data['id']
                    self.workpieces[workpiece_id] = {
                        'id': workpiece_id,
                        'nfc_code': workpiece_data.get('nfc_code', ''),
                        'color': workpiece_data.get('color', 'UNKNOWN'),
                        'quality_check': workpiece_data.get('quality_check', 'UNKNOWN'),
                        'description': workpiece_data.get('description', ''),
                        'enabled': workpiece_data.get('enabled', True)
                    }
                
            logger.info(f"🔧 Loaded {len(self.workpieces)} workpieces")
            
        except Exception as e:
            logger.error(f"❌ Failed to load workpieces: {e}")
    
    def _load_modules(self):
        """Lädt Modules Konfiguration"""
        modules_file = self.registry_path / "modules.yml"
        if not modules_file.exists():
            logger.warning(f"⚠️ Modules file not found: {modules_file}")
            return
        
        try:
            with open(modules_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
            # Modules sind als Liste
            modules_list = data.get('modules', [])
            for module_data in modules_list:
                if isinstance(module_data, dict) and 'id' in module_data:
                    module_id = module_data['id']
                    self.modules[module_id] = {
                        'id': module_id,
                        'name': module_data.get('name', module_id),
                        'type': module_data.get('type', 'UNKNOWN'),
                        'enabled': module_data.get('enabled', True),
                        'icon': module_data.get('icon', '🔧'),
                        'name_lang_en': module_data.get('name_lang_en', ''),
                        'name_lang_de': module_data.get('name_lang_de', '')
                    }
                
            logger.info(f"🏭 Loaded {len(self.modules)} modules")
            
        except Exception as e:
            logger.error(f"❌ Failed to load modules: {e}")
    
    def _load_stations(self):
        """Lädt Stations Konfiguration"""
        stations_file = self.registry_path / "stations.yml"
        if not stations_file.exists():
            logger.warning(f"⚠️ Stations file not found: {stations_file}")
            return
        
        try:
            with open(stations_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
            # Stations sind als Dictionary mit Unterkategorien
            stations_data = data.get('stations', {})
            for category, stations_list in stations_data.items():
                if isinstance(stations_list, list):
                       for station_data in stations_list:
                           if isinstance(station_data, dict) and 'id' in station_data:
                               station_id = station_data['id']
                               # Hole Name aus Modules über ID
                               module_name = self._get_module_name_by_id(station_id)
                               self.stations[station_id] = {
                                   'id': station_id,
                                   'name': module_name,
                                   'type': category,
                                   'ip_address': station_data.get('ip_address', ''),
                                   'ip_range': station_data.get('ip_range', ''),
                                   'opc_ua_server': station_data.get('opc_ua_server', False),
                                   'opc_ua_endpoint': station_data.get('opc_ua_endpoint', ''),
                                   'description': station_data.get('description', '')
                               }
                
            logger.info(f"🏭 Loaded {len(self.stations)} stations")
            
        except Exception as e:
            logger.error(f"❌ Failed to load stations: {e}")
    
    def _load_txt_controllers(self):
        """Lädt TXT Controllers Konfiguration"""
        txt_file = self.registry_path / "txt_controllers.yml"
        if not txt_file.exists():
            logger.warning(f"⚠️ TXT controllers file not found: {txt_file}")
            return
        
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
            # TXT Controllers sind als Liste
            controllers_list = data.get('txt_controllers', [])
            for controller_data in controllers_list:
                if isinstance(controller_data, dict) and 'id' in controller_data:
                    controller_id = controller_data['id']
                    # Hole Module-Name für zugeordnet_zu_modul
                    module_id = controller_data.get('zugeordnet_zu_modul', '')
                    module_name = self._get_module_name_by_id(module_id) if module_id else ''
                    
                    self.txt_controllers[controller_id] = {
                        'id': controller_id,
                        'name': controller_data.get('name', controller_id),
                        'ip_address': controller_data.get('ip_address', ''),
                        'zugeordnet_zu_modul': module_id,
                        'zugeordnet_zu_modul_name': module_name,
                        'mqtt_client': controller_data.get('mqtt_client', ''),
                        'description': controller_data.get('description', '')
                    }
                
            logger.info(f"🎮 Loaded {len(self.txt_controllers)} TXT controllers")
            
        except Exception as e:
            logger.error(f"❌ Failed to load TXT controllers: {e}")
    
    # Public API Methods
    
    def get_topics(self) -> Dict[str, Any]:
        """Gibt alle Topics zurück"""
        return self.topics
    
    def get_templates(self) -> Dict[str, Any]:
        """Gibt alle Templates zurück (DEPRECATED - use get_schemas)"""
        return self.schemas
    
    def get_schemas(self) -> Dict[str, Any]:
        """Gibt alle Schemas zurück"""
        return self.schemas
    
    def get_topic_schema_mappings(self) -> Dict[str, Any]:
        """Gibt alle Topic-Schema-Mappings zurück"""
        return self.topic_schema_mappings
    
    def get_topic_schema(self, topic: str) -> Optional[Dict]:
        """Gibt das Schema für einen Topic zurück"""
        topic_info = self.topics.get(topic)
        if not topic_info or not topic_info.get('schema'):
            return None
        
        schema_file = self.registry_path / "schemas" / topic_info['schema']
        if not schema_file.exists():
            return None
        
        try:
            import json
            with open(schema_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden des Schemas {schema_file}: {e}")
            return None
    
    def get_topic_description(self, topic: str) -> Optional[str]:
        """Gibt die Beschreibung für einen Topic zurück"""
        topic_info = self.topics.get(topic)
        return topic_info.get('description') if topic_info else None
    
    def validate_topic_payload(self, topic: str, payload: Dict) -> Dict[str, Any]:
        """Validiert einen Payload gegen das Topic-Schema"""
        schema = self.get_topic_schema(topic)
        if not schema:
            return {
                'valid': False,
                'error': 'No schema found for topic',
                'schema_file': None
            }
        
        try:
            import jsonschema
            jsonschema.validate(payload, schema)
            return {
                'valid': True,
                'error': None,
                'schema_file': self.topics[topic]['schema']
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'schema_file': self.topics[topic]['schema']
            }
    
    def get_mqtt_clients(self) -> Dict[str, Any]:
        """Gibt alle MQTT Clients zurück"""
        return self.mqtt_clients
    
    def get_workpieces(self) -> Dict[str, Any]:
        """Gibt alle Workpieces zurück"""
        return self.workpieces
    
    def get_modules(self) -> Dict[str, Any]:
        """Gibt alle Modules zurück"""
        return self.modules
    
    def get_stations(self) -> Dict[str, Any]:
        """Gibt alle Stations zurück"""
        return self.stations
    
    def get_txt_controllers(self) -> Dict[str, Any]:
        """Gibt alle TXT Controllers zurück"""
        return self.txt_controllers
    
    def _get_module_name_by_id(self, module_id: str) -> str:
        """Hole Module-Name aus Modules über ID"""
        if module_id in self.modules:
            return self.modules[module_id].get('name', module_id)
        return module_id  # Fallback: ID als Name verwenden
    
    def get_active_mqtt_clients(self) -> Dict[str, Any]:
        """Gibt nur aktive MQTT Clients zurück"""
        return {name: config for name, config in self.mqtt_clients.items() if config.get('active', False)}
    
    def get_mqtt_client_config(self, client_name: str) -> Dict[str, Any]:
        """Gibt Konfiguration für einen spezifischen MQTT Client zurück"""
        return self.mqtt_clients.get(client_name, {})

    def get_registry_stats(self) -> Dict[str, Any]:
        """Gibt Registry-Statistiken zurück"""
        return {
            'load_timestamp': self._load_timestamp.isoformat(),
            'topics_count': len(self.topics),
            'schemas_count': len(self.schemas),
            'mappings_count': len(self.topic_schema_mappings),
            'mqtt_clients_count': len(self.mqtt_clients),
            'workpieces_count': len(self.workpieces),
            'modules_count': len(self.modules),
            'stations_count': len(self.stations),
            'txt_controllers_count': len(self.txt_controllers)
        }


# Singleton Factory
def get_registry_manager(registry_path: str = "omf2/registry/") -> RegistryManager:
    """
    Factory-Funktion für Registry Manager Singleton
    
    Args:
        registry_path: Pfad zur Registry v2
        
    Returns:
        Registry Manager Singleton Instance
    """
    return RegistryManager(registry_path)
