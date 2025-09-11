"""
Kommando-Zentrale Component für OMF Dashboard
Traditionelle Steuerungsfunktionen für die Modellfabrik
"""

import uuid
from datetime import datetime, timezone

import streamlit as st

# MessageGateway für sauberes Publishing
from src_orbis.omf.tools.mqtt_gateway import MessageGateway

# WorkflowOrderManager für korrekte orderId/orderUpdateId Verwaltung


def show_factory_steering():
    """Hauptfunktion für die Factory Steuerung"""
    st.subheader("🏭 Factory Steuerung")
    st.markdown("**Traditionelle Steuerungsfunktionen für die Modellfabrik:**")

    # MessageGateway initialisieren
    mqtt_client = st.session_state.get("mqtt_client")
    if not mqtt_client:
        st.error("❌ MQTT-Client nicht verfügbar")
        return

    gateway = MessageGateway(mqtt_client)

    # Factory Reset Section - Aufklappbare Box
    with st.expander("🏭 Factory Reset", expanded=False):
        _show_factory_reset_section(gateway)

    # Module Sequences Section - Aufklappbare Box
    with st.expander("🔧 Modul-Sequenzen", expanded=False):
        _show_module_sequences_section(gateway)

    # FTS Commands Section - Aufklappbare Box
    with st.expander("🚗 FTS (Fahrerloses Transportsystem) Steuerung", expanded=False):
        _show_fts_commands_section(gateway)

    # Order Commands Section - Aufklappbare Box
    with st.expander("📋 Auftrags-Befehle", expanded=False):
        _show_order_commands_section(gateway)

    # Navigation Commands Section - Aufklappbare Box
    with st.expander("🗺️ Navigation", expanded=False):
        _show_navigation_commands_section(gateway)


