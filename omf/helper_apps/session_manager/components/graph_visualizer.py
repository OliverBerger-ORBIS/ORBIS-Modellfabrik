"""
Graph Visualizer - Interactive Graph Visualization for Message Chains

Erstellt interaktive Graphen für die Visualisierung von Message-Ketten
mit verschiedenen Layout-Algorithmen und Filteroptionen.
"""

from datetime import datetime
from typing import Any, Dict, List

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from omf.dashboard.tools.logging_config import get_logger

from .graph_analyzer import GraphAnalyzer, MessageNode

logger = get_logger(__name__)


class GraphVisualizer:
    """Erstellt interaktive Graph-Visualisierungen für Message-Ketten"""

    def __init__(self):
        self.analyzer = GraphAnalyzer()
        self.layout_algorithms = {
            "Spring Layout": nx.spring_layout,
            "Circular Layout": nx.circular_layout,
            "Random Layout": nx.random_layout,
            "Shell Layout": nx.shell_layout,
            "Kamada Kawai": nx.kamada_kawai_layout,
            "Planar Layout": nx.planar_layout,
        }

    def render_graph_analysis(self, session_data: Dict[str, Any]) -> None:
        """Rendert die Graph-Analyse-UI"""
        st.header("🔗 Message Chain Graph Analysis")
        st.markdown("**Interaktive Visualisierung von Message-Ketten basierend auf Meta-Informationen**")

        # Session analysieren
        if not self.analyzer.analyze_session(session_data):
            st.error("❌ Fehler bei der Graph-Analyse")
            return

        # Tabs für verschiedene Ansichten
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 Graph Overview", "🔗 Message Chains", "🎯 Interactive Graph", "📈 Statistics"]
        )

        with tab1:
            self._render_graph_overview()

        with tab2:
            self._render_message_chains()

        with tab3:
            self._render_interactive_graph()

        with tab4:
            self._render_statistics()

    def _render_graph_overview(self):
        """Rendert Graph-Übersicht"""
        st.subheader("📊 Graph Overview")

        summary = self.analyzer.get_graph_summary()

        # Metriken anzeigen
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Messages", summary["total_messages"])

        with col2:
            st.metric("Graph Nodes", summary["total_nodes"])

        with col3:
            st.metric("Graph Edges", summary["total_edges"])

        with col4:
            st.metric("Message Chains", summary["message_chains"])

        # Verbindungsstatistiken
        st.subheader("🔗 Connection Types")

        if summary["connection_stats"]:
            connection_df = pd.DataFrame(
                list(summary["connection_stats"].items()), columns=["Connection Type", "Count"]
            )

            # Farben für verschiedene Verbindungstypen
            color_map = {
                "order_id": "#FF6B6B",
                "workpiece_id": "#4ECDC4",
                "nfc_code": "#45B7D1",
                "module_id": "#96CEB4",
                "temporal": "#FFEAA7",
            }

            connection_df["Color"] = connection_df["Connection Type"].map(color_map).fillna("#DDA0DD")

            fig = px.bar(
                connection_df,
                x="Connection Type",
                y="Count",
                color="Connection Type",
                color_discrete_map=color_map,
                title="Message Connections by Type",
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Keine Verbindungen gefunden")

        # Graph-Eigenschaften
        st.subheader("📈 Graph Properties")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Graph Density", f"{summary['graph_density']:.3f}")
            st.metric("Connected", "Yes" if summary["is_connected"] else "No")

        with col2:
            st.metric("Strongly Connected Components", summary["strongly_connected_components"])

    def _render_message_chains(self):
        """Rendert Message-Ketten"""
        st.subheader("🔗 Message Chains")

        # Filter für Mindestlänge
        min_length = st.slider("Minimum Chain Length", 2, 10, 2)

        chains = self.analyzer.get_message_chains(min_length)

        if not chains:
            st.info("ℹ️ Keine Message-Ketten gefunden")
            return

        st.write(f"**Gefundene Ketten:** {len(chains)}")

        # Ketten anzeigen
        for i, chain in enumerate(chains[:10]):  # Zeige max 10 Ketten
            with st.expander(f"Chain {i+1} ({len(chain)} messages)", expanded=False):
                self._render_chain_details(chain)

    def _render_chain_details(self, chain: List[MessageNode]):
        """Rendert Details einer Message-Kette"""
        # Timeline der Kette
        chain_data = []
        for j, msg in enumerate(chain):
            chain_data.append(
                {
                    "Step": j + 1,
                    "Timestamp": msg.timestamp,
                    "Topic": msg.topic,
                    "Order ID": msg.order_id or "-",
                    "Workpiece ID": msg.workpiece_id or "-",
                    "NFC Code": msg.nfc_code or "-",
                    "Module ID": msg.module_id or "-",
                    "Message Type": msg.message_type or "-",
                }
            )

        chain_df = pd.DataFrame(chain_data)
        st.dataframe(chain_df, use_container_width=True)

        # Timeline-Visualisierung
        if len(chain) > 1:
            fig = go.Figure()

            for j, msg in enumerate(chain):
                fig.add_trace(
                    go.Scatter(
                        x=[msg.timestamp],
                        y=[j],
                        mode='markers+text',
                        marker={"size": 10, "color": px.colors.qualitative.Set1[j % len(px.colors.qualitative.Set1)]},
                        text=[f"Step {j+1}"],
                        textposition="top center",
                        name=f"Message {j+1}",
                        hovertemplate=f"<b>Step {j+1}</b><br>"
                        + "Time: %{x}<br>"
                        + f"Topic: {msg.topic}<br>"
                        + f"Order ID: {msg.order_id or 'N/A'}<br>"
                        + f"Workpiece ID: {msg.workpiece_id or 'N/A'}<br>"
                        + f"NFC Code: {msg.nfc_code or 'N/A'}<br>"
                        + f"Module ID: {msg.module_id or 'N/A'}<extra></extra>",
                    )
                )

            fig.update_layout(
                title="Message Chain Timeline", xaxis_title="Time", yaxis_title="Step", showlegend=False, height=400
            )

            st.plotly_chart(fig, use_container_width=True)

    def _render_interactive_graph(self):
        """Rendert interaktiven Graph"""
        st.subheader("🎯 Interactive Graph")

        # Layout-Auswahl
        col1, col2 = st.columns([1, 2])

        with col1:
            layout_name = st.selectbox("Layout Algorithm", list(self.layout_algorithms.keys()))
            show_labels = st.checkbox("Show Labels", value=True)
            node_size = st.slider("Node Size", 5, 30, 15)

            # Debug-Informationen
            if st.checkbox("🔍 Debug-Info anzeigen"):
                st.write("**Gefundene Meta-Informationen:**")
                order_ids = set()
                workpiece_ids = set()
                nfc_codes = set()
                module_ids = set()

                for msg in self.analyzer.messages:
                    if msg.order_id:
                        order_ids.add(msg.order_id)
                    if msg.workpiece_id:
                        workpiece_ids.add(msg.workpiece_id)
                    if msg.nfc_code:
                        nfc_codes.add(msg.nfc_code)
                    if msg.module_id:
                        module_ids.add(msg.module_id)

                st.write(f"Order IDs: {len(order_ids)} - {list(order_ids)[:5]}")
                st.write(f"Workpiece IDs: {len(workpiece_ids)} - {list(workpiece_ids)[:5]}")
                st.write(f"NFC Codes: {len(nfc_codes)} - {list(nfc_codes)[:5]}")
                st.write(f"Module IDs: {len(module_ids)} - {list(module_ids)[:5]}")

                # Message-Ketten Debug
                chains = self.analyzer.get_message_chains(2)
                st.write(f"Message Chains (min 2): {len(chains)}")
                if chains:
                    for i, chain in enumerate(chains[:3]):
                        st.write(f"Chain {i+1}: {len(chain)} messages")
                        for j, msg in enumerate(chain[:3]):
                            st.write(f"  {j+1}. {msg.topic} - Order: {msg.order_id}, Workpiece: {msg.workpiece_id}")

        with col2:
            # Filter
            st.write("**Filter:**")
            filter_order_id = st.text_input("Order ID Filter", placeholder="Enter Order ID")
            filter_module_id = st.text_input("Module ID Filter", placeholder="Enter Module ID")
            filter_message_type = st.multiselect(
                "Message Type Filter",
                ["state", "order", "status", "flow", "other"],
                default=["state", "order", "status", "flow", "other"],
            )

        # Graph erstellen
        if st.button("🔄 Update Graph", type="primary"):
            self._create_interactive_graph(
                layout_name, show_labels, node_size, filter_order_id, filter_module_id, filter_message_type
            )

    def _create_interactive_graph(
        self,
        layout_name: str,
        show_labels: bool,
        node_size: int,
        filter_order_id: str,
        filter_module_id: str,
        filter_message_type: List[str],
    ):
        """Erstellt interaktiven Graph"""
        try:
            # Graph filtern
            filtered_graph = self._filter_graph(filter_order_id, filter_module_id, filter_message_type)

            if filtered_graph.number_of_nodes() == 0:
                st.warning("⚠️ Keine Knoten nach Filterung gefunden")
                return

            # Layout berechnen
            layout_func = self.layout_algorithms[layout_name]
            pos = layout_func(filtered_graph)

            # Plotly-Graph erstellen
            edge_x = []
            edge_y = []
            edge_info = []

            for edge in filtered_graph.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

                # Edge-Informationen
                edge_data = filtered_graph[edge[0]][edge[1]]
                edge_info.append(f"Connection: {edge_data.get('connection_type', 'unknown')}")

            # Edges
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y, line={"width": 2, "color": '#888'}, hoverinfo='none', mode='lines'
            )

            # Nodes
            node_x = []
            node_y = []
            node_text = []
            node_hover = []
            node_colors = []

            for node in filtered_graph.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)

                # Node-Informationen
                node_data = filtered_graph.nodes[node]
                node_text.append(node if show_labels else "")

                # Hover-Informationen
                hover_text = f"<b>Message: {node}</b><br>"
                hover_text += f"Topic: {node_data.get('topic', 'N/A')}<br>"
                hover_text += f"Order ID: {node_data.get('order_id', 'N/A')}<br>"
                hover_text += f"Workpiece ID: {node_data.get('workpiece_id', 'N/A')}<br>"
                hover_text += f"NFC Code: {node_data.get('nfc_code', 'N/A')}<br>"
                hover_text += f"Module ID: {node_data.get('module_id', 'N/A')}<br>"
                hover_text += f"Message Type: {node_data.get('message_type', 'N/A')}"
                node_hover.append(hover_text)

                # Farbe basierend auf Message-Typ
                color_map = {
                    "state": "#FF6B6B",
                    "order": "#4ECDC4",
                    "status": "#45B7D1",
                    "flow": "#96CEB4",
                    "other": "#DDA0DD",
                }
                node_colors.append(color_map.get(node_data.get('message_type', 'other'), "#DDA0DD"))

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text',
                hoverinfo='text',
                hovertext=node_hover,
                text=node_text,
                textposition="middle center",
                marker={"size": node_size, "color": node_colors, "line": {"width": 2, "color": 'white'}},
            )

            # Graph zusammenstellen
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title={
                        "text": f'Message Chain Graph ({filtered_graph.number_of_nodes()} nodes, '
                        f'{filtered_graph.number_of_edges()} edges)',
                        "font": {"size": 16},
                    },
                    showlegend=False,
                    hovermode='closest',
                    margin={"b": 20, "l": 5, "r": 5, "t": 40},
                    annotations=[
                        {
                            "text": "Interactive graph - hover over nodes for details",
                            "showarrow": False,
                            "xref": "paper",
                            "yref": "paper",
                            "x": 0.005,
                            "y": -0.002,
                            "xanchor": "left",
                            "yanchor": "bottom",
                            "font": {"color": "gray", "size": 12},
                        }
                    ],
                    xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                    yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                    height=600,
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            logger.error(f"Fehler beim Erstellen des interaktiven Graphen: {e}")
            st.error(f"Fehler beim Erstellen des Graphen: {e}")

    def _filter_graph(self, order_id: str, module_id: str, message_types: List[str]) -> nx.DiGraph:
        """Filtert Graph basierend auf Kriterien"""
        filtered_graph = self.analyzer.graph.copy()

        # Knoten filtern
        nodes_to_remove = []
        for node, data in filtered_graph.nodes(data=True):
            should_remove = False

            # Order ID Filter
            if order_id and data.get('order_id') != order_id:
                should_remove = True

            # Module ID Filter
            if module_id and data.get('module_id') != module_id:
                should_remove = True

            # Message Type Filter
            if data.get('message_type') not in message_types:
                should_remove = True

            if should_remove:
                nodes_to_remove.append(node)

        # Knoten entfernen
        for node in nodes_to_remove:
            filtered_graph.remove_node(node)

        return filtered_graph

    def _render_statistics(self):
        """Rendert detaillierte Statistiken"""
        st.subheader("📈 Detailed Statistics")

        summary = self.analyzer.get_graph_summary()

        # Graph-Metriken
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Graph Density", f"{summary['graph_density']:.4f}")
            st.metric("Average Degree", f"{2 * summary['total_edges'] / max(summary['total_nodes'], 1):.2f}")

        with col2:
            st.metric("Connected Components", summary['strongly_connected_components'])
            st.metric("Is Connected", "Yes" if summary['is_connected'] else "No")

        # Message-Verteilung
        st.subheader("📊 Message Distribution")

        message_types = {}
        for msg in self.analyzer.messages:
            msg_type = msg.message_type or "unknown"
            message_types[msg_type] = message_types.get(msg_type, 0) + 1

        if message_types:
            type_df = pd.DataFrame(list(message_types.items()), columns=["Message Type", "Count"])

            fig = px.pie(type_df, values="Count", names="Message Type", title="Message Distribution by Type")
            st.plotly_chart(fig, use_container_width=True)

        # Zeitliche Verteilung
        st.subheader("⏰ Temporal Distribution")

        if self.analyzer.messages:
            timestamps = [msg.timestamp for msg in self.analyzer.messages]
            time_df = pd.DataFrame({"timestamp": timestamps, "count": [1] * len(timestamps)})

            # Gruppiere nach Minuten
            time_df["minute"] = time_df["timestamp"].dt.floor("min")
            minute_counts = time_df.groupby("minute").size().reset_index(name="count")

            fig = px.line(minute_counts, x="minute", y="count", title="Messages per Minute")
            st.plotly_chart(fig, use_container_width=True)

        # Export-Button
        st.subheader("💾 Export Data")

        if st.button("📥 Export Graph Data"):
            graph_data = self.analyzer.export_graph_data()

            # JSON-Download
            import json

            json_str = json.dumps(graph_data, indent=2, default=str)

            st.download_button(
                label="Download Graph Data (JSON)",
                data=json_str,
                file_name=f"graph_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )
