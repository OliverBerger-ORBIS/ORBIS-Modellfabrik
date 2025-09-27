"""
Factory Steering/Control Tab for OMF2 Dashboard
Administrative control interface for factory operations
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any

from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_steering_tab():
    """Render the factory steering/control tab"""
    st.header("🎛️ Factory Control")
    st.markdown("Administrative control interface for factory operations")
    
    # Create subtabs for different control areas
    control_tabs = st.tabs(["🏭 Factory Control", "🔧 Module Control", "📊 System Monitor", "⚙️ Configuration"])
    
    with control_tabs[0]:
        _render_factory_control()
    
    with control_tabs[1]:
        _render_module_control()
    
    with control_tabs[2]:
        _render_system_monitor()
    
    with control_tabs[3]:
        _render_configuration()


def _render_factory_control():
    """Render factory-level control interface"""
    st.subheader("🏭 Factory Operations Control")
    
    # Factory status overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Factory Status", "🟢 Running")
    
    with col2:
        st.metric("Active Workpieces", "12", "+2")
    
    with col3:
        st.metric("Modules Online", "8/10", "⚠️")
    
    with col4:
        st.metric("Efficiency", "87%", "+3%")
    
    st.markdown("---")
    
    # Factory control buttons
    st.subheader("🎛️ Factory Commands")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("▶️ Start Production", type="primary"):
            st.success("✅ Production sequence started")
            logger.info("Factory production started via dashboard")
    
    with col2:
        if st.button("⏸️ Pause Operations", type="secondary"):
            st.warning("⏸️ Factory operations paused")
            logger.info("Factory operations paused via dashboard")
    
    with col3:
        if st.button("⏹️ Stop Production", type="secondary"):
            st.error("⏹️ Production stopped")
            logger.info("Factory production stopped via dashboard")
    
    with col4:
        if st.button("🔄 Reset System", type="secondary"):
            st.info("🔄 System reset initiated")
            logger.info("Factory system reset via dashboard")
    
    # Production queue
    st.markdown("---")
    st.subheader("📋 Production Queue")
    
    queue_items = [
        {"id": "WP001", "color": "BLAU", "status": "processing", "module": "HBW"},
        {"id": "WP002", "color": "WEISS", "status": "queued", "module": "-"},
        {"id": "WP003", "color": "ROT", "status": "queued", "module": "-"}
    ]
    
    for item in queue_items:
        status_icon = "⚙️" if item["status"] == "processing" else "⏳"
        st.write(f"{status_icon} **{item['id']}** - {item['color']} - Module: {item['module']} - Status: {item['status'].title()}")


def _render_module_control():
    """Render module-level control interface"""
    st.subheader("🔧 Individual Module Control")
    
    # Module selection
    modules = ["HBW", "DRILL", "MILL", "AIQS", "DPS", "CHRG", "FTS"]
    selected_module = st.selectbox("Select Module:", modules)
    
    # Module status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Module Status", "🟢 Online")
    
    with col2:
        st.metric("Current Task", "Processing WP001")
    
    with col3:
        st.metric("Queue Length", "2 items")
    
    # Module control buttons
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"▶️ Start {selected_module}"):
            st.success(f"✅ {selected_module} started")
    
    with col2:
        if st.button(f"⏸️ Pause {selected_module}"):
            st.warning(f"⏸️ {selected_module} paused")
    
    with col3:
        if st.button(f"⏹️ Stop {selected_module}"):
            st.error(f"⏹️ {selected_module} stopped")
    
    with col4:
        if st.button(f"🔄 Reset {selected_module}"):
            st.info(f"🔄 {selected_module} reset")
    
    # Module parameters
    st.markdown("---")
    st.subheader("⚙️ Module Parameters")
    
    with st.expander(f"{selected_module} Configuration", expanded=False):
        st.slider("Processing Speed", 0, 100, 75, key=f"speed_{selected_module}")
        st.slider("Quality Threshold", 0, 100, 90, key=f"quality_{selected_module}")
        st.checkbox("Auto-retry on Error", value=True, key=f"retry_{selected_module}")


def _render_system_monitor():
    """Render system monitoring interface"""
    st.subheader("📊 System Performance Monitor")
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("CPU Usage", "45%", "-5%")
    
    with col2:
        st.metric("Memory Usage", "68%", "+2%")
    
    with col3:
        st.metric("Network I/O", "1.2 MB/s", "+0.3")
    
    with col4:
        st.metric("MQTT Messages", "1,247", "+15")
    
    # System status
    st.markdown("---")
    st.subheader("🔍 System Status")
    
    status_items = [
        {"component": "CCU Gateway", "status": "healthy", "uptime": "2d 14h 23m"},
        {"component": "Message Center", "status": "healthy", "uptime": "2d 14h 23m"},
        {"component": "MQTT Broker", "status": "warning", "uptime": "1d 08h 45m"},
        {"component": "Database", "status": "healthy", "uptime": "7d 12h 15m"}
    ]
    
    for item in status_items:
        status_color = "🟢" if item["status"] == "healthy" else "🟡" if item["status"] == "warning" else "🔴"
        st.write(f"{status_color} **{item['component']}** - {item['status'].title()} - Uptime: {item['uptime']}")
    
    # Resource usage chart
    st.markdown("---")
    st.subheader("📈 Resource Usage Trends")
    
    import pandas as pd
    import numpy as np
    from datetime import timedelta
    
    # Generate sample data
    hours = list(range(24))
    data = pd.DataFrame({
        'Hour': hours,
        'CPU %': np.random.randint(20, 80, 24),
        'Memory %': np.random.randint(40, 90, 24),
        'Network MB/s': np.random.uniform(0.5, 2.0, 24)
    })
    
    st.line_chart(data.set_index('Hour'))


def _render_configuration():
    """Render system configuration interface"""
    st.subheader("⚙️ System Configuration")
    
    st.warning("⚠️ Changes to system configuration require administrator privileges and may require system restart.")
    
    # Configuration sections
    config_sections = st.tabs(["🔗 MQTT Settings", "🏭 Factory Settings", "👥 User Management", "📊 Logging"])
    
    with config_sections[0]:
        _render_mqtt_config()
    
    with config_sections[1]:
        _render_factory_config()
    
    with config_sections[2]:
        _render_user_config()
    
    with config_sections[3]:
        _render_logging_config()


def _render_mqtt_config():
    """Render MQTT configuration"""
    st.subheader("🔗 MQTT Broker Configuration")
    
    with st.form("mqtt_config"):
        st.text_input("MQTT Host", value="localhost", key="mqtt_host")
        st.number_input("MQTT Port", min_value=1, max_value=65535, value=1883, key="mqtt_port")
        st.text_input("Username", key="mqtt_username")
        st.text_input("Password", type="password", key="mqtt_password")
        st.number_input("Keepalive (seconds)", min_value=30, max_value=300, value=60, key="mqtt_keepalive")
        
        if st.form_submit_button("💾 Save MQTT Configuration"):
            st.success("✅ MQTT configuration saved (restart required)")


def _render_factory_config():
    """Render factory configuration"""
    st.subheader("🏭 Factory Configuration")
    
    with st.form("factory_config"):
        st.text_input("Factory Name", value="ORBIS Modellfabrik", key="factory_name")
        st.text_input("Factory Location", value="Deutschland", key="factory_location")
        st.number_input("Max Concurrent Workpieces", min_value=1, max_value=50, value=10, key="max_workpieces")
        st.selectbox("Default Workpiece Color", ["BLAU", "WEISS", "ROT"], key="default_color")
        st.checkbox("Auto-start on System Boot", value=True, key="auto_start")
        
        if st.form_submit_button("💾 Save Factory Configuration"):
            st.success("✅ Factory configuration saved")


def _render_user_config():
    """Render user management configuration"""
    st.subheader("👥 User Management")
    
    st.info("🔒 User management configuration is handled via user_roles.yml file")
    
    # Show current users (read-only for now)
    st.write("**Current Users:**")
    users = [
        {"name": "admin", "role": "Administrator", "active": True},
        {"name": "operator1", "role": "Operator", "active": True},
        {"name": "guest", "role": "Viewer", "active": True}
    ]
    
    for user in users:
        status_icon = "🟢" if user["active"] else "🔴"
        st.write(f"{status_icon} **{user['name']}** - {user['role']}")


def _render_logging_config():
    """Render logging configuration"""
    st.subheader("📊 Logging Configuration")
    
    with st.form("logging_config"):
        st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"], index=1, key="log_level")
        st.number_input("Max Log File Size (MB)", min_value=1, max_value=1000, value=10, key="max_log_size")
        st.number_input("Log Retention Days", min_value=1, max_value=365, value=30, key="log_retention")
        st.checkbox("Enable File Logging", value=True, key="file_logging")
        st.checkbox("Enable Console Logging", value=True, key="console_logging")
        
        if st.form_submit_button("💾 Save Logging Configuration"):
            st.success("✅ Logging configuration saved")