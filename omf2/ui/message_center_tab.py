"""
Message Center Tab for OMF2 Dashboard
Handles messaging and notifications
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import List, Dict, Any

from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_message_center_tab():
    """Render the message center tab"""
    st.header("📨 Message Center")
    st.markdown("Central messaging and notification hub")
    
    # Create tabs for different message types
    msg_tabs = st.tabs(["📥 Inbox", "📤 Outbox", "⚠️ Alerts", "📊 Statistics"])
    
    with msg_tabs[0]:
        _render_inbox()
    
    with msg_tabs[1]:
        _render_outbox()
    
    with msg_tabs[2]:
        _render_alerts()
    
    with msg_tabs[3]:
        _render_statistics()


def _render_inbox():
    """Render inbox section"""
    st.subheader("📥 Incoming Messages")
    
    # Sample message data
    messages = [
        {
            "id": "MSG001",
            "sender": "CCU System",
            "subject": "Workpiece Processing Complete",
            "timestamp": datetime.now() - timedelta(minutes=5),
            "priority": "normal",
            "read": False
        },
        {
            "id": "MSG002", 
            "sender": "Factory Controller",
            "subject": "Maintenance Required",
            "timestamp": datetime.now() - timedelta(hours=1),
            "priority": "high",
            "read": True
        },
        {
            "id": "MSG003",
            "sender": "Quality Control",
            "subject": "Inspection Results Available",
            "timestamp": datetime.now() - timedelta(hours=3),
            "priority": "normal",
            "read": True
        }
    ]
    
    # Message filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_unread = st.checkbox("Show unread only", value=False)
    
    with col2:
        priority_filter = st.selectbox("Priority filter", ["All", "high", "normal", "low"])
    
    with col3:
        if st.button("🔄 Refresh Messages"):
            st.rerun()
    
    # Filter messages
    filtered_messages = messages
    if show_unread:
        filtered_messages = [msg for msg in filtered_messages if not msg["read"]]
    
    if priority_filter != "All":
        filtered_messages = [msg for msg in filtered_messages if msg["priority"] == priority_filter]
    
    # Display messages
    for msg in filtered_messages:
        priority_icon = "🔴" if msg["priority"] == "high" else "🟡" if msg["priority"] == "normal" else "🟢"
        read_icon = "📧" if not msg["read"] else "📖"
        
        with st.expander(f"{priority_icon} {read_icon} {msg['subject']} - {msg['sender']}", expanded=not msg["read"]):
            st.write(f"**From:** {msg['sender']}")
            st.write(f"**Time:** {msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"**Priority:** {msg['priority'].title()}")
            st.write("---")
            st.write("Message content would be displayed here...")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Mark as Read", key=f"read_{msg['id']}"):
                    st.success(f"Message {msg['id']} marked as read")
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{msg['id']}"):
                    st.success(f"Message {msg['id']} deleted")
            with col3:
                if st.button("↩️ Reply", key=f"reply_{msg['id']}"):
                    st.info("Reply functionality coming soon")


def _render_outbox():
    """Render outbox section"""
    st.subheader("📤 Send Message")
    
    # Message composition form
    with st.form("send_message"):
        recipient = st.selectbox("Recipient", ["CCU System", "Factory Controller", "Quality Control", "Maintenance"])
        subject = st.text_input("Subject")
        priority = st.selectbox("Priority", ["normal", "high", "low"])
        message_body = st.text_area("Message", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            send_now = st.form_submit_button("📤 Send Now")
        with col2:
            save_draft = st.form_submit_button("💾 Save Draft")
        
        if send_now:
            if subject and message_body:
                st.success(f"✅ Message sent to {recipient}")
                logger.info(f"Message sent to {recipient}: {subject}")
            else:
                st.error("❌ Please fill in subject and message")
        
        if save_draft:
            st.info("💾 Draft saved")
    
    st.markdown("---")
    st.subheader("📝 Sent Messages")
    
    # Sample sent messages
    sent_messages = [
        {"recipient": "Maintenance", "subject": "Schedule Inspection", "timestamp": datetime.now() - timedelta(hours=2)},
        {"recipient": "CCU System", "subject": "Configuration Update", "timestamp": datetime.now() - timedelta(days=1)}
    ]
    
    for msg in sent_messages:
        st.write(f"📤 **To:** {msg['recipient']} | **Subject:** {msg['subject']} | **Sent:** {msg['timestamp'].strftime('%Y-%m-%d %H:%M')}")


def _render_alerts():
    """Render alerts section"""
    st.subheader("⚠️ System Alerts")
    
    # Sample alerts
    alerts = [
        {"level": "error", "message": "MQTT connection lost to CCU", "timestamp": datetime.now() - timedelta(minutes=2)},
        {"level": "warning", "message": "High CPU usage on controller", "timestamp": datetime.now() - timedelta(minutes=15)},
        {"level": "info", "message": "Scheduled maintenance reminder", "timestamp": datetime.now() - timedelta(hours=1)}
    ]
    
    for alert in alerts:
        if alert["level"] == "error":
            st.error(f"🔴 **Error:** {alert['message']} - {alert['timestamp'].strftime('%H:%M:%S')}")
        elif alert["level"] == "warning":
            st.warning(f"🟡 **Warning:** {alert['message']} - {alert['timestamp'].strftime('%H:%M:%S')}")
        else:
            st.info(f"🔵 **Info:** {alert['message']} - {alert['timestamp'].strftime('%H:%M:%S')}")
    
    # Alert configuration
    st.markdown("---")
    st.subheader("🔔 Alert Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Email notifications", value=True)
        st.checkbox("Desktop notifications", value=False)
    
    with col2:
        st.selectbox("Alert threshold", ["Low", "Medium", "High"], index=1)
        st.number_input("Max alerts per hour", min_value=1, max_value=100, value=10)


def _render_statistics():
    """Render message statistics"""
    st.subheader("📊 Message Statistics")
    
    # Sample statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Messages", "1,247", "+23")
    
    with col2:
        st.metric("Unread Messages", "5", "-2")
    
    with col3:
        st.metric("Alerts Today", "8", "+3")
    
    with col4:
        st.metric("Response Rate", "94%", "+2%")
    
    # Message trend chart (placeholder)
    st.markdown("---")
    st.subheader("📈 Message Trends")
    
    import pandas as pd
    import numpy as np
    
    # Generate sample data
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='D')
    data = pd.DataFrame({
        'Date': dates,
        'Messages': np.random.randint(20, 100, len(dates)),
        'Alerts': np.random.randint(0, 15, len(dates))
    })
    
    st.line_chart(data.set_index('Date'))
    
    # Message types distribution
    st.markdown("---")
    st.subheader("📋 Message Types")
    
    message_types = {
        "System Notifications": 45,
        "Error Reports": 15,
        "Status Updates": 30,
        "User Messages": 10
    }
    
    st.bar_chart(message_types)