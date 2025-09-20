"""
APS Orders - Order History
Zeigt die Order History an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh

class APSOrderHistoryManager:
    """Manager für Order History"""
    
    def __init__(self):
        self.history = []
        self.last_update = None
    
    def update_from_mqtt_client(self, mqtt_client):
        """Aktualisiert die History basierend auf MQTT-Nachrichten"""
        try:
            # Subscribe to order-related topics
            mqtt_client.subscribe_many([
                "ccu/order/request",
                "ccu/order/response",
                "ccu/order/state",
                "module/v1/ff/+/order"
            ])
            
            # Get messages from buffer
            request_messages = list(mqtt_client.get_buffer("ccu/order/request"))
            response_messages = list(mqtt_client.get_buffer("ccu/order/response"))
            state_messages = list(mqtt_client.get_buffer("ccu/order/state"))
            module_messages = list(mqtt_client.get_buffer("module/v1/ff/+/order"))
            
            # Combine all order-related messages
            self.history = request_messages + response_messages + state_messages + module_messages
            
        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden der Order History: {e}")

def show_aps_orders_history():
    """Zeigt die Order History an"""
    st.subheader("📊 Order History")
    
    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return
    
    # Initialize manager in session state
    if "aps_order_history_manager" not in st.session_state:
        st.session_state["aps_order_history_manager"] = APSOrderHistoryManager()
    
    manager = st.session_state["aps_order_history_manager"]
    
    # Update history from MQTT
    manager.update_from_mqtt_client(client)
    
    if manager.history:
        st.success(f"✅ {len(manager.history)} Order-Nachrichten gefunden")
        
        # Show order messages
        for i, msg in enumerate(manager.history):
            with st.expander(f"📋 Order {i+1}: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    else:
        st.warning("⚠️ Keine Order-Nachrichten gefunden")
    
    # Clear history button
    if st.button("🗑️ Clear History", key="aoh_clear_history"):
        manager.history = []
        st.success("✅ History gelöscht")
    
    # Auto-refresh info
    st.info("💡 **Order History wird automatisch aus MQTT-Nachrichten aktualisiert**")
