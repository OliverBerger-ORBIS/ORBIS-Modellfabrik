"""
Settings UI für Session Manager
Streamlit UI für die Einstellungen
"""

from pathlib import Path

import streamlit as st

from ..utils.logging_config import get_logger
from ..utils.ui_refresh import RerunController, request_refresh
from .logs import show_logs
from .settings_manager import SettingsManager

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
        st.markdown(
            "Konfiguration für **Replay Station**, **Session Recorder**, **Logging** und Import/Export der Einstellungsdatei."
        )

        tab1, tab2, tab3 = st.tabs(["▶️ Replay Station", "🔴 Session Recorder", "📝 Logging & Diagnose"])

        with tab1:
            self._render_replay_station_settings()

        with tab2:
            self._render_session_recorder_settings()

        with tab3:
            self._render_logging_and_diagnostics()

        st.markdown("---")
        self._render_general_settings()

    def _render_logging_and_diagnostics(self):
        """Logging-Level, Log-Datei und Live-Logs (ehemals Top-Level-Tab „Logging“)."""
        st.subheader("📝 Logging")
        diag_logger = get_logger("session_manager.settings_ui")

        current_level = st.session_state.get("logging_level", "INFO")
        st.caption(
            f"Aktuelles Level: **{current_level}** · Live-Stream unten (Ring-Buffer). JSONL-Datei unter Projekt-`logs/`."
        )
        level_options = ["DEBUG", "INFO", "WARNING", "ERROR"]
        selected_level = st.selectbox(
            "Logging-Level",
            level_options,
            index=level_options.index(current_level) if current_level in level_options else 1,
            help="Gilt für neue Logger-Ausgaben nach Änderung (Seite neu laden kann nötig sein).",
            key="settings_logging_level_select",
        )
        if selected_level != current_level:
            st.session_state["logging_level"] = selected_level
            st.success(f"Level auf **{selected_level}** gesetzt — bei Bedarf App neu starten für volle Wirkung.")
            request_refresh()

        st.info("Alte Log-Dateien werden beim App-Start bereinigt (siehe `logging_config`).")

        log_file = Path("logs/session_manager.jsonl")
        st.markdown(f"**Log-Datei:** `{log_file}`")
        if log_file.exists():
            size_mb = log_file.stat().st_size / (1024 * 1024)
            st.markdown(f"**Größe:** {size_mb:.2f} MB")
            if st.button("🗑️ Log-Datei löschen", key="settings_delete_jsonl"):
                try:
                    log_file.unlink()
                    st.success("Log-Datei gelöscht.")
                    request_refresh()
                except OSError as e:
                    st.error(f"Löschen fehlgeschlagen: {e}")
        else:
            st.warning("Datei existiert noch nicht.")

        with st.expander("JSONL-Datei — letzte Zeilen"):
            if log_file.exists():
                try:
                    lines = log_file.read_text(encoding="utf-8").splitlines()
                    tail = "\n".join(lines[-20:]) if lines else ""
                    st.code(tail or "(leer)", language="text")
                except OSError as e:
                    st.error(str(e))
            else:
                st.caption("Keine Datei.")

        with st.expander("Optional: Test-Logzeilen senden"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("DEBUG", key="log_demo_debug"):
                    diag_logger.debug("Debug-Testzeile (Settings)")
            with c2:
                if st.button("INFO", key="log_demo_info"):
                    diag_logger.info("Info-Testzeile (Settings)")
            with c3:
                if st.button("WARNING", key="log_demo_warn"):
                    diag_logger.warning("Warning-Testzeile (Settings)")
            with c4:
                if st.button("ERROR", key="log_demo_err"):
                    diag_logger.error("Error-Testzeile (Settings)")

        st.markdown("---")
        show_logs()

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

        preset_labels = ("Alle Topics (unfiltered)", "Analyse: ohne Arduino / BME680 / Kamera / LDR (DR-25)")
        preset_values = ("none", "analysis")
        current_preset = self.settings_manager.get_session_recorder_recording_exclusion_preset()
        preset_index = preset_values.index(current_preset) if current_preset in preset_values else 0
        selected_label = st.selectbox(
            "Topic-Aufnahme (Session Recorder)",
            options=list(preset_labels),
            index=preset_index,
            help="„Analyse“ unterdrückt Schreiben von Arduino-, BME680-, Kamera- und LDR-Topics (DR-25).",
            key=f"settings_recorder_exclusion_preset_{current_preset}",
        )
        recording_exclusion_preset = preset_values[preset_labels.index(selected_label)]

        col1, col2 = st.columns(2)

        with col1:
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
                    "auto_save": auto_save,
                    "save_interval": save_interval,
                    "max_file_size": max_file_size,
                    "recording_exclusion_preset": recording_exclusion_preset,
                },
            )
            st.success("✅ Recording Einstellungen gespeichert!")

    # def _render_template_analysis_settings(self):
    #     """Rendert die Template Analyse Einstellungen"""
    #     # REMOVED: template_analysis.py wurde entfernt
    #     st.subheader("📋 Template Analyse Einstellungen")
    #     st.info("❌ Template-Analyse Feature wurde entfernt (nicht verwendet)")

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
