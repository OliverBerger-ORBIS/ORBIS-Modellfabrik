#!/usr/bin/env python3
"""
Session Manager - Streamlit Dashboard
Verwaltung und Analyse von MQTT-Sessions für die ORBIS Modellfabrik
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src_orbis to path for imports
current_dir = Path(__file__).parent
src_orbis_path = current_dir.parent.parent.parent
if str(src_orbis_path) not in sys.path:
    sys.path.insert(0, str(src_orbis_path))

# Import components
from src_orbis.helper_apps.session_manager.components.replay_station import show_replay_station
from src_orbis.helper_apps.session_manager.components.session_analysis import show_session_analysis
from src_orbis.helper_apps.session_manager.components.session_recorder import show_session_recorder
from src_orbis.helper_apps.session_manager.components.template_analysis import show_template_analysis

# Page configuration
st.set_page_config(
    page_title="Session Manager",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Hauptfunktion des Session Managers"""
    
    # Header
    st.title("🎙️ Session Manager")
    st.markdown("Verwaltung und Analyse von MQTT-Sessions für die ORBIS Modellfabrik")
    
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    
    # Tab selection
    tab = st.sidebar.selectbox(
        "Wähle einen Tab:",
        [
            "📡 Replay Station",
            "📊 Session Analyse", 
            "🎙️ Session Recorder",
            "🔍 Template Analyse"
        ]
    )
    
    # Tab content
    if tab == "📡 Replay Station":
        show_replay_station()
    elif tab == "📊 Session Analyse":
        show_session_analysis()
    elif tab == "🎙️ Session Recorder":
        show_session_recorder()
    elif tab == "🔍 Template Analyse":
        show_template_analysis()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Session Manager v1.0.0**")
    st.sidebar.markdown("ORBIS Modellfabrik")

if __name__ == "__main__":
    main()
