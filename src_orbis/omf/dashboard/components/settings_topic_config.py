"""
OMF Dashboard Settings - Topic-Konfiguration
Exakte Kopie der show_topic_config() Funktion aus settings.py
"""

import os
import sys

import streamlit as st

# Add src_orbis to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def show_topic_config():
    """Zeigt die Topic-Konfiguration an - Exakte Kopie aus settings.py"""
    st.markdown("### 📡 Topic-Konfiguration")
    st.markdown("MQTT-Topic-Konfiguration und -Verwaltung")

    try:
        import os
        import sys

        # Füge den tools-Pfad hinzu
        tools_path = os.path.join(os.path.dirname(__file__), "..", "..", "tools")
        if tools_path not in sys.path:
            sys.path.append(tools_path)

        from topic_manager import get_omf_topic_manager

        topic_manager = get_omf_topic_manager()

        # Debug: Zeige Topic Manager Info
        all_topics = topic_manager.get_all_topics()
        st.info(f"🔍 Topic Manager geladen: {len(all_topics)} Topics verfügbar")

        # Debug: Zeige erste paar Topics mit Template-Info
        with st.expander("🔍 Debug: Topic Manager Details", expanded=False):
            # Zeige Topics nach Kategorie
            categories = ["CCU", "TXT", "MODULE", "Node-RED"]
            for category in categories:
                category_topics = {k: v for k, v in all_topics.items() if v.get("category") == category}
                if category_topics:
                    st.markdown(f"**{category} Topics ({len(category_topics)}):**")
                    for topic, info in list(category_topics.items())[:3]:  # Zeige erste 3 pro Kategorie
                        st.markdown(f"  - **{topic}:**")
                        st.markdown(f"    - Template: `{info.get('template', 'Kein Template')}`")
                        st.markdown(f"    - Direction: `{info.get('template_direction', 'N/A')}`")
                        st.markdown(f"    - Category: `{info.get('category', 'N/A')}`")
                    st.markdown("---")

        # Modul Filter
        st.markdown("#### 🔍 Modul Filter")
        all_modules = list(topic_manager.get_statistics().get("module_counts", {}).keys())
        selected_module = st.selectbox(
            "🔗 Modul filtern (nur für MODULE-Kategorie relevant)",
            options=["Alle"] + all_modules,
            index=0,
        )

        st.markdown("---")

        # Kategorien mit Expander
        categories = topic_manager.get_categories()
        for category_name, category_info in categories.items():
            icon = category_info.get("icon", "📋")
            description = category_info.get("description", "")

            with st.expander(f"{icon} {category_name}", expanded=False):
                st.markdown(f"**Beschreibung:** {description}")

                # Topics dieser Kategorie mit Filter
                category_topics = topic_manager.get_topics_by_category(category_name)
                if category_topics:
                    # Filter nur für MODULE-Kategorie anwenden
                    filtered_topics = {}
                    for topic, info in category_topics.items():
                        # Modul Filter nur für MODULE-Kategorie
                        if category_name == "MODULE" and selected_module != "Alle":
                            if info.get("module") != selected_module:
                                continue

                        filtered_topics[topic] = info

                    if filtered_topics:
                        st.markdown(f"**Topics ({len(filtered_topics)} von " f"{len(category_topics)}):**")
                        topic_data = []
                        for topic, info in filtered_topics.items():
                            friendly_name = info.get("friendly_name", topic)
                            description = info.get("description", "")
                            sub_category = info.get("sub_category", "")
                            module = info.get("module", "")

                            topic_data.append(
                                {
                                    "Topic": topic,
                                    "Friendly Name": friendly_name,
                                    "Beschreibung": description,
                                    "Sub-Kategorie": sub_category,
                                    "Modul": module,
                                    "Template": info.get("template", "Kein Template"),
                                    "Direction": info.get("template_direction", "N/A"),
                                }
                            )

                        # Debug: Zeige Template-Zuordnungen
                        templates_with_mapping = [t for t in topic_data if t["Template"] != "Kein Template"]
                        templates_without_mapping = [t for t in topic_data if t["Template"] == "Kein Template"]

                        # Debug: Zeige erste paar Topics mit Details
                        with st.expander("🔍 Debug: Topic-Details", expanded=False):
                            for topic in topic_data[:5]:  # Zeige erste 5
                                st.markdown(f"**{topic['Topic']}:**")
                                st.markdown(f"  - Template: `{topic['Template']}`")
                                st.markdown(f"  - Direction: `{topic['Direction']}`")
                                st.markdown(f"  - Category: `{topic.get('Sub-Kategorie', 'N/A')}`")
                                st.markdown("---")

                        # Zeige Template-Statistiken
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("✅ Mit Template", len(templates_with_mapping))
                        with col2:
                            st.metric("❌ Ohne Template", len(templates_without_mapping))

                        # Debug: Zeige alle Topics ohne Template
                        if templates_without_mapping:
                            with st.expander("⚠️ Topics ohne Template-Zuordnung", expanded=False):
                                st.markdown(f"**{len(templates_without_mapping)} Topics ohne Template:**")
                                for topic in templates_without_mapping:
                                    st.markdown(f"- **{topic['Topic']}** (Kategorie: {topic.get('Kategorie', 'N/A')})")

                        st.dataframe(
                            topic_data,
                            column_config={
                                "Topic": st.column_config.TextColumn("Topic", width="medium"),
                                "Friendly Name": st.column_config.TextColumn("Friendly Name", width="medium"),
                                "Beschreibung": st.column_config.TextColumn("Beschreibung", width="large"),
                                "Sub-Kategorie": st.column_config.TextColumn("Sub-Kategorie", width="small"),
                                "Modul": st.column_config.TextColumn("Modul", width="small"),
                                "Template": st.column_config.TextColumn("Template", width="medium"),
                                "Direction": st.column_config.TextColumn("Direction", width="small"),
                            },
                            hide_index=True,
                        )
                    else:
                        st.info("Keine Topics für die gewählten Filter gefunden.")
                else:
                    st.info("Keine Topics für diese Kategorie gefunden.")

        # Sub-Kategorien für Module
        st.markdown("---")
        st.markdown("#### 🔗 Modul Sub-Kategorien")
        sub_categories = topic_manager.get_module_sub_categories()
        for sub_cat_name, sub_cat_info in sub_categories.items():
            icon = sub_cat_info.get("icon", "📋")
            description = sub_cat_info.get("description", "")

            with st.expander(f"{icon} {sub_cat_name}", expanded=False):
                st.markdown(f"**Beschreibung:** {description}")

                # Topics dieser Sub-Kategorie mit Filter
                sub_cat_topics = topic_manager.get_topics_by_sub_category(sub_cat_name)
                if sub_cat_topics:
                    # Modul Filter anwenden (nur für MODULE-Kategorie relevant)
                    filtered_topics = {}
                    for topic, info in sub_cat_topics.items():
                        # Modul Filter nur für MODULE-Kategorie
                        if selected_module != "Alle":
                            if info.get("module") != selected_module:
                                continue

                        filtered_topics[topic] = info

                    if filtered_topics:
                        st.markdown(f"**Topics ({len(filtered_topics)} von {len(sub_cat_topics)}):**")
                        topic_data = []
                        for topic, info in filtered_topics.items():
                            friendly_name = info.get("friendly_name", topic)
                            description = info.get("description", "")
                            module = info.get("module", "")

                            topic_data.append(
                                {
                                    "Topic": topic,
                                    "Friendly Name": friendly_name,
                                    "Beschreibung": description,
                                    "Modul": module,
                                }
                            )

                        st.dataframe(
                            topic_data,
                            column_config={
                                "Topic": st.column_config.TextColumn("Topic", width="medium"),
                                "Friendly Name": st.column_config.TextColumn("Friendly Name", width="medium"),
                                "Beschreibung": st.column_config.TextColumn("Beschreibung", width="large"),
                                "Modul": st.column_config.TextColumn("Modul", width="small"),
                            },
                            hide_index=True,
                        )
                    else:
                        st.info("Keine Topics für die gewählten Filter gefunden.")
                else:
                    st.info("Keine Topics für diese Sub-Kategorie gefunden.")

        # Metadata
        st.markdown("---")
        metadata = topic_manager.get_metadata()
        if metadata:
            st.markdown("#### 📋 Konfigurations-Metadaten")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Version:** {metadata.get('version', 'Unbekannt')}")
                st.markdown(f"**Autor:** {metadata.get('author', 'Unbekannt')}")
            with col2:
                st.markdown(f"**Letzte Aktualisierung:** {metadata.get('last_updated', 'Unbekannt')}")
                st.markdown(f"**Beschreibung:** {metadata.get('description', 'Keine Beschreibung')}")

    except ImportError:
        st.error("Topic Manager konnte nicht importiert werden.")
        st.info("Topic-Konfiguration wird implementiert...")

        # Fallback: Beispiel-Topics
        st.markdown("#### Beispiel-Topics:")
        example_topics = [
            "ccu/state",
            "module/v1/ff/SVR3QA2098/state",
            "fts/v1/ff/5iO4/connection",
        ]

        for topic in example_topics:
            st.code(topic)
