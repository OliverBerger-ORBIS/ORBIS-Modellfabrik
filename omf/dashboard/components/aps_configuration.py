"""
APS Configuration Dashboard - Wrapper für alle APS-Configuration-Funktionen
Hauptkomponente für alle APS-Configuration-Funktionen mit Untertabs
"""

import streamlit as st

from .aps_configuration_controllers import show_aps_configuration_controllers
from .aps_configuration_mqtt import show_aps_configuration_mqtt
from .aps_configuration_system import show_aps_configuration_system
from .aps_configuration_monitoring import show_aps_configuration_monitoring

def show_aps_configuration():
    """Hauptfunktion für die APS Configuration mit Untertabs"""
    st.header("⚙️ APS Configuration")
    st.markdown("Konfiguration und Einstellungen für die APS")
    
    # Untertabs für verschiedene APS-Configuration-Bereiche
    aps_config_tab1, aps_config_tab2, aps_config_tab3, aps_config_tab4 = st.tabs(
        ["🎮 Controller Config", "📡 MQTT Config", "🔧 System Config", "📊 Monitoring Config"]
    )
    
    # Tab 1: Controller Config
    with aps_config_tab1:
        show_aps_configuration_controllers()
    
    # Tab 2: MQTT Config
    with aps_config_tab2:
        show_aps_configuration_mqtt()
    
    # Tab 3: System Config
    with aps_config_tab3:
        show_aps_configuration_system()
    
    # Tab 4: Monitoring Config
    with aps_config_tab4:
        show_aps_configuration_monitoring()