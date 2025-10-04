#!/usr/bin/env python3
"""
Logging Configuration for OMF2 Dashboard
Simple configuration interface for adjusting log levels
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any

def load_logging_config() -> Dict[str, Any]:
    """Load logging configuration from YAML file"""
    config_path = Path(__file__).parent.parent / "config" / "logging_config.yml"
    
    if not config_path.exists():
        # Return default configuration
        return {
            "global": {"level": "INFO", "buffer_size": 1000, "file_logging": True},
            "modules": {
                "omf2": {"level": "INFO"},
                "omf2.ccu": {"level": "INFO"},
                "omf2.admin": {"level": "INFO"},
                "omf2.common": {"level": "INFO"},
                "omf2.ui": {"level": "INFO"},
                "omf2.nodered": {"level": "INFO"}
            },
            "business_managers": {
                "sensor_manager": {"level": "INFO"},
                "module_manager": {"level": "INFO"}
            },
            "mqtt_clients": {
                "admin_mqtt_client": {"level": "INFO"},
                "ccu_mqtt_client": {"level": "INFO"}
            }
        }
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Failed to load logging config: {e}")
        return {}

def apply_logging_config():
    """Apply logging configuration from YAML file"""
    config = load_logging_config()
    
    # Apply global level
    global_level = config.get("global", {}).get("level", "INFO")
    logging.getLogger().setLevel(getattr(logging, global_level.upper()))
    
    # Apply module-specific levels
    modules = config.get("modules", {})
    for module_name, module_config in modules.items():
        level = module_config.get("level", "INFO")
        logging.getLogger(module_name).setLevel(getattr(logging, level.upper()))
    
    # Apply business manager levels
    business_managers = config.get("business_managers", {})
    for manager_name, manager_config in business_managers.items():
        level = manager_config.get("level", "INFO")
        # Business managers use omf2.ccu logger
        logging.getLogger(f"omf2.ccu.{manager_name}").setLevel(getattr(logging, level.upper()))
    
    # Apply MQTT client levels
    mqtt_clients = config.get("mqtt_clients", {})
    for client_name, client_config in mqtt_clients.items():
        level = client_config.get("level", "INFO")
        # MQTT clients use omf2.admin or omf2.ccu logger
        if "admin" in client_name:
            logging.getLogger(f"omf2.admin.{client_name}").setLevel(getattr(logging, level.upper()))
        else:
            logging.getLogger(f"omf2.ccu.{client_name}").setLevel(getattr(logging, level.upper()))

def set_debug_mode(module: str = None, enabled: bool = True):
    """Quick function to enable/disable debug logging for specific modules"""
    level = logging.DEBUG if enabled else logging.INFO
    
    if module:
        # Specific module
        if module.startswith("omf2."):
            logging.getLogger(module).setLevel(level)
        else:
            logging.getLogger(f"omf2.{module}").setLevel(level)
    else:
        # All OMF2 modules
        for logger_name in ["omf2", "omf2.ccu", "omf2.admin", "omf2.common", "omf2.ui", "omf2.nodered"]:
            logging.getLogger(logger_name).setLevel(level)

def get_current_log_levels() -> Dict[str, str]:
    """Get current logging levels for all OMF2 modules"""
    levels = {}
    for logger_name in ["omf2", "omf2.ccu", "omf2.admin", "omf2.common", "omf2.ui", "omf2.nodered"]:
        logger = logging.getLogger(logger_name)
        levels[logger_name] = logging.getLevelName(logger.level)
    return levels

# Quick access functions
def enable_debug_logging():
    """Enable debug logging for all modules"""
    set_debug_mode(enabled=True)

def disable_debug_logging():
    """Disable debug logging for all modules"""
    set_debug_mode(enabled=False)

def enable_sensor_debug():
    """Enable debug logging for sensor manager"""
    set_debug_mode("omf2.ccu.sensor_manager", True)

def enable_module_debug():
    """Enable debug logging for module manager"""
    set_debug_mode("omf2.ccu.module_manager", True)

def enable_mqtt_debug():
    """Enable debug logging for MQTT clients"""
    set_debug_mode("omf2.ccu.ccu_mqtt_client", True)
    set_debug_mode("omf2.admin.admin_mqtt_client", True)
