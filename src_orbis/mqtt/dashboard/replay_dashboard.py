#!/usr/bin/env python3
"""
APS Replay Dashboard
Separates Dashboard für Session-Replay mit lesefreundlichen Anzeigen
"""
import json
import os
import sqlite3
import sys
import time

import pandas as pd
import streamlit as st

# Path correction
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_script_dir, "..", "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Import existing utilities
from src_orbis.mqtt.dashboard.config.topic_mapping import get_friendly_topic_name

# Page config
st.set_page_config(
    page_title="APS Replay Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Note: Auto-refresh can be disabled with: streamlit run replay_dashboard.py --server.runOnSave false


class ReplayDashboard:
    """Separate Replay Dashboard für Session-Analyse"""

    def __init__(self):
        self.sessions_dir = os.path.join(_project_root, "mqtt-data/sessions")

        # Module mapping for friendly names
        self.module_mapping = {
            "SVR3QA2098": "HBW (Hochregallager)",
            "SVR4H76449": "MILL (Fräse)",
            "SVR4H76530": "DRILL (Bohrer)",
            "SVR3QA0022": "AIQS (Qualitätsprüfung)",
            "SVR4H73275": "DPS (Warenein- und -ausgang)",
            "5iO4": "FTS (Fahrerloses Transportsystem)",
            "CHRG0": "CHARGING (Ladestation)",
        }

    def run(self):
        """Main dashboard function"""
        st.title("🎬 APS Replay Dashboard")
        st.markdown("**Session-Replay mit lesefreundlichen Anzeigen**")

        # Session selection
        self._show_session_selection()

        # Main layout: Left side controls, Right side production steps
        if "selected_session" in st.session_state and st.session_state.selected_session:
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("🎮 Replay Steuerung")
                self._show_replay_controls()

            with col2:
                st.subheader("🏭 Fertigungsschritte")
                self._show_production_workflow()

    def _show_session_selection(self):
        """Show session selection interface"""
        st.header("📁 Session-Auswahl")

        # Get available sessions
        available_sessions = self._get_available_sessions()

        if not available_sessions:
            st.warning("❌ Keine Sessions verfügbar. Starte eine Session über die Kommandozeile.")
            return

        # Session selection
        selected_session = st.selectbox(
            "Session auswählen:",
            available_sessions,
            format_func=lambda x: f"{x} ({self._get_session_info(x)})",
        )

        if selected_session:
            # Check if session changed
            session_changed = selected_session != st.session_state.get("selected_session", None)

            st.session_state.selected_session = selected_session

            # Load session data
            messages_df = self._load_session_messages(selected_session)
            if messages_df is not None:
                st.session_state.messages_df = messages_df

                # Reset replay state if session changed
                if session_changed:
                    st.session_state.replay_message_index = 0
                    st.session_state.replay_playing = False
                    st.session_state.replay_speed = 1.0

                st.success(f"✅ Session geladen: {selected_session} ({len(messages_df)} Nachrichten)")
            else:
                st.error(f"❌ Fehler beim Laden der Session: {selected_session}")

    def _get_available_sessions(self):
        """Get list of available sessions"""
        sessions = []
        if os.path.exists(self.sessions_dir):
            for file in os.listdir(self.sessions_dir):
                if file.endswith(".db") and "aps_persistent_traffic_" in file:
                    session_name = file.replace("aps_persistent_traffic_", "").replace(".db", "")
                    sessions.append(session_name)
        return sorted(sessions, reverse=True)

    def _get_session_info(self, session_name):
        """Get basic session information"""
        db_path = os.path.join(self.sessions_dir, f"aps_persistent_traffic_{session_name}.db")
        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT COUNT(*) as count FROM mqtt_messages", conn)
            count = df.iloc[0]["count"]
            conn.close()
            return f"{count} Nachrichten"
        except:
            return "Keine Daten"

    def _load_session_messages(self, session_name):
        """Load messages from session database"""
        try:
            db_path = os.path.join(self.sessions_dir, f"aps_persistent_traffic_{session_name}.db")

            if not os.path.exists(db_path):
                return None

            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
            conn.close()

            if df.empty:
                return None

            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            return df

        except Exception as e:
            st.error(f"Fehler beim Laden der Session: {e}")
            return None

    def _show_replay_controls(self):
        """Show replay controls for selected session"""
        messages_df = st.session_state.messages_df

        # Initialize replay state
        if "replay_message_index" not in st.session_state:
            st.session_state.replay_message_index = 0
        if "replay_playing" not in st.session_state:
            st.session_state.replay_playing = False
        if "replay_speed" not in st.session_state:
            st.session_state.replay_speed = 1.0

        # Speed control and verbose mode in one row
        col1, col2 = st.columns([1, 1])

        with col1:
            # Speed control
            speed_options = [
                0.5,
                1.0,
                2.0,
                5.0,
                10.0,
                999.0,
            ]  # 999.0 = as fast as possible
            speed_labels = ["0.5x", "1x", "2x", "5x", "10x", "Fast as possible"]

            speed_index = (
                speed_options.index(st.session_state.replay_speed)
                if st.session_state.replay_speed in speed_options
                else 1
            )
            selected_speed_index = st.selectbox(
                "Geschwindigkeit:",
                range(len(speed_options)),
                index=speed_index,
                format_func=lambda x: speed_labels[x],
            )
            st.session_state.replay_speed = speed_options[selected_speed_index]

        with col2:
            # Verbose mode toggle
            verbose_mode = st.checkbox("🔍 Verbose-Modus (Camera-Nachrichten anzeigen)", value=False)

        # Filter messages
        filtered_df = self._filter_messages(messages_df, verbose_mode)

        # Show filtered camera messages info
        if not verbose_mode:
            original_count = len(messages_df)
            camera_count = len(messages_df[messages_df["topic"].str.contains("j1/txt/1/i/cam", na=False)])
            if camera_count > 0:
                st.info(f"📷 {camera_count} Camera-Nachrichten ausgeblendet")

        if len(filtered_df) == 0:
            st.warning("Keine Nachrichten nach den aktuellen Filtern verfügbar.")
            return

        # Navigation controls
        self._show_navigation_controls(filtered_df)

        # Current message display
        self._show_current_message(filtered_df)

        # Note: Production workflow is now shown in the right column

    def _show_production_workflow(self):
        """Show production workflow steps with live updates."""
        if "messages_df" not in st.session_state or st.session_state.messages_df is None:
            st.info("Keine Session geladen.")
            return

        messages_df = st.session_state.messages_df

        # Filter camera messages for workflow analysis
        filtered_df = messages_df[~messages_df["topic"].str.contains("j1/txt/1/i/cam", na=False)]

        # Get current message index
        current_index = st.session_state.get("replay_message_index", 0)

        # Get messages up to current time
        messages_up_to_current = filtered_df.iloc[: current_index + 1]

        # Determine workpiece type from messages
        workpiece_type = self._determine_workpiece_type(messages_up_to_current)

        if workpiece_type:
            st.success(f"🎯 Workpiece-Typ erkannt: **{workpiece_type}**")

            # Get production steps for this workpiece type
            production_steps = self._get_production_steps_for_type(workpiece_type)

            # Update steps based on messages up to current time
            updated_steps = self._update_production_steps_from_messages(production_steps, messages_up_to_current)

            # Display production steps with status
            st.write("**📋 Fertigungsschritte:**")

            for step in updated_steps:
                # Status icon and text
                if step["status"] == "done":
                    status_icon = "✅"
                    status_text = "Erledigt"
                    text_style = "**"  # Bold for done
                elif step["status"] == "in_progress":
                    status_icon = "🔄"
                    status_text = "In Bearbeitung"
                    text_style = "**"  # Bold for in progress
                else:
                    status_icon = "⏳"
                    status_text = "Geplant"
                    text_style = ""  # Normal for planned

                # Display step with status at the end
                step_text = f"{status_icon} **Schritt {step['step']}:** {step['icon']} {step['action']}"

                if step["status"] == "planned":
                    # Use transparent text for planned steps
                    st.markdown(
                        f"<div style='opacity: 0.6;'>{step_text} | **{status_text}**</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(f"{step_text} | **{status_text}**")

                # Show progress indicator for current step
                if step["status"] == "in_progress":
                    st.progress(0.5)  # Show progress for current step
        else:
            st.warning("⚠️ Workpiece-Typ konnte nicht bestimmt werden.")
            st.info("💡 Starte das Replay, um den Workflow zu analysieren.")

    def _determine_workpiece_type(self, messages_df):
        """Determine workpiece type from order messages."""
        if messages_df.empty:
            return None

        # Look for order messages with workpiece type information
        order_messages = messages_df[messages_df["topic"].str.contains("order", na=False)]

        for _, message in order_messages.iterrows():
            try:
                payload = json.loads(message["payload"])
                if isinstance(payload, dict):
                    # Check for type field
                    if "type" in payload:
                        return payload["type"].upper()

                    # Check for workpiece information
                    if "workpiece" in payload and isinstance(payload["workpiece"], dict):
                        if "type" in payload["workpiece"]:
                            return payload["workpiece"]["type"].upper()
            except:
                continue

        return None

    def _filter_messages(self, messages_df, verbose_mode):
        """Filter messages based on user preferences"""
        df = messages_df.copy()

        # Filter camera messages unless verbose mode
        if not verbose_mode:
            df = df[~df["topic"].str.contains("j1/txt/1/i/cam", na=False)]

        return df

    def _show_navigation_controls(self, filtered_df):
        """Show navigation controls"""
        total_messages = len(filtered_df)

        # Navigation buttons
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if st.button("⏮️ Erste"):
                st.session_state.replay_message_index = 0
                st.session_state.replay_playing = False

        with col2:
            if st.button("◀️ Vorherige"):
                if st.session_state.replay_message_index > 0:
                    st.session_state.replay_message_index -= 1
                st.session_state.replay_playing = False

        with col3:
            play_button_text = "⏸️ Pause" if st.session_state.replay_playing else "▶️ Play"
            if st.button(play_button_text):
                st.session_state.replay_playing = not st.session_state.replay_playing

        with col4:
            if st.button("▶️ Nächste"):
                if st.session_state.replay_message_index < total_messages - 1:
                    st.session_state.replay_message_index += 1
                st.session_state.replay_playing = False

        with col5:
            if st.button("⏭️ Letzte"):
                st.session_state.replay_message_index = total_messages - 1
                st.session_state.replay_playing = False

        # Message slider
        message_index = st.slider(
            "Nachricht:",
            min_value=0,
            max_value=total_messages - 1,
            value=st.session_state.replay_message_index,
        )

        st.write(f"Nachricht {message_index + 1} von {total_messages}")

        # Update message index if changed by slider
        if message_index != st.session_state.replay_message_index:
            st.session_state.replay_message_index = message_index
            st.session_state.replay_playing = False  # Stop playing when manually navigating

        # Progress bar - only show if total_messages > 0
        if total_messages > 0:
            progress = (message_index + 1) / total_messages
            st.progress(min(1.0, max(0.0, progress)))  # Clamp to [0.0, 1.0]

        # Auto-play functionality
        if st.session_state.replay_playing:
            if st.session_state.replay_message_index < total_messages - 1:
                st.session_state.replay_message_index += 1
                # Handle "as fast as possible" speed
                if st.session_state.replay_speed >= 999.0:
                    st.rerun()  # No delay for maximum speed
                else:
                    time.sleep(1.0 / st.session_state.replay_speed)  # Adjustable speed
                    st.rerun()
            else:
                st.session_state.replay_playing = False

    def _show_current_message(self, filtered_df):
        """Show current message with friendly displays"""
        if len(filtered_df) == 0:
            return

        current_message = filtered_df.iloc[st.session_state.replay_message_index]

        st.subheader(f"📨 Aktuelle Nachricht ({st.session_state.replay_message_index + 1}/{len(filtered_df)})")

        # Message details with friendly names
        col1, col2 = st.columns([1, 2])

        with col1:
            st.write("**Zeitstempel:**")
            st.write(current_message["timestamp"].strftime("%Y-%m-%d %H:%M:%S"))

            st.write("**Topic:**")
            friendly_topic = get_friendly_topic_name(current_message["topic"])
            st.write(f"📡 {friendly_topic}")
            st.write(f"🔗 Original: `{current_message['topic']}`")

            # Extract module name if applicable
            module_name = self._extract_module_name(current_message["topic"])
            if module_name:
                st.write(f"🏭 Modul: {module_name}")

            # Check for production workflow information
            workflow_info = self._extract_workflow_info(current_message)
            if workflow_info:
                st.write("**🏭 Fertigungsschritte:**")
                st.write(workflow_info)

        with col2:
            st.write("**Payload:**")
            try:
                payload = json.loads(current_message["payload"])
                st.json(payload)
            except:
                st.code(
                    current_message["payload"][:500] + "..."
                    if len(current_message["payload"]) > 500
                    else current_message["payload"]
                )

    def _extract_module_name(self, topic):
        """Extract friendly module name from topic"""
        for module_id, friendly_name in self.module_mapping.items():
            if module_id in topic:
                return friendly_name
        return None

    def _extract_workflow_info(self, message):
        """Extract production workflow information from message"""
        try:
            payload = json.loads(message["payload"])
            topic = message["topic"]

            # Check for order messages with workflow information
            if "order" in topic.lower():
                if isinstance(payload, dict):
                    # Look for workflow/sequence information
                    workflow_info = []

                    # Check for orderId
                    if "orderId" in payload:
                        workflow_info.append(f"Order-ID: {payload['orderId'][:8]}...")

                    # Check for orderType
                    if "orderType" in payload:
                        workflow_info.append(f"Order-Type: {payload['orderType']}")

                    # Check for workpiece information
                    if "workpieceId" in payload:
                        workflow_info.append(f"Workpiece: {payload['workpieceId']}")

                    # Check for target modules or actions
                    if "targetModule" in payload:
                        module_name = self._extract_module_name(payload["targetModule"])
                        if module_name:
                            workflow_info.append(f"Target: {module_name}")
                        else:
                            workflow_info.append(f"Target: {payload['targetModule']}")

                    if "action" in payload:
                        workflow_info.append(f"Action: {payload['action']}")

                    # Check for sequence or steps information
                    if "sequence" in payload:
                        workflow_info.append(f"Sequence: {len(payload['sequence'])} steps")

                    if "steps" in payload:
                        workflow_info.append(f"Steps: {len(payload['steps'])} planned")

                    if "workflow" in payload:
                        workflow_info.append(f"Workflow: {payload['workflow']}")

                    # Check for status information
                    if "status" in payload:
                        workflow_info.append(f"Status: {payload['status']}")

                    if workflow_info:
                        return " | ".join(workflow_info)

            # Check for module state messages
            elif "module/v1/ff/" in topic and "/state" in topic:
                if isinstance(payload, dict):
                    state_info = []

                    if "state" in payload:
                        state_info.append(f"State: {payload['state']}")

                    if "moduleId" in payload:
                        module_name = self._extract_module_name(payload["moduleId"])
                        if module_name:
                            state_info.append(f"Module: {module_name}")

                    if "orderId" in payload:
                        state_info.append(f"Order: {payload['orderId'][:8]}...")

                    if "actionId" in payload:
                        state_info.append(f"Action: {payload['actionId']}")

                    if state_info:
                        return " | ".join(state_info)

            # Check for FTS messages
            elif "fts/" in topic:
                if isinstance(payload, dict):
                    fts_info = []

                    if "position" in payload:
                        fts_info.append(f"Position: {payload['position']}")

                    if "target" in payload:
                        fts_info.append(f"Target: {payload['target']}")

                    if "status" in payload:
                        fts_info.append(f"Status: {payload['status']}")

                    if fts_info:
                        return " | ".join(fts_info)

            # Check for CCU messages
            elif "ccu/" in topic:
                if isinstance(payload, dict):
                    ccu_info = []

                    if "orderId" in payload:
                        ccu_info.append(f"Order: {payload['orderId'][:8]}...")

                    if "actionId" in payload:
                        ccu_info.append(f"Action: {payload['actionId']}")

                    if "status" in payload:
                        ccu_info.append(f"Status: {payload['status']}")

                    if ccu_info:
                        return " | ".join(ccu_info)

        except:
            pass

        return None

    def _show_production_workflow_analysis(self, filtered_df):
        """Show production workflow analysis based on messages"""
        st.subheader("🏭 Fertigungsschritte-Analyse")

        # Get messages up to current point
        messages_up_to_current = filtered_df.iloc[: st.session_state.replay_message_index + 1]

        # Show detected production steps (simplified, no order message analysis)
        detected_steps = self._detect_production_steps(messages_up_to_current)
        if detected_steps:
            st.write("**🎯 Erkannte Fertigungsschritte:**")
            for step in detected_steps:
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.write(f"**{step['step']:2d}.**")
                with col2:
                    st.write(f"{step['icon']} {step['action']}")
                with col3:
                    if step["status"] == "done":
                        st.success("✅ done")
                    elif step["status"] == "in_progress":
                        st.warning("🔄 in progress")
                    else:
                        st.info("⏳ planned")
        else:
            st.info(
                "Keine Fertigungsschritte erkannt. Navigiere durch die Nachrichten, um Order-Informationen zu finden."
            )

    def _extract_workflow_steps(self, payload):
        """Extract workflow steps from payload"""
        steps = []

        # Check for sequence array
        if "sequence" in payload and isinstance(payload["sequence"], list):
            for step in payload["sequence"]:
                if isinstance(step, dict):
                    if "action" in step:
                        steps.append(f"Action: {step['action']}")
                    if "module" in step:
                        module_name = self._extract_module_name(step["module"])
                        if module_name:
                            steps.append(f"Module: {module_name}")
                    if "target" in step:
                        steps.append(f"Target: {step['target']}")

        # Check for steps array
        if "steps" in payload and isinstance(payload["steps"], list):
            for step in payload["steps"]:
                if isinstance(step, dict):
                    if "action" in step:
                        steps.append(f"Action: {step['action']}")
                    if "module" in step:
                        module_name = self._extract_module_name(step["module"])
                        if module_name:
                            steps.append(f"Module: {module_name}")

        # Check for workflow object
        if "workflow" in payload and isinstance(payload["workflow"], dict):
            workflow = payload["workflow"]
            if "actions" in workflow:
                for action in workflow["actions"]:
                    if isinstance(action, dict):
                        if "type" in action:
                            steps.append(f"Action: {action['type']}")
                        if "target" in action:
                            steps.append(f"Target: {action['target']}")

        return steps

    def _detect_production_steps(self, messages_df):
        """Detect production steps from messages"""
        steps = []

        # Look for order messages to determine type
        order_messages = messages_df[messages_df["topic"].str.contains("order", na=False)]
        order_type = None

        for _, order_msg in order_messages.iterrows():
            try:
                payload = json.loads(order_msg["payload"])
                if "type" in payload:
                    order_type = payload["type"]
                    break
            except:
                continue

        if order_type:
            # Get base steps for this order type
            base_steps = self._get_production_steps_for_type(order_type)

            # Update status based on messages
            for step in base_steps:
                step["status"] = self._determine_step_status(step, messages_df)
                steps.append(step)

        return steps

    def _determine_step_status(self, step, messages_df):
        """Determine status of a production step based on messages"""
        module = step["module"]

        # Check for module activity
        if module == "FTS":
            fts_messages = messages_df[messages_df["topic"].str.contains("fts/", na=False)]
            if len(fts_messages) > 0:
                return "done"

        elif module == "HBW":
            hbw_messages = messages_df[messages_df["topic"].str.contains("SVR3QA2098", na=False)]
            if len(hbw_messages) > 0:
                return "done"

        elif module == "MILL":
            mill_messages = messages_df[messages_df["topic"].str.contains("SVR4H76449", na=False)]
            if len(mill_messages) > 0:
                return "done"

        elif module == "DRILL":
            drill_messages = messages_df[messages_df["topic"].str.contains("SVR4H76530", na=False)]
            if len(drill_messages) > 0:
                return "done"

        elif module == "AIQS":
            aiqs_messages = messages_df[messages_df["topic"].str.contains("SVR3QA0022", na=False)]
            if len(aiqs_messages) > 0:
                return "done"

        elif module == "DPS":
            dps_messages = messages_df[messages_df["topic"].str.contains("SVR4H73275", na=False)]
            if len(dps_messages) > 0:
                return "done"

        return "planned"

    def _get_production_steps_for_type(self, workpiece_type):
        """Get production steps for a specific workpiece type"""
        if workpiece_type == "BLUE":
            return [
                {
                    "step": 1,
                    "module": "HBW",
                    "action": "HBW: PICK(DRILL)",
                    "icon": "🏗️",
                    "status": "planned",
                },
                {
                    "step": 2,
                    "module": "HBW",
                    "action": "HBW: DROP(DRILL)",
                    "icon": "🏗️",
                    "status": "planned",
                },
                {
                    "step": 3,
                    "module": "FTS",
                    "action": "FTS → Bohrer",
                    "icon": "🚚",
                    "status": "planned",
                },
                {
                    "step": 4,
                    "module": "DRILL",
                    "action": "Bohrer: PICK(DRILL)",
                    "icon": "🔧",
                    "status": "planned",
                },
                {
                    "step": 5,
                    "module": "DRILL",
                    "action": "Bohrer: DRILL(DRILL)",
                    "icon": "🔧",
                    "status": "planned",
                },
                {
                    "step": 6,
                    "module": "DRILL",
                    "action": "Bohrer: DROP(DRILL)",
                    "icon": "🔧",
                    "status": "planned",
                },
                {
                    "step": 7,
                    "module": "FTS",
                    "action": "FTS → Hochregallager",
                    "icon": "🚚",
                    "status": "planned",
                },
                {
                    "step": 8,
                    "module": "HBW",
                    "action": "HBW: PICK(MILL)",
                    "icon": "🏗️",
                    "status": "planned",
                },
                {
                    "step": 9,
                    "module": "HBW",
                    "action": "HBW: DROP(MILL)",
                    "icon": "🏗️",
                    "status": "planned",
                },
                {
                    "step": 10,
                    "module": "FTS",
                    "action": "FTS → Fräse",
                    "icon": "🚚",
                    "status": "planned",
                },
                {
                    "step": 11,
                    "module": "MILL",
                    "action": "Fräse: PICK(MILL)",
                    "icon": "⚙️",
                    "status": "planned",
                },
                {
                    "step": 12,
                    "module": "MILL",
                    "action": "Fräse: MILL(MILL)",
                    "icon": "⚙️",
                    "status": "planned",
                },
                {
                    "step": 13,
                    "module": "MILL",
                    "action": "Fräse: DROP(MILL)",
                    "icon": "⚙️",
                    "status": "planned",
                },
                {
                    "step": 14,
                    "module": "FTS",
                    "action": "FTS → KI-Qualitätssicherung",
                    "icon": "🚚",
                    "status": "planned",
                },
                {
                    "step": 15,
                    "module": "AIQS",
                    "action": "AIQS: PICK",
                    "icon": "🔍",
                    "status": "planned",
                },
                {
                    "step": 16,
                    "module": "AIQS",
                    "action": "KI-Qualitätssicherung: Qualitätsprüfung",
                    "icon": "🔍",
                    "status": "planned",
                },
                {
                    "step": 17,
                    "module": "AIQS",
                    "action": "AIQS: DROP",
                    "icon": "🔍",
                    "status": "planned",
                },
                {
                    "step": 18,
                    "module": "FTS",
                    "action": "FTS → Warenein- und -ausgang",
                    "icon": "🚚",
                    "status": "planned",
                },
                {
                    "step": 19,
                    "module": "DPS",
                    "action": "Warenein- und -ausgang: DROP",
                    "icon": "📦",
                    "status": "planned",
                },
            ]
        elif workpiece_type == "RED":
            return [
                {
                    "step": 1,
                    "module": "HBW",
                    "action": "HBW: PICK(MILL)",
                    "icon": "🏗️",
                    "status": "planned",
                },
                {
                    "step": 2,
                    "module": "HBW",
                    "action": "HBW: DROP(MILL)",
                    "icon": "🏗️",
                    "status": "planned",
                },
                {
                    "step": 3,
                    "module": "FTS",
                    "action": "FTS → Fräse",
                    "icon": "🚚",
                    "status": "planned",
                },
                {
                    "step": 4,
                    "module": "MILL",
                    "action": "Fräse: PICK(MILL)",
                    "icon": "⚙️",
                    "status": "planned",
                },
                {
                    "step": 5,
                    "module": "MILL",
                    "action": "Fräse: MILL(MILL)",
                    "icon": "⚙️",
                    "status": "planned",
                },
                {
                    "step": 6,
                    "module": "MILL",
                    "action": "Fräse: DROP(MILL)",
                    "icon": "⚙️",
                    "status": "planned",
                },
                {
                    "step": 7,
                    "module": "FTS",
                    "action": "FTS → KI-Qualitätssicherung",
                    "icon": "🚚",
                    "status": "planned",
                },
                {
                    "step": 8,
                    "module": "AIQS",
                    "action": "AIQS: PICK",
                    "icon": "🔍",
                    "status": "planned",
                },
                {
                    "step": 9,
                    "module": "AIQS",
                    "action": "KI-Qualitätssicherung: Qualitätsprüfung",
                    "icon": "🔍",
                    "status": "planned",
                },
                {
                    "step": 10,
                    "module": "AIQS",
                    "action": "AIQS: DROP",
                    "icon": "🔍",
                    "status": "planned",
                },
                {
                    "step": 11,
                    "module": "FTS",
                    "action": "FTS → Warenein- und -ausgang",
                    "icon": "🚚",
                    "status": "planned",
                },
                {
                    "step": 12,
                    "module": "DPS",
                    "action": "Warenein- und -ausgang: DROP",
                    "icon": "📦",
                    "status": "planned",
                },
            ]
        elif workpiece_type == "WHITE":
            return [
                {
                    "step": 1,
                    "module": "HBW",
                    "action": "HBW: PICK(DRILL)",
                    "icon": "🏗️",
                    "status": "planned",
                },
                {
                    "step": 2,
                    "module": "HBW",
                    "action": "HBW: DROP(DRILL)",
                    "icon": "🏗️",
                    "status": "planned",
                },
                {
                    "step": 3,
                    "module": "FTS",
                    "action": "FTS → Bohrer",
                    "icon": "🚚",
                    "status": "planned",
                },
                {
                    "step": 4,
                    "module": "DRILL",
                    "action": "Bohrer: PICK(DRILL)",
                    "icon": "🔧",
                    "status": "planned",
                },
                {
                    "step": 5,
                    "module": "DRILL",
                    "action": "Bohrer: DRILL(DRILL)",
                    "icon": "🔧",
                    "status": "planned",
                },
                {
                    "step": 6,
                    "module": "DRILL",
                    "action": "Bohrer: DROP(DRILL)",
                    "icon": "🔧",
                    "status": "planned",
                },
                {
                    "step": 7,
                    "module": "FTS",
                    "action": "FTS → KI-Qualitätssicherung",
                    "icon": "🚚",
                    "status": "planned",
                },
                {
                    "step": 8,
                    "module": "AIQS",
                    "action": "AIQS: PICK",
                    "icon": "🔍",
                    "status": "planned",
                },
                {
                    "step": 9,
                    "module": "AIQS",
                    "action": "KI-Qualitätssicherung: Qualitätsprüfung",
                    "icon": "🔍",
                    "status": "planned",
                },
                {
                    "step": 10,
                    "module": "AIQS",
                    "action": "AIQS: DROP",
                    "icon": "🔍",
                    "status": "planned",
                },
                {
                    "step": 11,
                    "module": "FTS",
                    "action": "FTS → Warenein- und -ausgang",
                    "icon": "🚚",
                    "status": "planned",
                },
                {
                    "step": 12,
                    "module": "DPS",
                    "action": "Warenein- und -ausgang: DROP",
                    "icon": "📦",
                    "status": "planned",
                },
            ]
        else:
            return []

    def _update_production_steps_from_messages(self, steps, messages_df, current_time=None):
        """Update production steps status based on specific message patterns."""
        if messages_df.empty:
            return steps

        # Create a copy of steps to avoid modifying the original
        updated_steps = steps.copy()

        # Track which steps are completed
        completed_steps = set()

        # Analyze messages to determine step completion
        for _, message in messages_df.iterrows():
            topic = message["topic"]
            payload = message["payload"]

            try:
                payload_data = json.loads(payload) if isinstance(payload, str) else payload
            except:
                payload_data = {}

            # HBW PICK and DROP (SVR3QA2098) - for all workflows
            if "SVR3QA2098" in topic:
                if "/pick" in topic.lower() or (
                    "action" in payload_data and "pick" in str(payload_data.get("action", "")).lower()
                ):
                    completed_steps.add(1)  # HBW PICK (all workflows)
                    completed_steps.add(8)  # HBW PICK (BLUE - second cycle)
                elif "/drop" in topic.lower() or (
                    "action" in payload_data and "drop" in str(payload_data.get("action", "")).lower()
                ):
                    completed_steps.add(2)  # HBW DROP (all workflows)
                    completed_steps.add(9)  # HBW DROP (BLUE - second cycle)

            # MILL PICK, MILL, DROP (SVR4H76449) - for RED and BLUE workflows
            elif "SVR4H76449" in topic:
                if "/pick" in topic.lower() or (
                    "action" in payload_data and "pick" in str(payload_data.get("action", "")).lower()
                ):
                    completed_steps.add(4)  # MILL PICK (RED)
                    completed_steps.add(11)  # MILL PICK (BLUE)
                elif "/mill" in topic.lower() or (
                    "action" in payload_data and "mill" in str(payload_data.get("action", "")).lower()
                ):
                    completed_steps.add(5)  # MILL MILL (RED)
                    completed_steps.add(12)  # MILL MILL (BLUE)
                elif "/drop" in topic.lower() or (
                    "action" in payload_data and "drop" in str(payload_data.get("action", "")).lower()
                ):
                    completed_steps.add(6)  # MILL DROP (RED)
                    completed_steps.add(13)  # MILL DROP (BLUE)

            # DRILL PICK, DRILL, DROP (SVR4H76530) - for WHITE and BLUE workflows
            elif "SVR4H76530" in topic:
                if "/pick" in topic.lower() or (
                    "action" in payload_data and "pick" in str(payload_data.get("action", "")).lower()
                ):
                    completed_steps.add(4)  # DRILL PICK (WHITE)
                    completed_steps.add(4)  # DRILL PICK (BLUE)
                elif "/drill" in topic.lower() or (
                    "action" in payload_data and "drill" in str(payload_data.get("action", "")).lower()
                ):
                    completed_steps.add(5)  # DRILL DRILL (WHITE)
                    completed_steps.add(5)  # DRILL DRILL (BLUE)
                elif "/drop" in topic.lower() or (
                    "action" in payload_data and "drop" in str(payload_data.get("action", "")).lower()
                ):
                    completed_steps.add(6)  # DRILL DROP (WHITE)
                    completed_steps.add(6)  # DRILL DROP (BLUE)

            # AIQS PICK and DROP (SVR3QA0022) - for RED, WHITE, and BLUE workflows
            elif "SVR3QA0022" in topic:
                if "/pick" in topic.lower() or (
                    "action" in payload_data and "pick" in str(payload_data.get("action", "")).lower()
                ):
                    completed_steps.add(8)  # AIQS PICK (RED/WHITE)
                    completed_steps.add(15)  # AIQS PICK (BLUE)
                elif "/drop" in topic.lower() or (
                    "action" in payload_data and "drop" in str(payload_data.get("action", "")).lower()
                ):
                    completed_steps.add(10)  # AIQS DROP (RED/WHITE)
                    completed_steps.add(17)  # AIQS DROP (BLUE)

            # DPS DROP (SVR4H73275) - for RED, WHITE, and BLUE workflows
            elif "SVR4H73275" in topic:
                if "/drop" in topic.lower() or (
                    "action" in payload_data and "drop" in str(payload_data.get("action", "")).lower()
                ):
                    completed_steps.add(12)  # DPS DROP (RED/WHITE)
                    completed_steps.add(19)  # DPS DROP (BLUE)

            # FTS transport steps (fts/ or 5iO4)
            elif "fts/" in topic or "5iO4" in topic:
                # Check for specific transport targets
                if "mill" in topic.lower() or "svr4h76449" in topic.lower():
                    completed_steps.add(3)  # FTS → Fräse (RED)
                    completed_steps.add(10)  # FTS → Fräse (BLUE)
                elif "drill" in topic.lower() or "svr4h76530" in topic.lower():
                    completed_steps.add(3)  # FTS → Bohrer (WHITE)
                    completed_steps.add(7)  # FTS → Bohrer (BLUE)
                elif "aiqs" in topic.lower() or "svr3qa0022" in topic.lower():
                    completed_steps.add(7)  # FTS → KI-Qualitätssicherung (RED/WHITE)
                    completed_steps.add(14)  # FTS → KI-Qualitätssicherung (BLUE)
                elif "dps" in topic.lower() or "svr4h73275" in topic.lower():
                    completed_steps.add(11)  # FTS → Warenein- und -ausgang (RED/WHITE)
                    completed_steps.add(18)  # FTS → Warenein- und -ausgang (BLUE)

        # Update step statuses
        for step in updated_steps:
            step_num = step["step"]

            if step_num in completed_steps:
                step["status"] = "done"
            elif step_num == max(completed_steps) + 1 if completed_steps else 1:
                step["status"] = "in_progress"
            else:
                step["status"] = "planned"

        return updated_steps


def main():
    """Main function"""
    dashboard = ReplayDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
