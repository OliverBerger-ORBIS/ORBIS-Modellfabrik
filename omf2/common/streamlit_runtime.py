#!/usr/bin/env python3
"""
Utilities for reading Streamlit runtime information (current server port).
"""

import os
from typing import Optional


def get_streamlit_port(default: int = 8501) -> str:
    """
    Determine the current Streamlit server port as a string.

    Priority:
    1) Streamlit config (server.port)
    2) Environment variable STREAMLIT_SERVER_PORT
    3) Provided default (8501)
    """
    # Try Streamlit config first (available inside Streamlit runtime)
    try:
        from streamlit import config as st_config  # type: ignore

        port_value = st_config.get_option("server.port")
        if isinstance(port_value, int) and port_value > 0:
            return str(port_value)
    except Exception:
        pass

    # Fallback: environment variable
    env_port: Optional[str] = os.environ.get("STREAMLIT_SERVER_PORT")
    if env_port and env_port.isdigit():
        return env_port

    # Default
    return str(default)
