"""
Order Analyzer - Session Manager Komponente für Order-basierte Message-Analyse

Analysiert Message-Ketten basierend auf Order-IDs mit interaktiver Visualisierung.
Verwendet OMF-Logging-Konzept (ohne MessageTemplateManager).
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import plotly.graph_objects as go
import streamlit as st

from ..utils.logging_config import get_logger
from ..utils.ui_refresh import request_refresh

# OMF Logging-System verwenden
logger = get_logger("session_manager.order_analyzer")


def show_order_analyzer():
    """Hauptfunktion für den Order Analyzer Session Manager Tab"""
    logger.info("🔍 Order Analyzer geladen")

    st.header("🔍 Order Analyzer")
    st.markdown("**Order-basierte Message-Analyse mit OMF-Logging-System**")

    # OMF-Logging-System initialisiert (ohne MessageTemplateManager)
    logger.info("✅ OMF-Logging-System initialisiert")

    # Tabs für verschiedene Funktionen
    tab1, tab2, tab3 = st.tabs(["📊 Message Analysis", "🔍 Order Analysis", "🔗 Message Chains"])

    with tab1:
        _show_message_analysis_section()

    with tab2:
        _show_order_analysis_section()

    with tab3:
        _show_message_chains_section()


def _show_message_analysis_section():
    """Zeigt die Message-Analyse-Sektion (ohne Template-Validierung)"""
    st.markdown("### 📊 Message Analysis")
    st.markdown("**Message-Analyse (Template-Validierung temporär deaktiviert)**")
    st.info("ℹ️ Template-Validierung temporär deaktiviert - nur Message-Analyse verfügbar")

    # Session-Auswahl
    st.markdown("#### 1️⃣ Session auswählen")
    sessions_dir = "data/omf-data/sessions"

    if not os.path.exists(sessions_dir):
        st.error("❌ Sessions-Verzeichnis nicht gefunden")
        return

    log_files = [f for f in os.listdir(sessions_dir) if f.endswith('.log')]

    if not log_files:
        st.warning("❌ Keine Session-Dateien gefunden")
        return

    selected_session = st.selectbox("📁 Session auswählen", options=log_files, key="message_analysis_session")

    if not selected_session:
        return

    # Topic-Auswahl
    st.markdown("#### 2️⃣ Topic auswählen")
    available_topics = [
        "ccu/order/request",
        "ccu/order/response",
        "module/v1/*/status",
        "module/v1/*/state",
        "module/v1/*/connection",
        "module/v1/*/order",
        "module/v1/*/factsheet",
    ]

    selected_topic = st.selectbox("Topic auswählen", options=available_topics, key="message_analysis_topic")

    # Zeitbereich-Auswahl
    st.markdown("#### 3️⃣ Zeitbereich auswählen")

    # Schnellauswahl-Buttons
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("5s", key="order_analyzer_5s"):
            st.session_state.order_analyzer_time_range = (0.0, 5.0)
            request_refresh()

    with col2:
        if st.button("15s", key="order_analyzer_15s"):
            st.session_state.order_analyzer_time_range = (0.0, 15.0)
            request_refresh()

    with col3:
        if st.button("30s", key="order_analyzer_30s"):
            st.session_state.order_analyzer_time_range = (0.0, 30.0)
            request_refresh()

    with col4:
        if st.button("60s", key="order_analyzer_60s"):
            st.session_state.order_analyzer_time_range = (0.0, 60.0)
            request_refresh()

    with col5:
        if st.button("120s", key="order_analyzer_120s"):
            st.session_state.order_analyzer_time_range = (0.0, 120.0)
            request_refresh()

    # Zeitbereich-Schieberegler
    time_range = st.slider(
        "⏱️ Zeitbereich (Sekunden)",
        min_value=0.0,
        max_value=600.0,  # 10 Minuten
        value=st.session_state.get("order_analyzer_time_range", (0.0, 30.0)),
        step=1.0,
        format="%.1f s",
        key="order_analyzer_time_slider",
    )

    # Session State aktualisieren
    st.session_state.order_analyzer_time_range = time_range

    # Aktueller Zeitbereich anzeigen
    st.info(f"📊 Zeitbereich: {time_range[0]:.1f}s - {time_range[1]:.1f}s")

    # Analyse starten
    if st.button("🔍 Messages analysieren", type="primary"):
        with st.spinner("Analysiere Messages..."):
            try:
                # Session-Daten laden
                session_data = _load_session_data(os.path.join(sessions_dir, selected_session))
                if not session_data:
                    st.error("❌ Keine Session-Daten geladen")
                    return

                # Messages filtern
                filtered_messages = []
                for msg in session_data:
                    if _topic_matches(msg.get('topic', ''), selected_topic):
                        filtered_messages.append(msg)

                if not filtered_messages:
                    st.warning("⚠️ Keine Messages für das ausgewählte Topic gefunden")
                    return

                # Zeitbereich anwenden (wie im Auftrag-Rot Analyzer)
                if time_range[1] > 0:
                    # Erste Message als Referenzpunkt
                    if filtered_messages:
                        # Timestamps zu datetime konvertieren
                        timestamps = []
                        for msg in filtered_messages:
                            try:
                                timestamp_str = msg.get('timestamp', '')
                                if timestamp_str:
                                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                    timestamps.append(timestamp)
                            except (ValueError, TypeError):
                                continue

                        if timestamps:
                            # Start-Zeit = erste Message
                            start_time = min(timestamps)
                            # End-Zeit = Start-Zeit + gewählte Sekunden
                            end_time = start_time + timedelta(seconds=time_range[1])

                            logger.info(f"⏱️ Zeitbereich: {start_time} bis {end_time} ({time_range[1]}s)")

                            # Messages im Zeitbereich filtern
                            filtered_messages = [
                                msg
                                for msg in filtered_messages
                                if start_time
                                <= datetime.fromisoformat(msg.get('timestamp', '').replace('Z', '+00:00'))
                                <= end_time
                            ]

                            logger.info(f"📊 {len(filtered_messages)} Messages im Zeitbereich gefunden")

                # Einfache Message-Analyse anzeigen
                _render_simple_message_analysis(filtered_messages, selected_topic)

            except Exception as e:
                logger.error(f"❌ Fehler bei der Message-Analyse: {e}")
                st.error(f"❌ Fehler bei der Message-Analyse: {e}")


def _show_order_analysis_section():
    """Zeigt die Order-Analyse-Sektion"""
    st.markdown("### 🔍 Order Analysis")
    st.markdown("**Order-Analyse (Template-Validierung temporär deaktiviert)**")
    st.info("ℹ️ Template-Validierung temporär deaktiviert - nur Message-Analyse verfügbar")

    # Einfache Order-Informationen
    st.markdown("#### 📋 Verfügbare Topics")
    available_topics = [
        "ccu/order/request",
        "ccu/order/response",
        "module/v1/*/status",
        "module/v1/*/state",
        "module/v1/*/connection",
        "module/v1/*/order",
        "module/v1/*/factsheet",
    ]

    for topic in available_topics:
        st.write(f"• {topic}")

    st.markdown("#### 📄 Kategorien")
    categories = [
        {"Kategorie": "CCU", "Beschreibung": "Central Control Unit Messages"},
        {"Kategorie": "MODULE", "Beschreibung": "Module-spezifische Messages"},
        {"Kategorie": "FTS", "Beschreibung": "Fahrerlose Transport System Messages"},
        {"Kategorie": "NODERED", "Beschreibung": "Node-RED Integration Messages"},
        {"Kategorie": "TXT", "Beschreibung": "TXT Controller Messages"},
    ]

    import pandas as pd

    categories_df = pd.DataFrame(categories)
    st.dataframe(categories_df, use_container_width=True)


def _show_message_chains_section():
    """Zeigt die Message-Chains-Sektion für Order-basierte Analyse"""
    st.markdown("### 🔗 Message Chains")
    st.markdown("**Message-Ketten basierend auf orderID, workpieceId, nfcCode**")

    # Session-Auswahl
    st.markdown("#### 1️⃣ Session auswählen")
    sessions_dir = "data/omf-data/sessions"

    if not os.path.exists(sessions_dir):
        st.error("❌ Sessions-Verzeichnis nicht gefunden")
        return

    log_files = [f for f in os.listdir(sessions_dir) if f.endswith('.log')]

    if not log_files:
        st.warning("❌ Keine Session-Dateien gefunden")
        return

    selected_session = st.selectbox("📁 Session auswählen", options=log_files, key="message_chains_session")

    if not selected_session:
        return

    # Order ID eingeben
    st.markdown("#### 2️⃣ Order ID eingeben")
    order_id = st.text_input("Order ID", placeholder="z.B. ORDER-123", key="message_chains_order_id")

    if not order_id:
        st.warning("⚠️ Bitte Order ID eingeben")
        return

    # Zeitbereich-Auswahl
    st.markdown("#### 3️⃣ Zeitbereich auswählen")

    # Schnellauswahl-Buttons
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("5s", key="message_chains_5s"):
            st.session_state.message_chains_time_range = (0.0, 5.0)
            request_refresh()

    with col2:
        if st.button("15s", key="message_chains_15s"):
            st.session_state.message_chains_time_range = (0.0, 15.0)
            request_refresh()

    with col3:
        if st.button("30s", key="message_chains_30s"):
            st.session_state.message_chains_time_range = (0.0, 30.0)
            request_refresh()

    with col4:
        if st.button("60s", key="message_chains_60s"):
            st.session_state.message_chains_time_range = (0.0, 60.0)
            request_refresh()

    with col5:
        if st.button("120s", key="message_chains_120s"):
            st.session_state.message_chains_time_range = (0.0, 120.0)
            request_refresh()

    # Zeitbereich-Schieberegler
    time_range = st.slider(
        "⏱️ Zeitbereich (Sekunden)",
        min_value=0.0,
        max_value=600.0,  # 10 Minuten
        value=st.session_state.get("message_chains_time_range", (0.0, 30.0)),
        step=1.0,
        format="%.1f s",
        key="message_chains_time_slider",
    )

    # Session State aktualisieren
    st.session_state.message_chains_time_range = time_range

    # Aktueller Zeitbereich anzeigen
    st.info(f"📊 Zeitbereich: {time_range[0]:.1f}s - {time_range[1]:.1f}s")

    # Analyse starten
    if st.button("🔍 Order-Chain analysieren", type="primary"):
        with st.spinner("Analysiere Order-Chain..."):
            try:
                # Order-Chain analysieren
                result = _analyze_order_chain(os.path.join(sessions_dir, selected_session), order_id, time_range)

                if result:
                    _render_order_chain_analysis(result)
                else:
                    st.warning("⚠️ Keine Messages für diese Order ID gefunden")

            except Exception as e:
                logger.error(f"❌ Fehler bei der Order-Chain-Analyse: {e}")
                st.error(f"❌ Fehler bei der Order-Chain-Analyse: {e}")


def _load_session_data(session_file: str) -> List[Dict[str, Any]]:
    """Lädt Session-Daten aus einer Log-Datei"""
    try:
        messages = []
        with open(session_file, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        messages.append(msg)
                    except json.JSONDecodeError:
                        continue

        logger.info(f"✅ {len(messages)} Messages aus {session_file} geladen")
        return messages

    except Exception as e:
        logger.error(f"❌ Fehler beim Laden der Session-Daten: {e}")
        return []


def _topic_matches(topic: str, pattern: str) -> bool:
    """Prüft ob ein Topic einem Pattern entspricht"""
    if pattern == topic:
        return True

    # Einfache Wildcard-Unterstützung
    if '*' in pattern:
        pattern_parts = pattern.split('*')
        if len(pattern_parts) == 2:
            return topic.startswith(pattern_parts[0]) and topic.endswith(pattern_parts[1])

    return False


def _render_simple_message_analysis(messages: List[Dict[str, Any]], topic: str):
    """Zeigt eine einfache Message-Analyse mit detaillierter Message-Liste"""
    logger.info(f"📊 Rendere Message-Analyse für {len(messages)} Messages")

    st.markdown("#### 📊 Analyse-Ergebnisse")

    # Statistiken
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Anzahl Messages", len(messages))
    with col2:
        st.metric("Topic", topic)
    with col3:
        if messages:
            st.metric("Zeitbereich", f"{len(messages)} Messages")

    # Message-Liste (wie im Auftrag-Rot Analyzer)
    st.markdown("#### 📋 Messages")

    if not messages:
        st.warning("❌ Keine Messages gefunden")
        return

    st.info(f"📊 {len(messages)} Messages gefunden")

    # Messages nach Timestamp sortieren
    sorted_messages = sorted(messages, key=lambda x: x.get('timestamp', ''))

    # Message-Liste mit aufklappbarem JSON
    for i, msg in enumerate(sorted_messages):
        with st.expander(f"📨 Message {i+1}: {msg.get('topic', 'Unknown')} - {msg.get('timestamp', 'No timestamp')}"):
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("**Metadaten:**")
                st.json(
                    {
                        'topic': msg.get('topic', 'N/A'),
                        'timestamp': msg.get('timestamp', 'N/A'),
                        'qos': msg.get('qos', 'N/A'),
                        'retain': msg.get('retain', 'N/A'),
                    }
                )

            with col2:
                st.markdown("**Payload:**")
                try:
                    payload = json.loads(msg.get('payload', '{}'))
                    st.json(payload)
                except json.JSONDecodeError:
                    st.text(msg.get('payload', 'Kein gültiges JSON'))


def _analyze_order_chain(session_path: str, order_id: str, time_range: Tuple[float, float]) -> Optional[Dict[str, Any]]:
    """Analysiert eine Order-Chain"""
    try:
        # Session-Daten laden
        messages = _load_session_data(session_path)
        if not messages:
            return None

        # Messages nach Order ID filtern
        order_messages = []
        for msg in messages:
            payload = msg.get('payload', {})
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    continue

            if payload.get('orderId') == order_id:
                order_messages.append(msg)

        if not order_messages:
            return None

        # Zeitbereich anwenden
        if time_range[1] > 0:
            start_time = min(msg['timestamp'] for msg in order_messages)
            end_time = start_time + time_range[1]
            order_messages = [msg for msg in order_messages if start_time <= msg['timestamp'] <= end_time]

        return {
            'order_id': order_id,
            'messages': order_messages,
            'time_range': time_range,
            'total_messages': len(order_messages),
        }

    except Exception as e:
        logger.error(f"❌ Fehler bei der Order-Chain-Analyse: {e}")
        return None


def _render_order_chain_analysis(result: Dict[str, Any]):
    """Zeigt die Order-Chain-Analyse"""
    st.markdown("#### 📊 Order-Chain-Analyse")

    # Statistiken
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Order ID", result['order_id'])
    with col2:
        st.metric("Anzahl Messages", result['total_messages'])
    with col3:
        st.metric("Zeitbereich", f"{result['time_range'][1]:.1f}s")

    # Message-Liste
    st.markdown("#### 📋 Messages")
    for i, msg in enumerate(result['messages']):
        with st.expander(f"Message {i+1}: {msg.get('topic', 'Unknown')}"):
            st.json(msg)

    # Graph-Visualisierung
    if len(result['messages']) > 1:
        st.markdown("#### 📈 Message-Chain Graph")
        try:
            graph = _create_order_chain_graph(result['messages'], result['order_id'])
            st.plotly_chart(graph, use_container_width=True)
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen des Graphs: {e}")
            st.error(f"❌ Fehler beim Erstellen des Graphs: {e}")


def _create_order_chain_graph(messages: List[Dict[str, Any]], order_id: str) -> go.Figure:
    """Erstellt einen Graph der Message-Chain"""
    # NetworkX Graph erstellen
    G = nx.DiGraph()

    # Nodes hinzufügen
    for i, msg in enumerate(messages):
        node_id = f"msg_{i}"
        G.add_node(node_id, topic=msg.get('topic', 'Unknown'), timestamp=msg.get('timestamp', 0), message=msg)

    # Edges hinzufügen (chronologisch)
    sorted_messages = sorted(messages, key=lambda x: x.get('timestamp', 0))
    for i in range(len(sorted_messages) - 1):
        G.add_edge(f"msg_{i}", f"msg_{i+1}")

    # Plotly Graph erstellen
    pos = nx.spring_layout(G, k=1, iterations=50)

    # Node-Positionen
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]

    # Edge-Positionen
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # Graph erstellen
    fig = go.Figure()

    # Edges hinzufügen
    fig.add_trace(
        go.Scatter(x=edge_x, y=edge_y, line={"width": 2, "color": '#888'}, hoverinfo='none', mode='lines', name='Edges')
    )

    # Nodes hinzufügen
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[f"Msg {i+1}" for i in range(len(messages))],
            textposition="middle center",
            marker={"size": 20, "color": 'lightblue', "line": {"width": 2, "color": 'darkblue'}},
            name='Messages',
        )
    )

    # Layout
    fig.update_layout(
        title=f"Message Chain für Order: {order_id}",
        titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        margin={"b": 20, "l": 5, "r": 5, "t": 40},
        annotations=[
            {
                "text": "Message-Chain basierend auf Order ID",
                "showarrow": False,
                "xref": "paper",
                "yref": "paper",
                "x": 0.005,
                "y": -0.002,
                "xanchor": 'left',
                "yanchor": 'bottom',
                "font": {"color": '#888', "size": 12},
            }
        ],
        xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
        yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
    )

    return fig
