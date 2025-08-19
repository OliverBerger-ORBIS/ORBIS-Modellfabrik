#!/usr/bin/env python3
"""
Node-RED Dashboard Integration
Integration für Node-RED Nachrichten-Analyse im Dashboard
"""

import streamlit as st
import pandas as pd
import sqlite3
import json
from typing import Dict, List, Optional
from node_red_message_analyzer import NodeRedMessageAnalyzer

def show_node_red_analysis_tab():
    """Node-RED Analyse Tab im Dashboard anzeigen"""
    
    st.subheader("🔍 Node-RED Nachrichten Analyse")
    st.markdown("Analysiert Node-RED Nachrichten aus Session-Daten")
    
    # Session-Auswahl
    session_files = get_available_sessions()
    
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
            analyze_node_red_session(selected_session)

def get_available_sessions() -> List[str]:
    """Verfügbare Session-Dateien finden"""
    import glob
    import os
    
    session_pattern = "mqtt-data/sessions/aps_persistent_traffic_*.db"
    session_files = glob.glob(session_pattern)
    
    # Sortiere nach Dateiname
    session_files.sort()
    
    return session_files

def analyze_node_red_session(session_file: str):
    """Node-RED Nachrichten einer Session analysieren"""
    
    try:
        analyzer = NodeRedMessageAnalyzer(session_file)
        
        # Verbindung herstellen
        if not analyzer.connect():
            st.error("❌ Verbindung zur Session-Datenbank fehlgeschlagen")
            return
        
        # Node-RED Nachrichten laden
        df = analyzer.get_node_red_messages()
        
        if df.empty:
            st.warning("⚠️ Keine Node-RED Nachrichten in dieser Session gefunden")
            analyzer.disconnect()
            return
        
        # Analysen durchführen
        topic_analysis = analyzer.analyze_node_red_topics(df)
        state_messages = analyzer.extract_node_red_state_messages(df)
        factsheet_messages = analyzer.extract_factsheet_messages(df)
        connection_messages = analyzer.extract_connection_messages(df)
        
        # Ergebnisse anzeigen
        display_node_red_analysis_results(
            session_file, topic_analysis, state_messages, 
            factsheet_messages, connection_messages, df
        )
        
        analyzer.disconnect()
        
    except Exception as e:
        st.error(f"❌ Fehler bei der Node-RED Analyse: {e}")

def display_node_red_analysis_results(
    session_file: str, 
    topic_analysis: Dict, 
    state_messages: pd.DataFrame,
    factsheet_messages: pd.DataFrame, 
    connection_messages: pd.DataFrame,
    all_messages: pd.DataFrame
):
    """Node-RED Analyse-Ergebnisse im Dashboard anzeigen"""
    
    # Session-Info
    st.success(f"✅ Node-RED Analyse abgeschlossen: {session_file.split('/')[-1]}")
    
    # Overview Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Gesamt-Nachrichten", topic_analysis.get('total_messages', 0))
    
    with col2:
        st.metric("Node-RED State", len(state_messages))
    
    with col3:
        st.metric("Factsheet", len(factsheet_messages))
    
    with col4:
        st.metric("Connection", len(connection_messages))
    
    # Topic Distribution
    st.subheader("📋 Topic Distribution")
    
    if 'topic_distribution' in topic_analysis:
        topic_df = pd.DataFrame(
            list(topic_analysis['topic_distribution'].items()),
            columns=['Topic', 'Count']
        ).sort_values('Count', ascending=False)
        
        st.dataframe(topic_df, use_container_width=True)
        
        # Bar Chart
        st.bar_chart(topic_df.set_index('Topic')['Count'])
    
    # Node-RED State Messages
    if not state_messages.empty:
        st.subheader("🔍 Node-RED State Messages")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Topics:**")
            for topic in state_messages['topic'].unique():
                st.markdown(f"• {topic}")
        
        with col2:
            st.markdown("**Sample Messages:**")
            for _, row in state_messages.head(3).iterrows():
                with st.expander(f"{row['timestamp']} - {row['topic']}"):
                    st.json(json.loads(row['payload']) if isinstance(row['payload'], str) else row['payload'])
    
    # Factsheet Messages
    if not factsheet_messages.empty:
        st.subheader("📋 Factsheet Messages")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Topics:**")
            for topic in factsheet_messages['topic'].unique():
                st.markdown(f"• {topic}")
        
        with col2:
            st.markdown("**Sample Messages:**")
            for _, row in factsheet_messages.head(3).iterrows():
                with st.expander(f"{row['timestamp']} - {row['topic']}"):
                    st.json(json.loads(row['payload']) if isinstance(row['payload'], str) else row['payload'])
    
    # Connection Messages
    if not connection_messages.empty:
        st.subheader("🔗 Connection Messages")
        
        # Connection Status Timeline
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
        
        # Timeline Chart
        st.markdown("**Connection Status Timeline:**")
        
        # Group by module and show connection states
        module_connections = connection_timeline.groupby(['module_type', 'connection_state']).size().unstack(fill_value=0)
        st.dataframe(module_connections, use_container_width=True)
        
        # Sample connection messages
        st.markdown("**Sample Connection Messages:**")
        for _, row in connection_messages.head(3).iterrows():
            with st.expander(f"{row['timestamp']} - {row['topic']}"):
                st.json(json.loads(row['payload']) if isinstance(row['payload'], str) else row['payload'])
    
    # Payload Analysis
    st.subheader("📦 Payload Structure Analysis")
    
    payload_analysis = analyze_payload_structures(all_messages)
    
    if payload_analysis:
        for structure, info in list(payload_analysis.items())[:5]:
            with st.expander(f"{structure} ({info['count']} Nachrichten)"):
                st.markdown(f"**Topics:** {', '.join(info['topics'][:5])}")
                if info['examples']:
                    st.markdown("**Example:**")
                    st.json(info['examples'][0])

