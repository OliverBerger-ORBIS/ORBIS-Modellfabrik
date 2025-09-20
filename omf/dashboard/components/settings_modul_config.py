"""
OMF Dashboard Settings - Modul-Konfiguration
Exakte Kopie der show_module_config() Funktion aus settings.py
"""

from pathlib import Path
import streamlit as st

from omf.config.omf_config import config
from omf.dashboard.utils.ui_refresh import request_refresh
from omf.tools.module_manager import get_omf_module_manager

# Add omf to path for imports


def show_module_config():
    """Zeigt Modul-Konfiguration - Exakte Kopie aus settings.py"""
    st.subheader("🏭 Modul-Konfiguration")

    # OMF Module Manager verwenden
    try:
        module_manager = get_omf_module_manager()
        all_modules = module_manager.get_all_modules()

        # Einfache Tabellen-Darstellung
        module_data = []
        for module_id, module_info in all_modules.items():
            icon = module_info.get("icon", "🏭")
            short_name = module_info.get("name", module_id)  # Kurzname wie HBW, FTS, etc.
            name_de = module_info.get("name_lang_de", module_info.get("name", module_id))
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
                    "Modul": st.column_config.TextColumn("Modul", width="medium"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "ID": st.column_config.TextColumn("ID", width="medium"),
                    "Typ": st.column_config.TextColumn("Typ", width="medium"),
                    "IP Range": st.column_config.TextColumn("IP Range", width="medium"),
                    "Aktiviert": st.column_config.TextColumn("Status", width="small"),
                },
                hide_index=True,
            )

        # Einzelne Module bearbeiten
        st.markdown("---")
        st.markdown("#### 📝 Module bearbeiten")

        selected_module = st.selectbox(
            "🏭 Modul auswählen",
            options=list(all_modules.keys()),
            format_func=lambda x: (f"{all_modules[x].get('name_lang_de', all_modules[x].get('name', x))} " f"({x})"),
        )

        if selected_module:
            module_info = all_modules[selected_module]
            icon = module_info.get("icon", "🏭")
            name_de = module_info.get("name_lang_de", module_info.get("name", selected_module))

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
                    module_manager.update_module(selected_module, {"enabled": enabled})
                    st.success(f"✅ {name_de} aktualisiert!")

        # Reload Button
        if st.button("🔄 Konfiguration neu laden"):
            if module_manager.reload_config():
                st.success("✅ Konfiguration neu geladen!")
                request_refresh()
            else:
                st.error("❌ Fehler beim Neuladen!")

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Modul-Konfiguration: {e}")
        st.info("📋 Verwende Fallback-Konfiguration...")

        # Fallback zur alten Konfiguration
        modules = config.get("modules", {})

        for module_id, module_config in modules.items():
            with st.expander(f"🏭 {module_config.get('name', module_id.upper())}"):
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
