"""
OMF Dashboard Settings Komponenten
"""

import os
import sys

import streamlit as st

# Add src_orbis to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from omf.config.omf_config import config
from omf.tools.module_manager import get_omf_module_manager
from omf.tools.nfc_manager import get_omf_nfc_manager


def show_dashboard_settings():
    """Zeigt Dashboard-Einstellungen"""
    st.subheader("⚙️ Dashboard-Einstellungen")

    col1, col2 = st.columns(2)

    with col1:
        # Sprache
        language = st.selectbox(
            "🌐 Sprache / Language",
            options=["de", "en"],
            index=0 if config.get("dashboard.language") == "de" else 1,
            format_func=lambda x: "Deutsch" if x == "de" else "English",
        )

        # Theme
        theme = st.selectbox(
            "🎨 Theme",
            options=["light", "dark"],
            index=0 if config.get("dashboard.theme") == "light" else 1,
        )

    with col2:
        # Auto Refresh
        auto_refresh = st.checkbox(
            "🔄 Auto Refresh", value=config.get("dashboard.auto_refresh", True)
        )

        # Refresh Interval
        if auto_refresh:
            refresh_interval = st.slider(
                "⏱️ Refresh Interval (Sekunden)",
                min_value=1,
                max_value=60,
                value=config.get("dashboard.refresh_interval", 5),
            )
        else:
            refresh_interval = config.get("dashboard.refresh_interval", 5)

    # Speichern Button
    if st.button("💾 Einstellungen speichern"):
        config.set("dashboard.language", language)
        config.set("dashboard.theme", theme)
        config.set("dashboard.auto_refresh", auto_refresh)
        config.set("dashboard.refresh_interval", refresh_interval)

        if config.save_config():
            st.success("✅ Einstellungen gespeichert!")
        else:
            st.error("❌ Fehler beim Speichern!")


