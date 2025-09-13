#!/usr/bin/env python3
"""
Session Manager Dashboard
Demonstriert kontrolliertes st.rerun() Handling und zentrales Logging
"""

import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from .logging_utils import get_session_logger
from .rerun_control import execute_pending_rerun, get_rerun_controller, request_rerun


class SessionManager:
    """Hauptklasse für Session-Management mit Logging und Rerun-Kontrolle"""

    def __init__(self):
        self.logger = get_session_logger("session_manager", "INFO")
        self.rerun_controller = get_rerun_controller("session_manager")
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Session State initialisieren"""
        if "session_data" not in st.session_state:
            st.session_state.session_data = {
                "counter": 0,
                "last_action": None,
                "session_start": datetime.now(),
                "actions_log": [],
            }
            self.logger.log_event("Session initialized", "INFO")

    def increment_counter(self):
        """Counter erhöhen mit kontrolliertem Rerun"""
        old_value = st.session_state.session_data["counter"]
        st.session_state.session_data["counter"] += 1
        new_value = st.session_state.session_data["counter"]

        # Logging
        self.logger.log_ui_action("counter_increment", {"old_value": old_value, "new_value": new_value})

        # Action Log aktualisieren
        action = f"Counter: {old_value} → {new_value}"
        st.session_state.session_data["actions_log"].append({"timestamp": datetime.now(), "action": action})
        st.session_state.session_data["last_action"] = action

        # Kontrollierten Rerun anfordern
        request_rerun("Counter wurde erhöht", "increment_button", show_ui_feedback=True)

    def reset_counter(self):
        """Counter zurücksetzen"""
        old_value = st.session_state.session_data["counter"]
        st.session_state.session_data["counter"] = 0

        # Logging
        self.logger.log_ui_action("counter_reset", {"old_value": old_value})

        # Action Log aktualisieren
        action = f"Counter reset: {old_value} → 0"
        st.session_state.session_data["actions_log"].append({"timestamp": datetime.now(), "action": action})
        st.session_state.session_data["last_action"] = action

        # Kontrollierten Rerun anfordern
        request_rerun("Counter wurde zurückgesetzt", "reset_button", show_ui_feedback=True)

    def simulate_error(self):
        """Fehler simulieren für Logging-Demo"""
        try:
            # Absichtlicher Fehler
            _ = 10 / 0
        except Exception as e:
            self.logger.log_error(e, "Simulierter Fehler für Demo-Zwecke")
            st.error("❌ Simulierter Fehler - siehe Log-Datei für Details")

            # Action Log aktualisieren
            action = "Error simulated"
            st.session_state.session_data["actions_log"].append({"timestamp": datetime.now(), "action": action})

    def load_session_data(self, data: dict):
        """Session-Daten laden (simuliert)"""
        self.logger.log_event("Loading session data", "INFO", data_keys=list(data.keys()))

        # Simuliere längere Ladezeit
        with st.spinner("Lade Session-Daten..."):
            time.sleep(1)  # Simulierte Ladezeit

        # Daten aktualisieren
        st.session_state.session_data.update(data)

        # Action Log aktualisieren
        action = f"Session data loaded: {len(data)} items"
        st.session_state.session_data["actions_log"].append({"timestamp": datetime.now(), "action": action})

        # Erfolg melden
        st.success("✅ Session-Daten erfolgreich geladen!")
        self.logger.log_event("Session data loaded successfully", "INFO")

        # Kontrollierten Rerun anfordern
        request_rerun("Session-Daten wurden geladen", "load_data", show_ui_feedback=True)


def render_session_status(session_manager: SessionManager):
    """Session-Status anzeigen"""
    st.markdown("### 📊 Session-Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        counter = st.session_state.session_data["counter"]
        st.metric("Counter", counter)

    with col2:
        session_start = st.session_state.session_data["session_start"]
        duration = datetime.now() - session_start
        st.metric("Session-Dauer", f"{duration.seconds}s")

    with col3:
        actions_count = len(st.session_state.session_data["actions_log"])
        st.metric("Aktionen", actions_count)


def render_rerun_status():
    """Status der Rerun-Kontrolle anzeigen"""
    st.markdown("### 🔄 Rerun-Status")

    controller = get_rerun_controller()

    col1, col2 = st.columns(2)

    with col1:
        is_pending = controller.is_rerun_pending()
        status = "🟡 Anstehend" if is_pending else "🟢 Bereit"
        st.metric("Rerun-Status", status)

    with col2:
        if is_pending:
            reason, source = controller.get_rerun_info()
            st.text(f"Grund: {reason}")
            st.text(f"Quelle: {source}")
        else:
            st.text("Kein Rerun anstehend")


def render_actions_log():
    """Aktions-Log anzeigen"""
    st.markdown("### 📝 Aktions-Log")

    actions = st.session_state.session_data["actions_log"]

    if not actions:
        st.info("Noch keine Aktionen durchgeführt")
        return

    # Zeige die letzten 10 Aktionen
    recent_actions = actions[-10:]

    for action in reversed(recent_actions):
        timestamp = action["timestamp"].strftime("%H:%M:%S")
        st.text(f"{timestamp} - {action['action']}")


def render_logging_demo(session_manager: SessionManager):
    """Logging-Demo Bereich"""
    st.markdown("### 📋 Logging-Demo")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📈 Counter +1"):
            session_manager.increment_counter()

    with col2:
        if st.button("🔄 Reset Counter"):
            session_manager.reset_counter()

    with col3:
        if st.button("⚠️ Fehler simulieren"):
            session_manager.simulate_error()


def render_session_data_demo(session_manager: SessionManager):
    """Session-Daten Demo"""
    st.markdown("### 💾 Session-Daten Demo")

    # Simulierte Daten zum Laden
    sample_data = {"demo_value": 42, "demo_text": "Test Session Data", "demo_timestamp": datetime.now().isoformat()}

    if st.button("📂 Session-Daten laden"):
        session_manager.load_session_data(sample_data)


def render_log_file_viewer():
    """Log-Datei Viewer"""
    st.markdown("### 📄 Log-Datei Viewer")

    log_file = Path("logs/session_manager.log")

    if not log_file.exists():
        st.warning("❌ Log-Datei noch nicht erstellt")
        return

    try:
        # Zeige die letzten Zeilen der Log-Datei
        with open(log_file, encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            st.info("Log-Datei ist leer")
            return

        # Zeige die letzten 20 Zeilen
        recent_lines = lines[-20:] if len(lines) > 20 else lines

        st.code('\n'.join(recent_lines), language='text')

        # Download-Button für vollständige Log-Datei
        with open(log_file, 'rb') as f:
            st.download_button(
                "📥 Vollständige Log-Datei herunterladen", f.read(), file_name="session_manager.log", mime="text/plain"
            )

    except Exception as e:
        st.error(f"❌ Fehler beim Lesen der Log-Datei: {e}")


def main():
    """Hauptfunktion der Session Manager App"""
    st.set_page_config(page_title="🎛️ Session Manager", page_icon="🎛️", layout="wide")

    st.title("🎛️ Session Manager Dashboard")
    st.markdown("Demonstriert kontrolliertes st.rerun() Handling und zentrales Logging")

    # Session Manager initialisieren
    session_manager = SessionManager()

    # Prüfe und führe anstehende Reruns aus
    # Dies sollte am Anfang jeder Streamlit-Ausführung stehen
    execute_pending_rerun()

    # Hauptlayout
    col1, col2 = st.columns([2, 1])

    with col1:
        render_session_status(session_manager)
        render_logging_demo(session_manager)
        render_session_data_demo(session_manager)

    with col2:
        render_rerun_status()
        render_actions_log()

    # Separator
    st.markdown("---")

    # Log-Datei Viewer
    render_log_file_viewer()

    # Entwickler-Info
    st.markdown("---")
    st.markdown("### 🔧 Entwickler-Info")
    st.info(
        """
        **Rerun-Kontrolle:**
        - Verwendung von `st.session_state["needs_rerun"]` Flag
        - Verhindert Rerun-Kaskaden und unnötige Reruns
        - UI-Feedback bei jedem Rerun

        **Logging-Konzept:**
        - Python logging-Modul mit strukturierten Logs
        - Log-Datei: `logs/session_manager.log`
        - Trennung von UI-Feedback und Entwickler-Logs
        - Konfigurierbar und wiederverwendbar
        """
    )


if __name__ == "__main__":
    main()
