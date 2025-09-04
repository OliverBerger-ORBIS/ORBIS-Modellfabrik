"""
Generische Steuerung Component für OMF Dashboard
Erweiterte Steuerungsmöglichkeiten für direkte MQTT-Nachrichten
"""

import json
from datetime import datetime
from pathlib import Path

import streamlit as st


def show_generic_steering():
    """Hauptfunktion für die Generic Steuerung"""
    st.subheader("🔧 Generic Steuerung")
    st.markdown("**Erweiterte Steuerungsmöglichkeiten für direkte MQTT-Nachrichten:**")

    # Freier Modus
    st.markdown("### 📝 Freier Modus")
    st.markdown("**Direkte Eingabe von Topic und Message-Payload:**")
    show_free_mode()

    # Topic-getriebener Ansatz
    st.markdown("---")
    st.markdown("### 📡 Topic-getriebener Ansatz")
    st.markdown("**Topic auswählen und passende Message-Templates verwenden:**")
    show_topic_driven_mode()

    # Message-getriebener Ansatz (Platzhalter)
    st.markdown("---")
    st.markdown("### 📋 Message-getriebener Ansatz")
    st.markdown("**Message-Template auswählen und Topic bearbeiten:**")
    st.info("🔄 Diese Funktion wird in der nächsten Version implementiert")


def show_free_mode():
    """Zeigt Freien Modus für direkte MQTT-Nachrichten"""
    # Session State für Topic und Payload
    if "free_mode_topic" not in st.session_state:
        st.session_state.free_mode_topic = "ccu/set/reset"
    if "free_mode_payload" not in st.session_state:
        st.session_state.free_mode_payload = json.dumps(
            {"timestamp": datetime.now().isoformat(), "withStorage": False}, indent=2, ensure_ascii=False
        )

    # Topic-Eingabe (unabhängig von Form)
    topic = st.text_input(
        "📡 MQTT Topic:",
        value=st.session_state.free_mode_topic,
        key="free_mode_topic_input",
        help="Geben Sie das gewünschte MQTT Topic ein",
    )

    # Message-Eingabe (JSON) - unabhängig von Form
    st.markdown("**📄 Message Payload (JSON):**")
    payload_json = st.text_area(
        "Payload:",
        value=st.session_state.free_mode_payload,
        key="free_mode_payload_input",
        height=150,
        help="Geben Sie den JSON-Payload ein",
    )

    # Session State aktualisieren (bei jeder Änderung)
    if st.session_state.free_mode_topic_input != st.session_state.free_mode_topic:
        st.session_state.free_mode_topic = st.session_state.free_mode_topic_input

    if st.session_state.free_mode_payload_input != st.session_state.free_mode_payload:
        st.session_state.free_mode_payload = st.session_state.free_mode_payload_input

    # Retain-Option
    retain_option = st.checkbox("💾 Retain Message", value=False, key="free_mode_retain")

    # Senden-Button (unabhängig von Form)
    if st.button("📤 Versenden mit MQTT-Client", key="free_mode_send"):
        # JSON Validierung
        try:
            parsed_payload = json.loads(payload_json)
            st.success("✅ JSON ist gültig")

            # Debug: Zeige die aktuellen Session State Werte
            st.info("🔍 **Session State Werte:**")
            st.info(f"🔍 Topic (Session): {st.session_state.free_mode_topic}")
            st.info(f"🔍 Payload (Session): {st.session_state.free_mode_payload}")
            st.info(f"🔍 Topic (Input): {st.session_state.free_mode_topic_input}")
            st.info(f"🔍 Payload (Input): {st.session_state.free_mode_payload_input}")

            # Direkt über MQTT-Client senden
            mqtt_client = st.session_state.get("mqtt_client")
            if mqtt_client and mqtt_client.connected:
                # Debug: Zeige die tatsächlich gesendete Payload
                st.info("🔍 **Wird gesendet:**")
                st.info(f"🔍 Topic: {topic}")
                st.info(f"🔍 Payload: {json.dumps(parsed_payload, indent=2)}")
                st.info(f"🔍 Retain: {retain_option}")

                # Nachrichten vor dem Senden zählen
                messages_before = len(mqtt_client.drain())
                st.info(f"🔍 Nachrichten vor dem Senden: {messages_before}")

                result = mqtt_client.publish(topic, parsed_payload, qos=1, retain=retain_option)

                # Nachrichten nach dem Senden zählen
                messages_after = len(mqtt_client.drain())
                st.info(f"🔍 Nachrichten nach dem Senden: {messages_after}")
                st.info(f"🔍 Neue Nachrichten: {messages_after - messages_before}")

                if result:
                    st.success(f"✅ Message erfolgreich gesendet an {topic}")
                    st.info(f"📄 Payload: {json.dumps(parsed_payload, indent=2)}")

                    # Debug: Alle Nachrichten anzeigen
                    all_messages = mqtt_client.drain()
                    sent_messages = [msg for msg in all_messages if msg.get("type") == "sent"]
                    st.info(f"🔍 Gesendete Nachrichten im Client: {len(sent_messages)}")

                else:
                    st.error("❌ Fehler beim Senden der Message")
            else:
                st.error("❌ MQTT nicht verbunden")

        except json.JSONDecodeError as e:
            st.error(f"❌ Ungültiges JSON: {e}")
            st.info("ℹ️ Bitte korrigieren Sie das JSON-Format")


