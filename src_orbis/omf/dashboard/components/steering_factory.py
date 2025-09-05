"""
Kommando-Zentrale Component für OMF Dashboard
Traditionelle Steuerungsfunktionen für die Modellfabrik
"""

import uuid
from datetime import datetime, timezone

import streamlit as st

# WorkflowOrderManager für korrekte orderId/orderUpdateId Verwaltung
try:
    from omf.tools.workflow_order_manager import get_workflow_order_manager
except ImportError:
    # Fallback für direkte Imports
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from omf.tools.workflow_order_manager import get_workflow_order_manager


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
        if st.button("🔄 Komplette Sequenz", key="aiqs_sequence", type="primary"):
            _prepare_module_sequence_message("AIQS")

    with col2:
        if st.button("📥 PICK", key="aiqs_pick"):
            _prepare_module_step_message("AIQS", "PICK")

    with col3:
        if st.button("🔍 CHECK", key="aiqs_check"):
            _prepare_module_step_message("AIQS", "CHECK_QUALITY")

    with col4:
        if st.button("📤 DROP", key="aiqs_drop"):
            _prepare_module_step_message("AIQS", "DROP")

    # Nachricht anzeigen und Send-Button für AIQS
    _show_message_and_send_button("aiqs")

    # MILL
    st.markdown("#### ⚙️ MILL (Fräsen)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔄 Komplette Sequenz", key="mill_sequence", type="primary"):
            _prepare_module_sequence_message("MILL")

    with col2:
        if st.button("📥 PICK", key="mill_pick"):
            _prepare_module_step_message("MILL", "PICK")

    with col3:
        if st.button("⚙️ MILL", key="mill_mill"):
            _prepare_module_step_message("MILL", "MILL")

    with col4:
        if st.button("📤 DROP", key="mill_drop"):
            _prepare_module_step_message("MILL", "DROP")

    # Nachricht anzeigen und Send-Button für MILL
    _show_message_and_send_button("mill")

    # DRILL
    st.markdown("#### 🔩 DRILL (Bohren)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🔄 Komplette Sequenz", key="drill_sequence", type="primary"):
            _prepare_module_sequence_message("DRILL")

    with col2:
        if st.button("📥 PICK", key="drill_pick"):
            _prepare_module_step_message("DRILL", "PICK")

    with col3:
        if st.button("🔩 DRILL", key="drill_drill"):
            _prepare_module_step_message("DRILL", "DRILL")

    with col4:
        if st.button("📤 DROP", key="drill_drop"):
            _prepare_module_step_message("DRILL", "DROP")

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


def _get_module_serial(module_name: str) -> str:
    """Hilfsfunktion um Module-Serials zu bekommen"""
    module_serials = {"AIQS": "SVR3QA2098", "MILL": "SVR4H76449", "DRILL": "SVR4H76530"}
    return module_serials.get(module_name, "UNKNOWN")


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
    """Startet generische Sequenz mit flexiblen Message-Topic-Kombinationen"""
    # WorkflowOrderManager verwenden
    workflow_manager = get_workflow_order_manager()

    # Generische Sequenz-Definitionen (Topic + Message-Struktur)
    sequence_definitions = {
        "AIQS": [
            {
                "name": "PICK",
                "topic": f"module/v1/ff/{_get_module_serial('AIQS')}/order",
                "message_template": {
                    "serialNumber": _get_module_serial("AIQS"),
                    "action": {"command": "PICK", "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"}},
                },
                "icon": "📥",
            },
            {
                "name": "CHECK_QUALITY",
                "topic": f"module/v1/ff/{_get_module_serial('AIQS')}/order",
                "message_template": {
                    "serialNumber": _get_module_serial("AIQS"),
                    "action": {
                        "command": "CHECK_QUALITY",
                        "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                    },
                },
                "icon": "🔍",
            },
            {
                "name": "DROP",
                "topic": f"module/v1/ff/{_get_module_serial('AIQS')}/order",
                "message_template": {
                    "serialNumber": _get_module_serial("AIQS"),
                    "action": {"command": "DROP", "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"}},
                },
                "icon": "📤",
            },
        ],
        "MILL": [
            {
                "name": "PICK",
                "topic": f"module/v1/ff/{_get_module_serial('MILL')}/order",
                "message_template": {
                    "serialNumber": _get_module_serial("MILL"),
                    "action": {"command": "PICK", "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"}},
                },
                "icon": "📥",
            },
            {
                "name": "MILL",
                "topic": f"module/v1/ff/{_get_module_serial('MILL')}/order",
                "message_template": {
                    "serialNumber": _get_module_serial("MILL"),
                    "action": {"command": "MILL", "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"}},
                },
                "icon": "⚙️",
            },
            {
                "name": "DROP",
                "topic": f"module/v1/ff/{_get_module_serial('MILL')}/order",
                "message_template": {
                    "serialNumber": _get_module_serial("MILL"),
                    "action": {"command": "DROP", "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"}},
                },
                "icon": "📤",
            },
        ],
        "DRILL": [
            {
                "name": "PICK",
                "topic": f"module/v1/ff/{_get_module_serial('DRILL')}/order",
                "message_template": {
                    "serialNumber": _get_module_serial("DRILL"),
                    "action": {"command": "PICK", "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"}},
                },
                "icon": "📥",
            },
            {
                "name": "DRILL",
                "topic": f"module/v1/ff/{_get_module_serial('DRILL')}/order",
                "message_template": {
                    "serialNumber": _get_module_serial("DRILL"),
                    "action": {"command": "DRILL", "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"}},
                },
                "icon": "🔩",
            },
            {
                "name": "DROP",
                "topic": f"module/v1/ff/{_get_module_serial('DRILL')}/order",
                "message_template": {
                    "serialNumber": _get_module_serial("DRILL"),
                    "action": {"command": "DROP", "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"}},
                },
                "icon": "📤",
            },
        ],
    }

    sequence_steps = sequence_definitions.get(module_name, [])
    if not sequence_steps:
        st.error(f"Keine Sequenz-Definition für Modul {module_name} gefunden")
        return

    # ✅ Workflow starten - gibt orderId zurück
    order_id = workflow_manager.start_workflow(module_name, [step["name"] for step in sequence_steps])

    # Transaktions-Status initialisieren
    st.session_state["sequence_transaction"] = {
        "module": module_name,
        "sequence_definition": sequence_steps,  # Vollständige Sequenz-Definition
        "current_step": 0,
        "completed_steps": [],
        "active": True,
        "order_id": order_id,  # ✅ GLEICHE orderId für alle Schritte
        "workflow_manager": workflow_manager,
        "show_topic_and_message": True,  # Flag für Payload-Anzeige
    }

    # Ersten Schritt vorbereiten
    _prepare_next_sequence_step(module_name)


