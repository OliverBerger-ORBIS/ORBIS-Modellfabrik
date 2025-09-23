"""
APS Modules Tab - Modul-Übersicht und -Steuerung
Entspricht dem "Modules" Tab des Original APS-Dashboards
Basiert auf overview_module_status.py, aber im APS-Stil modernisiert
"""

import streamlit as st
import pandas as pd
from omf.dashboard.tools.logging_config import get_logger
from omf.dashboard.utils.ui_refresh import request_refresh

logger = get_logger("dashboard.components.aps_modules")


def show_aps_modules():
    """Zeigt den APS Modules Tab mit Tabellen-Layout und Aktions-Buttons"""
    st.header("🏭 APS Modules")
    st.write("Modul-Übersicht mit Status, Verbindungen und Aktionen")
    
    # Module Overview Controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Refresh Status", use_container_width=True):
            _refresh_module_status()
    
    with col2:
        if st.button("📊 Show Statistics", use_container_width=True):
            _show_module_statistics()
    
    with col3:
        if st.button("⚙️ Module Settings", use_container_width=True):
            _show_module_settings()
    
    st.divider()
    
    # Module Overview Table
    _show_module_overview_table()


def _refresh_module_status():
    """Aktualisiert den Modul-Status"""
    try:
        # UI-Refresh Pattern
        request_refresh()
        
        st.success("✅ Module Status aktualisiert")
        logger.info("Module Status manuell aktualisiert")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Aktualisieren des Module Status: {e}")
        logger.error(f"Fehler beim Aktualisieren des Module Status: {e}")


def _show_module_statistics():
    """Zeigt Modul-Statistiken"""
    try:
        # Importiere die bestehende overview_module_status Komponente
        from omf.dashboard.components.overview_module_status import show_overview_module_status
        
        # Zeige die Module-Statistiken
        show_overview_module_status()
        
        logger.info("Module Statistics erfolgreich angezeigt")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Module Statistics: {e}")
        logger.error(f"Fehler beim Laden der Module Statistics: {e}")


def _show_module_settings():
    """Zeigt Modul-Einstellungen"""
    st.subheader("⚙️ Module Settings")
    st.write("Erweiterte Einstellungen für Module")
    
    # Placeholder für zukünftige Module-Einstellungen
    st.info("🚧 Module Settings werden in zukünftigen Versionen implementiert")


def _show_module_overview_table():
    """Zeigt die Module Overview Tabelle im APS-Stil"""
    st.subheader("📊 Module Overview")
    
    try:
        # Importiere die bestehende overview_module_status Komponente
        from omf.dashboard.components.overview_module_status import get_static_module_info, _get_module_real_time_status
        
        # Get MQTT client from session state
        client = st.session_state.get("mqtt_client")
        if not client:
            st.error("❌ MQTT Client nicht verfügbar")
            return
        
        # Get static module information
        all_modules = get_static_module_info()
        
        if not all_modules:
            st.error("❌ Keine Module konfiguriert")
            return
        
        # Initialize module status store in session state
        if "module_status_store" not in st.session_state:
            st.session_state["module_status_store"] = {}
        
        # Per-Topic-Buffer für Modul-Status
        try:
            # Topics für Modul-Status abonnieren
            client.subscribe_many(
                ["module/v1/ff/+/state", "module/v1/ff/+/connection", "ccu/pairing/state", "module/v1/ff/+/factsheet"]
            )
            
            # Nachrichten aus Per-Topic-Buffer holen
            state_messages = list(client.get_buffer("module/v1/ff/+/state"))
            connection_messages = list(client.get_buffer("module/v1/ff/+/connection"))
            pairing_messages = list(client.get_buffer("ccu/pairing/state"))
            factsheet_messages = list(client.get_buffer("module/v1/ff/+/factsheet"))
            
            # Alle Messages zusammenfassen
            all_messages = state_messages + connection_messages + pairing_messages + factsheet_messages
            
            # Nachrichten verarbeiten
            from omf.dashboard.components.overview_module_status import _process_module_messages
            _process_module_messages(all_messages, st.session_state["module_status_store"])
            
        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden der MQTT-Nachrichten: {e}")
        
        # Get factory configuration for "Configured" status
        factory_config = _get_factory_configuration()
        
        # Create module table data with APS-style layout
        module_table_data = []
        
        for module_id, module_info in all_modules.items():
            # Skip disabled modules
            if not module_info.get("enabled", True):
                continue
            
            # Get real-time status from store
            real_time_status = _get_module_real_time_status(module_id, st.session_state["module_status_store"])
            
            # Get module icon
            icon_display = module_info.get("icon", _get_module_icon(module_id))
            
            # Get display name
            display_name = module_info.get("name_lang_de", module_info.get("name", module_id))
            
            # Status indicators - APS-style
            connected = real_time_status.get("connected", False)
            connection_display = "✅" if connected else "❌"
            
            # Availability-Status aus ccu/pairing/state mit grafischer Darstellung
            available = real_time_status.get("available", "Unknown")
            availability_display = _get_availability_display(available)
            
            # Configured status - aus Factory Configuration
            configured = _is_module_configured(module_info["id"], factory_config)
            configured_display = "✅" if configured else "❌"
            
            module_table_data.append(
                {
                    "ID": module_info["id"],
                    "Name": f"{icon_display} {display_name}",
                    "Connected": connection_display,
                    "Availability Status": availability_display,
                    "Configured": configured_display,
                    "Actions": _get_module_actions(module_id, available, configured)
                }
            )
        
        # Display module table in APS-style
        if module_table_data:
            module_df = pd.DataFrame(module_table_data)
            
            # Display table with APS-style formatting
            st.dataframe(
                module_df,
                use_container_width=True,
                column_config={
                    "ID": st.column_config.TextColumn("ID", width="medium"),
                    "Name": st.column_config.TextColumn("Name", width="large"),
                    "Connected": st.column_config.TextColumn("Connected", width="small"),
                    "Availability Status": st.column_config.TextColumn("Availability Status", width="medium"),
                    "Configured": st.column_config.TextColumn("Configured", width="small"),
                    "Actions": st.column_config.TextColumn("Actions", width="medium"),
                },
            )
            
            # Status wird automatisch aktualisiert
            st.success("✅ **Module Status wird automatisch aus MQTT-Nachrichten aktualisiert**")
            
        else:
            st.warning("⚠️ Keine aktiven Module gefunden")
            
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Module Overview: {e}")
        logger.error(f"Fehler beim Laden der Module Overview: {e}")


