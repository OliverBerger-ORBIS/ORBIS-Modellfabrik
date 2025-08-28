#!/usr/bin/env python3
"""
APS Interactive Dashboard
Orbis Development - Interaktives Dashboard für MQTT-Datenanalyse
"""
import os
import sys
import glob
import json
import time
import sqlite3
import yaml
import uuid
import pandas as pd
import streamlit as st
import plotly.express as px
import paho.mqtt.client as mqtt
from datetime import datetime

# --- Start of Path Correction ---
# This block ensures that the script can find the 'src_orbis' package,
# regardless of how the script is run.

# Get the absolute path of the directory containing this script.
_script_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate up to the project root directory (which contains 'src_orbis').
# .../src_orbis/mqtt/dashboard -> .../src_orbis/mqtt -> .../src_orbis -> .../
_project_root = os.path.abspath(os.path.join(_script_dir, "..", "..", ".."))

# Add the project root to the Python path if it's not already there.
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
# --- End of Path Correction ---


# Now that the path is correct, we can use absolute imports from 'src_orbis'.
from src_orbis.mqtt.dashboard.utils.data_handling import extract_module_info
from src_orbis.mqtt.dashboard.components.filters import create_filters

# Template Message Manager imports
from src_orbis.mqtt.tools.template_message_manager import TemplateMessageManager
from src_orbis.mqtt.dashboard.template_control import TemplateControlDashboard

# Module Mapping imports
from src_orbis.mqtt.tools.module_manager import get_module_manager

# Topic Manager imports
from src_orbis.mqtt.tools.topic_manager import get_topic_manager

# Node-RED Analysis imports
from src_orbis.mqtt.tools.node_red_message_analyzer import NodeRedMessageAnalyzer

# APS Analysis imports
from src_orbis.mqtt.dashboard.components.aps_analysis import APSAnalysis



# Topic Mapping imports (using TopicManager)
from src_orbis.mqtt.tools.topic_manager import get_topic_manager

# Icon Configuration imports
from src_orbis.mqtt.dashboard.config.icon_config import (
    get_module_icon,
    get_logo_path,
    get_module_icon_path,
    get_status_icon,
    MODULE_ICONS,
    STATUS_ICONS
)

