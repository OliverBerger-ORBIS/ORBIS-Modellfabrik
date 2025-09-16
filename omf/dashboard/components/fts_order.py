"""
FTS Order Komponente

Zeigt FTS-Befehle und Navigation an.
MQTT-Topic: fts/v1/ff/5iO4/order
"""

from datetime import datetime

import streamlit as st

# MessageProcessor entfernt - verwenden jetzt Per-Topic-Buffer

# MessageTemplate Bibliothek Import
try:
    from omf.tools.message_template_manager import get_message_template_manager

    TEMPLATE_MANAGER_AVAILABLE = True
except ImportError as e:
    TEMPLATE_MANAGER_AVAILABLE = False
    print(f"❌ MessageTemplate Import-Fehler: {e}")
except Exception as e:
    TEMPLATE_MANAGER_AVAILABLE = False
    print(f"❌ MessageTemplate Fehler: {e}")


def process_fts_order_messages_from_buffers(order_messages):
    """Verarbeitet FTS-Order-Nachrichten aus Per-Topic-Buffer"""
    if not order_messages:
        return

    # Neueste FTS-Order-Nachricht finden
    if order_messages:
        latest_order_msg = max(order_messages, key=lambda x: x.get("ts", 0))
        # Order-Daten in Session-State speichern
        st.session_state["fts_order_data"] = latest_order_msg.get("payload", {})
        # Timestamp für letzte Aktualisierung speichern
        st.session_state["fts_order_last_update"] = latest_order_msg.get("ts", 0)


def get_formatted_timestamp(timestamp):
    """Timestamp in lesbares Format konvertieren (wie in overview_inventory)"""
    if not timestamp:
        return "Nie aktualisiert"

    try:
        # Unix-Timestamp zu datetime konvertieren
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except (ValueError, OSError):
        return f"Timestamp: {timestamp}"


def analyze_fts_order_data(order_data):
    """Analysiert FTS-Order-Daten semantisch basierend auf RAW-Data-Struktur"""
    if not order_data:
        return {}

    try:
        import json

        if isinstance(order_data, str):
            order_data = json.loads(order_data)

        # Semantische Analyse basierend auf RAW-Data
        analysis = {
            # Grundinformationen
            "serial_number": order_data.get("serialNumber", "N/A"),
            "timestamp": order_data.get("timestamp", "N/A"),
            "order_id": order_data.get("orderId", "N/A"),
            "order_update_id": order_data.get("orderUpdateId", "N/A"),
            # Navigation
            "nodes": [],
            "edges": [],
            "node_count": 0,
            "edge_count": 0,
            # Route-Analyse
            "route_summary": "Keine Route",
            "start_node": "N/A",
            "end_node": "N/A",
            "total_distance": 0,
            # Aktionen
            "actions": [],
            "action_count": 0,
            "action_types": [],
            "has_turn": False,
            "has_dock": False,
            "has_pass": False,
        }

        # Nodes analysieren
        nodes = order_data.get("nodes", [])
        if nodes:
            analysis["nodes"] = nodes
            analysis["node_count"] = len(nodes)

            # Start- und End-Node identifizieren
            if len(nodes) >= 2:
                analysis["start_node"] = nodes[0].get("id", "N/A")
                analysis["end_node"] = nodes[-1].get("id", "N/A")

            # Aktionen aus Nodes extrahieren
            actions = []
            for node in nodes:
                action = node.get("action", {})
                if action:
                    actions.append(action)

            analysis["actions"] = actions
            analysis["action_count"] = len(actions)

            # Aktion-Typen sammeln
            action_types = [action.get("type", "UNKNOWN") for action in actions]
            analysis["action_types"] = list(set(action_types))  # Eindeutige Typen

            # Spezifische Aktion-Typen prüfen
            analysis["has_turn"] = "TURN" in action_types
            analysis["has_dock"] = "DOCK" in action_types
            analysis["has_pass"] = "PASS" in action_types

        # Edges analysieren
        edges = order_data.get("edges", [])
        if edges:
            analysis["edges"] = edges
            analysis["edge_count"] = len(edges)

            # Gesamtdistanz berechnen
            total_distance = sum(edge.get("length", 0) for edge in edges)
            analysis["total_distance"] = total_distance

        # Route-Zusammenfassung erstellen
        if analysis["node_count"] > 0:
            start = analysis["start_node"]
            end = analysis["end_node"]
            distance = analysis["total_distance"]
            action_summary = ", ".join(analysis["action_types"])

            if start != "N/A" and end != "N/A":
                analysis["route_summary"] = f"Von {start} nach {end} ({distance}mm)"
                if action_summary:
                    analysis["route_summary"] += f" - Aktionen: {action_summary}"
            else:
                analysis["route_summary"] = f"{analysis['node_count']} Nodes, {distance}mm"

        # Template-Validierung (falls verfügbar)
        template_validation = None
        if TEMPLATE_MANAGER_AVAILABLE:
            try:
                template_manager = get_message_template_manager()
                # Versuche FTS-Order-Topic zu validieren
                validation_result = template_manager.validate_message("fts/v1/ff/5iO4/order", order_data)
                if validation_result.get("valid", False):
                    template_validation = {
                        "valid": True,
                        "topic": "fts/v1/ff/5iO4/order",
                        "template": validation_result.get("template", {}),
                    }
                else:
                    template_validation = {
                        "valid": False,
                        "topic": "fts/v1/ff/5iO4/order",
                        "errors": validation_result.get("errors", []),
                        "template": validation_result.get("template", {}),
                        "error": validation_result.get("error", "Unknown error"),
                    }
            except Exception as e:
                template_validation = {
                    "valid": False,
                    "error": f"Template-Validierung fehlgeschlagen: {e}",
                }

        analysis["template_validation"] = template_validation
        return analysis

    except Exception as e:
        st.warning(f"⚠️ Fehler bei der FTS-Order-Analyse: {e}")
        return {}


