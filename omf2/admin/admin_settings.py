#!/usr/bin/env python3
"""
Admin Settings - System administration and configuration management
"""

import logging
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AdminSettings:
    """
    Admin Settings Manager - Handles system configuration and administration
    """
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path(__file__).parent.parent / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration files
        self.mqtt_settings_file = self.config_dir / "mqtt_settings.yml"
        self.user_roles_file = self.config_dir / "user_roles.yml"
        self.apps_file = self.config_dir / "apps.yml"
        
        logger.info(f"⚙️ Admin Settings initialized with config dir: {self.config_dir}")
    
    def load_mqtt_settings(self) -> Dict[str, Any]:
        """Load MQTT settings configuration"""
        try:
            if self.mqtt_settings_file.exists():
                with open(self.mqtt_settings_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                return self._get_default_mqtt_settings()
        except Exception as e:
            logger.error(f"❌ Failed to load MQTT settings: {e}")
            return self._get_default_mqtt_settings()
    
    def save_mqtt_settings(self, settings: Dict[str, Any]) -> bool:
        """Save MQTT settings configuration"""
        try:
            with open(self.mqtt_settings_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(settings, f, default_flow_style=False, allow_unicode=True)
            logger.info("✅ MQTT settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save MQTT settings: {e}")
            return False
    
    def load_user_roles(self) -> Dict[str, Any]:
        """Load user roles configuration"""
        try:
            if self.user_roles_file.exists():
                with open(self.user_roles_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                return self._get_default_user_roles()
        except Exception as e:
            logger.error(f"❌ Failed to load user roles: {e}")
            return self._get_default_user_roles()
    
    def save_user_roles(self, roles: Dict[str, Any]) -> bool:
        """Save user roles configuration"""
        try:
            with open(self.user_roles_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(roles, f, default_flow_style=False, allow_unicode=True)
            logger.info("✅ User roles saved successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save user roles: {e}")
            return False
    
    def load_apps_config(self) -> Dict[str, Any]:
        """Load apps configuration"""
        try:
            if self.apps_file.exists():
                with open(self.apps_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                return self._get_default_apps_config()
        except Exception as e:
            logger.error(f"❌ Failed to load apps config: {e}")
            return self._get_default_apps_config()
    
    def save_apps_config(self, apps_config: Dict[str, Any]) -> bool:
        """Save apps configuration"""
        try:
            with open(self.apps_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(apps_config, f, default_flow_style=False, allow_unicode=True)
            logger.info("✅ Apps config saved successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save apps config: {e}")
            return False
    
    def _get_default_mqtt_settings(self) -> Dict[str, Any]:
        """Get default MQTT settings"""
        return {
            "environments": {
                "live": {
                    "host": "localhost",
                    "port": 1883,
                    "username": "",
                    "password": "",
                    "client_id_prefix": "omf2_live",
                    "enabled": True
                },
                "replay": {
                    "host": "localhost",
                    "port": 1883,
                    "username": "",
                    "password": "",
                    "client_id_prefix": "omf2_replay",
                    "enabled": True
                },
                "mock": {
                    "host": "localhost",
                    "port": 1883,
                    "username": "",
                    "password": "",
                    "client_id_prefix": "omf2_mock",
                    "enabled": True
                }
            },
            "default_environment": "replay",
            "connection_timeout": 60,
            "keepalive": 60,
            "clean_session": True,
            "qos_default": 1
        }
    
    def _get_default_user_roles(self) -> Dict[str, Any]:
        """Get default user roles"""
        return {
            "roles": {
                "admin": {
                    "name": "Administrator",
                    "permissions": ["*"],
                    "description": "Full system access"
                },
                "operator": {
                    "name": "Operator",
                    "permissions": ["read", "control"],
                    "description": "System operation and control"
                },
            },
            "users": {
                "admin": {
                    "role": "admin",
                    "name": "System Administrator",
                    "active": True
                }
            },
            "default_role": "operator"
        }
    
    def _get_default_apps_config(self) -> Dict[str, Any]:
        """Get default apps configuration"""
        return {
            "apps": {
                "ccu_dashboard": {
                    "name": "CCU Dashboard",
                    "description": "Central Control Unit Dashboard",
                    "enabled": True,
                    "module": "omf2.ui.ccu.ccu_overview.ccu_overview_tab"
                },
                "system_logs": {
                    "name": "System Logs",
                    "description": "System log viewer and analysis",
                    "enabled": True,
                    "module": "omf2.ui.system.logs_tab"
                },
                "admin_settings": {
                    "name": "Admin Settings",
                    "description": "System administration and configuration",
                    "enabled": True,
                    "module": "omf2.ui.system.admin_settings_tab",
                    "required_role": "admin"
                }
            }
        }
    
    def get_environment_settings(self, environment: str) -> Optional[Dict[str, Any]]:
        """Get settings for specific environment"""
        mqtt_settings = self.load_mqtt_settings()
        environments = mqtt_settings.get("environments", {})
        return environments.get(environment)
    
    def get_available_environments(self) -> List[str]:
        """Get list of available environments"""
        mqtt_settings = self.load_mqtt_settings()
        environments = mqtt_settings.get("environments", {})
        return [env for env, config in environments.items() if config.get("enabled", True)]
    
    def get_user_permissions(self, username: str) -> List[str]:
        """Get permissions for specific user"""
        user_roles = self.load_user_roles()
        users = user_roles.get("users", {})
        user_info = users.get(username, {})
        
        if not user_info.get("active", False):
            return []
        
        role_name = user_info.get("role", user_roles.get("default_role", "operator"))
        roles = user_roles.get("roles", {})
        role_info = roles.get(role_name, {})
        
        return role_info.get("permissions", [])
    
    def has_permission(self, username: str, permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_user_permissions(username)
        return "*" in permissions or permission in permissions
    
    def get_enabled_apps(self, username: str = None) -> Dict[str, Any]:
        """Get enabled apps for user"""
        apps_config = self.load_apps_config()
        apps = apps_config.get("apps", {})
        enabled_apps = {}
        
        for app_id, app_config in apps.items():
            if not app_config.get("enabled", True):
                continue
            
            required_role = app_config.get("required_role")
            if required_role and username:
                if not self.has_permission(username, required_role):
                    continue
            
            enabled_apps[app_id] = app_config
        
        return enabled_apps