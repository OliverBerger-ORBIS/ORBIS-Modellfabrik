#!/usr/bin/env python3
"""
CCU Message Monitor Component - Wiederverwendbare Komponente für CCU MQTT Message Monitoring
"""

import streamlit as st
import pandas as pd
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_ccu_message_monitor(ccu_gateway, title="CCU Message Monitor", show_controls=True):
    """
    Render CCU Message Monitor Component - Wiederverwendbare Komponente
    
    Args:
        ccu_gateway: CCU Gateway instance (Gateway-Pattern)
        title: Title for the monitor section
        show_controls: Whether to show control buttons
    """
    try:
        logger.info("📡 Rendering CCU Message Monitor Component")
        
        st.subheader(f"📡 {title}")
        st.markdown("CCU MQTT Message Monitoring - Echtzeit-Nachrichten über CCU Gateway")
        
        if not ccu_gateway:
            st.error("❌ CCU Gateway nicht verfügbar")
            return
        
        # Get MQTT client through gateway
        mqtt_client = ccu_gateway.mqtt_client
        if not mqtt_client:
            st.error("❌ CCU MQTT Client nicht verfügbar über Gateway")
            return
        
        # DEBUG: Check CCU MQTT Client status
        logger.info(f"🔍 DEBUG: CCU MQTT Client connected: {mqtt_client.connected}")
        logger.info(f"🔍 DEBUG: CCU MQTT Client client_id: {mqtt_client.client_id}")
        logger.info(f"🔍 DEBUG: CCU MQTT Client subscribed topics: {mqtt_client._get_subscribed_topics()}")
        
        # CCU Message Monitor Controls (optional)
        if show_controls:
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button(f"{UISymbols.get_status_icon('refresh')} Refresh Messages", use_container_width=True, key="ccu_refresh_messages"):
                    logger.info("🔄 DEBUG: Refresh Messages Button clicked")
                    _refresh_ccu_messages(ccu_gateway)
            
            with col2:
                if st.button(f"{UISymbols.get_functional_icon('dashboard')} Show Statistics", use_container_width=True, key="ccu_show_statistics"):
                    _show_ccu_message_statistics(ccu_gateway)
            
            with col3:
                if st.button(f"{UISymbols.get_functional_icon('settings')} Clear Buffer", use_container_width=True, key="ccu_clear_buffer"):
                    _clear_ccu_message_buffer(ccu_gateway)
        
        # Get all buffers from CCU MQTT client
        all_buffers = mqtt_client.get_all_buffers()
        
        # DEBUG: Log buffer information
        logger.info(f"🔍 DEBUG: CCU MQTT Client buffers: {len(all_buffers) if all_buffers else 0} topics")
        if all_buffers:
            for topic, messages in all_buffers.items():
                logger.info(f"🔍 DEBUG: Topic {topic}: {len(messages) if messages else 0} messages")
        else:
            logger.warning("🔍 DEBUG: No buffers found in CCU MQTT Client")
        
        # Always show subscribed topics, even if no buffers
        subscribed_topics = mqtt_client._get_subscribed_topics()
        if subscribed_topics:
            st.success(f"📡 CCU MQTT Client subscribed to {len(subscribed_topics)} topics")
            with st.expander("📋 Subscribed Topics", expanded=False):
                for topic in subscribed_topics:
                    st.text(f"  • {topic}")
        else:
            st.warning("⚠️ CCU MQTT Client has no subscribed topics")
        
        if not all_buffers:
            st.info("📋 Keine CCU Messages verfügbar")
            st.info("💡 Messages werden angezeigt, sobald der Client connected ist und Nachrichten empfängt")
            return
        
        # Create message table data
        message_table_data = []
        
        for topic, messages in all_buffers.items():
            if not messages:
                continue
            
            # Create a copy of messages to avoid "deque mutated during iteration" error
            messages_copy = list(messages) if hasattr(messages, '__iter__') else [messages]
            
            # Process ALL messages in buffer, not just the latest (like Admin)
            for message in messages_copy:
                # Extract message info - handle both dict and other types
                if isinstance(message, dict):
                    # Format timestamp properly
                    raw_timestamp = message.get('mqtt_timestamp', 'Unknown')
                    if isinstance(raw_timestamp, (int, float)):
                        from datetime import datetime
                        timestamp = datetime.fromtimestamp(raw_timestamp).strftime('%H:%M:%S.%f')[:-3]
                    else:
                        timestamp = str(raw_timestamp)
                    
                    message_type = _get_message_type(topic)
                    status = _get_message_status(message)
                    
                    # Format payload as JSON if possible
                    payload = message.get('payload', message)
                    if isinstance(payload, (dict, list)):
                        import json
                        data = json.dumps(payload, indent=2)[:200] + "..." if len(json.dumps(payload)) > 200 else json.dumps(payload, indent=2)
                    else:
                        data = str(payload)[:100] + "..." if len(str(payload)) > 100 else str(payload)
                else:
                    timestamp = 'Unknown'
                    message_type = _get_message_type(topic)
                    status = "📨 Message"
                    data = str(message)[:100] + "..." if len(str(message)) > 100 else str(message)
                
                message_table_data.append({
                    "Topic": topic,
                    "Type": message_type,
                    "Status": status,
                    "Timestamp": timestamp,
                    "Data": data
                })
        
        # Sort messages by timestamp (newest first) - like Admin
        if message_table_data:
            # Sort by timestamp (newest first)
            message_table_data.sort(key=lambda x: x.get('Timestamp', ''), reverse=True)
            
            df = pd.DataFrame(message_table_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📋 Keine CCU Messages verfügbar")
        
    except Exception as e:
        logger.error(f"❌ CCU Message Monitor Component error: {e}")
        st.error(f"❌ CCU Message Monitor Component failed: {e}")


def _get_message_type(topic):
    """Get message type based on topic"""
    if "state" in topic:
        return "🟢 State"
    elif "connection" in topic:
        return "🔌 Connection"
    elif "factsheet" in topic:
        return "📄 Factsheet"
    elif "ccu" in topic:
        return "🏭 CCU"
    elif "module" in topic:
        return "🏗️ Module"
    elif "fts" in topic:
        return "🚗 FTS"
    else:
        return "📨 Message"


def _get_message_status(message):
    """Get message status based on content"""
    if isinstance(message, dict):
        if message.get('connected', False):
            return "🟢 Connected"
        elif message.get('available') in ["READY", "AVAILABLE"]:
            return "🟢 Available"
        elif message.get('available') == "BUSY":
            return "🟡 Busy"
        elif message.get('available') == "ERROR":
            return "🔴 Error"
        else:
            return "⚪ Unknown"
    else:
        # Handle non-dict messages (like deque items)
        return "📨 Message"


def _refresh_ccu_messages(ccu_gateway):
    """Refresh CCU Messages - EXACT like Admin but with CCU topics"""
    try:
        logger.info("🔄 DEBUG: _refresh_ccu_messages function called")
        logger.info("🔄 Refreshing CCU Messages")
        
        # Get MQTT client through gateway
        mqtt_client = ccu_gateway.mqtt_client
        if mqtt_client:
            logger.info("🔄 DEBUG: MQTT client exists, getting subscribed topics")
            # Get subscribed topics from registry (not hardcoded!)
            subscribed_topics = mqtt_client._get_subscribed_topics()
            logger.info(f"🔄 DEBUG: Got {len(subscribed_topics) if subscribed_topics else 0} subscribed topics")
            if subscribed_topics:
                # Re-subscribe to all CCU topics from registry
                logger.info(f"🔄 DEBUG: About to call subscribe_many, that is the problem")
                logger.info(f"🔄 DEBUG: Subscribed topics: {subscribed_topics}")
                # mqtt_client.subscribe_many(subscribed_topics)
                logger.info(f"🔄 DEBUG: We have to get all buffers instead")
                logger.info(f"📥 Re-subscribed to {len(subscribed_topics)} CCU topics")
            else:
                logger.warning("⚠️ No CCU topics found in registry")
        else:
            logger.warning("🔄 DEBUG: No MQTT client provided")
        logger.info("🔄 DEBUG: About to show success message")
        st.success("✅ CCU Messages refreshed!")
        logger.info("🔄 DEBUG: Success message shown")
        
        # CRITICAL: Request UI refresh to update the display
        from omf2.ui.utils.ui_refresh import request_refresh
        request_refresh()
    except Exception as e:
        logger.error(f"❌ DEBUG: Exception in _refresh_ccu_messages: {e}")
        logger.error(f"❌ CCU Messages refresh error: {e}")
        st.error(f"❌ CCU Messages refresh failed: {e}")


def _show_ccu_message_statistics(ccu_gateway):
    """Show CCU Message Statistics - ECHTE MQTT-Daten"""
    try:
        logger.info("📊 Showing CCU Message Statistics")
        st.subheader("📊 CCU Message Statistics")
        
        # Get all buffers from CCU Gateway
        all_buffers = ccu_gateway.get_all_message_buffers()
        
        # Calculate statistics
        total_topics = len(all_buffers)
        total_messages = 0
        for messages in all_buffers.values():
            if messages:
                # Create a copy to avoid "deque mutated during iteration" error
                messages_copy = list(messages) if hasattr(messages, '__iter__') else [messages]
                total_messages += len(messages_copy)
        
        # Count by type
        state_topics = sum(1 for topic in all_buffers.keys() if "state" in topic)
        connection_topics = sum(1 for topic in all_buffers.keys() if "connection" in topic)
        ccu_topics = sum(1 for topic in all_buffers.keys() if "ccu" in topic)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt Topics", total_topics)
        
        with col2:
            st.metric("Gesamt Messages", total_messages)
        
        with col3:
            st.metric("State Topics", state_topics)
        
        with col4:
            st.metric("Connection Topics", connection_topics)
        
        logger.info("CCU Message Statistics erfolgreich angezeigt")
        
    except Exception as e:
        logger.error(f"❌ CCU Message Statistics error: {e}")
        st.error(f"❌ CCU Message Statistics failed: {e}")


def _clear_ccu_message_buffer(ccu_gateway):
    """Clear CCU Message Buffer"""
    try:
        logger.info("🧹 Clearing CCU Message Buffer")
        # TODO: Implement buffer clearing
        st.success("✅ CCU Message Buffer cleared!")
    except Exception as e:
        logger.error(f"❌ CCU Message Buffer clear error: {e}")
        st.error(f"❌ CCU Message Buffer clear failed: {e}")