# Page config
st.set_page_config(
    page_title="ORBIS Modellfabrik Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_broker_config():
    """Loads MQTT broker configurations from the YAML file."""
    config_path = os.path.join(
        os.path.dirname(__file__), "../../../config/credentials.example.yml"
    )
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config.get("mqtt_brokers", [])
    except FileNotFoundError:
        st.error(f"Konfigurationsdatei nicht gefunden: {config_path}")
        return []
    except Exception as e:
        st.error(f"Fehler beim Laden der Broker-Konfiguration: {e}")
        return []


class APSDashboard:
    """APS Interactive Dashboard"""

    def __init__(self, db_file, verbose_mode=False):
        self.db_file = db_file
        self.conn = None
        self.verbose_mode = verbose_mode

        # Initialize Template Message Manager
        self.template_manager = TemplateMessageManager()
        self.template_control = TemplateControlDashboard(self.template_manager)
        self.aps_analysis = APSAnalysis()
        
        # Initialize Module Mapping Utilities
        self.module_mapping = get_module_manager()
        
        # Initialize Topic Manager
        self.topic_manager = get_topic_manager()
        
        # Initialize Message Template Manager (YAML-based, no analysis at startup)
        try:
            from ..tools.message_template_manager import get_message_template_manager
            self.message_template_manager = get_message_template_manager()
        except ImportError:
            # Fallback for direct execution
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))
            from message_template_manager import get_message_template_manager
            self.message_template_manager = get_message_template_manager()

        # Load broker configurations
        self.broker_configs = load_broker_config()

        # MQTT Client setup
        self.mqtt_client = None
        self.mqtt_connected = False
        self.mqtt_messages_sent = []
        self.mqtt_responses = []

        # MQTT Configuration - fixed for APS Modellfabrik
        self.mqtt_broker = "192.168.0.100"
        self.mqtt_port = 1883
        self.mqtt_username = "default"
        self.mqtt_password = "default"

    # set_broker method removed - using fixed APS Modellfabrik configuration

    def connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            return True
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()

    def setup_mqtt_client(self):
        """Setup MQTT client for sending messages"""
        try:
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            if self.mqtt_username and self.mqtt_password:
                self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)

            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            self.mqtt_client.on_message = self._on_mqtt_message

            return True
        except Exception as e:
            st.error(f"MQTT Client Setup Error: {e}")
            return False

    def connect_mqtt(self):
        """Connect to MQTT broker"""
        if self.mqtt_connected:
            return True

        if not self.mqtt_client:
            if not self.setup_mqtt_client():
                return False

        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()

            # Wait for connection
            time.sleep(1)  # Give a second for the connection to establish
            
            # Subscribe to CCU responses for Template Message Manager
            if self.mqtt_connected and hasattr(self, 'template_manager'):
                self.mqtt_client.subscribe("ccu/order/response", qos=1)
                self.mqtt_client.subscribe("ccu/order/status", qos=1)
                self.mqtt_client.subscribe("module/+/order/response", qos=1)
            
            return self.mqtt_connected
        except Exception as e:
            st.error(f"MQTT Connection Error: {e}")
            return False

    def disconnect_mqtt(self):
        """Disconnect from MQTT broker"""
        if self.mqtt_client and self.mqtt_connected:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            except Exception as e:
                st.warning(f"MQTT Disconnect Warning: {e}")

    def _on_mqtt_connect(self, client, userdata, flags, rc, properties=None):
        """MQTT connection callback (VERSION2 API)"""
        if rc == 0:
            self.mqtt_connected = True
            # Subscribe to module state topics to receive responses
            all_modules = self.module_mapping.get_all_modules()
            for module_id, module_info in all_modules.items():
                state_topic = f"module/v1/ff/{module_info['id']}/state"
                client.subscribe(state_topic, qos=1)
                print(f"Subscribed to: {state_topic}")
            # This callback is in a different thread, so we can't use st.success directly
            # We'll rely on the main thread to show connection status
        else:
            self.mqtt_connected = False

    def _on_mqtt_disconnect(self, client, userdata, rc, properties=None, reasonCode=None):
        """MQTT disconnection callback (VERSION2 API)"""
        self.mqtt_connected = False
        # This callback is in a different thread, we can't use st.info directly

    def _on_mqtt_message(self, client, userdata, msg, properties=None):
        """MQTT message callback for responses (VERSION2 API)"""
        try:
            payload = json.loads(msg.payload.decode())
            response_info = {
                "timestamp": datetime.now(),
                "topic": msg.topic,
                "payload": payload,
                "qos": msg.qos,
            }
            self.mqtt_responses.append(response_info)
            
            # Handle CCU responses for Template Message Manager
            if msg.topic == "ccu/order/response" and hasattr(self, 'template_manager'):
                try:
                    # Extract order information from CCU response
                    if isinstance(payload, dict):
                        order_id = payload.get('orderId')
                        color = payload.get('type')
                        workpiece_id = payload.get('workpieceId')
                        
                        if order_id and color and workpiece_id:
                            # Handle CCU response in template manager
                            self.template_manager.handle_ccu_response(
                                order_id, color, workpiece_id, payload
                            )
                except Exception as e:
                    print(f"Template Manager CCU Response Error: {e}")
                    
        except Exception as e:
            # Can't use st.warning here due to thread context
            print(f"MQTT Response Parse Error: {e}")

    def send_mqtt_message_direct(self, topic, message):
        """Send MQTT message directly"""
        # Use session state for MQTT connection status
        if not st.session_state.get("mqtt_connected", False):
            st.warning("Keine MQTT-Verbindung. Bitte verbinden Sie sich zuerst.")
            return False, "MQTT nicht verbunden"

        # Use stored dashboard instance for MQTT client
        dashboard = st.session_state.get("mqtt_dashboard")
        if not dashboard or not dashboard.mqtt_client:
            st.warning("MQTT-Client nicht verfügbar. Bitte verbinden Sie sich erneut.")
            return False, "MQTT-Client nicht verfügbar"

        try:
            if isinstance(message, dict):
                message_json = json.dumps(message)
            else:
                message_json = str(message)

            result = dashboard.mqtt_client.publish(topic, message_json, qos=1)

            sent_info = {
                "timestamp": datetime.now(),
                "topic": topic,
                "message": message,
                "result": result.rc,
            }
            # Store in dashboard instance
            if hasattr(dashboard, 'mqtt_messages_sent'):
                dashboard.mqtt_messages_sent.append(sent_info)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                return True, "Nachricht erfolgreich gesendet"
            else:
                return False, f"Send Error: {result.rc}"

        except Exception as e:
            return False, f"Exception: {e}"

    def load_data(self):
        """Load all data from database"""
        try:
            query = """
                SELECT timestamp, topic, payload, qos, retain, 
                       message_type, module_type, serial_number, status,
                       session_label, process_label
                FROM mqtt_messages
                ORDER BY timestamp
            """

            df = pd.read_sql_query(query, self.conn)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["date"] = df["timestamp"].dt.date
            df["hour"] = df["timestamp"].dt.hour
            df["minute"] = df["timestamp"].dt.minute

            # Extract module information from topics
            df = extract_module_info(df)

            # Filter camera topics if not in verbose mode
            original_count = len(df)
            if not self.verbose_mode:
                df = df[~df["topic"].str.contains("j1/txt/1/i/cam", na=False)]

            filtered_count = len(df)
            st.session_state.filtered_camera_messages = original_count - filtered_count

            return df

        except Exception as e:
            st.error(f"Error loading data: {e}")
            return None

    def extract_module_info(self, df):
        """Extract module information from topics and payloads"""
        try:
            # Extract module type and serial number from topics
            def extract_module_from_topic(topic):
                topic_lower = topic.lower()

                # Module patterns in topics - more specific patterns first

                if "svr3qa0022" in topic_lower:
                    return "HBW", "SVR3QA0022"
                elif "svr4h73275" in topic_lower:
                    return "DPS", "SVR4H73275"
                elif "svr4h76530" in topic_lower:
                    return "AIQS", "SVR4H76530"
                elif "svr3qa2098" in topic_lower:
                    return "MILL", "SVR3QA2098"
                elif "svr4h76449" in topic_lower:
                    return "DRILL", "SVR4H76449"
                elif "5io4" in topic_lower:
                    return "FTS", "5IO4"
                elif "ccu" in topic_lower:
                    return "CCU", "CCU"
                elif "txt" in topic_lower or "j1" in topic_lower:
                    return "TXT", "TXT"
                elif "hbw" in topic_lower:
                    return "HBW", "unknown"
                elif "dps" in topic_lower:
                    return "DPS", "unknown"
                elif "aiqs" in topic_lower:
                    return "AIQS", "unknown"
                elif "mill" in topic_lower:
                    return "MILL", "unknown"
                elif "drill" in topic_lower:
                    return "DRILL", "unknown"
                elif "oven" in topic_lower:
                    return "OVEN", "unknown"
                elif "fts" in topic_lower:
                    return "FTS", "unknown"
                else:
                    return "unknown", "unknown"

            # Rename session labels to new format
            def rename_session_label(session_label):
                if "bestellung_blau" in session_label.lower():
                    return "Order_cloud_blue_ok"
                elif "bestellung_rot" in session_label.lower():
                    return "Order_cloud_red_ok"
                elif "bestellung_gelb" in session_label.lower():
                    return "Order_cloud_yellow_ok"
                elif "order_local" in session_label.lower():
                    return "Order_local_unknown_ok"
                elif "wareneingang" in session_label.lower():
                    return "Wareneingang_manual_ok"
                elif "test" in session_label.lower():
                    return "Test_unknown_ok"
                else:
                    return session_label

            # Extract status from payloads
            def extract_status_from_payload(payload):
                try:
                    if pd.isna(payload) or payload == "":
                        return "unknown"

                    # Try JSON first
                    try:
                        data = json.loads(payload)

                        # Check for status fields in JSON
                        if isinstance(data, dict):
                            if "available" in data:
                                return str(data["available"])
                            elif "status" in data:
                                return str(data["status"])
                            elif "state" in data:
                                return str(data["state"])
                            elif "connected" in data:
                                return (
                                    "CONNECTED" if data["connected"] else "DISCONNECTED"
                                )
                            elif "charging" in data:
                                return (
                                    "CHARGING" if data["charging"] else "NOT_CHARGING"
                                )
                            elif "type" in data:
                                return str(data["type"])
                            elif "subType" in data:
                                return str(data["subType"])
                            elif "messageType" in data:
                                return str(data["messageType"])
                            elif "modules" in data:
                                return "MODULE_LIST"
                            elif "transports" in data:
                                return "TRANSPORT_LIST"

                        return "unknown"

                    except json.JSONDecodeError:
                        # Handle non-JSON payloads
                        payload_str = str(payload).lower()

                        # Check for common status patterns in text
                        if "ready" in payload_str:
                            return "READY"
                        elif "busy" in payload_str:
                            return "BUSY"
                        elif "connected" in payload_str:
                            return "CONNECTED"
                        elif "disconnected" in payload_str:
                            return "DISCONNECTED"
                        elif "charging" in payload_str:
                            return "CHARGING"
                        elif "error" in payload_str:
                            return "ERROR"
                        elif "ok" in payload_str:
                            return "OK"
                        elif "true" in payload_str:
                            return "TRUE"
                        elif "false" in payload_str:
                            return "FALSE"
                        elif "data:image" in payload_str:
                            return "CAMERA_DATA"
                        elif len(payload_str) < 50:  # Short text payloads
                            return payload_str.upper()

                        return "unknown"

                except Exception as e:
                    return "unknown"

            # Apply extraction
            module_info = df["topic"].apply(extract_module_from_topic)
            df["module_type_extracted"] = [info[0] for info in module_info]
            df["serial_number_extracted"] = [info[1] for info in module_info]
            df["status_extracted"] = df["payload"].apply(extract_status_from_payload)

            # Use extracted values if original are unknown
            df.loc[df["module_type"] == "unknown", "module_type"] = df.loc[
                df["module_type"] == "unknown", "module_type_extracted"
            ]
            df.loc[df["serial_number"] == "unknown", "serial_number"] = df.loc[
                df["serial_number"] == "unknown", "serial_number_extracted"
            ]
            df.loc[df["status"] == "unknown", "status"] = df.loc[
                df["status"] == "unknown", "status_extracted"
            ]

            # Rename session labels
            df["session_label"] = df["session_label"].apply(rename_session_label)

            # Clean up
            df = df.drop(
                [
                    "module_type_extracted",
                    "serial_number_extracted",
                    "status_extracted",
                ],
                axis=1,
            )

            return df

        except Exception as e:
            st.warning(f"Module extraction warning: {e}")
            return df

    def create_filters(self, df, single_session_mode=False):
        """Create filters for APS analysis using the new filter component"""
        return create_filters(df, single_session_mode)

    def show_overview(self, df):
        """Show overview statistics"""
        st.header("📊 Übersicht")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Gesamt-Nachrichten", f"{len(df):,}")

        with col2:
            unique_topics = df["topic"].nunique()
            st.metric("Unique Topics", f"{unique_topics:,}")

        with col3:
            if not df.empty:
                duration = df["timestamp"].max() - df["timestamp"].min()
                st.metric("Zeitraum", f"{duration}")

        with col4:
            sessions = df["session_label"].nunique()
            st.metric("Sessions", f"{sessions:,}")

        # Process distribution
        col1, col2 = st.columns(2)

        with col1:
            process_counts = df["process_label"].value_counts()
            fig = px.pie(
                values=process_counts.values,
                names=process_counts.index,
                title="Nachrichten nach Prozess-Typ",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            module_counts = df["module_type"].value_counts()
            fig = px.pie(
                values=module_counts.values,
                names=module_counts.index,
                title="Nachrichten nach Modul-Typ",
            )
            st.plotly_chart(fig, use_container_width=True)

    def show_timeline(self, df):
        """Show message timeline"""
        st.header("⏰ Nachrichten-Timeline")

        if not df.empty:
            # Resample to minute intervals
            df_timeline = (
                df.set_index("timestamp").resample("1min").size().reset_index()
            )
            df_timeline.columns = ["timestamp", "message_count"]

            fig = px.line(
                df_timeline,
                x="timestamp",
                y="message_count",
                title="Nachrichten pro Minute",
            )
            fig.update_layout(xaxis_title="Zeit", yaxis_title="Nachrichten/Minute")
            st.plotly_chart(fig, use_container_width=True)

    def show_message_table(self, df):
        """Show filtered message table"""
        st.header("📋 Nachrichten-Tabelle")

        if not df.empty:
            # Select columns to display
            display_columns = [
                "timestamp",
                "topic",
                "module_type",
                "serial_number",
                "status",
                "process_label",
                "session_label",
            ]
            available_columns = [col for col in display_columns if col in df.columns]

            # Create display DataFrame with friendly topic names
            df_display = df[available_columns].copy()
            df_display["friendly_topic"] = df_display["topic"].apply(lambda x: self.topic_manager.get_friendly_name(x))
            
            # Reorder columns to show friendly_topic first
            display_cols = ["timestamp", "friendly_topic"] + [col for col in available_columns if col != "timestamp"]

            # Show table with selected columns
            st.dataframe(
                df_display[display_cols].head(1000),  # Limit to 1000 rows
                use_container_width=True,
            )

            # Show total count
            st.info(f"Zeige {min(len(df_display), 1000)} von {len(df):,} Nachrichten")
            
            # Topic mapping info
            total_topics = df["topic"].nunique()
            mapped_topics = len([t for t in df["topic"].unique() if self.topic_manager.get_friendly_name(t) != t])
            unmapped_topics = total_topics - mapped_topics
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gesamt Topics", total_topics)
            with col2:
                st.metric("Mapped Topics", mapped_topics)
            with col3:
                st.metric("Unmapped Topics", unmapped_topics)
            

        else:
            st.warning("Keine Nachrichten mit den gewählten Filtern gefunden.")

    def show_topic_analysis(self, df):
        """Show topic analysis"""
        st.header("📡 Topic-Analyse")

        if not df.empty:
            # Create analysis DataFrame with friendly topic names
            df_analysis = df[["topic"]].copy()
            df_analysis["friendly_topic"] = df_analysis["topic"].apply(lambda x: self.topic_manager.get_friendly_name(x))
            
            col1, col2 = st.columns(2)

            with col1:
                # Top topics with friendly names
                topic_counts = df_analysis["friendly_topic"].value_counts().head(10)
                fig = px.bar(
                    x=topic_counts.values,
                    y=topic_counts.index,
                    orientation="h",
                    title="Top 10 Topics (benutzerfreundlich)",
                )
                fig.update_layout(xaxis_title="Anzahl", yaxis_title="Topic")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Topic comparison
                st.subheader("Topic-Vergleich")
                
                # Show both original and friendly names
                topic_comparison = df_analysis[["topic", "friendly_topic"]].drop_duplicates().head(10)
                st.dataframe(topic_comparison, use_container_width=True)
                
                # Topic statistics
                total_topics = df["topic"].nunique()
                mapped_topics = df_analysis["friendly_topic"].nunique()
                unmapped_count = len([t for t in df["topic"].unique() if self.topic_manager.get_friendly_name(t) == t])
                
                st.metric("Gesamt Topics", total_topics)
                st.metric("Mapped Topics", total_topics - unmapped_count)
                st.metric("Unmapped Topics", unmapped_count)
            
            # Topic distribution with friendly names
            st.subheader("Topic-Verteilung (benutzerfreundlich)")
            
            # Group by friendly topic names
            friendly_topic_counts = df_analysis["friendly_topic"].value_counts()
            
            col3, col4 = st.columns(2)
            
            with col3:
                # Pie chart of friendly topics
                fig = px.pie(
                    values=friendly_topic_counts.values,
                    names=friendly_topic_counts.index,
                    title="Topic-Verteilung",
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col4:
                # Topic table with both names
                topic_summary = df_analysis.groupby(["topic", "friendly_topic"]).size().reset_index(name="count")
                topic_summary = topic_summary.sort_values("count", ascending=False)
                st.dataframe(topic_summary.head(15), use_container_width=True)

    def show_status_analysis(self, df):
        """Show status analysis"""
        st.header("📊 Status-Analyse")

        if not df.empty:
            col1, col2 = st.columns(2)

            with col1:
                status_counts = df["status"].value_counts().head(10)
                fig = px.bar(
                    x=status_counts.values,
                    y=status_counts.index,
                    orientation="h",
                    title="Top 10 Status-Werte",
                )
                fig.update_layout(xaxis_title="Anzahl", yaxis_title="Status")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Status over time
                if len(df) > 1:
                    status_timeline = (
                        df.groupby(["timestamp", "status"])
                        .size()
                        .reset_index(name="count")
                    )
                    fig = px.scatter(
                        status_timeline,
                        x="timestamp",
                        y="status",
                        size="count",
                        title="Status über Zeit",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Payload type analysis
            st.subheader("📦 Payload-Typ Analyse")

            def analyze_payload_type(payload):
                try:
                    if pd.isna(payload) or payload == "":
                        return "EMPTY"
                    elif payload.startswith("{"):
                        return "JSON"
                    elif payload.startswith("data:image"):
                        return "CAMERA_IMAGE"
                    elif len(str(payload)) < 50:
                        return "SHORT_TEXT"
                    else:
                        return "LONG_TEXT"
                except:
                    return "UNKNOWN"

            df["payload_type"] = df["payload"].apply(analyze_payload_type)
            payload_type_counts = df["payload_type"].value_counts()

            col3, col4 = st.columns(2)

            with col3:
                fig = px.pie(
                    values=payload_type_counts.values,
                    names=payload_type_counts.index,
                    title="Payload-Typen Verteilung",
                )
                st.plotly_chart(fig, use_container_width=True)

            with col4:
                st.subheader("Payload-Typ Details")
                st.dataframe(
                    payload_type_counts.reset_index().rename(
                        columns={"index": "Typ", "payload_type": "Anzahl"}
                    ),
                    use_container_width=True,
                )

    def show_payload_analysis(self, df):
        """Show payload analysis"""
        st.header("📦 Payload-Analyse")

        if not df.empty:
            # Create payload DataFrame with friendly topic names
            df_payload = df[["topic", "payload", "timestamp"]].copy()
            df_payload["friendly_topic"] = df_payload["topic"].apply(lambda x: self.topic_manager.get_friendly_name(x))
            
            # Payload overview
            st.subheader("📊 Payload Übersicht")
            
            # Payload statistics
            total_messages = len(df_payload)
            messages_with_payload = len(df_payload[df_payload["payload"].notna() & (df_payload["payload"] != "")])
            json_payloads = 0
            text_payloads = 0
            
            for payload in df_payload["payload"].dropna():
                if payload:
                    try:
                        json.loads(payload)
                        json_payloads += 1
                    except:
                        text_payloads += 1
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Gesamt Nachrichten", total_messages)
            with col2:
                st.metric("Mit Payload", messages_with_payload)
            with col3:
                st.metric("JSON Payloads", json_payloads)
            with col4:
                st.metric("Text Payloads", text_payloads)
            
            st.markdown("---")
            
            # Payload details with meta information
            st.subheader("📄 Payload Details mit Meta-Informationen")
            
            # Show first 50 messages with payload details
            for idx, row in df_payload.head(50).iterrows():
                if pd.notna(row.get('payload')) and row['payload']:
                    with st.expander(f"📄 Nachricht #{idx + 1} - {row['friendly_topic']}", expanded=False):
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.markdown("**Meta-Informationen:**")
                            st.markdown(f"• **ID:** #{idx + 1}")
                            st.markdown(f"• **Timestamp:** {row['timestamp']}")
                            st.markdown(f"• **Topic:** `{row['topic']}`")
                            st.markdown(f"• **Friendly Topic:** {row['friendly_topic']}")
                            
                            if pd.notna(row.get('module_type')):
                                st.markdown(f"• **Module:** {row['module_type']}")
                            if pd.notna(row.get('serial_number')):
                                st.markdown(f"• **Serial:** {row['serial_number']}")
                            if pd.notna(row.get('status')):
                                st.markdown(f"• **Status:** {row['status']}")
                            if pd.notna(row.get('process_label')):
                                st.markdown(f"• **Process:** {row['process_label']}")
                            if pd.notna(row.get('session_label')):
                                st.markdown(f"• **Session:** {row['session_label']}")
                            
                            # Payload type
                            try:
                                json.loads(row['payload'])
                                st.markdown("• **Payload Type:** JSON")
                            except:
                                st.markdown("• **Payload Type:** Text")
                        
                        with col2:
                            st.markdown("**Payload:**")
                            try:
                                # Try to parse JSON payload
                                payload_data = json.loads(row['payload'])
                                st.json(payload_data)
                            except:
                                # Show as text if not JSON
                                st.text_area("Payload (Text):", str(row['payload']), height=200, key=f"payload_text_{idx}")
                
                # Show separator for messages without payload
                else:
                    with st.expander(f"📄 Nachricht #{idx + 1} - {row['friendly_topic']} (Kein Payload)", expanded=False):
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.markdown("**Meta-Informationen:**")
                            st.markdown(f"• **ID:** #{idx + 1}")
                            st.markdown(f"• **Timestamp:** {row['timestamp']}")
                            st.markdown(f"• **Topic:** `{row['topic']}`")
                            st.markdown(f"• **Friendly Topic:** {row['friendly_topic']}")
                            
                            if pd.notna(row.get('module_type')):
                                st.markdown(f"• **Module:** {row['module_type']}")
                            if pd.notna(row.get('serial_number')):
                                st.markdown(f"• **Serial:** {row['serial_number']}")
                            if pd.notna(row.get('status')):
                                st.markdown(f"• **Status:** {row['status']}")
                            if pd.notna(row.get('process_label')):
                                st.markdown(f"• **Process:** {row['process_label']}")
                            if pd.notna(row.get('session_label')):
                                st.markdown(f"• **Session:** {row['session_label']}")
                            
                            st.markdown("• **Payload Type:** Kein Payload")
                        
                        with col2:
                            st.info("Kein Payload vorhanden")
            
            # Show info if more messages exist
            if len(df) > 50:
                st.info(f"Zeige die ersten 50 von {len(df):,} Nachrichten. Verwende die Filter oben, um spezifische Nachrichten zu finden.")
            
            st.markdown("---")
            
            # JSON Payload Analysis
            st.subheader("🔍 JSON Payload Struktur-Analyse")
            
            # Try to extract JSON data
            json_payloads = []
            for payload in df["payload"].dropna():
                try:
                    data = json.loads(payload)
                    json_payloads.append(data)
                except:
                    continue

            if json_payloads:
                # Show sample payload
                sample_payload = json_payloads[0]
                st.markdown("**Beispiel JSON Payload:**")
                st.json(sample_payload)

                # Extract common fields
                common_fields = {}
                for payload in json_payloads[:100]:  # Analyze first 100
                    if isinstance(payload, dict):
                        for key in payload.keys():
                            if key not in common_fields:
                                common_fields[key] = 0
                            common_fields[key] += 1
                    elif isinstance(payload, list):
                        # Handle list payloads
                        common_fields["list_length"] = (
                            common_fields.get("list_length", 0) + 1
                        )
                        if len(payload) > 0:
                            # Analyze first item if it's a dict
                            if isinstance(payload[0], dict):
                                for key in payload[0].keys():
                                    if key not in common_fields:
                                        common_fields[key] = 0
                                    common_fields[key] += 1

                if common_fields:
                    st.markdown("**Häufige Felder in JSON Payloads:**")
                    field_df = pd.DataFrame(
                        list(common_fields.items()), columns=["Feld", "Anzahl"]
                    )
                    st.dataframe(field_df.sort_values("Anzahl", ascending=False))
            else:
                st.info("Keine JSON Payloads gefunden.")
        else:
            st.warning("Keine Nachrichten mit den gewählten Filtern gefunden.")

    def show_session_analysis(self, df):
        """Show session analysis"""
        st.header("🏷️ Session-Analyse")

        # Session information section
        st.subheader("📝 Session-Information")

        st.info(
            """
        **💡 Session Recording:**
        
        ```bash
        python src_orbis/mqtt/loggers/aps_session_logger.py --session-label wareneingang-rot --auto-start
        ```
        
        **Beispiele:** `wareneingang-rot`, `auftrag-blau`, `ai-not-ok-rot`
        """
        )

        st.markdown("---")

        # Session analysis
        st.subheader("📊 Session-Analyse")

        if not df.empty:
            col1, col2 = st.columns(2)

            with col1:
                # Session distribution
                session_counts = df["session_label"].value_counts()
                fig = px.pie(
                    values=session_counts.values,
                    names=session_counts.index,
                    title="Nachrichten nach Session",
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Session breakdown
                st.subheader("Session-Details")

                # Parse session labels
                session_info = []
                for session_label in df["session_label"].unique():
                    parts = session_label.split("_")
                    if len(parts) >= 3:
                        order_type = parts[0]  # Order, Wareneingang, Test
                        source = parts[1]  # cloud, local, manual
                        color = parts[2]  # blue, red, yellow, unknown
                        status = parts[3] if len(parts) > 3 else "ok"  # ok, nok

                        session_info.append(
                            {
                                "Session": session_label,
                                "Typ": order_type,
                                "Quelle": source,
                                "Farbe": color,
                                "Status": status,
                                "Nachrichten": len(
                                    df[df["session_label"] == session_label]
                                ),
                            }
                        )

                if session_info:
                    session_df = pd.DataFrame(session_info)
                    st.dataframe(session_df, use_container_width=True)
                else:
                    st.info("Keine strukturierten Session-Labels gefunden.")

            # Session timeline
            st.subheader("Session-Timeline")
            if len(df) > 1:
                session_timeline = (
                    df.groupby(["timestamp", "session_label"])
                    .size()
                    .reset_index(name="count")
                )
                fig = px.scatter(
                    session_timeline,
                    x="timestamp",
                    y="session_label",
                    size="count",
                    title="Sessions über Zeit",
                )
                st.plotly_chart(fig, use_container_width=True)

    def show_mqtt_control(self):
        """Show MQTT control interface"""
        st.header("🎮 MQTT Module Control")
        st.markdown("Steuere APS-Module über funktionierende MQTT-Nachrichten")
        
        # MQTT status info (connection managed in sidebar)
        if not st.session_state.get("mqtt_connected", False):
            st.warning("⚠️ MQTT-Verbindung erforderlich - verwende die Sidebar zum Verbinden")

        # MQTT Control Interface
        st.subheader("📤 MQTT Message Control")

        # Control method selection
        control_method = st.selectbox(
            "Steuerungsmethode:",
            ["Overview", "Bestellung", "Template Message"],
        )

        if control_method == "Overview":
            self.show_module_control_rows()
        elif control_method == "Bestellung":
            self.show_order_control_combined()
        elif control_method == "Template Message":
            self.show_template_control()

    def show_order_control_combined(self):
        """Show combined order control with both trigger and HBW status options"""
        st.header("📋 Bestellung")
        
        if not st.session_state.get("mqtt_connected", False):
            st.warning("⚠️ MQTT-Verbindung erforderlich")
            return
        
        # Two sections in one method
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚀 Bestellung-Trigger")
            st.markdown("**Direkte Bestellung ohne HBW-Status-Prüfung**")
            
            # Order buttons
            col1a, col1b, col1c = st.columns(3)
            
            with col1a:
                if st.button("🔴 ROT", type="primary", use_container_width=True):
                    self.send_browser_order("RED")
                    st.success("✅ ROT-Bestellung gesendet!")
            
            with col1b:
                if st.button("⚪ WEISS", type="primary", use_container_width=True):
                    self.send_browser_order("WHITE")
                    st.success("✅ WEISS-Bestellung gesendet!")
            
            with col1c:
                if st.button("🔵 BLAU", type="primary", use_container_width=True):
                    self.send_browser_order("BLUE")
                    st.success("✅ BLAU-Bestellung gesendet!")
        
        with col2:
            st.subheader("📦 Bestellung (mit HBW-Status)")
            st.markdown("**Bestellung nur für verfügbare Werkstücke**")
            
            # Get HBW status
            hbw_status = self.get_hbw_status()
            
            if hbw_status:
                # Display available workpieces
                available_workpieces = hbw_status.get('available_workpieces', [])
                
                if available_workpieces:
                    st.success(f"✅ {len(available_workpieces)} Werkstücke verfügbar")
                    
                    # Show available workpieces
                    for workpiece in available_workpieces:
                        color = workpiece.get('color', 'UNKNOWN')
                        position = workpiece.get('position', 'UNKNOWN')
                        st.write(f"📦 {color} - Position: {position}")
                    
                    # Order buttons for available workpieces
                    col2a, col2b, col2c = st.columns(3)
                    
                    colors = ['RED', 'WHITE', 'BLUE']
                    cols = [col2a, col2b, col2c]
                    
                    for i, color in enumerate(colors):
                        with cols[i]:
                            # Check if color is available
                            is_available = any(w.get('color') == color for w in available_workpieces)
                            
                            if is_available:
                                if st.button(f"{color} bestellen", type="primary", use_container_width=True):
                                    self.send_browser_order(color)
                                    st.success(f"✅ {color}-Bestellung gesendet!")
                            else:
                                st.button(f"{color} bestellen", disabled=True, use_container_width=True)
                                st.caption(f"❌ {color} nicht verfügbar")
                else:
                    st.warning("⚠️ Keine Werkstücke im HBW verfügbar")
            else:
                st.error("❌ HBW-Status konnte nicht abgerufen werden")
                st.info("💡 Verwende 'Bestellung-Trigger' für direkte Bestellung")
        
        # Order format info (shared)
        st.subheader("📋 Bestellungs-Format")
        st.info("""
        **Browser-Order-Format:**
        - **Topic:** `/j1/txt/1/f/o/order`
        - **Payload:** `{"type": "COLOR", "ts": "timestamp"}`
        - **CCU orchestriert** automatisch alle Module
        """)
        
        # Recent orders
        if hasattr(self, 'recent_orders') and self.recent_orders:
            st.subheader("📋 Letzte Bestellungen")
            for order in self.recent_orders[-5:]:
                st.write(f"🕐 {order['timestamp']} - {order['type']}")



    def send_browser_order(self, color):
        """Send browser order in the correct format"""
        if not st.session_state.get("mqtt_connected", False):
            st.error("❌ MQTT-Verbindung erforderlich")
            return
        
        if not hasattr(self, 'mqtt_client') or not self.mqtt_client:
            st.error("❌ MQTT-Client nicht verfügbar")
            return
        
        try:
            # Create order message
            order_data = {
                "type": color,
                "ts": datetime.now().isoformat() + "Z"
            }
            
            # Send order
            topic = "/j1/txt/1/f/o/order"
            result = self.mqtt_client.publish(topic, json.dumps(order_data))
            
            if result.rc == 0:
                # Store recent order
                if not hasattr(self, 'recent_orders'):
                    self.recent_orders = []
                
                self.recent_orders.append({
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'type': color,
                    'topic': topic,
                    'payload': order_data
                })
                
                st.success(f"✅ {color}-Bestellung erfolgreich gesendet!")
            else:
                st.error(f"❌ Fehler beim Senden der Bestellung: {result.rc}")
                
        except Exception as e:
            st.error(f"❌ Fehler: {e}")

    def get_hbw_status(self):
        """Get HBW status and available workpieces"""
        if not st.session_state.get("mqtt_connected", False):
            return None
        
        if not hasattr(self, 'mqtt_client') or not self.mqtt_client:
            return None
        
        try:
            # This is a simplified version - in practice you'd need to:
            # 1. Subscribe to HBW state messages
            # 2. Request factsheet from HBW
            # 3. Parse the response for available workpieces
            
            # For now, return a mock status
            # TODO: Implement real HBW status checking
            return {
                'available_workpieces': [
                    {'color': 'RED', 'position': 'B1'},
                    {'color': 'WHITE', 'position': 'B2'},
                    {'color': 'BLUE', 'position': 'B3'}
                ]
            }
            
        except Exception as e:
            st.error(f"❌ Fehler beim Abrufen des HBW-Status: {e}")
            return None

    def show_template_control(self):
        """Show template-based MQTT control with Template Message Manager"""
        st.header("🎯 Template Message Manager")
        st.markdown("**Programmatische APS-Steuerung mit 9 Workflow Templates**")

        # Set MQTT client for template manager
        if self.mqtt_client:
            self.template_manager.set_mqtt_client(self.mqtt_client)
            self.template_control.template_manager = self.template_manager

        # Template Control Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🚀 Wareneingang Control", 
            "📊 Order Tracking", 
            "📚 Template Library",
            "🧪 Template Testing",
            "⚙️ Custom Templates"
        ])

        with tab1:
            self.template_control.show_wareneingang_control()

        with tab2:
            self.template_control.show_order_tracking()

        with tab3:
            self.template_control.show_template_library()

        with tab4:
            self.template_control.show_template_testing()

        with tab5:
            self.template_control.show_custom_template_creator()





    def show_module_overview_dashboard(self, df):
        """Show comprehensive module overview dashboard"""
        # Header with Factory Reset button
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.header("🏭 ORBIS Modellfabrik Overview")
        st.markdown("Übersicht aller APS-Module mit Status und Steuerungsmöglichkeiten")
        
        with col2:
            st.markdown("")  # Spacer
            st.markdown("")  # Spacer
            
            # Factory Reset Icon Button
            if st.session_state.get("mqtt_connected", False):
                if st.button("🔄", help="Fabrik zurücksetzen", use_container_width=True):
                    st.session_state.show_reset_modal = True
            else:
                st.button("🔄", help="MQTT-Verbindung erforderlich", disabled=True, use_container_width=True)

        st.markdown("---")

        # Sub-navigation for overview
        overview_tab1, overview_tab2, overview_tab3, overview_tab4 = st.tabs([
            "📋 Module Status",
            "📦 Bestellung",
            "📋 Bestellung Rohware",
            "📊 Lagerbestand"
        ])

        with overview_tab1:
            # Module table
            st.subheader("📋 Module Status")

        # Create module table data
        module_table_data = []
        all_modules = self.module_mapping.get_all_modules()
        for module_id, module_info in all_modules.items():
            # Get availability status
            recent_messages = df[df["topic"].str.contains(module_info["id"], na=False)]
            availability_status = self.extract_availability_status(
                recent_messages, module_info["id"]
            )

            # Connection status - use session state for consistency
            if st.session_state.get("mqtt_connected", False):
                connection_status = f"{get_status_icon('available')} Connected"
            else:
                connection_status = f"{get_status_icon('offline')} Disconnected"

            # Activity status with enhanced icons using new function
            if availability_status:
                activity_display = self.get_enhanced_status_display(availability_status, module_info["type"])
            elif len(recent_messages) > 0:
                # If we have recent messages but no specific status, show "Active"
                activity_display = f"{get_status_icon('available')} Active"
            else:
                # No recent messages at all
                activity_display = f"{get_status_icon('offline')} No Data"

            # Get module icon (use emoji for table display)
            # For table display, prefer emoji over file paths
            module_name = module_info.get('name', module_id)
            module_key_upper = module_name.upper()
            icon_from_function = get_module_icon(module_key_upper)
            
            # If it's a file path, fallback to emoji from MODULE_ICONS
            if icon_from_function and ('/' in icon_from_function or '\\' in icon_from_function):
                icon_display = MODULE_ICONS.get(module_key_upper, "❓")
            else:
                icon_display = icon_from_function
            
            # Get first available IP address from ip_addresses list
            ip_addresses = module_info.get('ip_addresses', [])
            current_ip = ip_addresses[0] if ip_addresses else "Unknown"
            
            module_table_data.append(
                {
                    "Name": f"{icon_display} {module_info.get('name', module_id)}",
                    "ID": module_info["id"],
                    "Type": module_info.get("type", "Unknown"),
                    "IP": current_ip,  # First available IP address (ToBeDone: from MQTT messages)
                    "Connected": connection_status,
                    "Activity Status": activity_display,
                    "Recent Messages": len(recent_messages),
                }
            )

        # Create DataFrame and display table
        module_df = pd.DataFrame(module_table_data)
        st.dataframe(
            module_df,
            use_container_width=True,
            column_config={
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "ID": st.column_config.TextColumn("ID", width="medium"),
                "Recent Messages": st.column_config.NumberColumn(
                    "Recent Messages", width="small"
                ),
            },
        )

        with overview_tab2:
            st.subheader("📦 Bestellung")
            st.info("💡 Bestellungs-Funktionalität wird hier implementiert")
            st.markdown("""
            **Geplante Features:**
            - Bestellungs-Übersicht
            - Bestellungs-Status
            - Bestellungs-Historie
            """)

        with overview_tab3:
            st.subheader("📋 Bestellung Rohware")
            st.info("💡 Rohware-Bestellungs-Funktionalität wird hier implementiert")
            st.markdown("""
            **Geplante Features:**
            - Rohware-Bestellungs-Übersicht
            - Rohware-Status
            - Rohware-Lieferungen
            """)

        with overview_tab4:
            st.subheader("📊 Lagerbestand")
            st.info("💡 Lagerbestands-Funktionalität wird hier implementiert")
            st.markdown("""
            **Geplante Features:**
            - Lagerbestands-Übersicht
            - Werkstück-Positionen
            - Lagerbestands-Historie
            """)

        # Factory Reset Modal
        if st.session_state.get("show_reset_modal", False):
            # Compact reset dialog
            with st.container():
                st.markdown("---")
                
                # Compact header with close button
                col_header1, col_header2 = st.columns([4, 1])
                with col_header1:
                    st.markdown("**🏭 Fabrik zurücksetzen**")
                with col_header2:
                    if st.button("❌", help="Schließen", key="close_reset_modal"):
                        st.session_state.show_reset_modal = False
                        st.rerun()
                
                # Compact warning
                st.warning("⚠️ **WARNUNG:** Diese Aktion setzt die gesamte Fabrik zurück!")
                
                # Compact options
                reset_with_storage = st.checkbox("Mit Storage zurücksetzen (HBW-Storage löschen)", value=False, 
                                               help="Aktivieren um alle HBW-Storage Daten zu löschen")
                
                # Compact buttons
                col_btn1, col_btn2, col_spacer = st.columns([1, 1, 2])
                
                with col_btn1:
                    if st.button("✅ JA - Zurücksetzen", type="primary", use_container_width=True, key="confirm_reset"):
                        self.send_factory_reset(reset_with_storage)
                        st.session_state.show_reset_modal = False
                        st.rerun()
                
                with col_btn2:
                    if st.button("❌ NEIN - Abbrechen", use_container_width=True, key="cancel_reset"):
                        st.session_state.show_reset_modal = False
                        st.rerun()
                
                with col_spacer:
                    st.markdown("")
                    st.markdown("*Klicke 'JA' um die Fabrik zurückzusetzen*")
                
                st.markdown("---")

        # Module control moved to MQTT Control tab
        st.info("🎮 **Module Control** ist jetzt im **MQTT Control** Tab verfügbar")

    def show_module_row(self, module_id, module_info, df):
        """Show individual module as a row"""
        with st.container():
            # Module header with border
            st.markdown(
                f"""
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin: 5px 0; background-color: #f8f9fa;">
                <h4>{module_info['icon']} {module_info['name']}</h4>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Module information in columns
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 3, 2])

            with col1:
                st.markdown(f"**ID:** `{module_info['id']}`")
                st.markdown(f"**Typ:** {module_info['type']}")

            with col2:
                st.markdown(f"**IP:** {module_info['ip']}")
                # Connection status
                if self.mqtt_connected:
                    st.success("🟢 Online")
                else:
                    st.error("🔴 Offline")

            with col3:
                # Availability status (based on recent messages)
                recent_messages = df[
                    df["topic"].str.contains(module_info["id"], na=False)
                ]
                if len(recent_messages) > 0:
                    # Try to extract availability status from recent messages
                    availability_status = self.extract_availability_status(
                        recent_messages, module_info["id"]
                    )
                    if availability_status:
                        if availability_status == "AVAILABLE":
                            st.success("🟢 Available")
                        elif availability_status == "BUSY":
                            st.warning("🟡 Busy")
                        elif availability_status == "BLOCKED":
                            st.error("🔴 Blocked")
                        else:
                            st.info(f"⚪ {availability_status}")
                    else:
                        # Fallback to time-based status
                        latest_time = recent_messages["timestamp"].max()
                        time_diff = (pd.Timestamp.now() - latest_time).total_seconds()

                        if time_diff < 60:  # Last message within 1 minute
                            st.success("🟢 Available")
                        elif time_diff < 300:  # Last message within 5 minutes
                            st.warning("🟡 Busy")
                        else:
                            st.info("🔵 Inactive")
                else:
                    st.info("⚪ No Data")

            with col4:
                # Commands
                st.markdown("**Verfügbare Befehle:**")
                for command in module_info["commands"]:
                    if st.button(
                        f"▶️ {command}",
                        key=f"cmd_{module_id}_{command}",
                        use_container_width=True,
                    ):
                        self.send_module_command(module_id, command)

            with col5:
                # Recent activity count
                if len(recent_messages) > 0:
                    st.metric("Letzte Aktivität", f"{len(recent_messages)} Nachrichten")
                    with st.expander("📊 Details"):
                        st.dataframe(
                            recent_messages[["timestamp", "topic", "status"]].head(3),
                            use_container_width=True,
                        )
                else:
                    st.info("Keine Aktivität")

            st.markdown("---")

    def show_module_card(self, module_id, module_info, df):
        """Show individual module card (legacy method)"""
        with st.container():
            st.markdown(
                f"""
            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0;">
                <h3>{module_info['icon']} {module_info['name']}</h3>
                <p><strong>ID:</strong> <code>{module_info['id']}</code></p>
                <p><strong>Typ:</strong> {module_info['type']}</p>
                <p><strong>IP:</strong> {module_info['ip']}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Connection status
            if self.mqtt_connected:
                st.success("🟢 Online")
            else:
                st.error("🔴 Offline")

            # Availability status (based on recent messages)
            recent_messages = df[df["topic"].str.contains(module_info["id"], na=False)]
            if len(recent_messages) > 0:
                latest_time = recent_messages["timestamp"].max()
                time_diff = (pd.Timestamp.now() - latest_time).total_seconds()

                if time_diff < 60:  # Last message within 1 minute
                    st.success("🟢 Verfügbar")
                elif time_diff < 300:  # Last message within 5 minutes
                    st.warning("🟡 Aktiv")
                else:
                    st.info("🔵 Inaktiv")
            else:
                st.info("⚪ Keine Daten")

            # Commands
            st.markdown("**Verfügbare Befehle:**")
            for command in module_info["commands"]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"• {command}")
                with col2:
                    if st.button(f"▶️", key=f"cmd_{module_id}_{command}"):
                        self.send_module_command(module_id, command)

            # Recent activity
            if len(recent_messages) > 0:
                with st.expander(
                    f"📊 Letzte Aktivität ({len(recent_messages)} Nachrichten)"
                ):
                    st.dataframe(
                        recent_messages[["timestamp", "topic", "status"]].head(5),
                        use_container_width=True,
                    )

    def _extract_module_name_from_topic(self, topic):
        """Extract module name from MQTT topic"""
        # Extract serial number from topic
        if '/ff/' in topic:
            serial = topic.split('/ff/')[1].split('/')[0]
            # Map serial to module name using ModuleManager
            all_modules = self.module_mapping.get_all_modules()
            for module_id, module_info in all_modules.items():
                if module_info['id'] == serial:
                    return module_info['name']
        return "Unknown"

    def send_module_command(self, module_id, command):
        """Send command to specific module"""
        try:
            if not self.mqtt_connected:
                if not self.connect_mqtt():
                    st.error("MQTT-Verbindung fehlgeschlagen")
                    return

            # Get module info
            all_modules = self.module_mapping.get_all_modules()
            module_info = all_modules.get(module_id)
            if not module_info:
                st.error(f"Modul {module_id} nicht gefunden")
                return

            # Create message based on module type
            if module_id == "FTS":
                # Special handling for FTS commands
                message = self.create_fts_message(command)
                topic = f"module/v1/ff/{module_info['id']}/order"
            else:
                # Standard APS module commands - simplified since message_library is removed
                message = {
                    "serialNumber": module_info["id"],
                    "orderId": str(uuid.uuid4()),
                    "orderUpdateId": 1,
                    "action": {
                        "id": str(uuid.uuid4()),
                        "command": command,
                        "metadata": {
                            "priority": "NORMAL",
                            "timeout": 300
                        }
                    }
                }
                topic = f"module/v1/ff/{module_info['id']}/order"

            # Send message
            success, result_message = self.send_mqtt_message_direct(topic, message)

            if success:
                st.success(f"✅ Befehl gesendet: {module_id} - {command}")
                st.info(f"📡 Topic: {topic}")
            else:
                st.error(f"❌ Fehler: {result_message}")

        except Exception as e:
            st.error(f"❌ Fehler beim Senden: {e}")

    def send_drill_sequence_command(self, module_id, command, workpiece_color, nfc_code):
        """Send DRILL sequence command with proper orderUpdateId management"""
        try:
            if not self.mqtt_connected:
                if not self.connect_mqtt():
                    st.error("MQTT-Verbindung fehlgeschlagen")
                    return

            # Get module info
            all_modules = self.module_mapping.get_all_modules()
            module_info = all_modules.get(module_id)
            if not module_info:
                st.error(f"Modul {module_id} nicht gefunden")
                return
            
            # Initialize or get current orderUpdateId for this module
            order_update_key = f"order_update_id_{module_id}"
            if order_update_key not in st.session_state:
                st.session_state[order_update_key] = 1
            else:
                st.session_state[order_update_key] += 1
            
            order_update_id = st.session_state[order_update_key]
            
            # Create message with proper metadata including NFC code
            message = {
                "serialNumber": module_info["id"],
                "orderId": str(uuid.uuid4()),
                "orderUpdateId": order_update_id,
                "action": {
                    "id": str(uuid.uuid4()),
                    "command": command,
                    "metadata": {
                        "priority": "NORMAL",
                        "timeout": 300,
                        "type": workpiece_color,
                        "workpieceId": nfc_code
                    }
                }
            }
            
            topic = f"module/v1/ff/{module_info['id']}/order"
            
            # Send message
            success, result_message = self.send_mqtt_message_direct(topic, message)
            
            if success:
                st.success(f"✅ {command} gesendet für {workpiece_color} Werkstück")
                st.info(f"📡 Topic: {topic}")
                st.info(f"🆔 OrderUpdateId: {order_update_id}")
                st.info(f"🔍 NFC-Code: {nfc_code}")
            else:
                st.error(f"❌ Fehler: {result_message}")
                
        except Exception as e:
            st.error(f"❌ Fehler beim Senden: {e}")

    def send_factory_reset(self, with_storage=False):
        """Send factory reset command via MQTT"""
        try:
            if not self.mqtt_connected:
                if not self.connect_mqtt():
                    st.error("MQTT-Verbindung fehlgeschlagen")
                    return

            # Create reset message based on session analysis
            reset_message = {
                "timestamp": datetime.now().isoformat() + "Z",
                "withStorage": with_storage
            }
            
            topic = "ccu/set/reset"
            
            # Send message
            success, result_message = self.send_mqtt_message_direct(topic, reset_message)
            
            if success:
                storage_text = "mit Storage-Löschung" if with_storage else "ohne Storage-Löschung"
                st.success(f"✅ Fabrik-Reset gesendet ({storage_text})")
                st.info(f"📡 Topic: {topic}")
                st.info(f"💾 Storage: {with_storage}")
                
                # Show warning about consequences
                if with_storage:
                    st.warning("⚠️ **ACHTUNG:** HBW-Storage wurde gelöscht!")
                else:
                    st.info("ℹ️ HBW-Storage wurde beibehalten")
            else:
                st.error(f"❌ Fehler beim Reset: {result_message}")
                
        except Exception as e:
            st.error(f"❌ Fehler beim Senden des Reset-Befehls: {e}")

    def extract_availability_status(self, recent_messages, module_id):
        """Extract availability status from recent MQTT messages"""
        try:
            # Check if we have any messages
            if recent_messages.empty:
                return None

            # Get the most recent message for this module
            latest_message = recent_messages.sort_values(
                "timestamp", ascending=False
            ).iloc[0]

            # Try to parse the payload
            if isinstance(latest_message["payload"], str):
                try:
                    payload_data = json.loads(latest_message["payload"])
                except:
                    payload_data = {}
            else:
                payload_data = (
                    latest_message["payload"] if latest_message["payload"] else {}
                )

            # Look for availability status in different possible locations
            availability_status = None

            # Check direct status field
            if "status" in payload_data:
                status = payload_data["status"].upper()
                if status in [
                    "AVAILABLE",
                    "BUSY",
                    "BLOCKED",
                    "IDLE",
                    "RUNNING",
                    "ERROR",
                ]:
                    availability_status = status

            # Check state field
            elif "state" in payload_data:
                state = payload_data["state"].upper()
                if state in [
                    "AVAILABLE",
                    "BUSY",
                    "BLOCKED",
                    "IDLE",
                    "RUNNING",
                    "ERROR",
                ]:
                    availability_status = state

            # Check availability field
            elif "availability" in payload_data:
                availability = payload_data["availability"].upper()
                if availability in [
                    "AVAILABLE",
                    "BUSY",
                    "BLOCKED",
                    "IDLE",
                    "RUNNING",
                    "ERROR",
                ]:
                    availability_status = availability

            # Check action status
            elif "action" in payload_data and "status" in payload_data["action"]:
                action_status = payload_data["action"]["status"].upper()
                if action_status in [
                    "AVAILABLE",
                    "BUSY",
                    "BLOCKED",
                    "IDLE",
                    "RUNNING",
                    "ERROR",
                ]:
                    availability_status = action_status

            # Map common statuses to availability
            if availability_status:
                status_mapping = {
                    "IDLE": "AVAILABLE",
                    "READY": "AVAILABLE",
                    "RUNNING": "BUSY",
                    "PROCESSING": "BUSY",
                    "ERROR": "BLOCKED",
                    "FAULT": "BLOCKED",
                }
                return status_mapping.get(availability_status, availability_status)

            return None

        except Exception as e:
            st.warning(f"Error extracting availability status: {e}")
            return None

    def get_enhanced_status_display(self, status_text, module_type=None):
        """Get enhanced status display with appropriate icons"""
        if not status_text:
            return f"{get_status_icon('offline')} No Data"
        
        status_lower = status_text.lower()
        
        # Module-specific status mappings
        if module_type:
            module_upper = module_type.upper()
            if module_upper == "CHRG" and "charging" in status_lower:
                return f"{get_status_icon('charging')} Charging"
            elif module_upper == "FTS" and ("transport" in status_lower or "moving" in status_lower):
                return f"{get_status_icon('transport')} Transport"
            elif module_upper in ["MILL", "DRILL"] and "processing" in status_lower:
                return f"{get_status_icon('processing')} Processing"
            elif module_upper == "HBW" and "storing" in status_lower:
                return f"{get_status_icon('ready')} Storing"
        
        # General status mappings
        if "available" in status_lower or "online" in status_lower:
            return f"{get_status_icon('available')} Available"
        elif "busy" in status_lower or "processing" in status_lower:
            return f"{get_status_icon('busy')} Busy"
        elif "blocked" in status_lower or "error" in status_lower:
            return f"{get_status_icon('blocked')} Blocked"
        elif "charging" in status_lower:
            return f"{get_status_icon('charging')} Charging"
        elif "transport" in status_lower or "moving" in status_lower:
            return f"{get_status_icon('transport')} Transport"
        elif "maintenance" in status_lower:
            return f"{get_status_icon('maintenance')} Maintenance"
        elif "idle" in status_lower or "waiting" in status_lower:
            return f"{get_status_icon('idle')} Idle"
        elif "ready" in status_lower:
            return f"{get_status_icon('ready')} Ready"
        else:
            return f"⚪ {status_text}"

    def create_fts_message(self, command):
        """Create FTS-specific message"""
        import uuid

        return {
            "serialNumber": "5iO4",
            "orderId": str(uuid.uuid4()),
            "orderUpdateId": 1,
            "action": {
                "id": str(uuid.uuid4()),
                "command": command.upper(),
                "metadata": {"priority": "NORMAL", "timeout": 300, "type": "TRANSPORT"},
            },
        }

    def get_fts_status(self):
        """Get current FTS status from recent messages"""
        try:
            # Query recent FTS state messages
            query = """
            SELECT payload, timestamp 
            FROM mqtt_messages 
            WHERE topic LIKE '%fts%' OR topic LIKE '%5iO4%'
            ORDER BY timestamp DESC 
            LIMIT 10
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            if df.empty:
                return "🟡 Unbekannt"
            
            # Look for activity status in recent messages
            for _, row in df.iterrows():
                try:
                    payload = json.loads(row['payload'])
                    
                    # Check for activity status
                    if 'activityStatus' in str(payload):
                        if 'CHARGING' in str(payload):
                            return "🔋 Lädt"
                        elif 'BUSY' in str(payload):
                            return "🔄 Beschäftigt"
                        elif 'READY' in str(payload):
                            return "🟢 Bereit"
                        elif 'IDLE' in str(payload):
                            return "🟢 Bereit"
                            
                except (json.JSONDecodeError, KeyError):
                    continue
            
            return "🟡 Unbekannt"
            
        except Exception as e:
            return "🔴 Fehler"

    def send_fts_command(self, action_type, metadata):
        """Send FTS-specific command via CCU"""
        try:
            if not self.mqtt_connected:
                if not self.connect_mqtt():
                    st.error("MQTT-Verbindung fehlgeschlagen")
                    return

            import uuid
            from datetime import datetime

            # FTS control via CCU based on session analysis
            if action_type == "startCharging":
                # Send charge command to CCU
                ccu_message = {
                    "serialNumber": "5iO4",
                    "charge": True
                }
                topic = "ccu/set/charge"
                
            elif action_type == "stopCharging":
                # Send stop charge command to CCU
                ccu_message = {
                    "serialNumber": "5iO4",
                    "charge": False
                }
                topic = "ccu/set/charge"
                
            elif action_type == "findInitialDockPosition":
                # Send pairing command to CCU first, then order
                ccu_message = {
                    "serialNumber": "5iO4"
                }
                topic = "ccu/pairing/pair_fts"
                
            elif action_type == "factsheetRequest":
                # Direct FTS command for status
                fts_message = {
                    "timestamp": datetime.now().isoformat() + "Z",
                    "serialNumber": "5iO4",
                    "actions": [
                        {
                            "actionId": str(uuid.uuid4()),
                            "actionType": "factsheetRequest",
                            "metadata": {}
                        }
                    ]
                }
                topic = "fts/v1/ff/5iO4/instantAction"
                
                # Send message
                success, result_message = self.send_mqtt_message_direct(topic, fts_message)
                
                if success:
                    st.success(f"✅ FTS Status abgefragt")
                    st.info(f"📡 Topic: {topic}")
                else:
                    st.error(f"❌ Fehler: {result_message}")
                return
                
            else:
                st.error(f"❌ Unbekannter FTS-Befehl: {action_type}")
                return
            
            # Send CCU message
            success, result_message = self.send_mqtt_message_direct(topic, ccu_message)
            
            if success:
                st.success(f"✅ FTS Befehl gesendet: {action_type}")
                st.info(f"📡 Topic: {topic}")
                st.info(f"📋 CCU Command: {ccu_message}")
            else:
                st.error(f"❌ Fehler: {result_message}")
                
        except Exception as e:
            st.error(f"❌ Fehler beim Senden des FTS-Befehls: {e}")

    # def show_node_red_analysis(self):
    #     """Show Node-RED message analysis - MOVED TO APS ANALYSIS TAB"""
        st.header("🔍 Node-RED Analyse")
        st.markdown("Analysiert Node-RED Nachrichten aus Session-Daten für ORDER-ID Management")
        
        # Session selection
        session_files = self.get_available_sessions()
        
        if not session_files:
            st.warning("❌ Keine Session-Dateien gefunden")
            return
        
        selected_session = st.selectbox(
            "Session auswählen:",
            session_files,
            format_func=lambda x: x.split('/')[-1].replace('.db', '')
        )
        
        if selected_session and st.button("🔍 Node-RED Nachrichten analysieren"):
            with st.spinner("Analysiere Node-RED Nachrichten..."):
                self.analyze_node_red_session(selected_session)
    
    def get_available_sessions(self):
        """Get available session files"""
        import glob
        import os
        
        # Get project root (3 levels up from dashboard)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        session_pattern = os.path.join(project_root, "mqtt-data/sessions/aps_persistent_traffic_*.db")
        session_files = glob.glob(session_pattern)
        session_files.sort()
        
        return session_files
    
    def analyze_node_red_session(self, session_file):
        """Analyze Node-RED messages from a session"""
        try:
            analyzer = NodeRedMessageAnalyzer(session_file)
            
            # Connect to database
            if not analyzer.connect():
                st.error("❌ Verbindung zur Session-Datenbank fehlgeschlagen")
                return
            
            # Load Node-RED messages
            df = analyzer.get_node_red_messages()
            
            if df.empty:
                st.warning("⚠️ Keine Node-RED Nachrichten in dieser Session gefunden")
                analyzer.disconnect()
                return
            
            # Perform analyses
            topic_analysis = analyzer.analyze_node_red_topics(df)
            state_messages = analyzer.extract_node_red_state_messages(df)
            factsheet_messages = analyzer.extract_factsheet_messages(df)
            connection_messages = analyzer.extract_connection_messages(df)
            
            # Display results
            self.display_node_red_results(
                session_file, topic_analysis, state_messages, 
                factsheet_messages, connection_messages, df
            )
            
            analyzer.disconnect()
            
        except Exception as e:
            st.error(f"❌ Fehler bei der Node-RED Analyse: {e}")
    
    def display_node_red_results(self, session_file, topic_analysis, state_messages, 
                                factsheet_messages, connection_messages, all_messages):
        """Display Node-RED analysis results"""
        
        # Session info
        st.success(f"✅ Node-RED Analyse abgeschlossen: {session_file.split('/')[-1]}")
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt-Nachrichten", topic_analysis.get('total_messages', 0))
        
        with col2:
            st.metric("Node-RED State", len(state_messages))
        
        with col3:
            st.metric("Factsheet", len(factsheet_messages))
        
        with col4:
            st.metric("Connection", len(connection_messages))
        
        # Topic distribution
        st.subheader("📋 Topic Distribution")
        
        if 'topic_distribution' in topic_analysis:
            # Create DataFrame with friendly names
            topic_df = pd.DataFrame(
                list(topic_analysis['topic_distribution'].items()),
                columns=['Topic', 'Count']
            ).sort_values('Count', ascending=False)
            
            # Create display DataFrame with friendly topic names
            topic_df_display = topic_df[['Topic', 'Count']].copy()
            topic_df_display['Friendly_Topic'] = topic_df_display['Topic'].apply(lambda x: self.topic_manager.get_friendly_name(x))
            
            # Show both original and friendly names
            st.dataframe(topic_df_display[['Friendly_Topic', 'Topic', 'Count']], use_container_width=True)
            
            # Bar chart with friendly names
            st.bar_chart(topic_df_display.set_index('Friendly_Topic')['Count'])
        
        # Node-RED State Messages
        if not state_messages.empty:
            st.subheader("🔍 Node-RED State Messages")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Topics:**")
                for topic in state_messages['topic'].unique():
                    friendly_name = self.topic_manager.get_friendly_name(topic)
                    st.markdown(f"• **{friendly_name}**")
                    if friendly_name != topic:
                        st.markdown(f"  `{topic}`")
            
            with col2:
                st.markdown("**Sample Messages:**")
                for _, row in state_messages.head(3).iterrows():
                    with st.expander(f"{row['timestamp']} - {row['topic']}"):
                        try:
                            payload = json.loads(row['payload']) if isinstance(row['payload'], str) else row['payload']
                            st.json(payload)
                        except:
                            st.text(str(row['payload']))
        
        # Factsheet Messages
        if not factsheet_messages.empty:
            st.subheader("📋 Factsheet Messages")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Topics:**")
                for topic in factsheet_messages['topic'].unique():
                    friendly_name = self.topic_manager.get_friendly_name(topic)
                    st.markdown(f"• **{friendly_name}**")
                    if friendly_name != topic:
                        st.markdown(f"  `{topic}`")
            
            with col2:
                st.markdown("**Sample Messages:**")
                for _, row in factsheet_messages.head(3).iterrows():
                    with st.expander(f"{row['timestamp']} - {row['topic']}"):
                        try:
                            payload = json.loads(row['payload']) if isinstance(row['payload'], str) else row['payload']
                            st.json(payload)
                        except:
                            st.text(str(row['payload']))
        
        # Connection Messages
        if not connection_messages.empty:
            st.subheader("🔗 Connection Messages")
            
            # Connection status timeline
            connection_timeline = connection_messages.copy()
            connection_timeline['timestamp'] = pd.to_datetime(connection_timeline['timestamp'])
            
            # Parse connection state
            def extract_connection_state(payload):
                try:
                    if isinstance(payload, str):
                        data = json.loads(payload)
                    else:
                        data = payload
                    return data.get('connectionState', 'unknown')
                except:
                    return 'unknown'
            
            connection_timeline['connection_state'] = connection_timeline['payload'].apply(extract_connection_state)
            
            # Timeline chart
            st.markdown("**Connection Status Timeline:**")
            
            # Group by module and show connection states
            module_connections = connection_timeline.groupby(['module_type', 'connection_state']).size().unstack(fill_value=0)
            st.dataframe(module_connections, use_container_width=True)
            
            # Sample connection messages
            st.markdown("**Sample Connection Messages:**")
            for _, row in connection_messages.head(3).iterrows():
                friendly_topic = self.topic_manager.get_friendly_name(row['topic'])
                with st.expander(f"{row['timestamp']} - {friendly_topic}"):
                    st.markdown(f"**Original Topic:** `{row['topic']}`")
                    try:
                        payload = json.loads(row['payload']) if isinstance(row['payload'], str) else row['payload']
                        st.json(payload)
                    except:
                        st.text(str(row['payload']))
        
        # ORDER-ID Management Insights
        st.subheader("🚨 ORDER-ID Management Insights")
        
        # Analyze state messages for ORDER-ID patterns
        if not state_messages.empty:
            st.markdown("**🔍 Node-RED State Message Analysis:**")
            
            # Look for ORDER-ID related information
            order_id_insights = []
            
            for _, row in state_messages.iterrows():
                try:
                    payload = json.loads(row['payload']) if isinstance(row['payload'], str) else row['payload']
                    
                    # Check for ORDER-ID related fields
                    if 'orderId' in payload:
                        order_id_insights.append({
                            'timestamp': row['timestamp'],
                            'topic': row['topic'],
                            'orderId': payload.get('orderId'),
                            'orderUpdateId': payload.get('orderUpdateId'),
                            'status': payload.get('actionState', {}).get('state') if 'actionState' in payload else None
                        })
                except:
                    continue
            
            if order_id_insights:
                st.markdown("**ORDER-ID Patterns gefunden:**")
                insights_df = pd.DataFrame(order_id_insights)
                st.dataframe(insights_df, use_container_width=True)
                
                # Show ORDER-ID distribution
                if 'orderId' in insights_df.columns:
                    order_id_counts = insights_df['orderId'].value_counts()
                    st.markdown("**ORDER-ID Verteilung:**")
                    st.bar_chart(order_id_counts.head(10))
            else:
                st.info("Keine ORDER-ID Patterns in Node-RED State Messages gefunden")
        
        # Connection insights for ORDER-ID Management
        if not connection_messages.empty:
            st.markdown("**🔗 Connection Status für ORDER-ID Management:**")
            
            # Show module availability
            module_availability = connection_timeline.groupby('module_type')['connection_state'].value_counts().unstack(fill_value=0)
            st.dataframe(module_availability, use_container_width=True)
            
            st.info("💡 **ORDER-ID Management Tipp:** Module müssen 'connected' sein, bevor ORDER-ID Workflows gestartet werden können")



    def show_template_library(self):
        """Show template library with analysis results"""
        st.header("📚 Template Library")
        st.markdown("MQTT Template-Analyse und Dokumentation")
        
        # Load template analysis results
        template_library_dir = "mqtt-data/template_library"
        
        if not os.path.exists(template_library_dir):
            st.warning("📁 Template Library Verzeichnis nicht gefunden!")
            st.info("Führe zuerst die Template-Analyzer aus:")
            st.code("python3 src_orbis/mqtt/tools/txt_template_analyzer.py")
            st.code("python3 src_orbis/mqtt/tools/ccu_template_analyzer.py")
            return
        
        # Load analysis files
        txt_file = os.path.join(template_library_dir, "txt_template_analysis.json")
        ccu_file = os.path.join(template_library_dir, "ccu_template_analysis.json")
        
        all_templates = {}
        
        if os.path.exists(txt_file):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    txt_data = json.load(f)
                    all_templates.update(txt_data.get('templates', {}))
            except Exception as e:
                st.error(f"❌ Fehler beim Laden der TXT-Analyse: {e}")
        
        if os.path.exists(ccu_file):
            try:
                with open(ccu_file, 'r', encoding='utf-8') as f:
                    ccu_data = json.load(f)
                    all_templates.update(ccu_data.get('templates', {}))
            except Exception as e:
                st.error(f"❌ Fehler beim Laden der CCU-Analyse: {e}")
        
        if not all_templates:
            st.warning("📄 Keine Template-Analysen gefunden!")
            return
        
        # Category filter
        categories = list(set(template.get('category', 'Unknown') for template in all_templates.values()))
        selected_category = st.selectbox(
            "📂 Kategorie auswählen:",
            ["Alle"] + categories,
            key="template_category_filter"
        )
        
        # Sub-category filter
        sub_categories = []
        if selected_category != "Alle":
            sub_categories = list(set(
                template.get('sub_category', 'Unknown') 
                for topic, template in all_templates.items()
                if template.get('category') == selected_category
            ))
        
        selected_sub_category = None
        if sub_categories:
            selected_sub_category = st.selectbox(
                "📋 Sub-Kategorie auswählen:",
                ["Alle"] + sub_categories,
                key="template_sub_category_filter"
            )
            if selected_sub_category == "Alle":
                selected_sub_category = None
        
        # Filter templates by category and sub-category
        if selected_category == "Alle":
            filtered_templates = all_templates
        else:
            filtered_templates = {
                topic: template for topic, template in all_templates.items()
                if template.get('category') == selected_category
            }
            
            # Apply sub-category filter if selected
            if selected_sub_category:
                filtered_templates = {
                    topic: template for topic, template in filtered_templates.items()
                    if template.get('sub_category') == selected_sub_category
                }
        
        st.markdown(f"**📊 {len(filtered_templates)} Templates gefunden**")
        
        # Display each template
        for topic, template in filtered_templates.items():
            with st.expander(f"📋 {topic}", expanded=False):
                self._display_template_details(template)
    
    def _display_template_details(self, template):
        """Display detailed template information with improved layout"""
        category = template.get('category', 'Unknown')
        stats = template.get('statistics', {})
        template_structure = template.get('template_structure', {})
        examples = template.get('examples', [])
        
        # Header with category and topic
        st.markdown(f"**Kategorie:** {category} | **Topic:** {template.get('topic', 'Unknown')}")
        
        # Top section: Meta-Info + Template Structure Description | Documentation
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Meta information in one line
            st.markdown("### 📊 Meta-Information")
            st.markdown(f"📈 **Nachrichten:** {stats.get('total_messages', 0)} | "
                       f"📁 **Sessions:** {stats.get('sessions', 0)} | "
                       f"🔄 **Variable Felder:** {stats.get('variable_fields', 0)} | "
                       f"🎯 **Enum-Felder:** {stats.get('enum_fields', 0)}")
            
            st.markdown("")
            st.markdown("### 📋 Template-Struktur Beschreibung")
            if template_structure:
                self._display_hierarchical_structure(template_structure, indent=1)
            else:
                st.markdown("*Keine Template-Struktur verfügbar*")
        
        with col2:
            # Documentation section (3 fields stacked)
            st.markdown("### 📝 Dokumentation (editierbar)")
            
            description = st.text_area(
                "💡 Beschreibung:",
                value=template.get('documentation', {}).get('description', ''),
                key=f"desc_{template.get('topic', 'unknown')}",
                height=80
            )
            
            usage = st.text_area(
                "🎯 Verwendung:",
                value=template.get('documentation', {}).get('usage', ''),
                key=f"usage_{template.get('topic', 'unknown')}",
                height=80
            )
            
            info = st.text_area(
                "📋 Info zur Template Struktur, Elemente,...:",
                value=template.get('documentation', {}).get('info', ''),
                key=f"info_{template.get('topic', 'unknown')}",
                height=80
            )
            
            # Save button
            if st.button("💾 Dokumentation speichern", key=f"save_{template.get('topic', 'unknown')}"):
                self._save_template_documentation(template.get('topic', 'unknown'), {
                    'description': description,
                    'usage': usage,
                    'info': info
                })
                st.success("✅ Dokumentation gespeichert!")
        
        # Visual separator between top and bottom sections
        st.markdown("---")
        
        # Bottom section: Template Structure | Examples (both as tabs)
        col1, col2 = st.columns(2)
        
        with col1:
            # Template structure as tab
            if template_structure:
                template_tab = st.tabs(["Template"])
                with template_tab[0]:
                    topic_name = template.get('topic', 'Unknown')
                    st.markdown(f"**{topic_name}**")
                    
                    # Display hierarchical template structure as code (same format as examples)
                    template_lines = self._generate_hierarchical_json(template_structure)
                    template_json = "{\n" + "\n".join(template_lines) + "\n}"
                    try:
                        # Validate JSON first
                        json.loads(template_json)
                        # Use st.code for consistent formatting with examples
                        st.code(template_json, language="json")
                    except json.JSONDecodeError:
                        # Fallback to code display if JSON is invalid
                        st.code(template_json, language="json")
            else:
                st.markdown("*Keine Template-Struktur verfügbar*")
        
        with col2:
            # Example tabs
            if examples:
                # Create tabs for examples
                example_tabs = st.tabs([f"Beispiel {i+1}" for i in range(len(examples))])
                
                for i, tab in enumerate(example_tabs):
                    with tab:
                        example = examples[i]
                        
                        # Display example with session info on same line
                        st.markdown(f"**Session:** {template.get('session_name', 'Unknown')} | "
                                   f"**Timestamp:** {template.get('timestamp', 'Unknown')}")
                        
                        # Display example as JSON starting with {, with friendly NFC code names
                        formatted_example = self._format_example_for_display(example)
                        st.json(formatted_example)
            else:
                st.markdown("*Keine Beispiele verfügbar*")
    
    def _display_hierarchical_structure(self, template_structure, indent=0):
        """Display template structure with proper hierarchical indentation and icons"""
        indent_str = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" * indent
        
        for field, placeholder in template_structure.items():
            if isinstance(placeholder, dict):
                # Nested object
                st.markdown(f"{indent_str}📦 **{field}**: Objekt", unsafe_allow_html=True)
                self._display_hierarchical_structure(placeholder, indent + 1)
            elif isinstance(placeholder, list):
                # Array
                st.markdown(f"{indent_str}📋 **{field}**: Array mit {len(placeholder)} Elementen", unsafe_allow_html=True)
                if placeholder and isinstance(placeholder[0], dict):
                    # Array of objects - show first element structure
                    self._display_hierarchical_structure(placeholder[0], indent + 1)
            elif isinstance(placeholder, str):
                if placeholder.startswith('['):
                    # ENUM field
                    st.markdown(f"{indent_str}🎯 **{field}**: {placeholder} (ENUM)", unsafe_allow_html=True)
                elif placeholder.startswith('<'):
                    # Placeholder field
                    if 'nfcCode' in placeholder:
                        st.markdown(f"{indent_str}🏷️ **{field}**: {placeholder} (NFC Code)", unsafe_allow_html=True)
                    elif 'ts' in placeholder:
                        st.markdown(f"{indent_str}⏰ **{field}**: {placeholder} (Timestamp)", unsafe_allow_html=True)
                    elif 'moduleId' in placeholder:
                        st.markdown(f"{indent_str}🔧 **{field}**: {placeholder} (Module ID)", unsafe_allow_html=True)
                    else:
                        st.markdown(f"{indent_str}📝 **{field}**: {placeholder} (Platzhalter)", unsafe_allow_html=True)
                else:
                    # Simple field
                    st.markdown(f"{indent_str}📄 **{field}**: {placeholder}", unsafe_allow_html=True)
            else:
                # Other types
                st.markdown(f"{indent_str}❓ **{field}**: {placeholder}", unsafe_allow_html=True)
    
    def _format_example_for_display(self, example_data):
        """Format example data for display, replacing NFC codes with friendly names"""
        if isinstance(example_data, dict):
            formatted = {}
            for key, value in example_data.items():
                if isinstance(value, str) and len(value) == 14 and value.startswith('04'):
                    # Replace NFC code with friendly name for display
                    from src_orbis.mqtt.tools.nfc_code_manager import get_nfc_manager
                    nfc_manager = get_nfc_manager()
                    friendly_name = nfc_manager.get_friendly_name(value)
                    formatted[key] = f"{friendly_name} ({value})"
                elif isinstance(value, dict):
                    formatted[key] = self._format_example_for_display(value)
                elif isinstance(value, list):
                    formatted[key] = [self._format_example_for_display(item) if isinstance(item, dict) else item for item in value]
                else:
                    formatted[key] = value
            return formatted
        return example_data
    def _generate_hierarchical_json(self, template_structure, indent=2):
        """Generate hierarchical JSON representation of template structure with proper formatting"""
        lines = []
        fields = list(template_structure.items())
        
        for i, (field, placeholder) in enumerate(fields):
            indent_str = " " * indent
            is_last = i == len(fields) - 1
            
            if isinstance(placeholder, dict):
                # Nested object
                lines.append(f'{indent_str}"{field}": {{')
                nested_lines = self._generate_hierarchical_json(placeholder, indent + 2)
                lines.extend(nested_lines)
                lines.append(f"{indent_str}}},")
            elif isinstance(placeholder, list):
                # Array
                lines.append(f'{indent_str}"{field}": [')
                if placeholder and isinstance(placeholder[0], dict):
                    # Array of objects
                    lines.append(f'{indent_str}  {{')
                    nested_lines = self._generate_hierarchical_json(placeholder[0], indent + 4)
                    lines.extend(nested_lines)
                    lines.append(f'{indent_str}  }}')
                else:
                    lines.append(f'{indent_str}  "{placeholder[0] if placeholder else "element"}"')
                lines.append(f"{indent_str}],")
            else:
                # Simple field - always use quotes for consistency
                if isinstance(placeholder, str):
                    lines.append(f'{indent_str}"{field}": "{placeholder}",')
                else:
                    lines.append(f'{indent_str}"{field}": "{placeholder}",')
        
        # Remove trailing comma from last line
        if lines and lines[-1].endswith(','):
            lines[-1] = lines[-1].rstrip(',')
        
        return lines
    
    def _save_template_documentation(self, topic, documentation):
        """Save template documentation to analysis JSON"""
        template_library_dir = "mqtt-data/template_library"
        
        # Find which file contains this topic
        txt_file = os.path.join(template_library_dir, "txt_template_analysis.json")
        ccu_file = os.path.join(template_library_dir, "ccu_template_analysis.json")
        
        for file_path in [txt_file, ccu_file]:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Update documentation for the topic
                    if 'templates' in data and topic in data['templates']:
                        if 'documentation' not in data['templates'][topic]:
                            data['templates'][topic]['documentation'] = {}
                        data['templates'][topic]['documentation'].update(documentation)
                        
                        # Save back to file
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        break
                except Exception as e:
                    st.error(f"❌ Fehler beim Speichern: {e}")

    def show_settings(self):
        """Show dashboard settings with sub-navigation"""
        st.header("⚙️ Einstellungen")
        st.markdown("Dashboard-Konfiguration und System-Informationen")

        # Sub-navigation for settings
        settings_tab1, settings_tab2, settings_tab3, settings_tab4, settings_tab5, settings_tab6 = st.tabs([
            "🔧 Dashboard",
            "🏭 Module",
            "🏷️ NFC-Codes",
            "📡 Topic-Konfiguration",
            "📚 MQTT-Templates",
            "📋 Message-Templates"
        ])

        with settings_tab1:
            self.show_dashboard_settings()

        with settings_tab2:
            self.show_module_settings()

        with settings_tab3:
            self.show_nfc_mapping_settings()

        with settings_tab4:
            self.show_topic_configuration_settings()

        with settings_tab5:
            self.show_mqtt_template_settings()
            
        with settings_tab6:
            self.show_message_template_settings()

    def show_dashboard_settings(self):
        """Show dashboard configuration settings"""
        st.subheader("🔧 Dashboard-Einstellungen")

        col1, col2 = st.columns(2)

        with col1:
            # Verbose mode
            verbose_mode = st.checkbox(
                "🔍 Verbose-Modus (alle Topics anzeigen)",
                value=self.verbose_mode,
                help="Zeigt alle MQTT-Topics an, auch Kamera-Daten",
            )

            # Auto-refresh
            auto_refresh = st.checkbox(
                "🔄 Auto-Refresh",
                value=True,
                help="Aktualisiert das Dashboard automatisch",
            )

            # Refresh interval
            if auto_refresh:
                refresh_interval = st.slider(
                    "⏱️ Refresh-Intervall (Sekunden)",
                    min_value=5,
                    max_value=60,
                    value=30,
                    step=5,
                )

        with col2:
            st.subheader("📊 Dashboard-Statistiken")

            # Dashboard statistics
            all_modules = self.module_mapping.get_all_modules()
            st.metric("Aktive Module", len(all_modules))
            st.metric(
                "Verfügbare Befehle",
                sum(
                    len(module.get("commands", []))
                    for module in all_modules.values()
                ),
            )
            st.metric("MQTT-Nachrichten gesendet", len(self.mqtt_messages_sent))
            st.metric("MQTT-Antworten empfangen", len(self.mqtt_responses))

        st.markdown("---")

        # System information
        st.subheader("💻 System-Informationen")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Datenbank-Dateien",
                len(glob.glob(os.path.join(os.path.dirname(self.db_file), "*.db"))),
            )
            st.metric("Dashboard-Version", "2.0")

        with col2:
            st.metric("Template-Nachrichten", len(self.template_manager.templates))
            st.metric("Message-Templates", self.message_template_manager.get_statistics()["total_topics"])
            st.metric("Session-Datenbanken", len(glob.glob(os.path.join(os.path.dirname(self.db_file), "aps_persistent_traffic_*.db"))))



    def show_nfc_mapping_settings(self):
        """Show NFC code mapping configuration from YAML file"""
        st.subheader("🏷️ NFC-Code Mapping")
        st.markdown("Zentrale Konfiguration der NFC-Codes aus `nfc_code_config.yml`")
        
        # Load NFC configuration from YAML
        nfc_config = self.load_nfc_config()
        
        if not nfc_config:
            st.error("❌ NFC-Konfiguration konnte nicht geladen werden")
            return
        
        # Display NFC codes organized by color
        colors = ["RED", "WHITE", "BLUE"]
        color_icons = {"RED": "🔴", "WHITE": "⚪", "BLUE": "🔵"}
        
        for color in colors:
            color_codes = {code: info for code, info in nfc_config['nfc_codes'].items() 
                          if info['color'] == color}
            
            if color_codes:
                with st.expander(f"{color_icons[color]} {color} Werkstücke ({len(color_codes)} Codes)", expanded=True):
                    # Create table data
                    table_data = []
                    for nfc_code, info in color_codes.items():
                        table_data.append({
                            "NFC-Code": nfc_code,
                            "Friendly-ID": info['friendly_id'],
                            "Quality-Check": info['quality_check'],
                            "Beschreibung": info['description']
                        })
                    
                    # Display as table
                    if table_data:
                        df = pd.DataFrame(table_data)
                        st.dataframe(
                            df,
                            use_container_width=True,
                            column_config={
                                "NFC-Code": st.column_config.TextColumn("NFC-Code", width="medium"),
                                "Friendly-ID": st.column_config.TextColumn("Friendly-ID", width="small"),
                                "Quality-Check": st.column_config.SelectboxColumn(
                                    "Quality-Check",
                                    options=["OK", "NOT-OK", "PENDING", "FAILED"],
                                    width="small"
                                ),
                                "Beschreibung": st.column_config.TextColumn("Beschreibung", width="large")
                            }
                        )
        
        # Statistics
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt NFC-Codes", len(nfc_config['nfc_codes']))
        with col2:
            red_count = len([c for c in nfc_config['nfc_codes'].values() if c['color'] == 'RED'])
            st.metric("🔴 RED", red_count)
        with col3:
            white_count = len([c for c in nfc_config['nfc_codes'].values() if c['color'] == 'WHITE'])
            st.metric("⚪ WHITE", white_count)
        with col4:
            blue_count = len([c for c in nfc_config['nfc_codes'].values() if c['color'] == 'BLUE'])
            st.metric("🔵 BLUE", blue_count)
        
        # Info about usage
        st.info("ℹ️ **Hinweis:** Friendly-IDs werden nur für die Dashboard-Anzeige verwendet. In MQTT-Nachrichten werden immer die echten NFC-Codes verwendet.")

    def show_module_settings(self):
        """Show module configuration settings from YAML file"""
        st.subheader("🏭 Modul-Konfiguration")
        st.markdown("Zentrale Konfiguration der Module aus `module_config.yml`")
        
        # Load module configuration from ModuleManager
        module_manager = self.module_mapping
        all_modules = module_manager.get_all_modules()
        
        if not all_modules:
            st.error("❌ Modul-Konfiguration konnte nicht geladen werden")
            return
        
        # Create table data for all modules in one table
        table_data = []
        type_icons = {
            "Processing": "⚙️",
            "Quality-Control": "🔍", 
            "Storage": "📦",
            "Input/Output": "🚪",
            "Charging": "🔋",
            "Transport": "🚗"
        }
        
        for module_id, info in all_modules.items():
            # Get module type icon
            module_type = info.get('type', 'Unknown')
            icon = type_icons.get(module_type, "🏭")
            
            # Get commands
            commands = info.get('commands', [])
            commands_display = ", ".join(commands) if commands else "Keine Befehle"
            
            table_data.append({
                "Icon + Modul": f"{icon} {info.get('name', '')}",
                "Modul-ID": module_id,
                "Name (DE)": info.get('name_lang_de', ''),
                "Name (EN)": info.get('name_lang_en', ''),
                "Modul-Type": module_type,
                "IP-Range": info.get('ip_range', ''),
                "Befehle": commands_display,
                "Beschreibung": info.get('description', '')
            })
        
        # Display as single table
        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "Icon + Modul": st.column_config.TextColumn("Icon + Modul", width="medium"),
                    "Modul-ID": st.column_config.TextColumn("Modul-ID", width="medium"),
                    "Name (DE)": st.column_config.TextColumn("Name (DE)", width="medium"),
                    "Name (EN)": st.column_config.TextColumn("Name (EN)", width="medium"),
                    "Modul-Type": st.column_config.TextColumn("Modul-Type", width="small"),
                    "IP-Range": st.column_config.TextColumn("IP-Range", width="small"),
                    "Befehle": st.column_config.TextColumn("Befehle", width="large"),
                    "Beschreibung": st.column_config.TextColumn("Beschreibung", width="large")
                }
            )
        
        # Statistics
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt Module", len(all_modules))
        with col2:
            processing_count = len(module_manager.get_modules_by_type("Processing"))
            st.metric("⚙️ Processing", processing_count)
        with col3:
            storage_count = len(module_manager.get_modules_by_type("Storage"))
            st.metric("📦 Storage", storage_count)
        with col4:
            other_count = len(all_modules) - processing_count - storage_count
            st.metric("🏭 Andere", other_count)
        
        # IP-Range Overview
        st.markdown("---")
        st.subheader("🌐 IP-Range Übersicht")
        
        ip_overview_data = []
        for module_id, info in all_modules.items():
            ip_range = info.get('ip_range', '')
            ip_addresses = info.get('ip_addresses', [])
            ip_count = len(ip_addresses)
            
            ip_overview_data.append({
                "Modul": info.get('name', module_id),
                "Modul-ID": module_id,
                "IP-Range": ip_range,
                "Anzahl IPs": ip_count,
                "IP-Adressen": ", ".join(ip_addresses) if ip_addresses else "Keine"
            })
        
        if ip_overview_data:
            ip_df = pd.DataFrame(ip_overview_data)
            st.dataframe(
                ip_df,
                use_container_width=True,
                column_config={
                    "Modul": st.column_config.TextColumn("Modul", width="small"),
                    "Modul-ID": st.column_config.TextColumn("Modul-ID", width="medium"),
                    "IP-Range": st.column_config.TextColumn("IP-Range", width="small"),
                    "Anzahl IPs": st.column_config.NumberColumn("Anzahl IPs", width="small"),
                    "IP-Adressen": st.column_config.TextColumn("IP-Adressen", width="large")
                }
            )
        
        # Info about usage
        st.info("ℹ️ **Hinweis:** Diese Konfiguration wird von allen Analysatoren und dem Dashboard verwendet. Änderungen müssen in der `module_config.yml` Datei vorgenommen werden.")

    def show_topic_configuration_settings(self):
        """Show topic configuration settings from YAML file"""
        st.subheader("📡 Topic-Konfiguration")
        st.markdown("Zentrale Konfiguration der MQTT-Topics aus `topic_config.yml`")
        
        # Load topic configuration from TopicManager
        topic_manager = self.topic_manager
        all_topics = topic_manager.get_all_topics()
        categories = topic_manager.get_categories()
        
        if not all_topics:
            st.error("❌ Topic-Konfiguration konnte nicht geladen werden")
            return
        
        # Display topics by category in collapsible sections
        for category_name, category_info in categories.items():
            category_icon = category_info.get('icon', '📋')
            category_description = category_info.get('description', '')
            
            # Get topics for this category
            category_topics = topic_manager.get_topics_by_category(category_name)
            
            if category_topics:
                with st.expander(f"{category_icon} {category_name} ({len(category_topics)} Topics)", expanded=False):
                    st.markdown(f"**Beschreibung:** {category_description}")
                    
                    # Check if this category has modules (MODULE or Node-RED)
                    has_modules = category_name in ["MODULE", "Node-RED"]
                    has_sub_categories = any(info.get('sub_category') for info in category_topics.values())
                    
                    if has_modules or has_sub_categories:
                        # Get unique modules for this category (if applicable)
                        modules = set()
                        if has_modules:
                            for topic, info in category_topics.items():
                                module = info.get('module', '')
                                if module:
                                    modules.add(module)
                        
                        # Get unique sub-categories for this category
                        sub_categories = set()
                        for topic, info in category_topics.items():
                            sub_category = info.get('sub_category', '')
                            if sub_category:
                                sub_categories.add(sub_category)
                        
                        # Create filter columns
                        if has_modules:
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                selected_module = st.selectbox(
                                    "Modul filtern:",
                                    ["Alle"] + sorted(list(modules)),
                                    key=f"module_filter_{category_name}"
                                )
                            
                            with col2:
                                selected_sub_category = st.selectbox(
                                    "Sub-Kategorie filtern:",
                                    ["Alle"] + sorted(list(sub_categories)),
                                    key=f"sub_category_filter_{category_name}"
                                )
                        else:
                            # Only sub-category filter for categories without modules
                            selected_module = "Alle"
                            selected_sub_category = st.selectbox(
                                "Sub-Kategorie filtern:",
                                ["Alle"] + sorted(list(sub_categories)),
                                key=f"sub_category_filter_{category_name}"
                            )
                        
                        # Filter topics based on selection
                        filtered_topics = {}
                        for topic, info in category_topics.items():
                            module = info.get('module', '')
                            sub_category = info.get('sub_category', '')
                            
                            # Apply module filter (only for categories with modules)
                            if has_modules and selected_module != "Alle" and module != selected_module:
                                continue
                            
                            # Apply sub-category filter
                            if selected_sub_category != "Alle" and sub_category != selected_sub_category:
                                continue
                            
                            filtered_topics[topic] = info
                        
                        category_topics = filtered_topics
                    
                    # Create table data for this category
                    table_data = []
                    for topic, info in category_topics.items():
                        # Get sub-category info for modules
                        sub_category = info.get('sub_category', '')
                        module = info.get('module', '')
                        
                        # Format sub-category display
                        sub_category_display = ""
                        if sub_category:
                            sub_category_icon = topic_manager.get_sub_category_icon(sub_category)
                            sub_category_description = topic_manager.get_sub_category_description(sub_category)
                            sub_category_display = f"{sub_category_icon} {sub_category}"
                        
                        # Format module display
                        module_display = f"({module})" if module else ""
                        
                        table_data.append({
                            "Topic": topic,
                            "Friendly-Name": info.get('friendly_name', topic),
                            "Sub-Kategorie": sub_category_display,
                            "Modul": module_display,
                            "Beschreibung": info.get('description', '')
                        })
                    
                    # Display as table
                    if table_data:
                        df = pd.DataFrame(table_data)
                        st.dataframe(
                            df,
                            use_container_width=True,
                            column_config={
                                "Topic": st.column_config.TextColumn("Topic", width="large"),
                                "Friendly-Name": st.column_config.TextColumn("Friendly-Name", width="medium"),
                                "Sub-Kategorie": st.column_config.TextColumn("Sub-Kategorie", width="small"),
                                "Modul": st.column_config.TextColumn("Modul", width="small"),
                                "Beschreibung": st.column_config.TextColumn("Beschreibung", width="large")
                            }
                        )
                    else:
                        st.info("Keine Topics mit den gewählten Filtern gefunden.")
        
        # Statistics
        st.markdown("---")
        stats = topic_manager.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt Topics", stats['total_topics'])
        with col2:
            st.metric("Kategorien", stats['total_categories'])
        with col3:
            module_topics = len(topic_manager.get_topics_by_category("MODULE"))
            st.metric("⚙️ Module Topics", module_topics)
        with col4:
            other_topics = stats['total_topics'] - module_topics
            st.metric("📡 Andere Topics", other_topics)
        
        # Sub-category statistics for modules
        if stats['sub_category_counts']:
            st.markdown("---")
            st.subheader("📊 Modul-Sub-Kategorien")
            
            sub_category_data = []
            for sub_category, count in stats['sub_category_counts'].items():
                icon = topic_manager.get_sub_category_icon(sub_category)
                description = topic_manager.get_sub_category_description(sub_category)
                
                sub_category_data.append({
                    "Sub-Kategorie": f"{icon} {sub_category}",
                    "Anzahl Topics": count,
                    "Beschreibung": description
                })
            
            if sub_category_data:
                sub_df = pd.DataFrame(sub_category_data)
                st.dataframe(
                    sub_df,
                    use_container_width=True,
                    column_config={
                        "Sub-Kategorie": st.column_config.TextColumn("Sub-Kategorie", width="medium"),
                        "Anzahl Topics": st.column_config.NumberColumn("Anzahl Topics", width="small"),
                        "Beschreibung": st.column_config.TextColumn("Beschreibung", width="large")
                    }
                )
        
        # Info about usage
        st.info("ℹ️ **Hinweis:** Diese Konfiguration wird für Topic-Mappings und Friendly-Names im Dashboard verwendet. Änderungen müssen in der `topic_config.yml` Datei vorgenommen werden.")

    def load_nfc_config(self):
        """Load NFC configuration from YAML file"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), "../config/nfc_code_config.yml"
            )
            with open(config_path, "r", encoding="utf-8") as f:
                import yaml
                return yaml.safe_load(f)
        except FileNotFoundError:
            st.error(f"❌ NFC-Konfigurationsdatei nicht gefunden: {config_path}")
            return None
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der NFC-Konfiguration: {e}")
            return None

    def show_mqtt_template_settings(self):
        """Show MQTT template configuration"""
        st.subheader("📚 MQTT-Template Konfiguration")
        st.markdown("Template-Nachrichten und Analyse-Einstellungen")

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 Verfügbare Templates:**")
            
            # Template categories
            template_categories = {
                "TXT": "TXT Controller Templates",
                "CCU": "CCU Templates", 
                "MODUL": "Module Templates",
                "Node-RED": "Node-RED Templates",
                "FTS": "FTS Templates"
            }
            
            for category, description in template_categories.items():
                with st.expander(f"📂 {category} - {description}", expanded=False):
                    st.markdown(f"**Beschreibung:** {description}")
                    st.markdown("**Status:** ⏳ Noch nicht analysiert")
                    st.markdown("**Aktion:** Verwende separate Analyse-Tools")
        
        with col2:
            st.markdown("**🔧 Analyse-Einstellungen:**")
            
            # Analysis configuration
            st.markdown("**Separate Analyse-Tools:**")
            st.code("TXT: python3 src_orbis/mqtt/tools/txt_template_analyzer.py")
            st.code("CCU: python3 src_orbis/mqtt/tools/ccu_template_analyzer.py")
            st.code("MODUL: python3 src_orbis/mqtt/tools/module_template_analyzer.py")
            st.code("Node-RED: python3 src_orbis/mqtt/tools/node_red_template_analyzer.py")
            st.code("FTS: python3 src_orbis/mqtt/tools/fts_template_analyzer.py")
            
            st.markdown("---")
            
            # Template statistics
            st.metric("Template-Kategorien", len(template_categories))
            st.metric("Analysierte Templates", 0)  # Will be updated when analysis is done
            st.metric("Template Library", "Bereit")

    def show_module_control_rows(self):
        """Show module control in rows with buttons"""
        st.markdown("**Modul-Steuerung zeilenweise:**")

        # Factory Reset Control (before modules)
        st.markdown("---")
        st.markdown("**🏭 Factory Reset Control**")
        
        # Reset options in columns
        col_reset1, col_reset2, col_reset3, col_reset4 = st.columns([2, 1, 1, 1])
        
        with col_reset1:
            reset_with_storage = st.checkbox("Mit Storage zurücksetzen (HBW-Storage löschen)", value=False, 
                                           help="Aktivieren um alle HBW-Storage Daten zu löschen")
        
        with col_reset2:
            if st.session_state.get("mqtt_connected", False):
                if st.button("✅ JA - Zurücksetzen", type="primary", use_container_width=True, key="confirm_reset_mqtt_control"):
                    self.send_factory_reset(reset_with_storage)
                    st.success("🏭 Fabrik wurde erfolgreich zurückgesetzt!")
                    st.rerun()
            else:
                st.button("✅ JA - Zurücksetzen", type="primary", disabled=True, use_container_width=True, key="confirm_reset_mqtt_control_disabled")
        
        with col_reset3:
            st.markdown("")
            st.markdown("*⚠️ Setzt alle Module zurück*")
        
        with col_reset4:
            st.markdown("")
            st.markdown("*🔄 System-Reset*")
        
        st.markdown("---")

        # Show each module in a row with control buttons
        all_modules = self.module_mapping.get_all_modules()
        for module_id, module_info in all_modules.items():
            with st.container():
                # Module header with icon
                # Use get_module_icon function for proper icon handling
                module_name = module_info.get('name', module_id)
                module_key_upper = module_name.upper()
                module_icon = get_module_icon(module_key_upper)
                
                # Display module header with icon
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    # Display icon (image file or emoji)
                    if module_icon and ('/' in module_icon or '\\' in module_icon):
                        # It's a file path - display as image
                        st.image(module_icon, width=48)
                    else:
                        # It's an emoji - display as text
                        st.markdown(f"### {module_icon}")
                
                with col2:
                    st.markdown(f"### {module_info['name']}")
                
                # Module info in columns
                col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
                
                with col1:
                    st.markdown(f"**ID:** `{module_info['id']}`")
                    st.markdown(f"**Typ:** {module_info['type']}")
                
                with col2:
                    # Get first available IP address from ip_addresses list
                    ip_addresses = module_info.get('ip_addresses', [])
                    current_ip = ip_addresses[0] if ip_addresses else "Unknown"
                    st.markdown(f"**IP:** {current_ip}")
                    # Connection status with enhanced icons
                    if st.session_state.get("mqtt_connected", False):
                        st.success(f"{get_status_icon('available')} Online")
                    else:
                        st.error(f"{get_status_icon('offline')} Offline")
                
                with col3:
                    # Show module status or recent activity
                    st.markdown("**Status:**")
                    if st.session_state.get("mqtt_connected", False):
                        st.success("🟢 Online")
                    else:
                        st.error("🔴 Offline")
                
                with col4:
                    st.markdown("**Steuerung:**")
                    
                    # Special sequence control for DRILL, MILL, and AIQS modules
                    module_name = module_info.get('name', module_id)
                    if module_name in ["DRILL", "MILL", "AIQS"]:
                        if module_name == "DRILL":
                            st.markdown("**Steuerung DRILL-Sequenz:**")
                            process_command = "DRILL"
                            process_icon = "⚙️"
                        elif module_name == "MILL":
                            st.markdown("**Steuerung MILL-Sequenz:**")
                            process_command = "MILL"
                            process_icon = "⚙️"
                        elif module_name == "AIQS":
                            st.markdown("**Steuerung AIQS-Sequenz:**")
                            process_command = "CHECK_QUALITY"
                            process_icon = "🔍"
                        
                        # Workpiece selection
                        workpiece_color = st.selectbox(
                            "Werkstück-Farbe:",
                            ["WHITE", "RED", "BLUE"],
                            key=f"{module_name.lower()}_color_{module_id}",
                            index=0  # Default to WHITE
                        )
                        
                        # Workpiece ID selection based on color
                        if workpiece_color == "WHITE":
                            workpiece_options = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"]
                            default_index = 0  # W1
                        elif workpiece_color == "RED":
                            workpiece_options = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
                            default_index = 0  # R1
                        else:  # BLUE
                            workpiece_options = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
                            default_index = 0  # B1
                        
                        workpiece_id = st.selectbox(
                            "Werkstück:",
                            workpiece_options,
                            key=f"{module_name.lower()}_workpiece_{module_id}",
                            index=default_index
                        )
                        
                        # Workpiece-ID wird direkt als NFC-Code verwendet
                        nfc_code = workpiece_id
                        st.info(f"🔍 NFC-Code: `{nfc_code}`")
                        
                        # Sequence buttons
                        col_seq1, col_seq2, col_seq3 = st.columns(3)
                        
                        with col_seq1:
                            if st.button(
                                "📤 PICK",
                                key=f"{module_name.lower()}_pick_{module_id}",
                                use_container_width=True,
                                type="primary"
                            ):
                                self.send_drill_sequence_command(module_id, "PICK", workpiece_color, nfc_code)
                        
                        with col_seq2:
                            if st.button(
                                f"{process_icon} {process_command}",
                                key=f"{module_name.lower()}_process_{module_id}",
                                use_container_width=True,
                                type="primary"
                            ):
                                self.send_drill_sequence_command(module_id, process_command, workpiece_color, nfc_code)
                        
                        with col_seq3:
                            if st.button(
                                "📥 DROP",
                                key=f"{module_name.lower()}_drop_{module_id}",
                                use_container_width=True,
                                type="primary"
                            ):
                                self.send_drill_sequence_command(module_id, "DROP", workpiece_color, nfc_code)
                    
                    # FTS-specific control
                    elif module_name == "FTS":
                        st.markdown("**🚗 FTS-Steuerung:**")
                        
                        # Simple status display (always available)
                        st.info(f"**Status:** 🟢 FTS-Steuerung verfügbar")
                        
                        # FTS control buttons - all always available for now
                        col_fts1, col_fts2, col_fts3, col_fts4 = st.columns(4)
                        
                        with col_fts1:
                            if st.button(
                                "🚗 Docke an",
                                key=f"fts_dock",
                                use_container_width=True,
                                type="primary",
                                help="FTS fährt zum Wareneingang (Initialisierung)"
                            ):
                                self.send_fts_command("findInitialDockPosition", {"nodeId": "SVR4H73275"})
                        
                        with col_fts2:
                            if st.button(
                                "🔋 FTS laden",
                                key=f"fts_charge",
                                use_container_width=True,
                                type="primary",
                                help="FTS fährt zur Charging Station"
                            ):
                                self.send_fts_command("startCharging", {})
                        
                        with col_fts3:
                            if st.button(
                                "⏹️ Laden beenden",
                                key=f"fts_stop_charge",
                                use_container_width=True,
                                type="primary",
                                help="FTS stoppt das Laden"
                            ):
                                self.send_fts_command("stopCharging", {})
                        
                        with col_fts4:
                            if st.button(
                                "🔄 Status abfragen",
                                key=f"fts_status",
                                use_container_width=True,
                                help="FTS Status abfragen"
                            ):
                                self.send_fts_command("factsheetRequest", {})
                    
                    # Standard control buttons for all other modules (HBW, DPS, etc.)
                    else:
                        button_order = []
                    
                    # Ensure button_order is always initialized
                    if 'button_order' not in locals():
                        button_order = []
                    
                    # Add PICK first
                    if "PICK" in module_info["commands"]:
                        button_order.append("PICK")
                    
                    # Add PROCESS commands (MILL, DRILL, CHECK_QUALITY)
                    process_commands = ["MILL", "DRILL", "CHECK_QUALITY"]
                    for cmd in process_commands:
                        if cmd in module_info["commands"] and cmd not in button_order:
                            button_order.append(cmd)
                    
                    # Add other commands (STORE, etc.)
                    for cmd in module_info["commands"]:
                        if cmd not in button_order:
                            button_order.append(cmd)
                    
                    # Add DROP last
                    if "DROP" in module_info["commands"]:
                        if "DROP" in button_order:
                            button_order.remove("DROP")
                        button_order.append("DROP")
                    
                    # Ensure unique commands only
                    button_order = list(dict.fromkeys(button_order))  # Remove duplicates while preserving order
                    
                    # Create buttons in order
                    for command in button_order:
                        button_text = f"▶️ {command}"
                        if command in ["MILL", "DRILL"]:
                            button_text = f"⚙️ {command}"
                        elif command == "CHECK_QUALITY":
                            button_text = f"🔍 {command}"
                        elif command == "STORE":
                            button_text = f"📦 {command}"
                        
                        if st.button(
                            button_text,
                            key=f"control_{module_id}_{command}",
                            use_container_width=True,
                        ):
                            self.send_module_command(module_id, command)
                
                st.markdown("---")

    def show_mqtt_monitor_standalone(self):
        """Show standalone MQTT message monitor"""
        st.header("📡 MQTT Monitor")
        st.markdown("Live-Monitoring von MQTT-Nachrichten und Antworten")

        # Connection status - use session state for consistency
        if not st.session_state.get("mqtt_connected", False):
            st.warning(f"{get_status_icon('offline')} MQTT-Verbindung erforderlich für Monitoring")
            st.info("Verwende die Sidebar zum Verbinden")
            return

        # Overview metrics
        dashboard = st.session_state.get("mqtt_dashboard")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sent_count = len(dashboard.mqtt_messages_sent) if dashboard and hasattr(dashboard, 'mqtt_messages_sent') else 0
            st.metric("📤 Gesendet", sent_count)
        
        with col2:
            received_count = len(dashboard.mqtt_responses) if dashboard and hasattr(dashboard, 'mqtt_responses') else 0
            st.metric("📨 Empfangen", received_count)
        
        with col3:
            if dashboard and hasattr(dashboard, 'mqtt_connected'):
                if dashboard.mqtt_connected:
                    status = f"{get_status_icon('available')} Connected"
                else:
                    status = f"{get_status_icon('offline')} Disconnected"
                st.metric("🔗 Status", status)
            else:
                st.metric("🔗 Status", "❓ Unknown")
        
        with col4:
            if dashboard and hasattr(dashboard, 'mqtt_broker'):
                st.metric("🌐 Broker", dashboard.mqtt_broker)
            else:
                st.metric("🌐 Broker", "Unknown")

        st.markdown("---")

        # Sent messages - use session state dashboard
        st.subheader("📤 Gesendete Nachrichten")
        if dashboard and hasattr(dashboard, 'mqtt_messages_sent') and dashboard.mqtt_messages_sent:
            sent_df = pd.DataFrame(dashboard.mqtt_messages_sent)
            sent_df["timestamp"] = pd.to_datetime(sent_df["timestamp"])
            sent_df = sent_df.sort_values("timestamp", ascending=False)

            # Create display DataFrame with friendly topic names
            sent_df_display = sent_df[["topic", "timestamp", "message", "result"]].copy()
            sent_df_display["friendly_topic"] = sent_df_display["topic"].apply(lambda x: self.topic_manager.get_friendly_name(x))

            # Display recent messages
            for idx, row in sent_df_display.head(10).iterrows():
                # Extract module name from topic
                module_name = self._extract_module_name_from_topic(row['topic'])
                message_type = row['topic'].split('/')[-1]  # 'order' or 'state'
                
                with st.expander(
                    f"📤 {row['timestamp'].strftime('%H:%M:%S')} - {row['friendly_topic']}"
                ):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Topic:** `{row['topic']}`")
                        st.markdown(f"**Module:** {module_name}")
                        st.markdown(f"**Type:** {message_type}")
                        st.markdown(f"**Result:** {row['result']}")
                    with col2:
                        st.json(row["message"])
        else:
            st.info("Noch keine Nachrichten gesendet")

        # Received responses - use session state dashboard
        st.subheader("📨 Empfangene Antworten")
        if dashboard and hasattr(dashboard, 'mqtt_responses') and dashboard.mqtt_responses:
            response_df = pd.DataFrame(dashboard.mqtt_responses)
            response_df["timestamp"] = pd.to_datetime(response_df["timestamp"])
            response_df = response_df.sort_values("timestamp", ascending=False)

            # Create display DataFrame with friendly topic names
            response_df_display = response_df[["topic", "timestamp", "payload", "qos"]].copy()
            response_df_display["friendly_topic"] = response_df_display["topic"].apply(lambda x: self.topic_manager.get_friendly_name(x))

            # Display recent responses
            for idx, row in response_df_display.head(10).iterrows():
                # Extract module name from topic
                module_name = self._extract_module_name_from_topic(row['topic'])
                message_type = row['topic'].split('/')[-1]  # 'order' or 'state'
                
                with st.expander(
                    f"📨 {row['timestamp'].strftime('%H:%M:%S')} - {row['friendly_topic']}"
                ):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Topic:** `{row['topic']}`")
                        st.markdown(f"**Module:** {module_name}")
                        st.markdown(f"**Type:** {message_type}")
                        st.markdown(f"**QoS:** {row['qos']}")
                    with col2:
                        st.json(row["payload"])
        else:
            st.info("Noch keine Antworten empfangen")

        # Control buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Gesendete Nachrichten löschen", use_container_width=True):
                if dashboard and hasattr(dashboard, 'mqtt_messages_sent'):
                    dashboard.mqtt_messages_sent.clear()
                st.success("Gesendete Nachrichten gelöscht")
                st.rerun()

        with col2:
            if st.button("🗑️ Empfangene Antworten löschen", use_container_width=True):
                if dashboard and hasattr(dashboard, 'mqtt_responses'):
                    dashboard.mqtt_responses.clear()
                st.success("Empfangene Antworten gelöscht")
                st.rerun()
        
        with col3:
            if st.button("🔄 Alle löschen", use_container_width=True):
                if dashboard:
                    if hasattr(dashboard, 'mqtt_messages_sent'):
                        dashboard.mqtt_messages_sent.clear()
                    if hasattr(dashboard, 'mqtt_responses'):
                        dashboard.mqtt_responses.clear()
                st.success("Alle Nachrichten gelöscht")
                st.rerun()

    def show_mqtt_monitor(self):
        """Show MQTT message monitor (legacy method for MQTT Control tab)"""
        st.markdown("**MQTT Message Monitor:**")

        # Connection status - use session state for consistency
        if not st.session_state.get("mqtt_connected", False):
            st.warning(f"{get_status_icon('offline')} MQTT-Verbindung erforderlich für Monitoring")
            st.info("Verwende die Sidebar zum Verbinden")
            return

        # Sent messages - use session state dashboard
        st.subheader("📤 Gesendete Nachrichten")
        dashboard = st.session_state.get("mqtt_dashboard")
        if dashboard and hasattr(dashboard, 'mqtt_messages_sent') and dashboard.mqtt_messages_sent:
            sent_df = pd.DataFrame(dashboard.mqtt_messages_sent)
            sent_df["timestamp"] = pd.to_datetime(sent_df["timestamp"])
            sent_df = sent_df.sort_values("timestamp", ascending=False)

            # Display recent messages
            for idx, row in sent_df.head(5).iterrows():
                # Extract module name from topic
                module_name = self._extract_module_name_from_topic(row['topic'])
                message_type = row['topic'].split('/')[-1]  # 'order' or 'state'
                
                with st.expander(
                    f"📤 {row['timestamp'].strftime('%H:%M:%S')} - {module_name}: {message_type}"
                ):
                    st.json(row["message"])
                    st.info(f"Result: {row['result']}")
        else:
            st.info("Noch keine Nachrichten gesendet")

        # Received responses - use session state dashboard
        st.subheader("📨 Empfangene Antworten")
        if dashboard and hasattr(dashboard, 'mqtt_responses') and dashboard.mqtt_responses:
            response_df = pd.DataFrame(dashboard.mqtt_responses)
            response_df["timestamp"] = pd.to_datetime(response_df["timestamp"])
            response_df = response_df.sort_values("timestamp", ascending=False)

            # Display recent responses
            for idx, row in response_df.head(5).iterrows():
                # Extract module name from topic
                module_name = self._extract_module_name_from_topic(row['topic'])
                message_type = row['topic'].split('/')[-1]  # 'order' or 'state'
                
                with st.expander(
                    f"📨 {row['timestamp'].strftime('%H:%M:%S')} - {module_name}: {message_type}"
                ):
                    st.json(row["payload"])
                    st.info(f"QoS: {row['qos']}")
        else:
            st.info("Noch keine Antworten empfangen")

        # Clear buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Gesendete Nachrichten löschen"):
                if dashboard and hasattr(dashboard, 'mqtt_messages_sent'):
                    dashboard.mqtt_messages_sent.clear()
                st.success("Gesendete Nachrichten gelöscht")
                st.rerun()

        with col2:
            if st.button("🗑️ Empfangene Antworten löschen"):
                if dashboard and hasattr(dashboard, 'mqtt_responses'):
                    dashboard.mqtt_responses.clear()
                st.success("Empfangene Antworten gelöscht")
                st.rerun()

    def send_mqtt_message(self, template_name, message_type):
        """Send MQTT message using template (DEPRECATED - Use Template Message Manager)"""
        st.warning("⚠️ Diese Methode ist veraltet. Verwende den Template Message Manager im 'Template Message' Tab.")
        st.info("🎯 Gehe zu 'MQTT Control' → 'Template Message' für die neue Template-Steuerung.")



    def create_sidebar(self):
        """Creates the sidebar with navigation and MQTT broker selection."""
        with st.sidebar:
            st.title("Navigation")

            # Page navigation
            page_options = ["📊 Analyse APS", "🎮 MQTT Control", "🏭 Overview"]
            selected_page = st.radio("Seite auswählen:", page_options)

            st.markdown("---")

            # MQTT Broker Selection
            st.subheader("🔗 MQTT-Verbindung")
            if not self.broker_configs:
                st.warning("Keine Broker-Konfigurationen gefunden.")
                return selected_page

            broker_names = [config["name"] for config in self.broker_configs]
            selected_broker_name = st.selectbox(
                "MQTT-Broker auswählen:",
                broker_names,
                index=0,
                key="selected_broker",
            )

            # Set the selected broker in the dashboard instance
            if selected_broker_name:
                self.set_broker(selected_broker_name)

            # Connection status and button
            if self.mqtt_connected:
                st.success(f"✅ Verbunden mit {self.mqtt_broker}")
                if st.button("Trennen"):
                    self.disconnect_mqtt()
                    st.rerun()
            else:
                st.error("❌ Nicht verbunden")
                if st.button("🔗 Verbinden"):
                    self.connect_mqtt()
                    st.rerun()

            return selected_page

    def run(self):
        """Main application loop."""
        selected_page = self.create_sidebar()

        if selected_page == "📊 Analyse APS":
            if self.connect():
                df = self.load_data()
                self.show_aps_analysis(df)
                self.disconnect()
        elif selected_page == "🎮 MQTT Control":
            self.show_mqtt_control()
        elif selected_page == "🏭 Overview":
            if self.connect():
                df = self.load_data()
                self.show_module_overview_dashboard(df)
                self.disconnect()

    def run_dashboard(self):
        """Run the dashboard"""
        if not self.connect():
            return

        try:
            # Load data
            with st.spinner("Lade Daten..."):
                df = self.load_data()

            if df is None or df.empty:
                st.warning("Keine Daten in der ausgewählten Datenbank gefunden.")
                return
            
            # Store current DataFrame for settings
            self.current_df = df

            # Main content - show selected tab
            if st.session_state.selected_tab == "🏭 Overview":
                self.show_module_overview_dashboard(df)
            elif st.session_state.selected_tab == "📡 MQTT Monitor":
                self.show_mqtt_monitor_standalone()
            elif st.session_state.selected_tab == "🔍 APS Analyse":
                self.aps_analysis.show_aps_analysis_tab()
            elif st.session_state.selected_tab == "🎮 MQTT Control":
                self.show_mqtt_control()
            elif st.session_state.selected_tab == "📚 Template Library":
                self.show_template_library()
            elif st.session_state.selected_tab == "⚙️ Einstellungen":
                self.show_settings()

        finally:
            self.disconnect()
            self.disconnect_mqtt()

    def show_message_template_settings(self):
        """Show Message Template configuration and analysis"""
        st.subheader("📋 Message Template Verwaltung")
        st.markdown("Zentrale Verwaltung der MQTT Message Templates und Template-Analyse")
        
        # Statistics
        stats = self.message_template_manager.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Gesamt Topics", stats["total_topics"])
        with col2:
            st.metric("Kategorien", stats["total_categories"])
        with col3:
            st.metric("Validierungs-Patterns", stats["validation_patterns"])
        with col4:
            st.metric("Cache-Größe", stats["analysis_cache_size"])
        
        st.markdown("---")
        
        # Template Analysis Section
        st.subheader("🔍 Template-Analyse")
        
        # Session selection for analysis
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        session_files = glob.glob(os.path.join(project_root, "mqtt-data/sessions/aps_persistent_traffic_*.db"))
        
        if session_files:
            selected_session = st.selectbox(
                "📁 Session für Template-Analyse auswählen:",
                options=session_files,
                format_func=lambda x: os.path.basename(x).replace('.db', ''),
                help="Wähle eine Session-DB für die Template-Analyse"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Template-Analyse starten", type="primary"):
                    with st.spinner("Analysiere Session-Templates..."):
                        analysis_result = self.message_template_manager.analyze_session_templates(selected_session)
                        
                        if "error" not in analysis_result:
                            st.success(f"✅ Analyse abgeschlossen: {analysis_result['topics_analyzed']} Topics analysiert")
                            
                            # Display analysis results
                            st.subheader("📊 Analyse-Ergebnisse")
                            
                            # Topics overview
                            topics_analyzed = analysis_result.get("topic_analysis", {})
                            if topics_analyzed:
                                topic_data = []
                                for topic, analysis in topics_analyzed.items():
                                    topic_data.append({
                                        "Topic": topic,
                                        "Nachrichten": analysis["message_count"],
                                        "Felder": len(analysis["field_types"]),
                                        "Beispiele": len(analysis["examples"])
                                    })
                                
                                df = pd.DataFrame(topic_data)
                                st.dataframe(df, use_container_width=True)
                            
                            # Template suggestions
                            suggestions = analysis_result.get("template_suggestions", {})
                            if suggestions:
                                st.subheader("💡 Template-Vorschläge")
                                
                                for topic, suggestion in suggestions.items():
                                    with st.expander(f"📋 {topic} ({suggestion['message_count']} Nachrichten)"):
                                        st.write(f"**Kategorie:** {suggestion['category']}")
                                        st.write(f"**Sub-Kategorie:** {suggestion['sub_category']}")
                                        st.write(f"**Beschreibung:** {suggestion['description']}")
                                        
                                        # Template structure
                                        if suggestion.get("template_structure"):
                                            st.write("**Template-Struktur:**")
                                            st.json(suggestion["template_structure"])
                                        
                                        # Validation rules
                                        if suggestion.get("validation_rules"):
                                            st.write("**Validierungsregeln:**")
                                            for rule in suggestion["validation_rules"]:
                                                st.write(f"• {rule}")
                                        
                                        # Examples
                                        if suggestion.get("examples"):
                                            st.write("**Beispiele:**")
                                            for i, example in enumerate(suggestion["examples"][:2]):  # Show first 2
                                                st.write(f"**Beispiel {i+1}:**")
                                                # Handle different example formats
                                                if isinstance(example, dict):
                                                    if "payload" in example:
                                                        st.json(example["payload"])
                                                    else:
                                                        st.json(example)
                                                elif isinstance(example, list):
                                                    st.json(example)
                                                else:
                                                    st.write(str(example))
                        else:
                            st.error(f"❌ Analyse fehlgeschlagen: {analysis_result['error']}")
            
            with col2:
                if st.button("🔄 Cache leeren"):
                    self.message_template_manager.session_analysis_cache.clear()
                    st.success("✅ Cache geleert")
                
                if st.button("📥 Konfiguration neu laden"):
                    self.message_template_manager.reload_config()
                    st.success("✅ Konfiguration neu geladen")
        else:
            st.warning("⚠️ Keine Session-Datenbanken gefunden")
        
        st.markdown("---")
        
        # Template Overview Section
        st.subheader("📚 Template-Übersicht")
        
        # Category filter
        categories = self.message_template_manager.get_categories()
        selected_category = st.selectbox(
            "🏷️ Kategorie filtern:",
            options=["Alle"] + categories,
            help="Filtere Templates nach Kategorie"
        )
        
        # Sub-category filter
        sub_categories = []
        if selected_category != "Alle":
            sub_categories = self.message_template_manager.get_sub_categories(selected_category)
        
        selected_sub_category = None
        if sub_categories:
            selected_sub_category = st.selectbox(
                "📋 Sub-Kategorie filtern:",
                options=["Alle"] + sub_categories,
                help="Filtere Templates nach Sub-Kategorie"
            )
            if selected_sub_category == "Alle":
                selected_sub_category = None
        
        # Module name filter (only for MODULE category)
        module_names = []
        if selected_category == "MODULE":
            # Get module names from module config
            try:
                module_config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'module_config.yml')
                if os.path.exists(module_config_file):
                    import yaml
                    with open(module_config_file, 'r', encoding='utf-8') as f:
                        module_config = yaml.safe_load(f)
                    
                    # Extract module names
                    modules = module_config.get('modules', {})
                    module_names = list(set(module.get('name', '') for module in modules.values() if module.get('name')))
                    module_names.sort()
            except Exception as e:
                st.warning(f"⚠️ Fehler beim Laden der Modul-Konfiguration: {e}")
        
        selected_module_name = None
        if module_names:
            selected_module_name = st.selectbox(
                "🏭 Modul filtern:",
                options=["Alle"] + module_names,
                help="Filtere Templates nach Modul-Namen"
            )
            if selected_module_name == "Alle":
                selected_module_name = None
        
        # Get templates
        if selected_category == "Alle":
            templates = self.message_template_manager.templates.get("topics", {})
        else:
            topic_list = self.message_template_manager.get_topics_by_category(selected_category)
            templates = {topic: self.message_template_manager.templates["topics"][topic] 
                        for topic in topic_list if topic in self.message_template_manager.templates["topics"]}
            
            # Apply sub-category filter if selected
            if selected_sub_category:
                templates = {
                    topic: template for topic, template in templates.items()
                    if template.get('sub_category') == selected_sub_category
                }
            
            # Apply module name filter if selected
            if selected_module_name:
                # Get module ID for the selected module name
                try:
                    module_config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'module_config.yml')
                    if os.path.exists(module_config_file):
                        import yaml
                        with open(module_config_file, 'r', encoding='utf-8') as f:
                            module_config = yaml.safe_load(f)
                        
                        # Find module ID for the selected name
                        modules = module_config.get('modules', {})
                        module_id = None
                        for module_id_key, module_info in modules.items():
                            if module_info.get('name') == selected_module_name:
                                module_id = module_id_key
                                break
                        
                        if module_id:
                            # Filter templates by module ID
                            templates = {
                                topic: template for topic, template in templates.items()
                                if module_id in topic
                            }
                except Exception as e:
                    st.warning(f"⚠️ Fehler beim Filtern nach Modul: {e}")
        
        if templates:
            for topic, template in templates.items():
                # Get module name for display
                module_name = "N/A"
                if template.get('category') == 'MODULE':
                    try:
                        module_config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'module_config.yml')
                        if os.path.exists(module_config_file):
                            import yaml
                            with open(module_config_file, 'r', encoding='utf-8') as f:
                                module_config = yaml.safe_load(f)
                            
                            # Find module name for the topic
                            modules = module_config.get('modules', {})
                            for module_id, module_info in modules.items():
                                if module_id in topic:
                                    module_name = module_info.get('name', module_id)
                                    break
                    except Exception:
                        pass
                
                with st.expander(f"📋 {topic}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Kategorie:** {template.get('category', 'N/A')}")
                        st.write(f"**Sub-Kategorie:** {template.get('sub_category', 'N/A')}")
                    with col2:
                        if template.get('category') == 'MODULE':
                            st.write(f"**Modul:** {module_name}")
                        st.write(f"**Beschreibung:** {template.get('description', 'N/A')}")
                    
                    # Template structure
                    if template.get("template_structure"):
                        st.write("**Template-Struktur:**")
                        structure_data = []
                        for field, field_info in template["template_structure"].items():
                            # Handle different field_info formats
                            if isinstance(field_info, dict):
                                field_type = field_info.get("type", "N/A")
                                is_required = field_info.get("required", False)
                                field_format = field_info.get("format", "N/A")
                                enum_values = field_info.get("enum", [])
                            else:
                                # Handle string format (TXT templates)
                                field_type = str(field_info)
                                is_required = False
                                field_format = "N/A"
                                enum_values = []
                            
                            structure_data.append({
                                "Feld": field,
                                "Typ": field_type,
                                "Erforderlich": "✅" if is_required else "❌",
                                "Format": field_format,
                                "Enum": str(enum_values) if enum_values else "N/A"
                            })
                        
                        df = pd.DataFrame(structure_data)
                        st.dataframe(df, use_container_width=True)
                    
                    # Examples
                    if template.get("examples"):
                        st.write("**Beispiele:**")
                        for i, example in enumerate(template["examples"][:2]):  # Show first 2
                            with st.expander(f"Beispiel {i+1}"):
                                # Handle different example formats
                                if isinstance(example, dict):
                                    if "payload" in example:
                                        st.json(example["payload"])
                                    else:
                                        st.json(example)
                                elif isinstance(example, list):
                                    st.json(example)
                                else:
                                    st.write(str(example))
                    
                    # Validation rules
                    if template.get("validation_rules"):
                        st.write("**Validierungsregeln:**")
                        for rule in template["validation_rules"]:
                            st.write(f"• {rule}")
        else:
            st.info("📝 Keine Templates gefunden")


def main():
    """Main function"""
    # ORBIS Logo in Sidebar
    logo_path = get_logo_path()
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=200)
    else:
        st.sidebar.markdown("## 🏭 ORBIS-Modellfabrik")
    st.sidebar.markdown("*Modellfabrik-Dashboard*")

    # Navigation in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📋 Navigation**")

    # Initialize selected tab in session state
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "🏭 Overview"

    # Tab buttons in sidebar with active highlighting
    tabs = [
        ("🏭 Overview", "🏭 Overview"),
        ("📡 MQTT Monitor", "📡 MQTT Monitor"),
        ("🔍 APS Analyse", "🔍 APS Analyse"),
        ("🎮 MQTT Control", "🎮 MQTT Control"),
        ("📚 Template Library", "📚 Template Library"),
        ("⚙️ Einstellungen", "⚙️ Einstellungen")
    ]
    
    for tab_name, tab_key in tabs:
        is_active = st.session_state.selected_tab == tab_key
        
        if st.sidebar.button(
            tab_name,
            use_container_width=True,
            key=f"nav_{tab_key}",
            disabled=is_active,
            type="primary" if is_active else "secondary"
        ):
            if not is_active:
                st.session_state.selected_tab = tab_key
                st.rerun()

    # Initialize session state
    if "dashboard_loaded" not in st.session_state:
        st.session_state.dashboard_loaded = False
    if "selected_db" not in st.session_state:
        st.session_state.selected_db = None
    if "verbose_mode" not in st.session_state:
        st.session_state.verbose_mode = False
    if "show_reset_modal" not in st.session_state:
        st.session_state.show_reset_modal = False


    # Session management moved to APS Analysis tab
    # Get project root (3 levels up from dashboard)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

    # Search in sessions directory only
    db_files = glob.glob(
        os.path.join(project_root, "mqtt-data/sessions/aps_persistent_traffic_*.db")
    )

    if not db_files:
        st.sidebar.error("Keine APS-Datenbanken gefunden!")
        st.sidebar.info(
            "Führe zuerst den Logger aus: `python src-orbis/aps_persistent_logger.py`"
        )
        return

    # Auto-select first database if none selected
    if (
        st.session_state.selected_db is None
        or st.session_state.selected_db not in db_files
    ):
        st.session_state.selected_db = db_files[0] if db_files else None
    
    # MQTT Connection status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔗 MQTT-Verbindung**")
    
    # Store MQTT connection status in session state
    if "mqtt_connected" not in st.session_state:
        st.session_state.mqtt_connected = False
    
    # MQTT Connection status and controls
    if st.session_state.mqtt_connected:
        st.sidebar.success(f"{get_status_icon('available')} Connected")
        if st.sidebar.button("🔌 Disconnect", key="disconnect_mqtt_sidebar"):
            # Disconnect MQTT dashboard if exists
            if "mqtt_dashboard" in st.session_state and st.session_state.mqtt_dashboard:
                st.session_state.mqtt_dashboard.disconnect_mqtt()
            st.session_state.mqtt_connected = False
            st.session_state.mqtt_dashboard = None
            st.rerun()
    else:
        st.sidebar.error(f"{get_status_icon('offline')} Not connected")
        if st.sidebar.button("🔗 Connect", key="connect_mqtt_sidebar"):
            if st.session_state.selected_db:
                # Create dashboard instance and store in session state
                dashboard = APSDashboard(st.session_state.selected_db, verbose_mode=st.session_state.verbose_mode)
                if dashboard.connect_mqtt():
                    st.session_state.mqtt_connected = True
                    st.session_state.mqtt_dashboard = dashboard
                    st.rerun()
                else:
                    st.sidebar.error("❌ Connection failed")
                    st.session_state.mqtt_connected = False
                    st.session_state.mqtt_dashboard = None

    # Auto-select first database if none selected
    if (
        st.session_state.selected_db is None
        or st.session_state.selected_db not in db_files
    ):
        st.session_state.selected_db = db_files[0] if db_files else None

    # Auto-start if database is available
    if st.session_state.selected_db and not st.session_state.dashboard_loaded:
        st.session_state.dashboard_loaded = True

    # Run dashboard if loaded
    if st.session_state.dashboard_loaded:
        dashboard = APSDashboard(
            st.session_state.selected_db, verbose_mode=st.session_state.verbose_mode
        )
        dashboard.run_dashboard()


if __name__ == "__main__":
    main()
