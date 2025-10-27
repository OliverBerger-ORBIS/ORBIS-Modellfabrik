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
    Check if UI refresh is needed by polling Redis-backed refresh timestamps
    or checking for manual refresh requests.
    
    This function checks:
    1. Manual refresh flag (set by request_refresh() from UI components)
    2. Redis-backed refresh timestamps for all configured groups
    
    Returns:
        True if refresh is needed, False otherwise
    """
    from omf2.backend.refresh import get_all_refresh_groups, get_last_refresh
    
    # Check manual refresh flag first
    manual_refresh = st.session_state.get(_FLAG, 0)
    if manual_refresh:
        st.session_state[_FLAG] = 0
        return True
    
    # Session state key for tracking last checked timestamps per group
    _LAST_CHECKED = "_ui_last_checked_timestamps"
    
    # Initialize tracking dict if not present
    if _LAST_CHECKED not in st.session_state:
        st.session_state[_LAST_CHECKED] = {}
    
    last_checked = st.session_state[_LAST_CHECKED]
    
    try:
        # Get all refresh groups from Redis
        groups = get_all_refresh_groups()
        
        # Check if any group has been updated since last check
        for group in groups:
            current_ts = get_last_refresh(group)
            
            if current_ts is not None:
                last_ts = last_checked.get(group, 0)
                
                # If timestamp is newer, trigger refresh
                if current_ts > last_ts:
                    # Update all checked timestamps
                    for g in groups:
                        ts = get_last_refresh(g)
                        if ts is not None:
                            last_checked[g] = ts
                    
                    return True
        
        return False
        
    except Exception as e:
        # Defensive: don't break UI if Redis polling fails
        from omf2.common.logger import get_logger
        logger = get_logger(__name__)
        logger.debug(f"⚠️ Failed to check refresh timestamps: {e}")
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
