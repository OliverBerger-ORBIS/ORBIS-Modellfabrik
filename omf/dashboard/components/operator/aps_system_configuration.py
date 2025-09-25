"""
APS System Configuration - Einfache Parameter für Produktion, Transport und Gesamtdauer
Entspricht dem "Configuration" Untertab des Original APS-Dashboards
"""

import streamlit as st
import yaml
from datetime import datetime
from pathlib import Path
from omf.dashboard.tools.logging_config import get_logger
from omf.dashboard.tools.path_constants import CONFIG_DIR
from omf.dashboard.utils.ui_refresh import request_refresh

logger = get_logger("omf.dashboard.components.operator.aps_system_configuration")
logger.info("🔍 LOADED: operator.aps_system_configuration")


def show_aps_system_configuration():
    """Zeigt die APS System Configuration mit 3 Parameter-Bereichen"""
    
    # Initialisiere Session State für Konfigurationswerte
    _init_configuration_state()
    
    # 1. Total Duration (Gesamtdauer)
    _show_total_duration_section()
    
    st.divider()
    
    # 2. Production Settings (Produktionseinstellungen)
    _show_production_settings_section()
    
    st.divider()
    
    # 3. Transport Settings (Transporteinstellungen)
    _show_transport_settings_section()
    
    st.divider()
    
    # Save Button
    _show_save_button()


def _init_configuration_state():
    """Initialisiert die Session State für Konfigurationswerte"""
    if "aps_configuration" not in st.session_state:
        # Lade Konfiguration aus Datei oder verwende Standardwerte
        config = _load_configuration_from_file()
        if config:
            st.session_state.aps_configuration = config
            logger.info("APS Configuration aus Datei geladen")
        else:
            st.session_state.aps_configuration = _get_default_configuration()
            logger.info("APS Configuration mit Standardwerten initialisiert")


def _show_total_duration_section():
    """Zeigt den Total Duration Bereich"""
    st.subheader("⏱️ Total Duration (Gesamtdauer)")
    st.write("Gesamtdauer für verschiedene Werkstück-Typen")
    
    # 3 Spalten für die 3 Werkstück-Typen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔵 Blue Workpiece**")
        st.image("https://via.placeholder.com/40x40/0066CC/FFFFFF?text=B", width=40)
        white_duration = st.number_input(
            "Duration (seconds)",
            min_value=0,
            max_value=3600,
            value=st.session_state.aps_configuration["total_duration"]["blue"],
            key="blue_duration",
            help="Gesamtdauer für blaue Werkstücke in Sekunden"
        )
        st.session_state.aps_configuration["total_duration"]["blue"] = white_duration
    
    with col2:
        st.markdown("**🔴 Red Workpiece**")
        st.image("https://via.placeholder.com/40x40/CC0000/FFFFFF?text=R", width=40)
        red_duration = st.number_input(
            "Duration (seconds)",
            min_value=0,
            max_value=3600,
            value=st.session_state.aps_configuration["total_duration"]["red"],
            key="red_duration",
            help="Gesamtdauer für rote Werkstücke in Sekunden"
        )
        st.session_state.aps_configuration["total_duration"]["red"] = red_duration
    
    with col3:
        st.markdown("**⚪ White Workpiece**")
        st.image("https://via.placeholder.com/40x40/FFFFFF/000000?text=W", width=40)
        white_duration = st.number_input(
            "Duration (seconds)",
            min_value=0,
            max_value=3600,
            value=st.session_state.aps_configuration["total_duration"]["white"],
            key="white_duration",
            help="Gesamtdauer für weiße Werkstücke in Sekunden"
        )
        st.session_state.aps_configuration["total_duration"]["white"] = white_duration


def _show_production_settings_section():
    """Zeigt den Production Settings Bereich"""
    st.subheader("🏭 Production Settings (Produktionseinstellungen)")
    st.write("Einstellungen für die Produktion")
    
    # Number of simultaneously producible workpieces
    simultaneous_workpieces = st.number_input(
        "Number of simultaneously producible workpieces",
        min_value=1,
        max_value=10,
        value=st.session_state.aps_configuration["production_settings"]["simultaneous_workpieces"],
        key="simultaneous_workpieces",
        help="Anzahl der gleichzeitig produzierbaren Werkstücke"
    )
    st.session_state.aps_configuration["production_settings"]["simultaneous_workpieces"] = simultaneous_workpieces


def _show_transport_settings_section():
    """Zeigt den Transport Settings Bereich"""
    st.subheader("🚚 Transport Settings (Transporteinstellungen)")
    st.write("Einstellungen für den Transport")
    
    # Charging threshold for AGV
    charging_threshold = st.number_input(
        "Charging threshold for AGV (%)",
        min_value=0,
        max_value=100,
        value=st.session_state.aps_configuration["transport_settings"]["charging_threshold"],
        key="charging_threshold",
        help="Ladungsschwelle für AGV in Prozent"
    )
    st.session_state.aps_configuration["transport_settings"]["charging_threshold"] = charging_threshold


def _show_save_button():
    """Zeigt den Save Button"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("💾 Save Configuration", type="primary", use_container_width=True):
            _save_configuration()


def _save_configuration():
    """Speichert die Konfiguration"""
    try:
        config = st.session_state.aps_configuration
        
        # Speichere in YAML-Datei
        _save_configuration_to_file(config)
        
        # Logging der gespeicherten Konfiguration
        logger.info(f"APS Configuration gespeichert: {config}")
        
        # Erfolgsmeldung
        st.success("✅ Configuration erfolgreich gespeichert!")
        
        # Zeige die gespeicherten Werte
        with st.expander("📋 Gespeicherte Konfiguration"):
            st.json(config)
        
        # UI-Refresh Pattern
        request_refresh()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Speichern der Konfiguration: {e}")
        logger.error(f"Fehler beim Speichern der APS Configuration: {e}")


def _get_default_configuration():
    """Gibt die Standard-Konfiguration zurück"""
    return {
        "total_duration": {
            "white": 580,  # Sekunden
            "blue": 550,   # Sekunden
            "red": 560     # Sekunden
        },
        "production_settings": {
            "simultaneous_workpieces": 4
        },
        "transport_settings": {
            "charging_threshold": 10  # Prozent
        },
        "metadata": {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "description": "APS System Configuration"
        }
    }


def _load_configuration_from_file():
    """Lädt die Konfiguration aus der YAML-Datei"""
    try:
        config_path = CONFIG_DIR / "aps_system_configuration.yml"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"APS Configuration aus {config_path} geladen")
                return config
        else:
            logger.info(f"APS Configuration Datei {config_path} nicht gefunden")
            return None
            
    except Exception as e:
        logger.error(f"Fehler beim Laden der APS Configuration: {e}")
        return None


def _save_configuration_to_file(config):
    """Speichert die Konfiguration in die YAML-Datei"""
    try:
        # Erstelle Config-Verzeichnis falls es nicht existiert
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        config_path = CONFIG_DIR / "aps_system_configuration.yml"
        
        # Aktualisiere Metadaten
        config["metadata"]["last_updated"] = datetime.now().isoformat()
        
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False, allow_unicode=True, indent=2)
            
        logger.info(f"APS Configuration in {config_path} gespeichert")
        
    except Exception as e:
        logger.error(f"Fehler beim Speichern der APS Configuration: {e}")
        raise


def get_configuration():
    """Gibt die aktuelle Konfiguration zurück"""
    if "aps_configuration" not in st.session_state:
        _init_configuration_state()
    
    return st.session_state.aps_configuration


def set_configuration(config):
    """Setzt die Konfiguration"""
    st.session_state.aps_configuration = config
    logger.info(f"APS Configuration gesetzt: {config}")


def reset_configuration():
    """Setzt die Konfiguration auf Standardwerte zurück"""
    _init_configuration_state()
    logger.info("APS Configuration auf Standardwerte zurückgesetzt")
