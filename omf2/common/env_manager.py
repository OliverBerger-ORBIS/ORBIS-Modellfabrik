"""
Environment Manager for OMF2
Manages environment switching (live, replay, mock) in sidebar
"""

import streamlit as st
import logging
from typing import Dict, Any


class EnvironmentManager:
    """
    Manages environment switching and configuration
    Integrates with sidebar for user selection
    """
    
    def __init__(self):
        self.logger = logging.getLogger("omf2.common.env_manager")
        
        # Initialize default environment in session state
        if "omf2_environment" not in st.session_state:
            st.session_state.omf2_environment = "mock"
            
        if "omf2_env_config" not in st.session_state:
            st.session_state.omf2_env_config = self._get_env_config("mock")
    
    def show_environment_selector(self) -> str:
        """
        Show environment selector in sidebar
        
        Returns:
            str: Selected environment
        """
        st.sidebar.subheader("🌍 Umgebung")
        
        environments = {
            "live": "🔴 Live System",
            "replay": "📼 Replay Mode", 
            "mock": "🧪 Mock/Test"
        }
        
        current_env = st.session_state.omf2_environment
        
        # Environment selector
        selected_env = st.sidebar.selectbox(
            "Aktuelle Umgebung:",
            options=list(environments.keys()),
            format_func=lambda x: environments[x],
            index=list(environments.keys()).index(current_env),
            key="env_selector"
        )
        
        # Check if environment changed
        if selected_env != current_env:
            self.logger.info(f"Environment switched from {current_env} to {selected_env}")
            st.session_state.omf2_environment = selected_env
            st.session_state.omf2_env_config = self._get_env_config(selected_env)
            
            # Show confirmation message
            st.sidebar.success(f"✅ Umgebung gewechselt zu: {environments[selected_env]}")
        
        # Show current environment info
        self._show_environment_info(selected_env)
        
        return selected_env
    
    def get_current_environment(self) -> str:
        """
        Get current environment
        
        Returns:
            str: Current environment
        """
        return st.session_state.get("omf2_environment", "mock")
    
    def get_environment_config(self) -> Dict[str, Any]:
        """
        Get current environment configuration
        
        Returns:
            Dict: Environment configuration
        """
        return st.session_state.get("omf2_env_config", self._get_env_config("mock"))
    
    def _get_env_config(self, env: str) -> Dict[str, Any]:
        """
        Get configuration for specific environment
        
        Args:
            env: Environment name
            
        Returns:
            Dict: Environment configuration
        """
        configs = {
            "live": {
                "name": "Live System",
                "description": "Produktions-System mit echten Daten",
                "mqtt_host": "192.168.0.100",
                "mqtt_port": 1883,
                "icon": "🔴",
                "color": "red"
            },
            "replay": {
                "name": "Replay Mode",
                "description": "Wiedergabe aufgezeichneter Daten",
                "mqtt_host": "localhost",
                "mqtt_port": 1884,
                "icon": "📼",
                "color": "orange"
            },
            "mock": {
                "name": "Mock/Test",
                "description": "Test-Umgebung mit simulierten Daten",
                "mqtt_host": "localhost", 
                "mqtt_port": 1883,
                "icon": "🧪",
                "color": "green"
            }
        }
        
        return configs.get(env, configs["mock"])
    
    def _show_environment_info(self, env: str):
        """
        Show environment information in sidebar
        
        Args:
            env: Current environment
        """
        config = self._get_env_config(env)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Umgebungs-Info:**")
        
        # Environment details
        st.sidebar.markdown(f"📊 **Name:** {config['name']}")
        st.sidebar.markdown(f"📝 **Beschreibung:** {config['description']}")
        st.sidebar.markdown(f"🌐 **MQTT Broker:** {config['mqtt_host']}:{config['mqtt_port']}")
        
        # Environment status indicator
        if env == "live":
            st.sidebar.error("⚠️ Produktions-System - Vorsicht bei Änderungen!")
        elif env == "replay":
            st.sidebar.warning("📼 Replay-Modus - Nur Lesezugriff")
        else:
            st.sidebar.success("🧪 Test-Umgebung - Sicher für Experimente")
    
    def show_connection_status(self, mqtt_gateway=None):
        """
        Show MQTT connection status in sidebar
        
        Args:
            mqtt_gateway: MQTT Gateway instance (optional)
        """
        st.sidebar.markdown("---")
        st.sidebar.subheader("📡 MQTT Status")
        
        if mqtt_gateway:
            status = mqtt_gateway.get_connection_status()
            
            if status["connected"]:
                st.sidebar.success("✅ Verbunden")
                st.sidebar.markdown(f"🏢 **Broker:** {status['broker']}")
                st.sidebar.markdown(f"🆔 **Client ID:** {status['client_id']}")
                
                # Message statistics
                messages = status.get("messages", {})
                if messages:
                    st.sidebar.markdown("**Nachrichten:**")
                    st.sidebar.markdown(f"📊 Total: {messages.get('total', 0)}")
                    st.sidebar.markdown(f"📤 Gesendet: {messages.get('sent', 0)}")
                    st.sidebar.markdown(f"📥 Empfangen: {messages.get('received', 0)}")
            else:
                st.sidebar.error("❌ Nicht verbunden")
                st.sidebar.markdown("🔄 Verbindung wird hergestellt...")
        else:
            st.sidebar.warning("⚠️ Gateway nicht initialisiert")
    
    def show_user_management(self):
        """Show user management in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("👤 Benutzer")
        
        # User role selector
        roles = ["Operator", "Supervisor", "Admin", "Developer"]
        current_role = st.session_state.get("omf2_user_role", "Operator")
        
        selected_role = st.sidebar.selectbox(
            "Benutzerrolle:",
            options=roles,
            index=roles.index(current_role) if current_role in roles else 0,
            key="user_role_selector"
        )
        
        if selected_role != current_role:
            st.session_state.omf2_user_role = selected_role
            st.sidebar.success(f"✅ Rolle gewechselt zu: {selected_role}")
        
        # User info
        st.sidebar.markdown(f"**Aktuelle Rolle:** {selected_role}")
        
        # Role-specific info
        role_permissions = {
            "Operator": "📋 Bedienung und Überwachung",
            "Supervisor": "👨‍💼 Konfiguration und Verwaltung",
            "Admin": "🔧 Vollzugriff auf alle Funktionen",
            "Developer": "💻 Entwicklung und Debug-Zugriff"
        }
        
        st.sidebar.markdown(f"**Berechtigungen:** {role_permissions.get(selected_role, 'Standard')}")
    
    def show_language_management(self):
        """Show language management in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("🌐 Sprache")
        
        languages = {
            "de": "🇩🇪 Deutsch",
            "en": "🇺🇸 English"
        }
        
        current_lang = st.session_state.get("omf2_language", "de")
        
        selected_lang = st.sidebar.selectbox(
            "Interface-Sprache:",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=list(languages.keys()).index(current_lang) if current_lang in languages else 0,
            key="language_selector"
        )
        
        if selected_lang != current_lang:
            st.session_state.omf2_language = selected_lang
            st.sidebar.success(f"✅ Sprache gewechselt zu: {languages[selected_lang]}")
    
    def show_complete_sidebar(self, mqtt_gateway=None):
        """
        Show complete sidebar with all management components
        
        Args:
            mqtt_gateway: MQTT Gateway instance (optional)
        """
        # Environment management
        current_env = self.show_environment_selector()
        
        # Connection status
        self.show_connection_status(mqtt_gateway)
        
        # User management
        self.show_user_management()
        
        # Language management  
        self.show_language_management()
        
        return current_env