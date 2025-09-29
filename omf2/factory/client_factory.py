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
        self._initialized = True
    
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
    
    def get_mqtt_client(self, domain: str, environment: str = 'development') -> Optional[Any]:
        """
        Get MQTT client for a specific domain
        
        Args:
            domain: Domain name (e.g., 'ccu', 'nodered', 'message_center')
            environment: Environment name
        
        Returns:
            MQTT client instance or None
        """
        client_key = f"{domain}_{environment}"
        
        if client_key not in self._clients:
            try:
                # Import the specific MQTT client class
                if domain == 'ccu':
                    from omf2.ccu.ccu_mqtt_client import CCUMQTTClient
                    client_class = CCUMQTTClient
                elif domain == 'nodered':
                    from omf2.nodered.nodered_mqtt_client import NodeREDMqttClient
                    client_class = NodeREDMqttClient
                elif domain == 'nodered_pub':
                    from omf2.nodered.nodered_pub_mqtt_client import NodeREDPubMQTTClient
                    client_class = NodeREDPubMQTTClient
                elif domain == 'nodered_sub':
                    from omf2.nodered.nodered_sub_mqtt_client import NodeREDSubMQTTClient
                    client_class = NodeREDSubMQTTClient
                elif domain == 'admin':
                    from omf2.admin.admin_mqtt_client import AdminMQTTClient
                    client_class = AdminMQTTClient
                else:
                    logger.error(f"❌ Unknown domain: {domain}")
                    return None
                
                # Get environment-specific config
                env_config = self._config.get('environments', {}).get(environment, {})
                mqtt_config = {**self._config.get('mqtt', {}), **env_config.get('mqtt', {})}
                
                # Create client instance (Singleton pattern)
                # MQTT clients are singletons, so we don't pass config to constructor
                self._clients[client_key] = client_class()
                logger.info(f"✅ Created MQTT client for {domain} in {environment}")
                
            except ImportError as e:
                logger.error(f"❌ Failed to import {domain} client: {e}")
                return None
            except Exception as e:
                logger.error(f"❌ Failed to create {domain} client: {e}")
                return None
        
        return self._clients.get(client_key)
    
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


# Singleton Factory
def get_client_factory() -> ClientFactory:
    """
    Factory-Funktion für ClientFactory Singleton
    
    Returns:
        ClientFactory Singleton Instance
    """
    return ClientFactory()