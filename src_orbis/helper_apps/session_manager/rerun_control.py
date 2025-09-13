#!/usr/bin/env python3
"""
Zentrale Rerun-Kontrolle für Session Manager
Implementiert kontrolliertes st.rerun() Handling mit Flag-System
"""

from typing import Callable

import streamlit as st

from .logging_utils import get_session_logger


class RerunController:
    """Zentrale Steuerung für st.rerun() mit Logging und UI-Feedback"""

    def __init__(self, logger_name: str = "session_manager"):
        self.logger = get_session_logger(logger_name)
        self.rerun_flag_key = "needs_rerun"
        self.rerun_reason_key = "rerun_reason"
        self.rerun_source_key = "rerun_source"

    def request_rerun(self, reason: str, source: str = "unknown", show_ui_feedback: bool = True):
        """Rerun anfordern mit Grund und Quelle"""
        # Verhindere Rerun-Kaskaden - nur wenn nicht bereits angefordert
        if not st.session_state.get(self.rerun_flag_key, False):
            st.session_state[self.rerun_flag_key] = True
            st.session_state[self.rerun_reason_key] = reason
            st.session_state[self.rerun_source_key] = source

            # Logging
            self.logger.log_rerun_trigger(reason, source)

            # UI-Feedback falls gewünscht
            if show_ui_feedback:
                self._show_rerun_feedback(reason, source)

    def execute_pending_rerun(self) -> bool:
        """Prüfen und ausführen von anstehendem Rerun"""
        if st.session_state.get(self.rerun_flag_key, False):
            reason = st.session_state.get(self.rerun_reason_key, "unknown")
            source = st.session_state.get(self.rerun_source_key, "unknown")

            # Flag zurücksetzen vor Rerun
            self._clear_rerun_flag()

            # Rerun ausführen
            self.logger.log_event(f"Executing rerun: {reason} from {source}", "INFO")
            st.rerun()
            return True
        return False

    def clear_rerun_request(self):
        """Rerun-Anfrage löschen ohne Ausführung"""
        if st.session_state.get(self.rerun_flag_key, False):
            reason = st.session_state.get(self.rerun_reason_key, "unknown")
            self.logger.log_event(f"Clearing rerun request: {reason}", "INFO")
            self._clear_rerun_flag()

    def is_rerun_pending(self) -> bool:
        """Prüfen ob Rerun ansteht"""
        return st.session_state.get(self.rerun_flag_key, False)

    def get_rerun_info(self) -> tuple[str, str]:
        """Information über anstehenden Rerun"""
        reason = st.session_state.get(self.rerun_reason_key, "unknown")
        source = st.session_state.get(self.rerun_source_key, "unknown")
        return reason, source

    def _clear_rerun_flag(self):
        """Interne Funktion zum Zurücksetzen der Rerun-Flags"""
        st.session_state[self.rerun_flag_key] = False
        st.session_state[self.rerun_reason_key] = ""
        st.session_state[self.rerun_source_key] = ""

    def _show_rerun_feedback(self, reason: str, source: str):
        """UI-Feedback für Rerun anzeigen"""
        feedback_msg = f"🔄 Aktualisierung: {reason}"
        if source != "unknown":
            feedback_msg += f" (von {source})"

        # Temporäres Info-Display
        st.info(feedback_msg)

    def with_rerun_on_change(self, reason: str, source: str = None):
        """Decorator/Context für automatischen Rerun bei Änderungen"""

        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                # Rerun nur wenn sich Ergebnis geändert hat
                old_result = st.session_state.get(f"_last_result_{func.__name__}", None)
                if result != old_result:
                    st.session_state[f"_last_result_{func.__name__}"] = result
                    self.request_rerun(reason, source or func.__name__)
                return result

            return wrapper

        return decorator


# Globale Controller-Instanz
_rerun_controller = None


def get_rerun_controller(logger_name: str = "session_manager") -> RerunController:
    """Zentrale Funktion zum Abrufen des Rerun-Controllers"""
    global _rerun_controller
    if _rerun_controller is None:
        _rerun_controller = RerunController(logger_name)
    return _rerun_controller


def request_rerun(reason: str, source: str = "unknown", show_ui_feedback: bool = True):
    """Convenience-Funktion für Rerun-Anfrage"""
    controller = get_rerun_controller()
    controller.request_rerun(reason, source, show_ui_feedback)


def execute_pending_rerun() -> bool:
    """Convenience-Funktion für Rerun-Ausführung"""
    controller = get_rerun_controller()
    return controller.execute_pending_rerun()
