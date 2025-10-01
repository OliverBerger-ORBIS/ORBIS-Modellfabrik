"""
Client Factory for OMF2
Manages MQTT clients and other connection clients using singleton pattern
"""

from typing import Dict, Any, Optional
import yaml
import threading
from pathlib import Path

from omf2.common.logger import get_logger

logger = get_logger(__name__)


class ClientFactory:
    """Factory for creating and managing client instances"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._clients: Dict[str, Any] = {}
        self._config = self._load_config()
        self._registry_manager = None  # Will be set from omf.py
        self._initialized = True
    
    def set_registry_manager(self, registry_manager):
        """Set Registry Manager for dynamic client configuration"""
        self._registry_manager = registry_manager
        logger.info("📚 Registry Manager set in Client Factory")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load client configuration"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "mqtt_settings.yml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"⚠️ Config file not found: {config_path}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'mqtt': {
                'host': 'localhost',
                'port': 1883,
                'username': None,
                'password': None,
                'keepalive': 60,
                'clean_session': True
            },
            'environments': {
                'development': {
                    'mqtt': {
                        'host': 'localhost',
                        'port': 1883
                    }
                },
                'production': {
                    'mqtt': {
                        'host': 'mqtt.orbis-modellfabrik.de',
                        'port': 1883
                    }
                }
            }
        }
    
    def get_mqtt_client(self, client_name: str) -> Optional[Any]:
        """
        Get MQTT client by simple name (lazy loading, singleton pattern)
        Dynamically loads client based on Registry Manager configuration
        
        Args:
            client_name: Client name from mqtt_clients.yml (e.g., 'admin_mqtt_client')
        
        Returns:
            MQTT client instance or None
        """
        if client_name not in self._clients:
            try:
                # Get client config from Registry Manager
                if self._registry_manager:
                    client_config = self._registry_manager.get_mqtt_client_config(client_name)
                    if not client_config:
                        logger.error(f"❌ No config found for client: {client_name}")
                        return None
                    
                    # Check if client is active
                    if not client_config.get('active', False):
                        logger.warning(f"⚠️ Client {client_name} is not active")
                        return None
                    
                    # Get client class name from config
                    client_class_name = client_config.get('client_class', '')
                    if not client_class_name:
                        logger.error(f"❌ No client_class defined for {client_name}")
                        return None
                    
                    # Dynamically import client class based on Registry config
                    client_class = self._import_client_class(client_class_name)
                    if not client_class:
                        return None
                    
                    # Create client instance (Singleton pattern)
                    self._clients[client_name] = client_class()
                    logger.info(f"✅ Created MQTT client: {client_name} ({client_class_name})")
                
                else:
                    # Fallback: Old hardcoded logic if no Registry Manager
                    logger.warning("⚠️ No Registry Manager - using fallback client creation")
                    client_class = self._get_fallback_client_class(client_name)
                    if not client_class:
                        return None
                    self._clients[client_name] = client_class()
                    logger.info(f"✅ Created MQTT client (fallback): {client_name}")
                
            except ImportError as e:
                logger.error(f"❌ Failed to import {client_name}: {e}")
                return None
            except Exception as e:
                logger.error(f"❌ Failed to create {client_name}: {e}")
                return None
        
        return self._clients.get(client_name)
    
    def _import_client_class(self, client_class_name: str):
        """Dynamically import MQTT client class based on class name"""
        try:
            if client_class_name == 'AdminMqttClient':
                from omf2.admin.admin_mqtt_client import AdminMQTTClient
                return AdminMQTTClient
            elif client_class_name == 'CcuMqttClient':
                from omf2.ccu.ccu_mqtt_client import CCUMQTTClient
                return CCUMQTTClient
            elif client_class_name == 'NodeRedPubMqttClient':
                from omf2.nodered.nodered_pub_mqtt_client import NodeREDPubMQTTClient
                return NodeREDPubMQTTClient
            elif client_class_name == 'NodeRedSubMqttClient':
                from omf2.nodered.nodered_sub_mqtt_client import NodeREDSubMQTTClient
                return NodeREDSubMQTTClient
            elif client_class_name == 'TxtAiqsMqttClient':
                from omf2.txt.txt_aiqs_mqtt_client import TxtAiqsMqttClient
                return TxtAiqsMqttClient
            elif client_class_name == 'TxtDpsMqttClient':
                from omf2.txt.txt_dps_mqtt_client import TxtDpsMqttClient
                return TxtDpsMqttClient
            elif client_class_name == 'TxtFtsMqttClient':
                from omf2.txt.txt_fts_mqtt_client import TxtFtsMqttClient
                return TxtFtsMqttClient
            elif client_class_name == 'TxtCgwMqttClient':
                from omf2.txt.txt_cgw_mqtt_client import TxtCgwMqttClient
                return TxtCgwMqttClient
            else:
                logger.error(f"❌ Unknown client class: {client_class_name}")
                return None
        except ImportError as e:
            logger.error(f"❌ Failed to import {client_class_name}: {e}")
            return None
    
    def _get_fallback_client_class(self, client_name: str):
        """Fallback: Old hardcoded client mapping"""
        try:
            if client_name == 'admin_mqtt_client':
                from omf2.admin.admin_mqtt_client import AdminMQTTClient
                return AdminMQTTClient
            elif client_name == 'ccu_mqtt_client':
                from omf2.ccu.ccu_mqtt_client import CCUMQTTClient
                return CCUMQTTClient
            elif client_name == 'nodered_pub_mqtt_client':
                from omf2.nodered.nodered_pub_mqtt_client import NodeREDPubMQTTClient
                return NodeREDPubMQTTClient
            elif client_name == 'nodered_sub_mqtt_client':
                from omf2.nodered.nodered_sub_mqtt_client import NodeREDSubMQTTClient
                return NodeREDSubMQTTClient
            else:
                logger.error(f"❌ Unknown client name: {client_name}")
                return None
        except ImportError as e:
            logger.error(f"❌ Failed to import {client_name}: {e}")
            return None
    
    def get_client(self, client_type: str, domain: str, **kwargs) -> Optional[Any]:
        """
        Generic method to get any type of client
        
        Args:
            client_type: Type of client ('mqtt', 'http', etc.)
            domain: Domain name
            **kwargs: Additional arguments
        
        Returns:
            Client instance or None
        """
        if client_type == 'mqtt':
            return self.get_mqtt_client(domain, kwargs.get('environment', 'development'))
        else:
            logger.error(f"❌ Unsupported client type: {client_type}")
            return None
    
    def disconnect_all(self):
        """Disconnect all clients"""
        for client_key, client in self._clients.items():
            try:
                if hasattr(client, 'disconnect'):
                    client.disconnect()
                    logger.info(f"✅ Disconnected client: {client_key}")
            except Exception as e:
                logger.error(f"❌ Failed to disconnect {client_key}: {e}")
        
        self._clients.clear()
    
    def get_client_status(self) -> Dict[str, bool]:
        """Get connection status of all clients"""
        status = {}
        for client_key, client in self._clients.items():
            try:
                if hasattr(client, 'is_connected'):
                    status[client_key] = client.is_connected()
                else:
                    status[client_key] = False
            except Exception:
                status[client_key] = False
        
        return status
    
    def get_available_clients(self) -> list[str]:
        """
        Get list of available MQTT client names from Registry Manager
        
        Returns:
            List of active client names
        """
        if self._registry_manager:
            active_clients = self._registry_manager.get_active_mqtt_clients()
            return list(active_clients.keys())
        else:
            # Fallback: Return hardcoded list
            return [
                'admin_mqtt_client',
                'ccu_mqtt_client',
                'nodered_pub_mqtt_client',
                'nodered_sub_mqtt_client'
            ]


# Singleton Factory
def get_client_factory() -> ClientFactory:
    """
    Factory-Funktion für ClientFactory Singleton
    
    Returns:
        ClientFactory Singleton Instance
    """
    return ClientFactory()