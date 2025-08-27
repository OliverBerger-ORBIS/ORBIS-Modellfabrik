import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import sqlite3
import os
import time
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
from pathlib import Path
import threading
import queue
import sys

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from mqtt.tools.template_library_manager import TemplateLibraryManager

class APSDashboard:
    def __init__(self, db_file=None):
        """Initialize the APS Dashboard"""
        self.db_file = db_file or "mqtt-data/aps_dashboard.db"
        self.mqtt_client = None
        self.mqtt_connected = False
        self.message_queue = queue.Queue()
        self.last_messages = []
        self.max_messages = 1000
        
        # Initialize Template Library Manager
        self.template_library = TemplateLibraryManager()
        
        # Initialize database
        self.init_database()
        
        # Initialize MQTT connection
        self.init_mqtt()
    
    def init_database(self):
        """Initialize the SQLite database"""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                topic TEXT NOT NULL,
                payload TEXT NOT NULL,
                session TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create topics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE NOT NULL,
                friendly_name TEXT,
                category TEXT,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                topic TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_mqtt(self):
        """Initialize MQTT connection"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message
            self.mqtt_client.on_disconnect = self.on_disconnect
            
            # Connect to MQTT broker
            self.mqtt_client.connect("localhost", 1883, 60)
            self.mqtt_client.loop_start()
            
        except Exception as e:
            st.error(f"MQTT connection failed: {e}")
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.mqtt_connected = True
            # Subscribe to all topics
            client.subscribe("#")
            st.success("✅ Connected to MQTT broker")
        else:
            st.error(f"❌ MQTT connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            # Parse payload
            if msg.payload:
                payload = msg.payload.decode('utf-8')
            else:
                payload = ""
            
            # Add to queue
            message = {
                'timestamp': datetime.now().isoformat(),
                'topic': msg.topic,
                'payload': payload,
                'session': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            self.message_queue.put(message)
            
            # Store in database
            self.store_message(message)
            
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.mqtt_connected = False
        if rc != 0:
            st.warning("⚠️ MQTT connection lost")
    
    def store_message(self, message):
        """Store message in database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (timestamp, topic, payload, session)
                VALUES (?, ?, ?, ?)
            ''', (message['timestamp'], message['topic'], message['payload'], message['session']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing message: {e}")
    
    def send_mqtt_message(self, topic, payload):
        """Send MQTT message"""
        if self.mqtt_connected and self.mqtt_client:
            try:
                self.mqtt_client.publish(topic, payload)
                st.success(f"✅ Message sent to {topic}")
                return True
            except Exception as e:
                st.error(f"❌ Failed to send message: {e}")
                return False
        else:
            st.error("❌ MQTT not connected")
            return False
    
    def disconnect_mqtt(self):
        """Disconnect from MQTT"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
    
    def get_recent_messages(self, limit=100):
        """Get recent messages from database"""
        try:
            conn = sqlite3.connect(self.db_file)
            df = pd.read_sql_query('''
                SELECT * FROM messages 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', conn, params=(limit,))
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error loading messages: {e}")
            return pd.DataFrame()
    
    def get_topic_stats(self):
        """Get topic statistics"""
        try:
            conn = sqlite3.connect(self.db_file)
            df = pd.read_sql_query('''
                SELECT topic, COUNT(*) as message_count,
                       MIN(created_at) as first_seen,
                       MAX(created_at) as last_seen
                FROM messages 
                GROUP BY topic
                ORDER BY message_count DESC
            ''', conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error loading topic stats: {e}")
            return pd.DataFrame()
    
    def show_dashboard(self):
        """Show the main dashboard"""
        st.set_page_config(
            page_title="ORBIS APS Dashboard",
            page_icon="🏭",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🏭 ORBIS APS Dashboard")
        
        # Sidebar
        self.show_sidebar()
        
        # Main content
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dashboard",
            "📡 MQTT Control", 
            "📋 Template Control",
            "⚙️ Einstellungen",
            "📚 Template Library"
        ])
        
        with tab1:
            self.show_main_dashboard()
        
        with tab2:
            self.show_mqtt_control()
        
        with tab3:
            self.show_template_control()
        
        with tab4:
            self.show_settings()
        
        with tab5:
            self.show_template_library()
    
    def show_sidebar(self):
        """Show sidebar with status and controls"""
        with st.sidebar:
            st.header("🔧 Dashboard Controls")
            
            # MQTT Status
            if self.mqtt_connected:
                st.success("🟢 MQTT Connected")
            else:
                st.error("🔴 MQTT Disconnected")
            
            # Connection controls
            if st.button("🔄 Reconnect MQTT"):
                self.init_mqtt()
            
            st.markdown("---")
            
            # Quick stats
            df_messages = self.get_recent_messages(1000)
            if not df_messages.empty:
                st.metric("Total Messages", len(df_messages))
                st.metric("Unique Topics", df_messages['topic'].nunique())
            
            st.markdown("---")
            
            # Template Library Status
            if self.template_library:
                templates = self.template_library.get_all_templates()
                st.metric("Templates in Library", len(templates))
            else:
                st.warning("Template Library not available")
    
    def show_main_dashboard(self):
        """Show main dashboard with overview"""
        st.header("📊 Dashboard Overview")
        
        # Get recent data
        df_messages = self.get_recent_messages(1000)
        df_topics = self.get_topic_stats()
        
        if df_messages.empty:
            st.info("📭 No messages received yet")
            return
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Messages", len(df_messages))
        
        with col2:
            st.metric("Unique Topics", df_messages['topic'].nunique())
        
        with col3:
            st.metric("Active Sessions", df_messages['session'].nunique())
        
        with col4:
            latest_time = pd.to_datetime(df_messages['timestamp'].max())
            st.metric("Latest Message", latest_time.strftime("%H:%M:%S"))
        
        st.markdown("---")
        
        # Message timeline
        st.subheader("📈 Message Timeline")
        
        if len(df_messages) > 1:
            df_messages['timestamp'] = pd.to_datetime(df_messages['timestamp'])
            df_messages['hour'] = df_messages['timestamp'].dt.hour
            
            hourly_counts = df_messages.groupby('hour').size().reset_index(name='count')
            
            fig = px.line(hourly_counts, x='hour', y='count', 
                         title="Messages per Hour")
            st.plotly_chart(fig, use_container_width=True)
        
        # Top topics
        st.subheader("📡 Top Topics")
        
        if not df_topics.empty:
            top_topics = df_topics.head(10)
            
            fig = px.bar(top_topics, x='topic', y='message_count',
                        title="Message Count by Topic")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent messages
        st.subheader("📨 Recent Messages")
        
        recent_messages = df_messages.head(20)
        for _, msg in recent_messages.iterrows():
            with st.expander(f"{msg['topic']} - {msg['timestamp']}", expanded=False):
                st.json(json.loads(msg['payload']) if msg['payload'] else {})
    
    def show_mqtt_control(self):
        """Show MQTT control interface"""
        st.header("📡 MQTT Control")
        
        # Message sending
        st.subheader("📤 Send Message")
        
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input("Topic:", value="test/topic")
        
        with col2:
            payload_type = st.selectbox("Payload Type:", ["JSON", "Text"])
        
        if payload_type == "JSON":
            payload = st.text_area("JSON Payload:", value='{"key": "value"}')
        else:
            payload = st.text_area("Text Payload:", value="Hello World")
        
        if st.button("📤 Send Message"):
            self.send_mqtt_message(topic, payload)
        
        st.markdown("---")
        
        # Template messages
        st.subheader("📋 Template Messages")
        
        templates = {
            "DRILL-PICK_WHITE": {
                "topic": "j1/txt/1/f/o/order",
                "payload": '{"command": "DRILL-PICK", "color": "WHITE", "orderId": "12345"}'
            },
            "DRILL-PICK_BLUE": {
                "topic": "j1/txt/1/f/o/order", 
                "payload": '{"command": "DRILL-PICK", "color": "BLUE", "orderId": "12345"}'
            },
            "MILL-PICK_RED": {
                "topic": "j1/txt/1/f/o/order",
                "payload": '{"command": "MILL-PICK", "color": "RED", "orderId": "12345"}'
            }
        }
        
        for name, template in templates.items():
            with st.expander(name, expanded=False):
                st.text(f"Topic: {template['topic']}")
                st.json(json.loads(template['payload']))
                
                if st.button(f"Send {name}", key=f"send_{name}"):
                    self.send_mqtt_message(template['topic'], template['payload'])
    
    def show_template_control(self):
        """Show template control interface"""
        st.header("📋 Template Control")
        
        # Template Library Overview
        if self.template_library:
            templates = self.template_library.get_all_templates()
            
            st.subheader("📚 Template Library")
            
            if templates:
                st.success(f"✅ {len(templates)} templates available")
                
                # Template categories
                categories = {}
                for template in templates:
                    category = template.get('category', 'Unknown')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(template)
                
                for category, cat_templates in categories.items():
                    with st.expander(f"{category} ({len(cat_templates)} templates)", expanded=False):
                        for template in cat_templates:
                            st.markdown(f"**{template['topic']}**")
                            st.markdown(f"*{template.get('description', 'No description')}*")
                            st.markdown("---")
            else:
                st.info("📭 No templates in library")
        else:
            st.error("❌ Template Library not available")
    
    def show_settings(self):
        """Show settings interface"""
        st.header("⚙️ Settings")
        
        st.subheader("🔧 Dashboard Settings")
        
        # Message retention
        retention_days = st.slider("Message Retention (days)", 1, 30, 7)
        
        if st.button("🗑️ Clean Old Messages"):
            self.clean_old_messages(retention_days)
        
        st.markdown("---")
        
        # MQTT Settings
        st.subheader("📡 MQTT Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            mqtt_host = st.text_input("MQTT Host:", value="localhost")
        
        with col2:
            mqtt_port = st.number_input("MQTT Port:", value=1883, min_value=1, max_value=65535)
        
        if st.button("🔗 Update MQTT Connection"):
            # Reconnect with new settings
            if self.mqtt_client:
                self.mqtt_client.disconnect()
            self.init_mqtt()
    
    def show_template_library(self):
        """Show template library interface"""
        st.header("📚 Template Library")
        
        if not self.template_library:
            st.error("❌ Template Library Manager nicht verfügbar")
            return
        
        # Template Library Overview
        templates = self.template_library.get_all_templates()
        
        if not templates:
            st.info("📭 Keine Templates in der Library verfügbar")
            st.info("💡 Verwende die separaten Analyse-Tools:")
            st.code("TXT: python3 src_orbis/mqtt/tools/txt_template_analyzer.py")
            st.code("CCU: python3 src_orbis/mqtt/tools/ccu_template_analyzer.py")
            return
        
        # Analysis History
        analysis_sessions = self.template_library.get_analysis_sessions()
        if analysis_sessions:
            st.markdown("**📈 Letzte Analysen:**")
            for session in analysis_sessions[:3]:  # Show last 3 sessions
                st.info(f"**{session['analysis_type'].upper()}:** {session['session_name']} "
                       f"({session['topics_count']} Topics, {session['messages_count']} Nachrichten) "
                       f"- {session['created_at']}")
        
        st.markdown("---")
        st.info("💡 Alle analysierten Templates werden in der Template Library gespeichert und angezeigt")
        
        # Display templates by category
        categories = {}
        for template in templates:
            category = template.get('category', 'Unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(template)
        
        for category, cat_templates in categories.items():
            st.subheader(f"📂 {category} Templates")
            
            for template in cat_templates:
                with st.expander(f"{template['topic']} ({template.get('message_count', 0)} Nachrichten)", expanded=False):
                    # Template information
                    st.markdown(f"**Beschreibung:** {template.get('description', 'Keine Beschreibung')}")
                    st.markdown(f"**Verwendung:** {template.get('usage', 'Keine Verwendungsangabe')}")
                    
                    # Template structure
                    if template.get('template'):
                        st.markdown("**📋 Template-Struktur:**")
                        st.json(template['template'])
                    
                    # Examples
                    if template.get('examples'):
                        st.markdown("**📄 Beispiel-Nachrichten:**")
                        for i, example in enumerate(template['examples'][:3]):  # Show first 3 examples
                            st.markdown(f"**Beispiel {i+1}:**")
                            
                            # Extract metadata
                            session = example.get('session', 'Unknown')
                            timestamp = example.get('timestamp', 'Unknown')
                            
                            # Display metadata in gray box
                            st.markdown(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>"
                                       f"<small>Session: {session} | Timestamp: {timestamp}</small></div>", 
                                       unsafe_allow_html=True)
                            
                            # Display payload as-is
                            if isinstance(example.get('payload'), dict):
                                st.json(example['payload'])
                            else:
                                st.text(example['payload'])
                    
                    # Variable fields
                    if template.get('variable_fields'):
                        st.markdown(f"**🔧 Variable Felder:** {', '.join(template['variable_fields'])}")
                    
                    # Interactive documentation editor
                    st.markdown("---")
                    st.markdown("**📝 Dokumentation bearbeiten:**")
                    
                    # Create session state keys for this template
                    template_key = template['topic'].replace('/', '_').replace(':', '_')
                    desc_key = f"desc_{template_key}"
                    usage_key = f"usage_{template_key}"
                    
                    # Initialize with existing values
                    if desc_key not in st.session_state:
                        st.session_state[desc_key] = template.get('description', '')
                    if usage_key not in st.session_state:
                        st.session_state[usage_key] = template.get('usage', '')
                    
                    # Input fields
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.session_state[desc_key] = st.text_area(
                            "💡 Beschreibung:",
                            value=st.session_state[desc_key],
                            key=f"textarea_{desc_key}",
                            height=80,
                            help="Wofür wird diese Nachricht verwendet?"
                        )
                    
                    with col2:
                        st.session_state[usage_key] = st.text_area(
                            "🎯 Verwendung:",
                            value=st.session_state[usage_key],
                            key=f"textarea_{usage_key}",
                            height=80,
                            help="Wie wird diese Nachricht im Workflow verwendet?"
                        )
                    
                    # Save button
                    if st.button("💾 Dokumentation speichern", key=f"save_{template_key}"):
                        # Update template in library
                        template['description'] = st.session_state[desc_key]
                        template['usage'] = st.session_state[usage_key]
                        self.template_library.update_template(template)
                        st.success(f"✅ Dokumentation für {template['topic']} gespeichert!")
    
    def clean_old_messages(self, days):
        """Clean old messages from database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                DELETE FROM messages 
                WHERE created_at < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            st.success(f"✅ Deleted {deleted_count} old messages")
            
        except Exception as e:
            st.error(f"❌ Error cleaning messages: {e}")

def main():
    """Main function"""
    dashboard = APSDashboard()
    
    try:
        dashboard.show_dashboard()
    finally:
        dashboard.disconnect_mqtt()

if __name__ == "__main__":
    main()
