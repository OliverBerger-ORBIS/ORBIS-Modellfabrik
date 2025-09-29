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
from omf2.ui.main_dashboard import MainDashboard
from omf2.ui.utils.ui_refresh import request_refresh, consume_refresh

# Configure logging
logger = get_logger("omf2.dashboard")

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
        
        # Initialize client factory in session state
        if 'client_factory' not in st.session_state:
            st.session_state['client_factory'] = get_client_factory()
        
        # Initialize admin MQTT client immediately (like old dashboard)
        if 'admin_mqtt_client' not in st.session_state:
            from omf2.admin.admin_mqtt_client import get_admin_mqtt_client
            st.session_state['admin_mqtt_client'] = get_admin_mqtt_client()
            logger.info("🔌 Admin MQTT Client initialized on startup")
        
        # Initialize log buffer with RingBufferHandler (like old dashboard)
        if 'log_buffer' not in st.session_state:
            from collections import deque
            from omf2.common.streamlit_log_buffer import RingBufferHandler, create_log_buffer
            
            # Create ring buffer
            st.session_state['log_buffer'] = create_log_buffer(maxlen=1000)
            logger.info("📋 Log buffer initialized")
            
            # Setup RingBufferHandler for all loggers
            ring_handler = RingBufferHandler(st.session_state['log_buffer'])
            ring_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
            
            # Add handler to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(ring_handler)
            st.session_state['ring_buffer_handler'] = ring_handler
            
            # Add some initial logs
            logger.info("🚀 OMF2 Dashboard started")
            logger.info("🔌 Admin MQTT Client initialized")
            logger.info("📊 Main Dashboard rendered")
        
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