"""
OMF Dashboard Settings - Message Templates
Exakte Kopie der show_messages_templates() Funktion aus settings.py
"""

import os
import sys

import streamlit as st

# Add src_orbis to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def show_messages_templates():
    """Zeigt die Message Templates an - Exakte Kopie aus settings.py"""
    st.markdown("### 📋 Message Templates")
    st.markdown("Message Template-Konfiguration und -Verwaltung")

    # Message Templates Display
    st.markdown("#### 📋 Message Templates (Struktur-Definitionen)")
    st.info("💡 Templates = Message-Struktur-Definitionen (nicht Beispiel-Nachrichten!)")

    # Template-Auswahl - Alle verfügbaren Templates
    template_categories = {
        "Module": {
            "connection": "Module Connection Status",
            "state": "Module State",
            "order": "Module Order",
            "factsheet": "Module Factsheet",
        },
        "CCU": {
            "control": "CCU Control",
            "state_config": "CCU State Config",
            "state_status": "CCU State Status",
        },
        "TXT": {
            "order_input": "TXT Order Input",
            "stock_input": "TXT Stock Input",
            "sensor_control": "TXT Sensor Control",
            "input": "TXT Input",
            "function_output": "TXT Function Output",
            "function_input": "TXT Function Input",
            "output": "TXT Output",
            "control": "TXT Control",
        },
        "Node-RED": {
            "ui": "Node-RED UI",
            "status": "Node-RED Status",
            "order": "Node-RED Order",
            "instantaction": "Node-RED Instant Action",
            "factsheet": "Node-RED Factsheet",
            "connection": "Node-RED Connection",
            "flows": "Node-RED Flows",
            "dashboard": "Node-RED Dashboard",
            "state": "Node-RED State",
        },
    }

    # Template-Kategorien als expandierte Expander
    selected_category = st.selectbox(
        "📁 Template-Kategorie auswählen:",
        list(template_categories.keys()),
        format_func=lambda x: f"{x} ({len(template_categories[x])} Templates)",
        index=0,
        key="template_category",
    )

    # Template-Auswahl basierend auf Kategorie
    if selected_category:
        selected_template = st.selectbox(
            "📋 Template auswählen:",
            list(template_categories[selected_category].keys()),
            format_func=lambda x: template_categories[selected_category][x],
            index=0,
            key="template_selection",
        )

    # Template laden und anzeigen (für alle Tabs)
    if selected_category and selected_template:
        try:
            from pathlib import Path

            import yaml

            # Debug: Zeige Template-Pfad
            # Node-RED Templates haben keine _template.yml Endung
            if selected_category == "Node-RED":
                template_path = Path(
                    f"src_orbis/omf/config/message_templates/templates/node_red/{selected_template}.yml"
                )
            else:
                template_path = Path(
                    f"src_orbis/omf/config/message_templates/templates/{selected_category.lower()}/{selected_template}_template.yml"
                )

            # Erweiterte Debug-Informationen
            st.markdown("### 🔍 Debug-Informationen")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Template-Pfad:**\n`{template_path}`")
                st.info(f"**Template existiert:** {template_path.exists()}")
            with col2:
                st.info(f"**Kategorie:** {selected_category}")
                st.info(f"**Template:** {selected_template}")

            # Verzeichnis-Inhalt anzeigen
            if selected_category == "Node-RED":
                template_dir = Path("src_orbis/omf/config/message_templates/templates/node_red")
            else:
                template_dir = Path(f"src_orbis/omf/config/message_templates/templates/{selected_category.lower()}")
            if template_dir.exists():
                yaml_files = list(template_dir.glob("*.yml"))
                st.info(f"**Verzeichnis-Inhalt:** {len(yaml_files)} YAML-Dateien gefunden")
                with st.expander("📁 Alle YAML-Dateien im Verzeichnis", expanded=False):
                    for yaml_file in yaml_files:
                        st.markdown(f"- `{yaml_file.name}`")

            if template_path.exists():
                with open(template_path, encoding="utf-8") as f:
                    template_data = yaml.safe_load(f)

                template = template_data.get("template", {})

                # Template-Übersicht
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Template Name", template.get("name", "N/A"))
                with col2:
                    st.metric(
                        "Required Fields",
                        len(template.get("structure", {}).get("required_fields", [])),
                    )
                with col3:
                    st.metric("Validation Rules", len(template.get("validation_rules", [])))

                # Template-Details
                with st.expander("📋 Template Details", expanded=True):
                    st.markdown(f"**Beschreibung:** {template.get('description', 'N/A')}")
                    st.markdown(f"**Semantischer Zweck:** {template.get('semantic_purpose', 'N/A')}")

                    # MQTT Integration
                    mqtt_info = template.get("mqtt", {})
                    st.markdown("**MQTT Integration:**")
                    st.markdown(f"- Topic Pattern: `{mqtt_info.get('topic_pattern', 'N/A')}`")
                    st.markdown(f"- Direction: {mqtt_info.get('direction', 'N/A')}")
                    st.markdown(f"- QoS: {mqtt_info.get('qos', 'N/A')}")

                # Structure Details
                with st.expander("🔧 Structure Definition", expanded=False):
                    structure = template.get("structure", {})

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Required Fields:**")
                        required_fields = structure.get("required_fields", [])
                        for field in required_fields:
                            st.markdown(f"- `{field}`")

                    with col2:
                        st.markdown("**Optional Fields:**")
                        optional_fields = structure.get("optional_fields", [])
                        for field in optional_fields:
                            st.markdown(f"- `{field}`")

                    # Field Definitions
                    st.markdown("**Field Definitions:**")
                    field_defs = structure.get("field_definitions", {})
                    for field_name, field_info in field_defs.items():
                        with st.expander(f"`{field_name}`", expanded=False):
                            st.markdown(f"- **Type:** {field_info.get('type', 'N/A')}")
                            st.markdown(f"- **Pattern:** {field_info.get('pattern', 'N/A')}")
                            st.markdown(f"- **Description:** {field_info.get('description', 'N/A')}")
                            st.markdown(f"- **Validation:** {field_info.get('validation', 'N/A')}")

                # Validation Rules
                with st.expander("✅ Validation Rules", expanded=False):
                    validation_rules = template.get("validation_rules", [])
                    for i, rule in enumerate(validation_rules, 1):
                        st.markdown(f"{i}. {rule}")

                # Variable Fields
                with st.expander("🎯 Variable Fields", expanded=False):
                    variable_fields = template.get("variable_fields", {})
                    for field_name, field_info in variable_fields.items():
                        with st.expander(f"`{field_name}`", expanded=False):
                            st.markdown(f"- **Type:** {field_info.get('type', 'N/A')}")
                            st.markdown(f"- **Description:** {field_info.get('description', 'N/A')}")

                            values = field_info.get("values", [])
                            if values:
                                st.markdown(f"- **Values:** {len(values)} verfügbar")
                                if len(values) <= 10:
                                    st.markdown(f"  - {', '.join(values)}")
                                else:
                                    st.markdown(f"  - {', '.join(values[:5])}... ({len(values)} total)")

                # Usage Examples
                with st.expander("📦 Usage Examples", expanded=False):
                    usage_examples = template.get("usage_examples", [])
                    if usage_examples:
                        st.markdown(f"**{len(usage_examples)} Beispiele verfügbar:**")

                        # Tabs für mehrere Beispiele
                        if len(usage_examples) > 1:
                            tab_names = [f"Beispiel {i + 1}" for i in range(len(usage_examples))]
                            tabs = st.tabs(tab_names)

                            for _i, (tab, example) in enumerate(zip(tabs, usage_examples)):
                                with tab:
                                    st.markdown(f"**{example.get('description', 'N/A')}**")
                                    st.markdown(f"**Topic:** `{example.get('topic', 'N/A')}`")
                                    st.markdown("**Payload:**")
                                    st.json(example.get("payload", {}))
                        else:
                            # Ein Beispiel
                            example = usage_examples[0]
                            st.markdown(f"**{example.get('description', 'N/A')}**")
                            st.markdown(f"**Topic:** `{example.get('topic', 'N/A')}`")
                            st.markdown("**Payload:**")
                            st.json(example.get("payload", {}))
                    else:
                        st.info("Keine Usage Examples verfügbar")

            else:
                st.error(f"❌ Template {selected_template} nicht gefunden!")

        except Exception as e:
            st.error(f"❌ Fehler beim Laden des Templates: {e}")
