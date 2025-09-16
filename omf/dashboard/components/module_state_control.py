"""
Module State Control Component für OMF Dashboard

UI-Komponente für Modul-Status-Management und automatische Sequenz-Ausführung.
Integriert den ModuleStateManager in das OMF Dashboard.
"""

import logging
from datetime import datetime, timezone
from typing import List

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh
from omf.tools.module_state_manager import CommandType, ModuleState, get_module_state_manager
from omf.tools.mqtt_gateway import MqttGateway

logger = logging.getLogger("omf.dashboard.module_state_control")


def show_module_state_control():
    """Hauptfunktion für Modul-Status-Kontrolle"""
    st.header("⚙️ Modul-Status-Kontrolle")
    st.markdown("**Automatisches Timing-Management für Modul-Sequenzen**")

    # MQTT-Client prüfen (Singleton-Pattern)
    mqtt_client = st.session_state.get("mqtt_client")
    if not mqtt_client:
        st.error("❌ MQTT-Client nicht verfügbar")
        return

    # Gateway initialisieren (Singleton-Pattern)
    if "mqtt_gateway" not in st.session_state:
        st.session_state.mqtt_gateway = MqttGateway(mqtt_client)

    gateway = st.session_state.mqtt_gateway

    # State Manager initialisieren (Singleton-Pattern)
    state_manager = get_module_state_manager()
    if not hasattr(state_manager, '_mqtt_client') or state_manager._mqtt_client is None:
        logger.info("Initialisiere ModuleStateManager mit MQTT-Client und Gateway")
        state_manager.initialize(mqtt_client, gateway)
        logger.info("ModuleStateManager erfolgreich initialisiert")

    # Untertabs für verschiedene Funktionen
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Modul-Status", "🔄 Sequenz-Steuerung", "⚡ Schnell-Commands", "📋 Laufende Sequenzen"]
    )

    with tab1:
        _show_module_status_overview(state_manager)

    with tab2:
        _show_sequence_control(state_manager)

    with tab3:
        _show_quick_commands(state_manager, gateway)

    with tab4:
        _show_running_sequences(state_manager)


def _show_module_status_overview(state_manager):
    """Zeigt Übersicht aller Modul-Status"""
    st.subheader("📊 Modul-Status-Übersicht")
    st.markdown("**Aktueller Status aller Module:**")

    # Refresh-Button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Aktualisieren", key="refresh_modules"):
            request_refresh()

    with col2:
        st.info("💡 Status wird automatisch über MQTT aktualisiert")

    # Modul-Status-Tabelle
    modules = state_manager.get_all_module_status()

    if not modules:
        st.warning("❌ Keine Modul-Informationen verfügbar")
        return

    # Status-Tabelle erstellen
    status_data = []
    for _module_id, module in modules.items():
        status_icon = _get_status_icon(module.current_state)
        availability_icon = "🟢" if module.is_available else "🔴"

        last_update = "Nie" if module.last_update is None else module.last_update.strftime("%H:%M:%S")

        status_data.append(
            {
                "Modul": f"{_get_module_icon(module.module_type)} {module.module_name}",
                "Status": f"{status_icon} {module.current_state.value}",
                "Verfügbar": f"{availability_icon} {'Ja' if module.is_available else 'Nein'}",
                "Letztes Update": last_update,
                "Typ": module.module_type,
            }
        )

    # Tabelle anzeigen
    import pandas as pd

    df = pd.DataFrame(status_data)
    st.dataframe(df, use_container_width=True)

    # Status-Legende
    with st.expander("📋 Status-Legende", expanded=False):
        st.markdown(
            """
            **Modul-Status:**
            - 🟢 **IDLE**: Modul bereit für Commands
            - 🟡 **PICKBUSY**: PICK-Operation läuft
            - 🟡 **MILLBUSY**: MILL-Operation läuft
            - 🟡 **DRILLBUSY**: DRILL-Operation läuft
            - 🟡 **CHECKBUSY**: CHECK_QUALITY-Operation läuft
            - 🟡 **WAITING_AFTER_***: Wartet auf nächsten Command
            - 🟡 **DROPBUSY**: DROP-Operation läuft
            - 🔴 **ERROR**: Fehler aufgetreten
            - ⚫ **OFFLINE**: Modul nicht erreichbar
            """
        )