def _show_factory_reset_section(gateway: MessageGateway):
    """Zeigt Factory Reset Funktionalität"""
    st.markdown("**Factory Reset der gesamten Modellfabrik:**")
    st.info("ℹ️ Setzt alle Module in den Ausgangszustand zurück")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🏭 Factory Reset", type="primary", key="factory_reset"):
            # Direkt über MessageGateway senden
            try:
                success = gateway.send(
                    topic="ccu/set/reset",
                    builder=lambda: {"timestamp": datetime.now(timezone.utc).isoformat(), "withStorage": False},
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ Factory Reset erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden des Factory Reset")
            except Exception as e:
                st.error(f"❌ Fehler beim Factory Reset: {e}")

    with col2:
        st.info("💡 Factory Reset wird direkt gesendet (keine Vorschau)")


def _show_module_sequences_section(gateway: MessageGateway):
    """Zeigt Modul-Sequenzen für AIQS, MILL, DRILL"""
    st.markdown("**Einzelne Module steuern:**")

    # AIQS Box
    with st.expander("🔍 AIQS (Qualitätsprüfung)", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔄 Komplette Sequenz", key="aiqs_sequence", type="primary"):
                st.info("💡 Sequenzen werden in zukünftiger Version über MessageGateway implementiert")

        with col2:
            if st.button("📥 PICK", key="aiqs_pick"):
                _send_module_command(gateway, "AIQS", "PICK")

        with col3:
            if st.button("🔍 CHECK", key="aiqs_check"):
                _send_module_command(gateway, "AIQS", "CHECK_QUALITY")

        with col4:
            if st.button("📤 DROP", key="aiqs_drop"):
                _send_module_command(gateway, "AIQS", "DROP")

    # MILL Box
    with st.expander("⚙️ MILL (Fräsen)", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔄 Komplette Sequenz", key="mill_sequence", type="primary"):
                st.info("💡 Sequenzen werden in zukünftiger Version über MessageGateway implementiert")

        with col2:
            if st.button("📥 PICK", key="mill_pick"):
                _send_module_command(gateway, "MILL", "PICK")

        with col3:
            if st.button("⚙️ MILL", key="mill_mill"):
                _send_module_command(gateway, "MILL", "MILL")

        with col4:
            if st.button("📤 DROP", key="mill_drop"):
                _send_module_command(gateway, "MILL", "DROP")

    # DRILL Box
    with st.expander("🔩 DRILL (Bohren)", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔄 Komplette Sequenz", key="drill_sequence", type="primary"):
                st.info("💡 Sequenzen werden in zukünftiger Version über MessageGateway implementiert")

        with col2:
            if st.button("📥 PICK", key="drill_pick"):
                _send_module_command(gateway, "DRILL", "PICK")

        with col3:
            if st.button("🔩 DRILL", key="drill_drill"):
                _send_module_command(gateway, "DRILL", "DRILL")

        with col4:
            if st.button("📤 DROP", key="drill_drop"):
                _send_module_command(gateway, "DRILL", "DROP")


def _show_fts_commands_section(gateway: MessageGateway):
    """Zeigt FTS-Steuerung"""
    st.markdown("**Fahrerloses Transportsystem (FTS) steuern:**")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("🚗 Docke an", key="fts_dock"):
            try:
                success = gateway.send(
                    topic="fts/v1/ff/5iO4/instantAction",
                    builder=lambda: {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "serialNumber": "5iO4",
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
                if success:
                    st.success("✅ FTS Dock-Befehl erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden des FTS Dock-Befehls")
            except Exception as e:
                st.error(f"❌ Fehler beim FTS Dock: {e}")

    with col2:
        if st.button("🔋 FTS laden", key="fts_charge"):
            try:
                success = gateway.send(
                    topic="ccu/set/charge",
                    builder=lambda: {"serialNumber": "5iO4", "charge": True},
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ FTS Lade-Befehl erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden des FTS Lade-Befehls")
            except Exception as e:
                st.error(f"❌ Fehler beim FTS Laden: {e}")

    with col3:
        if st.button("⏹️ Laden beenden", key="fts_stop_charging"):
            try:
                success = gateway.send(
                    topic="ccu/set/charge",
                    builder=lambda: {"serialNumber": "5iO4", "charge": False},
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ FTS Lade-Stop erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden des FTS Lade-Stops")
            except Exception as e:
                st.error(f"❌ Fehler beim FTS Lade-Stop: {e}")

    with col4:
        if st.button("🔄 Status abfragen", key="fts_status"):
            try:
                success = gateway.send(
                    topic="fts/v1/ff/5iO4/instantAction",
                    builder=lambda: {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "serialNumber": "5iO4",
                        "actions": [{"actionType": "status", "actionId": str(uuid.uuid4())}],
                    },
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ FTS Status-Abfrage erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden der FTS Status-Abfrage")
            except Exception as e:
                st.error(f"❌ Fehler bei FTS Status: {e}")

    with col5:
        if st.button("⏸️ Stop", key="fts_stop"):
            try:
                success = gateway.send(
                    topic="fts/v1/ff/5iO4/instantAction",
                    builder=lambda: {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "serialNumber": "5iO4",
                        "actions": [{"actionType": "stop", "actionId": str(uuid.uuid4())}],
                    },
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ FTS Stop-Befehl erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden des FTS Stop-Befehls")
            except Exception as e:
                st.error(f"❌ Fehler bei FTS Stop: {e}")

    st.info("💡 FTS-Befehle werden direkt gesendet (keine Vorschau)")


def _show_order_commands_section(gateway: MessageGateway):
    """Zeigt Auftrags-Befehle"""
    st.markdown("**Aufträge für spezifische Farben senden:**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔴 ROT", key="order_red"):
            try:
                success = gateway.send(
                    topic="ccu/order/request",
                    builder=lambda: {
                        "type": "RED",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "orderType": "PRODUCTION",
                    },
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ ROT Auftrag erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden des ROT Auftrags")
            except Exception as e:
                st.error(f"❌ Fehler beim ROT Auftrag: {e}")

    with col2:
        if st.button("⚪ WEISS", key="order_white"):
            try:
                success = gateway.send(
                    topic="ccu/order/request",
                    builder=lambda: {
                        "type": "WHITE",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "orderType": "PRODUCTION",
                    },
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ WEISS Auftrag erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden des WEISS Auftrags")
            except Exception as e:
                st.error(f"❌ Fehler beim WEISS Auftrag: {e}")

    with col3:
        if st.button("🔵 BLAU", key="order_blue"):
            try:
                success = gateway.send(
                    topic="ccu/order/request",
                    builder=lambda: {
                        "type": "BLUE",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "orderType": "PRODUCTION",
                    },
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ BLAU Auftrag erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden des BLAU Auftrags")
            except Exception as e:
                st.error(f"❌ Fehler beim BLAU Auftrag: {e}")

    st.info("💡 Aufträge werden direkt gesendet (keine Vorschau)")


def _send_module_command(gateway: MessageGateway, module_name: str, command: str):
    """Sendet einen einzelnen Modul-Befehl über MessageGateway"""
    # Modul-spezifische Serial Numbers
    module_serials = {"AIQS": "SVR4H76530", "MILL": "SVR3QA2098", "DRILL": "SVR4H76449"}
    serial_number = module_serials.get(module_name, "UNKNOWN")

    try:
        success = gateway.send(
            topic=f"module/v1/ff/{serial_number}/order",
            builder=lambda: {
                "serialNumber": serial_number,
                "orderId": str(uuid.uuid4()),
                "orderUpdateId": 1,  # Vereinfacht für einzelne Befehle
                "action": {
                    "id": str(uuid.uuid4()),
                    "command": command,
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            },
            ensure_order_id=True,
        )
        if success:
            st.success(f"✅ {module_name} {command} erfolgreich gesendet!")
        else:
            st.error(f"❌ Fehler beim Senden von {module_name} {command}")
    except Exception as e:
        st.error(f"❌ Fehler bei {module_name} {command}: {e}")


def _show_navigation_commands_section(gateway: MessageGateway):
    """Zeigt Navigations-Befehle"""
    st.markdown("**FTS-Navigation zu spezifischen Positionen:**")

    # Basis-Routen (DPS-HBW und HBW-DPS)
    st.markdown("#### 🚛 Basis-Routen")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚛 DPS-HBW", key="nav_dps_hbw", help="Von DPS zu HBW"):
            try:
                success = gateway.send(
                    topic="fts/v1/ff/5iO4/instantAction",
                    builder=lambda: {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "serialNumber": "5iO4",
                        "actions": [
                            {
                                "actionType": "navigateToPosition",
                                "actionId": str(uuid.uuid4()),
                                "metadata": {"route": "DPS_HBW", "loadType": "WHITE"},
                            }
                        ],
                    },
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ DPS-HBW Navigation erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden der DPS-HBW Navigation")
            except Exception as e:
                st.error(f"❌ Fehler bei DPS-HBW Navigation: {e}")

    with col2:
        if st.button("🏭 HBW-DPS", key="nav_hbw_dps", help="Von HBW zu DPS"):
            try:
                success = gateway.send(
                    topic="fts/v1/ff/5iO4/instantAction",
                    builder=lambda: {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "serialNumber": "5iO4",
                        "actions": [
                            {
                                "actionType": "navigateToPosition",
                                "actionId": str(uuid.uuid4()),
                                "metadata": {"route": "HBW_DPS", "loadType": "WHITE"},
                            }
                        ],
                    },
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ HBW-DPS Navigation erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden der HBW-DPS Navigation")
            except Exception as e:
                st.error(f"❌ Fehler bei HBW-DPS Navigation: {e}")

    # Produktions-Routen
    st.markdown("#### 🎨 Produktions-Routen")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔴 RED-Prod", key="nav_red_prod", help="Produktions-Route ROT"):
            try:
                success = gateway.send(
                    topic="fts/v1/ff/5iO4/instantAction",
                    builder=lambda: {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "serialNumber": "5iO4",
                        "actions": [
                            {
                                "actionType": "navigateToPosition",
                                "actionId": str(uuid.uuid4()),
                                "metadata": {"route": "RED_Prod", "loadType": "RED"},
                            }
                        ],
                    },
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ RED-Prod Navigation erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden der RED-Prod Navigation")
            except Exception as e:
                st.error(f"❌ Fehler bei RED-Prod Navigation: {e}")

    with col2:
        if st.button("🔵 BLUE-Prod", key="nav_blue_prod", help="Produktions-Route BLAU"):
            try:
                success = gateway.send(
                    topic="fts/v1/ff/5iO4/instantAction",
                    builder=lambda: {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "serialNumber": "5iO4",
                        "actions": [
                            {
                                "actionType": "navigateToPosition",
                                "actionId": str(uuid.uuid4()),
                                "metadata": {"route": "BLUE_Prod", "loadType": "BLUE"},
                            }
                        ],
                    },
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ BLUE-Prod Navigation erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden der BLUE-Prod Navigation")
            except Exception as e:
                st.error(f"❌ Fehler bei BLUE-Prod Navigation: {e}")

    with col3:
        if st.button("⚪ WHITE-Prod", key="nav_white_prod", help="Produktions-Route WEISS"):
            try:
                success = gateway.send(
                    topic="fts/v1/ff/5iO4/instantAction",
                    builder=lambda: {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "serialNumber": "5iO4",
                        "actions": [
                            {
                                "actionType": "navigateToPosition",
                                "actionId": str(uuid.uuid4()),
                                "metadata": {"route": "WHITE_Prod", "loadType": "WHITE"},
                            }
                        ],
                    },
                    ensure_order_id=True,
                )
                if success:
                    st.success("✅ WHITE-Prod Navigation erfolgreich gesendet!")
                else:
                    st.error("❌ Fehler beim Senden der WHITE-Prod Navigation")
            except Exception as e:
                st.error(f"❌ Fehler bei WHITE-Prod Navigation: {e}")

    st.info("💡 Navigation-Befehle werden direkt gesendet (keine Vorschau)")


# Hilfsfunktionen für Tests und Legacy-Support
def _get_module_serial(module_name: str) -> str:
    """Gibt die Seriennummer für ein Modul zurück"""
    module_serials = {"AIQS": "SVR4H76530", "MILL": "SVR3QA2098", "DRILL": "SVR4H76449"}
    return module_serials.get(module_name, "UNKNOWN")


def _prepare_fts_message(action_type: str, metadata: dict = None) -> dict:
    """Erstellt eine FTS-Nachricht für Tests"""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "serialNumber": "5iO4",
        "actions": [{"actionType": action_type, "actionId": str(uuid.uuid4()), "metadata": metadata or {}}],
    }


def _prepare_module_sequence_message(module_name: str, sequence: list) -> dict:
    """Erstellt eine Modul-Sequenz-Nachricht für Tests"""
    serial_number = _get_module_serial(module_name)
    return {"serialNumber": serial_number, "orderId": str(uuid.uuid4()), "orderUpdateId": 1, "sequence": sequence}


def _prepare_module_step_message(module_name: str, command: str) -> dict:
    """Erstellt eine einzelne Modul-Schritt-Nachricht für Tests"""
    serial_number = _get_module_serial(module_name)
    return {
        "serialNumber": serial_number,
        "orderId": str(uuid.uuid4()),
        "orderUpdateId": 1,
        "action": {
            "id": str(uuid.uuid4()),
            "command": command,
            "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
        },
    }


def _prepare_navigation_message(route: str, load_type: str = "WHITE") -> dict:
    """Erstellt eine Navigation-Nachricht für Tests"""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "serialNumber": "5iO4",
        "actions": [
            {
                "actionType": "navigateToPosition",
                "actionId": str(uuid.uuid4()),
                "metadata": {"route": route, "loadType": load_type}
            }
        ]
    }
