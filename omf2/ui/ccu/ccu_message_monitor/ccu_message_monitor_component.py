#!/usr/bin/env python3
"""
CCU Message Monitor Component - Displays and filters CCU MQTT messages
"""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import pandas as pd
    import streamlit as st

    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

logger = logging.getLogger(__name__)


# Constants for filter options
ALL_OPTION = "All"
TOPIC_OPTIONS = [
    ALL_OPTION,
    "ccu/state",
    "ccu/status",
    "ccu/control",
    "ccu/workflow",
    "ccu/connection",
]

STATUS_OPTIONS = [
    ALL_OPTION,
    "Connection Status",
    "Module State",
    "FTS State",
    "Factsheet",
    "CCU State",
]

TYPE_OPTIONS = [
    ALL_OPTION,
    "Status Update",
    "Control Command",
    "Connection",
    "Workflow",
]


def _extract_serial_from_payload(payload: Any) -> str:
    """Extract serial number from payload if present."""
    if isinstance(payload, dict):
        # Look for common serial number fields
        for key in ["serial", "serial_number", "device_serial", "module_serial"]:
            if key in payload:
                return str(payload[key])
        # Look for nested serial
        if "details" in payload and isinstance(payload["details"], dict):
            for key in ["serial", "serial_number"]:
                if key in payload["details"]:
                    return str(payload["details"][key])
    return ""


def _detect_status_category(topic: str, payload: Any) -> str:
    """
    Detect status category based on topic and payload content.

    Categories:
    - Connection Status: Connection-related messages
    - Module State: Module state changes (Bohrstation, Frässtation, etc.)
    - FTS State: FTS (Fahrerloses Transportsystem) state
    - Factsheet: Factsheet-related messages
    - CCU State: General CCU state messages
    """
    topic_lower = topic.lower()

    # Connection Status
    if "connection" in topic_lower:
        return "Connection Status"

    if isinstance(payload, dict):
        payload_str = json.dumps(payload).lower()

        # Check for connection-related keywords
        if any(word in payload_str for word in ["connected", "disconnected", "connection"]):
            return "Connection Status"

        # Check for FTS-related keywords
        if any(word in payload_str for word in ["fts", "transport", "fahrerlos"]):
            return "FTS State"

        # Check for Module state (Bohrstation, Frässtation, etc.)
        module_pattern = r'(bohr|fräs|dreh|montage|station|modul)'
        if re.search(module_pattern, payload_str, re.IGNORECASE):
            return "Module State"

        # Check for Factsheet
        if "factsheet" in payload_str:
            return "Factsheet"

    # Default to CCU State for status/state topics
    if "status" in topic_lower or "state" in topic_lower:
        return "CCU State"

    return "CCU State"


def _detect_module_or_fts(payload: Any) -> str:
    """
    Extract module name or FTS identifier from payload.

    Returns module/FTS name if found, otherwise empty string.
    """
    if isinstance(payload, dict):
        # Direct module field
        if "module" in payload:
            return str(payload["module"])

        # Component field
        if "component" in payload:
            return str(payload["component"])

        # Target field
        if "target" in payload:
            return str(payload["target"])

        # Check in details
        if "details" in payload and isinstance(payload["details"], dict):
            if "module" in payload["details"]:
                return str(payload["details"]["module"])
            if "component" in payload["details"]:
                return str(payload["details"]["component"])

        # Search for module patterns in payload
        payload_str = json.dumps(payload)

        # FTS patterns
        fts_match = re.search(r'(FTS[-_]?\d+|fts[-_]?\d+)', payload_str, re.IGNORECASE)
        if fts_match:
            return fts_match.group(1).upper()

        # Module patterns (Bohrstation, Frässtation, etc.)
        module_match = re.search(r'(Bohr|Fräs|Dreh|Montage)station', payload_str, re.IGNORECASE)
        if module_match:
            return module_match.group(0).capitalize()

    return ""


def _detect_message_type(topic: str, payload: Any) -> str:
    """Detect message type based on topic."""
    topic_lower = topic.lower()

    if "status" in topic_lower:
        return "Status Update"
    elif "control" in topic_lower:
        return "Control Command"
    elif "connection" in topic_lower:
        return "Connection"
    elif "workflow" in topic_lower:
        return "Workflow"
    else:
        return "Other"


