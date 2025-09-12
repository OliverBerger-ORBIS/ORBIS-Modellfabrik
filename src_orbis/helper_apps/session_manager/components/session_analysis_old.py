"""
Session Analyse Komponente
Analyse einer ausgewählten Session mit Timeline-Visualisierung und Topic-Filterung
"""

import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src_orbis.omf.tools.topic_manager import OmfTopicManager

# Logging konfigurieren
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('data/logs/session_manager.log'), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class SessionAnalyzer:
    """Session Analyse mit OMF Topic-Config Integration"""

    def __init__(self):
        self.topic_manager = OmfTopicManager()
        self.session_data = None
        self.messages_df = None

    def load_session_data(self, session_file_path: str) -> bool:
        """Lädt Session-Daten aus einer Log-Datei"""
        try:
            logger.debug(f"Lade Session-Daten: {session_file_path}")
            # Lade Session-Daten (vereinfacht für Demo)
            # In der echten Implementierung würde hier die Session-Datenbank abgefragt
            self.session_data = self._parse_session_file(session_file_path)
            logger.debug(f"Session-Daten erfolgreich geladen: {len(self.session_data['messages'])} Messages")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Laden der Session-Daten: {e}", exc_info=True)
            st.error(f"Fehler beim Laden der Session-Daten: {e}")
            return False

    def _parse_session_file(self, file_path: str) -> Dict:
        """Parst eine Session-Log-Datei (JSON-Format)"""
        logger.debug(f"Parse Session-Datei: {file_path}")

        if file_path == "demo":
            # Mock-Daten für Demo
            return {
                "session_id": "demo_session",
                "start_time": datetime(2024, 1, 15, 10, 30, 0),
                "end_time": datetime(2024, 1, 15, 11, 45, 0),
                "messages": self._generate_mock_messages(),
            }

        # Echte Session-Datei parsen
        try:
            session_path = Path(file_path)
            if not session_path.exists():
                logger.error(f"Session-Datei nicht gefunden: {file_path}")
                return self._generate_mock_messages()

            messages = []
            start_time = None
            end_time = None

            with open(session_path, encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        line = line.strip()
                        if not line:
                            continue

                        # Versuche JSON-Format zu parsen
                        try:
                            # Parse JSON-Format: {"timestamp": "...", "topic": "...", "payload": "..."}
                            data = json.loads(line)

                            if "timestamp" in data and "topic" in data and "payload" in data:
                                # Parse Timestamp
                                timestamp_str = data["timestamp"]
                                if timestamp_str.endswith('Z'):
                                    timestamp_str = timestamp_str[:-1] + '+00:00'
                                elif '+' not in timestamp_str and 'Z' not in timestamp_str:
                                    timestamp_str += '+00:00'

                                timestamp = datetime.fromisoformat(timestamp_str)

                                messages.append(
                                    {
                                        "timestamp": timestamp,
                                        "topic": data["topic"],
                                        "payload": data["payload"],
                                        "qos": data.get("qos", 0),
                                    }
                                )

                                if start_time is None:
                                    start_time = timestamp
                                end_time = timestamp

                        except json.JSONDecodeError:
                            # Fallback: Versuche altes Format [timestamp] topic: payload
                            if ']' in line and ':' in line:
                                timestamp_str = line.split(']')[0][1:]  # Entferne [ und ]
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

                                topic_payload = line.split(']')[1].strip()
                                if ':' in topic_payload:
                                    topic, payload = topic_payload.split(':', 1)
                                    topic = topic.strip()
                                    payload = payload.strip()

                                    messages.append(
                                        {"timestamp": timestamp, "topic": topic, "payload": payload, "qos": 0}
                                    )

                                    if start_time is None:
                                        start_time = timestamp
                                    end_time = timestamp

                    except Exception as e:
                        logger.warning(f"Fehler beim Parsen von Zeile {line_num}: {e}")
                        continue

            if not messages:
                logger.warning("Keine gültigen Messages gefunden, verwende Mock-Daten")
                return self._generate_mock_messages()

            logger.debug(f"Session geparst: {len(messages)} Messages, {start_time} bis {end_time}")

            return {
                "session_id": session_path.stem,
                "start_time": start_time,
                "end_time": end_time,
                "messages": sorted(messages, key=lambda x: x["timestamp"]),
            }

        except Exception as e:
            logger.error(f"Fehler beim Parsen der Session-Datei: {e}")
            return self._generate_mock_messages()

    def _generate_mock_messages(self) -> List[Dict]:
        """Generiert Mock-Messages für Demo"""
        import random

        topics = [
            "ccu/state/status",
            "ccu/state/flow",
            "module/v1/ff/SVR3QA0022/state",
            "module/v1/ff/SVR3QA0022/order",
            "module/v1/ff/SVR4H76449/state",
            "fts/v1/ff/5iO4/state",
            "fts/v1/ff/5iO4/order",
            "/j1/txt/1/f/i/stock",
            "/j1/txt/1/f/o/order",
        ]

        messages = []
        start_time = datetime(2024, 1, 15, 10, 30, 0)

        for i in range(200):
            timestamp = start_time + timedelta(seconds=i * 2 + random.randint(0, 5))
            topic = random.choice(topics)
            payload = f"{{'value': {random.randint(0, 100)}, 'timestamp': '{timestamp.isoformat()}'}}"

            messages.append(
                {"timestamp": timestamp, "topic": topic, "payload": payload, "qos": random.choice([0, 1, 2])}
            )

        return sorted(messages, key=lambda x: x["timestamp"])

    def get_available_topics(self, exclude_prefilter: bool = True) -> List[str]:
        """Gibt alle verfügbaren Topics aus der Session zurück"""
        if not self.session_data:
            return []

        topics = set()
        for message in self.session_data["messages"]:
            topics.add(message["topic"])

        # Vorfilter anwenden
        if exclude_prefilter:
            prefilter_topics = self._get_prefilter_topics()
            topics = topics - set(prefilter_topics)

        return sorted(topics)

    def _get_prefilter_topics(self) -> List[str]:
        """Gibt die Vorfilter-Topics zurück (uninteressante Topics)"""
        return [
            "/j1/txt/1/i/cam",  # Kamera-Daten
            "/j1/txt/1/i/bme",  # BME680-Sensor-Daten
            # Weitere uninteressante Topics können hier hinzugefügt werden
        ]

    def get_topic_categories(self) -> Dict[str, List[str]]:
        """Gruppiert Topics nach Kategorien basierend auf OMF Config"""
        topics = self.get_available_topics()
        logger.debug(f"Verfügbare Topics: {topics}")
        categories = {}

        for topic in topics:
            try:
                topic_info = self.topic_manager.get_topic_info(topic)
                category = topic_info.get("category", "Unknown")
                logger.debug(f"Topic {topic} -> Kategorie: {category}")

                if category not in categories:
                    categories[category] = []
                categories[category].append(topic)
            except Exception as e:
                logger.error(f"Fehler beim Verarbeiten von Topic {topic}: {e}")
                category = "Unknown"
                if category not in categories:
                    categories[category] = []
                categories[category].append(topic)

        logger.debug(f"Topic-Kategorien: {categories}")
        return categories

    def get_topic_subcategories(self) -> Dict[str, Dict[str, List[str]]]:
        """Gruppiert Topics nach Kategorien und Sub-Kategorien basierend auf OMF Config"""
        topics = self.get_available_topics()
        logger.debug(f"Verfügbare Topics für Sub-Kategorien: {topics}")

        subcategories = {}

        for topic in topics:
            try:
                topic_info = self.topic_manager.get_topic_info(topic)
                category = topic_info.get("category", "Unknown")
                sub_category = topic_info.get("sub_category", "Sonstige")

                logger.debug(f"Topic {topic} -> Kategorie: {category}, Sub-Kategorie: {sub_category}")

                if category not in subcategories:
                    subcategories[category] = {}
                if sub_category not in subcategories[category]:
                    subcategories[category][sub_category] = []
                subcategories[category][sub_category].append(topic)
            except Exception as e:
                logger.error(f"Fehler beim Sub-Kategorisieren von Topic {topic}: {e}")
                # Fallback: Kategorie und Sub-Kategorie aus Topic-Name ableiten
                if topic.startswith("ccu/"):
                    category = "CCU"
                    if "state" in topic:
                        sub_category = "State"
                    elif "control" in topic or "set" in topic:
                        sub_category = "Control"
                    elif "order" in topic:
                        sub_category = "Order"
                    elif "status" in topic or "pairing" in topic:
                        sub_category = "Status"
                    else:
                        sub_category = "Sonstige"
                elif topic.startswith("module/"):
                    category = "MODULE"
                    if "connection" in topic:
                        sub_category = "Connection"
                    elif "factsheet" in topic:
                        sub_category = "Factsheet"
                    elif "instantAction" in topic:
                        sub_category = "InstantAction"
                    elif "order" in topic:
                        sub_category = "Order"
                    elif "state" in topic:
                        sub_category = "State"
                    else:
                        sub_category = "Sonstige"
                elif topic.startswith("/j1/txt/"):
                    category = "TXT"
                    if "/f/i/" in topic:
                        sub_category = "Function Input"
                    elif "/f/o/" in topic:
                        sub_category = "Function Output"
                    elif "/i/" in topic:
                        sub_category = "Input"
                    elif "/o/" in topic:
                        sub_category = "Output"
                    elif "/c/" in topic:
                        sub_category = "Control"
                    else:
                        sub_category = "General"
                elif topic.startswith("fts/"):
                    category = "FTS"
                    if "connection" in topic:
                        sub_category = "Connection"
                    elif "factsheet" in topic:
                        sub_category = "Factsheet"
                    elif "instantAction" in topic:
                        sub_category = "InstantAction"
                    elif "order" in topic:
                        sub_category = "Order"
                    elif "state" in topic:
                        sub_category = "State"
                    else:
                        sub_category = "Sonstige"
                else:
                    category = "Unknown"
                    sub_category = "Sonstige"

                if category not in subcategories:
                    subcategories[category] = {}
                if sub_category not in subcategories[category]:
                    subcategories[category][sub_category] = []
                subcategories[category][sub_category].append(topic)

        logger.debug(f"Topic-Sub-Kategorien: {subcategories}")
        return subcategories

    def create_timeline_visualization(
        self, selected_topics: List[str] = None, filtered_messages: List[Dict] = None
    ) -> go.Figure:
        """Erstellt Timeline-Visualisierung (Zeit vs Topic-Name)"""
        try:
            logger.debug(f"Erstelle Timeline-Visualisierung mit Topics: {selected_topics}")

            if not self.session_data:
                logger.warning("Keine Session-Daten verfügbar für Timeline")
                return go.Figure()

            # Verwende gefilterte Messages oder alle Messages
            if filtered_messages is not None:
                messages = filtered_messages
                logger.debug(f"Verwende gefilterte Messages: {len(messages)}")
            else:
                messages = self.session_data["messages"]
                logger.debug(f"Anzahl Messages vor Filterung: {len(messages)}")

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
                            marker={'size': 8, 'opacity': 0.7},
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

    def get_message_statistics(self) -> Dict:
        """Gibt Message-Statistiken zurück"""
        if not self.session_data:
            return {}

        messages = self.session_data["messages"]

        # Gruppiere nach Topics
        topic_counts = {}
        for message in messages:
            topic = message["topic"]
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        return {
            "total_messages": len(messages),
            "unique_topics": len(topic_counts),
            "topic_counts": topic_counts,
            "duration_minutes": (self.session_data["end_time"] - self.session_data["start_time"]).total_seconds() / 60,
        }


def show_session_analysis():
    """Session Analyse Tab mit Timeline-Visualisierung und Topic-Filterung"""

    st.header("📊 Session Analyse")
    st.markdown("Analyse einer ausgewählten Session mit Timeline-Visualisierung")

    # Session State initialisieren
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
    else:
        logger.debug(
            f"Session State: loaded={st.session_state.session_loaded}, current={st.session_state.current_session}"
        )

    analyzer = st.session_state.session_analyzer

    # Session-Auswahl aus mqtt-data Verzeichnis mit Regex-Filter
    st.subheader("📁 Session-Auswahl")

    # Regex-Filter für Session-Namen
    col1, col2 = st.columns([3, 1])

    with col1:
        # Regex-Filter Eingabe
        regex_filter = st.text_input(
            "🔍 Session-Filter (Regex):",
            placeholder="z.B. auftrag, aps, ccu...",
            help="Filtere Sessions nach Dateinamen mit Regex-Pattern",
        )

    with col2:
        # Filter zurücksetzen Button
        if st.button("🔄 Filter zurücksetzen"):
            st.rerun()

    # Verfügbare Sessions aus mqtt-data/sessions/ laden
    sessions_dir = Path("mqtt-data/sessions")
    all_sessions = []

    if sessions_dir.exists():
        for file_path in sessions_dir.glob("*.log"):
            all_sessions.append(file_path.stem)

    # Demo-Session hinzufügen
    all_sessions.insert(0, "demo")

    if not all_sessions:
        all_sessions = ["demo"]

    # Regex-Filter anwenden
    if regex_filter:
        try:
            pattern = re.compile(regex_filter, re.IGNORECASE)
            filtered_sessions = [session for session in all_sessions if pattern.search(session)]
        except re.error:
            st.error(f"Ungültiges Regex-Pattern: {regex_filter}")
            filtered_sessions = all_sessions
    else:
        filtered_sessions = all_sessions

    # Session-Auswahl
    if filtered_sessions:
        selected_session = st.selectbox(
            f"Verfügbare Sessions ({len(filtered_sessions)} von {len(all_sessions)}):",
            filtered_sessions,
            help="Wählen Sie eine Session zur Analyse aus",
        )
    else:
        st.warning("Keine Sessions gefunden, die dem Filter entsprechen.")
        selected_session = "demo"

    # Session laden Button
    if st.button("📊 Session laden", type="primary", use_container_width=True):
        with st.spinner("Lade Session-Daten..."):
            if selected_session == "demo":
                success = analyzer.load_session_data("demo")
            else:
                success = analyzer.load_session_data(f"mqtt-data/sessions/{selected_session}.log")

            if success:
                st.session_state.session_loaded = True
                st.session_state.current_session = selected_session
                st.success("Session erfolgreich geladen!")
                st.rerun()
            else:
                st.error("Fehler beim Laden der Session!")

    # Session-Daten anzeigen
    if st.session_state.session_loaded and analyzer.session_data:
        st.divider()

        # Session-Übersicht
        st.subheader("📈 Session-Übersicht")

        stats = analyzer.get_message_statistics()
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Nachrichten", stats["total_messages"])
        with col2:
            st.metric("Topics", stats["unique_topics"])
        with col3:
            st.metric("Dauer", f"{stats['duration_minutes']:.1f} min")
        with col4:
            st.metric("Session-ID", analyzer.session_data["session_id"])

        # Vorfilter-System
        st.subheader("🚫 Vorfilter (Uninteressante Topics)")

        # Vorfilter-Topics anzeigen und bearbeiten
        prefilter_topics = analyzer._get_prefilter_topics()

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            # Vorfilter-Topics anzeigen
            if prefilter_topics:
                st.markdown("**Aktuell ausgefilterte Topics:**")
                for topic in prefilter_topics:
                    friendly_name = analyzer.topic_manager.get_friendly_name(topic)
                    st.text(f"• {topic} ({friendly_name})")
            else:
                st.info("Keine Vorfilter-Topics definiert")

        with col2:
            # Vorfilter-Statistiken
            if analyzer.session_data and "messages" in analyzer.session_data:
                prefiltered_messages = 0
                for message in analyzer.session_data["messages"]:
                    if message["topic"] in prefilter_topics:
                        prefiltered_messages += 1

                st.metric(
                    "Ausgefilterte Messages",
                    f"{prefiltered_messages}",
                    help="Anzahl der Messages von ausgefilterten Topics",
                )

        with col3:
            # Vorfilter zurücksetzen Button
            if st.button("🔄 Vorfilter zurücksetzen", help="Zeige alle Topics an"):
                st.session_state.show_all_topics = True
                st.rerun()

        st.divider()

        # Erweiterte Topic-Filterung
        st.subheader("🔍 Topic-Filterung")

        # Filter-Reset Button
        col1, col2 = st.columns([3, 1])

        with col1:
            # Filter-Modus auswählen
            filter_mode = st.radio(
                "Filter-Modus:",
                ["📂 Nach Kategorie", "🏷️ Nach Sub-Kategorie", "🏷️ Nach Friendly Name", "📝 Nach Topic Name"],
                horizontal=True,
            )

        with col2:
            # Topic-Filter zurücksetzen Button
            if st.button("🔄 Topic-Filter zurücksetzen", help="Setze alle Topic-Filter zurück"):
                st.session_state.topic_filter_reset = True
                st.rerun()

        # Vorfilter berücksichtigen
        show_all_topics = getattr(st.session_state, 'show_all_topics', False)
        all_topics = analyzer.get_available_topics(exclude_prefilter=not show_all_topics)
        selected_topics = []

        # Filter-Reset prüfen
        if getattr(st.session_state, 'topic_filter_reset', False):
            st.session_state.topic_filter_reset = False
            # Setze alle Topics als ausgewählt für die Filter-Modi
            st.session_state.selected_categories = list(analyzer.get_topic_categories().keys())
            st.session_state.selected_subcategories = []
            st.session_state.selected_friendly_topics = []
            st.session_state.selected_topic_names = all_topics
            selected_topics = all_topics  # Alle Topics anzeigen

        if filter_mode == "📂 Nach Kategorie":
            # Kategorie-basierte Filterung
            categories = analyzer.get_topic_categories()

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("**Verfügbare Kategorien:**")
                for category, topics in categories.items():
                    with st.expander(f"{category} ({len(topics)} Topics)"):
                        for topic in topics:
                            friendly_name = analyzer.topic_manager.get_friendly_name(topic)
                            st.text(f"• {topic}")
                            st.caption(f"  {friendly_name}")

            with col2:
                # Kategorie-Auswahl mit Session State
                default_categories = getattr(st.session_state, 'selected_categories', list(categories.keys())[:2])
                selected_categories = st.multiselect(
                    "Kategorien auswählen:",
                    options=list(categories.keys()),
                    default=default_categories,
                    help="Wählen Sie Kategorien für die Timeline-Visualisierung aus. Mit 'X' können Sie Kategorien entfernen.",
                )

                # Session State aktualisieren
                st.session_state.selected_categories = selected_categories

                # Topics basierend auf ausgewählten Kategorien
                for category in selected_categories:
                    selected_topics.extend(categories[category])
                selected_topics = list(set(selected_topics))  # Duplikate entfernen

        elif filter_mode == "🏷️ Nach Sub-Kategorie":
            # Sub-Kategorie-basierte Filterung
            subcategories = analyzer.get_topic_subcategories()

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("**Verfügbare Sub-Kategorien:**")
                for category, subcats in subcategories.items():
                    with st.expander(f"**{category}**"):
                        for subcat, _topics in subcats.items():
                            with st.expander(f"{subcat} ({len(topics)} Topics)", expanded=False):
                                for topic in topics:
                                    friendly_name = analyzer.topic_manager.get_friendly_name(topic)
                                    st.text(f"• {topic}")
                                    st.caption(f"  {friendly_name}")

            with col2:
                # Sub-Kategorie-Auswahl
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
                    help="Wählen Sie Sub-Kategorien für die Timeline-Visualisierung aus. Mit 'X' können Sie Sub-Kategorien entfernen.",
                )

                # Session State aktualisieren
                st.session_state.selected_subcategories = selected_subcategories

                # Topics basierend auf ausgewählten Sub-Kategorien
                for subcat_str in selected_subcategories:
                    category, subcat = subcat_str.split(" → ", 1)
                    if category in subcategories and subcat in subcategories[category]:
                        selected_topics.extend(subcategories[category][subcat])
                selected_topics = list(set(selected_topics))  # Duplikate entfernen

        elif filter_mode == "🏷️ Nach Friendly Name":
            # Friendly Name Filterung
            friendly_names = {topic: analyzer.topic_manager.get_friendly_name(topic) for topic in all_topics}

            # Suchfeld für Friendly Names
            search_term = st.text_input(
                "Friendly Name suchen:", placeholder="z.B. CCU, MODULE, TXT...", help="Suchen Sie nach Friendly Names"
            )

            if search_term:
                filtered_topics = [
                    topic
                    for topic, friendly_name in friendly_names.items()
                    if search_term.lower() in friendly_name.lower()
                ]
            else:
                filtered_topics = all_topics

            # Topic-Auswahl mit Friendly Names
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

        else:  # Nach Topic Name
            # Topic Name Filterung
            search_term = st.text_input(
                "Topic Name suchen:", placeholder="z.B. ccu/state, module/v1/ff...", help="Suchen Sie nach Topic Names"
            )

            if search_term:
                filtered_topics = [topic for topic in all_topics if search_term.lower() in topic.lower()]
            else:
                filtered_topics = all_topics

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

        # Timeline-Visualisierung mit Zeitfilter
        if selected_topics:
            logger.debug(f"Erstelle Timeline mit ausgewählten Topics: {selected_topics}")
            st.subheader("⏱️ Timeline-Visualisierung")
            st.markdown("**Zeit vs Topic-Name** - Jeder Punkt repräsentiert eine MQTT-Nachricht")
            st.markdown("💡 **Tipp:** Klicken Sie auf einen Datenpunkt, um die Payload-Details anzuzeigen")

            # Zeitbereich-Filter
            if analyzer.session_data and "messages" in analyzer.session_data:
                messages = analyzer.session_data["messages"]
                if messages:
                    # Zeitbereich berechnen
                    timestamps = [msg["timestamp"] for msg in messages]
                    min_time = min(timestamps)
                    max_time = max(timestamps)

                    # Konvertiere zu Unix-Timestamps für Slider
                    min_timestamp = min_time.timestamp()
                    max_timestamp = max_time.timestamp()

                    st.subheader("⏰ Zeitbereich-Filter")
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        # Schiebe-Regler für Zeitbereich (mit Unix-Timestamps)
                        time_range_timestamps = st.slider(
                            "Zeitbereich auswählen:",
                            min_value=min_timestamp,
                            max_value=max_timestamp,
                            value=(min_timestamp, max_timestamp),
                            step=1.0,  # 1 Sekunde Schritte
                            help="Wählen Sie den interessanten Zeitbereich für die Timeline aus",
                        )

                        # Konvertiere zurück zu datetime-Objekten mit Timezone
                        time_range = (
                            pd.to_datetime(time_range_timestamps[0], unit='s', utc=True),
                            pd.to_datetime(time_range_timestamps[1], unit='s', utc=True),
                        )

                        # Zeige gewählten Zeitbereich an
                        st.info(
                            f"📊 **Gewählter Zeitbereich:** {time_range[0].strftime('%H:%M:%S')} - {time_range[1].strftime('%H:%M:%S')}"
                        )

                    with col2:
                        if st.button("🔄 Zeitfilter zurücksetzen"):
                            st.session_state.time_range_reset = True
                            st.rerun()

                        # Schnelle Zeitbereich-Auswahl
                        st.markdown("**Schnelle Auswahl:**")
                        if st.button("⏰ Ganzer Zeitbereich"):
                            st.rerun()

                        if st.button("⏱️ Letzte 5 Min"):
                            # Berechne 5 Minuten vor Ende
                            end_time = max_time
                            start_time = end_time - pd.Timedelta(minutes=5)
                            st.rerun()

                        if st.button("⏱️ Erste 5 Min"):
                            # Berechne 5 Minuten nach Anfang
                            start_time = min_time
                            end_time = start_time + pd.Timedelta(minutes=5)
                            st.rerun()

                    # Messages nach Zeitbereich filtern
                    filtered_messages = [msg for msg in messages if time_range[0] <= msg["timestamp"] <= time_range[1]]

                    # Zeige gefilterte Messages-Statistik
                    st.success(
                        f"✅ **Gefilterte Messages:** {len(filtered_messages)} von {len(messages)} ({len(filtered_messages)/len(messages)*100:.1f}%)"
                    )

                    # Timeline mit gefilterten Messages erstellen
                    try:
                        timeline_fig = analyzer.create_timeline_visualization(selected_topics, filtered_messages)
                        logger.debug("Timeline-Plot erfolgreich erstellt, zeige Chart")

                        # Plot anzeigen
                        st.plotly_chart(timeline_fig, use_container_width=True)
                        logger.debug("Timeline-Chart erfolgreich angezeigt")

                    except Exception as e:
                        logger.error(f"Fehler beim Erstellen der Timeline: {e}")
                        st.error(f"Fehler beim Erstellen der Timeline: {e}")
                else:
                    st.warning("Keine Messages in der Session gefunden")
            else:
                # Fallback ohne Zeitfilter
                try:
                    timeline_fig = analyzer.create_timeline_visualization(selected_topics)
                    logger.debug("Timeline-Plot erfolgreich erstellt, zeige Chart")

                    # Plot anzeigen
                    st.plotly_chart(timeline_fig, use_container_width=True)
                    logger.debug("Timeline-Chart erfolgreich angezeigt")

                except Exception as e:
                    logger.error(f"Fehler beim Erstellen der Timeline: {e}")
                    st.error(f"Fehler beim Erstellen der Timeline: {e}")

                # Payload-Anzeige bei Klick (vereinfachte Version)
                st.subheader("📄 Payload-Details")
                st.info(
                    "💡 **Hinweis:** Klicken Sie auf einen Datenpunkt in der Timeline, um die Payload-Details zu sehen. Die Details werden in den Hover-Tooltips angezeigt."
                )

                # Alternative: Payload-Suche nach Topic
                st.markdown("**Oder suchen Sie nach einem spezifischen Topic:**")

                # Topic-Auswahl für Payload-Anzeige
                all_topics_in_session = set()
                for message in analyzer.session_data["messages"]:
                    all_topics_in_session.add(message["topic"])

                selected_topic_for_payload = st.selectbox(
                    "Topic für Payload-Anzeige auswählen:",
                    options=sorted(all_topics_in_session),
                    help="Wählen Sie ein Topic aus, um die Payloads anzuzeigen",
                )

                if selected_topic_for_payload:
                    # Zeige Payloads für das ausgewählte Topic (berücksichtige Zeitfilter)
                    if 'filtered_messages' in locals():
                        topic_messages = [
                            msg for msg in filtered_messages if msg["topic"] == selected_topic_for_payload
                        ]
                    else:
                        topic_messages = [
                            msg
                            for msg in analyzer.session_data["messages"]
                            if msg["topic"] == selected_topic_for_payload
                        ]

                    if topic_messages:
                        st.markdown(f"**{len(topic_messages)} Messages für Topic: `{selected_topic_for_payload}`**")

                        # Zeige die ersten 5 Messages
                        for i, message in enumerate(topic_messages[:5]):
                            with st.expander(f"Message {i+1} - {message['timestamp']}"):
                                col1, col2 = st.columns([1, 2])

                                with col1:
                                    st.markdown("**Topic:**")
                                    st.code(message["topic"])

                                    st.markdown("**Zeitstempel:**")
                                    st.code(str(message["timestamp"]))

                                with col2:
                                    st.markdown("**Payload:**")
                                    try:
                                        # Versuche JSON zu formatieren
                                        import json

                                        payload_json = json.loads(message["payload"])
                                        st.json(payload_json)
                                    except (json.JSONDecodeError, TypeError):
                                        # Fallback: Als Text anzeigen
                                        st.code(message["payload"], language="text")

                        if len(topic_messages) > 5:
                            st.info(
                                f"Zeige nur die ersten 5 von {len(topic_messages)} Messages. Verwenden Sie die Filter, um spezifische Topics zu analysieren."
                            )
                    else:
                        st.warning("Keine Messages für das ausgewählte Topic gefunden.")

                logger.debug("Timeline-Chart erfolgreich angezeigt")

            # Topic-Statistiken
            st.subheader("📊 Topic-Statistiken")

            # Erstelle DataFrame für die ausgewählten Topics
            selected_stats = {topic: stats["topic_counts"].get(topic, 0) for topic in selected_topics}

            # Bar Chart für Topic-Counts
            fig_bar = px.bar(
                x=list(selected_stats.keys()),
                y=list(selected_stats.values()),
                title="Nachrichten pro Topic",
                labels={"x": "Topic", "y": "Anzahl Nachrichten"},
                color=list(selected_stats.values()),
                color_continuous_scale="viridis",
            )

            # Topic-Namen anpassen
            fig_bar.update_xaxes(
                tickangle=45, ticktext=[analyzer.topic_manager.get_friendly_name(topic) for topic in selected_topics]
            )

            st.plotly_chart(fig_bar, use_container_width=True)

            # Detaillierte Topic-Liste
            st.subheader("📋 Detaillierte Topic-Informationen")

            topic_data = []
            for topic in selected_topics:
                topic_info = analyzer.topic_manager.get_topic_info(topic)
                topic_data.append(
                    {
                        "Topic": topic,
                        "Friendly Name": analyzer.topic_manager.get_friendly_name(topic),
                        "Kategorie": topic_info.get("category", "Unknown"),
                        "Nachrichten": stats["topic_counts"].get(topic, 0),
                        "Beschreibung": topic_info.get("description", "Keine Beschreibung"),
                    }
                )

            df_topics = pd.DataFrame(topic_data)
            st.dataframe(df_topics, use_container_width=True)

        else:
            st.info("Bitte wählen Sie mindestens ein Topic für die Timeline-Visualisierung aus.")

    else:
        st.info("👆 Bitte laden Sie zuerst eine Session, um die Analyse zu starten.")

        # Demo-Button für schnelle Tests
        if st.button("🚀 Demo-Session laden"):
            with st.spinner("Lade Demo-Session..."):
                success = analyzer.load_session_data("demo")
                if success:
                    st.session_state.session_loaded = True
                    st.session_state.current_session = "demo"
                    st.success("Demo-Session geladen!")
                    st.rerun()
                else:
                    st.error("Fehler beim Laden der Demo-Session!")