def show_topic_driven_mode():
    """Zeigt Topic-getriebenen Modus mit YAML-Integration"""
    try:
        # Alle Topics aus topic-config.yml laden
        import yaml

        topic_config_path = Path(__file__).parent.parent.parent / "config" / "topic_config.yml"
        topic_mapping_path = Path(__file__).parent.parent.parent / "config" / "topic_message_mapping.yml"

        # Topic-Konfiguration laden
        with open(topic_config_path, encoding="utf-8") as f:
            topic_config = yaml.safe_load(f)

        # Topic-Message-Mapping laden
        with open(topic_mapping_path, encoding="utf-8") as f:
            topic_mapping = yaml.safe_load(f)

        # Alle verfügbaren Topics extrahieren
        available_topics = []
        if topic_config and "topics" in topic_config:
            for topic, info in topic_config["topics"].items():
                # Nur outbound Topics anzeigen (für Steuerung)
                template_direction = info.get("template_direction", "unknown")
                if template_direction in ["outbound", "bidirectional"]:
                    friendly_name = info.get("friendly_name", topic)
                    category = info.get("category", "Unknown")
                    description = info.get("description", "")

                    available_topics.append(
                        {
                            "topic": topic,
                            "friendly_name": friendly_name,
                            "category": category,
                            "description": description,
                            "template_direction": template_direction,
                        }
                    )

        # Topics nach Kategorie gruppieren
        if available_topics:
            # Topic-Auswahl
            topic_options = [(t["topic"], f"{t['friendly_name']} ({t['category']})") for t in available_topics]

            selected_topic_info = st.selectbox(
                "📡 MQTT Topic auswählen:",
                options=topic_options,
                format_func=lambda x: x[1],
                help="Wählen Sie ein Topic aus der Liste der verfügbaren Steuerungs-Topics",
            )

            # Topic-Info verarbeiten
            if selected_topic_info:
                selected_topic = selected_topic_info[0]

                # Topic-Info aus der Konfiguration holen
                topic_info = next((t for t in available_topics if t["topic"] == selected_topic), None)

                if topic_info:
                    st.info(f"**Ausgewähltes Topic:** {selected_topic}")
                    st.info(f"**Kategorie:** {topic_info['category']}")
                    st.info(f"**Beschreibung:** {topic_info['description']}")

                    # Message-Template aus topic_message_mapping.yml finden
                    template_name = "general"  # Default
                    template_description = "Allgemeine Nachrichten"

                    if topic_mapping and "topic_mappings" in topic_mapping:
                        # Exakte Topic-Übereinstimmung suchen
                        if selected_topic in topic_mapping["topic_mappings"]:
                            mapping_info = topic_mapping["topic_mappings"][selected_topic]
                            template_name = mapping_info.get("template", "general")
                            template_description = mapping_info.get("description", "Allgemeine Nachrichten")
                        else:
                            # Pattern-basierte Suche für Module-Topics
                            for pattern, mapping_info in topic_mapping["topic_mappings"].items():
                                if "{" in pattern:  # Pattern mit Platzhaltern
                                    # Einfache Pattern-Übereinstimmung
                                    if pattern.replace("{module_id}", "").replace("{moduleId}", "") in selected_topic:
                                        template_name = mapping_info.get("template", "general")
                                        template_description = mapping_info.get("description", "Allgemeine Nachrichten")
                                        break

                    st.info(f"**Verwendetes Template:** {template_name}")
                    st.info(f"**Template-Beschreibung:** {template_description}")

                    # Beispiel-Payload basierend auf Template generieren
                    example_payload = _generate_example_payload(template_name, selected_topic)

                    # Payload-Bearbeitung
                    st.markdown("**📄 Message Payload (JSON) - Bearbeiten Sie die Beispiel-Nachricht:**")

                    payload_json = st.text_area(
                        "Payload:",
                        value=json.dumps(example_payload, indent=2, ensure_ascii=False),
                        height=200,
                        help="Bearbeiten Sie die Beispiel-Nachricht nach Ihren Wünschen",
                        key="topic_driven_payload_editor",
                    )

                    # JSON-Validierung nach dem Editieren
                    json_valid = False
                    parsed_payload = None

                    try:
                        parsed_payload = json.loads(payload_json)
                        json_valid = True
                        st.success("✅ JSON ist gültig")
                    except json.JSONDecodeError as e:
                        st.error(f"❌ Ungültiges JSON: {e}")
                        st.info("ℹ️ Bitte korrigieren Sie das JSON-Format")
                        json_valid = False

                    # Senden-Button (nur wenn JSON gültig ist)
                    if json_valid and parsed_payload:
                        # Retain-Option VOR dem Senden anzeigen
                        retain_option = st.checkbox("💾 Retain Message", value=False, key="retain_topic_driven")

                        if st.button("📤 Versenden mit MQTT-Client", key="send_topic_driven_message"):
                            # Direkt über MQTT-Client senden
                            mqtt_client = st.session_state.get("mqtt_client")
                            if mqtt_client and mqtt_client.connected:
                                result = mqtt_client.publish(
                                    selected_topic, parsed_payload, qos=1, retain=retain_option
                                )
                                if result:
                                    st.success(f"✅ Message erfolgreich gesendet an {selected_topic}")
                                    st.info(f"📄 Payload: {json.dumps(parsed_payload, indent=2)}")
                                else:
                                    st.error("❌ Fehler beim Senden der Message")
                            else:
                                st.error("❌ MQTT nicht verbunden")
                    else:
                        st.warning("⚠️ JSON muss gültig sein, bevor gesendet werden kann")
        else:
            st.warning("⚠️ Keine verfügbaren Topics gefunden")
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Topic-Konfiguration: {e}")
        st.info("ℹ️ Überprüfen Sie die topic-config.yml und topic_message_mapping.yml Dateien")


