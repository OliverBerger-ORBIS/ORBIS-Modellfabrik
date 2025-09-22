"""
Kommando-Zentrale Component für OMF Dashboard
Traditionelle Steuerungsfunktionen für die Modellfabrik
"""

import uuid
from datetime import datetime, timezone

import streamlit as st

from omf.dashboard.tools.logging_config import get_logger

# MqttGateway für sauberes Publishing
from omf.dashboard.tools.mqtt_gateway import MqttGateway
from omf.dashboard.utils.ui_refresh import request_refresh

# WorkflowOrderManager für korrekte orderId/orderUpdateId Verwaltung

# Logger für Factory Steering
logger = get_logger("omf.dashboard.components.steering_factory")


def show_factory_steering():
    """Hauptfunktion für die Factory Steuerung"""
    logger.info("🏭 Factory Steering geladen")
    st.subheader("🏭 Factory Steuerung")
    st.markdown("**Traditionelle Steuerungsfunktionen für die Modellfabrik:**")

    # MessageGateway initialisieren
    mqtt_client = st.session_state.get("mqtt_client")
    if not mqtt_client:
        logger.warning("❌ MQTT-Client nicht verfügbar")
        st.error("❌ MQTT-Client nicht verfügbar")
        return

    logger.info("✅ MQTT-Client verfügbar, initialisiere Gateway")
    gateway = MqttGateway(mqtt_client)

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


def _show_factory_reset_section(gateway: MqttGateway):
    """Zeigt Factory Reset Funktionalität"""
    st.markdown("**Factory Reset der gesamten Modellfabrik:**")
    st.info("ℹ️ Setzt alle Module in den Ausgangszustand zurück")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🏭 Factory Reset", type="primary", key="factory_reset"):
            logger.info("🏭 Factory Reset angefordert")
            # Direkt über MqttGateway senden
            try:
                success = gateway.send(
                    topic="ccu/set/reset",
                    builder=lambda: {"timestamp": datetime.now(timezone.utc).isoformat(), "withStorage": False},
                    ensure_order_id=True,
                )
                if success:
                    logger.info("✅ Factory Reset erfolgreich gesendet")
                    st.success("✅ Factory Reset erfolgreich gesendet!")
                else:
                    logger.error("❌ Fehler beim Senden des Factory Reset")
                    st.error("❌ Fehler beim Senden des Factory Reset")
            except Exception as e:
                logger.error(f"❌ Fehler beim Factory Reset: {e}")
                st.error(f"❌ Fehler beim Factory Reset: {e}")

    with col2:
        st.info("💡 Factory Reset wird direkt gesendet (keine Vorschau)")


