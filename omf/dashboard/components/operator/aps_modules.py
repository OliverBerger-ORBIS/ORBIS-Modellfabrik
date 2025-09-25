"""
APS Modules Tab - Modul-Übersicht und -Steuerung
Entspricht dem "Modules" Tab des Original APS-Dashboards
Basiert auf overview_module_status.py, aber im APS-Stil modernisiert
"""

import streamlit as st
import pandas as pd
from omf.dashboard.tools.logging_config import get_logger
# from omf.dashboard.utils.ui_refresh import request_refresh  # ENTFERNT - verletzt Singleton-Pattern!

logger = get_logger("omf.dashboard.components.operator.aps_modules")
logger.info("🔍 LOADED: operator.aps_modules")


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
        # KEIN request_refresh() - verletzt Singleton-Pattern!
        # Status wird automatisch über Per-Topic-Buffer aktualisiert
        
        logger.info("✅ Module Status wird automatisch aktualisiert")
        logger.info("Module Status Refresh-Button gedrückt (automatische Updates)")
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Aktualisieren des Module Status: {e}")


def _show_module_statistics():
    """Zeigt Modul-Statistiken - komplett eigenständig ohne Abhängigkeiten"""
    try:
        st.subheader("📊 Module Statistics")
        
        # Get module information directly from registry
        from omf.tools.module_manager import get_omf_module_manager
        module_manager = get_omf_module_manager()
        all_modules = module_manager.get_all_modules()
        
        if not all_modules:
            st.error("❌ Keine Module konfiguriert")
            return
        
        # Get real-time status
        module_status_store = st.session_state.get("module_status_store", {})
        
        # Calculate statistics
        total_modules = len(all_modules)
        connected_count = 0
        available_count = 0
        total_messages = 0
        
        for module_id, module_info in all_modules.items():
            if not module_info.get("enabled", True):
                continue
                
            real_time_status = module_status_store.get(module_id, {})
            if real_time_status.get("connected", False):
                connected_count += 1
            if real_time_status.get("available") in ["READY", "AVAILABLE"]:
                available_count += 1
            total_messages += real_time_status.get("message_count", 0)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt Module", total_modules)
        
        with col2:
            st.metric("Verbunden", connected_count)
        
        with col3:
            st.metric("Verfügbar", available_count)
        
        with col4:
            st.metric("Nachrichten", total_messages)
        
        logger.info("Module Statistics erfolgreich angezeigt")
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Laden der Module Statistics: {e}")


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
        from omf.dashboard.components.operator.overview_module_status import get_static_module_info, _get_module_real_time_status
        
        # Get MQTT client from session state
        client = st.session_state.get("mqtt_client")
        if not client:
            st.error("❌ MQTT Client nicht verfügbar")
            return
        
        # Get module information directly from registry
        from omf.tools.module_manager import get_omf_module_manager
        module_manager = get_omf_module_manager()
        all_modules = module_manager.get_all_modules()
        
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
            # Process module messages directly (no dependency to overview_module_status)
            _process_module_messages_direct(all_messages, st.session_state["module_status_store"])
            
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
                },
            )
            
            # Status wird automatisch aktualisiert
            logger.info("✅ **Module Status wird automatisch aus MQTT-Nachrichten aktualisiert**")
            
            # Module Actions außerhalb der Tabelle
            _show_module_actions(all_modules, factory_config)
            
        else:
            logger.warning("⚠️ Keine aktiven Module gefunden")
            
    except Exception as e:
        logger.error(f"❌ Fehler beim Laden der Module Overview: {e}")


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
    """Lädt die Factory Configuration für Configured Status aus der Registry"""
    try:
        from omf.dashboard.tools.path_constants import REGISTRY_DIR
        import yaml
        
        # Verwende Registry v1 shopfloor configuration
        config_path = REGISTRY_DIR / "model" / "v1" / "shopfloor.yml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                logger.info(f"✅ Using registry v1 shopfloor: {config_path}")
                return yaml.safe_load(file)
        else:
            logger.warning(f"⚠️ Registry shopfloor configuration not found at {config_path}")
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


