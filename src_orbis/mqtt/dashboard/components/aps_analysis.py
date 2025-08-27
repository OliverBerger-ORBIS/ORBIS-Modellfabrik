import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime
import subprocess
import sys
from ...tools.topic_manager import get_topic_manager

class APSAnalysis:
    """Comprehensive APS Analysis Component for Multi-Protocol Analysis."""
    
    def __init__(self):
        self.sessions_dir = "mqtt-data/sessions"
        self.analysis_results = {}
    
    def show_aps_analysis_tab(self):
        """Main APS Analysis Tab with sub-sections."""
        st.header("🔍 APS Analyse")
        st.markdown("Umfassende Analyse aller APS-Protokolle und Kommunikationswege")
        
        # Session Management
        self._show_session_management()
        
        # Analysis Sub-Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📡 MQTT Analyse", 
            "🔧 Node-RED Analyse", 
            "🌐 Web-Server Analyse",
            "🔄 Multi-Protokoll Analyse"
        ])
        
        with tab1:
            self._show_mqtt_analysis()
        
        with tab2:
            self._show_nodered_analysis()
        
        with tab3:
            self._show_webserver_analysis()
        
        with tab4:
            self._show_multi_protocol_analysis()
    
    def _show_session_management(self):
        """Session Management Section."""
        st.subheader("📊 Session Management")
        
        st.info("""
        **💡 Session-Management über Kommandozeile:**
        
        **Session starten:**
        ```bash
        python src_orbis/mqtt/tools/start_aps_analysis_session.py --session SESSION_NAME
        ```
        
        **Session stoppen:**
        ```bash
        python src_orbis/mqtt/tools/stop_aps_analysis_session.py
        ```
        
        **Oder direkt mit APS Session Logger:**
        ```bash
        python src_orbis/mqtt/loggers/aps_session_logger.py --session-label SESSION_NAME --process-type custom --auto-start
        ```
        """)
        
        # Available Sessions
        st.subheader("📁 Verfügbare Sessions")
        sessions = self._get_available_sessions()
        
        if sessions:
            selected_session = st.selectbox(
                "Session auswählen:",
                sessions,
                format_func=lambda x: f"{x} ({self._get_session_info(x)})"
            )
            
            if selected_session:
                self._show_session_overview(selected_session)
        else:
            st.info("Keine Sessions verfügbar. Starte eine neue Session über die Kommandozeile.")
    
    def _show_mqtt_analysis(self):
        """MQTT Analysis Sub-Section."""
        st.subheader("📡 MQTT Analyse")
        
        if 'selected_session' in st.session_state:
            session_name = st.session_state.selected_session
            self._analyze_mqtt_session(session_name)
        else:
            st.info("Wähle eine Session aus, um MQTT-Analyse durchzuführen.")
    
    def _show_nodered_analysis(self):
        """Node-RED Analysis Sub-Section."""
        st.subheader("🔧 Node-RED Analyse")
        
        if 'selected_session' in st.session_state:
            session_name = st.session_state.selected_session
            self._analyze_nodered_session(session_name)
        else:
            st.info("Wähle eine Session aus, um Node-RED-Analyse durchzuführen.")
    
    def _show_webserver_analysis(self):
        """Web-Server Analysis Sub-Section."""
        st.subheader("🌐 Web-Server Analyse")
        
        if 'selected_session' in st.session_state:
            session_name = st.session_state.selected_session
            self._analyze_webserver_session(session_name)
        else:
            st.info("Wähle eine Session aus, um Web-Server-Analyse durchzuführen.")
    
    def _show_multi_protocol_analysis(self):
        """Multi-Protocol Analysis Sub-Section."""
        st.subheader("🔄 Multi-Protokoll Analyse")
        
        if 'selected_session' in st.session_state:
            session_name = st.session_state.selected_session
            self._analyze_multi_protocol_session(session_name)
        else:
            st.info("Wähle eine Session aus, um Multi-Protokoll-Analyse durchzuführen.")
    
    def _start_analysis_session(self, session_name):
        """Start comprehensive analysis session."""
        st.info("Session-Management erfolgt über die Kommandozeile. Siehe Anweisungen oben.")
    
    def _stop_analysis_session(self):
        """Stop analysis session."""
        st.info("Session-Management erfolgt über die Kommandozeile. Siehe Anweisungen oben.")
    
    def _get_available_sessions(self):
        """Get list of available sessions."""
        sessions = []
        if os.path.exists(self.sessions_dir):
            for file in os.listdir(self.sessions_dir):
                if file.endswith('.db') and 'aps_persistent_traffic_' in file:
                    session_name = file.replace('aps_persistent_traffic_', '').replace('.db', '')
                    sessions.append(session_name)
        return sorted(sessions, reverse=True)
    
    def _get_session_info(self, session_name):
        """Get basic session information."""
        db_path = os.path.join(self.sessions_dir, f"aps_persistent_traffic_{session_name}.db")
        try:
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query("SELECT COUNT(*) as count FROM mqtt_messages", conn)
            count = df.iloc[0]['count']
            conn.close()
            return f"{count} Nachrichten"
        except:
            return "Keine Daten"
    
    def _show_session_overview(self, session_name):
        """Show session overview."""
        st.session_state.selected_session = session_name
        
        db_path = os.path.join(self.sessions_dir, f"aps_persistent_traffic_{session_name}.db")
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
                conn.close()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Nachrichten", len(df))
                
                with col2:
                    if len(df) > 0:
                        start_time = pd.to_datetime(df['timestamp'].min())
                        st.metric("Start", start_time.strftime('%H:%M:%S'))
                
                with col3:
                    if len(df) > 0:
                        end_time = pd.to_datetime(df['timestamp'].max())
                        st.metric("Ende", end_time.strftime('%H:%M:%S'))
                
                with col4:
                    if len(df) > 0:
                        duration = end_time - start_time
                        st.metric("Dauer", str(duration).split('.')[0])
                
            except Exception as e:
                st.error(f"Fehler beim Laden der Session: {e}")
        else:
            st.warning("Session-Daten nicht gefunden.")
    
    def _analyze_mqtt_session(self, session_name):
        """Analyze MQTT session data."""
        st.write("### MQTT Protokoll Analyse")
        
        db_path = os.path.join(self.sessions_dir, f"aps_persistent_traffic_{session_name}.db")
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
                conn.close()
                
                # Add session_label column for compatibility
                df['session_label'] = session_name
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Add required columns for filters if they don't exist
                if 'module_type' not in df.columns:
                    df['module_type'] = 'unknown'
                if 'status' not in df.columns:
                    df['status'] = 'unknown'
                if 'process_label' not in df.columns:
                    df['process_label'] = 'unknown'
                if 'serial_number' not in df.columns:
                    df['serial_number'] = 'unknown'
                
                # Extract module information for proper filtering
                from ..utils.data_handling import extract_module_info
                df = extract_module_info(df)
                
                # Verbose mode toggle for camera filtering
                verbose_mode = st.checkbox("🔍 Verbose-Modus (Camera-Nachrichten anzeigen)", value=False)
                
                # Filter camera topics if not in verbose mode
                original_count = len(df)
                if not verbose_mode:
                    df = df[~df['topic'].str.contains('j1/txt/1/i/cam', na=False)]
                
                filtered_count = len(df)
                if original_count != filtered_count:
                    st.info(f"📷 {original_count - filtered_count} Camera-Nachrichten ausgeblendet (Verbose-Modus deaktiviert)")
                
                # Import and use the filter component
                from ..components.filters import create_filters
                
                # Create filters
                df_filtered = create_filters(df, single_session_mode=True)
                
                # Analysis sub-tabs
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "📊 Übersicht",
                    "⏰ Timeline", 
                    "📋 Nachrichten",
                    "📡 Topics",
                    "📦 Payload",
                    "🏷️ Sessions"
                ])
                
                with tab1:
                    self._show_mqtt_overview(df_filtered)
                
                with tab2:
                    self._show_mqtt_timeline(df_filtered)
                
                with tab3:
                    self._show_mqtt_message_table(df_filtered)
                
                with tab4:
                    self._show_mqtt_topic_analysis(df_filtered)
                
                with tab5:
                    self._show_mqtt_payload_analysis(df_filtered)
                
                with tab6:
                    self._show_mqtt_session_analysis(df_filtered)
                
            except Exception as e:
                st.error(f"Fehler bei MQTT-Analyse: {e}")
        else:
            st.error("Session-Daten nicht gefunden.")
    
    def _show_mqtt_overview(self, df):
        """Show MQTT overview analysis."""
        if df.empty:
            st.warning("Keine Daten für Übersicht verfügbar.")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Nachrichten", len(df))
        
        with col2:
            if len(df) > 0:
                start_time = df['timestamp'].min()
                st.metric("Start", start_time.strftime('%H:%M:%S'))
        
        with col3:
            if len(df) > 0:
                end_time = df['timestamp'].max()
                st.metric("Ende", end_time.strftime('%H:%M:%S'))
        
        with col4:
            if len(df) > 0:
                duration = end_time - start_time
                st.metric("Dauer", str(duration).split('.')[0])
        
        # Topic distribution with friendly names
        st.subheader("📡 Topic-Verteilung")
        topic_manager = get_topic_manager()
        df_topic = df.copy()
        df_topic.loc[:, 'friendly_topic'] = df_topic['topic'].apply(lambda x: topic_manager.get_friendly_name(x))
        topic_counts = df_topic['friendly_topic'].value_counts().head(10)
        st.bar_chart(topic_counts)
        
        # Module activity with module names
        st.subheader("🏭 Modul-Aktivität")
        module_messages = df[df['topic'].str.contains('module/v1/ff/', na=False)]
        if len(module_messages) > 0:
            # Extract module IDs and map to friendly names
            module_messages = module_messages.copy()
            module_messages['module_id'] = module_messages['topic'].str.extract(r'module/v1/ff/([^/]+)')
            
            # Map module IDs to friendly names
            module_name_mapping = {
                'SVR3QA2098': 'HBW (Hochregallager)',
                'SVR4H76449': 'MILL (Fräse)',
                'SVR4H76530': 'DRILL (Bohrer)',
                'SVR3QA0022': 'AIQS (Qualitätsprüfung)',
                'SVR4H73275': 'DPS (Warenein- und -ausgang)',
                '5iO4': 'FTS (Fahrerloses Transportsystem)',
                'CHRG0': 'CHARGING (Ladestation)'
            }
            
            module_messages['module_name'] = module_messages['module_id'].map(
                lambda x: module_name_mapping.get(x, x)
            )
            
            module_counts = module_messages['module_name'].value_counts()
            st.bar_chart(module_counts)
        else:
            st.info("Keine Modul-Nachrichten gefunden")
        
        # Protocol analysis
        self._analyze_mqtt_protocols(df)
    
    def _show_mqtt_timeline(self, df):
        """Show MQTT timeline analysis."""
        if df.empty:
            st.warning("Keine Daten für Timeline verfügbar.")
            return
        
        st.subheader("⏰ Nachrichten Timeline")
        
        # Timeline chart
        timeline_data = df.set_index('timestamp').resample('1s').size()
        st.line_chart(timeline_data)
        
        # Activity heatmap
        st.subheader("🔥 Aktivitäts-Heatmap")
        df = df.copy()
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        
        # Create heatmap data
        heatmap_data = df.groupby(['hour', 'minute']).size().unstack(fill_value=0)
        st.dataframe(heatmap_data, use_container_width=True)
    
    def _show_mqtt_message_table(self, df):
        """Show MQTT message table."""
        if df.empty:
            st.warning("Keine Nachrichten verfügbar.")
            return
        
        st.subheader("📋 Nachrichten-Tabelle")
        
        # Add friendly topic names
        topic_manager = get_topic_manager()
        df_display = df.copy()
        df_display['friendly_topic'] = df_display['topic'].apply(lambda x: topic_manager.get_friendly_name(x))
        
        # Show recent messages
        recent_messages = df_display[['timestamp', 'friendly_topic', 'payload']].tail(50)
        st.dataframe(recent_messages, use_container_width=True)
    
    def _show_mqtt_topic_analysis(self, df):
        """Show MQTT topic analysis."""
        if df.empty:
            st.warning("Keine Daten für Topic-Analyse verfügbar.")
            return
        
        st.subheader("📡 Topic-Analyse")
        
        # Import friendly topic mapping
        topic_manager = get_topic_manager()
        
        # Create analysis DataFrame with friendly topic names
        df_analysis = df[["topic"]].copy()
        df_analysis["friendly_topic"] = df_analysis["topic"].apply(lambda x: topic_manager.get_friendly_name(x))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top topics with friendly names
            topic_counts = df_analysis["friendly_topic"].value_counts().head(10)
            st.bar_chart(topic_counts)
        
        with col2:
            # Topic comparison
            st.subheader("Topic-Vergleich")
            
            # Show both original and friendly names
            topic_comparison = df_analysis[["topic", "friendly_topic"]].drop_duplicates().head(10)
            st.dataframe(topic_comparison, use_container_width=True)
            
            # Topic statistics
            total_topics = df["topic"].nunique()
            mapped_topics = df_analysis["friendly_topic"].nunique()
            unmapped_count = len([t for t in df["topic"].unique() if topic_manager.get_friendly_name(t) == t])
            
            st.metric("Gesamt Topics", total_topics)
            st.metric("Mapped Topics", total_topics - unmapped_count)
            st.metric("Unmapped Topics", unmapped_count)
    
    def _show_mqtt_payload_analysis(self, df):
        """Show MQTT payload analysis."""
        if df.empty:
            st.warning("Keine Daten für Payload-Analyse verfügbar.")
            return
        
        st.subheader("📦 Payload-Analyse")
        
        # Payload size analysis
        df = df.copy()
        df['payload_size'] = df['payload'].str.len()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Payload-Größe")
            payload_sizes = df['payload_size'].value_counts().head(10)
            st.bar_chart(payload_sizes)
        
        with col2:
            st.subheader("Payload-Statistiken")
            st.metric("Durchschnittliche Größe", f"{df['payload_size'].mean():.0f} Zeichen")
            st.metric("Maximale Größe", f"{df['payload_size'].max()} Zeichen")
            st.metric("Minimale Größe", f"{df['payload_size'].min()} Zeichen")
        
        # JSON payload analysis
        st.subheader("JSON Payload-Analyse")
        json_payloads = []
        for idx, row in df.iterrows():
            try:
                json_data = json.loads(row['payload'])
                if isinstance(json_data, dict):
                    json_payloads.append(json_data)
            except:
                continue
        
        if json_payloads:
            st.success(f"✅ {len(json_payloads)} JSON Payloads gefunden")
            
            # Show sample JSON payloads
            st.subheader("Beispiel JSON Payloads")
            for i, payload in enumerate(json_payloads[:3]):
                with st.expander(f"JSON Payload {i+1}"):
                    st.json(payload)
        else:
            st.info("Keine JSON Payloads gefunden")
    
    def _show_mqtt_session_analysis(self, df):
        """Show MQTT session analysis."""
        if df.empty:
            st.warning("Keine Daten für Session-Analyse verfügbar.")
            return
        
        st.subheader("🏷️ Session-Analyse")
        
        # Session overview
        if 'session_label' in df.columns:
            session_counts = df['session_label'].value_counts()
            st.bar_chart(session_counts)
        
        # Message flow analysis
        st.subheader("📊 Nachrichten-Fluss")
        
        # Group by time intervals
        df = df.copy()
        df['time_interval'] = df['timestamp'].dt.floor('1min')
        message_flow = df.groupby('time_interval').size()
        
        st.line_chart(message_flow)
    
    def _analyze_mqtt_protocols(self, df):
        """Analyze MQTT protocols and message types."""
        if df.empty:
            return
        
        st.subheader("🔧 Protokoll-Analyse")
        
        # Protocol categorization
        protocols = {
            'Module': df[df['topic'].str.contains('module/v1/ff/', na=False)],
            'CCU': df[df['topic'].str.contains('ccu/', na=False)],
            'TXT': df[df['topic'].str.contains('j1/txt/', na=False)],
            'FTS': df[df['topic'].str.contains('fts/', na=False)],
            'Other': df[~df['topic'].str.contains('module/v1/ff/|ccu/|j1/txt/|fts/', na=False)]
        }
        
        # Protocol overview
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Protokoll-Verteilung:**")
            protocol_counts = {name: len(data) for name, data in protocols.items()}
            st.bar_chart(protocol_counts)
        
        with col2:
            st.write("**📈 Protokoll-Statistiken:**")
            for name, data in protocols.items():
                if len(data) > 0:
                    st.metric(f"{name} Nachrichten", len(data))
    
    def _analyze_nodered_session(self, session_name):
        """Analyze Node-RED session data."""
        st.write("### Node-RED Protokoll Analyse")
        
        db_path = os.path.join(self.sessions_dir, f"aps_persistent_traffic_{session_name}.db")
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
                conn.close()
                
                # Add required columns for filters if they don't exist
                if 'module_type' not in df.columns:
                    df['module_type'] = 'unknown'
                if 'status' not in df.columns:
                    df['status'] = 'unknown'
                if 'process_label' not in df.columns:
                    df['process_label'] = 'unknown'
                if 'serial_number' not in df.columns:
                    df['serial_number'] = 'unknown'
                
                # Extract module information for proper filtering
                from ..utils.data_handling import extract_module_info
                df = extract_module_info(df)
                
                # Filter Node-RED specific messages
                nodered_messages = df[df['topic'].str.contains('NodeRed|nodered|workflow', na=False)]
                
                if len(nodered_messages) > 0:
                    st.success(f"✅ {len(nodered_messages)} Node-RED Nachrichten gefunden")
                    
                    # Node-RED Topic Analysis
                    nodered_topics = nodered_messages['topic'].value_counts()
                    st.write("**Node-RED Topics:**")
                    st.bar_chart(nodered_topics.head(10))
                    
                    # Node-RED Message Types
                    st.write("**Node-RED Nachrichten-Typen:**")
                    
                    # Status messages
                    status_messages = nodered_messages[nodered_messages['topic'].str.contains('/status', na=False)]
                    if len(status_messages) > 0:
                        st.write(f"📊 Status: {len(status_messages)} Nachrichten")
                    
                    # Connection messages
                    connection_messages = nodered_messages[nodered_messages['topic'].str.contains('/connection', na=False)]
                    if len(connection_messages) > 0:
                        st.write(f"🔗 Connection: {len(connection_messages)} Nachrichten")
                    
                    # Order messages
                    order_messages = nodered_messages[nodered_messages['topic'].str.contains('order', na=False)]
                    if len(order_messages) > 0:
                        st.write(f"📋 Orders: {len(order_messages)} Nachrichten")
                        
                        # Show recent order messages
                        st.write("**Letzte Order-Nachrichten:**")
                        recent_orders = order_messages.tail(5)
                        for idx, row in recent_orders.iterrows():
                            st.write(f"**{row['topic']}** - {row['timestamp']}")
                            try:
                                payload = json.loads(row['payload'])
                                st.json(payload)
                            except:
                                st.code(row['payload'])
                    
                    # Workflow messages
                    workflow_messages = nodered_messages[nodered_messages['topic'].str.contains('workflow', na=False)]
                    if len(workflow_messages) > 0:
                        st.write(f"🔄 Workflow: {len(workflow_messages)} Nachrichten")
                        
                        # Show recent workflow messages
                        st.write("**Letzte Workflow-Nachrichten:**")
                        recent_workflows = workflow_messages.tail(3)
                        for idx, row in recent_workflows.iterrows():
                            st.write(f"**{row['topic']}** - {row['timestamp']}")
                            try:
                                payload = json.loads(row['payload'])
                                st.json(payload)
                            except:
                                st.code(row['payload'])
                
                else:
                    st.warning("⚠️ Keine Node-RED Nachrichten in dieser Session gefunden")
                    
            except Exception as e:
                st.error(f"Fehler bei Node-RED-Analyse: {e}")
        else:
            st.error("Session-Daten nicht gefunden.")
    
    def _analyze_webserver_session(self, session_name):
        """Analyze Web-Server session data."""
        st.write("### Web-Server Protokoll Analyse")
        
        db_path = os.path.join(self.sessions_dir, f"aps_persistent_traffic_{session_name}.db")
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
                conn.close()
                
                # Add required columns for filters if they don't exist
                if 'module_type' not in df.columns:
                    df['module_type'] = 'unknown'
                if 'status' not in df.columns:
                    df['status'] = 'unknown'
                if 'process_label' not in df.columns:
                    df['process_label'] = 'unknown'
                if 'serial_number' not in df.columns:
                    df['serial_number'] = 'unknown'
                
                # Extract module information for proper filtering
                from ..utils.data_handling import extract_module_info
                df = extract_module_info(df)
                
                # Filter Web-Server specific messages (MQTT)
                webserver_messages = df[df['topic'].str.contains('fischertechnik|web|http|api|rest', na=False)]
                
                # Also check for HTTP traffic database
                http_db_path = os.path.join(self.sessions_dir, f"http_traffic_{session_name}.db")
                if os.path.exists(http_db_path):
                    try:
                        conn = sqlite3.connect(http_db_path)
                        http_df = pd.read_sql_query("SELECT * FROM http_requests ORDER BY timestamp", conn)
                        conn.close()
                        
                        st.success(f"✅ HTTP Traffic Database gefunden: {len(http_df)} Requests")
                        
                        # HTTP Traffic Analysis
                        st.write("**🌐 HTTP Traffic Analyse:**")
                        
                        # Request methods
                        method_counts = http_df['method'].value_counts()
                        st.write("**HTTP Methods:**")
                        st.bar_chart(method_counts)
                        
                        # Status codes
                        status_counts = http_df['response_status'].value_counts()
                        st.write("**HTTP Status Codes:**")
                        st.bar_chart(status_counts)
                        
                        # Order-related requests
                        order_requests = http_df[http_df['url'].str.contains('order', na=False)]
                        if len(order_requests) > 0:
                            st.write(f"📋 Order HTTP Requests: {len(order_requests)}")
                            
                            # Show order requests
                            st.write("**Order HTTP Requests:**")
                            for idx, row in order_requests.iterrows():
                                st.write(f"**{row['timestamp']}** - {row['method']} {row['url']}")
                                if row['body']:
                                    try:
                                        body_data = json.loads(row['body'])
                                        st.json(body_data)
                                    except:
                                        st.code(row['body'][:200] + "..." if len(row['body']) > 200 else row['body'])
                                st.write("---")
                        
                        # API endpoints
                        endpoint_counts = http_df['url'].value_counts().head(10)
                        st.write("**Top API Endpoints:**")
                        st.bar_chart(endpoint_counts)
                        
                    except Exception as e:
                        st.error(f"Fehler beim Laden der HTTP Traffic Daten: {e}")
                else:
                    st.info("💡 HTTP Traffic Database nicht gefunden. Starte Session mit HTTP Logger.")
                
                if len(webserver_messages) > 0:
                    st.success(f"✅ {len(webserver_messages)} Web-Server Nachrichten gefunden")
                    
                    # Web-Server Topic Analysis
                    webserver_topics = webserver_messages['topic'].value_counts()
                    st.write("**Web-Server Topics:**")
                    st.bar_chart(webserver_topics.head(10))
                    
                    # Web-Server Message Types
                    st.write("**Web-Server Nachrichten-Typen:**")
                    
                    # Fischertechnik messages
                    fischertech_messages = webserver_messages[webserver_messages['topic'].str.contains('fischertechnik', na=False)]
                    if len(fischertech_messages) > 0:
                        st.write(f"🏭 Fischertechnik: {len(fischertech_messages)} Nachrichten")
                        
                        # Show recent fischertechnik messages
                        st.write("**Letzte Fischertechnik-Nachrichten:**")
                        recent_fischertech = fischertech_messages.tail(5)
                        for idx, row in recent_fischertech.iterrows():
                            st.write(f"**{row['topic']}** - {row['timestamp']}")
                            try:
                                payload = json.loads(row['payload'])
                                st.json(payload)
                            except:
                                st.code(row['payload'])
                    
                    # HTTP/API messages
                    http_messages = webserver_messages[webserver_messages['topic'].str.contains('http|api|rest', na=False)]
                    if len(http_messages) > 0:
                        st.write(f"🌐 HTTP/API: {len(http_messages)} Nachrichten")
                        
                        # Show recent HTTP messages
                        st.write("**Letzte HTTP/API-Nachrichten:**")
                        recent_http = http_messages.tail(3)
                        for idx, row in recent_http.iterrows():
                            st.write(f"**{row['topic']}** - {row['timestamp']}")
                            try:
                                payload = json.loads(row['payload'])
                                st.json(payload)
                            except:
                                st.code(row['payload'])
                    
                    # Web interface messages
                    web_messages = webserver_messages[webserver_messages['topic'].str.contains('web|dashboard', na=False)]
                    if len(web_messages) > 0:
                        st.write(f"🖥️ Web Interface: {len(web_messages)} Nachrichten")
                        
                        # Show recent web messages
                        st.write("**Letzte Web-Interface-Nachrichten:**")
                        recent_web = web_messages.tail(3)
                        for idx, row in recent_web.iterrows():
                            st.write(f"**{row['topic']}** - {row['timestamp']}")
                            try:
                                payload = json.loads(row['payload'])
                                st.json(payload)
                            except:
                                st.code(row['payload'])
                
                else:
                    st.warning("⚠️ Keine Web-Server Nachrichten in dieser Session gefunden")
                    st.info("""
                    **💡 Tipp:** Web-Server Nachrichten können auch über HTTP-Logs oder Browser Developer Tools erfasst werden.
                    
                    **Mögliche Topics:**
                    - `fischertechnik/order/start`
                    - `web/interface/order`
                    - `api/rest/orders`
                    """)
                    
            except Exception as e:
                st.error(f"Fehler bei Web-Server-Analyse: {e}")
        else:
            st.error("Session-Daten nicht gefunden.")
    
    def _analyze_multi_protocol_session(self, session_name):
        """Analyze multi-protocol session data."""
        st.write("### Multi-Protokoll Korrelations-Analyse")
        
        db_path = os.path.join(self.sessions_dir, f"aps_persistent_traffic_{session_name}.db")
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
                conn.close()
                
                # Add required columns for filters if they don't exist
                if 'module_type' not in df.columns:
                    df['module_type'] = 'unknown'
                if 'status' not in df.columns:
                    df['status'] = 'unknown'
                if 'process_label' not in df.columns:
                    df['process_label'] = 'unknown'
                if 'serial_number' not in df.columns:
                    df['serial_number'] = 'unknown'
                
                # Extract module information for proper filtering
                from ..utils.data_handling import extract_module_info
                df = extract_module_info(df)
                
                # Protocol categorization
                protocols = {
                    'MQTT': df[df['topic'].str.contains('module/v1/ff/|ccu/|txt/', na=False)],
                    'Node-RED': df[df['topic'].str.contains('NodeRed|nodered|workflow', na=False)],
                    'Web-Server': df[df['topic'].str.contains('fischertechnik|web|http|api|rest', na=False)],
                    'Other': df[~df['topic'].str.contains('module/v1/ff/|ccu/|txt/|NodeRed|nodered|workflow|fischertechnik|web|http|api|rest', na=False)]
                }
                
                # Protocol overview
                st.write("**📊 Protokoll-Verteilung:**")
                protocol_counts = {name: len(data) for name, data in protocols.items()}
                st.bar_chart(protocol_counts)
                
                # Timeline correlation
                st.write("**⏰ Multi-Protokoll Timeline:**")
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Create protocol column
                df['protocol'] = 'Other'
                df.loc[df['topic'].str.contains('module/v1/ff/|ccu/|txt/', na=False), 'protocol'] = 'MQTT'
                df.loc[df['topic'].str.contains('NodeRed|nodered|workflow', na=False), 'protocol'] = 'Node-RED'
                df.loc[df['topic'].str.contains('fischertechnik|web|http|api|rest', na=False), 'protocol'] = 'Web-Server'
                
                # Timeline by protocol
                timeline_data = df.groupby([df['timestamp'].dt.floor('1s'), 'protocol']).size().unstack(fill_value=0)
                st.line_chart(timeline_data)
                
                # Order correlation analysis
                st.write("**📋 Order-Korrelation zwischen Protokollen:**")
                
                # Find order-related messages across protocols
                order_messages = df[df['topic'].str.contains('order', na=False)]
                
                if len(order_messages) > 0:
                    st.success(f"✅ {len(order_messages)} Order-Nachrichten gefunden")
                    
                    # Group by protocol
                    order_by_protocol = order_messages.groupby('protocol').size()
                    st.write("**Order-Nachrichten pro Protokoll:**")
                    st.bar_chart(order_by_protocol)
                    
                    # Show order sequence
                    st.write("**📋 Order-Sequenz über Protokolle:**")
                    order_sequence = order_messages[['timestamp', 'topic', 'protocol', 'payload']].sort_values('timestamp')
                    
                    for idx, row in order_sequence.iterrows():
                        st.write(f"**{row['timestamp']}** - {row['protocol']} - {row['topic']}")
                        try:
                            payload = json.loads(row['payload'])
                            if isinstance(payload, dict) and 'orderId' in payload:
                                st.write(f"   Order-ID: {payload['orderId'][:8]}...")
                            if isinstance(payload, dict) and 'orderType' in payload:
                                st.write(f"   Order-Type: {payload['orderType']}")
                        except:
                            pass
                        st.write("---")
                
                else:
                    st.warning("⚠️ Keine Order-Nachrichten gefunden")
                
                # Module interaction analysis
                st.write("**🏭 Module-Interaktion über Protokolle:**")
                
                # Find module-related messages
                module_messages = df[df['topic'].str.contains('module/v1/ff/', na=False)]
                
                if len(module_messages) > 0:
                    # Extract module IDs
                    module_messages['module_id'] = module_messages['topic'].str.extract(r'module/v1/ff/([^/]+)')
                    
                    # Module activity by protocol
                    module_activity = module_messages.groupby('module_id').size().sort_values(ascending=False)
                    st.write("**Module-Aktivität:**")
                    st.bar_chart(module_activity.head(10))
                    
                    # Module state changes
                    state_messages = module_messages[module_messages['topic'].str.contains('/state', na=False)]
                    if len(state_messages) > 0:
                        st.write(f"📊 {len(state_messages)} Module State-Änderungen")
                        
                        # Show recent state changes
                        recent_states = state_messages.tail(5)
                        for idx, row in recent_states.iterrows():
                            st.write(f"**{row['module_id']}** - {row['timestamp']}")
                            try:
                                payload = json.loads(row['payload'])
                                if isinstance(payload, dict) and 'state' in payload:
                                    st.write(f"   State: {payload['state']}")
                            except:
                                pass
                
                # Cross-protocol message flow
                st.write("**🔄 Protokoll-übergreifende Nachrichtenflüsse:**")
                
                # Find messages with common patterns (orderId, actionId, etc.)
                common_patterns = ['orderId', 'actionId', 'workpieceId', 'serialNumber']
                
                for pattern in common_patterns:
                    pattern_messages = df[df['payload'].str.contains(pattern, na=False)]
                    if len(pattern_messages) > 0:
                        st.write(f"**{pattern}** - {len(pattern_messages)} Nachrichten über Protokolle")
                        
                        # Show distribution
                        pattern_by_protocol = pattern_messages.groupby('protocol').size()
                        st.bar_chart(pattern_by_protocol)
                
            except Exception as e:
                st.error(f"Fehler bei Multi-Protokoll-Analyse: {e}")
        else:
            st.error("Session-Daten nicht gefunden.")
    
    def _analyze_mqtt_protocols(self, df):
        """Analyze MQTT protocols and patterns."""
        st.write("**Protokoll-Analyse:**")
        
        # Order Analysis
        order_messages = df[df['topic'].str.contains('order', na=False)]
        if len(order_messages) > 0:
            st.write(f"📋 Orders: {len(order_messages)} Nachrichten")
        
        # Module Analysis
        module_messages = df[df['topic'].str.contains('module/v1/ff/', na=False)]
        if len(module_messages) > 0:
            st.write(f"🏭 Module: {len(module_messages)} Nachrichten")
        
        # CCU Analysis
        ccu_messages = df[df['topic'].str.contains('ccu/', na=False)]
        if len(ccu_messages) > 0:
            st.write(f"🎛️ CCU: {len(ccu_messages)} Nachrichten")
