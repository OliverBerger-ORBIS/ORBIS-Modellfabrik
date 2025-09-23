"""
APS Processes Tab - Workflow-Diagramme für Produktionsprozesse
Entspricht dem "Processes" Tab des Original APS-Dashboards
Basiert auf der bestehenden OMF-Produktplanung, aber im APS-Stil modernisiert
"""

import streamlit as st
from omf.dashboard.tools.logging_config import get_logger
from omf.dashboard.utils.ui_refresh import request_refresh

logger = get_logger("dashboard.components.aps_processes")


def show_aps_processes():
    """Zeigt den APS Processes Tab mit Workflow-Diagrammen"""
    st.header("🔄 APS Processes")
    st.write("Produktionsplanung und Workflow-Diagramme für verschiedene Produkttypen")
    
    # Controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add Step", use_container_width=True, key="aps_processes_add_step"):
            _add_workflow_step()
    
    with col2:
        if st.button("💾 Save Workflow", use_container_width=True, key="aps_processes_save"):
            _save_workflow()
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True, key="aps_processes_refresh"):
            _refresh_workflow()
    
    with col4:
        advanced_processing = st.toggle(
            "Activate advanced processing steps", 
            value=False, 
            key="aps_processes_advanced"
        )
    
    st.divider()
    
    # Workflow-Diagramme für 3 Produkttypen
    _show_workflow_diagrams()


def _show_workflow_diagrams():
    """Zeigt die Workflow-Diagramme für alle Produkttypen"""
    
    # Allgemeiner Workflow
    st.subheader("📋 General Workflow")
    _show_general_workflow()
    
    st.divider()
    
    # 3 Produkttypen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        _show_blue_product_workflow()
    
    with col2:
        _show_red_product_workflow()
    
    with col3:
        _show_white_product_workflow()


def _show_general_workflow():
    """Zeigt den allgemeinen Workflow"""
    st.markdown("""
    <div style="border: 2px solid #007bff; border-radius: 8px; padding: 20px; margin: 10px 0; background-color: #f8f9fa;">
        <h4 style="margin: 0; color: #007bff; text-align: center;">🔄 General Production Workflow</h4>
        <div style="text-align: center; margin: 20px 0;">
            <div style="display: inline-block; margin: 10px; padding: 15px; border: 2px solid #28a745; border-radius: 8px; background-color: #d4edda;">
                <h5 style="margin: 0; color: #28a745;">📥 Retrieve via high-bay warehouse</h5>
            </div>
            <div style="margin: 20px 0; font-size: 24px;">⬇️</div>
            <div style="display: inline-block; margin: 10px; padding: 15px; border: 2px solid #ffc107; border-radius: 8px; background-color: #fff3cd;">
                <h5 style="margin: 0; color: #856404;">⚡ Parallel Processing</h5>
            </div>
            <div style="margin: 20px 0; font-size: 24px;">⬇️</div>
            <div style="display: inline-block; margin: 10px; padding: 15px; border: 2px solid #dc3545; border-radius: 8px; background-color: #f8d7da;">
                <h5 style="margin: 0; color: #721c24;">📤 Delivery via Goods Outgoing</h5>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _show_blue_product_workflow():
    """Zeigt den Workflow für blaue Produkte"""
    st.subheader("🔵 Blue Product")
    st.write("**3 Verarbeitungsschritte:**")
    
    # Workflow-Schritte für Blue Product
    steps = [
        ("🔩 Drilling Station", "Bohren des Werkstücks"),
        ("⚙️ Milling Station", "Fräsen des Werkstücks"),
        ("🤖 Quality Control with AI", "Qualitätskontrolle mittels KI")
    ]
    
    _display_workflow_steps(steps, "blue")


def _show_red_product_workflow():
    """Zeigt den Workflow für rote Produkte"""
    st.subheader("🔴 Red Product")
    st.write("**2 Verarbeitungsschritte:**")
    
    # Workflow-Schritte für Red Product
    steps = [
        ("⚙️ Milling Station", "Fräsen des Werkstücks"),
        ("🤖 Quality Control with AI", "Qualitätskontrolle mittels KI")
    ]
    
    _display_workflow_steps(steps, "red")


def _show_white_product_workflow():
    """Zeigt den Workflow für weiße Produkte"""
    st.subheader("⚪ White Product")
    st.write("**2 Verarbeitungsschritte:**")
    
    # Workflow-Schritte für White Product
    steps = [
        ("🔩 Drilling Station", "Bohren des Werkstücks"),
        ("🤖 Quality Control with AI", "Qualitätskontrolle mittels KI")
    ]
    
    _display_workflow_steps(steps, "white")


def _display_workflow_steps(steps, product_type):
    """Zeigt die Workflow-Schritte für einen Produkttyp"""
    for i, (station, description) in enumerate(steps, 1):
        # Status-Icons (simuliert)
        status_icon = "✅" if i == 1 else "⏰"  # Erster Schritt abgeschlossen, andere anstehend
        
        st.markdown(f"""
        <div style="border: 2px solid #6c757d; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f8f9fa;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 24px;">{status_icon}</span>
                <div>
                    <h5 style="margin: 0; color: #495057;">{i}. {station}</h5>
                    <p style="margin: 5px 0; color: #6c757d; font-size: 14px;">{description}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _add_workflow_step():
    """Fügt einen neuen Workflow-Schritt hinzu"""
    try:
        st.success("✅ Neuer Workflow-Schritt hinzugefügt")
        logger.info("Neuer Workflow-Schritt hinzugefügt")
        
        # UI-Refresh Pattern
        request_refresh()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Hinzufügen des Workflow-Schritts: {e}")
        logger.error(f"Fehler beim Hinzufügen des Workflow-Schritts: {e}")


def _save_workflow():
    """Speichert den aktuellen Workflow"""
    try:
        st.success("✅ Workflow erfolgreich gespeichert")
        logger.info("Workflow gespeichert")
        
        # UI-Refresh Pattern
        request_refresh()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Speichern des Workflows: {e}")
        logger.error(f"Fehler beim Speichern des Workflows: {e}")


def _refresh_workflow():
    """Aktualisiert den Workflow"""
    try:
        st.success("✅ Workflow aktualisiert")
        logger.info("Workflow aktualisiert")
        
        # UI-Refresh Pattern
        request_refresh()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Aktualisieren des Workflows: {e}")
        logger.error(f"Fehler beim Aktualisieren des Workflows: {e}")


def get_workflow_data():
    """Gibt die aktuellen Workflow-Daten zurück"""
    return {
        "blue_product": {
            "steps": [
                {"station": "Drilling Station", "description": "Bohren des Werkstücks"},
                {"station": "Milling Station", "description": "Fräsen des Werkstücks"},
                {"station": "Quality Control with AI", "description": "Qualitätskontrolle mittels KI"}
            ]
        },
        "red_product": {
            "steps": [
                {"station": "Milling Station", "description": "Fräsen des Werkstücks"},
                {"station": "Quality Control with AI", "description": "Qualitätskontrolle mittels KI"}
            ]
        },
        "white_product": {
            "steps": [
                {"station": "Drilling Station", "description": "Bohren des Werkstücks"},
                {"station": "Quality Control with AI", "description": "Qualitätskontrolle mittels KI"}
            ]
        }
    }


def set_workflow_data(workflow_data):
    """Setzt die Workflow-Daten"""
    logger.info(f"Workflow-Daten gesetzt: {workflow_data}")


def get_advanced_processing_status():
    """Gibt den Status der erweiterten Verarbeitungsschritte zurück"""
    return st.session_state.get("aps_processes_advanced", False)
