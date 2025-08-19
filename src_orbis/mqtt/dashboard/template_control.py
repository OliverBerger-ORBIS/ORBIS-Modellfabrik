#!/usr/bin/env python3
"""
Dashboard Integration für Template Message Control
Streamlit Widgets für Wareneingang und Order Tracking
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, Any

from ..tools.template_message_manager import TemplateMessageManager, format_order_display


class TemplateControlDashboard:
    """Dashboard Widgets für Template Message Control"""
    
    def __init__(self, template_manager: TemplateMessageManager):
        self.template_manager = template_manager
    
    def show_wareneingang_control(self):
        """Zeigt das Wareneingang Control Panel"""
        st.subheader("🏭 Wareneingang Control")
        
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                # Farb-Auswahl
                color = st.selectbox(
                    "Werkstück-Farbe:",
                    ["RED", "WHITE", "BLUE"],
                    help="Wähle die Farbe des Werkstücks"
                )
                
                # Werkstück-ID (NFC oder manuell)
                workpiece_id = st.text_input(
                    "Werkstück-ID (NFC):",
                    value="04798eca341290",
                    help="NFC-gelesene Werkstück-ID oder manuell eingegeben"
                )
                
                # Trigger Button
                if st.button("🚀 Wareneingang starten", type="primary"):
                    if workpiece_id and len(workpiece_id) >= 10:
                        success = self.template_manager.send_wareneingang_trigger(color, workpiece_id)
                        if success:
                            st.success(f"✅ Wareneingang für {color} Werkstück gestartet!")
                            st.info(f"📊 Order Tracking gestartet für {workpiece_id}")
                        else:
                            st.error("❌ Fehler beim Starten des Wareneingangs")
                    else:
                        st.error("❌ Bitte gültige Werkstück-ID eingeben (mindestens 10 Zeichen)")
            
            with col2:
                # Template Info
                template_info = self.template_manager.get_template_info("wareneingang_trigger")
                if template_info:
                    st.info("📋 Template Info:")
                    st.write(f"**Topic:** `{template_info['topic']}`")
                    st.write(f"**Parameter:** {list(template_info['parameters'].keys())}")
                    
                    # Parameter Details
                    with st.expander("🔍 Parameter Details"):
                        for param, details in template_info['parameters'].items():
                            if isinstance(details, list):
                                st.write(f"**{param}:** {', '.join(details)}")
                            else:
                                st.write(f"**{param}:** {details}")
    
    def show_order_tracking(self):
        """Zeigt das Order Tracking Dashboard"""
        st.subheader("📊 Order Tracking")
        
        # Statistiken
        stats = self.template_manager.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Aktive Orders", stats["active_orders"])
        with col2:
            st.metric("Abgeschlossen", stats["completed_orders"])
        with col3:
            st.metric("Fehler", stats["error_orders"])
        with col4:
            st.metric("Gesamt", stats["total_orders"])
        
        # Farb-Verteilung
        if stats["color_distribution"]:
            st.write("🎨 Farb-Verteilung:")
            for color, count in stats["color_distribution"].items():
                st.write(f"  {color}: {count} Orders")
        
        # Aktive Orders
        active_orders = self.template_manager.get_active_orders()
        if active_orders:
            st.write("🔄 **Aktive Orders:**")
            
            for order_id, order_info in active_orders.items():
                with st.expander(format_order_display(order_info)):
                    self._show_order_details(order_info)
        else:
            st.info("📭 Keine aktiven Orders")
        
        # Order Historie
        order_history = self.template_manager.get_order_history()
        if order_history:
            st.write("📚 **Order Historie:**")
            
            # Filter nach Status
            status_filter = st.selectbox(
                "Status Filter:",
                ["Alle", "COMPLETED", "ERROR"],
                key="history_filter"
            )
            
            filtered_history = order_history
            if status_filter != "Alle":
                filtered_history = [order for order in order_history if order.get("status") == status_filter]
            
            for order_info in filtered_history[-10:]:  # Letzte 10 Orders
                with st.expander(format_order_display(order_info)):
                    self._show_order_details(order_info)
        else:
            st.info("📭 Keine Order-Historie verfügbar")
    
    def _show_order_details(self, order_info: Dict[str, Any]):
        """Zeigt Details einer Order"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Grunddaten:**")
            st.write(f"**Werkstück-ID:** {order_info.get('workpieceId', 'N/A')}")
            st.write(f"**Farbe:** {order_info.get('color', 'N/A')}")
            st.write(f"**Status:** {order_info.get('status', 'N/A')}")
            
            if order_info.get('orderId'):
                st.write(f"**ORDER-ID:** `{order_info['orderId']}`")
            
            st.write(f"**Start:** {order_info.get('startTime', 'N/A')}")
            
            if order_info.get('endTime'):
                st.write(f"**Ende:** {order_info['endTime']}")
            
            if order_info.get('errorTime'):
                st.write(f"**Fehler:** {order_info['errorTime']}")
        
        with col2:
            st.write("**Nachrichten:**")
            messages = order_info.get('messages', [])
            if messages:
                st.write(f"**Anzahl:** {len(messages)}")
                
                # Letzte Nachricht anzeigen
                if messages:
                    last_msg = messages[-1]
                    st.write(f"**Letzte:** {last_msg.get('timestamp', 'N/A')}")
                    
                    # Message Details
                    with st.expander("📄 Letzte Nachricht Details"):
                        st.json(last_msg.get('data', {}))
            else:
                st.write("**Anzahl:** 0")
            
            # CCU Response
            if order_info.get('ccuResponse'):
                with st.expander("📋 CCU Response"):
                    st.json(order_info['ccuResponse'])
    
    def show_template_library(self):
        """Zeigt die Template Library"""
        st.subheader("📚 Template Library")
        
        templates = self.template_manager.list_templates()
        
        for template_name in templates:
            template_info = self.template_manager.get_template_info(template_name)
            if template_info:
                with st.expander(f"📄 {template_name}"):
                    st.write(f"**Beschreibung:** {template_info['description']}")
                    st.write(f"**Topic:** `{template_info['topic']}`")
                    
                    # Payload Preview
                    st.write("**Payload:**")
                    st.json(template_info['payload'])
                    
                    # Parameter
                    st.write("**Parameter:**")
                    for param, details in template_info['parameters'].items():
                        if isinstance(details, list):
                            st.write(f"  - **{param}:** {', '.join(details)}")
                        else:
                            st.write(f"  - **{param}:** {details}")
    
    def show_template_testing(self):
        """Zeigt Template Testing Interface"""
        st.subheader("🧪 Template Testing")
        
        # Template auswählen
        templates = self.template_manager.list_templates()
        selected_template = st.selectbox("Template auswählen:", templates)
        
        if selected_template:
            template_info = self.template_manager.get_template_info(selected_template)
            if template_info:
                st.write(f"**Template:** {selected_template}")
                st.write(f"**Topic:** `{template_info['topic']}`")
                
                # Parameter eingeben
                st.write("**Parameter eingeben:**")
                test_params = {}
                
                for param, details in template_info['parameters'].items():
                    if isinstance(details, list):
                        test_params[param] = st.selectbox(f"{param}:", details)
                    elif details == "string (NFC)":
                        test_params[param] = st.text_input(f"{param}:", value="04798eca341290")
                    elif details == "ISO 8601":
                        test_params[param] = st.text_input(f"{param}:", value=datetime.now().isoformat())
                    else:
                        test_params[param] = st.text_input(f"{param}:")
                
                # Validierung
                is_valid = self.template_manager.validate_parameters(selected_template, test_params)
                
                if is_valid:
                    st.success("✅ Parameter sind gültig")
                    
                    # Test senden (nur für Wareneingang)
                    if selected_template == "wareneingang_trigger":
                        if st.button("🚀 Test senden"):
                            success = self.template_manager.send_wareneingang_trigger(
                                test_params["color"], 
                                test_params["workpieceId"]
                            )
                            if success:
                                st.success("✅ Test erfolgreich gesendet!")
                            else:
                                st.error("❌ Fehler beim Senden des Tests")
                else:
                    st.error("❌ Parameter sind ungültig")
    
    def show_custom_template_creator(self):
        """Zeigt Interface zum Erstellen benutzerdefinierter Templates"""
        st.subheader("🔧 Benutzerdefinierte Templates")
        
        with st.form("custom_template_form"):
            template_name = st.text_input("Template Name:")
            topic = st.text_input("MQTT Topic:")
            
            # Payload JSON
            payload_json = st.text_area(
                "Payload (JSON):",
                value='{\n  "timestamp": "{{timestamp}}",\n  "type": "{{color}}"\n}',
                height=200
            )
            
            # Parameter
            st.write("**Parameter:**")
            param_name = st.text_input("Parameter Name:")
            param_type = st.selectbox("Parameter Typ:", ["string", "list", "ISO 8601"])
            
            if param_type == "list":
                param_values = st.text_input("Werte (kommagetrennt):")
            
            submitted = st.form_submit_button("Template erstellen")
            
            if submitted:
                try:
                    # Payload parsen
                    payload = json.loads(payload_json)
                    
                    # Parameter erstellen
                    parameters = {}
                    if param_name:
                        if param_type == "list":
                            parameters[param_name] = [v.strip() for v in param_values.split(",")]
                        else:
                            parameters[param_name] = param_type
                    
                    # Template erstellen
                    success = self.template_manager.create_custom_template(
                        template_name, topic, payload, parameters
                    )
                    
                    if success:
                        st.success(f"✅ Template '{template_name}' erfolgreich erstellt!")
                    else:
                        st.error("❌ Fehler beim Erstellen des Templates")
                        
                except json.JSONDecodeError:
                    st.error("❌ Ungültiges JSON Format")
                except Exception as e:
                    st.error(f"❌ Fehler: {e}")


def create_template_control_dashboard(template_manager: TemplateMessageManager) -> TemplateControlDashboard:
    """Erstellt ein Template Control Dashboard"""
    return TemplateControlDashboard(template_manager)


if __name__ == "__main__":
    # Test des Template Control Dashboards
    print("🧪 Template Control Dashboard Test")
    print("=" * 50)
    
    # Template Manager erstellen
    manager = TemplateMessageManager()
    
    # Dashboard erstellen
    dashboard = create_template_control_dashboard(manager)
    
    print("✅ Template Control Dashboard erstellt")
    print("📋 Verfügbare Methoden:")
    print("  - show_wareneingang_control()")
    print("  - show_order_tracking()")
    print("  - show_template_library()")
    print("  - show_template_testing()")
    print("  - show_custom_template_creator()")
    
    print("\n✅ Template Control Dashboard Test abgeschlossen")
