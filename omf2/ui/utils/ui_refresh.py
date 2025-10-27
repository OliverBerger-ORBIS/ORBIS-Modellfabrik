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
    Check if backend refresh has been triggered and rerun if needed.
    
    This function checks the backend refresh API for any new refresh events
    and returns True if a rerun should happen. It tracks the last known
    refresh timestamp in session_state to avoid unnecessary reruns.
    
    Returns:
        True if a rerun should happen, False otherwise
    """
    # First check local flag for component-initiated refreshes
    ts = st.session_state.get(_FLAG, 0)
    if ts:
        st.session_state[_FLAG] = 0
        return True
    
    # Then check backend for refresh events
    try:
        from omf2.backend.refresh import get_last_refresh
        
        # Check common refresh groups
        refresh_groups = ["order_updates", "module_updates", "sensor_updates"]
        
        for group in refresh_groups:
            # Get current refresh timestamp from backend
            current_ts = get_last_refresh(group)
            
            if current_ts is not None:
                # Get last known timestamp from session_state
                key = f"_last_refresh_ts_{group}"
                last_ts = st.session_state.get(key, None)
                
                # If this is new or timestamp has changed, trigger refresh
                if last_ts is None or current_ts > last_ts:
                    # Update session_state with new timestamp
                    st.session_state[key] = current_ts
                    return True
        
        return False
    
    except Exception as e:
        # If backend check fails, fall back to no refresh
        # This ensures the app continues to work even if Redis is unavailable
        from omf2.common.logger import get_logger
        logger = get_logger(__name__)
        logger.debug(f"⚠️ Backend refresh check failed: {e}")
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
