"""
Workpiece Subtab Component
Provides workpiece configuration interface
"""

import streamlit as st
import logging
from omf2.common.i18n import translate, get_current_language


def show_workpiece_subtab(logger: logging.Logger):
    """
    Zeigt den Workpiece Subtab
    
    Args:
        logger: Logger instance für diese Komponente
    """
    logger.info("Workpiece Subtab geöffnet")
    
    current_lang = get_current_language()
    
    st.subheader(f"🔧 {translate('workpiece_config', current_lang)}")
    
    # Workpiece-Konfiguration Interface
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Werkstück-Typen")
        
        workpiece_types = [
            "Typ A - Standard",
            "Typ B - Erweitert", 
            "Typ C - Spezial"
        ]
        
        selected_type = st.selectbox(
            "Werkstück-Typ wählen:",
            workpiece_types
        )
        
        st.write("### Eigenschaften")
        dimensions = st.text_input("Abmessungen (mm)", value="100x50x25")
        weight = st.number_input("Gewicht (g)", min_value=0, max_value=5000, value=250)
        material = st.selectbox("Material", ["Aluminium", "Stahl", "Kunststoff"])
        
    with col2:
        st.write("### Konfiguration")
        
        # Workpiece-spezifische Einstellungen
        processing_time = st.slider("Bearbeitungszeit (s)", 10, 300, 60)
        quality_check = st.checkbox("Qualitätsprüfung", value=True)
        priority = st.selectbox("Priorität", ["Niedrig", "Normal", "Hoch"])
        
        st.write("### Status")
        st.info(f"🔧 Ausgewählter Typ: {selected_type}")
        st.info(f"⚖️ Gewicht: {weight}g")
        st.info(f"📏 Abmessungen: {dimensions}")
        
    # Aktionen
    st.write("### Aktionen")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔧 Konfiguration speichern"):
            logger.info(f"Workpiece-Konfiguration gespeichert: {selected_type}")
            st.success("✅ Konfiguration gespeichert!")
            
    with col2:
        if st.button("🔄 Zurücksetzen"):
            logger.info("Workpiece-Konfiguration zurückgesetzt")
            st.warning("⚠️ Konfiguration zurückgesetzt")
            
    with col3:
        if st.button("📋 Vorlage laden"):
            logger.info("Workpiece-Vorlage geladen")
            st.info("📋 Standard-Vorlage geladen")
    
    # Registry-basierte Informationen (Placeholder)
    with st.expander("🗄️ Registry-Information"):
        st.write("**Verfügbare Werkstück-Templates:**")
        st.code("""
registry/model/v1/entities/workpieces.yml:
- workpiece_type: "standard_a"
  dimensions: "100x50x25"
  weight: 250
  material: "aluminium"
  processing_steps: ["drill", "mill", "inspect"]
        """)
        
        st.write("**Template-Validierung:**")
        st.success("✅ Alle Felder gültig")
        st.info("💡 Registry-Integration wird über omf2/registry/model/v1/ verwaltet")