def show_module_config():
    """Zeigt Modul-Konfiguration"""
    st.subheader("🏭 Modul-Konfiguration")

    # OMF Module Manager verwenden
    try:
        module_manager = get_omf_module_manager()
        all_modules = module_manager.get_all_modules()

        # Einfache Tabellen-Darstellung
        module_data = []
        for module_id, module_info in all_modules.items():
            icon = module_info.get("icon", "🏭")
            short_name = module_info.get(
                "name", module_id
            )  # Kurzname wie HBW, FTS, etc.
            name_de = module_info.get(
                "name_lang_de", module_info.get("name", module_id)
            )
            module_type = module_info.get("type", "Unknown")
            ip_range = module_info.get("ip_range", "Unknown")
            enabled = module_info.get("enabled", True)

            module_data.append(
                {
                    "Modul": f"{icon} {short_name}",
                    "Name": name_de,
                    "ID": module_id,
                    "Typ": module_type,
                    "IP Range": ip_range,
                    "Aktiviert": "✅" if enabled else "❌",
                }
            )

        # Tabelle anzeigen
        if module_data:
            st.dataframe(
                module_data,
                column_config={
                    "Modul": st.column_config.TextColumn(
                        "Modul", width="medium"
                    ),
                    "Name": st.column_config.TextColumn(
                        "Name", width="medium"
                    ),
                    "ID": st.column_config.TextColumn("ID", width="medium"),
                    "Typ": st.column_config.TextColumn("Typ", width="medium"),
                    "IP Range": st.column_config.TextColumn(
                        "IP Range", width="medium"
                    ),
                    "Aktiviert": st.column_config.TextColumn(
                        "Status", width="small"
                    ),
                },
                hide_index=True,
            )

        # Einzelne Module bearbeiten
        st.markdown("---")
        st.markdown("#### 📝 Module bearbeiten")

        selected_module = st.selectbox(
            "🏭 Modul auswählen",
            options=list(all_modules.keys()),
            format_func=lambda x: (
                f"{all_modules[x].get('name_lang_de', all_modules[x].get('name', x))} "
                f"({x})"
            ),
        )

        if selected_module:
            module_info = all_modules[selected_module]
            icon = module_info.get("icon", "🏭")
            name_de = module_info.get(
                "name_lang_de", module_info.get("name", selected_module)
            )

            st.markdown(f"**{icon} {name_de}**")

            col1, col2 = st.columns(2)

            with col1:
                enabled = st.checkbox(
                    "✅ Aktiviert",
                    value=module_info.get("enabled", True),
                    key=f"module_{selected_module}_enabled",
                )

            with col2:
                if st.button("💾 Änderungen speichern"):
                    module_manager.update_module(
                        selected_module, {"enabled": enabled}
                    )
                    st.success(f"✅ {name_de} aktualisiert!")

        # Reload Button
        if st.button("🔄 Konfiguration neu laden"):
            if module_manager.reload_config():
                st.success("✅ Konfiguration neu geladen!")
                st.rerun()
            else:
                st.error("❌ Fehler beim Neuladen!")

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Modul-Konfiguration: {e}")
        st.info("📋 Verwende Fallback-Konfiguration...")

        # Fallback zur alten Konfiguration
        modules = config.get("modules", {})

        for module_id, module_config in modules.items():
            with st.expander(
                f"🏭 {module_config.get('name', module_id.upper())}"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    enabled = st.checkbox(
                        "✅ Aktiviert",
                        value=module_config.get("enabled", True),
                        key=f"module_{module_id}_enabled",
                    )

                with col2:
                    name = st.text_input(
                        "📝 Name",
                        value=module_config.get("name", module_id.upper()),
                        key=f"module_{module_id}_name",
                    )

                # Konfiguration aktualisieren
                modules[module_id] = {"name": name, "enabled": enabled}

        # Speichern Button
        if st.button("💾 Modul-Konfiguration speichern"):
            config.set("modules", modules)
            if config.save_config():
                st.success("✅ Modul-Konfiguration gespeichert!")
            else:
                st.error("❌ Fehler beim Speichern!")


def show_nfc_config():
    """Zeigt NFC-Konfiguration"""
    st.subheader("📱 NFC-Konfiguration")

    # OMF NFC Manager verwenden
    try:
        nfc_manager = get_omf_nfc_manager()

        # ROTE Werkstücke
        red_codes = nfc_manager.get_nfc_codes_by_color("RED")
        with st.expander("🔴 Rote Werkstücke (8)", expanded=False):
            if red_codes:
                red_data = []
                for nfc_code, nfc_info in red_codes.items():
                    friendly_id = nfc_info.get("friendly_id", nfc_code)
                    quality_check = nfc_info.get("quality_check", "Unknown")
                    description = nfc_info.get("description", "No description")
                    enabled = nfc_info.get("enabled", True)

                    red_data.append(
                        {
                            "Werkstück": f"🔴 {friendly_id}",
                            "NFC Code": nfc_code[:12] + "...",
                            "Qualität": quality_check,
                            "Beschreibung": description,
                            "Status": "✅" if enabled else "❌",
                        }
                    )

                if red_data:
                    st.dataframe(
                        red_data,
                        column_config={
                            "Werkstück": st.column_config.TextColumn(
                                "Werkstück", width="medium"
                            ),
                            "NFC Code": st.column_config.TextColumn(
                                "NFC Code", width="medium"
                            ),
                            "Qualität": st.column_config.TextColumn(
                                "Qualität", width="small"
                            ),
                            "Beschreibung": st.column_config.TextColumn(
                                "Beschreibung", width="medium"
                            ),
                            "Status": st.column_config.TextColumn(
                                "Status", width="small"
                            ),
                        },
                        hide_index=True,
                    )

        # WEISSE Werkstücke
        white_codes = nfc_manager.get_nfc_codes_by_color("WHITE")
        with st.expander("⚪ Weiße Werkstücke (8)", expanded=False):
            if white_codes:
                white_data = []
                for nfc_code, nfc_info in white_codes.items():
                    friendly_id = nfc_info.get("friendly_id", nfc_code)
                    quality_check = nfc_info.get("quality_check", "Unknown")
                    description = nfc_info.get("description", "No description")
                    enabled = nfc_info.get("enabled", True)

                    white_data.append(
                        {
                            "Werkstück": f"⚪ {friendly_id}",
                            "NFC Code": nfc_code[:12] + "...",
                            "Qualität": quality_check,
                            "Beschreibung": description,
                            "Status": "✅" if enabled else "❌",
                        }
                    )

                if white_data:
                    st.dataframe(
                        white_data,
                        column_config={
                            "Werkstück": st.column_config.TextColumn(
                                "Werkstück", width="medium"
                            ),
                            "NFC Code": st.column_config.TextColumn(
                                "NFC Code", width="medium"
                            ),
                            "Qualität": st.column_config.TextColumn(
                                "Qualität", width="small"
                            ),
                            "Beschreibung": st.column_config.TextColumn(
                                "Beschreibung", width="medium"
                            ),
                            "Status": st.column_config.TextColumn(
                                "Status", width="small"
                            ),
                        },
                        hide_index=True,
                    )

        # BLAUE Werkstücke
        blue_codes = nfc_manager.get_nfc_codes_by_color("BLUE")
        with st.expander("🔵 Blaue Werkstücke (8)", expanded=False):
            if blue_codes:
                blue_data = []
                for nfc_code, nfc_info in blue_codes.items():
                    friendly_id = nfc_info.get("friendly_id", nfc_code)
                    quality_check = nfc_info.get("quality_check", "Unknown")
                    description = nfc_info.get("description", "No description")
                    enabled = nfc_info.get("enabled", True)

                    blue_data.append(
                        {
                            "Werkstück": f"🔵 {friendly_id}",
                            "NFC Code": nfc_code[:12] + "...",
                            "Qualität": quality_check,
                            "Beschreibung": description,
                            "Status": "✅" if enabled else "❌",
                        }
                    )

                if blue_data:
                    st.dataframe(
                        blue_data,
                        column_config={
                            "Werkstück": st.column_config.TextColumn(
                                "Werkstück", width="medium"
                            ),
                            "NFC Code": st.column_config.TextColumn(
                                "NFC Code", width="medium"
                            ),
                            "Qualität": st.column_config.TextColumn(
                                "Qualität", width="small"
                            ),
                            "Beschreibung": st.column_config.TextColumn(
                                "Beschreibung", width="medium"
                            ),
                            "Status": st.column_config.TextColumn(
                                "Status", width="small"
                            ),
                        },
                        hide_index=True,
                    )

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der NFC-Konfiguration: {e}")
        st.info("📋 NFC-Konfiguration konnte nicht geladen werden.")


def show_mqtt_config():
    """Zeigt die MQTT-Broker Konfiguration an"""
    st.markdown("### 🔗 MQTT-Broker Konfiguration")
    st.markdown("MQTT-Broker Einstellungen und Verbindungsverwaltung")

    try:
        import os
        import sys

        # Füge den tools-Pfad hinzu
        tools_path = os.path.join(os.path.dirname(__file__), "..", "..", "tools")
        if tools_path not in sys.path:
            sys.path.append(tools_path)

        from mqtt_client import get_omf_mqtt_client

        mqtt_client = get_omf_mqtt_client()

        # Connection Status
        col1, col2 = st.columns(2)
        with col1:
            if mqtt_client.is_connected():
                st.success("🔗 Verbunden")
                if st.button("🔌 Trennen", key="settings_mqtt_disconnect"):
                    mqtt_client.disconnect()
                    st.success("✅ Getrennt!")
                    st.rerun()
            else:
                st.error("❌ Nicht verbunden")
                if st.button("🔗 Verbinden", key="settings_mqtt_connect"):
                    if mqtt_client.connect():
                        st.success("✅ Verbunden!")
                    else:
                        st.error("❌ Verbindung fehlgeschlagen!")
                    st.rerun()

        with col2:
            # Statistiken
            stats = mqtt_client.get_statistics()
            st.metric(
                "📨 Nachrichten empfangen", 
                stats.get("messages_received", 0)
            )
            st.metric("📤 Nachrichten gesendet", stats.get("messages_sent", 0))

        st.markdown("---")

        # Broker Konfiguration
        st.markdown("#### 🌐 Broker Einstellungen")

        # Lade aktuelle Konfiguration
        config = mqtt_client.config
        broker_config = config.get("broker", {}).get("aps", {})

        col1, col2 = st.columns(2)
        with col1:
            host = st.text_input(
                "🌐 Host",
                value=broker_config.get("host", "192.168.178.100"),
                key="mqtt_host",
            )

            port = st.number_input(
                "🔌 Port",
                min_value=1,
                max_value=65535,
                value=broker_config.get("port", 1883),
                key="mqtt_port",
            )

            client_id = st.text_input(
                "🆔 Client ID",
                value=broker_config.get("client_id", "omf_dashboard"),
                key="mqtt_client_id",
            )

        with col2:
            username = st.text_input(
                "👤 Username",
                value=broker_config.get("username", ""),
                key="mqtt_username",
            )

            password = st.text_input(
                "🔒 Password",
                value=broker_config.get("password", ""),
                type="password",
                key="mqtt_password",
            )

            keepalive = st.number_input(
                "⏱️ Keepalive (Sekunden)",
                min_value=1,
                max_value=3600,
                value=broker_config.get("keepalive", 60),
                key="mqtt_keepalive",
            )

        # Speichern Button
        if st.button("💾 Broker-Konfiguration speichern"):
            # Update Konfiguration
            broker_config.update(
                {
                    "host": host,
                    "port": port,
                    "username": username,
                    "password": password,
                    "client_id": client_id,
                    "keepalive": keepalive,
                }
            )

            # Speichere Konfiguration
            try:
                import yaml

                config_path = os.path.join(
                    tools_path, "..", "config", "mqtt_config.yml"
                )
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        config, f, default_flow_style=False, allow_unicode=True
                    )
                st.success("✅ Broker-Konfiguration gespeichert!")
            except Exception as e:
                st.error(f"❌ Fehler beim Speichern: {e}")

        st.markdown("---")

        # Topic Subscriptions
        st.markdown("#### 📡 Topic Subscriptions")
        subscriptions = config.get("subscriptions", {})

        for category, topics in subscriptions.items():
            with st.expander(f"📡 {category.upper()}", expanded=False):
                for topic in topics:
                    st.code(topic)

    except ImportError:
        st.error("MQTT Client konnte nicht importiert werden.")
        st.info("MQTT-Konfiguration wird implementiert...")


