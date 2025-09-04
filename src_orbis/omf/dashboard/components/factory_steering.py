"""
Kommando-Zentrale Component für OMF Dashboard
Traditionelle Steuerungsfunktionen für die Modellfabrik
"""

import uuid
from datetime import datetime, timezone

import streamlit as st


def show_factory_steering():
    """Hauptfunktion für die Factory Steuerung"""
    st.subheader("🏭 Factory Steuerung")
    st.markdown("**Traditionelle Steuerungsfunktionen für die Modellfabrik:**")

    # Factory Reset Section
    st.markdown("### 🏭 Factory Steuerung")
    _show_factory_reset_section()

    # Module Sequences Section
    st.markdown("### 🔧 Modul-Sequenzen")
    _show_module_sequences_section()

    # FTS Commands Section
    st.markdown("### 🚗 FTS (Fahrerloses Transportsystem) Steuerung")
    _show_fts_commands_section()

    # Order Commands Section
    st.markdown("### 📋 Auftrags-Befehle")
    _show_order_commands_section()


def _show_factory_reset_section():
    """Zeigt Factory Reset Funktionalität"""
    st.markdown("**Factory Reset der gesamten Modellfabrik:**")

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("🏭 Factory Reset", type="primary", key="factory_reset"):
            # Nachricht vorbereiten und anzeigen
            _prepare_factory_reset_message()

    with col2:
        st.info("ℹ️ Setzt alle Module in den Ausgangszustand zurück")

    # Nachricht anzeigen und Send-Button
    _show_message_and_send_button("factory_reset")


def _show_module_sequences_section():
    """Zeigt Modul-Sequenzen für AIQS, MILL, DRILL"""
    st.markdown("**Einzelne Module steuern:**")

    # AIQS
    st.markdown("#### 🔍 AIQS (Qualitätsprüfung)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📥 PICK", key="aiqs_pick"):
            _prepare_module_step_message("AIQS", "PICK")

    with col2:
        if st.button("🔍 CHECK", key="aiqs_check"):
            _prepare_module_step_message("AIQS", "CHECK_QUALITY")

    with col3:
        if st.button("📤 DROP", key="aiqs_drop"):
            _prepare_module_step_message("AIQS", "DROP")

    with col4:
        if st.button("🔄 Komplette Sequenz", key="aiqs_sequence"):
            _prepare_module_sequence_message("AIQS")

    # Nachricht anzeigen und Send-Button für AIQS
    _show_message_and_send_button("aiqs")

    # MILL
    st.markdown("#### ⚙️ MILL (Fräsen)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📥 PICK", key="mill_pick"):
            _prepare_module_step_message("MILL", "PICK")

    with col2:
        if st.button("⚙️ MILL", key="mill_mill"):
            _prepare_module_step_message("MILL", "MILL")

    with col3:
        if st.button("📤 DROP", key="mill_drop"):
            _prepare_module_step_message("MILL", "DROP")

    with col4:
        if st.button("🔄 Komplette Sequenz", key="mill_sequence"):
            _prepare_module_sequence_message("MILL")

    # Nachricht anzeigen und Send-Button für MILL
    _show_message_and_send_button("mill")

    # DRILL
    st.markdown("#### 🔩 DRILL (Bohren)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📥 PICK", key="drill_pick"):
            _prepare_module_step_message("DRILL", "PICK")

    with col2:
        if st.button("🔩 DRILL", key="drill_drill"):
            _prepare_module_step_message("DRILL", "DRILL")

    with col3:
        if st.button("📤 DROP", key="drill_drop"):
            _prepare_module_step_message("DRILL", "DROP")

    with col4:
        if st.button("🔄 Komplette Sequenz", key="drill_sequence"):
            _prepare_module_sequence_message("DRILL")

    # Nachricht anzeigen und Send-Button für DRILL
    _show_message_and_send_button("drill")


def _show_fts_commands_section():
    """Zeigt FTS-Steuerung"""
    st.markdown("**Fahrerloses Transportsystem (FTS) steuern:**")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("🚗 Docke an", key="fts_dock"):
            _prepare_fts_message("DOCK")

    with col2:
        if st.button("🔋 FTS laden", key="fts_charge"):
            _prepare_fts_message("CHARGE")

    with col3:
        if st.button("⏹️ Laden beenden", key="fts_stop_charging"):
            _prepare_fts_message("STOP")

    with col4:
        if st.button("🔄 Status abfragen", key="fts_status"):
            _prepare_fts_message("STATUS")

    with col5:
        if st.button("⏸️ Stop", key="fts_stop"):
            _prepare_fts_message("STOP")

    # Nachricht anzeigen und Send-Button für FTS
    _show_message_and_send_button("fts")


def _show_order_commands_section():
    """Zeigt Auftrags-Befehle"""
    st.markdown("**Aufträge für spezifische Farben senden:**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔴 ROT", key="order_red"):
            _prepare_order_message("RED")

    with col2:
        if st.button("⚪ WEISS", key="order_white"):
            _prepare_order_message("WHITE")

    with col3:
        if st.button("🔵 BLAU", key="order_blue"):
            _prepare_order_message("BLUE")

    # Nachricht anzeigen und Send-Button für Orders
    _show_message_and_send_button("order")


def _prepare_factory_reset_message():
    """Bereitet Factory Reset Nachricht vor"""
    payload = {"timestamp": datetime.now().isoformat(), "withStorage": False}

    st.session_state["pending_message"] = {"topic": "ccu/set/reset", "payload": payload, "type": "factory_reset"}