def _prepare_next_sequence_step(module_name: str):
    """Bereitet den nächsten Schritt in der Sequenz vor"""
    if "sequence_transaction" not in st.session_state:
        return

    transaction = st.session_state["sequence_transaction"]
    if not transaction["active"] or transaction["module"] != module_name:
        return

    current_step = transaction["current_step"]
    sequence_definition = transaction["sequence_definition"]

    if current_step >= len(sequence_definition):
        # Sequenz abgeschlossen
        transaction["active"] = False
        return

    # Aktuellen Schritt aus der Sequenz-Definition holen
    step_definition = sequence_definition[current_step]

    # ✅ WorkflowOrderManager verwenden
    workflow_manager = transaction["workflow_manager"]
    order_id = transaction["order_id"]

    # WorkflowOrderManager für korrekte orderId/orderUpdateId
    workflow_info = workflow_manager.execute_command(order_id, step_definition["name"])

    # Message-Template kopieren und IDs hinzufügen
    payload = step_definition["message_template"].copy()
    payload["orderId"] = workflow_info["orderId"]  # ✅ GLEICHE orderId
    payload["orderUpdateId"] = workflow_info["orderUpdateId"]  # ✅ Inkrementiert
    payload["action"]["id"] = str(uuid.uuid4())

    # Pending Message setzen
    st.session_state["pending_message"] = {
        "topic": step_definition["topic"],
        "payload": payload,
        "type": f"{module_name.lower()}_sequence_step_{current_step}",
        "note": (
            f"Sequenz-Schritt {current_step + 1}/{len(sequence_definition)}: "
            f"{step_definition['name']} für {module_name} "
            f"(orderId: {workflow_info['orderId'][:8]}..., orderUpdateId: {workflow_info['orderUpdateId']})"
        ),
    }


def _complete_sequence_step(module_name: str):
    """Markiert aktuellen Sequenz-Schritt als abgeschlossen und bereitet nächsten vor"""
    if "sequence_transaction" not in st.session_state:
        return

    transaction = st.session_state["sequence_transaction"]
    if not transaction["active"] or transaction["module"] != module_name:
        return

    # Aktuellen Schritt als abgeschlossen markieren
    current_step = transaction["current_step"]
    transaction["completed_steps"].append(current_step)
    transaction["current_step"] += 1

    # Nächsten Schritt vorbereiten
    _prepare_next_sequence_step(module_name)