def _show_sequence_control(state_manager):
    """Zeigt Sequenz-Steuerung für Module"""
    st.subheader("🔄 Sequenz-Steuerung")
    st.markdown("**Automatische Sequenz-Ausführung:**")

    # Modul-Auswahl
    modules = state_manager.get_all_module_status()
    module_options = {f"{module.module_name} ({module_id})": module_id for module_id, module in modules.items()}

    selected_module = st.selectbox(
        "Modul auswählen:", options=list(module_options.keys()), key="sequence_module_select"
    )

    if not selected_module:
        return

    module_id = module_options[selected_module]
    module = modules[module_id]

    # Verfügbare Commands für das Modul
    available_commands = _get_available_commands_for_module(module.module_type)

    st.markdown(f"**Verfügbare Commands für {module.module_name}:**")

    # Command-Sequenz erstellen
    selected_commands = []

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Sequenz erstellen:**")
        for i, command in enumerate(available_commands):
            if st.checkbox(f"{command.value}", key=f"cmd_{i}_{module_id}"):
                selected_commands.append(command)

    with col2:
        st.markdown("**Vorschau:**")
        if selected_commands:
            sequence_text = " → ".join([cmd.value for cmd in selected_commands])
            st.code(sequence_text)
        else:
            st.info("Keine Commands ausgewählt")

    # Sequenz starten
    if selected_commands and st.button("🚀 Sequenz starten", key=f"start_sequence_{module_id}"):
        try:
            sequence_name = f"manual_{int(datetime.now().timestamp())}"
            sequence_id = state_manager.start_sequence(
                module_id=module_id, sequence_name=sequence_name, commands=selected_commands
            )
            st.success(f"✅ Sequenz gestartet: {sequence_id}")
            request_refresh()
        except Exception as e:
            st.error(f"❌ Fehler beim Starten der Sequenz: {e}")


def _show_quick_commands(state_manager, gateway):
    """Zeigt Schnell-Commands für Module"""
    st.subheader("⚡ Schnell-Commands")
    st.markdown("**Schnell-Commands (Einzelne Befehle):**")

    modules = state_manager.get_all_module_status()

    # Für jedes Modul Schnell-Commands anzeigen
    for module_id, module in modules.items():
        with st.expander(
            f"{_get_module_icon(module.module_type)} {module.module_name} - Schnell-Commands", expanded=False
        ):
            available_commands = _get_available_commands_for_module(module.module_type)

            cols = st.columns(min(len(available_commands), 4))

            for i, command in enumerate(available_commands):
                with cols[i % 4]:
                    if st.button(
                        f"{command.value}",
                        key=f"quick_{module_id}_{command.value}",
                        disabled=not _is_module_ready_for_command(module, command),
                    ):
                        _send_quick_command(state_manager, gateway, module_id, command)


