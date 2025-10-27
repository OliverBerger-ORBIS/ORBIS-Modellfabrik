from __future__ import annotations

import threading
import time

import streamlit as st

_FLAG = "_ui_refresh_requested_at"


class RerunController:
    """
    Thread-sicherer Controller für st.rerun() Aufrufe mit Debouncing.

    Verhindert zu häufige Rerun-Requests und Race Conditions in MQTT-Callbacks.
    """

    def __init__(self, debounce_ms: int = 100):
        """
        Args:
            debounce_ms: Mindestabstand zwischen Rerun-Requests in Millisekunden
        """
        self._last_rerun = 0
        self._debounce_ms = debounce_ms
        self._lock = threading.Lock()

    def request_rerun(self, force: bool = False) -> bool:
        """
        Fordert einen Rerun an, wenn Debounce-Zeit verstrichen ist.

        Args:
            force: Rerun erzwingen, auch wenn Debounce-Zeit nicht verstrichen ist

        Returns:
            True wenn Rerun ausgeführt wurde, False wenn debounced
        """
        with self._lock:
            now = time.time() * 1000  # Millisekunden
            if force or (now - self._last_rerun) > self._debounce_ms:
                self._last_rerun = now
                st.rerun()
                return True
            return False

    def get_time_since_last_rerun(self) -> float:
        """Gibt die Zeit seit dem letzten Rerun in Millisekunden zurück."""
        with self._lock:
            return (time.time() * 1000) - self._last_rerun


# Globale RerunController-Instanz
_rerun_controller: RerunController | None = None


def get_rerun_controller() -> RerunController:
    """Gibt die globale RerunController-Instanz zurück."""
    global _rerun_controller
    if _rerun_controller is None:
        _rerun_controller = RerunController()
    return _rerun_controller


def request_refresh() -> None:
    """Aus Komponenten aufrufen statt st.rerun(); löst einen EINMALIGEN Refresh aus."""
    st.session_state[_FLAG] = time.time()


def consume_refresh() -> bool:
    """
    Check if any refresh group has been updated since last check.

    This function checks the backend refresh timestamps for all known groups
    and triggers a rerun if any have been updated. This ensures st.rerun() is
    called exactly once per detected refresh event.

    Returns:
        True if refresh detected and rerun should occur, False otherwise
    """
    try:
        from omf2.backend.refresh import get_all_refresh_groups, get_last_refresh_ts

        # Get all active refresh groups
        groups = get_all_refresh_groups()

        if not groups:
            # No refresh groups yet, nothing to check
            return False

        # Check each group for updates
        refresh_needed = False
        for group in groups:
            # Get current timestamp from backend
            current_ts = get_last_refresh_ts(group)

            if current_ts is None:
                continue

            # Get last seen timestamp from session state
            session_key = f"_last_seen_refresh_{group}"
            last_seen_ts = st.session_state.get(session_key, 0)

            # Check if timestamp has increased
            if current_ts > last_seen_ts:
                # Update session state with new timestamp
                st.session_state[session_key] = current_ts
                refresh_needed = True

        return refresh_needed

    except Exception as e:
        # Defensive: log error but don't break UI flow
        from omf2.common.logger import get_logger
        logger = get_logger(__name__)
        logger.debug(f"⚠️ Error checking refresh status: {e}")
        return False


def request_rerun_safe(force: bool = False) -> bool:
    """
    Thread-sichere Rerun-Anfrage mit Debouncing.

    Args:
        force: Rerun erzwingen, auch wenn Debounce-Zeit nicht verstrichen ist

    Returns:
        True wenn Rerun ausgeführt wurde, False wenn debounced
    """
    controller = get_rerun_controller()
    return controller.request_rerun(force)
