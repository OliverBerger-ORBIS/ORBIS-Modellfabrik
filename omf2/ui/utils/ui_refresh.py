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
    Check for UI refresh via Redis-backed backend polling.
    
    Polls all configured refresh groups and triggers a rerun if any have new timestamps.
    This is the single entrypoint for UI refreshes in the main application.
    
    Returns:
        True if a refresh was detected (triggers st.rerun()), False otherwise
    """
    try:
        from omf2.backend.refresh import get_all_refresh_groups, get_last_refresh
        
        # Get all active refresh groups
        groups = get_all_refresh_groups()
        
        if not groups:
            # No refresh groups yet, nothing to check
            return False
        
        # Check each group for updates
        for group in groups:
            # Get current timestamp from backend
            current_timestamp = get_last_refresh(group)
            
            if current_timestamp is None:
                continue
            
            # Get last known timestamp from session_state
            key = f"_last_refresh_{group}"
            last_timestamp = st.session_state.get(key, None)
            
            # Check if refresh is needed
            if last_timestamp is None or current_timestamp > last_timestamp:
                # Update session_state with new timestamp
                st.session_state[key] = current_timestamp
                return True
        
        return False
        
    except Exception as e:
        # Defensive: don't break the app if refresh checking fails
        from omf2.common.logger import get_logger
        logger = get_logger(__name__)
        logger.debug(f"⚠️ Error checking for refresh: {e}")
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
