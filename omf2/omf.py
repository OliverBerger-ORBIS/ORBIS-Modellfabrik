#!/usr/bin/env python3
"""
OMF2 Dashboard - Main Streamlit Application
ORBIS Modellfabrik - Modern Streamlit-based Dashboard

Entry point for the omf2 Streamlit dashboard application.
Follows the architecture defined in projekt-struktur-omf2.md
"""

from __future__ import annotations

import logging
import sys
import atexit
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st

from omf2.common.i18n import I18nManager
from omf2.common.logger import get_logger
from omf2.factory.client_factory import get_client_factory
from omf2.factory.gateway_factory import get_gateway_factory
from omf2.ui.main_dashboard import MainDashboard
from omf2.ui.utils.ui_refresh import request_refresh, consume_refresh

from omf2.common.logger import setup_multilevel_ringbuffer_logging

# BEST PRACTICE: Frühe Initialisierung vor erstem logger.info()
if 'log_handler' not in st.session_state:
    handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler
    st.session_state['log_buffers'] = buffers

# Configure logging
from omf2.common.logger import setup_file_logging
log_dir = setup_file_logging()
logger = get_logger("omf2.dashboard")
logger.info(f"📝 OMF2 Logging aktiviert: {log_dir}")

# Configure logging levels for OMF2 modules
import logging
from omf2.common.logging_config import apply_logging_config

# Apply logging configuration from YAML file
apply_logging_config()
logger.info("📋 Logging configuration applied from config file")

# KRITISCH: Nach apply_logging_config() Handler-Attachment verifizieren
from omf2.common.logging_config import _ensure_multilevel_handler_attached
_ensure_multilevel_handler_attached()
logger.info("✅ Logging handler attachment verified after config apply")

def cleanup_resources():
    """Cleanup resources on application exit"""
    try:
        logger.info("🧹 Cleaning up resources on exit...")
        
        # Disconnect MQTT clients
        if 'admin_mqtt_client' in st.session_state:
            admin_client = st.session_state.get('admin_mqtt_client')
            if admin_client and hasattr(admin_client, 'disconnect'):
                admin_client.disconnect()
                logger.info("🔌 Admin MQTT Client disconnected")
        
        # Disconnect CCU MQTT client (EXACT same pattern as Admin)
        if 'ccu_mqtt_client' in st.session_state:
            ccu_client = st.session_state.get('ccu_mqtt_client')
            if ccu_client and hasattr(ccu_client, 'disconnect'):
                ccu_client.disconnect()
                logger.info("🏗️ CCU MQTT Client disconnected")
        
        # Clear session state
        st.session_state.clear()
        logger.info("🧹 Session state cleared")
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")

# Register cleanup function (signal handlers don't work in Streamlit)
atexit.register(cleanup_resources)

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="OMF2 Dashboard - ORBIS Modellfabrik",
        page_icon="🏭",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik',
            'Report a bug': 'https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/issues',
            'About': "OMF2 Dashboard - ORBIS Modellfabrik Factory Management System"
        }
    )

def initialize_session_state():
    """Initialize Streamlit session state with default values - EXACT like old dashboard"""
    defaults = {
        'user_role': 'administrator',  # DEFAULT: Administrator
        'current_language': 'de',
        'current_environment': 'mock',  # DEFAULT: Mock (stabiler)
        'initialized': False,
        'mqtt_clients': {},
        'ui_managers': {}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    """Main application function"""
    try:
        # TODO: MQTT Client Probleme für nodered_pub/nodered_sub vermeiden:
        # 1. Registry-Struktur: mqtt_clients.get('client_name', {}) NICHT mqtt_clients.get('mqtt_clients', {}).get('client_name', {})
        # 2. Environment-Switch: reconnect_environment() mit Switch-Logging implementieren
        # 3. Connection Loop: Topics aus Registry laden, Try-catch um Subscription
        # 4. Admin Client: Wildcard "#" durch Registry-Liste ersetzen
        
        # Setup page configuration
        setup_page_config()
        
        # Initialize session state
        initialize_session_state()
        
        # Handle UI refresh requests (only place where st.rerun() is allowed)
        if consume_refresh():
            st.rerun()
            return
        
        # Initialize logging for this session
        if not st.session_state.get('logging_initialized', False):
            logger.info("🚀 Starting OMF2 Dashboard session")
            st.session_state['logging_initialized'] = True
        
        # Initialize I18n manager in session state
        if 'i18n_manager' not in st.session_state:
            st.session_state['i18n_manager'] = I18nManager()
        
        # Initialize Registry Manager (Singleton - nur einmal initialisiert)
        if 'registry_manager' not in st.session_state:
            from omf2.registry.manager.registry_manager import get_registry_manager, RegistryManager
            # Reset singleton to use new path
            RegistryManager._instance = None
            RegistryManager._initialized = False
            st.session_state['registry_manager'] = get_registry_manager("omf2/registry/")
            logger.info("📚 Registry Manager initialized on startup")
        
        # Initialize Client Factory and connect to Registry Manager
        if 'client_factory' not in st.session_state:
            client_factory = get_client_factory()
            client_factory.set_registry_manager(st.session_state['registry_manager'])
            st.session_state['client_factory'] = client_factory
            logger.info("🏭 Client Factory initialized with Registry Manager")
        
        # Initialize Gateway Factory
        if 'gateway_factory' not in st.session_state:
            st.session_state['gateway_factory'] = get_gateway_factory()
            logger.info("🏭 Gateway Factory initialized")
        
        # Initialize admin MQTT client via Client Factory (based on Registry)
        if 'admin_mqtt_client' not in st.session_state:
            client_factory = st.session_state['client_factory']
            admin_client = client_factory.get_mqtt_client('admin_mqtt_client')
            if admin_client:
                st.session_state['admin_mqtt_client'] = admin_client
                logger.info("🔌 Admin MQTT Client initialized via Client Factory")
            else:
                logger.error("❌ Failed to initialize Admin MQTT Client")
        
        # Initialize CCU MQTT client via Client Factory (EXACT same pattern as Admin)
        if 'ccu_mqtt_client' not in st.session_state:
            client_factory = st.session_state['client_factory']
            ccu_client = client_factory.get_mqtt_client('ccu_mqtt_client')
            if ccu_client:
                st.session_state['ccu_mqtt_client'] = ccu_client
                logger.info("🏗️ CCU MQTT Client initialized via Client Factory")
            else:
                logger.error("❌ Failed to initialize CCU MQTT Client")
        
        # Connect to MQTT (central connection for entire app)
        admin_client = st.session_state['admin_mqtt_client']
        current_env = st.session_state.get('current_environment', 'mock')
        if not admin_client.connected:
            admin_client.connect(current_env)
            logger.info(f"🔌 Admin MQTT Client connected to {current_env} on startup")
        
        # Connect CCU MQTT client (EXACT same pattern as Admin)
        ccu_client = st.session_state['ccu_mqtt_client']
        if not ccu_client.connected:
            ccu_client.connect(current_env)
            logger.info(f"🏗️ CCU MQTT Client connected to {current_env} on startup")
        
        # Create and render main dashboard
        if 'main_dashboard' not in st.session_state:
            st.session_state['main_dashboard'] = MainDashboard()
        
        # Render the dashboard
        st.session_state['main_dashboard'].render()
        
    except Exception as e:
        logger.error(f"❌ Dashboard initialization error: {e}")
        st.error(f"❌ Dashboard initialization failed: {e}")
        st.info("💡 Please check the logs for more details and try refreshing the page.")

if __name__ == "__main__":
    main()