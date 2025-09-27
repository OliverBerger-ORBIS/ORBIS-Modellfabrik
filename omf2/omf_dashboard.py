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
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st

from omf2.common.i18n import I18nManager
from omf2.common.logger import get_logger
from omf2.factory.client_factory import ClientFactory
from omf2.ui.main_dashboard import MainDashboard

# Configure logging
logger = get_logger("omf2.dashboard")

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
    """Initialize Streamlit session state with default values"""
    defaults = {
        'user_role': 'viewer',
        'current_language': 'de',
        'current_environment': 'development',
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
        
        # Initialize logging for this session
        if not st.session_state.get('logging_initialized', False):
            logger.info("🚀 Starting OMF2 Dashboard session")
            st.session_state['logging_initialized'] = True
        
        # Initialize I18n manager in session state
        if 'i18n_manager' not in st.session_state:
            st.session_state['i18n_manager'] = I18nManager()
        
        # Initialize client factory in session state
        if 'client_factory' not in st.session_state:
            st.session_state['client_factory'] = ClientFactory()
        
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