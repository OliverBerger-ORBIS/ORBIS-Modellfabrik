"""
Settings UI für Session Manager
Streamlit UI für die Einstellungen
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import RerunController
from omf.helper_apps.session_manager.components.settings_manager import SettingsManager
from omf.tools.logging_config import get_logger

logger = get_logger(__name__)

class SettingsUI:
    """UI-Komponente für die Einstellungen"""

    def __init__(self, settings_manager: SettingsManager):
        self.settings_manager = settings_manager
        self.rerun_controller = RerunController()

    def render_settings_page(self):
        """Rendert die komplette Settings-Seite"""
        logger.info("⚙️ Settings Tab geladen")
        st.title("⚙️ Einstellungen")
        st.markdown("Zentrale Konfiguration für alle Session Manager Tabs")

        # Tabs für verschiedene Sektionen
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 Session Analyse", "▶️ Replay Station", "🔴 Session Recorder", "📋 Template Analyse"]
        )

        with tab1:
            self._render_session_analysis_settings()

        with tab2:
            self._render_replay_station_settings()

        with tab3:
            self._render_session_recorder_settings()

        with tab4:
            self._render_template_analysis_settings()

        # Allgemeine Einstellungen
        st.markdown("---")
        self._render_general_settings()

    def _render_session_analysis_settings(self):
        """Rendert die Session Analyse Einstellungen"""
        st.subheader("📊 Session Analyse Einstellungen")

        # Session-Verzeichnis
        st.markdown("**📁 Session-Verzeichnis**")
        st.markdown("Verzeichnis in dem die Session-Dateien gespeichert sind")

        current_directory = self.settings_manager.get_session_directory("session_analysis")
        new_directory = st.text_input(
            "Session-Verzeichnis:", value=current_directory, help="Pfad zum Verzeichnis mit Session-Dateien (.log)"
        )

        if new_directory != current_directory:
            if st.button("💾 Verzeichnis speichern", key="save_session_dir"):
                self.settings_manager.set_setting("session_analysis", "session_directory", new_directory)
                st.success(f"Session-Verzeichnis gespeichert: {new_directory}")
                self.rerun_controller.request_rerun()

        st.markdown("---")

        # Vorfilter-Topics
        st.markdown("**🔧 Vorfilter-Topics**")
        st.markdown("Topics die standardmäßig aus der Timeline ausgefiltert werden")

        current_topics = self.settings_manager.get_prefilter_topics()

        # Topic hinzufügen
        col1, col2 = st.columns([3, 1])
        with col1:
            new_topic = st.text_input("Neues Topic hinzufügen:", placeholder="/j1/txt/1/i/example")
        with col2:
            if st.button("➕ Hinzufügen", key="add_topic"):
                if new_topic and new_topic not in current_topics:
                    self.settings_manager.add_prefilter_topic(new_topic)
                    self.rerun_controller.request_rerun()

        # Vorfilter-Topics mit Aktiv/Nicht-Aktiv Buttons
        st.markdown("**Aktivierte Vorfilter-Topics:**")

        # Standard-Topics die häufig gefiltert werden
        common_topics = [
            "/j1/txt/1/i/cam",  # Kamera-Daten
            "/j1/txt/1/i/bme",  # BME680-Sensor-Daten
            "/j1/txt/1/c/bme680",  # BME680-Sensor-Daten (andere Schreibweise)
            "/j1/txt/1/c/cam",  # Kamera-Daten (andere Schreibweise)
            "/j1/txt/1/c/ldr",  # LDR-Sensor-Daten
            "/j1/txt/1/i/ldr",  # LDR-Sensor-Daten (andere Schreibweise)
        ]

        # Alle Topics (Standard + aktuelle)
        all_topics = list(set(common_topics + current_topics))

        if all_topics:
            for i, topic in enumerate(sorted(all_topics)):
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.code(topic)
                with col2:
                    is_active = topic in current_topics
                    if st.button("✅" if is_active else "❌", key=f"toggle_topic_{i}"):
                        if is_active:
                            self.settings_manager.remove_prefilter_topic(topic)
                        else:
                            self.settings_manager.add_prefilter_topic(topic)
                        self.rerun_controller.request_rerun()
                with col3:
                    if topic not in common_topics:  # Nur benutzerdefinierte Topics können gelöscht werden
                        if st.button("🗑️", key=f"delete_topic_{i}"):
                            self.settings_manager.remove_prefilter_topic(topic)
                            self.rerun_controller.request_rerun()
        else:
            st.info("Keine Vorfilter-Topics konfiguriert")

        # Weitere Session Analyse Einstellungen
        st.markdown("**⚙️ Weitere Einstellungen**")

        show_all_topics = self.settings_manager.get_setting("session_analysis", "show_all_topics_by_default", False)
        if st.checkbox("Alle Topics standardmäßig anzeigen", value=show_all_topics):
            self.settings_manager.set_setting("session_analysis", "show_all_topics_by_default", True)
        else:
            self.settings_manager.set_setting("session_analysis", "show_all_topics_by_default", False)

        timeline_height = self.settings_manager.get_setting("session_analysis", "timeline_height", 600)
        new_height = st.slider("Timeline-Höhe (Pixel)", 300, 1000, timeline_height)
        if new_height != timeline_height:
            self.settings_manager.set_setting("session_analysis", "timeline_height", new_height)

        max_topics = self.settings_manager.get_setting("session_analysis", "max_topics_display", 50)
        new_max = st.slider("Max. Topics in Anzeige", 10, 200, max_topics)
        if new_max != max_topics:
            self.settings_manager.set_setting("session_analysis", "max_topics_display", new_max)

    def _render_replay_station_settings(self):
        """Rendert die Replay Station Einstellungen"""
        st.subheader("▶️ Replay Station Einstellungen")

        # Session-Verzeichnis Einstellungen
        st.markdown("#### 📁 Session-Verzeichnis")
        current_dir = self.settings_manager.get_session_directory()

        session_directory = st.text_input(
            "Session-Verzeichnis", value=current_dir, help="Verzeichnis in dem sich die Session-Dateien befinden"
        )

        # Session-Verzeichnis Einstellungen speichern
        if st.button("💾 Session-Verzeichnis speichern"):
            self.settings_manager.update_session_directory(session_directory)
            st.success("✅ Session-Verzeichnis gespeichert!")

        st.markdown("---")

        # MQTT Broker Einstellungen
        st.markdown("#### 🔌 MQTT Broker Konfiguration")
        mqtt_settings = self.settings_manager.get_mqtt_broker_settings()

        col1, col2 = st.columns(2)

        with col1:
            mqtt_host = st.text_input(
                "MQTT Broker Host",
                value=mqtt_settings.get("host", "localhost"),
                help="Hostname oder IP-Adresse des MQTT Brokers",
            )

            mqtt_port = st.number_input(
                "MQTT Broker Port",
                min_value=1,
                max_value=65535,
                value=mqtt_settings.get("port", 1883),
                help="Port des MQTT Brokers",
            )

        with col2:
            mqtt_qos = st.selectbox(
                "QoS Level",
                options=[0, 1, 2],
                index=mqtt_settings.get("qos", 1),
                help="Quality of Service Level für MQTT Nachrichten",
            )

            mqtt_timeout = st.number_input(
                "Timeout (Sekunden)",
                min_value=1,
                max_value=60,
                value=mqtt_settings.get("timeout", 5),
                help="Timeout für MQTT Verbindungen",
            )

        # MQTT Einstellungen speichern
        if st.button("💾 MQTT Broker Einstellungen speichern"):
            self.settings_manager.update_mqtt_broker_settings(
                mqtt_host, int(mqtt_port), int(mqtt_qos), int(mqtt_timeout)
            )
            st.success("✅ MQTT Broker Einstellungen gespeichert!")

        st.markdown("---")

        # Replay-Einstellungen
        st.markdown("#### ▶️ Replay Einstellungen")
        replay_settings = self.settings_manager.get_setting("replay_station", "replay", {})

        col1, col2 = st.columns(2)

        with col1:
            default_speed = st.slider(
                "Standard-Geschwindigkeit",
                min_value=0.1,
                max_value=10.0,
                value=replay_settings.get("default_speed", 1.0),
                step=0.1,
                help="Geschwindigkeit für Replay (1.0 = Original-Geschwindigkeit)",
            )

        with col2:
            auto_play = st.checkbox(
                "Auto-Play",
                value=replay_settings.get("auto_play", False),
                help="Automatisches Starten des Replays nach Session-Load",
            )

        # Loop-Einstellung
        loop_playback = st.checkbox(
            "Loop-Wiedergabe",
            value=replay_settings.get("loop_playback", False),
            help="Wiederholung der Session nach Ende",
        )

        # Replay Einstellungen speichern
        if st.button("💾 Replay Einstellungen speichern"):
            self.settings_manager.set_setting(
                "replay_station",
                "replay",
                {"default_speed": default_speed, "auto_play": auto_play, "loop_playback": loop_playback},
            )
            st.success("✅ Replay Einstellungen gespeichert!")

    def _render_session_recorder_settings(self):
        """Rendert die Session Recorder Einstellungen"""
        st.subheader("🔴 Session Recorder Einstellungen")

        # Session-Verzeichnis Einstellungen
        st.markdown("#### 📁 Session-Verzeichnis")
        current_dir = self.settings_manager.get_session_recorder_directory()

        session_directory = st.text_input(
            "Session-Verzeichnis",
            value=current_dir,
            help="Verzeichnis in dem die Session-Dateien gespeichert werden",
            key="recorder_session_dir",
        )

        # Session-Verzeichnis Einstellungen speichern
        if st.button("💾 Session-Verzeichnis speichern", key="save_recorder_dir"):
            self.settings_manager.update_session_recorder_directory(session_directory)
            st.success("✅ Session-Verzeichnis gespeichert!")

        st.markdown("---")

        # MQTT Broker Einstellungen
        st.markdown("#### 🔌 MQTT Broker Konfiguration")
        mqtt_settings = self.settings_manager.get_session_recorder_mqtt_settings()

        col1, col2 = st.columns(2)

        with col1:
            mqtt_host = st.text_input(
                "MQTT Broker Host",
                value=mqtt_settings.get("host", "localhost"),
                help="Hostname oder IP-Adresse des MQTT Brokers",
                key="recorder_mqtt_host",
            )

            mqtt_port = st.number_input(
                "MQTT Broker Port",
                min_value=1,
                max_value=65535,
                value=mqtt_settings.get("port", 1883),
                help="Port des MQTT Brokers",
                key="recorder_mqtt_port",
            )

        with col2:
            mqtt_qos = st.selectbox(
                "QoS Level",
                options=[0, 1, 2],
                index=mqtt_settings.get("qos", 1),
                help="Quality of Service Level für MQTT Nachrichten",
                key="recorder_mqtt_qos",
            )

            mqtt_timeout = st.number_input(
                "Timeout (Sekunden)",
                min_value=1,
                max_value=60,
                value=mqtt_settings.get("timeout", 5),
                help="Timeout für MQTT Verbindungen",
                key="recorder_mqtt_timeout",
            )

        # Username und Password in separater Zeile
        col3, col4 = st.columns(2)

        with col3:
            mqtt_username = st.text_input(
                "MQTT Username (optional)",
                value=mqtt_settings.get("username", ""),
                help="Benutzername für MQTT Broker Authentifizierung",
                key="recorder_mqtt_username",
            )

        with col4:
            mqtt_password = st.text_input(
                "MQTT Password (optional)",
                value=mqtt_settings.get("password", ""),
                type="password",
                help="Passwort für MQTT Broker Authentifizierung",
                key="recorder_mqtt_password",
            )

        # MQTT Einstellungen speichern
        if st.button("💾 MQTT Broker Einstellungen speichern", key="save_recorder_mqtt"):
            self.settings_manager.update_session_recorder_mqtt_settings(
                mqtt_host, int(mqtt_port), int(mqtt_qos), int(mqtt_timeout), mqtt_username, mqtt_password
            )
            st.success("✅ MQTT Broker Einstellungen gespeichert!")

        st.markdown("---")

        # Recording-Einstellungen
        st.markdown("#### 🔴 Recording Einstellungen")
        recording_settings = self.settings_manager.get_setting("session_recorder", "recording", {})

        col1, col2 = st.columns(2)

        with col1:
            file_format = st.selectbox(
                "Datei-Format",
                options=["sqlite", "log"],
                index=0 if recording_settings.get("file_format", "sqlite") == "sqlite" else 1,
                help="Format für gespeicherte Session-Dateien",
                key="recorder_file_format",
            )

            auto_save = st.checkbox(
                "Automatisches Speichern",
                value=recording_settings.get("auto_save", True),
                help="Automatisches Speichern der Session-Daten",
                key="recorder_auto_save",
            )

        with col2:
            save_interval = st.number_input(
                "Speicher-Intervall (Sekunden)",
                min_value=60,
                max_value=3600,
                value=recording_settings.get("save_interval", 300),
                help="Intervall für automatisches Speichern",
                key="recorder_save_interval",
            )

            max_file_size = st.number_input(
                "Max. Dateigröße (MB)",
                min_value=10,
                max_value=1000,
                value=recording_settings.get("max_file_size", 100),
                help="Maximale Größe einer Session-Datei",
                key="recorder_max_file_size",
            )

        # Recording Einstellungen speichern
        if st.button("💾 Recording Einstellungen speichern", key="save_recorder_recording"):
            self.settings_manager.set_setting(
                "session_recorder",
                "recording",
                {
                    "file_format": file_format,
                    "auto_save": auto_save,
                    "save_interval": save_interval,
                    "max_file_size": max_file_size,
                },
            )
            st.success("✅ Recording Einstellungen gespeichert!")

    def _render_template_analysis_settings(self):
        """Rendert die Template Analyse Einstellungen"""
        st.subheader("📋 Template Analyse Einstellungen")

        show_payload = self.settings_manager.get_setting("template_analysis", "show_payload_preview", True)
        if st.checkbox("Payload-Vorschau anzeigen", value=show_payload):
            self.settings_manager.set_setting("template_analysis", "show_payload_preview", True)
        else:
            self.settings_manager.set_setting("template_analysis", "show_payload_preview", False)

        max_payload = self.settings_manager.get_setting("template_analysis", "max_payload_length", 200)
        new_length = st.slider("Max. Payload-Länge", 50, 1000, max_payload, 50)
        if new_length != max_payload:
            self.settings_manager.set_setting("template_analysis", "max_payload_length", new_length)

    def _render_general_settings(self):
        """Rendert die allgemeinen Einstellungen"""
        st.subheader("⚙️ Allgemeine Einstellungen")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Auf Standard zurücksetzen"):
                self.settings_manager.reset_to_defaults()
                st.success("Einstellungen auf Standard zurückgesetzt!")
                self.rerun_controller.request_rerun()

        with col2:
            if st.button("💾 Einstellungen speichern"):
                self.settings_manager.save_settings()
                st.success("Einstellungen gespeichert!")

        with col3:
            if st.button("📥 Einstellungen laden"):
                self.settings_manager._load_settings()
                st.success("Einstellungen neu geladen!")

        # Einstellungsdatei-Info
        st.markdown("**📁 Einstellungsdatei:**")
        st.code(f"{self.settings_manager.settings_file.absolute()}")

        # Aktuelle Einstellungen anzeigen
        with st.expander("🔍 Aktuelle Einstellungen anzeigen"):
            st.json(self.settings_manager.settings)