@st.cache_data(ttl=60)
def _prepare_dataframe(messages: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Prepare and cache dataframe with extracted fields for efficient filtering.

    Args:
        messages: List of message dicts with 'timestamp', 'topic', 'payload'

    Returns:
        DataFrame with columns: timestamp, topic, msg_type, serial, detected_status,
                                module_fts, type_display, payload_str, payload_obj
    """
    rows = []

    for msg in messages:
        topic = msg.get("topic", "")
        payload = msg.get("payload", {})
        timestamp = msg.get("timestamp", 0)

        # Convert timestamp to datetime
        try:
            dt = datetime.fromtimestamp(timestamp)
            timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError):
            timestamp_str = str(timestamp)

        # Extract fields
        serial = _extract_serial_from_payload(payload)
        detected_status = _detect_status_category(topic, payload)
        module_fts = _detect_module_or_fts(payload)
        msg_type = _detect_message_type(topic, payload)

        # Create display type
        type_display = msg_type

        # Payload as string for display
        if isinstance(payload, dict):
            payload_str = json.dumps(payload, indent=2, ensure_ascii=False)
        else:
            payload_str = str(payload)

        rows.append(
            {
                "timestamp": timestamp_str,
                "topic": topic,
                "msg_type": msg_type,
                "serial": serial,
                "detected_status": detected_status,
                "module_fts": module_fts,
                "type_display": type_display,
                "payload_str": payload_str,
                "payload_obj": payload,
            }
        )

    return pd.DataFrame(rows)


def _apply_filters(
    df: pd.DataFrame, topic_filter: str, module_fts_filter: str, status_filter: str, type_filter: str
) -> pd.DataFrame:
    """
    Apply filters to dataframe.

    Args:
        df: DataFrame to filter
        topic_filter: Topic filter value
        module_fts_filter: Module/FTS filter value
        status_filter: Status category filter value
        type_filter: Message type filter value

    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()

    # Apply topic filter
    if topic_filter != ALL_OPTION:
        # Support wildcard matching for topics with /+
        if "+" in topic_filter:
            pattern = topic_filter.replace("+", ".*")
            filtered = filtered[filtered["topic"].str.match(pattern, na=False)]
        else:
            filtered = filtered[filtered["topic"] == topic_filter]

    # Apply module/FTS filter
    if module_fts_filter != ALL_OPTION:
        filtered = filtered[filtered["module_fts"] == module_fts_filter]

    # Apply status filter
    if status_filter != ALL_OPTION:
        filtered = filtered[filtered["detected_status"] == status_filter]

    # Apply type filter
    if type_filter != ALL_OPTION:
        filtered = filtered[filtered["type_display"] == type_filter]

    return filtered


def _initialize_session_state():
    """Initialize all required session state keys before widget creation."""
    defaults = {
        "ccu_msg_topic_filter": ALL_OPTION,
        "ccu_msg_module_fts_filter": ALL_OPTION,
        "ccu_msg_status_filter": ALL_OPTION,
        "ccu_msg_type_filter": ALL_OPTION,
        "ccu_msg_selected_row": None,
        "ccu_msg_show_payload": False,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def render_ccu_message_monitor(messages: Optional[List[Dict[str, Any]]] = None):
    """
    Render CCU Message Monitor component.

    Args:
        messages: List of messages to display. Each message should have:
                  - timestamp: Unix timestamp or datetime
                  - topic: MQTT topic string
                  - payload: Message payload (dict or string)

    If messages is None, sample data will be used for demonstration.
    """
    if not STREAMLIT_AVAILABLE:
        logger.error("Streamlit not available for CCU Message Monitor")
        return

    # Initialize session state BEFORE creating any widgets
    _initialize_session_state()

    st.header("📡 CCU Message Monitor")
    st.markdown("Monitor and filter CCU MQTT messages")

    # Use sample data if no messages provided
    if messages is None:
        messages = _get_sample_messages()

    if not messages:
        st.info("No messages to display")
        return

    # Prepare dataframe with cached preprocessing
    df = _prepare_dataframe(messages)

    # Extract dynamic filter options from data
    available_topics = [ALL_OPTION] + sorted(df["topic"].unique().tolist())
    available_modules = [ALL_OPTION] + sorted([m for m in df["module_fts"].unique() if m])
    available_statuses = [ALL_OPTION] + sorted(df["detected_status"].unique().tolist())
    available_types = [ALL_OPTION] + sorted(df["type_display"].unique().tolist())

    # 5-Column Filter Bar
    st.subheader("🔍 Filters")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        topic_filter = st.selectbox(
            "Topic",
            options=available_topics,
            index=(
                available_topics.index(st.session_state.ccu_msg_topic_filter)
                if st.session_state.ccu_msg_topic_filter in available_topics
                else 0
            ),
            key="topic_filter_widget",
        )
        st.session_state.ccu_msg_topic_filter = topic_filter

    with col2:
        module_fts_filter = st.selectbox(
            "Module/FTS",
            options=available_modules,
            index=(
                available_modules.index(st.session_state.ccu_msg_module_fts_filter)
                if st.session_state.ccu_msg_module_fts_filter in available_modules
                else 0
            ),
            key="module_fts_filter_widget",
        )
        st.session_state.ccu_msg_module_fts_filter = module_fts_filter

    with col3:
        status_filter = st.selectbox(
            "Status",
            options=available_statuses,
            index=(
                available_statuses.index(st.session_state.ccu_msg_status_filter)
                if st.session_state.ccu_msg_status_filter in available_statuses
                else 0
            ),
            key="status_filter_widget",
        )
        st.session_state.ccu_msg_status_filter = status_filter

    with col4:
        type_filter = st.selectbox(
            "Type",
            options=available_types,
            index=(
                available_types.index(st.session_state.ccu_msg_type_filter)
                if st.session_state.ccu_msg_type_filter in available_types
                else 0
            ),
            key="type_filter_widget",
        )
        st.session_state.ccu_msg_type_filter = type_filter

    with col5:
        st.write("")  # Spacer for alignment
        col5a, col5b = st.columns(2)
        with col5a:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        with col5b:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.ccu_msg_topic_filter = ALL_OPTION
                st.session_state.ccu_msg_module_fts_filter = ALL_OPTION
                st.session_state.ccu_msg_status_filter = ALL_OPTION
                st.session_state.ccu_msg_type_filter = ALL_OPTION
                st.rerun()

    # Apply filters
    filtered_df = _apply_filters(df, topic_filter, module_fts_filter, status_filter, type_filter)

    # Display filter results
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} messages**")

    if len(filtered_df) == 0:
        st.warning("No messages match the current filters")
        return

    # Display table with selection
    st.subheader("📋 Messages")

    # Prepare display dataframe (without internal columns)
    display_df = filtered_df[["timestamp", "topic", "detected_status", "module_fts", "type_display"]].copy()
    display_df.columns = ["Timestamp", "Topic", "Status", "Module/FTS", "Type"]

    # Display dataframe with selection
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400,
    )

    # Row selector for payload display
    st.subheader("📦 Payload Viewer")

    row_index = st.number_input(
        "Select row to view payload (0-based index):",
        min_value=0,
        max_value=max(0, len(filtered_df) - 1),
        value=0 if len(filtered_df) > 0 else 0,
        step=1,
        key="row_selector",
    )

    if 0 <= row_index < len(filtered_df):
        selected_row = filtered_df.iloc[row_index]

        # Display selected message info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Topic", selected_row["topic"])
        with col2:
            st.metric("Status", selected_row["detected_status"])
        with col3:
            st.metric("Module/FTS", selected_row["module_fts"] or "N/A")

        # Display payload
        st.code(selected_row["payload_str"], language="json")

        # Copy button
        if st.button("📋 Copy Payload to Clipboard"):
            st.code(selected_row["payload_str"])
            st.success("Payload displayed above - use your browser's copy function")


