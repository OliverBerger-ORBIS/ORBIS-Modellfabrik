from __future__ import annotations

import time

import streamlit as st

_FLAG = "_ui_refresh_requested_at"


def request_refresh() -> None:
    """Aus Komponenten aufrufen statt st.rerun(); löst einen EINMALIGEN Refresh aus."""
    st.session_state[_FLAG] = time.time()


def consume_refresh() -> bool:
    """Früh in omf_dashboard.main() aufrufen. Gibt genau einmal True zurück, dann Flag löschen."""
    ts = st.session_state.get(_FLAG, 0)
    if ts:
        st.session_state[_FLAG] = 0
        return True
    return False