def _show_running_sequences(state_manager):
    """Zeigt laufende Sequenzen"""
    st.subheader("📋 Laufende Sequenzen")
    st.markdown("**Aktuell ausgeführte Sequenzen:**")

    running_sequences = state_manager.get_running_sequences()

    if not running_sequences:
        st.info("ℹ️ Keine laufenden Sequenzen")
        return

    for sequence_id, sequence in running_sequences.items():
        with st.expander(f"🔄 {sequence.sequence_name} ({sequence.module_id})", expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Aktueller Schritt", f"{sequence.current_step + 1}/{len(sequence.steps)}")

            with col2:
                st.metric("Status", sequence.status)

            with col3:
                if st.button("⏹️ Stoppen", key=f"stop_{sequence_id}"):
                    state_manager.stop_sequence(sequence_id)
                    request_refresh()

            # Fortschrittsbalken
            progress = (sequence.current_step / len(sequence.steps)) * 100
            st.progress(progress / 100)

            # Command-Liste
            st.markdown("**Sequenz-Schritte:**")
            for i, step in enumerate(sequence.steps):
                status_icon = "✅" if i < sequence.current_step else "🔄" if i == sequence.current_step else "⏳"
                st.write(f"{status_icon} {step.command.value}")


def _get_available_commands_for_module(module_type: str) -> List[CommandType]:
    """Gibt verfügbare Commands für einen Modul-Typ zurück"""
    if module_type == "Processing":
        return [CommandType.PICK, CommandType.MILL, CommandType.DRILL, CommandType.CHECK_QUALITY, CommandType.DROP]
    elif module_type == "Storage":
        return [CommandType.STORE, CommandType.PICK, CommandType.DROP]
    elif module_type == "Input/Output":
        return [CommandType.INPUT_RGB, CommandType.RGB_NFC, CommandType.PICK, CommandType.DROP]
    elif module_type == "Transport":
        return [CommandType.NAVIGATE, CommandType.PICK, CommandType.DROP]
    elif module_type == "Charging":
        return [CommandType.START_CHARGING, CommandType.STOP_CHARGING]
    else:
        return [CommandType.GET_STATUS]


def _is_module_ready_for_command(module, command: CommandType) -> bool:
    """Prüft ob ein Modul bereit für einen Command ist"""
    if not module.is_available:
        return False

    # Vereinfachte Bereitschaftsprüfung
    if module.current_state == ModuleState.IDLE:
        return command in [
            CommandType.PICK,
            CommandType.STORE,
            CommandType.INPUT_RGB,
            CommandType.NAVIGATE,
            CommandType.GET_STATUS,
        ]
    elif module.current_state in [
        ModuleState.WAITING_AFTER_PICK,
        ModuleState.WAITING_AFTER_MILL,
        ModuleState.WAITING_AFTER_DRILL,
        ModuleState.WAITING_AFTER_CHECK,
    ]:
        return command in [CommandType.MILL, CommandType.DRILL, CommandType.CHECK_QUALITY, CommandType.DROP]

    return False


def _send_quick_command(state_manager, gateway, module_id: str, command: CommandType):
    """Sendet einen einzelnen Command an ein Modul"""
    try:
        module = state_manager.get_module_status(module_id)
        if not module:
            st.error(f"Modul {module_id} nicht gefunden")
            return

        success = gateway.send(
            topic=f"module/v1/ff/{module.serial_number}/order",
            builder=lambda: {
                "serialNumber": module.serial_number,
                "orderId": f"quick_{int(datetime.now().timestamp())}",
                "orderUpdateId": 1,
                "action": {"command": command.value, "id": f"quick_{int(datetime.now().timestamp())}", "metadata": {}},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            ensure_order_id=False,
        )

        if success:
            st.success(f"✅ {command.value} an {module.module_name} gesendet")
        else:
            st.error(f"❌ Fehler beim Senden von {command.value}")

    except Exception as e:
        st.error(f"❌ Exception: {e}")


def _get_status_icon(state: ModuleState) -> str:
    """Gibt Icon für Modul-Status zurück"""
    icon_map = {
        ModuleState.IDLE: "🟢",
        ModuleState.PICKBUSY: "🟡",
        ModuleState.MILLBUSY: "🟡",
        ModuleState.DRILLBUSY: "🟡",
        ModuleState.CHECKBUSY: "🟡",
        ModuleState.WAITING_AFTER_PICK: "🟡",
        ModuleState.WAITING_AFTER_MILL: "🟡",
        ModuleState.WAITING_AFTER_DRILL: "🟡",
        ModuleState.WAITING_AFTER_CHECK: "🟡",
        ModuleState.DROPBUSY: "🟡",
        ModuleState.ERROR: "🔴",
        ModuleState.OFFLINE: "⚫",
    }
    return icon_map.get(state, "⚪")


def _get_module_icon(module_type: str) -> str:
    """Gibt Icon für Modul-Typ zurück"""
    icon_map = {
        "Processing": "⚙️",
        "Storage": "🏬",
        "Input/Output": "📦",
        "Transport": "🚗",
        "Charging": "🔋",
    }
    return icon_map.get(module_type, "❓")