def analyze_payload_structures(df: pd.DataFrame) -> Dict:
    """Payload-Strukturen analysieren"""
    payload_analysis = {}
    
    for _, row in df.iterrows():
        try:
            if isinstance(row['payload'], str):
                payload = json.loads(row['payload'])
            else:
                payload = row['payload']
            
            if payload:
                payload_keys = list(payload.keys())
                key_str = ', '.join(sorted(payload_keys))
                
                if key_str not in payload_analysis:
                    payload_analysis[key_str] = {
                        'count': 0,
                        'examples': [],
                        'topics': set()
                    }
                
                payload_analysis[key_str]['count'] += 1
                payload_analysis[key_str]['topics'].add(row['topic'])
                
                if len(payload_analysis[key_str]['examples']) < 2:
                    payload_analysis[key_str]['examples'].append(payload)
        
        except:
            continue
    
    # Sets zu Listen konvertieren
    for key in payload_analysis:
        payload_analysis[key]['topics'] = list(payload_analysis[key]['topics'])
    
    return payload_analysis

def show_node_red_insights():
    """Node-RED Insights anzeigen"""
    
    st.subheader("💡 Node-RED Insights")
    
    insights = [
        {
            "title": "🔍 Node-RED State Messages",
            "description": "Zeigen den aktuellen Status der Module über Node-RED Gateway",
            "topics": [
                "module/v1/ff/NodeRed/{Module-ID}/state",
                "Enthält actionState, batteryState, errors, etc."
            ]
        },
        {
            "title": "📋 Factsheet Messages", 
            "description": "Enthalten detaillierte Modul-Informationen",
            "topics": [
                "module/v1/ff/{Module-ID}/factsheet",
                "module/v1/ff/NodeRed/{Module-ID}/factsheet",
                "Enthält loadSpecification, physicalParameters, etc."
            ]
        },
        {
            "title": "🔗 Connection Messages",
            "description": "Zeigen Verbindungsstatus der Module",
            "topics": [
                "module/v1/ff/{Module-ID}/connection",
                "module/v1/ff/NodeRed/{Module-ID}/connection",
                "Enthält connectionState, ip, manufacturer, etc."
            ]
        }
    ]
    
    for insight in insights:
        with st.expander(insight["title"]):
            st.markdown(insight["description"])
            st.markdown("**Topics:**")
            for topic in insight["topics"]:
                st.code(topic)

# Integration in das Dashboard
if __name__ == "__main__":
    st.set_page_config(page_title="Node-RED Analysis", layout="wide")
    
    st.title("🔍 Node-RED Message Analysis")
    
    tab1, tab2 = st.tabs(["📊 Session Analysis", "💡 Insights"])
    
    with tab1:
        show_node_red_analysis_tab()
    
    with tab2:
        show_node_red_insights()