def show_fts_order():
    """Zeigt FTS-Order-Informationen"""
    st.subheader("📋 FTS Order")

    # MQTT-Client für Per-Topic-Buffer
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # FTS-Order-Topic abonnieren
        mqtt_client.subscribe_many(["fts/v1/ff/5iO4/order"])

        # Nachrichten aus Per-Topic-Buffer holen
        order_messages = list(mqtt_client.get_buffer("fts/v1/ff/5iO4/order"))

        # Nachrichten verarbeiten
        process_fts_order_messages_from_buffers(order_messages)

        # Status-Anzeige
        last_update_timestamp = st.session_state.get("fts_order_last_update")
        if last_update_timestamp:
            formatted_time = get_formatted_timestamp(last_update_timestamp)
            st.success(f"✅ FTS Order aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine FTS-Order-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - FTS Order wird nicht aktualisiert")

    # Order-Daten anzeigen
    order_data = st.session_state.get("fts_order_data")

    if order_data:
        # Semantische Analyse der FTS-Order-Daten
        analysis = analyze_fts_order_data(order_data)

        if analysis:
            # Order-Informationen mit korrekten Feldnamen
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📤 Aktuelle Order")
                order_id = analysis.get("order_id", "N/A")
                st.write(f"**Order ID:** {order_id}")

                order_update_id = analysis.get("order_update_id", "N/A")
                st.write(f"**Order Update ID:** {order_update_id}")

                serial_number = analysis.get("serial_number", "N/A")
                st.write(f"**Serial Number:** {serial_number}")

            with col2:
                st.markdown("### 🗺️ Navigation")
                route_summary = analysis.get("route_summary", "Keine Route")
                st.write(f"**Route:** {route_summary}")

                start_node = analysis.get("start_node", "N/A")
                st.write(f"**Start:** {start_node}")

                end_node = analysis.get("end_node", "N/A")
                st.write(f"**Ziel:** {end_node}")

                # Timestamp
                timestamp = analysis.get("timestamp", "N/A")
                if timestamp != "N/A":
                    st.write(f"**Timestamp:** {timestamp}")

            # Route-Details
            st.markdown("### 🛣️ Route-Details")
            node_count = analysis.get("node_count", 0)
            edge_count = analysis.get("edge_count", 0)
            total_distance = analysis.get("total_distance", 0)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Nodes", node_count)
            with col2:
                st.metric("Edges", edge_count)
            with col3:
                st.metric("Distanz", f"{total_distance}mm")

            # Aktionen
            st.markdown("### 🎯 Aktionen")
            actions = analysis.get("actions", [])
            action_count = analysis.get("action_count", 0)
            action_types = analysis.get("action_types", [])

            if actions:
                st.write(f"**Anzahl Aktionen:** {action_count}")
                st.write(f"**Aktion-Typen:** {', '.join(action_types)}")

                # Spezifische Aktionen
                if analysis.get("has_turn", False):
                    st.info("🔄 **Turn-Aktion:** FTS dreht sich")
                if analysis.get("has_dock", False):
                    st.success("🔗 **Dock-Aktion:** FTS dockt an")
                if analysis.get("has_pass", False):
                    st.info("➡️ **Pass-Aktion:** FTS fährt durch")

                # Aktion-Details
                st.markdown("**Aktion-Details:**")
                for i, action in enumerate(actions, 1):
                    action_type = action.get("type", "UNKNOWN")
                    action_id = action.get("id", "N/A")
                    metadata = action.get("metadata", {})

                    st.write(f"{i}. **{action_type}** (ID: {action_id})")
                    if metadata:
                        for key, value in metadata.items():
                            st.write(f"   - **{key}:** {value}")
            else:
                st.info("ℹ️ Keine Aktionen in dieser Order")

            # Template-Validierung
            template_validation = analysis.get("template_validation")
            st.markdown("### 📋 MessageTemplate Validierung")

            if template_validation:
                if template_validation.get("valid", False):
                    st.success(f"✅ **Template gültig:** {template_validation.get('topic', 'Unknown')}")
                    template = template_validation.get("template", {})
                    if template:
                        st.write(f"**Template:** {template.get('description', 'N/A')}")
                        st.write(f"**Kategorie:** {template.get('category', 'N/A')}")
                else:
                    st.error("❌ **Template-Validierung fehlgeschlagen**")
                    error = template_validation.get("error", "Unknown error")
                    st.write(f"**Fehler:** {error}")
                    errors = template_validation.get("errors", [])
                    if errors:
                        st.write("**Validierungsfehler:**")
                        for error in errors:
                            st.write(f"- {error}")
            else:
                st.warning("⚠️ **Template-Validierung nicht verfügbar**")

            # Raw Data (erweiterbar)
            with st.expander("🔍 Raw Order Data"):
                st.json(order_data)

        else:
            st.error("❌ Fehler bei der semantischen Analyse der Order-Daten")
            st.write("**Raw Data:**")
            st.write(order_data)
    else:
        st.write("**MQTT-Topic:** `fts/v1/ff/5iO4/order`")