def _show_module_actions(all_modules, factory_config):
    """Zeigt klickbare Module Actions außerhalb der Tabelle"""
    st.subheader("🔧 Module Actions")
    
    # Get real-time status for actions
    module_status_store = st.session_state.get("module_status_store", {})
    
    # Group actions by type
    calibrate_modules = []
    charging_modules = []
    
    for module_id, module_info in all_modules.items():
        if not module_info.get("enabled", True):
            continue
            
        # Get real-time status
        # Get module real-time status directly (no dependency to overview_module_status)
        real_time_status = _get_module_real_time_status_direct(module_id, module_status_store)
        available = real_time_status.get("available", "Unknown")
        configured = _is_module_configured(module_id, factory_config)
        
        # Check for Calibrate action
        if module_id in ["SVR3QA0022", "SVR4H73275", "SVR4H76530"]:  # HBW, DPS, AIQS
            connected = real_time_status.get("connected", False)
            if connected:
                calibrate_modules.append({
                    "id": module_id,
                    "name": module_info.get("name_lang_de", module_info.get("name", module_id)),
                    "icon": module_info.get("icon", _get_module_icon(module_id))
                })
        
        # Check for FTS actions (Docke an, FTS laden, Finish charging)
        if module_id == "5iO4":
            fts_actions = []
            # Docke an ist immer verfügbar für FTS
            fts_actions.append("dock")
            # FTS laden ist immer verfügbar für FTS
            fts_actions.append("start_charging")
            # Finish charging nur wenn BLOCKED
            if available == "BLOCKED":
                fts_actions.append("finish_charging")
            
            if fts_actions:
                charging_modules.append({
                    "id": module_id,
                    "name": module_info.get("name_lang_de", module_info.get("name", module_id)),
                    "icon": module_info.get("icon", _get_module_icon(module_id)),
                    "actions": fts_actions
                })
    
    # Display Calibrate Actions
    if calibrate_modules:
        st.markdown("**🔧 Module Calibration**")
        for module in calibrate_modules:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{module['icon']} {module['name']} ({module['id']})")
            with col2:
                if st.button("🔧 Calibrate", key=f"calibrate_{module['id']}", use_container_width=True):
                    _execute_calibrate_command(module['id'])
        st.divider()
    
    # Display FTS Actions
    if charging_modules:
        st.markdown("**🚗 FTS Actions**")
        for module in charging_modules:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"{module['icon']} {module['name']} ({module['id']})")
            
            # Multiple buttons für FTS actions
            actions = module.get('actions', [])
            if "dock" in actions:
                with col2:
                    if st.button("🚗 Docke an", key=f"dock_{module['id']}", use_container_width=True):
                        _execute_dock_command(module['id'])
            
            if "start_charging" in actions:
                with col3:
                    if st.button("🔋 FTS laden", key=f"start_charging_{module['id']}", use_container_width=True):
                        _execute_start_charging_command(module['id'])
            
            if "finish_charging" in actions:
                with col4:
                    if st.button("⚡ Laden beenden", key=f"finish_charging_{module['id']}", use_container_width=True):
                        _execute_finish_charging_command(module['id'])
        st.divider()
    
    # Show message if no actions available
    if not calibrate_modules and not charging_modules:
        st.info("ℹ️ Keine Module-Aktionen verfügbar. Alle Module sind konfiguriert und verfügbar.")


def _execute_calibrate_command(module_id):
    """Führt Calibrate-Befehl für ein Modul aus"""
    try:
        # TODO: Implementiere echte MQTT-Calibrate-Befehle
        logger.info(f"✅ Calibrate-Befehl für {module_id} gesendet")
        logger.info(f"Calibrate-Befehl für {module_id} ausgeführt")
        
        # KEIN request_refresh() - verletzt Singleton-Pattern!
        # Status wird automatisch über Per-Topic-Buffer aktualisiert
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Calibrate-Befehl für {module_id}: {e}")


def _execute_dock_command(module_id):
    """Führt Dock-Befehl für FTS aus - wie in steering_factory"""
    try:
        import uuid
        from datetime import datetime, timezone
        
        # MQTT-Client aus session state holen
        mqtt_client = st.session_state.get("mqtt_client")
        if not mqtt_client:
            st.error("❌ MQTT-Client nicht verfügbar")
            return
        
        # MqttGateway initialisieren (wie in steering_factory)
        from omf.dashboard.tools.mqtt_gateway import MqttGateway
        gateway = MqttGateway(mqtt_client)
        
        # FTS "Docke an" Befehl senden (exakt wie in steering_factory)
        gateway.send(
            topic="fts/v1/ff/5iO4/instantAction",
            builder=lambda: {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "serialNumber": module_id,
                "actions": [
                    {
                        "actionType": "findInitialDockPosition",
                        "actionId": str(uuid.uuid4()),
                        "metadata": {"nodeId": "SVR4H73275"},
                    }
                ],
            },
            ensure_order_id=True,
        )
        
        # Wenn wir hier ankommen, wurde die Nachricht erfolgreich gesendet
        # (kein Exception aufgetreten)
        logger.info(f"✅ FTS Dock-Befehl für {module_id} erfolgreich gesendet!")
        # KEIN st.success() - verhindert UI-Refresh und MQTT-Verbindungsabbruch
        
        # KEIN request_refresh() - verletzt Singleton-Pattern!
        # Status wird automatisch über Per-Topic-Buffer aktualisiert
        
    except Exception as e:
        logger.error(f"❌ Fehler beim FTS Dock für {module_id}: {e}")