def _show_module_sequences_section(gateway: MqttGateway):
    """Zeigt Modul-Sequenzen für AIQS, MILL, DRILL"""
    st.markdown("**Einzelne Module steuern:**")

    # AIQS Box
    with st.expander("🔍 AIQS (Qualitätsprüfung)", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔄 Komplette Sequenz", key="aiqs_sequence", type="primary"):
                _prepare_module_sequence("AIQS", ["PICK", "CHECK_QUALITY", "DROP"])

        with col2:
            if st.button("📥 PICK", key="aiqs_pick"):
                _send_module_command(gateway, "AIQS", "PICK")

        with col3:
            if st.button("🔍 CHECK", key="aiqs_check"):
                _send_module_command(gateway, "AIQS", "CHECK_QUALITY")

        with col4:
            if st.button("📤 DROP", key="aiqs_drop"):
                _send_module_command(gateway, "AIQS", "DROP")

        # AIQS Sequenz-Anzeige
        _show_module_sequence_display_inline(gateway, "AIQS")

    # MILL Box
    with st.expander("⚙️ MILL (Fräsen)", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔄 Komplette Sequenz", key="mill_sequence", type="primary"):
                _prepare_module_sequence("MILL", ["PICK", "MILL", "DROP"])

        with col2:
            if st.button("📥 PICK", key="mill_pick"):
                _send_module_command(gateway, "MILL", "PICK")

        with col3:
            if st.button("⚙️ MILL", key="mill_mill"):
                _send_module_command(gateway, "MILL", "MILL")

        with col4:
            if st.button("📤 DROP", key="mill_drop"):
                _send_module_command(gateway, "MILL", "DROP")

        # MILL Sequenz-Anzeige
        _show_module_sequence_display_inline(gateway, "MILL")

    # DRILL Box
    with st.expander("🔩 DRILL (Bohren)", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔄 Komplette Sequenz", key="drill_sequence", type="primary"):
                _prepare_module_sequence("DRILL", ["PICK", "DRILL", "DROP"])

        with col2:
            if st.button("📥 PICK", key="drill_pick"):
                _send_module_command(gateway, "DRILL", "PICK")

        with col3:
            if st.button("🔩 DRILL", key="drill_drill"):
                _send_module_command(gateway, "DRILL", "DRILL")

        with col4:
            if st.button("📤 DROP", key="drill_drop"):
                _send_module_command(gateway, "DRILL", "DROP")

        # DRILL Sequenz-Anzeige
        _show_module_sequence_display_inline(gateway, "DRILL")


def _show_fts_commands_section(gateway: MqttGateway):
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


def _show_order_commands_section(gateway: MqttGateway):
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


def _send_module_command(gateway: MqttGateway, module_name: str, command: str):
    """Sendet einen einzelnen Modul-Befehl über MqttGateway"""
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


def _show_navigation_commands_section(gateway: MqttGateway):
    """Zeigt Navigations-Befehle"""
    st.markdown("**FTS-Navigation zu spezifischen Positionen:**")

    # Basis-Routen (DPS-HBW und HBW-DPS)
    st.markdown("#### 🚛 Basis-Routen")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚛 DPS-HBW", key="nav_dps_hbw", help="Von DPS zu HBW"):
            _prepare_navigation_message("DPS-HBW")
            request_refresh()

    with col2:
        if st.button("🏭 HBW-DPS", key="nav_hbw_dps", help="Von HBW zu DPS"):
            _prepare_navigation_message("HBW-DPS")
            request_refresh()

    # Produktions-Routen
    st.markdown("#### 🎨 Produktions-Routen")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔴 RED-Prod", key="nav_red_prod", help="Produktions-Route ROT"):
            _prepare_navigation_message("RED-Prod")
            request_refresh()

    with col2:
        if st.button("🔵 BLUE-Prod", key="nav_blue_prod", help="Produktions-Route BLAU"):
            _prepare_navigation_message("BLUE-Prod")
            request_refresh()

    with col3:
        if st.button("⚪ WHITE-Prod", key="nav_white_prod", help="Produktions-Route WEISS"):
            _prepare_navigation_message("WHITE-Prod")
            request_refresh()

    # Nachricht anzeigen und Send-Button für Navigation
    if "pending_message" in st.session_state and st.session_state["pending_message"]["type"] == "navigation":
        st.markdown("---")
        pending = st.session_state["pending_message"]

        st.markdown("**📤 Zu sendende Nachricht:**")
        st.markdown(f"**Topic:** `{pending['topic']}`")

        with st.expander("📋 Payload anzeigen", expanded=False):
            st.json(pending["payload"])

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📤 Senden", key="send_navigation", type="primary"):
                _send_pending_message()
        with col2:
            if st.button("❌ Abbrechen", key="cancel_navigation"):
                del st.session_state["pending_message"]
                request_refresh()


# Hilfsfunktionen für Tests und Legacy-Support
def _get_module_serial(module_name: str) -> str:
    """Gibt die Seriennummer für ein Modul zurück"""
    module_serials = {"AIQS": "SVR4H76530", "MILL": "SVR3QA2098", "DRILL": "SVR4H76449"}
    return module_serials.get(module_name, "UNKNOWN")


def _prepare_fts_message(action_type: str, metadata: dict = None) -> dict:
    """Erstellt eine FTS-Nachricht für Tests und setzt pending_message"""
    message = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "serialNumber": "5iO4",
        "actions": [{"actionType": action_type, "actionId": str(uuid.uuid4()), "metadata": metadata or {}}],
    }

    # Für Tests: pending_message setzen
    if "pending_message" not in st.session_state:
        st.session_state["pending_message"] = {
            "topic": "fts/v1/ff/5iO4/instantAction",
            "payload": message,
            "type": "fts",
        }

    return message


def _prepare_module_sequence_message(module_name: str, sequence: list) -> dict:
    """Erstellt eine Modul-Sequenz-Nachricht für Tests und setzt pending_message"""
    serial_number = _get_module_serial(module_name)
    message = {"serialNumber": serial_number, "orderId": str(uuid.uuid4()), "orderUpdateId": 1, "sequence": sequence}

    # Für Tests: pending_message setzen
    if "pending_message" not in st.session_state:
        st.session_state["pending_message"] = {
            "topic": f"module/v1/ff/{serial_number}/order",
            "payload": message,
            "type": "module",
        }

    return message


def _prepare_module_step_message(module_name: str, command: str) -> dict:
    """Erstellt eine einzelne Modul-Schritt-Nachricht für Tests und setzt pending_message"""
    serial_number = _get_module_serial(module_name)
    message = {
        "serialNumber": serial_number,
        "orderId": str(uuid.uuid4()),
        "orderUpdateId": 1,
        "action": {
            "id": str(uuid.uuid4()),
            "command": command,
            "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
        },
    }

    # Für Tests: pending_message setzen (immer überschreiben)
    st.session_state["pending_message"] = {
        "topic": f"module/v1/ff/{serial_number}/order",
        "payload": message,
        "type": "module",
    }

    return message


def _prepare_navigation_message(navigation_type: str):
    """Bereitet Navigations-Nachricht vor mit Message Generator"""
    # Prüfen ob MQTT-Client verfügbar ist
    mqtt_client = st.session_state.get("mqtt_client")
    if not mqtt_client:
        st.error("❌ MQTT-Client nicht verfügbar. Bitte wählen Sie zuerst eine Umgebung in der Sidebar.")
        return

    # MessageGenerator verwenden
    from omf.dashboard.tools.message_generator import get_omf_message_generator

    generator = get_omf_message_generator()

    # Route-Typ mapping für alle Navigation-Typen
    route_mapping = {
        "DPS-HBW": "DPS_HBW",
        "HBW-DPS": "HBW_DPS",
        "RED-Prod": "RED_Prod",
        "BLUE-Prod": "BLUE_Prod",
        "WHITE-Prod": "WHITE_Prod",
    }

    # Load-Type basierend auf Navigation-Typ
    load_type_mapping = {
        "DPS-HBW": "WHITE",
        "HBW-DPS": "WHITE",
        "RED-Prod": "RED",
        "BLUE-Prod": "BLUE",
        "WHITE-Prod": "WHITE",
    }

    route_type = route_mapping.get(navigation_type)
    load_type = load_type_mapping.get(navigation_type, "WHITE")

    if not route_type:
        st.error(f"❌ Unbekannter Navigation-Typ: {navigation_type}")
        return

    # Navigation Message generieren
    message = generator.generate_fts_navigation_message(route_type=route_type, load_type=load_type)

    if message:
        st.session_state["pending_message"] = {
            "topic": message["topic"],
            "payload": message["payload"],
            "type": "navigation",
        }
    else:
        st.error(f"❌ Fehler beim Generieren der Navigation-Nachricht für {navigation_type}")


def _send_pending_message():
    """Sendet die vorbereitete Nachricht"""
    if "pending_message" not in st.session_state:
        st.error("❌ Keine Nachricht zum Senden vorbereitet")
        return

    pending = st.session_state["pending_message"]

    try:
        mqtt_client = st.session_state.get("mqtt_client")
        if mqtt_client and mqtt_client.connected:
            result = mqtt_client.publish_json(pending["topic"], pending["payload"], qos=1, retain=False)

            if result:
                st.success(f"✅ Nachricht erfolgreich gesendet an {pending['topic']}!")
                del st.session_state["pending_message"]
                request_refresh()
            else:
                st.error("❌ Fehler beim Senden der Nachricht")
        else:
            st.error("❌ MQTT nicht verbunden")
    except Exception as e:
        st.error(f"❌ Fehler beim Senden: {e}")


def _prepare_module_sequence(module_name: str, commands: list):
    """Bereitet eine Modul-Sequenz vor und speichert sie im Session State"""
    # Modul-spezifische Serial Numbers
    module_serials = {"AIQS": "SVR4H76530", "MILL": "SVR3QA2098", "DRILL": "SVR4H76449"}
    serial_number = module_serials.get(module_name, "UNKNOWN")

    # Neue orderId für die Sequenz
    order_id = str(uuid.uuid4())

    # Sequenz-Messages erstellen
    sequence_messages = []
    for i, command in enumerate(commands, 1):
        message = {
            "topic": f"module/v1/ff/{serial_number}/order",
            "payload": {
                "serialNumber": serial_number,
                "orderId": order_id,
                "orderUpdateId": i,
                "action": {
                    "id": str(uuid.uuid4()),
                    "command": command,
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            },
            "step": i,
            "command": command,
            "module": module_name,
        }
        sequence_messages.append(message)

    # Im Session State speichern
    st.session_state["module_sequence"] = {
        "module": module_name,
        "order_id": order_id,
        "messages": sequence_messages,
        "total_steps": len(commands),
    }

    st.success(f"✅ {module_name} Sequenz vorbereitet ({len(commands)} Schritte)")
    request_refresh()


def _show_module_sequence_display_inline(gateway: MqttGateway, module_name: str):
    """Zeigt vorbereitete Modul-Sequenz inline in der jeweiligen Modul-Box"""
    if "module_sequence" not in st.session_state:
        return

    sequence = st.session_state["module_sequence"]
    if sequence["module"] != module_name:
        return

    module = sequence["module"]
    order_id = sequence["order_id"]
    messages = sequence["messages"]
    total_steps = sequence["total_steps"]

    st.markdown("---")
    st.markdown(f"**📋 {module} Sequenz ({total_steps} Schritte)**")
    st.info(f"**Order ID:** `{order_id}`")

    # Status-Anzeige
    sent_count = len(sequence.get("sent_messages", []))
    if sent_count == 0:
        st.info("⏳ Sequenz bereit - warten auf Send-Befehle")
    elif sent_count < total_steps:
        st.warning(f"🔄 Sequenz läuft - {sent_count}/{total_steps} Schritte gesendet")
    elif sent_count == total_steps:
        st.success("✅ Sequenz abgeschlossen - alle Schritte gesendet")

    for i, message in enumerate(messages, 1):
        # Status für diesen Schritt
        is_sent = i in sequence.get("sent_messages", [])
        status_icon = "✅" if is_sent else "⏳"

        with st.expander(f"**{i}️⃣ {message['command']}** {status_icon} - {message['topic']}", expanded=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.json(message["payload"])

            with col2:
                if is_sent:
                    st.success("✅ Gesendet")
                else:
                    if st.button("📤 Senden", key=f"send_sequence_{module}_{i}", type="primary"):
                        _send_sequence_message(gateway, message, i, total_steps)

    # Sequenz löschen Button
    if st.button("🗑️ Sequenz löschen", key=f"clear_sequence_{module}"):
        del st.session_state["module_sequence"]
        request_refresh()


def _send_sequence_message(gateway: MqttGateway, message: dict, step: int, total_steps: int):
    """Sendet eine einzelne Message aus der Sequenz"""
    try:
        success = gateway.send(topic=message["topic"], builder=lambda: message["payload"])

        if success:
            st.success(f"✅ Schritt {step}/{total_steps} ({message['command']}) erfolgreich gesendet!")

            # Optional: Nach erfolgreichem Senden aus Sequenz entfernen
            if "module_sequence" in st.session_state:
                sequence = st.session_state["module_sequence"]
                # Message als gesendet markieren
                if "sent_messages" not in sequence:
                    sequence["sent_messages"] = []
                sequence["sent_messages"].append(step)

                # Alle Messages gesendet?
                if len(sequence["sent_messages"]) == total_steps:
                    st.success("🎉 Komplette Sequenz erfolgreich gesendet!")
                    st.balloons()  # Feier-Animation

                    # Sequenz als abgeschlossen markieren
                    sequence["status"] = "completed"
                    sequence["completed_at"] = datetime.now(timezone.utc).isoformat()

                    # Nach 3 Sekunden automatisch schließen
                    import time

                    time.sleep(3)
                    del st.session_state["module_sequence"]
                    request_refresh()
        else:
            st.error(f"❌ Fehler beim Senden von Schritt {step} ({message['command']})")
    except Exception as e:
        st.error(f"❌ Fehler bei Schritt {step} ({message['command']}): {e}")
