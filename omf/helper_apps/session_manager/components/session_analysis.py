"""
Session Analysis - Main controller for session analysis functionality
Refactored version with separated components
"""

import streamlit as st
import pandas as pd

from omf.dashboard.tools.logging_config import get_logger
from omf.helper_apps.session_manager.components.session_analyzer import SessionAnalyzer
from omf.helper_apps.session_manager.components.settings_manager import SettingsManager
from omf.helper_apps.session_manager.components.timeline_visualizer import TimelineVisualizer
from omf.helper_apps.session_manager.components.ui_components import SessionAnalysisUI

logger = get_logger(__name__)


def render_payload_sequence(messages, selected_topics=None):
    """Rendert die Payload Sequenz Visualisierung als kompakte Konsolen-Log Tabelle mit festen Spalten-Breiten"""
    st.header("📋 Payload Sequenz")
    st.markdown("**Chronologische Darstellung der gefilterten Topic und Payload Daten**")
    
    if not messages:
        st.info("ℹ️ Keine Messages verfügbar (Filter angewendet)")
        return
    
    # Topic-Filter anwenden wenn selected_topics angegeben ist
    filtered_messages = messages
    if selected_topics:
        filtered_messages = [msg for msg in messages if msg.get("topic", "") in selected_topics]
        logger.debug(f"Topic-Filter angewendet: {len(filtered_messages)} von {len(messages)} Messages")
    
    if not filtered_messages:
        st.info("ℹ️ Keine Messages nach Topic-Filter verfügbar")
        return
    
    # Daten für die Tabelle vorbereiten
    table_data = []
    for i, msg in enumerate(filtered_messages):
        try:
            # Payload als vollständiger String (nicht abgeschnitten)
            payload_str = msg.get("payload", "")
            payload_string = payload_to_full_string(payload_str)
            
            table_data.append({
                "Topic": msg.get("topic", ""),
                "Payload": payload_string,
                "Raw_Payload": payload_str  # Für Expand-to-JSON
            })
        except Exception as e:
            logger.warning(f"Fehler beim Formatieren von Message {i}: {e}")
            table_data.append({
                "Topic": msg.get("topic", ""),
                "Payload": f"Fehler beim Formatieren: {str(payload_str)}",
                "Raw_Payload": payload_str
            })
    
    # Tabelle anzeigen
    if table_data:
        # Streamlit DataFrame für bessere Darstellung
        df = pd.DataFrame(table_data)
        
        # Tabelle mit konfigurierbaren Spalten
        st.subheader(f"📊 Messages ({len(table_data)} Einträge)")
        
        # Container für feste Breite (unabhängig von Fenster-Größe)
        container = st.container()
        
        with container:
            # Neue Spalten-Anordnung: Topic | Payload | Expand
            # Topic doppelte Größe, neue Gewichtungen: [2, 6, 1]
            col1, col2, col3 = st.columns([2, 6, 1])
            
            with col1:
                st.markdown("**Topic**")
            with col2:
                st.markdown("**Payload**")
            with col3:
                st.markdown("**Expand**")
            
            # Tabelle zeilenweise rendern mit neuer Spalten-Anordnung
            for idx, row in df.iterrows():
                col1, col2, col3 = st.columns([2, 6, 1])  # Gleiche Gewichtungen
                
                with col1:
                    # Topic als Code-ähnlicher Text (Konsolen-Log Stil) - doppelte Größe
                    st.code(str(row["Topic"]), language="text")
                
                with col2:
                    # Payload als vollständiger String (Konsolen-Log Stil)
                    st.code(str(row["Payload"]), language="json")
                
                with col3:
                    # Expand/Collapse mit st.expander für bessere Performance (kein st.rerun)
                    with st.expander("🔍"):
                        formatted_json = format_json_payload(row["Raw_Payload"])
                        st.code(formatted_json, language="json")
        
        # Export-Button
        if st.button("📥 Payload Sequenz exportieren"):
            export_payload_sequence(df)
    else:
        st.warning("⚠️ Keine Daten für Payload Sequenz verfügbar")