def _generate_example_payload(template_name: str, selected_topic: str) -> dict:
    """Generiert Beispiel-Payload basierend auf Template und Topic"""
    # Gültiger Timestamp
    current_timestamp = datetime.now().isoformat()

    if template_name == "ccu/control":
        return {
            "command": "start",
            "parameters": {"mode": "normal", "modules": ["SVR3QA0022", "SVR3QA2098"]},
            "priority": 8,
            "timestamp": current_timestamp,
        }
    elif template_name == "module/order":
        # Modul-spezifische Befehle basierend auf Topic
        if "HBW" in selected_topic:
            return {
                "serialNumber": "SVR3QA0022",
                "orderId": "ORDER_001",
                "orderUpdateId": 1,
                "action": {
                    "id": "action_001",
                    "command": "PICK",
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            }
        elif "MILL" in selected_topic:
            return {
                "serialNumber": "SVR3QA2098",
                "orderId": "ORDER_002",
                "orderUpdateId": 1,
                "action": {
                    "id": "action_002",
                    "command": "MILL",
                    "metadata": {"priority": "HIGH", "timeout": 600, "type": "WHITE"},
                },
            }
        elif "DRILL" in selected_topic:
            return {
                "serialNumber": "SVR4H76449",
                "orderId": "ORDER_003",
                "orderUpdateId": 1,
                "action": {
                    "id": "action_003",
                    "command": "DRILL",
                    "metadata": {"priority": "HIGH", "timeout": 450, "type": "BLUE"},
                },
            }
        elif "AIQS" in selected_topic:
            return {
                "serialNumber": "SVR4H76530",
                "orderId": "ORDER_004",
                "orderUpdateId": 1,
                "action": {
                    "id": "action_004",
                    "command": "CHECK_QUALITY",
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            }
        else:
            return {
                "serialNumber": "MODULE_ID",
                "orderId": "ORDER_XXX",
                "orderUpdateId": 1,
                "action": {
                    "id": "action_XXX",
                    "command": "COMMAND",
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            }
    elif template_name == "txt/sensor_control":
        return {
            "sensor_type": "bme680",
            "command": "start",
            "parameters": {"sampling_rate": 1000, "temperature_unit": "celsius"},
            "ts": current_timestamp,
        }
    else:
        return {"command": "example", "timestamp": current_timestamp, "parameters": {"value": 123, "enabled": True}}