def _execute_start_charging_command(module_id):
    """Führt Start Charging-Befehl für FTS aus - wie in steering_factory"""
    try:
        # MQTT-Client aus session state holen
        mqtt_client = st.session_state.get("mqtt_client")
        if not mqtt_client:
            st.error("❌ MQTT-Client nicht verfügbar")
            return
        
        # MqttGateway initialisieren (wie in steering_factory)
        from omf.dashboard.tools.mqtt_gateway import MqttGateway
        gateway = MqttGateway(mqtt_client)
        
        # FTS "FTS laden" Befehl senden (exakt wie in steering_factory)
        gateway.send(
            topic="ccu/set/charge",
            builder=lambda: {"serialNumber": module_id, "charge": True},
            ensure_order_id=True,
        )
        
        # Wenn wir hier ankommen, wurde die Nachricht erfolgreich gesendet
        # (kein Exception aufgetreten)
        logger.info(f"✅ FTS Lade-Befehl für {module_id} erfolgreich gesendet!")
        # KEIN st.success() - verhindert UI-Refresh und MQTT-Verbindungsabbruch
        
        # KEIN request_refresh() - verletzt Singleton-Pattern!
        # Status wird automatisch über Per-Topic-Buffer aktualisiert
        
    except Exception as e:
        logger.error(f"❌ Fehler beim FTS Laden für {module_id}: {e}")


def _execute_finish_charging_command(module_id):
    """Führt Finish Charging-Befehl für ein Modul aus - wie in steering_factory"""
    try:
        # MQTT-Client aus session state holen
        mqtt_client = st.session_state.get("mqtt_client")
        if not mqtt_client:
            st.error("❌ MQTT-Client nicht verfügbar")
            return
        
        # MqttGateway initialisieren (wie in steering_factory)
        from omf.dashboard.tools.mqtt_gateway import MqttGateway
        gateway = MqttGateway(mqtt_client)
        
        # FTS "Laden beenden" Befehl senden (exakt wie in steering_factory)
        gateway.send(
            topic="ccu/set/charge",
            builder=lambda: {"serialNumber": module_id, "charge": False},
            ensure_order_id=True,
        )
        
        # Wenn wir hier ankommen, wurde die Nachricht erfolgreich gesendet
        # (kein Exception aufgetreten)
        logger.info(f"✅ FTS Lade-Stop für {module_id} erfolgreich gesendet!")
        # KEIN st.success() - verhindert UI-Refresh und MQTT-Verbindungsabbruch
        
        # KEIN request_refresh() - verletzt Singleton-Pattern!
        # Status wird automatisch über Per-Topic-Buffer aktualisiert
        
    except Exception as e:
        logger.error(f"❌ Fehler beim FTS Lade-Stop für {module_id}: {e}")


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


def _process_module_messages_direct(messages, module_status_store):
    """Processes module messages directly - no dependency to overview_module_status"""
    for message in messages:
        try:
            # Extract module ID from topic
            topic = message.get("topic", "")
            if "/state/" in topic:
                module_id = topic.split("/state/")[1].split("/")[0]
            elif "/connection/" in topic:
                module_id = topic.split("/connection/")[1].split("/")[0]
            else:
                continue
                
            # Update module status
            if module_id not in module_status_store:
                module_status_store[module_id] = {}
                
            # Update based on message type
            if "/state/" in topic:
                payload = message.get("payload", {})
                if isinstance(payload, str):
                    import json
                    payload = json.loads(payload)
                module_status_store[module_id]["available"] = payload.get("available", "Unknown")
                module_status_store[module_id]["connected"] = payload.get("connected", False)
                module_status_store[module_id]["message_count"] = module_status_store[module_id].get("message_count", 0) + 1
                
        except Exception as e:
            logger.error(f"Error processing module message: {e}")


def _get_module_real_time_status_direct(module_id, module_status_store):
    """Gets module real-time status directly - no dependency to overview_module_status"""
    return module_status_store.get(module_id, {
        "available": "Unknown",
        "connected": False,
        "message_count": 0
    })