def payload_to_string(payload_str):
    """Konvertiert Payload zu einem kompakten String für Tabellenanzeige"""
    if not payload_str:
        return "{}"
    
    # Wenn bereits ein Dictionary ist
    if isinstance(payload_str, dict):
        try:
            import json
            return json.dumps(payload_str, separators=(',', ':'), ensure_ascii=False)
        except Exception:
            return str(payload_str)
    
    # Wenn String ist, versuche zu kompaktieren
    if isinstance(payload_str, str):
        # Entferne unnötige Leerzeichen und Zeilenumbrüche
        compact = payload_str.replace('\n', '').replace('\r', '').replace('  ', ' ')
        # Kürze bei sehr langen Strings
        if len(compact) > 100:
            return compact[:97] + "..."
        return compact
    
    # Fallback
    return str(payload_str)


def payload_to_full_string(payload_str):
    """Konvertiert Payload zu einem vollständigen String für Konsolen-Log Darstellung (nicht abgeschnitten)"""
    if not payload_str:
        return "{}"
    
    # Wenn bereits ein Dictionary ist
    if isinstance(payload_str, dict):
        try:
            import json
            return json.dumps(payload_str, separators=(',', ':'), ensure_ascii=False)
        except Exception:
            return str(payload_str)
    
    # Wenn String ist, kompaktieren aber nicht abschneiden
    if isinstance(payload_str, str):
        # Entferne nur Zeilenumbrüche und überflüssige Leerzeichen, aber behalte den vollständigen Inhalt
        compact = payload_str.replace('\n', '').replace('\r', '').replace('  ', ' ')
        return compact
    
    # Fallback
    return str(payload_str)


def format_json_payload(payload_str):
    """Formatiert Payload als JSON (fehlertolerant)"""
    import json
    
    if not payload_str:
        return "{}"
    
    # Wenn bereits ein Dictionary ist
    if isinstance(payload_str, dict):
        try:
            return json.dumps(payload_str, indent=2, ensure_ascii=False)
        except Exception:
            return str(payload_str)
    
    # Wenn String ist, versuche JSON zu parsen
    if isinstance(payload_str, str):
        try:
            # Versuche JSON zu parsen
            parsed = json.loads(payload_str)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            # Wenn kein gültiges JSON, zeige als String
            return str(payload_str)
    
    # Fallback
    return str(payload_str)


def export_payload_sequence(df):
    """Exportiert Payload Sequenz als CSV"""
    try:
        # Nur Topic und Payload für Export (Raw_Payload ist nur für interne Verwendung)
        export_df = df[["Topic", "Payload"]].copy()
        csv_data = export_df.to_csv(index=False, encoding='utf-8')
        
        st.download_button(
            label="📥 Download Payload Sequenz (CSV)",
            data=csv_data,
            file_name=f"payload_sequence_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
        st.success("✅ Export bereit")
    except Exception as e:
        logger.error(f"Fehler beim Export: {e}")
        st.error(f"❌ Fehler beim Export: {e}")


def show_session_analysis():
    """Hauptfunktion für Session-Analyse (Refactored)"""
    logger.info("📊 Session Analysis Tab geladen")

    # Settings Manager initialisieren
    settings_manager = SettingsManager()

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

    # Session-Verzeichnis aus Settings laden
    session_directory = settings_manager.get_session_directory("session_analysis")
    logger.debug(f"Session-Verzeichnis aus Settings: {session_directory}")

    # Session-Auswahl mit Settings-Verzeichnis
    selected_session = ui.render_session_selection(session_directory)

    if selected_session:
        # Session laden
        if analyzer.load_session_data(selected_session, session_directory):
            st.session_state.session_loaded = True
            st.session_state.current_session = selected_session
            st.success(f"✅ Session erfolgreich geladen: {selected_session}")
            logger.info(f"Session geladen: {selected_session} aus {session_directory}")
        else:
            st.error("❌ Fehler beim Laden der Session")
            logger.error(f"Fehler beim Laden der Session: {selected_session}")
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

            # Payload Sequenz Visualisierung
            st.markdown("---")
            render_payload_sequence(filtered_messages, selected_topics)
        else:
            st.warning("Bitte wählen Sie Topics für die Visualisierung aus")
    else:
        st.info("Bitte laden Sie zuerst eine Session")