def _get_sample_messages() -> List[Dict[str, Any]]:
    """Generate sample messages for testing."""
    import time

    base_time = time.time()

    messages = [
        {
            "timestamp": base_time - 300,
            "topic": "ccu/connection",
            "payload": {
                "timestamp": "2024-01-15T10:00:00Z",
                "component": "CCU-Main",
                "connected": True,
                "details": {"host": "localhost", "port": 1883},
            },
        },
        {
            "timestamp": base_time - 240,
            "topic": "ccu/status",
            "payload": {
                "timestamp": "2024-01-15T10:01:00Z",
                "module": "Bohrstation",
                "state": "running",
                "details": {"serial": "BS-001", "workpiece_id": "WP-12345"},
            },
        },
        {
            "timestamp": base_time - 180,
            "topic": "ccu/status",
            "payload": {
                "timestamp": "2024-01-15T10:02:00Z",
                "module": "Frässtation",
                "state": "idle",
                "details": {"serial": "FS-002", "maintenance_due": False},
            },
        },
        {
            "timestamp": base_time - 120,
            "topic": "ccu/control",
            "payload": {
                "timestamp": "2024-01-15T10:03:00Z",
                "command": "start",
                "target": "Bohrstation",
                "parameters": {"mode": "auto", "speed": 100},
            },
        },
        {
            "timestamp": base_time - 90,
            "topic": "ccu/status",
            "payload": {
                "timestamp": "2024-01-15T10:03:30Z",
                "module": "FTS-1",
                "state": "transporting",
                "details": {"from": "Bohrstation", "to": "Frässtation", "workpiece": "WP-12345"},
            },
        },
        {
            "timestamp": base_time - 60,
            "topic": "ccu/workflow/WF001",
            "payload": {
                "timestamp": "2024-01-15T10:04:00Z",
                "workflow_id": "WF001",
                "step": "drilling",
                "status": "completed",
                "data": {"duration": 45, "quality": "OK"},
            },
        },
        {
            "timestamp": base_time - 30,
            "topic": "ccu/state",
            "payload": {
                "timestamp": "2024-01-15T10:04:30Z",
                "status": "running",
                "active_workflows": 2,
                "connected_modules": 5,
            },
        },
        {
            "timestamp": base_time - 15,
            "topic": "ccu/status",
            "payload": {
                "timestamp": "2024-01-15T10:04:45Z",
                "module": "Montagestation",
                "state": "error",
                "details": {"error_code": "E001", "message": "Sensor malfunction"},
            },
        },
        {
            "timestamp": base_time - 5,
            "topic": "ccu/connection",
            "payload": {
                "timestamp": "2024-01-15T10:04:55Z",
                "component": "FTS-2",
                "connected": False,
                "details": {"reason": "timeout", "last_seen": "2024-01-15T10:03:00Z"},
            },
        },
        {
            "timestamp": base_time,
            "topic": "ccu/status",
            "payload": {
                "timestamp": "2024-01-15T10:05:00Z",
                "module": "Qualitätskontrolle",
                "state": "inspecting",
                "details": {"workpiece": "WP-12345", "progress": 75},
            },
        },
    ]

    return messages


# Main entry point for standalone testing
if __name__ == "__main__":
    if STREAMLIT_AVAILABLE:
        st.set_page_config(page_title="CCU Message Monitor", page_icon="📡", layout="wide")

        # Generate sample messages
        sample_messages = _get_sample_messages()

        # Render the component
        render_ccu_message_monitor(sample_messages)

        # Show instructions
        st.sidebar.header("ℹ️ Instructions")
        st.sidebar.markdown(
            """
        **CCU Message Monitor**

        This component displays and filters CCU MQTT messages.

        **Features:**
        - 5-column filter bar (Topic, Module/FTS, Status, Type, Actions)
        - Persistent filter settings
        - Row selector for payload inspection
        - Automatic status and module detection

        **Testing:**
        Run this file directly with:
        ```bash
        streamlit run omf2/ui/ccu/ccu_message_monitor/ccu_message_monitor_component.py
        ```

        **Filter Persistence:**
        Filters persist across refresh operations.
        Use the Clear button to reset all filters.
        """
        )
    else:
        print("Streamlit is not available. Install it with: pip install streamlit")
