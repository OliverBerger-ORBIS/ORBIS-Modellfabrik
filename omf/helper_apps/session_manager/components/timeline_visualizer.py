"""
Timeline Visualizer - Creates timeline visualizations for session analysis
"""

from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from omf.tools.logging_config import get_logger
from omf.tools.topic_manager import OmfTopicManager

logger = get_logger(__name__)


class TimelineVisualizer:
    """Creates timeline visualizations for session analysis"""

    def __init__(self):
        self.topic_manager = OmfTopicManager()

    def create_timeline_visualization(self, messages: List[Dict], selected_topics: List[str] = None) -> go.Figure:
        """Erstellt Timeline-Visualisierung (Zeit vs Topic-Name)"""
        try:
            logger.info(f"Erstelle Timeline-Visualisierung mit Topics: {selected_topics}")

            if not messages:
                logger.warning("Keine Messages verfügbar für Timeline")
                return go.Figure()

            # Filtere Messages nach ausgewählten Topics
            if selected_topics:
                messages = [msg for msg in messages if msg["topic"] in selected_topics]
                logger.debug(f"Anzahl Messages nach Filterung: {len(messages)}")

            # Erstelle DataFrame für Plotly
            df = pd.DataFrame(messages)
            if df.empty:
                logger.warning("DataFrame ist leer nach Filterung")
                return go.Figure()

            df["timestamp"] = pd.to_datetime(df["timestamp"])
            logger.debug(f"DataFrame erstellt mit {len(df)} Zeilen")

            # Erstelle Timeline-Plot
            fig = go.Figure()

            # Gruppiere nach Topics
            unique_topics = df["topic"].unique()
            logger.debug(f"Eindeutige Topics: {unique_topics}")

            # Erstelle Topic-zu-Y-Position Mapping
            topic_y_mapping = {topic: i for i, topic in enumerate(unique_topics)}

            for topic in unique_topics:
                try:
                    topic_messages = df[df["topic"] == topic]
                    logger.debug(f"Topic {topic}: {len(topic_messages)} Messages")

                    # Y-Position basierend auf Topic-Reihenfolge
                    y_pos = topic_y_mapping[topic]

                    friendly_name = self.topic_manager.get_friendly_name(topic)
                    logger.debug(f"Topic {topic} -> Friendly Name: {friendly_name}")

                    # Erstelle Hover-Text mit Payload-Info
                    hover_texts = []
                    for _, row in topic_messages.iterrows():
                        payload_preview = (
                            str(row["payload"])[:100] + "..." if len(str(row["payload"])) > 100 else str(row["payload"])
                        )
                        hover_texts.append(
                            f"Topic: {row['topic']}<br>Zeit: {row['timestamp']}<br>Payload: {payload_preview}"
                        )

                    fig.add_trace(
                        go.Scatter(
                            x=topic_messages["timestamp"],
                            y=[y_pos] * len(topic_messages),
                            mode='markers',
                            name=topic,  # Original Topic-Name statt Friendly Name
                            text=hover_texts,
                            hovertemplate="%{text}<extra></extra>",
                            marker={"size": 8, "opacity": 0.7},
                            customdata=topic_messages[["topic", "payload", "timestamp"]].values,  # Für Click-Events
                        )
                    )
                except Exception as e:
                    logger.error(f"Fehler beim Erstellen von Trace für Topic {topic}: {e}")
                    continue

            # Layout anpassen
            fig.update_layout(
                title="Timeline-Visualisierung: Zeit vs Topics",
                xaxis_title="Zeit",
                yaxis_title="Topics",
                height=600,
                showlegend=True,
                hovermode='closest',
            )

            # Y-Achse anpassen - Original Topic-Namen
            try:
                fig.update_yaxes(
                    tickmode='array',
                    tickvals=list(range(len(unique_topics))),
                    ticktext=list(unique_topics),  # Original Topic-Namen
                    showgrid=True,
                )
            except Exception as e:
                logger.error(f"Fehler beim Anpassen der Y-Achse: {e}")

            logger.debug("Timeline-Visualisierung erfolgreich erstellt")
            return fig

        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Timeline-Visualisierung: {e}", exc_info=True)
            st.error(f"Fehler beim Erstellen der Timeline: {e}")
            return go.Figure()

    def _create_scatter_plot(self, data: List[Dict], topics: List[str]) -> go.Figure:
        """Erstellt Scatter-Plot für Timeline"""
        # Diese Methode kann für erweiterte Visualisierungen verwendet werden
        pass

    def _get_topic_colors(self, topics: List[str]) -> Dict[str, str]:
        """Gibt Farben für Topics zurück"""
        # Diese Methode kann für farbige Visualisierungen verwendet werden
        pass

    def _format_hover_template(self, topics: List[str]) -> str:
        """Formatiert Hover-Template für Topics"""
        # Diese Methode kann für erweiterte Hover-Informationen verwendet werden
        pass
