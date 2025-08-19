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
from src_orbis.mqtt.dashboard.config.settings import APS_MODULES_EXTENDED
from src_orbis.mqtt.dashboard.utils.data_handling import extract_module_info
from src_orbis.mqtt.dashboard.components.filters import create_filters
from src_orbis.mqtt.tools.mqtt_message_library import (
    MQTTMessageLibrary,
    create_message_from_template,
    list_available_templates,
    get_template_info,
)

# Page config
st.set_page_config(
    page_title="APS MQTT Dashboard",
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

        # Initialize MQTT message library
        self.message_library = MQTTMessageLibrary()

        # Load broker configurations
        self.broker_configs = load_broker_config()

        # Set module definitions from config
        self.aps_modules_extended = APS_MODULES_EXTENDED

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
            for module_name, module_info in self.aps_modules_extended.items():
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

    def create_filters(self, df):
        """Create filters for APS analysis"""
        st.subheader("🔍 Filter")

        # Initialize filter states
        if "selected_date" not in st.session_state:
            st.session_state.selected_date = None
        if "selected_session" not in st.session_state:
            st.session_state.selected_session = "Alle"
        if "selected_process" not in st.session_state:
            st.session_state.selected_process = "Alle"
        if "selected_module" not in st.session_state:
            st.session_state.selected_module = "Alle"
        if "selected_status" not in st.session_state:
            st.session_state.selected_status = "Alle"
        if "selected_topic" not in st.session_state:
            st.session_state.selected_topic = "Alle"

        col1, col2 = st.columns(2)
        df_filtered = df

        with col1:
            # Date range filter
            if not df.empty:
                min_date = df["date"].min()
                max_date = df["date"].max()
                
                # Reset selected_date if it's outside the current data range
                if (st.session_state.selected_date and 
                    (st.session_state.selected_date < min_date or 
                     st.session_state.selected_date > max_date)):
                    st.session_state.selected_date = None
                
                default_date = (
                    st.session_state.selected_date
                    if st.session_state.selected_date
                    else max_date
                )
                selected_date = st.date_input(
                    "Datum", value=default_date, min_value=min_date, max_value=max_date
                )
                st.session_state.selected_date = selected_date
                df_filtered = df[df["date"] == selected_date]

            # Session filter
            sessions = ["Alle"] + list(df["session_label"].unique())
            selected_session = st.selectbox(
                "Session",
                sessions,
                index=(
                    0
                    if st.session_state.selected_session == "Alle"
                    else (
                        sessions.index(st.session_state.selected_session)
                        if st.session_state.selected_session in sessions
                        else 0
                    )
                ),
            )
            st.session_state.selected_session = selected_session
            if selected_session != "Alle":
                df_filtered = df_filtered[
                    df_filtered["session_label"] == selected_session
                ]

            # Process filter
            processes = ["Alle"] + list(df["process_label"].unique())
            selected_process = st.selectbox(
                "Prozess",
                processes,
                index=(
                    0
                    if st.session_state.selected_process == "Alle"
                    else (
                        processes.index(st.session_state.selected_process)
                        if st.session_state.selected_process in processes
                        else 0
                    )
                ),
            )
            st.session_state.selected_process = selected_process
            if selected_process != "Alle":
                df_filtered = df_filtered[
                    df_filtered["process_label"] == selected_process
                ]

        with col2:
            # Module filter
            modules = ["Alle"] + list(df["module_type"].unique())
            selected_module = st.selectbox(
                "Modul",
                modules,
                index=(
                    0
                    if st.session_state.selected_module == "Alle"
                    else (
                        modules.index(st.session_state.selected_module)
                        if st.session_state.selected_module in modules
                        else 0
                    )
                ),
            )
            st.session_state.selected_module = selected_module
            if selected_module != "Alle":
                df_filtered = df_filtered[df_filtered["module_type"] == selected_module]

            # Status filter
            statuses = ["Alle"] + list(df["status"].unique())
            selected_status = st.selectbox(
                "Status",
                statuses,
                index=(
                    0
                    if st.session_state.selected_status == "Alle"
                    else (
                        statuses.index(st.session_state.selected_status)
                        if st.session_state.selected_status in statuses
                        else 0
                    )
                ),
            )
            st.session_state.selected_status = selected_status
            if selected_status != "Alle":
                df_filtered = df_filtered[df_filtered["status"] == selected_status]

            # Topic filter
            topics = ["Alle"] + list(df["topic"].unique())
            selected_topic = st.selectbox(
                "Topic",
                topics,
                index=(
                    0
                    if st.session_state.selected_topic == "Alle"
                    else (
                        topics.index(st.session_state.selected_topic)
                        if st.session_state.selected_topic in topics
                        else 0
                    )
                ),
            )
            st.session_state.selected_topic = selected_topic
            if selected_topic != "Alle":
                df_filtered = df_filtered[df_filtered["topic"] == selected_topic]

        # Filter reset button
        if st.button("🔄 Filter zurücksetzen"):
            st.session_state.selected_date = None
            st.session_state.selected_session = "Alle"
            st.session_state.selected_process = "Alle"
            st.session_state.selected_module = "Alle"
            st.session_state.selected_status = "Alle"
            st.session_state.selected_topic = "Alle"
            st.rerun()

        st.markdown(f"**Gefilterte Nachrichten:** {len(df_filtered):,}")
        if len(df_filtered) == 0:
            st.warning("⚠️ Keine Nachrichten mit den gewählten Filtern gefunden!")
            st.info(
                "💡 Tipp: Versuche andere Filter-Kombinationen oder aktiviere den Verbose-Modus"
            )

        return df_filtered

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
            # Select columns to display (including serial number)
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

            # Show table with selected columns
            st.dataframe(
                df[available_columns].head(1000),  # Limit to 1000 rows
                use_container_width=True,
            )

            # Show total count
            st.info(f"Zeige {min(len(df), 1000)} von {len(df):,} Nachrichten")
        else:
            st.warning("Keine Nachrichten mit den gewählten Filtern gefunden.")

    def show_topic_analysis(self, df):
        """Show topic analysis"""
        st.header("📡 Topic-Analyse")

        if not df.empty:
            col1, col2 = st.columns(2)

            with col1:
                # Top topics
                topic_counts = df["topic"].value_counts().head(10)
                fig = px.bar(
                    x=topic_counts.values,
                    y=topic_counts.index,
                    orientation="h",
                    title="Top 10 Topics",
                )
                fig.update_layout(xaxis_title="Anzahl", yaxis_title="Topic")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Topic word cloud (simplified)
                topic_text = " ".join(df["topic"].astype(str))
                st.subheader("Topic-Übersicht")
                st.text_area(
                    "Alle Topics (erste 1000 Zeichen):", topic_text[:1000], height=200
                )

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
            # Try to extract JSON data
            json_payloads = []
            for payload in df["payload"].dropna():
                try:
                    data = json.loads(payload)
                    json_payloads.append(data)
                except:
                    continue

            if json_payloads:
                st.subheader("JSON Payload Struktur")

                # Show sample payload
                sample_payload = json_payloads[0]
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
                    st.subheader("Häufige Felder in JSON Payloads")
                    field_df = pd.DataFrame(
                        list(common_fields.items()), columns=["Feld", "Anzahl"]
                    )
                    st.dataframe(field_df.sort_values("Anzahl", ascending=False))
            else:
                st.info("Keine JSON Payloads gefunden.")

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
            ["Module Overview", "Template Message", "MQTT Monitor"],
        )

        if control_method == "Module Overview":
            self.show_module_control_rows()
        elif control_method == "Template Message":
            self.show_template_control()
        elif control_method == "MQTT Monitor":
            self.show_mqtt_monitor()

    def show_template_control(self):
        """Show template-based MQTT control"""
        st.markdown("**Verwende vordefinierte, funktionierende MQTT-Nachrichten:**")

        # Get available templates
        templates = list_available_templates()

        if not templates:
            st.warning("Keine Templates verfügbar!")
            return

        # Template selection
        selected_template = st.selectbox("Template auswählen:", templates)

        if selected_template:
            # Show template info
            template_info = get_template_info(selected_template)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Template Details:**")
                st.markdown(f"• **Modul:** {template_info['module']}")
                st.markdown(f"• **Befehl:** {template_info['command']}")
                st.markdown(f"• **Beschreibung:** {template_info['description']}")
                st.markdown(
                    f"• **Erwartete Antwort:** {template_info['expected_response']}"
                )
                st.markdown(f"• **Notizen:** {template_info['notes']}")

            with col2:
                st.markdown("**MQTT Message:**")
                try:
                    message = create_message_from_template(selected_template)
                    st.json(message)
                except Exception as e:
                    st.error(f"Fehler beim Erstellen der Nachricht: {e}")

            # Send button
            if st.button(f"📤 {selected_template} senden", type="primary"):
                self.send_mqtt_message(selected_template, "template")



    def show_aps_analysis(self, df):
        """Show comprehensive APS data analysis"""
        st.header("📊 APS Analyse MQTT")
        st.markdown("Umfassende Analyse der APS-Daten aus den Sessions")

        # Session management section
        st.subheader("🗄️ Session-Verwaltung")
        
        # Get project root (3 levels up from dashboard)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        
        # Search in sessions directory only
        db_files = glob.glob(
            os.path.join(project_root, "mqtt-data/sessions/aps_persistent_traffic_*.db")
        )
        
        if db_files:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Database selection dropdown
                selected_db = st.selectbox(
                    "Session auswählen:",
                    db_files,
                    index=(
                        0
                        if st.session_state.selected_db is None
                        or st.session_state.selected_db not in db_files
                        else db_files.index(st.session_state.selected_db)
                    ),
                    format_func=lambda x: os.path.basename(x)
                    .replace("aps_persistent_traffic_", "")
                    .replace(".db", ""),
                )
                
                if selected_db != st.session_state.selected_db:
                    st.session_state.selected_db = selected_db
                    st.rerun()
            
            with col2:
                # Database info
                if st.session_state.selected_db:
                    db_size = os.path.getsize(st.session_state.selected_db) / (1024 * 1024)
                    st.info(f"**Größe:** {db_size:.2f} MB")
        else:
            st.error("Keine APS-Datenbanken gefunden!")
            st.info(
                "Führe zuerst den Logger aus: `python src_orbis/aps_persistent_logger.py`"
            )
            return

        # Verbose mode toggle
        verbose_mode = st.checkbox(
            "🔍 Verbose-Modus (alle Topics anzeigen)", value=self.verbose_mode
        )
        if verbose_mode != self.verbose_mode:
            self.verbose_mode = verbose_mode
            st.rerun()

        # Create filters
        df_filtered = self.create_filters(df)

        st.markdown("---")

        # Analysis sub-tabs
        (
            analysis_tab1,
            analysis_tab2,
            analysis_tab3,
            analysis_tab4,
            analysis_tab5,
            analysis_tab6,
        ) = st.tabs(
            [
                "📊 Übersicht",
                "⏰ Timeline",
                "📋 Nachrichten",
                "📡 Topics",
                "📦 Payload",
                "🏷️ Sessions",
            ]
        )

        with analysis_tab1:
            self.show_overview(df_filtered)

        with analysis_tab2:
            self.show_timeline(df_filtered)

        with analysis_tab3:
            self.show_message_table(df_filtered)

        with analysis_tab4:
            self.show_topic_analysis(df_filtered)

        with analysis_tab5:
            self.show_payload_analysis(df_filtered)

        with analysis_tab6:
            self.show_session_analysis(df_filtered)

    def show_module_overview_dashboard(self, df):
        """Show comprehensive module overview dashboard"""
        st.header("🏭 Module Overview")
        st.markdown("Übersicht aller APS-Module mit Status und Steuerungsmöglichkeiten")

        st.markdown("---")

        # Module table
        st.subheader("📋 Module Status")

        # Create module table data
        module_table_data = []
        for module_key, module_info in self.aps_modules_extended.items():
            # Get availability status
            recent_messages = df[df["topic"].str.contains(module_info["id"], na=False)]
            availability_status = self.extract_availability_status(
                recent_messages, module_info["id"]
            )

            # Connection status - use session state for consistency
            connection_status = (
                "🟢 Connected" if st.session_state.get("mqtt_connected", False) else "🔴 Disconnected"
            )

            # Activity status
            if availability_status:
                if availability_status == "AVAILABLE":
                    activity_display = "🟢 Available"
                elif availability_status == "BUSY":
                    activity_display = "🟡 Busy"
                elif availability_status == "BLOCKED":
                    activity_display = "🔴 Blocked"
                else:
                    activity_display = f"⚪ {availability_status}"
            else:
                if len(recent_messages) > 0:
                    activity_display = "🟡 Active"
                else:
                    activity_display = "⚪ No Data"

            # Commands as string
            commands_str = ", ".join(module_info["commands"])

            module_table_data.append(
                {
                    "ID": module_info["id"],
                    "Name": f"{module_info['icon']} {module_info['name']}",
                    "Type": module_info["type"],
                    "IP": module_info["ip"],
                    "Connected": connection_status,
                    "Activity Status": activity_display,
                    "Commands": commands_str,
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
                "Commands": st.column_config.TextColumn("Commands", width="large"),
                "Recent Messages": st.column_config.NumberColumn(
                    "Recent Messages", width="small"
                ),
            },
        )

        # Module control moved to MQTT Control tab
        st.info("🎮 **Module Control** ist jetzt im **MQTT Control** Tab verfügbar")

        # Module statistics
        st.markdown("---")
        st.subheader("📊 Module Statistiken")

        col1, col2 = st.columns(2)

        with col1:
            # Module types
            module_types = {}
            for module_info in self.aps_modules_extended.values():
                module_type = module_info["type"]
                module_types[module_type] = module_types.get(module_type, 0) + 1

            fig_types = px.pie(
                values=list(module_types.values()),
                names=list(module_types.keys()),
                title="Module nach Typ",
            )
            st.plotly_chart(fig_types, use_container_width=True)

        with col2:
            # Command distribution
            all_commands = []
            for module_info in self.aps_modules_extended.values():
                all_commands.extend(module_info["commands"])

            command_counts = pd.Series(all_commands).value_counts()
            fig_commands = px.bar(
                x=command_counts.index,
                y=command_counts.values,
                title="Befehls-Verteilung",
                labels={"x": "Befehl", "y": "Anzahl Module"},
            )
            st.plotly_chart(fig_commands, use_container_width=True)

    def show_module_row(self, module_key, module_info, df):
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
                        key=f"cmd_{module_key}_{command}",
                        use_container_width=True,
                    ):
                        self.send_module_command(module_key, command)

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

    def show_module_card(self, module_key, module_info, df):
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
                    if st.button(f"▶️", key=f"cmd_{module_key}_{command}"):
                        self.send_module_command(module_key, command)

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
            # Map serial to module name
            for module_name, module_info in self.aps_modules_extended.items():
                if module_info['id'] == serial:
                    return module_name
        return "Unknown"

    def send_module_command(self, module_key, command):
        """Send command to specific module"""
        try:
            if not self.mqtt_connected:
                if not self.connect_mqtt():
                    st.error("MQTT-Verbindung fehlgeschlagen")
                    return

            # Get module info
            module_info = self.aps_modules_extended[module_key]

            # Create message based on module type
            if module_key == "FTS":
                # Special handling for FTS commands
                message = self.create_fts_message(command)
                topic = f"module/v1/ff/{module_info['id']}/order"
            else:
                # Standard APS module commands
                message = self.message_library.create_order_message(module_key, command)
                topic = self.message_library.get_topic(module_key, "order")

            # Send message
            success, result_message = self.send_mqtt_message_direct(topic, message)

            if success:
                st.success(f"✅ Befehl gesendet: {module_key} - {command}")
                st.info(f"📡 Topic: {topic}")
            else:
                st.error(f"❌ Fehler: {result_message}")

        except Exception as e:
            st.error(f"❌ Fehler beim Senden: {e}")

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

    def show_settings(self):
        """Show dashboard settings"""
        st.header("⚙️ Einstellungen")
        st.markdown("Dashboard-Konfiguration und System-Informationen")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔧 Dashboard-Einstellungen")

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
            st.metric("Aktive Module", len(self.aps_modules_extended))
            st.metric(
                "Verfügbare Befehle",
                sum(
                    len(module["commands"])
                    for module in self.aps_modules_extended.values()
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
            st.metric("Template-Nachrichten", len(list_available_templates()))
            st.metric("Session-Datenbanken", len(glob.glob(os.path.join(os.path.dirname(self.db_file), "aps_persistent_traffic_*.db"))))

    def show_module_control_rows(self):
        """Show module control in rows with buttons"""
        st.markdown("**Modul-Steuerung zeilenweise:**")

        # Show each module in a row with control buttons
        for module_key, module_info in self.aps_modules_extended.items():
            with st.container():
                # Module header
                st.markdown(f"### {module_info['icon']} {module_info['name']}")
                
                # Module info in columns
                col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
                
                with col1:
                    st.markdown(f"**ID:** `{module_info['id']}`")
                    st.markdown(f"**Typ:** {module_info['type']}")
                
                with col2:
                    st.markdown(f"**IP:** {module_info['ip']}")
                    # Connection status
                    if st.session_state.get("mqtt_connected", False):
                        st.success("🟢 Online")
                    else:
                        st.error("🔴 Offline")
                
                with col3:
                    st.markdown("**Verfügbare Befehle:**")
                    for command in module_info["commands"]:
                        st.markdown(f"• {command}")
                
                with col4:
                    st.markdown("**Steuerung:**")
                    # Control buttons in logical order: PICK -> PROCESS -> DROP
                    button_order = []
                    
                    # Add PICK first
                    if "PICK" in module_info["commands"]:
                        button_order.append("PICK")
                    
                    # Add PROCESS commands (MILL, DRILL, CHECK_QUALITY)
                    process_commands = ["MILL", "DRILL", "CHECK_QUALITY"]
                    for cmd in process_commands:
                        if cmd in module_info["commands"]:
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
                            key=f"control_{module_key}_{command}",
                            use_container_width=True,
                        ):
                            self.send_module_command(module_key, command)
                
                st.markdown("---")

    def show_mqtt_monitor(self):
        """Show MQTT message monitor"""
        st.markdown("**MQTT Message Monitor:**")

        # Connection status - use session state for consistency
        if not st.session_state.get("mqtt_connected", False):
            st.warning("⚠️ MQTT-Verbindung erforderlich für Monitoring")
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
        """Send MQTT message using template"""
        try:
            # Create message from template
            message = create_message_from_template(template_name)
            template_info = get_template_info(template_name)
            module_name = template_info["module"]

            # Get topic
            topic = self.message_library.get_topic(module_name, "order")

            # Send message
            success, result_message = self.send_mqtt_message_direct(topic, message)

            if success:
                st.success(f"✅ MQTT-Nachricht gesendet: {template_name}")
                st.info(f"📡 Topic: {topic}")
                st.json(message)
            else:
                st.error(f"❌ MQTT-Versand fehlgeschlagen: {result_message}")

        except Exception as e:
            st.error(f"❌ Fehler beim Senden der Template-Nachricht: {e}")



    def create_sidebar(self):
        """Creates the sidebar with navigation and MQTT broker selection."""
        with st.sidebar:
            st.title("Navigation")

            # Page navigation
            page_options = ["📊 Analyse APS", "🎮 MQTT Control", "🏭 Module Overview"]
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
        elif selected_page == "🏭 Module Overview":
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

            # Main content - show selected tab
            if st.session_state.selected_tab == "🏭 Module Overview":
                self.show_module_overview_dashboard(df)
            elif st.session_state.selected_tab == "📊 Analyse APS":
                self.show_aps_analysis(df)
            elif st.session_state.selected_tab == "🎮 MQTT Control":
                self.show_mqtt_control()
            elif st.session_state.selected_tab == "⚙️ Einstellungen":
                self.show_settings()

        finally:
            self.disconnect()
            self.disconnect_mqtt()


def main():
    """Main function"""
    st.sidebar.title("ORBIS-Modellfabrik Dashboard")

    # Navigation in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📋 Navigation**")

    # Initialize selected tab in session state
    if "selected_tab" not in st.session_state:
        st.session_state.selected_tab = "🏭 Module Overview"

    # Tab buttons in sidebar with active highlighting
    tabs = [
        ("🏭 Module Overview", "🏭 Module Overview"),
        ("📊 Analyse APS", "📊 Analyse APS"), 
        ("🎮 MQTT Control", "🎮 MQTT Control"),
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
        st.sidebar.success("✅ Connected")
        if st.sidebar.button("🔌 Disconnect", key="disconnect_mqtt_sidebar"):
            # Disconnect MQTT dashboard if exists
            if "mqtt_dashboard" in st.session_state and st.session_state.mqtt_dashboard:
                st.session_state.mqtt_dashboard.disconnect_mqtt()
            st.session_state.mqtt_connected = False
            st.session_state.mqtt_dashboard = None
            st.rerun()
    else:
        st.sidebar.error("❌ Not connected")
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