def _prepare_module_step_message(module_name: str, step: str):
    """Bereitet Modul-Schritt Nachricht vor"""
    # Modul-spezifische Serial Numbers
    module_serials = {"AIQS": "SVR4H76530", "MILL": "SVR3QA2098", "DRILL": "SVR4H76449"}

    serial_number = module_serials.get(module_name, "UNKNOWN")

    # Topic generieren - KORRIGIERT: Verwende korrekten Modul-Topic aus YAMLs
    topic = f"module/v1/ff/{serial_number}/order"

    # OrderUpdateId-Logik: Für Sequenzen hochzählen
    if "order_update_counter" not in st.session_state:
        st.session_state["order_update_counter"] = 1
    else:
        st.session_state["order_update_counter"] += 1

    # Payload generieren
    payload = {
        "serialNumber": serial_number,
        "orderId": str(uuid.uuid4()),
        "orderUpdateId": st.session_state["order_update_counter"],
        "action": {
            "id": str(uuid.uuid4()),
            "command": step,
            "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
        },
    }

    st.session_state["pending_message"] = {
        "topic": topic,
        "payload": payload,
        "type": f"{module_name.lower()}_{step.lower()}",
    }


def _prepare_module_sequence_message(module_name: str):
    """Bereitet komplette Modul-Sequenz Nachricht vor"""
    # Für Sequenzen zeigen wir nur den ersten Schritt an
    _prepare_module_step_message(module_name, "PICK")
    # Hinweis hinzufügen
    st.session_state["pending_message"]["note"] = f"Komplette Sequenz: PICK → PROCESS → DROP für {module_name}"


def _prepare_fts_message(command: str):
    """Bereitet FTS-Nachricht vor"""
    # FUNKTIONIERENDE TOPICS UND PAYLOADS AUS DEN SESSIONS

    if command == "DOCK":
        # Docke an - funktioniert!
        topic = "fts/v1/ff/5iO4/instantAction"
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "serialNumber": "5iO4",
            "actions": [
                {
                    "actionType": "findInitialDockPosition",
                    "actionId": str(uuid.uuid4()),
                    "metadata": {"nodeId": "SVR4H73275"},  # DPS-Modul
                }
            ],
        }
    elif command == "CHARGE":
        # Charge Start - funktioniert!
        topic = "ccu/set/charge"
        payload = {"serialNumber": "5iO4", "charge": True}
    elif command == "STOP":
        # Charge Stop - funktioniert!
        topic = "ccu/set/charge"
        payload = {"serialNumber": "5iO4", "charge": False}
    else:
        # Fallback für unbekannte Commands
        topic = "fts/v1/ff/5iO4/instantAction"
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "serialNumber": "5iO4",
            "actions": [{"actionType": command.lower(), "actionId": str(uuid.uuid4())}],
        }

    st.session_state["pending_message"] = {"topic": topic, "payload": payload, "type": f"fts_{command.lower()}"}


def _prepare_order_message(color: str):
    """Bereitet Auftrags-Nachricht vor"""
    # FUNKTIONIERENDE TOPICS UND PAYLOADS AUS DEN SESSIONS

    # Korrekter Topic aus den Sessions
    topic = "ccu/order/request"

    # Payload-Struktur aus den funktionierenden Sessions
    payload = {
        "type": color,  # RED, WHITE, BLUE
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "orderType": "PRODUCTION",
    }

    st.session_state["pending_message"] = {"topic": topic, "payload": payload, "type": f"order_{color.lower()}"}


def _show_message_and_send_button(message_type: str):
    """Zeigt vorbereitete Nachricht und Send-Button an"""
    if "pending_message" not in st.session_state:
        return

    pending = st.session_state["pending_message"]

    # Nur anzeigen wenn es der richtige Typ ist
    if not pending["type"].startswith(message_type):
        return

    st.markdown("---")
    st.markdown("### 📤 Zu sendende Nachricht:")

    # Topic anzeigen
    st.markdown(f"**Topic:** `{pending['topic']}`")

    # Payload anzeigen
    st.markdown("**Payload:**")
    st.json(pending["payload"])

    # Hinweis anzeigen falls vorhanden
    if "note" in pending:
        st.info(pending["note"])

    # Send-Button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("📤 Senden", type="primary", key=f"send_{pending['type']}"):
            _send_pending_message()

    with col2:
        if st.button("❌ Abbrechen", key=f"cancel_{pending['type']}"):
            if "pending_message" in st.session_state:
                del st.session_state["pending_message"]
            st.rerun()


def _send_pending_message():
    """Sendet die vorbereitete Nachricht"""
    if "pending_message" not in st.session_state:
        st.error("❌ Keine Nachricht zum Senden vorbereitet")
        return

    pending = st.session_state["pending_message"]

    try:
        mqtt_client = st.session_state.get("mqtt_client")
        if mqtt_client and mqtt_client.connected:
            result = mqtt_client.publish(pending["topic"], pending["payload"], qos=1, retain=False)

            if result:
                st.success(f"✅ Nachricht erfolgreich gesendet an {pending['topic']}!")
                # Nachricht aus session_state entfernen
                del st.session_state["pending_message"]
                st.rerun()
            else:
                st.error("❌ Fehler beim Senden der Nachricht")
        else:
            st.error("❌ MQTT nicht verbunden")
    except Exception as e:
        st.error(f"❌ Fehler beim Senden: {e}")
