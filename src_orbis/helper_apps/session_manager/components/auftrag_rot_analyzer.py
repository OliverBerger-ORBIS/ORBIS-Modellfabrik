"""
Auftrag-Rot Analyzer - Spezifische Analyse für ccu/order/request mit orderType: PRODUCTION

Analysiert die Message-Kette für einen roten Auftrag und erstellt einen Graph
basierend auf orderId, workpieceId und nfcCode Verbindungen.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import plotly.graph_objects as go
import streamlit as st

from src_orbis.omf.dashboard.utils.ui_refresh import request_refresh
from src_orbis.omf.tools.logging_config import get_logger

logger = get_logger("session_manager.auftrag_rot_analyzer")


class AuftragRotAnalyzer:
    """Analysiert Message-Ketten für rote Aufträge (orderType: PRODUCTION)"""

    def __init__(self):
        self.messages = []
        self.graph = nx.DiGraph()
        self.order_id = None
        self.workpiece_id = None
        self.nfc_code = None

    def load_session_from_log(self, log_file_path: str) -> bool:
        """Lädt Session-Daten aus einer .log Datei"""
        try:
            with open(log_file_path, encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            message = json.loads(line.strip())
                            self.messages.append(message)
                        except json.JSONDecodeError:
                            continue

            logger.info(f"✅ {len(self.messages)} Messages aus {log_file_path} geladen")
            return True
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Session: {e}")
            return False

    def find_ccu_order_request(self) -> Optional[Dict[str, Any]]:
        """Findet die ccu/order/request Message mit orderType: PRODUCTION"""
        for message in self.messages:
            if message.get('topic') == 'ccu/order/request' and message.get('payload'):
                try:
                    payload = json.loads(message['payload'])
                    if payload.get('orderType') == 'PRODUCTION':
                        logger.info(f"🎯 CCU Order Request gefunden: {payload}")
                        return message
                except json.JSONDecodeError:
                    continue
        return None

    def extract_order_metadata(self, ccu_message: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert Metadaten aus der CCU Order Request Message"""
        try:
            payload = json.loads(ccu_message['payload'])
            metadata = {
                'order_type': payload.get('orderType'),
                'workpiece_type': payload.get('type'),
                'timestamp': payload.get('timestamp'),
                'ccu_timestamp': ccu_message['timestamp'],
            }
            logger.info(f"📋 Order Metadaten: {metadata}")
            return metadata
        except Exception as e:
            logger.error(f"❌ Fehler beim Extrahieren der Metadaten: {e}")
            return {}

    def find_related_messages(
        self,
        session_data: List[Dict[str, Any]],
        root_message: Dict[str, Any],
        time_filter_seconds: Optional[Tuple[float, float]] = None,
    ) -> List[Dict[str, Any]]:
        """Findet alle mit der Root-Message verbundenen Messages"""
        root_timestamp = root_message['timestamp']
        root_time = datetime.fromisoformat(root_timestamp.replace('Z', '+00:00'))

        related_messages = []

        # Bestimme Zeitfenster
        if time_filter_seconds:
            # Verwende benutzerdefinierten Zeitfilter
            start_offset, end_offset = time_filter_seconds
            start_time = root_time + timedelta(seconds=start_offset)
            end_time = root_time + timedelta(seconds=end_offset)
            logger.info(f"⏱️ Zeitfilter: {start_offset:.1f}s - {end_offset:.1f}s nach Root Message")
        else:
            # Standard: 5 Minuten nach der Root Message
            start_time = root_time
            end_time = root_time + timedelta(seconds=300)  # 5 Minuten
            logger.info("⏱️ Standard-Zeitfilter: 5 Minuten nach Root Message")

        # Suche nach Messages im definierten Zeitfenster
        for message in session_data:
            try:
                msg_time = datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))

                # Prüfe ob Message im Zeitfenster liegt
                if start_time <= msg_time <= end_time:
                    related_messages.append(message)
            except Exception:
                continue

        logger.info(
            f"🔗 {len(related_messages)} verwandte Messages gefunden (Zeitfenster: {start_time.strftime('%H:%M:%S')} - {end_time.strftime('%H:%M:%S')})"
        )
        return related_messages

    def extract_order_id_from_messages(self, messages: List[Dict[str, Any]]) -> Optional[str]:
        """Extrahiert orderId aus den Messages"""
        for message in messages:
            if message.get('payload'):
                try:
                    payload = json.loads(message['payload'])
                    if 'orderId' in payload and payload['orderId']:
                        order_id = payload['orderId']
                        if order_id != "" and order_id != 0:
                            logger.info(f"🆔 OrderId gefunden: {order_id}")
                            return order_id
                except json.JSONDecodeError:
                    continue
        return None

    def extract_workpiece_metadata(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extrahiert workpieceId und nfcCode aus den Messages"""
        workpieces = []

        for message in messages:
            if message.get('payload'):
                try:
                    payload = json.loads(message['payload'])

                    # Suche nach workpieceId in verschiedenen Strukturen
                    workpiece_id = None
                    nfc_code = None
                    load_type = None

                    # Direkte workpieceId
                    if 'workpieceId' in payload:
                        workpiece_id = payload['workpieceId']

                    # In loads Array
                    if 'loads' in payload and isinstance(payload['loads'], list):
                        for load in payload['loads']:
                            if isinstance(load, dict):
                                if 'loadId' in load and load['loadId']:
                                    workpiece_id = load['loadId']
                                if 'loadType' in load and load['loadType']:
                                    load_type = load['loadType']

                    # In workpiece Objekt
                    if 'workpiece' in payload and isinstance(payload['workpiece'], dict):
                        wp = payload['workpiece']
                        if 'id' in wp and wp['id']:
                            workpiece_id = wp['id']
                        if 'type' in wp and wp['type']:
                            load_type = wp['type']

                    # nfcCode in verschiedenen Strukturen
                    if 'nfcCode' in payload:
                        nfc_code = payload['nfcCode']
                    elif 'loadId' in payload and payload['loadId']:
                        nfc_code = payload['loadId']

                    if workpiece_id or nfc_code or load_type:
                        workpieces.append(
                            {
                                'message': message,
                                'workpiece_id': workpiece_id,
                                'nfc_code': nfc_code,
                                'load_type': load_type,
                                'topic': message['topic'],
                                'timestamp': message['timestamp'],
                            }
                        )

                except json.JSONDecodeError:
                    continue

        logger.info(f"🔧 {len(workpieces)} Workpiece-Messages gefunden")
        return workpieces

    def build_message_chain_graph(
        self, root_message: Dict[str, Any], related_messages: List[Dict[str, Any]]
    ) -> nx.DiGraph:
        """Erstellt einen gerichteten Graph der Message-Kette"""
        graph = nx.DiGraph()

        # Root Message als Wurzel
        graph.add_node(
            'root_message',
            type='root_message',
            topic=root_message.get('topic', 'unknown'),
            timestamp=root_message['timestamp'],
            payload=root_message.get('payload', ''),
            color='red',
            size=20,
        )

        # OrderId extrahieren
        order_id = self.extract_order_id_from_messages(related_messages)
        if order_id:
            graph.add_node(f'order_{order_id}', type='order', order_id=order_id, color='blue', size=15)
            graph.add_edge('root_message', f'order_{order_id}', relation='creates')

        # Workpiece-Messages hinzufügen
        workpieces = self.extract_workpiece_metadata(related_messages)
        for i, wp in enumerate(workpieces):
            node_id = f'workpiece_{i}'
            graph.add_node(
                node_id,
                type='workpiece',
                topic=wp['topic'],
                timestamp=wp['timestamp'],
                workpiece_id=wp['workpiece_id'],
                nfc_code=wp['nfc_code'],
                load_type=wp['load_type'],
                color='green',
                size=10,
            )

            # Verbindung zur Order
            if order_id:
                graph.add_edge(f'order_{order_id}', node_id, relation='processes')

            # Verbindung zur Root Message
            graph.add_edge('root_message', node_id, relation='triggers')

        # FTS Messages hinzufügen
        fts_messages = [msg for msg in related_messages if 'fts/' in msg.get('topic', '')]
        for i, fts_msg in enumerate(fts_messages):
            node_id = f'fts_{i}'
            graph.add_node(
                node_id, type='fts', topic=fts_msg['topic'], timestamp=fts_msg['timestamp'], color='orange', size=12
            )

            if order_id:
                graph.add_edge(f'order_{order_id}', node_id, relation='transports')

        # Module Messages hinzufügen
        module_messages = [msg for msg in related_messages if 'module/' in msg.get('topic', '')]
        for i, mod_msg in enumerate(module_messages):
            node_id = f'module_{i}'
            graph.add_node(
                node_id, type='module', topic=mod_msg['topic'], timestamp=mod_msg['timestamp'], color='purple', size=8
            )

            if order_id:
                graph.add_edge(f'order_{order_id}', node_id, relation='controls')

        logger.info(f"📊 Graph erstellt mit {graph.number_of_nodes()} Knoten und {graph.number_of_edges()} Kanten")
        return graph

    def create_plotly_graph(self, graph: nx.DiGraph) -> go.Figure:
        """Erstellt eine Plotly-Visualisierung des Graphen"""
        if graph.number_of_nodes() == 0:
            return go.Figure()

        # Layout berechnen
        pos = nx.spring_layout(graph, k=3, iterations=50)

        # Knoten vorbereiten
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []

        for node in graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # Node-Info
            node_data = graph.nodes[node]
            node_text.append(
                f"{node}<br>Type: {node_data.get('type', 'unknown')}<br>Topic: {node_data.get('topic', 'N/A')}"
            )

            # Farbe basierend auf Typ
            color_map = {
                'ccu_order_request': 'red',
                'order': 'blue',
                'workpiece': 'green',
                'fts': 'orange',
                'module': 'purple',
            }
            node_colors.append(color_map.get(node_data.get('type', 'unknown'), 'gray'))

            # Größe
            node_sizes.append(node_data.get('size', 10))

        # Kanten vorbereiten
        edge_x = []
        edge_y = []

        for edge in graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # Plotly Figure erstellen
        fig = go.Figure()

        # Kanten hinzufügen
        fig.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=2, color='rgba(125,125,125,0.5)'),
                hoverinfo='none',
                mode='lines',
                name='Edges',
            )
        )

        # Knoten hinzufügen
        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="middle center",
                marker=dict(size=node_sizes, color=node_colors, line=dict(width=2, color='black')),
                name='Nodes',
            )
        )

        # Layout anpassen
        fig.update_layout(
            title=dict(text='Auftrag-Rot Message Chain Graph', font=dict(size=16)),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="Message-Kette für ccu/order/request mit orderType: PRODUCTION",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.005,
                    y=-0.002,
                    xanchor="left",
                    yanchor="bottom",
                    font=dict(color="gray", size=12),
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
        )

        return fig

    def analyze_auftrag_rot(
        self, log_file_path: str, time_filter_seconds: Optional[Tuple[float, float]] = None
    ) -> Dict[str, Any]:
        """Hauptfunktion für die Auftrag-Rot Analyse"""
        logger.info("🔍 Starte Auftrag-Rot Analyse")

        # Session laden
        if not self.load_session_from_log(log_file_path):
            return {'error': 'Fehler beim Laden der Session'}

        # CCU Order Request finden
        ccu_message = self.find_ccu_order_request()
        if not ccu_message:
            return {'error': 'Keine ccu/order/request Message mit orderType: PRODUCTION gefunden'}

        # Metadaten extrahieren
        metadata = self.extract_order_metadata(ccu_message)

        # Verwandte Messages finden (mit Zeitfilter)
        related_messages = self.find_related_messages(ccu_message, time_filter_seconds)

        # Graph erstellen
        graph = self.build_message_chain_graph(ccu_message, related_messages)

        # Plotly-Visualisierung
        plotly_fig = self.create_plotly_graph(graph)

        return {
            'success': True,
            'metadata': metadata,
            'ccu_message': ccu_message,
            'related_messages_count': len(related_messages),
            'graph_nodes': graph.number_of_nodes(),
            'graph_edges': graph.number_of_edges(),
            'plotly_figure': plotly_fig,
            'graph': graph,
            'time_filter': time_filter_seconds,
        }

    def render_analysis_ui(self, analysis_result: Dict[str, Any]) -> None:
        """Rendert die Analyse-UI im Streamlit Dashboard"""
        if 'error' in analysis_result:
            st.error(f"❌ {analysis_result['error']}")
            return

        st.success("✅ Auftrag-Rot Analyse erfolgreich")

        # Metadaten anzeigen
        st.subheader("📋 Order Metadaten")
        metadata = analysis_result['metadata']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Order Type", metadata.get('order_type', 'N/A'))
        with col2:
            st.metric("Workpiece Type", metadata.get('workpiece_type', 'N/A'))
        with col3:
            st.metric("Timestamp", metadata.get('timestamp', 'N/A'))

        # Statistiken
        st.subheader("📊 Analyse Statistiken")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Verwandte Messages", analysis_result['related_messages_count'])
        with col2:
            st.metric("Graph Knoten", analysis_result['graph_nodes'])
        with col3:
            st.metric("Graph Kanten", analysis_result['graph_edges'])
        with col4:
            time_filter = analysis_result.get('time_filter')
            if time_filter:
                st.metric("Zeitfilter", f"{time_filter[0]:.1f}s - {time_filter[1]:.1f}s")
            else:
                st.metric("Zeitfilter", "Standard (5 Min)")

        # Graph-Visualisierung
        st.subheader("🔗 Message Chain Graph")
        if 'plotly_figure' in analysis_result:
            st.plotly_chart(analysis_result['plotly_figure'], use_container_width=True)

        # Graph-Details
        st.subheader("📋 Graph Details")
        graph = analysis_result['graph']

        # Knoten-Liste
        st.write("**Knoten:**")
        for node in graph.nodes():
            node_data = graph.nodes[node]
            st.write(f"- **{node}**: {node_data.get('type', 'unknown')} ({node_data.get('topic', 'N/A')})")

        # Kanten-Liste
        st.write("**Kanten:**")
        for edge in graph.edges():
            edge_data = graph.edges[edge]
            st.write(f"- **{edge[0]}** → **{edge[1]}**: {edge_data.get('relation', 'unknown')}")


def load_session_data(session_file: str) -> list:
    """Lädt Session-Daten aus einer Log-Datei"""
    import json
    import os

    sessions_dir = "data/omf-data/sessions"
    log_path = os.path.join(sessions_dir, session_file)

    if not os.path.exists(log_path):
        return []

    messages = []
    try:
        with open(log_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        messages.append(msg)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.error(f"Fehler beim Laden der Session: {e}")
        return []

    return messages


def analyze_auftrag_rot_with_root(session_file: str, root_message: dict, time_range: tuple) -> dict:
    """Analysiert Message-Kette basierend auf einer Root-Message"""
    import os

    analyzer = AuftragRotAnalyzer()
    log_path = os.path.join("data/omf-data/sessions", session_file)

    # Verwandte Messages finden
    session_data = load_session_data(session_file)
    related_messages = analyzer.find_related_messages(session_data, root_message, time_range)

    # Graph erstellen
    graph = analyzer.build_message_chain_graph(root_message, related_messages)

    # Plotly-Visualisierung
    plotly_figure = analyzer.create_plotly_graph(graph)

    return {
        'root_message': root_message,
        'related_messages': related_messages,
        'graph': graph,
        'plotly_figure': plotly_figure,
        'related_messages_count': len(related_messages),
        'graph_nodes': graph.number_of_nodes(),
        'graph_edges': graph.number_of_edges(),
        'time_filter': time_range,
    }


def render_message_list(result: dict) -> None:
    """Rendert die Liste der gefundenen Messages mit aufklappbarem JSON"""
    related_messages = result.get('related_messages', [])

    if not related_messages:
        st.warning("❌ Keine verwandten Messages gefunden")
        return

    st.info(f"📊 {len(related_messages)} verwandte Messages gefunden")

    # Messages nach Timestamp sortieren
    sorted_messages = sorted(related_messages, key=lambda x: x.get('timestamp', ''))

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


def render_graph_visualization(result: dict) -> None:
    """Rendert die Graph-Visualisierung"""
    plotly_figure = result.get('plotly_figure')

    if plotly_figure and plotly_figure.data:
        st.plotly_chart(plotly_figure, use_container_width=True)

        # Graph-Statistiken
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Knoten", result.get('graph_nodes', 0))

        with col2:
            st.metric("Kanten", result.get('graph_edges', 0))

        with col3:
            st.metric("Messages", result.get('related_messages_count', 0))
    else:
        st.warning("❌ Kein Graph verfügbar")


def show_auftrag_rot_analysis():
    """Zeigt die umstrukturierte Auftrag-Rot Analyse UI"""
    st.header("🔴 Auftrag-Rot Analyse")
    st.markdown("**Schritt-für-Schritt Analyse von Message-Ketten**")

    # Schritt 1: Session-Auswahl
    st.markdown("### 1️⃣ Session auswählen")
    sessions_dir = "data/omf-data/sessions"
    import os

    if os.path.exists(sessions_dir):
        log_files = [f for f in os.listdir(sessions_dir) if f.endswith('.log') and 'rot' in f.lower()]

        if not log_files:
            st.warning("❌ Keine rot-Sessions gefunden")
            return

        selected_session = st.selectbox("📁 Session auswählen", options=log_files, key="auftrag_rot_session")

        if not selected_session:
            return

        # Session laden und Topics extrahieren
        session_data = load_session_data(selected_session)
        if not session_data:
            st.error("❌ Fehler beim Laden der Session")
            return

        # Schritt 2: Topic-Auswahl
        st.markdown("### 2️⃣ Topic auswählen")

        # Verfügbare Topics aus der Session extrahieren
        available_topics = list(set(msg.get('topic', '') for msg in session_data if msg.get('topic')))
        available_topics.sort()

        if not available_topics:
            st.warning("❌ Keine Topics in der Session gefunden")
            return

        selected_topic = st.selectbox("📡 Topic auswählen", options=available_topics, key="auftrag_rot_topic")

        if not selected_topic:
            return

        # Schritt 3: Message-Auswahl
        st.markdown("### 3️⃣ Message auswählen")

        # Messages für das gewählte Topic finden
        topic_messages = [msg for msg in session_data if msg.get('topic') == selected_topic]

        if not topic_messages:
            st.warning(f"❌ Keine Messages für Topic '{selected_topic}' gefunden")
            return

        st.info(f"📊 {len(topic_messages)} Messages für Topic '{selected_topic}' gefunden")

        # Message-Auswahl (erste Message als Default)
        if len(topic_messages) == 1:
            selected_message = topic_messages[0]
            st.success("✅ Nur eine Message gefunden - wird automatisch ausgewählt")
        else:
            # Dropdown für Message-Auswahl
            message_options = []
            for i, msg in enumerate(topic_messages):
                timestamp = msg.get('timestamp', '')
                payload_preview = (
                    str(msg.get('payload', ''))[:50] + "..."
                    if len(str(msg.get('payload', ''))) > 50
                    else str(msg.get('payload', ''))
                )
                message_options.append(f"Message {i+1}: {timestamp} - {payload_preview}")

            selected_message_idx = st.selectbox(
                "📨 Message auswählen",
                options=range(len(topic_messages)),
                format_func=lambda x: message_options[x],
                key="auftrag_rot_message",
            )
            selected_message = topic_messages[selected_message_idx]

        # Schritt 4: Zeitbereich-Einstellungen
        st.markdown("### 4️⃣ Zeitbereich-Einstellungen")

        # Schnellauswahl-Buttons
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if st.button("5s", key="auftrag_rot_5s"):
                st.session_state.auftrag_rot_time_range = (0.0, 5.0)
                request_refresh()

        with col2:
            if st.button("15s", key="auftrag_rot_15s"):
                st.session_state.auftrag_rot_time_range = (0.0, 15.0)
                request_refresh()

        with col3:
            if st.button("30s", key="auftrag_rot_30s"):
                st.session_state.auftrag_rot_time_range = (0.0, 30.0)
                request_refresh()

        with col4:
            if st.button("60s", key="auftrag_rot_60s"):
                st.session_state.auftrag_rot_time_range = (0.0, 60.0)
                request_refresh()

        with col5:
            if st.button("120s", key="auftrag_rot_120s"):
                st.session_state.auftrag_rot_time_range = (0.0, 120.0)
                request_refresh()

        # Zeitbereich-Schieberegler
        time_range = st.slider(
            "⏱️ Zeitbereich (Sekunden)",
            min_value=0.0,
            max_value=600.0,  # 10 Minuten
            value=st.session_state.get('auftrag_rot_time_range', (0.0, 30.0)),
            step=1.0,
            format="%.1f s",
            key="auftrag_rot_time_slider",
        )

        # Session State aktualisieren
        st.session_state.auftrag_rot_time_range = time_range

        # Aktueller Zeitbereich anzeigen
        st.info(f"📊 Zeitbereich: {time_range[0]:.1f}s - {time_range[1]:.1f}s")

        # Schritt 5: Analyse starten
        st.markdown("### 5️⃣ Analyse starten")

        if st.button("🔍 Analyse starten", type="primary", key="auftrag_rot_analyze"):
            with st.spinner("🔍 Analysiere Message-Kette..."):
                # Analyse durchführen
                result = analyze_auftrag_rot_with_root(selected_session, selected_message, time_range)

                if 'error' in result:
                    st.error(f"❌ Fehler bei der Analyse: {result['error']}")
                else:
                    # Schritt 6: Message-Liste anzeigen
                    st.markdown("### 6️⃣ Gefundene Messages")
                    render_message_list(result)

                    # Schritt 7: Graph-Visualisierung
                    st.markdown("### 7️⃣ Graph-Visualisierung")
                    render_graph_visualization(result)
    else:
        st.error("❌ Sessions-Verzeichnis nicht gefunden")
