#!/usr/bin/env python3
"""
Enhanced View Subtab - omf/ style message display with filtering and detailed payload inspection
Gateway-Pattern konform: Nutzt AdminGateway statt direkten MQTT-Client
"""

import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, List, Any

from omf2.ui.utils.message_utils import (
    MessageRow, 
    flatten_messages_for_df, 
    parse_payload_for_display,
    get_available_categories,
    filter_messages_by_category,
    filter_messages_by_type
)
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_message_monitor_subtab(admin_gateway):
    """Render Message Monitor Subtab with omf/ style UI
    
    Args:
        admin_gateway: AdminGateway Instanz (Gateway-Pattern)
    """
    logger.info(f"{UISymbols.get_functional_icon('dashboard')} Rendering Message Monitor Subtab")
    
    try:
        st.subheader(f"{UISymbols.get_functional_icon('dashboard')} Message Monitor (omf/ Style)")
        st.markdown("**Structured table view with filtering and detailed payload inspection**")
        
        # Connection status shown in sidebar only
        
        # Filter-Optionen (aus omf/)
        st.subheader(f"{UISymbols.get_functional_icon('search')} Filter & Einstellungen")
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])

        with col5:
            if st.button("🗑️ Historie löschen", type="secondary", key="clear_history_enhanced"):
                logger.info("🗑️ Historie löschen angefordert")
                # Gateway-Pattern: Nutze AdminGateway clear_message_history
                if admin_gateway.clear_message_history():
                    st.success(f"{UISymbols.get_status_icon('success')} Nachrichten-Historie gelöscht")
                    request_refresh()
                else:
                    st.error(f"{UISymbols.get_status_icon('error')} Historie löschen fehlgeschlagen")

        with col1:
            # Nachrichten-Typ Filter
            message_type_filter = st.selectbox(
                "📨 Nachrichten-Typ", 
                options=["Alle", "received", "sent"], 
                index=0,
                key="enhanced_message_type_filter"
            )

        with col2:
            # Topic-Kategorie Filter (nur nach Topic-Pattern)
            topic_categories = ["Alle", "ccu", "module", "txt", "nodered", "fts"]
            category_filter = st.selectbox(
                "🏷️ Topic-Kategorie", 
                options=topic_categories, 
                index=0,
                key="enhanced_category_filter"
            )

        with col3:
            # Einfacher Filter nach Topic-Pattern
            topic_pattern_filter = st.text_input(
                f"{UISymbols.get_functional_icon('search')} Topic Pattern",
                placeholder="z.B. ccu/, module/, txt/",
                key="enhanced_topic_pattern_filter"
            )

        with col4:
            # Anzahl Nachrichten
            max_messages = st.number_input(
                f"{UISymbols.get_functional_icon('dashboard')} Max", 
                min_value=10, 
                max_value=1000, 
                value=200, 
                step=10,
                key="enhanced_max_messages"
            )

        with col6:
            # Manual refresh only
            if st.button(f"{UISymbols.get_status_icon('refresh')} Refresh Now", key="manual_refresh_enhanced"):
                request_refresh()

        # Get all topic buffers and convert to MessageRow format
        try:
            # Gateway-Pattern: Nutze AdminGateway get_all_message_buffers
            all_buffers = admin_gateway.get_all_message_buffers()
            message_rows = []
            
            for topic, buffer_data in all_buffers.items():
                if buffer_data and len(buffer_data) > 0:
                    # Process ALL messages in buffer, not just the latest
                    for message in buffer_data:
                        message_row = MessageRow(
                            topic=topic,
                            payload=message.get('payload', message),
                            message_type=message.get('message_type', 'received'),  # Default to 'received' for normal messages
                            timestamp=message.get('timestamp', time.time()),
                            qos=message.get('qos', 0),
                            retain=message.get('retain', False)
                        )
                        message_rows.append(message_row)
        except Exception as e:
            logger.error(f"{UISymbols.get_status_icon('error')} Message buffer processing failed: {e}")
            st.error(f"{UISymbols.get_status_icon('error')} Message processing error: {e}")
            message_rows = []
            all_buffers = {}

        # Sort messages by timestamp (newest first)
        message_rows.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Filter messages
        filtered_messages = message_rows
        
        # Apply filters (nur einfache Filter)
        try:
            # Message Type Filter
            if message_type_filter != "Alle":
                filtered_messages = filter_messages_by_type(filtered_messages, message_type_filter)
            
            # Category Filter
            if category_filter != "Alle":
                filtered_messages = filter_messages_by_category(filtered_messages, category_filter)
            
            # Topic-Pattern Filter
            if topic_pattern_filter:
                filtered_messages = [msg for msg in filtered_messages if topic_pattern_filter.lower() in msg.topic.lower()]
        except Exception as e:
            logger.error(f"{UISymbols.get_status_icon('error')} Filter application failed: {e}")
            st.error(f"{UISymbols.get_status_icon('error')} Filter error: {e}")
            filtered_messages = message_rows  # Fallback to all messages

        # Nach Anzahl begrenzen
        filtered_messages = filtered_messages[-max_messages:]

        # Nachrichten anzeigen
        st.subheader("📨 Nachrichten")

        if filtered_messages:
            # Kompakte Tabellen-Darstellung (aus omf/)
            df = flatten_messages_for_df(filtered_messages)

            # Statistiken
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric(f"{UISymbols.get_functional_icon('dashboard')} Gesamt", len(message_rows))
            with col2:
                st.metric(f"{UISymbols.get_functional_icon('search')} Gefiltert", len(filtered_messages))
            with col3:
                received_count = len([m for m in filtered_messages if m.message_type == "received"])
                st.metric(f"{UISymbols.get_status_icon('receive')} Empfangen", received_count)
            with col4:
                sent_count = len([m for m in filtered_messages if m.message_type == "sent"])
                st.metric(f"{UISymbols.get_status_icon('send')} Gesendet", sent_count)
            with col5:
                st.metric(f"{UISymbols.get_functional_icon('topic_driven')} Topics", len(all_buffers))

            # Tabelle anzeigen (aus omf/)
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "⏰": st.column_config.TextColumn("Zeit", width="small"),
                    "📨": st.column_config.TextColumn("Typ", width="small"),
                    "🏷️": st.column_config.TextColumn("Kategorie", width="small"),
                    f"{UISymbols.get_functional_icon('topic_driven')}": st.column_config.TextColumn("Topic", width="medium"),
                    "📄": st.column_config.TextColumn("Payload", width="extra-large"),
                    "🔢": st.column_config.NumberColumn("QoS", width="small"),
                    "💾": st.column_config.TextColumn("Retain", width="small"),
                },
                hide_index=True,
                height=400,
            )

            # Erweiterte Payload-Anzeige für die letzten 5 Nachrichten (aus omf/)
            st.subheader(f"{UISymbols.get_functional_icon('search')} Detaillierte Payload-Ansicht (letzte 5 Nachrichten)")
            recent_messages = filtered_messages[-5:] if len(filtered_messages) >= 5 else filtered_messages

            for i, msg in enumerate(reversed(recent_messages)):
                with st.expander(f"📄 Nachricht {len(recent_messages) - i}: {msg.topic}", expanded=False):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.write(f"**Zeit:** {datetime.fromtimestamp(msg.timestamp).strftime('%H:%M:%S')}")
                        st.write(f"**Typ:** {msg.message_type}")
                        st.write(f"**QoS:** {msg.qos}")
                        st.write(f"**Retain:** {msg.retain}")
                    with col2:
                        st.write("**Vollständiger Payload:**")
                        # Parse payload for display
                        parsed_payload = parse_payload_for_display(msg.payload)
                        st.code(parsed_payload, language="json")

            # Filter-Info
            filter_info = (
                f"{UISymbols.get_functional_icon('dashboard')} **{len(filtered_messages)} von {len(message_rows)} "
                f"Nachrichten angezeigt** (gefiltert nach: {message_type_filter}, "
                f"{category_filter})"
            )
            st.info(filter_info)

        else:
            st.warning(f"{UISymbols.get_status_icon('warning')} Keine Nachrichten entsprechen den aktuellen Filtern")
            if not all_buffers:
                st.info("💡 Send a test message from the 'Send Messages' tab to see live monitoring in action!")

        # Auto-refresh functionality removed (not supported)

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Enhanced View Subtab error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Enhanced View failed: {e}")