def show_topic_config():
    """Zeigt die Topic-Konfiguration an"""
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
                category_topics = {
                    k: v for k, v in all_topics.items() if v.get("category") == category
                }
                if category_topics:
                    st.markdown(f"**{category} Topics ({len(category_topics)}):**")
                    for topic, info in list(category_topics.items())[
                        :3
                    ]:  # Zeige erste 3 pro Kategorie
                        st.markdown(f"  - **{topic}:**")
                        st.markdown(
                            f"    - Template: `{info.get('template', 'Kein Template')}`"
                        )
                        st.markdown(
                            f"    - Direction: `{info.get('template_direction', 'N/A')}`"
                        )
                        st.markdown(f"    - Category: `{info.get('category', 'N/A')}`")
                    st.markdown("---")

        # Modul Filter
        st.markdown("#### 🔍 Modul Filter")
        all_modules = list(
            topic_manager.get_statistics().get("module_counts", {}).keys()
        )
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
                        st.markdown(
                            f"**Topics ({len(filtered_topics)} von {len(category_topics)}):**"
                        )
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
                        templates_with_mapping = [
                            t for t in topic_data if t["Template"] != "Kein Template"
                        ]
                        templates_without_mapping = [
                            t for t in topic_data if t["Template"] == "Kein Template"
                        ]

                        # Debug: Zeige erste paar Topics mit Details
                        with st.expander("🔍 Debug: Topic-Details", expanded=False):
                            for topic in topic_data[:5]:  # Zeige erste 5
                                st.markdown(f"**{topic['Topic']}:**")
                                st.markdown(f"  - Template: `{topic['Template']}`")
                                st.markdown(f"  - Direction: `{topic['Direction']}`")
                                st.markdown(
                                    f"  - Category: `{topic.get('Sub-Kategorie', 'N/A')}`"
                                )
                                st.markdown("---")

                        # Zeige Template-Statistiken
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("✅ Mit Template", len(templates_with_mapping))
                        with col2:
                            st.metric("❌ Ohne Template", len(templates_without_mapping))

                        # Debug: Zeige alle Topics ohne Template
                        if templates_without_mapping:
                            with st.expander(
                                "⚠️ Topics ohne Template-Zuordnung", expanded=False
                            ):
                                st.markdown(
                                    f"**{len(templates_without_mapping)} Topics ohne Template:**"
                                )
                                for topic in templates_without_mapping:
                                    st.markdown(
                                        f"- **{topic['Topic']}** (Kategorie: {topic.get('Kategorie', 'N/A')})"
                                    )

                        st.dataframe(
                            topic_data,
                            column_config={
                                "Topic": st.column_config.TextColumn(
                                    "Topic", width="medium"
                                ),
                                "Friendly Name": st.column_config.TextColumn(
                                    "Friendly Name", width="medium"
                                ),
                                "Beschreibung": st.column_config.TextColumn(
                                    "Beschreibung", width="large"
                                ),
                                "Sub-Kategorie": st.column_config.TextColumn(
                                    "Sub-Kategorie", width="small"
                                ),
                                "Modul": st.column_config.TextColumn(
                                    "Modul", width="small"
                                ),
                                "Template": st.column_config.TextColumn(
                                    "Template", width="medium"
                                ),
                                "Direction": st.column_config.TextColumn(
                                    "Direction", width="small"
                                ),
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
                        st.markdown(
                            f"**Topics ({len(filtered_topics)} von {len(sub_cat_topics)}):**"
                        )
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
                                "Topic": st.column_config.TextColumn(
                                    "Topic", width="medium"
                                ),
                                "Friendly Name": st.column_config.TextColumn(
                                    "Friendly Name", width="medium"
                                ),
                                "Beschreibung": st.column_config.TextColumn(
                                    "Beschreibung", width="large"
                                ),
                                "Modul": st.column_config.TextColumn(
                                    "Modul", width="small"
                                ),
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
                st.markdown(
                    f"**Letzte Aktualisierung:** {metadata.get('last_updated', 'Unbekannt')}"
                )
                st.markdown(
                    f"**Beschreibung:** {metadata.get('description', 'Keine Beschreibung')}"
                )

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


def show_messages_templates():
    """Zeigt die Message Templates an"""
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
                template_dir = Path(
                    "src_orbis/omf/config/message_templates/templates/node_red"
                )
            else:
                template_dir = Path(
                    f"src_orbis/omf/config/message_templates/templates/{selected_category.lower()}"
                )
            if template_dir.exists():
                yaml_files = list(template_dir.glob("*.yml"))
                st.info(
                    f"**Verzeichnis-Inhalt:** {len(yaml_files)} YAML-Dateien gefunden"
                )
                with st.expander("📁 Alle YAML-Dateien im Verzeichnis", expanded=False):
                    for yaml_file in yaml_files:
                        st.markdown(f"- `{yaml_file.name}`")

            if template_path.exists():
                with open(template_path, "r", encoding="utf-8") as f:
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
                    st.metric(
                        "Validation Rules", len(template.get("validation_rules", []))
                    )

                # Template-Details
                with st.expander("📋 Template Details", expanded=True):
                    st.markdown(
                        f"**Beschreibung:** {template.get('description', 'N/A')}"
                    )
                    st.markdown(
                        f"**Semantischer Zweck:** {template.get('semantic_purpose', 'N/A')}"
                    )

                    # MQTT Integration
                    mqtt_info = template.get("mqtt", {})
                    st.markdown("**MQTT Integration:**")
                    st.markdown(
                        f"- Topic Pattern: `{mqtt_info.get('topic_pattern', 'N/A')}`"
                    )
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
                            st.markdown(
                                f"- **Pattern:** {field_info.get('pattern', 'N/A')}"
                            )
                            st.markdown(
                                f"- **Description:** {field_info.get('description', 'N/A')}"
                            )
                            st.markdown(
                                f"- **Validation:** {field_info.get('validation', 'N/A')}"
                            )

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
                            st.markdown(
                                f"- **Description:** {field_info.get('description', 'N/A')}"
                            )

                            values = field_info.get("values", [])
                            if values:
                                st.markdown(f"- **Values:** {len(values)} verfügbar")
                                if len(values) <= 10:
                                    st.markdown(f"  - {', '.join(values)}")
                                else:
                                    st.markdown(
                                        f"  - {', '.join(values[:5])}... ({len(values)} total)"
                                    )

                # Usage Examples
                with st.expander("📦 Usage Examples", expanded=False):
                    usage_examples = template.get("usage_examples", [])
                    if usage_examples:
                        st.markdown(f"**{len(usage_examples)} Beispiele verfügbar:**")

                        # Tabs für mehrere Beispiele
                        if len(usage_examples) > 1:
                            tab_names = [
                                f"Beispiel {i + 1}" for i in range(len(usage_examples))
                            ]
                            tabs = st.tabs(tab_names)

                            for i, (tab, example) in enumerate(
                                zip(tabs, usage_examples)
                            ):
                                with tab:
                                    st.markdown(
                                        f"**{example.get('description', 'N/A')}**"
                                    )
                                    st.markdown(
                                        f"**Topic:** `{example.get('topic', 'N/A')}`"
                                    )
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
