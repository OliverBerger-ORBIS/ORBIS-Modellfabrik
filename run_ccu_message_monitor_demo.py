#!/usr/bin/env python3
"""
Demo script to run CCU Message Monitor with sample data.

Usage:
    streamlit run run_ccu_message_monitor_demo.py
"""

import streamlit as st

from omf2.ui.ccu.ccu_message_monitor import render_ccu_message_monitor

# Configure Streamlit page
st.set_page_config(
    page_title="CCU Message Monitor Demo",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add title and description
st.title("📡 CCU Message Monitor Demo")
st.markdown(
    """
This demo shows the CCU Message Monitor component with sample MQTT messages.

**Features demonstrated:**
- Filter persistence across refreshes
- 5-column filter bar (Topic, Module/FTS, Status, Type, Actions)
- Automatic status and module detection
- Row selector for payload inspection
- Cached dataframe preprocessing for performance
"""
)

st.markdown("---")

# Render the component with default sample data (None = use internal sample data)
render_ccu_message_monitor(messages=None)

# Add sidebar information
st.sidebar.header("ℹ️ Demo Information")
st.sidebar.markdown(
    """
**Test Scenarios:**

1. **Filter by Topic:**
   - Select "ccu/status" to see only status messages
   - Select "ccu/connection" to see connection events

2. **Filter by Module/FTS:**
   - Select "Bohrstation" to see drilling station messages
   - Select "FTS-1" to see transport system messages

3. **Filter by Status:**
   - Select "Module State" to see module status changes
   - Select "Connection Status" to see connection events

4. **Combined Filters:**
   - Try combining multiple filters
   - Example: Topic="ccu/status" + Status="Module State"

5. **Filter Persistence:**
   - Set filters
   - Click "Refresh" button
   - Filters should remain set

6. **Payload Viewer:**
   - Use the row selector to view detailed payload
   - Examine JSON structure of different message types
"""
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
**Sample Data Includes:**
- Connection status messages
- Module state updates (Bohrstation, Frässtation, etc.)
- FTS transport messages
- Workflow updates
- Error conditions
- System state messages
"""
)
