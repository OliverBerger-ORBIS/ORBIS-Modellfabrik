"""
Steering Component für OMF Dashboard
Kommando-Zentrale: Übernahme der Steuerung der Modellfabrik
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# Add tools path for imports
tools_path = Path(__file__).parent.parent.parent / "tools"
if str(tools_path) not in sys.path:
    sys.path.append(str(tools_path))

try:
    from message_generator import MessageGenerator, get_omf_message_generator
    from message_template_manager import get_omf_message_template_manager
    from mqtt_client import get_omf_mqtt_client
    from topic_mapping_manager import get_omf_topic_mapping_manager
    from workflow_order_manager import get_workflow_order_manager
except ImportError as e:
    st.error(f"❌ Import-Fehler: {e}")
    st.info("Steering-Komponente kann nicht geladen werden")


def show_steering_dashboard():
    """Hauptfunktion für die Steuerung (Kommando-Zentrale)"""

    st.subheader("🎮 Kommando-Zentrale")
    st.markdown("**Übernahme der Steuerung der Modellfabrik über MQTT-Messages**")

    # Status-Übersicht
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("MQTT Status", "Connected" if _check_mqtt_connection() else "Disconnected")

    with col2:
        st.metric("Verfügbare Templates", _count_available_templates())

    with col3:
        st.metric("Aktive Module", _count_active_modules())

    # Hauptfunktionen
    st.markdown("---")

    # Factory Steuerung (Factory Reset + Bestellung)
    show_factory_control()

    # Separate Modul-Boxen
    st.markdown("### 🏭 Modul-Steuerung")

    # MILL Modul
    with st.expander("⚙️ MILL (Fräse)", expanded=True):
        _show_module_control_box("MILL", "⚙️", "Fräse")

    # DRILL Modul
    with st.expander("🔧 DRILL (Bohrer)", expanded=True):
        _show_module_control_box("DRILL", "🔧", "Bohrer")

    # AIQS Modul
    with st.expander("🔍 AIQS (Qualitätssicherung)", expanded=True):
        _show_module_control_box("AIQS", "🔍", "Qualitätssicherung")

    # FTS-Steuerung
    with st.expander("🚗 FTS-Steuerung", expanded=True):
        show_fts_control()

    # Message-Generator
    st.markdown("---")
    st.markdown("### 🔧 Message-Generator")
    st.markdown("**Benutzerdefinierte MQTT-Nachrichten erstellen und senden:**")

    with st.expander("📝 Nachricht erstellen", expanded=False):
        show_message_generator()


def _check_mqtt_connection() -> bool:
    """Prüft MQTT-Verbindung (inkl. Mock-Support)"""
    try:
        # Mock-Modus prüfen
        if st.session_state.get("mqtt_mock_enabled", False):
            return True

        # Echte MQTT-Verbindung prüfen
        mqtt_client = get_omf_mqtt_client()
        return mqtt_client.is_connected()
    except Exception:
        return False


def _count_available_templates() -> int:
    """Zählt verfügbare Templates"""
    try:
        template_manager = get_omf_message_template_manager()
        return len(template_manager.templates)
    except Exception:
        return 0


def _count_active_modules() -> int:
    """Zählt aktive Module"""
    try:
        # TODO: Implementiere Module-Zählung
        return 0
    except Exception:
        return 0


def _send_factory_reset_message(with_storage: bool, clear_storage: bool = False):
    """Sendet Factory Reset Message"""
    try:
        mqtt_client = get_omf_mqtt_client()
        message_generator = MessageGenerator()

        # Factory Reset Template verwenden
        reset_message = message_generator.generate_factory_reset_message(with_storage, clear_storage)

        if reset_message:
            topic = reset_message.get("topic", "ccu/factory/reset")
            payload = reset_message.get("payload", {})

            # Generierte Nachricht anzeigen
            st.markdown("**📤 Generierte MQTT-Nachricht:**")
            st.json({"topic": topic, "payload": payload})

            # MQTT-Verbindung prüfen (inkl. Mock-Support)
            if mqtt_client.is_connected() or st.session_state.get("mqtt_mock_enabled", False):
                if st.session_state.get("mqtt_mock_enabled", False):
                    st.success(
                        f"✅ Factory Reset Message simuliert: withStorage={with_storage}, clearStorage={clear_storage}"
                    )
                    st.info("🧪 Mock-Modus: Message wurde nicht wirklich gesendet")
                else:
                    mqtt_client.publish(topic, payload)
                    st.success(
                        f"✅ Factory Reset Message gesendet: withStorage={with_storage}, clearStorage={clear_storage}"
                    )
            else:
                st.warning("⚠️ MQTT nicht verbunden - Message nur generiert (nicht gesendet)")
                st.info("💡 Message wird gesendet sobald MQTT-Verbindung hergestellt ist")
        else:
            st.error("❌ Factory Reset Template nicht gefunden")

    except Exception as e:
        st.error(f"❌ Fehler beim Generieren der Factory Reset Message: {e}")


def _get_module_sequence_steps(module: str) -> list:
    """Gibt die Sequenz-Schritte für ein Modul zurück"""
    sequences = {
        "MILL": ["PICK(MILL)", "MILL(MILL)", "DROP(MILL)"],
        "DRILL": ["PICK(DRILL)", "DRILL(DRILL)", "DROP(DRILL)"],
        "AIQS": ["PICK(AIQS)", "CHECK_QUALITY(AIQS)", "DROP(AIQS)"],
    }
    return sequences.get(module, [])


def _send_module_sequence(module: str):
    """Sendet eine komplette Modul-Sequenz"""
    try:
        mqtt_client = get_omf_mqtt_client()
        message_generator = MessageGenerator()

        # Sequenz-Schritte
        sequence_steps = _get_module_sequence_steps(module)

        for step in sequence_steps:
            # Message für jeden Schritt generieren
            message = message_generator.generate_module_sequence_message(module, step)

            if message:
                topic = message.get("topic", f"module/v1/ff/{module}/order")
                payload = message.get("payload", {})

                mqtt_client.publish(topic, payload)
                st.info(f"Sequenz-Schritt gesendet: {step}")
            else:
                st.error(f"Template für Sequenz-Schritt nicht gefunden: {step}")

    except Exception as e:
        st.error(f"Fehler beim Senden der Modul-Sequenz: {e}")


def _send_single_module_step(module: str, step: str, step_number: int):
    """Sendet einen einzelnen Modul-Schritt mit WorkflowOrderManager"""
    try:
        mqtt_client = get_omf_mqtt_client()
        message_generator = MessageGenerator()

        # WorkflowOrderManager mit Fallback
        order_id = None
        try:
            workflow_manager = get_workflow_order_manager()

            # Aktive Workflows für dieses Modul finden
            active_workflows = workflow_manager.get_active_workflows()
            module_workflows = {k: v for k, v in active_workflows.items() if v["module"] == module}

            # ORDER-ID für diesen Schritt verwenden oder neue erstellen
            if module_workflows:
                # Verwende die erste aktive ORDER-ID für dieses Modul
                order_id = list(module_workflows.keys())[0]
            else:
                # Neue ORDER-ID für neues Workflow erstellen
                commands = ["PICK", "PROCESS", "DROP"]
                order_id = workflow_manager.start_workflow(module, commands)
        except Exception as e:
            st.warning(f"⚠️ WorkflowOrderManager nicht verfügbar: {e}")
            # Fallback: Einfache UUID
            import uuid

            order_id = str(uuid.uuid4())

        # Message für einzelnen Schritt generieren (mit ORDER-ID)
        message = message_generator.generate_module_sequence_message(module, step, step_number, order_id)

        if message:
            topic = message.get("topic", f"module/v1/ff/{module}/order")
            payload = message.get("payload", {})

            # Workflow-Info anzeigen (mit Fallback)
            try:
                workflow_info = workflow_manager.get_workflow_status(order_id)
                if workflow_info:
                    st.info(
                        f"🔄 **Workflow:** ORDER-ID `{order_id[:8]}...` | Update-ID: {workflow_info['orderUpdateId']}"
                    )

                    # orderUpdateId in Payload anzeigen
                    if "parameters" in payload and "orderUpdateId" in payload["parameters"]:
                        st.success(
                            f"✅ **orderUpdateId:** {payload['parameters']['orderUpdateId']} in Nachricht übernommen"
                        )
                    else:
                        st.warning("⚠️ orderUpdateId nicht in Payload gefunden")
            except Exception:
                st.info(f"🔄 **ORDER-ID:** `{order_id[:8]}...`")

            # Generierte Nachricht anzeigen
            st.markdown(f"**📤 Generierte MQTT-Nachricht für {module} {step}:**")
            st.json({"topic": topic, "payload": payload})

            # MQTT-Verbindung prüfen (inkl. Mock-Support)
            if mqtt_client.is_connected() or st.session_state.get("mqtt_mock_enabled", False):
                if st.session_state.get("mqtt_mock_enabled", False):
                    st.success(f"✅ {module} {step} simuliert (Step {step_number})")
                    st.info("🧪 Mock-Modus: Message wurde nicht wirklich gesendet")
                else:
                    mqtt_client.publish(topic, payload)
                    st.success(f"✅ {module} {step} gesendet (Step {step_number})")
            else:
                st.warning("⚠️ MQTT nicht verbunden - Message nur generiert (nicht gesendet)")
                st.info("💡 Message wird gesendet sobald MQTT-Verbindung hergestellt ist")
        else:
            st.error(f"❌ Template für Modul-Schritt nicht gefunden: {module} {step}")

    except Exception as e:
        st.error(f"❌ Fehler beim Generieren des Modul-Schritts: {e}")


def _get_module_status(module: str) -> str:
    """Gibt den aktuellen Status eines Moduls zurück"""
    try:
        # TODO: Implementiere Modul-Status-Abfrage
        return "🟡 Unbekannt"
    except Exception:
        return "🔴 Fehler"


def _get_fts_status() -> str:
    """Gibt den aktuellen FTS-Status zurück"""
    try:
        # TODO: Implementiere FTS-Status-Abfrage
        return "🟡 Unbekannt"
    except Exception:
        return "🔴 Fehler"


def _send_fts_command(command: str):
    """Sendet FTS-Befehl"""
    try:
        mqtt_client = get_omf_mqtt_client()
        message_generator = MessageGenerator()

        # FTS-Command Template verwenden
        fts_message = message_generator.generate_fts_command_message(command)

        if fts_message:
            topic = fts_message.get("topic", "fts/v1/command")
            payload = fts_message.get("payload", {})

            # Generierte Nachricht anzeigen
            st.markdown(f"**📤 Generierte MQTT-Nachricht für FTS {command}:**")
            st.json({"topic": topic, "payload": payload})

            # MQTT-Verbindung prüfen (inkl. Mock-Support)
            if mqtt_client.is_connected() or st.session_state.get("mqtt_mock_enabled", False):
                if st.session_state.get("mqtt_mock_enabled", False):
                    st.success(f"✅ FTS-Befehl simuliert: {command}")
                    st.info("🧪 Mock-Modus: Message wurde nicht wirklich gesendet")
                else:
                    mqtt_client.publish(topic, payload)
                    st.success(f"✅ FTS-Befehl gesendet: {command}")
            else:
                st.warning("⚠️ MQTT nicht verbunden - Message nur generiert (nicht gesendet)")
                st.info("💡 Message wird gesendet sobald MQTT-Verbindung hergestellt ist")
        else:
            st.error(f"❌ FTS-Command Template nicht gefunden: {command}")

    except Exception as e:
        st.error(f"❌ Fehler beim Generieren des FTS-Befehls: {e}")


def show_factory_reset():
    """Zeigt Factory Reset Steuerung mit Dialog"""
    st.markdown("**Fabrik zurücksetzen:**")

    # Factory Reset Dialog
    if st.button("🔄 Factory Reset starten", key="factory_reset_dialog"):
        st.session_state.show_factory_reset_dialog = True

    # Dialog anzeigen
    if st.session_state.get("show_factory_reset_dialog", False):
        with st.expander("⚠️ Factory Reset Dialog", expanded=True):
            st.warning("**Achtung:** Factory Reset wird alle Module zurücksetzen!")

            # Factory Reset Optionen
            st.markdown("**Factory Reset Optionen:**")

            # withStorage Option (Default: FALSE)
            with_storage = st.checkbox(
                "Mit Lagerung zurücksetzen",
                value=False,
                help="Wenn aktiviert, werden Werkstücke im HBW gelagert (withStorage=true)",
            )

            # Lager löschen Option (nur wenn withStorage=false)
            if not with_storage:
                clear_storage = st.checkbox(
                    "Lager löschen",
                    value=False,
                    help="Wenn aktiviert, werden alle Werkstücke aus dem HBW entfernt (clearStorage=true)",
                )
            else:
                clear_storage = False
                st.info("ℹ️ Lager löschen ist nur verfügbar wenn 'Mit Lagerung' deaktiviert ist")

            col1, col2, col3 = st.columns(3)

            # MQTT-Verbindung prüfen
            mqtt_connected = _check_mqtt_connection()

            with col1:
                if st.button(
                    "✅ Bestätigen",
                    key="confirm_factory_reset",
                    disabled=not mqtt_connected,
                ):
                    _send_factory_reset_message(with_storage=with_storage, clear_storage=clear_storage)
                    if mqtt_connected:
                        st.success("Factory Reset ausgeführt")
                    st.session_state.show_factory_reset_dialog = False

            with col2:
                if st.button("❌ Abbrechen", key="cancel_factory_reset"):
                    st.session_state.show_factory_reset_dialog = False
                    st.info("Factory Reset abgebrochen")

            with col3:
                if st.button(
                    "🔄 Nur Lager löschen",
                    key="clear_storage_only",
                    disabled=not mqtt_connected,
                ):
                    _send_factory_reset_message(with_storage=False, clear_storage=True)
                    if mqtt_connected:
                        st.success("Lager gelöscht")
                    st.session_state.show_factory_reset_dialog = False

            # MQTT-Status anzeigen
            if not mqtt_connected:
                st.warning("⚠️ MQTT nicht verbunden - Buttons deaktiviert")


def _show_module_control_box(module: str, icon: str, name: str):
    """Zeigt eine einzelne Modul-Steuerungsbox mit WorkflowOrderManager"""
    st.markdown(f"### {icon} {name} ({module})")

    # Sequenz-Schritte für dieses Modul
    sequence_steps = _get_module_sequence_steps(module)

    # MQTT-Verbindung prüfen
    mqtt_connected = _check_mqtt_connection()

    # WorkflowOrderManager für ORDER-ID Management (mit Fallback)
    try:
        workflow_manager = get_workflow_order_manager()

        # Aktive Workflows für dieses Modul anzeigen
        active_workflows = workflow_manager.get_active_workflows()
        module_workflows = {k: v for k, v in active_workflows.items() if v["module"] == module}

        if module_workflows:
            st.info(f"🔄 {len(module_workflows)} aktive Workflow(s) für {name}")
            for order_id, workflow in module_workflows.items():
                st.markdown(f"**ORDER-ID:** `{order_id[:8]}...` | **Update-ID:** {workflow['orderUpdateId']}")
    except Exception as e:
        st.warning(f"⚠️ WorkflowOrderManager nicht verfügbar: {e}")

    # Befehle nebeneinander in einer Reihe
    cols = st.columns(len(sequence_steps))

    for i, (col, step) in enumerate(zip(cols, sequence_steps)):
        step_name = step.split("(")[0]  # PICK, DRILL, DROP, etc.

        with col:
            if st.button(
                f"▶️ {step_name}",
                key=f"{module}_{step_name}_{i}",
                disabled=not mqtt_connected,
            ):
                _send_single_module_step(module, step, i + 1)
                if mqtt_connected:
                    st.success(f"{module} {step_name} ausgeführt")

    # MQTT-Status anzeigen
    if not mqtt_connected:
        if st.session_state.get("mqtt_mock_enabled", False):
            st.success("🧪 Mock-Modus aktiv - Buttons funktionsfähig")
        else:
            st.warning("⚠️ MQTT nicht verbunden - Buttons deaktiviert")

    # Status-Anzeige
    module_status = _get_module_status(module)
    st.markdown(f"**Status:** {module_status}")

    # Sequenz-Info
    st.markdown(f"**Sequenz:** {' → '.join([step.split('(')[0] for step in sequence_steps])}")


def show_fts_control():
    """Zeigt FTS-Steuerung mit Status-Abhängigkeiten"""
    st.markdown("**FTS (Fahrerloses Transportsystem) Steuerung:**")

    # FTS-Status anzeigen
    fts_status = _get_fts_status()
    st.markdown(f"**Aktueller Status:** {fts_status}")

    # Status-basierte Button-Aktivierung
    is_charging = "charging" in fts_status.lower() or "laden" in fts_status.lower()
    is_at_charging_station = "charging" in fts_status.lower() or "ladestation" in fts_status.lower()

    # MQTT-Verbindung prüfen
    mqtt_connected = _check_mqtt_connection()

    # FTS-Befehle mit Abhängigkeiten
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔌 Laden", key="fts_charge", disabled=is_charging or not mqtt_connected):
            _send_fts_command("charge")
            if mqtt_connected:
                st.success("FTS-Ladebefehl gesendet")

        if st.button("🚪 Dock an DPS", key="fts_dock_dps", disabled=not mqtt_connected):
            _send_fts_command("dock_to_dps")
            if mqtt_connected:
                st.success("FTS-Dock-Befehl gesendet")

    with col2:
        if st.button(
            "🔋 Laden beenden",
            key="fts_finish_charging",
            disabled=not is_at_charging_station or not mqtt_connected,
        ):
            _send_fts_command("finish_charging")
            if mqtt_connected:
                st.success("FTS-Laden-Beenden-Befehl gesendet")

        if st.button("📊 Status abfragen", key="fts_get_status", disabled=not mqtt_connected):
            _send_fts_command("get_status")
            if mqtt_connected:
                st.info("FTS-Status-Abfrage gesendet")

    # MQTT-Status anzeigen
    if not mqtt_connected:
        if st.session_state.get("mqtt_mock_enabled", False):
            st.success("🧪 Mock-Modus aktiv - Buttons funktionsfähig")
        else:
            st.warning("⚠️ MQTT nicht verbunden - Buttons deaktiviert")


def show_message_generator():
    """Zeigt Message-Generator mit Topic-basierter Template-Auswahl"""
    st.markdown("**Message-Generator für benutzerdefinierte MQTT-Nachrichten:**")

    try:
        # Topic-Mapping-Manager laden
        topic_manager = get_omf_topic_mapping_manager()
        available_topics = topic_manager.get_available_topics()

        if available_topics:
            # Topic-Auswahl
            selected_topic = st.selectbox("MQTT Topic auswählen:", available_topics)

            if selected_topic:
                # Topic-Informationen anzeigen
                topic_info = topic_manager.get_topic_info(selected_topic)
                if topic_info:
                    st.markdown(f"**📡 Topic: {selected_topic}**")
                    st.info(f"**Beschreibung:** {topic_info.get('description', 'Keine Beschreibung')}")
                    st.info(f"**Richtung:** {topic_info.get('direction', 'Unbekannt')}")
                    st.info(f"**Zweck:** {topic_info.get('semantic_purpose', 'Unbekannt')}")

                # Template für Topic finden
                template_name = topic_manager.get_template_for_topic(selected_topic)

                if template_name:
                    st.markdown(f"**📋 Verwendetes Template: {template_name}**")

                    # Beispiel-Nachricht generieren
                    try:
                        message_generator = get_omf_message_generator()

                        # Topic-spezifische Parameter generieren
                        example_params = _generate_topic_specific_params(selected_topic, topic_info)

                        # Beispiel-Nachricht generieren
                        example_message = message_generator.generate_message(template_name, **example_params)

                        if example_message:
                            topic, payload = example_message

                            # Editierbare Nachricht anzeigen
                            st.markdown("**📝 Beispiel-Nachricht (editierbar):**")

                            # Topic editieren (mit Resolved-Variablen)
                            resolved_topic = _resolve_topic_variables(selected_topic, example_params)
                            edited_topic = st.text_input("MQTT Topic:", value=resolved_topic, key="edit_topic")

                            # Payload editieren
                            st.markdown("**Payload (JSON):**")
                            payload_json = json.dumps(payload, indent=2, ensure_ascii=False)
                            edited_payload = st.text_area(
                                "Payload:",
                                value=payload_json,
                                height=200,
                                key="edit_payload",
                            )

                            # JSON Validierung
                            try:
                                parsed_payload = json.loads(edited_payload)
                                st.success("✅ JSON ist gültig")

                                # Senden-Button
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    if st.button("📤 Senden", key="send_custom_message"):
                                        # MQTT-Verbindung prüfen
                                        mqtt_connected = _check_mqtt_connection()

                                        if mqtt_connected:
                                            try:
                                                # MQTT Client holen
                                                mqtt_client = get_omf_mqtt_client()

                                                # Message senden
                                                mqtt_client.publish(
                                                    edited_topic,
                                                    json.dumps(parsed_payload),
                                                )

                                                if st.session_state.get("mqtt_mock_enabled", False):
                                                    st.success("🧪 Message simuliert gesendet!")
                                                else:
                                                    st.success("✅ Message erfolgreich gesendet!")

                                            except Exception as e:
                                                st.error(f"❌ Fehler beim Senden: {e}")
                                        else:
                                            st.warning("⚠️ MQTT nicht verbunden - Message nicht gesendet")

                                with col2:
                                    st.info("ℹ️ Nachricht wird an das ausgewählte Topic gesendet")

                            except json.JSONDecodeError as e:
                                st.error(f"❌ Ungültiges JSON: {e}")
                                st.info("ℹ️ Bitte korrigieren Sie das JSON-Format")

                        else:
                            st.warning("⚠️ Konnte keine Beispiel-Nachricht für dieses Template generieren")

                    except Exception as e:
                        st.error(f"❌ Fehler beim Generieren der Beispiel-Nachricht: {e}")
                        st.info("ℹ️ Template nicht gefunden oder ungültig")
                else:
                    st.warning("⚠️ Kein Template für dieses Topic gefunden")
        else:
            st.info("Keine Topics verfügbar")

    except Exception as e:
        st.error(f"Fehler beim Laden der Topic-Mappings: {e}")


def _generate_topic_specific_params(topic: str, topic_info: dict) -> dict:
    """Generiert topic-spezifische Parameter basierend auf Topic-Pattern"""
    base_params = {"timestamp": datetime.now().isoformat()}

    if "module/v1/ff/" in topic and "/order" in topic:
        # Module Order Topic
        base_params.update(
            {
                "module_id": "SVR3QA2098",  # MILL
                "command": "PICK",
                "order_id": "example-order-123",
                "parameters": {"orderUpdateId": 1, "subActionId": 1},
            }
        )
    elif "module/v1/ff/" in topic and "/state" in topic:
        # Module State Topic
        base_params.update({"module_id": "SVR3QA2098", "status": "IDLE"})
    elif "module/v1/ff/" in topic and "/connection" in topic:
        # Module Connection Topic
        base_params.update({"module_id": "SVR3QA2098", "connected": True, "ip": "192.168.0.40"})
    elif "ccu/state/stock" in topic:
        # CCU Stock State Topic
        base_params.update(
            {
                "stockItems": [
                    {
                        "hbw": "SVR3QA0022",
                        "location": "A1",
                        "workpiece": {
                            "id": "040a8dca341291",
                            "state": "RAW",
                            "type": "RED",
                        },
                    }
                ],
                "ts": datetime.now().isoformat(),
            }
        )
    elif "ccu/order" in topic:
        # CCU Order Topic
        base_params.update({"type": "RED", "workpieceId": "040a8dca341291", "orderType": "PRODUCTION"})
    elif "fts" in topic:
        # FTS Topic
        base_params.update({"serialNumber": "5iO4", "command": "PICK"})

    return base_params


def _resolve_topic_variables(topic_pattern: str, params: dict) -> str:
    """Löst Variable in Topic-Patterns auf"""
    resolved_topic = topic_pattern

    # Module-ID auflösen
    if "{module_id}" in resolved_topic and "module_id" in params:
        resolved_topic = resolved_topic.replace("{module_id}", params["module_id"])

    return resolved_topic


def show_order_request():
    """Zeigt Bestellungs-Funktionalität mit Farb- und Typ-Auswahl"""
    st.markdown("### 📦 Bestellung auslösen")
    st.markdown("**Werkstück-Bestellung für verschiedene Farben und Workflow-Typen:**")

    # MQTT-Verbindung prüfen
    mqtt_connected = _check_mqtt_connection()

    # Bestellungs-Optionen
    col1, col2 = st.columns(2)

    with col1:
        # Farbe auswählen
        color = st.selectbox(
            "🎨 Werkstück-Farbe:",
            ["RED", "WHITE", "BLUE"],
            format_func=lambda x: {"RED": "🔴 Rot", "WHITE": "⚪ Weiß", "BLUE": "🔵 Blau"}[x],
        )

        # Workflow-Typ auswählen (nur Produktion macht Sinn für Bestellungen)
        order_type = st.selectbox(
            "📋 Workflow-Typ:",
            ["PRODUCTION"],  # Nur Produktion verfügbar
            format_func=lambda x: {"PRODUCTION": "⚙️ Auftrag (Produktion)"}[x],
        )

    with col2:
        # Werkstück-ID (optional)
        workpiece_id = st.text_input(
            "🆔 Werkstück-ID (optional):",
            value="",
            help="14-stellige NFC-ID (z.B. 040a8dca341291). Leer lassen für automatische Generierung.",
        )

        # Bestellungs-Button
        if st.button(
            "📤 Bestellung auslösen",
            key="send_order_request",
            disabled=not mqtt_connected,
        ):
            _send_order_request(color, order_type, workpiece_id)

    # MQTT-Status anzeigen
    if not mqtt_connected:
        if st.session_state.get("mqtt_mock_enabled", False):
            st.success("🧪 Mock-Modus aktiv - Bestellung wird simuliert")
        else:
            st.warning("⚠️ MQTT nicht verbunden - Bestellung nicht möglich")

    # Workflow-Info anzeigen
    st.markdown("---")
    st.markdown("**ℹ️ Workflow-Informationen:**")

    workflow_info = {
        "RED": {"PRODUCTION": "🔴 Rot → MILL → AIQS → Ausgang"},
        "WHITE": {"PRODUCTION": "⚪ Weiß → DRILL → AIQS → Ausgang"},
        "BLUE": {"PRODUCTION": "🔵 Blau → DRILL → MILL → AIQS → Ausgang"},
    }

    st.info(f"**Workflow:** {workflow_info[color][order_type]}")


def _send_order_request(color: str, order_type: str, workpiece_id: str = ""):
    """Sendet Bestellungs-Request"""
    try:
        mqtt_client = get_omf_mqtt_client()
        message_generator = MessageGenerator()

        # Werkstück-ID generieren falls nicht angegeben
        if not workpiece_id:
            import uuid

            workpiece_id = f"040a8dca{uuid.uuid4().hex[:6]}"

        # Spezialisierte CCU Order Request Nachricht generieren
        # Nur Produktion verfügbar, AI-Inspection ist Teil der Produktion
        message = message_generator.generate_ccu_order_request_message(
            color=color,
            order_type="PRODUCTION",
            workpiece_id=workpiece_id,
            ai_inspection=False,  # AI-Inspection ist automatisch Teil der Produktion
        )

        if message:
            topic, payload = message

            # Generierte Nachricht anzeigen
            st.markdown("**📤 Generierte Bestellungs-Nachricht:**")
            st.json({"topic": topic, "payload": payload})

            # MQTT-Verbindung prüfen (inkl. Mock-Support)
            if mqtt_client.is_connected() or st.session_state.get("mqtt_mock_enabled", False):
                if st.session_state.get("mqtt_mock_enabled", False):
                    st.success(f"✅ Bestellung simuliert: {color} {order_type}")
                    st.info("🧪 Mock-Modus: Nachricht wurde nicht wirklich gesendet")
                else:
                    mqtt_client.publish(topic, payload)
                    st.success(f"✅ Bestellung gesendet: {color} {order_type}")
                    st.info(f"🆔 Werkstück-ID: {workpiece_id}")
            else:
                st.warning("⚠️ MQTT nicht verbunden - Bestellung nur generiert (nicht gesendet)")
        else:
            st.error("❌ Template für Bestellung nicht gefunden: ccu/order/request")

    except Exception as e:
        st.error(f"❌ Fehler beim Generieren der Bestellung: {e}")


def show_factory_control():
    """Zeigt Factory-Steuerung (Factory Reset + Bestellung)"""
    st.markdown("### 🏭 Factory Steuerung")

    # Factory Reset
    with st.expander("🔄 Factory Reset", expanded=True):
        show_factory_reset()

    # Bestellung
    with st.expander("📦 Bestellung auslösen", expanded=True):
        show_order_request()


# Export functions
def show_steering():
    """Hauptexport-Funktion"""
    show_steering_dashboard()
