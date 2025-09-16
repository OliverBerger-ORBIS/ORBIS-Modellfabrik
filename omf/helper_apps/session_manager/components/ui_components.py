"""
UI Components - Streamlit UI components for session analysis
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

from omf.helper_apps.session_manager.components.session_analyzer import SessionAnalyzer
from omf.helper_apps.session_manager.components.topic_manager import TopicFilterManager
from omf.dashboard.utils.ui_refresh import request_refresh
from omf.tools.logging_config import get_logger

logger = get_logger("session_manager.ui_components")


class SessionAnalysisUI:
    """UI Components for session analysis"""

    def __init__(self):
        self.topic_filter_manager = TopicFilterManager()

    def render_session_selection(self, session_directory: str = None) -> str:
        """Renders session selection UI and returns selected session path"""
        logger.debug("Session-Auswahl UI wird gerendert")
        st.subheader("📁 Session-Auswahl")

        # Session-Dateien aus konfiguriertem Verzeichnis laden
        if session_directory is None:
            from omf.helper_apps.session_manager.components.settings_manager import SettingsManager

            settings_manager = SettingsManager()
            session_directory = settings_manager.get_session_directory()

        logger.debug(f"Verwende Session-Verzeichnis: {session_directory}")
        # Absoluten Pfad verwenden, relativ zum Projekt-Root
        if not Path(session_directory).is_absolute():
            project_root = Path(__file__).parent.parent.parent.parent.parent
            sessions_dir = project_root / session_directory
        else:
            sessions_dir = Path(session_directory)

        if sessions_dir.exists():
            session_files = list(sessions_dir.glob("*.log"))
            session_options = ["demo"] + [str(f) for f in session_files]
            logger.debug(f"Gefundene Session-Dateien: {len(session_files)}")
        else:
            session_options = ["demo"]
            st.warning(f"❌ Sessions-Verzeichnis nicht gefunden: {sessions_dir}")
            logger.warning(f"Sessions-Verzeichnis nicht gefunden: {sessions_dir}")

        # Session-Auswahl
        selected_session = st.selectbox(
            "Session auswählen:", options=session_options, help="Wählen Sie eine Session für die Analyse aus"
        )

        # Regex-Filter für Session-Namen
        col1, col2 = st.columns([3, 1])
        with col1:
            regex_filter = st.text_input(
                "Filter Session-Namen (Regex):", value="", help="z.B. 'production_order' für alle ProductionOrderssessions"
            )

        with col2:
            if st.button("🔄 Filter zurücksetzen"):
                st.session_state.session_regex_filter = ""
                # st.rerun() entfernt - wird automatisch durch Streamlit gehandhabt

        # Filter anwenden
        if regex_filter:
            try:
                pattern = re.compile(regex_filter, re.IGNORECASE)
                filtered_sessions = [s for s in session_options if pattern.search(s)]
                if filtered_sessions:
                    selected_session = st.selectbox(
                        "Gefilterte Sessions:",
                        options=filtered_sessions,
                        help=f"Sessions gefiltert nach: {regex_filter}",
                    )
                else:
                    st.warning(f"Keine Sessions gefunden für Filter: {regex_filter}")
                    selected_session = session_options[0]
            except re.error:
                st.error(f"Ungültiger Regex-Pattern: {regex_filter}")
                selected_session = session_options[0]

        # Session laden Button
        if st.button("📊 Session laden", type="primary"):
            return selected_session

        return None

    def render_topic_filters(self, analyzer: SessionAnalyzer) -> Tuple[str, List[str]]:
        """Renders topic filtering UI and returns filter mode and selected topics"""
        st.subheader("🔍 Topic-Filter")

        # Vorfilter-Info
        show_all_topics = getattr(st.session_state, 'show_all_topics', False)
        all_topics = analyzer.get_available_topics(exclude_prefilter=not show_all_topics)

        # Vorfilter-UI in einklappbarer Box
        with st.expander("🔧 Vorfilter-Einstellungen", expanded=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info("Vorfilter entfernt uninteressante Topics (z.B. Kamera-Daten)")
                if st.checkbox("Alle Topics anzeigen (Vorfilter deaktivieren)", value=show_all_topics):
                    st.session_state.show_all_topics = True
                    # st.rerun() entfernt - wird automatisch durch Streamlit gehandhabt
                else:
                    st.session_state.show_all_topics = False
                    # st.rerun() entfernt - wird automatisch durch Streamlit gehandhabt

            with col2:
                if st.button("🔄 Vorfilter zurücksetzen"):
                    st.session_state.show_all_topics = False
                    # st.rerun() entfernt - wird automatisch durch Streamlit gehandhabt

            # Vorfilter-Statistiken
            prefilter_topics = analyzer._get_prefilter_topics()

            # Message-Counts für gefilterte Topics berechnen
            filtered_message_counts = {}
            if analyzer.session_data:
                for msg in analyzer.session_data["messages"]:
                    topic = msg["topic"]
                    if topic in prefilter_topics:
                        filtered_message_counts[topic] = filtered_message_counts.get(topic, 0) + 1

            # Gesamtanzahl ausgefilterte Messages
            total_filtered_messages = sum(filtered_message_counts.values())

            # Topics die tatsächlich in der Session vorhanden sind UND gefiltert werden
            filtered_topics_in_session = list(filtered_message_counts.keys())
            filtered_count = len(filtered_topics_in_session)

            # Debug: Zeige alle Topics in Session vs. Vorfilter
            if analyzer.session_data:
                all_session_topics = {msg["topic"] for msg in analyzer.session_data["messages"]}
                actually_filtered_topics = all_session_topics.intersection(set(prefilter_topics))
                logger.debug(
                    f"Debug Vorfilter: {len(prefilter_topics)} konfiguriert, "
                    f"{len(all_session_topics)} in Session, "
                    f"{len(actually_filtered_topics)} tatsächlich gefiltert"
                )

                # Metriken anzeigen
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Ausgefilterte Topics", f"{filtered_count} Topics")
                with col2:
                    st.metric("Ausgefilterte Messages", f"{total_filtered_messages} Messages")

                # Vorfilter-Topics in Session State speichern
                st.session_state.prefilter_topics = filtered_topics_in_session

                # Detaillierte Vorfilter-Statistik
                if filtered_count > 0:
                    st.success(
                        f"✅ {filtered_count} Topics werden vom Vorfilter ausgefiltert "
                        f"({total_filtered_messages} Messages)"
                    )

                    # Gefilterte Topics mit Message-Counts anzeigen
                    with st.expander(f"🔍 Gefilterte Topics Details ({filtered_count} Topics)", expanded=False):
                        # Nach Message-Count sortieren
                        sorted_topics = sorted(filtered_message_counts.items(), key=lambda x: x[1], reverse=True)

                        for topic, count in sorted_topics:
                            friendly_name = analyzer.topic_manager.get_friendly_name(topic)
                            if friendly_name != topic:
                                st.write(f"• `{topic}` → {friendly_name} ({count} Messages)")
                            else:
                                st.write(f"• `{topic}` ({count} Messages)")

                        # Copy-Button für Topics
                        if st.button("📋 Gefilterte Topics kopieren"):
                            topics_text = "\n".join([f"{topic} ({count} Messages)" for topic, count in sorted_topics])
                            st.code(topics_text, language="text")
                            st.success("Gefilterte Topics in Zwischenablage kopiert!")
                else:
                    # Zeige alle konfigurierten Vorfilter-Topics (auch wenn nicht in Session)
                    if prefilter_topics:
                        st.info(
                            f"ℹ️ {len(prefilter_topics)} Vorfilter-Topics konfiguriert, "
                            f"aber nicht in dieser Session vorhanden"
                        )

                        with st.expander(
                            f"⚙️ Konfigurierte Vorfilter-Topics ({len(prefilter_topics)} Topics)", expanded=False
                        ):
                            st.write("**In Settings konfiguriert, aber nicht in dieser Session vorhanden:**")
                            for topic in sorted(prefilter_topics):
                                friendly_name = analyzer.topic_manager.get_friendly_name(topic)
                                if friendly_name != topic:
                                    st.write(f"• `{topic}` → {friendly_name}")
                                else:
                                    st.write(f"• `{topic}`")
                    else:
                        st.info("ℹ️ Keine Vorfilter-Topics konfiguriert")

                # Zusätzliche Debug-Informationen
                if analyzer.session_data and prefilter_topics:
                    all_session_topics = {msg["topic"] for msg in analyzer.session_data["messages"]}
                    configured_but_not_in_session = set(prefilter_topics) - all_session_topics
                    if configured_but_not_in_session:
                        st.info(
                            f"🔍 **Debug:** {len(configured_but_not_in_session)} "
                            f"konfigurierte Vorfilter-Topics sind nicht in dieser Session vorhanden"
                        )

                # Link zu Settings
                st.markdown(
                    "💡 **Tipp:** Vorfilter-Topics können in den "
                    "[⚙️ Einstellungen](?tab=⚙️+Einstellungen) konfiguriert werden"
                )

        # Eigentliche Analyse - Nach Vorfilter
        st.markdown("---")
        st.markdown("**📊 Eigentliche Analyse**")

        # Berechne verbleibende Messages nach Vorfilter
        if analyzer.session_data:
            total_messages = len(analyzer.session_data["messages"])
            remaining_messages = total_messages - total_filtered_messages

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gesamt Messages", f"{total_messages:,}")
            with col2:
                st.metric("Ausgefiltert", f"{total_filtered_messages:,}")
            with col3:
                st.metric("Verbleibend", f"{remaining_messages:,}")

            if remaining_messages > 0:
                st.success(f"✅ {remaining_messages:,} Messages stehen für die nachfolgende Analyse zur Verfügung")
            else:
                st.warning("⚠️ Alle Messages wurden vom Vorfilter ausgefiltert!")

        st.markdown("---")

        # Filter-Modus
        filter_modes = ["📂 Nach Kategorie", "🏷️ Nach Sub-Kategorie", "🏷️ Nach Friendly Name", "📝 Nach Topic Name"]

        col1, col2 = st.columns([3, 1])
        with col1:
            filter_mode = st.radio(
                "Filter-Modus:", options=filter_modes, horizontal=True, help="Wählen Sie die Art der Topic-Filterung"
            )

        with col2:
            if st.button("🔄 Topic-Filter zurücksetzen"):
                st.session_state.topic_filter_reset = True
                # st.rerun() entfernt - wird automatisch durch Streamlit gehandhabt

        # Filter-Reset prüfen
        if getattr(st.session_state, 'topic_filter_reset', False):
            st.session_state.topic_filter_reset = False
            # Setze alle Topics als ausgewählt für die Filter-Modi
            categories = self.topic_filter_manager.get_topic_categories(all_topics)
            st.session_state.selected_categories = list(categories.keys())
            st.session_state.selected_subcategories = []
            st.session_state.selected_friendly_topics = []
            st.session_state.selected_topic_names = all_topics
            selected_topics = all_topics  # Alle Topics anzeigen
        else:
            selected_topics = []

        # Filter-spezifische UI
        if filter_mode == "📂 Nach Kategorie":
            selected_topics = self._render_category_filter(all_topics)
        elif filter_mode == "🏷️ Nach Sub-Kategorie":
            selected_topics = self._render_subcategory_filter(all_topics)
        elif filter_mode == "🏷️ Nach Friendly Name":
            selected_topics = self._render_friendly_name_filter(all_topics)
        else:  # Nach Topic Name
            selected_topics = self._render_topic_name_filter(all_topics)

        return filter_mode, selected_topics

    def _render_category_filter(self, all_topics: List[str]) -> List[str]:
        """Renders category-based filtering UI"""
        categories = self.topic_filter_manager.get_topic_categories(all_topics)

        col1, col2 = st.columns([1, 2])

        with col1:
            # Kategorie-Info
            st.info("**Verfügbare Kategorien:**")
            for category, topics in categories.items():
                st.text(f"• {category}: {len(topics)} Topics")

        with col2:
            # Kategorie-Auswahl mit Session State
            default_categories = getattr(st.session_state, 'selected_categories', list(categories.keys())[:2])
            selected_categories = st.multiselect(
                "Kategorien auswählen:",
                options=list(categories.keys()),
                default=default_categories,
                help="Wählen Sie Kategorien für die Timeline-Visualisierung aus. "
                "Mit 'X' können Sie Kategorien entfernen.",
            )

            # Session State aktualisieren
            st.session_state.selected_categories = selected_categories

            # Topics basierend auf ausgewählten Kategorien
            selected_topics = self.topic_filter_manager.filter_topics_by_category(all_topics, selected_categories)

        return selected_topics

    def _render_subcategory_filter(self, all_topics: List[str]) -> List[str]:
        """Renders subcategory-based filtering UI"""
        subcategories = self.topic_filter_manager.get_topic_subcategories(all_topics)

        col1, col2 = st.columns([1, 2])

        with col1:
            # Sub-Kategorie-Info
            st.info("**Verfügbare Sub-Kategorien:**")
            for category, subcats in subcategories.items():
                st.text(f"**{category}:**")
                for subcat, _topics in subcats.items():
                    st.text(f"  • {subcat}: {len(_topics)} Topics")

        with col2:
            # Alle Sub-Kategorien als Liste
            all_subcategories = []
            for category, subcats in subcategories.items():
                for subcat, _topics in subcats.items():
                    all_subcategories.append(f"{category} → {subcat}")

            # Sub-Kategorie-Auswahl mit Session State
            default_subcategories = getattr(st.session_state, 'selected_subcategories', all_subcategories[:3])
            selected_subcategories = st.multiselect(
                "Sub-Kategorien auswählen:",
                options=all_subcategories,
                default=default_subcategories,
                help="Wählen Sie Sub-Kategorien für die Timeline-Visualisierung aus. "
                "Mit 'X' können Sie Sub-Kategorien entfernen.",
            )

            # Session State aktualisieren
            st.session_state.selected_subcategories = selected_subcategories

            # Topics basierend auf ausgewählten Sub-Kategorien
            selected_topics = self.topic_filter_manager.filter_topics_by_subcategory(all_topics, selected_subcategories)

        return selected_topics

    def _render_friendly_name_filter(self, all_topics: List[str]) -> List[str]:
        """Renders friendly name-based filtering UI"""
        col1, col2 = st.columns([1, 2])

        with col1:
            # Friendly Name Suche
            search_term = st.text_input(
                "Friendly Name suchen:", value="", help="Suchen Sie nach Topics über deren Friendly Names"
            )

            # Filter anwenden
            if search_term:
                filtered_topics = self.topic_filter_manager.filter_topics_by_friendly_name(all_topics, search_term)
            else:
                filtered_topics = all_topics

        with col2:
            # Topic-Auswahl mit Friendly Names
            friendly_names = self.topic_filter_manager.get_friendly_names(filtered_topics)

            # Friendly Name Filter mit Session State
            default_friendly_topics = getattr(st.session_state, 'selected_friendly_topics', filtered_topics[:5])
            selected_topics = st.multiselect(
                "Topics auswählen:",
                options=filtered_topics,
                default=default_friendly_topics,
                format_func=lambda x: f"{x} ({friendly_names[x]})",
                help="Wählen Sie Topics für die Timeline-Visualisierung aus. Mit 'X' können Sie Topics entfernen.",
            )

            # Session State aktualisieren
            st.session_state.selected_friendly_topics = selected_topics

        return selected_topics

    def _render_topic_name_filter(self, all_topics: List[str]) -> List[str]:
        """Renders topic name-based filtering UI"""
        col1, col2 = st.columns([1, 2])

        with col1:
            # Topic Name Suche
            search_term = st.text_input("Topic Name suchen:", value="", help="Suchen Sie nach Topics über deren Namen")

            # Filter anwenden
            if search_term:
                filtered_topics = self.topic_filter_manager.filter_topics_by_name(all_topics, search_term)
            else:
                filtered_topics = all_topics

        with col2:
            # Topic-Auswahl
            # Topic Name Filter mit Session State
            default_topic_names = getattr(st.session_state, 'selected_topic_names', filtered_topics[:5])
            selected_topics = st.multiselect(
                "Topics auswählen:",
                options=filtered_topics,
                default=default_topic_names,
                help="Wählen Sie Topics für die Timeline-Visualisierung aus. Mit 'X' können Sie Topics entfernen.",
            )

            # Session State aktualisieren
            st.session_state.selected_topic_names = selected_topics

        return selected_topics

    def render_timeline_controls(self, messages: List[Dict]) -> Tuple[datetime, datetime]:
        """Renders timeline controls and returns time range"""
        st.subheader("⏱️ Zeitfilter")

        if not messages:
            return None, None

        # Zeitbereich berechnen
        timestamps = [msg["timestamp"] for msg in messages]
        min_time = min(timestamps)
        max_time = max(timestamps)

        col1, col2 = st.columns([3, 1])

        with col1:
            # Konvertiere zu Unix-Timestamps für Berechnung
            min_timestamp = min_time.timestamp()
            max_timestamp = max_time.timestamp()

            # Berechne relative Sekunden (0 bis Ende)
            total_duration_seconds = max_timestamp - min_timestamp

            # Schiebe-Regler für Zeitbereich (mit relativen Sekunden)
            # Verwende gespeicherten Wert oder Standard
            default_value = st.session_state.get('time_range_seconds', (0.0, total_duration_seconds))

            time_range_seconds = st.slider(
                "Zeitbereich auswählen (Sekunden):",
                min_value=0.0,
                max_value=total_duration_seconds,
                value=default_value,
                step=1.0,  # 1 Sekunde Schritte
                format="%.1f s",  # Anzeige in Sekunden
                help="Wählen Sie den interessanten Zeitbereich für die Timeline aus (0 = Start, Ende = Session-Ende)",
            )

            # Speichere den aktuellen Wert im Session State
            st.session_state.time_range_seconds = time_range_seconds

            # Konvertiere relative Sekunden zurück zu absoluten Timestamps
            start_timestamp = min_timestamp + time_range_seconds[0]
            end_timestamp = min_timestamp + time_range_seconds[1]

            # Konvertiere zurück zu datetime-Objekten mit Timezone
            time_range = (
                pd.to_datetime(start_timestamp, unit='s', utc=True),
                pd.to_datetime(end_timestamp, unit='s', utc=True),
            )

            # Zeige gewählten Zeitbereich an
            st.info(
                f"📊 **Gewählter Zeitbereich:** "
                f"{time_range[0].strftime('%H:%M:%S')} - {time_range[1].strftime('%H:%M:%S')} "
                f"({time_range_seconds[0]:.1f}s - {time_range_seconds[1]:.1f}s)"
            )

        with col2:
            # Schnellauswahl-Buttons
            if st.button("⏰ Ganzer Zeitbereich"):
                st.session_state.time_range_reset = True
                st.session_state.time_range_seconds = (0.0, total_duration_seconds)
                request_refresh()

            if st.button("⏱️ Letzte 5 Min"):
                last_5_min = max(0.0, total_duration_seconds - 300.0)  # 5 Minuten = 300 Sekunden
                st.session_state.time_range_seconds = (last_5_min, total_duration_seconds)
                request_refresh()

            if st.button("⏱️ Erste 5 Min"):
                first_5_min = min(300.0, total_duration_seconds)  # 5 Minuten = 300 Sekunden
                st.session_state.time_range_seconds = (0.0, first_5_min)
                request_refresh()

            # Zeitfilter zurücksetzen
            if st.button("🔄 Zeitfilter zurücksetzen"):
                st.session_state.time_range_reset = True
                st.session_state.time_range_seconds = (0.0, total_duration_seconds)
                request_refresh()

        return time_range

    def render_payload_display(self, messages: List[Dict], selected_topics: List[str]):
        """Renders payload display UI"""
        if not messages or not selected_topics:
            return

        st.subheader("📄 Payload-Details")

        # Filtere Messages nach ausgewählten Topics
        topic_messages = {topic: [] for topic in selected_topics}
        for msg in messages:
            if msg["topic"] in selected_topics:
                topic_messages[msg["topic"]].append(msg)

        # Topic-Auswahl für Payload-Anzeige
        selected_topic = st.selectbox(
            "Topic für Payload-Anzeige:",
            options=selected_topics,
            help="Wählen Sie ein Topic aus, um dessen Payloads anzuzeigen",
        )

        if selected_topic and topic_messages[selected_topic]:
            # Zeige erste 5 Messages des ausgewählten Topics
            messages_to_show = topic_messages[selected_topic][:5]

            st.info(f"**Erste {len(messages_to_show)} Messages von {selected_topic}:**")

            for i, msg in enumerate(messages_to_show, 1):
                with st.expander(f"Message {i} - {msg['timestamp'].strftime('%H:%M:%S.%f')[:-3]}"):
                    try:
                        # Versuche JSON-Parsing
                        payload_data = json.loads(msg["payload"])
                        st.json(payload_data)
                    except (json.JSONDecodeError, TypeError):
                        # Fallback: Text anzeigen
                        st.text(msg["payload"])

    def render_statistics(self, analyzer: SessionAnalyzer, messages: List[Dict]):
        """Renders statistics UI"""
        st.subheader("📊 Statistiken")

        # Session-Statistiken
        stats = analyzer.get_message_statistics()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Gesamt Messages", stats.get("total_messages", 0))

        with col2:
            st.metric("Eindeutige Topics", stats.get("unique_topics", 0))

        with col3:
            duration = stats.get("duration_minutes", 0)
            st.metric("Dauer (Min)", f"{duration:.1f}")

        # Gefilterte Messages
        if messages:
            st.success(
                f"✅ **Gefilterte Messages:** {len(messages)} von "
                f"{stats.get('total_messages', 0)} "
                f"({len(messages)/stats.get('total_messages', 1)*100:.1f}%)"
            )

        # Zeitbereich
        if stats.get("start_time") and stats.get("end_time"):
            st.info(
                f"🕐 **Zeitbereich:** "
                f"{stats['start_time'].strftime('%H:%M:%S')} - "
                f"{stats['end_time'].strftime('%H:%M:%S')}"
            )