def _get_module_icon(module_name):
    """Get module icon from module name"""
    MODULE_ICONS = {
        "MILL": "⚙️", 
        "DRILL": "🔩", 
        "AIQS": "🤖", 
        "HBW": "🏬", 
        "DPS": "📦", 
        "FTS": "🚗", 
        "CHRG": "🔋"
    }
    return MODULE_ICONS.get(module_name.upper(), "❓")


def _get_availability_display(available):
    """Gibt die grafische Darstellung des Availability Status zurück"""
    if available == "READY":
        return "🟢 Available"
    elif available == "BUSY":
        return "🟡 Busy"
    elif available == "BLOCKED":
        return "🔴 Blocked"
    else:
        return f"⚪ {available}"


def _get_factory_configuration():
    """Lädt die Factory Configuration für Configured Status"""
    try:
        from omf.dashboard.tools.path_constants import CONFIG_DIR
        import yaml
        
        config_path = CONFIG_DIR / "shopfloor" / "layout.yml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        return None
    except Exception as e:
        logger.error(f"Fehler beim Laden der Factory Configuration: {e}")
        return None


def _is_module_configured(module_id, factory_config):
    """Prüft, ob ein Modul in der Factory Configuration konfiguriert ist"""
    if not factory_config:
        return False
    
    positions = factory_config.get("positions", [])
    for position in positions:
        if position.get("type") == "MODULE" and position.get("module_serial") == module_id:
            return position.get("enabled", False)
    
    return False


def _get_module_actions(module_id, availability, configured):
    """Gibt die verfügbaren Aktionen für ein Modul zurück"""
    actions = []
    
    # Calibrate Button für bestimmte Module (nur wenn nicht konfiguriert)
    if module_id in ["SVR3QA0022", "SVR4H73275", "SVR4H76530"]:  # HBW, DPS, AIQS
        if not configured:
            actions.append("Calibrate")
    
    # Finish charging Button für AGV (nur wenn BLOCKED)
    if module_id == "5iO4" and availability == "BLOCKED":
        actions.append("Finish charging")
    
    return ", ".join(actions) if actions else "None"


def get_module_status():
    """Gibt den aktuellen Modul-Status zurück"""
    if "module_status_store" not in st.session_state:
        return {}
    
    return st.session_state["module_status_store"]


def set_module_status(module_id, status_data):
    """Setzt den Status für ein bestimmtes Modul"""
    if "module_status_store" not in st.session_state:
        st.session_state["module_status_store"] = {}
    
    st.session_state["module_status_store"][module_id] = status_data
    logger.info(f"Module Status für {module_id} gesetzt: {status_data}")


def reset_module_status():
    """Setzt den Modul-Status zurück"""
    st.session_state["module_status_store"] = {}
    logger.info("Module Status zurückgesetzt")
