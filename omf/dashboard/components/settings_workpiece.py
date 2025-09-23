"""
OMF Dashboard Settings - Werkstück-Konfiguration
Registry-basierte Werkstück-Verwaltung
"""

import streamlit as st

from omf.tools.workpiece_manager import get_omf_workpiece_manager

# Add omf to path for imports


def show_workpiece_config():
    """Zeigt Werkstück-Konfiguration aus Registry"""
    st.subheader("🔧 Werkstück-Konfiguration")

    # OMF Workpiece Manager verwenden
    try:
        workpiece_manager = get_omf_workpiece_manager()

        # ROTE Werkstücke
        red_codes = workpiece_manager.get_workpieces_by_color("RED")
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
                            "Werkstück": st.column_config.TextColumn("Werkstück", width="medium"),
                            "NFC Code": st.column_config.TextColumn("NFC Code", width="medium"),
                            "Qualität": st.column_config.TextColumn("Qualität", width="small"),
                            "Beschreibung": st.column_config.TextColumn("Beschreibung", width="medium"),
                            "Status": st.column_config.TextColumn("Status", width="small"),
                        },
                        hide_index=True,
                    )

        # WEISSE Werkstücke
        white_codes = workpiece_manager.get_workpieces_by_color("WHITE")
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
                            "Werkstück": st.column_config.TextColumn("Werkstück", width="medium"),
                            "NFC Code": st.column_config.TextColumn("NFC Code", width="medium"),
                            "Qualität": st.column_config.TextColumn("Qualität", width="small"),
                            "Beschreibung": st.column_config.TextColumn("Beschreibung", width="medium"),
                            "Status": st.column_config.TextColumn("Status", width="small"),
                        },
                        hide_index=True,
                    )

        # BLAUE Werkstücke
        blue_codes = workpiece_manager.get_workpieces_by_color("BLUE")
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
                            "Werkstück": st.column_config.TextColumn("Werkstück", width="medium"),
                            "NFC Code": st.column_config.TextColumn("NFC Code", width="medium"),
                            "Qualität": st.column_config.TextColumn("Qualität", width="small"),
                            "Beschreibung": st.column_config.TextColumn("Beschreibung", width="medium"),
                            "Status": st.column_config.TextColumn("Status", width="small"),
                        },
                        hide_index=True,
                    )

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Werkstück-Konfiguration: {e}")
        st.info("📋 Werkstück-Konfiguration konnte nicht geladen werden.")
