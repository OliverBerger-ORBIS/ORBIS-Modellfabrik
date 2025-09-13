"""
Session Analysis - Main controller for session analysis functionality
Refactored version with separated components
"""

import logging

import streamlit as st

from src_orbis.helper_apps.session_manager.components.graph_visualizer import GraphVisualizer
from src_orbis.helper_apps.session_manager.components.session_analyzer import SessionAnalyzer
from src_orbis.helper_apps.session_manager.components.timeline_visualizer import TimelineVisualizer
from src_orbis.helper_apps.session_manager.components.ui_components import SessionAnalysisUI

logger = logging.getLogger(__name__)


def show_session_analysis():
    """Hauptfunktion für Session-Analyse (Refactored)"""

    # Session State initialisieren (nur einmal)
    if 'session_analyzer' not in st.session_state:
        logger.debug("Initialisiere Session State")
        st.session_state.session_analyzer = SessionAnalyzer()
        st.session_state.session_loaded = False
        st.session_state.current_session = None
        st.session_state.show_all_topics = False  # Vorfilter aktiv
        st.session_state.topic_filter_reset = False  # Filter-Reset
        st.session_state.time_range_reset = False  # Zeitfilter-Reset
        st.session_state.selected_categories = []  # Ausgewählte Kategorien
        st.session_state.selected_subcategories = []  # Ausgewählte Sub-Kategorien
        st.session_state.selected_friendly_topics = []  # Ausgewählte Friendly Topics
        st.session_state.selected_topic_names = []  # Ausgewählte Topic Names
        st.session_state.prefilter_topics = []  # Gefilterte Topics für Anzeige
    else:
        logger.debug(
            f"Session State: loaded={st.session_state.session_loaded}, current={st.session_state.current_session}"
        )

    # Komponenten initialisieren
    analyzer = st.session_state.session_analyzer
    visualizer = TimelineVisualizer()
    ui = SessionAnalysisUI()
    graph_visualizer = GraphVisualizer()

    # Session-Auswahl
    selected_session = ui.render_session_selection()

    if selected_session:
        # Session laden
        if analyzer.load_session_data(selected_session):
            st.session_state.session_loaded = True
            st.session_state.current_session = selected_session
            st.success(f"✅ Session erfolgreich geladen: {selected_session}")
        else:
            st.error("❌ Fehler beim Laden der Session")
            return

    # Session-Analyse anzeigen
    if st.session_state.session_loaded:
        # Topic-Filter
        filter_mode, selected_topics = ui.render_topic_filters(analyzer)

        # Timeline-Visualisierung mit Zeitfilter
        if selected_topics:
            logger.debug(f"Erstelle Timeline mit ausgewählten Topics: {selected_topics}")
            st.subheader("⏱️ Timeline-Visualisierung")

            # Zeitfilter
            messages = analyzer.session_data["messages"]
            time_range = ui.render_timeline_controls(messages)

            # Messages nach Zeitbereich filtern
            filtered_messages = messages
            if time_range and time_range[0] and time_range[1]:
                # Konvertiere String-Timestamps zu pandas Timestamps für Vergleich
                import pandas as pd

                filtered_messages = []
                for msg in messages:
                    try:
                        # Konvertiere String-Timestamp zu pandas Timestamp
                        msg_timestamp = pd.to_datetime(msg["timestamp"])

                        # Stelle sicher, dass beide Timestamps den gleichen Timezone-Status haben
                        if msg_timestamp.tz is None and time_range[0].tz is not None:
                            # msg_timestamp ist timezone-naive, time_range ist timezone-aware
                            msg_timestamp = msg_timestamp.tz_localize('UTC')
                        elif msg_timestamp.tz is not None and time_range[0].tz is None:
                            # msg_timestamp ist timezone-aware, time_range ist timezone-naive
                            msg_timestamp = msg_timestamp.tz_localize(None)

                        if time_range[0] <= msg_timestamp <= time_range[1]:
                            filtered_messages.append(msg)
                    except Exception as e:
                        logger.warning(f"Fehler beim Parsen von Timestamp: {msg['timestamp']} - {e}")
                        # Bei Fehlern: Message trotzdem hinzufügen
                        filtered_messages.append(msg)
                logger.debug(f"Zeitfilter: {len(filtered_messages)} von {len(messages)} Messages")

            # Timeline erstellen
            try:
                fig = visualizer.create_timeline_visualization(filtered_messages, selected_topics)
                if fig.data:  # Prüfe ob Figure Daten hat
                    logger.debug("Timeline-Plot erfolgreich erstellt, zeige Chart")
                    st.plotly_chart(fig, use_container_width=True)
                    logger.debug("Timeline-Chart erfolgreich angezeigt")
                else:
                    st.warning("Keine Daten für Timeline verfügbar")
            except Exception as e:
                logger.error(f"Fehler beim Erstellen der Timeline: {e}")
                st.error(f"Fehler beim Erstellen der Timeline: {e}")

            # Payload-Details
            ui.render_payload_display(filtered_messages, selected_topics)

            # Statistiken
            ui.render_statistics(analyzer, filtered_messages)

            # Graph-Visualisierung
            st.markdown("---")
            graph_visualizer.render_graph_analysis(analyzer.session_data)
        else:
            st.warning("Bitte wählen Sie Topics für die Visualisierung aus")
    else:
        st.info("Bitte laden Sie zuerst eine Session")
