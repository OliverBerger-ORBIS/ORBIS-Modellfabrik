"""
APS Configuration Tab - Haupt-Tab für APS-Konfiguration
Wrapper für Factory Configuration und System Configuration
"""

import streamlit as st
import json
import yaml
from pathlib import Path
from omf.dashboard.tools.logging_config import get_logger
from omf.dashboard.tools.path_constants import CONFIG_DIR
from omf.dashboard.utils.ui_refresh import request_refresh

logger = get_logger("omf.dashboard.components.operator.aps_configuration")
logger.info("🔍 LOADED: operator.aps_configuration")


def show_aps_configuration():
    """Zeigt den APS Configuration Tab mit Untertabs"""
    st.header("⚙️ APS Configuration")
    
    # Untertabs für Configuration
    tab1, tab2 = st.tabs(["🏭 Factory Configuration", "⚙️ Configuration"])
    
    with tab1:
        _show_factory_configuration_section()
    
    with tab2:
        _show_system_configuration_section()


def _show_factory_configuration_section():
    """Zeigt die Factory Configuration (nutzt bestehende shopfloor_layout.py)"""
    st.subheader("🏭 Factory Configuration")
    st.write("Modul-Anordnung und Verbindungen im Shopfloor-Layout")
    
    # Factory Configuration Controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("📥 Load Factory Layout", use_container_width=True):
            _load_factory_layout()
    
    with col2:
        if st.button("💾 Save Factory Layout", use_container_width=True):
            _save_factory_layout()
    
    with col3:
        if st.button("🔄 Reset to Default", use_container_width=True):
            _reset_factory_layout()
    
    st.divider()
    
    try:
        # Importiere die bestehende shopfloor_layout Komponente
        from omf.dashboard.components.operator.shopfloor_layout import show_shopfloor_layout
        
        # Zeige das Shopfloor-Layout
        show_shopfloor_layout()
        
        logger.info("Factory Configuration erfolgreich angezeigt")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Factory Configuration: {e}")
        logger.error(f"Fehler beim Laden der Factory Configuration: {e}")


def _show_system_configuration_section():
    """Zeigt die System Configuration (einfache Parameter)"""
    st.subheader("⚙️ Configuration")
    st.write("Einfache Parameter für Produktion, Transport und Gesamtdauer")
    
    try:
        # Importiere die neue System Configuration Komponente
        from omf.dashboard.components.operator.aps_system_configuration import show_aps_system_configuration
        
        # Zeige die System Configuration
        show_aps_system_configuration()
        
        logger.info("System Configuration erfolgreich angezeigt")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der System Configuration: {e}")
        logger.error(f"Fehler beim Laden der System Configuration: {e}")


def _load_factory_layout():
    """Lädt die Factory Layout Konfiguration"""
    try:
        # Lade aus OMF YAML-Format
        yaml_path = CONFIG_DIR / "shopfloor" / "layout.yml"
        if yaml_path.exists():
            with open(yaml_path, 'r', encoding='utf-8') as file:
                layout_data = yaml.safe_load(file)
                st.success("✅ Factory Layout aus YAML geladen")
                logger.info(f"Factory Layout aus {yaml_path} geladen")
                return layout_data
        
        # Fallback: Lade aus Original APS JSON-Format
        json_path = CONFIG_DIR / "factory-layout.json"
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as file:
                layout_data = json.load(file)
                st.success("✅ Factory Layout aus JSON geladen")
                logger.info(f"Factory Layout aus {json_path} geladen")
                return layout_data
        
        st.warning("⚠️ Keine Factory Layout Datei gefunden")
        return None
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Factory Layout: {e}")
        logger.error(f"Fehler beim Laden der Factory Layout: {e}")
        return None


def _save_factory_layout():
    """Speichert die Factory Layout Konfiguration"""
    try:
        # Lade aktuelle Layout-Daten
        layout_data = _load_factory_layout()
        if not layout_data:
            st.error("❌ Keine Layout-Daten zum Speichern gefunden")
            return
        
        # Speichere in YAML-Format (OMF Standard)
        yaml_path = CONFIG_DIR / "shopfloor" / "layout.yml"
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(yaml_path, 'w', encoding='utf-8') as file:
            yaml.dump(layout_data, file, default_flow_style=False, allow_unicode=True, indent=2)
        
        # Speichere auch in JSON-Format (APS Kompatibilität)
        json_path = CONFIG_DIR / "factory-layout.json"
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(layout_data, file, indent=2, ensure_ascii=False)
        
        st.success("✅ Factory Layout gespeichert (YAML + JSON)")
        logger.info(f"Factory Layout in {yaml_path} und {json_path} gespeichert")
        
        # UI-Refresh Pattern
        request_refresh()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Speichern der Factory Layout: {e}")
        logger.error(f"Fehler beim Speichern der Factory Layout: {e}")


def _reset_factory_layout():
    """Setzt die Factory Layout auf Standardwerte zurück"""
    try:
        # Lade Standard-Layout aus Original APS
        default_path = Path("integrations/ff-central-control-unit/central-control/data/factory-layout.json.default")
        
        if default_path.exists():
            with open(default_path, 'r', encoding='utf-8') as file:
                default_data = json.load(file)
            
            # Speichere als aktuelle Konfiguration
            yaml_path = CONFIG_DIR / "shopfloor" / "layout.yml"
            yaml_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Konvertiere JSON zu YAML-Format
            yaml_data = _convert_json_to_yaml_layout(default_data)
            
            with open(yaml_path, 'w', encoding='utf-8') as file:
                yaml.dump(yaml_data, file, default_flow_style=False, allow_unicode=True, indent=2)
            
            st.success("✅ Factory Layout auf Standardwerte zurückgesetzt")
            logger.info("Factory Layout auf Standardwerte zurückgesetzt")
            
            # UI-Refresh Pattern
            request_refresh()
        else:
            st.error("❌ Standard-Layout Datei nicht gefunden")
            
    except Exception as e:
        st.error(f"❌ Fehler beim Zurücksetzen der Factory Layout: {e}")
        logger.error(f"Fehler beim Zurücksetzen der Factory Layout: {e}")


def _convert_json_to_yaml_layout(json_data):
    """Konvertiert JSON-Layout zu YAML-Layout Format"""
    # Diese Funktion würde das JSON-Format in das YAML-Format konvertieren
    # Für jetzt geben wir die JSON-Daten zurück
    return json_data