def _cancel_sequence_transaction():
    """Bricht die aktuelle Sequenz-Transaktion ab"""
    if "sequence_transaction" in st.session_state:
        transaction = st.session_state["sequence_transaction"]
        transaction["active"] = False

        # Workflow im WorkflowOrderManager abschließen falls vorhanden
        if "workflow_manager" in transaction and "order_id" in transaction:
            try:
                transaction["workflow_manager"].complete_workflow(transaction["order_id"])
            except Exception as e:
                print(f"⚠️ Fehler beim Abschließen des Workflows: {e}")

    if "pending_message" in st.session_state:
        del st.session_state["pending_message"]


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

    # Transaktions-Header anzeigen falls aktive Sequenz
    if "sequence_transaction" in st.session_state and st.session_state["sequence_transaction"]["active"]:
        transaction = st.session_state["sequence_transaction"]
        module_name = transaction["module"]
        sequence_definition = transaction["sequence_definition"]
        total_steps = len(sequence_definition)
        current_step = transaction["current_step"]

        st.markdown(f"### 🔄 **Beginne Transaktion: Sequenz {module_name}**")
        st.markdown(f"**Fortschritt:** {current_step + 1}/{total_steps} Schritte")
        st.markdown("*(Sequenz Transaktion kann abgebrochen werden)*")

        # Visuelle Sequenz-Anzeige mit generischen Definitionen
        st.markdown("#### 📋 **Sequenz-Ablauf (Manuelle Steuerung):**")

        # Sequenz als Pfeile anzeigen mit generischen Definitionen
        sequence_display = []
        for i, step_def in enumerate(sequence_definition):
            icon = step_def["icon"]
            name = step_def["name"]
            if i == current_step:
                # Aktueller Schritt - hervorgehoben
                sequence_display.append(f"**{icon} {name}(SEND)**")
            elif i < current_step:
                # Abgeschlossener Schritt - grau
                sequence_display.append(f"~~{icon} {name}(✓)~~")
            else:
                # Zukünftiger Schritt - normal
                sequence_display.append(f"{icon} {name}(WARTEN)")

        # Sequenz mit Pfeilen verbinden
        sequence_text = " → ".join(sequence_display)
        st.markdown(f"**{sequence_text}**")

        # Anweisung für User
        current_step_def = sequence_definition[current_step]
        st.info(
            f"**Anweisung:** Klicken Sie auf 'Senden' für **{current_step_def['name']}** - "
            f"dann wird automatisch der nächste Schritt vorbereitet."
        )

        # Option: Payload-Anzeige ein/ausschalten
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Sequenz-Optionen:**")
        with col2:
            show_payload = st.checkbox(
                "Payload anzeigen",
                value=transaction.get("show_topic_and_message", True),
                key="sequence_show_payload",
                help="Zeigt die vollständige MQTT-Nachricht an",
            )
            # Flag in der Transaktion aktualisieren
            transaction["show_topic_and_message"] = show_payload

        # Fortschrittsbalken
        progress = (current_step + 1) / total_steps
        st.progress(progress)

        st.markdown("---")

    st.markdown("### 📤 Zu sendende Nachricht:")

    # Topic anzeigen
    st.markdown(f"**Topic:** `{pending['topic']}`")

    # Optional: Command hervorheben (falls vorhanden)
    if "action" in pending["payload"] and "command" in pending["payload"]["action"]:
        command = pending["payload"]["action"]["command"]
        st.markdown(f"**🎯 Command:** `{command}`")

    # Optional: Payload anzeigen (über Flag gesteuert)
    if "sequence_transaction" in st.session_state and st.session_state["sequence_transaction"]["active"]:
        show_details = st.session_state["sequence_transaction"].get("show_topic_and_message", True)
        if show_details:
            st.markdown("**Payload:**")
            st.json(pending["payload"])
    else:
        # Für einzelne Schritte immer anzeigen
        st.markdown("**Payload:**")
        st.json(pending["payload"])

    # Hinweis anzeigen falls vorhanden
    if "note" in pending:
        st.info(pending["note"])

    # Send-Button mit Transaktions-Logik
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("📤 Senden", type="primary", key=f"send_{pending['type']}"):
            _send_pending_message()

    with col2:
        if st.button("❌ Abbrechen", key=f"cancel_{pending['type']}"):
            if "sequence_transaction" in st.session_state and st.session_state["sequence_transaction"]["active"]:
                _cancel_sequence_transaction()
            else:
                if "pending_message" in st.session_state:
                    del st.session_state["pending_message"]
            st.rerun()

    # Transaktions-Ende anzeigen falls Sequenz abgeschlossen
    if "sequence_transaction" in st.session_state and not st.session_state["sequence_transaction"]["active"]:
        st.markdown("---")
        st.success("✅ **Ende Transaktion** - Sequenz erfolgreich abgeschlossen!")

        # Workflow im WorkflowOrderManager abschließen
        transaction = st.session_state["sequence_transaction"]
        if "workflow_manager" in transaction and "order_id" in transaction:
            try:
                transaction["workflow_manager"].complete_workflow(transaction["order_id"])
            except Exception as e:
                print(f"⚠️ Fehler beim Abschließen des Workflows: {e}")

        # Cleanup
        if "pending_message" in st.session_state:
            del st.session_state["pending_message"]
        if "sequence_transaction" in st.session_state:
            del st.session_state["sequence_transaction"]


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

                # Transaktions-Logik: Nächsten Schritt vorbereiten falls aktive Sequenz
                if "sequence_transaction" in st.session_state and st.session_state["sequence_transaction"]["active"]:
                    transaction = st.session_state["sequence_transaction"]
                    module_name = transaction["module"]
                    _complete_sequence_step(module_name)
                else:
                    # Normale Nachricht: Aus session_state entfernen
                    del st.session_state["pending_message"]

                st.rerun()
            else:
                st.error("❌ Fehler beim Senden der Nachricht")
        else:
            st.error("❌ MQTT nicht verbunden")
    except Exception as e:
        st.error(f"❌ Fehler beim Senden: {e}")
