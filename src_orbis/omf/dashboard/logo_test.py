#!/usr/bin/env python3
"""
ORBIS Logo Test - Vergleich der verschiedenen ORBIS-Logos
Version: 3.0.0
"""

import os

import streamlit as st


def main():
    """Hauptfunktion für Logo-Test"""

    # Page config
    st.set_page_config(
        page_title="ORBIS Logo Test",
        page_icon="🏭",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.title("🎨 ORBIS Logo Test")
    st.markdown("Vergleich der verschiedenen ORBIS-Logos für das Dashboard")

    # Logo-Dateien (nicht verwendet, aber für Referenz behalten)
    # logo_files = [
    #     "orbis_logo.png",  # Aktuelles Logo
    #     "ORBIS_4C.png",  # Neues Logo 1
    #     "ORBIS_RGB_BIG.png",  # Neues Logo 2
    #     "ORBIS_Weiss.png",  # Neues Logo 3
    #     "ORBIS_WWW_4C.png",  # Neues Logo 4
    # ]

    # Assets-Verzeichnis
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")

    # Logo-Vergleich
    st.markdown("## 📊 Logo-Vergleich")

    # Erste Zeile: Aktuelles Logo vs neue Logos
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🏭 Aktuelles Logo")
        current_logo_path = os.path.join(assets_dir, "orbis_logo.png")
        if os.path.exists(current_logo_path):
            st.image(current_logo_path, width=200)
            st.markdown("**Datei:** `orbis_logo.png`")
            st.markdown("**Größe:** 6.9KB")
        else:
            st.error("Logo nicht gefunden!")

    with col2:
        st.markdown("### 🆕 Neues Logo 1")
        logo1_path = os.path.join(assets_dir, "ORBIS_4C.png")
        if os.path.exists(logo1_path):
            st.image(logo1_path, width=200)
            st.markdown("**Datei:** `ORBIS_4C.png`")
            st.markdown("**Größe:** 61KB")
        else:
            st.error("Logo nicht gefunden!")

    with col3:
        st.markdown("### 🆕 Neues Logo 2")
        logo2_path = os.path.join(assets_dir, "ORBIS_RGB_BIG.png")
        if os.path.exists(logo2_path):
            st.image(logo2_path, width=200)
            st.markdown("**Datei:** `ORBIS_RGB_BIG.png`")
            st.markdown("**Größe:** 18KB")
        else:
            st.error("Logo nicht gefunden!")

    # Zweite Zeile: Weitere neue Logos
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("### 🆕 Neues Logo 3")
        logo3_path = os.path.join(assets_dir, "ORBIS_Weiss.png")
        if os.path.exists(logo3_path):
            st.image(logo3_path, width=200)
            st.markdown("**Datei:** `ORBIS_Weiss.png`")
            st.markdown("**Größe:** 51KB")
        else:
            st.error("Logo nicht gefunden!")

    with col5:
        st.markdown("### 🆕 Neues Logo 4")
        logo4_path = os.path.join(assets_dir, "ORBIS_WWW_4C.png")
        if os.path.exists(logo4_path):
            st.image(logo4_path, width=200)
            st.markdown("**Datei:** `ORBIS_WWW_4C.png`")
            st.markdown("**Größe:** 20KB")
        else:
            st.error("Logo nicht gefunden!")

    with col6:
        st.markdown("### 🏭 Fallback (Emoji)")
        st.markdown("🏭")
        st.markdown("**Fallback:** Fabrik-Emoji")
        st.markdown("**Größe:** Minimal")

    # Dashboard-Simulation
    st.markdown("---")
    st.markdown("## 🖥️ Dashboard-Simulation")
    st.markdown("Wie würde das Logo im Dashboard aussehen?")

    # Logo-Auswahl für Simulation
    selected_logo = st.selectbox(
        "Logo für Dashboard-Simulation auswählen:",
        [
            "orbis_logo.png",
            "ORBIS_4C.png",
            "ORBIS_RGB_BIG.png",
            "ORBIS_Weiss.png",
            "ORBIS_WWW_4C.png",
            "Fallback (Emoji)",
        ],
        index=0,
    )

    # Dashboard-Header simulieren
    st.markdown("### 📊 Simulierter Dashboard-Header")

    col_logo, col_title, col_status = st.columns([1, 3, 1])

    with col_logo:
        if selected_logo == "Fallback (Emoji)":
            st.markdown("🏭")
            st.caption("ORBIS Modellfabrik")
        else:
            logo_path = os.path.join(assets_dir, selected_logo)
            if os.path.exists(logo_path):
                st.image(logo_path, width=100)
            else:
                st.markdown("🏭")
                st.caption("ORBIS Modellfabrik")

    with col_title:
        st.title("ORBIS Modellfabrik Dashboard")

    with col_status:
        st.success("🔗 MQTT Connected")

    # Bewertung
    st.markdown("---")
    st.markdown("## ⭐ Logo-Bewertung")

    col_quality, col_size, col_style = st.columns(3)

    with col_quality:
        st.markdown("### 🎨 Qualität")
        quality_scores = {
            "orbis_logo.png": 7,
            "ORBIS_4C.png": 9,
            "ORBIS_RGB_BIG.png": 8,
            "ORBIS_Weiss.png": 8,
            "ORBIS_WWW_4C.png": 8,
            "Fallback (Emoji)": 5,
        }

        for logo, score in quality_scores.items():
            st.markdown(f"**{logo}:** {'⭐' * score}")

    with col_size:
        st.markdown("### 📏 Dateigröße")
        size_info = {
            "orbis_logo.png": "6.9KB",
            "ORBIS_4C.png": "61KB",
            "ORBIS_RGB_BIG.png": "18KB",
            "ORBIS_Weiss.png": "51KB",
            "ORBIS_WWW_4C.png": "20KB",
            "Fallback (Emoji)": "Minimal",
        }

        for logo, size in size_info.items():
            st.markdown(f"**{logo}:** {size}")

    with col_style:
        st.markdown("### 🎯 Stil")
        style_comments = {
            "orbis_logo.png": "Einfach, klein",
            "ORBIS_4C.png": "Professionell, 4C",
            "ORBIS_RGB_BIG.png": "RGB, größer",
            "ORBIS_Weiss.png": "Weiß, elegant",
            "ORBIS_WWW_4C.png": "Web-optimiert",
            "Fallback (Emoji)": "Universal",
        }

        for logo, style in style_comments.items():
            st.markdown(f"**{logo}:** {style}")

    # Empfehlung
    st.markdown("---")
    st.markdown("## 💡 Empfehlung")

    st.info(
        """
    **Für das Dashboard empfehle ich:**

    🥇 **ORBIS_RGB_BIG.png** - Gute Qualität, moderate Größe, RGB-fähig
    🥈 **ORBIS_WWW_4C.png** - Web-optimiert, 4C, gute Größe
    🥉 **ORBIS_4C.png** - Höchste Qualität, aber größere Datei

    **Fallback:** Fabrik-Emoji 🏭 für maximale Kompatibilität
    """
    )

    # Code-Snippet für Integration
    st.markdown("---")
    st.markdown("## 🔧 Integration")

    st.code(
        """
# In omf_dashboard.py - Logo-Pfad ändern:
logo_path = os.path.join(
    os.path.dirname(__file__),
    "assets",
    "ORBIS_RGB_BIG.png"  # Ihr gewähltes Logo
)
    """,
        language="python",
    )


if __name__ == "__main__":
    main()
