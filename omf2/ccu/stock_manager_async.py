#!/usr/bin/env python3
"""
Stock Manager Async Initialization
Initialisiert den Stock Manager im Hintergrund-Thread für non-blocking Zugriff
"""

import threading
from typing import Any, Optional

import streamlit as st

from omf2.common.logger import get_logger

logger = get_logger(__name__)


def initialize_stock_manager_in_background():
    """Initialisiert den Stock Manager im Hintergrund-Thread"""
    try:
        logger.info("🔄 Stock Manager Background-Initialisierung gestartet")

        # Import hier um zirkuläre Imports zu vermeiden
        from omf2.ccu.stock_manager import StockManager

        # Stock Manager erstellen
        manager = StockManager()

        # Status im Session-State aktualisieren
        st.session_state["stock_manager_status"] = "ready"
        st.session_state["stock_manager"] = manager

        logger.info("✅ Stock Manager Background-Initialisierung erfolgreich")
        logger.info(f"🏗️ Stock Manager Inventory: {manager.inventory}")

    except Exception as e:
        logger.error(f"❌ Stock Manager Background-Initialisierung fehlgeschlagen: {e}")
        import traceback

        logger.error(f"❌ Traceback: {traceback.format_exc()}")

        # Fehler-Status im Session-State setzen
        st.session_state["stock_manager_status"] = "failed"
        st.session_state["stock_manager_error"] = str(e)


def get_stock_manager_nonblocking() -> Optional[Any]:
    """
    Non-Blocking Stock Manager Zugriff

    Returns:
        StockManager: Wenn initialisiert und bereit
        None: Wenn noch initialisiert wird oder Fehler aufgetreten ist
    """
    # Status im Session-State verwalten
    if "stock_manager_status" not in st.session_state:
        st.session_state["stock_manager_status"] = "not_initialized"

    if st.session_state["stock_manager_status"] == "not_initialized":
        # Initialisierung starten
        logger.info("🚀 Stock Manager Initialisierung gestartet")
        st.session_state["stock_manager_status"] = "initializing"

        # Hintergrund-Thread starten
        thread = threading.Thread(target=initialize_stock_manager_in_background)
        thread.daemon = True
        thread.start()

        return None

    elif st.session_state["stock_manager_status"] == "initializing":
        # Noch initialisierend
        return None

    elif st.session_state["stock_manager_status"] == "ready":
        # Bereit - Manager zurückgeben
        return st.session_state.get("stock_manager")

    elif st.session_state["stock_manager_status"] == "failed":
        # Fehler aufgetreten
        error = st.session_state.get("stock_manager_error", "Unknown error")
        logger.error(f"❌ Stock Manager nicht verfügbar: {error}")
        return None

    return None


def get_stock_manager_status() -> str:
    """
    Gibt den aktuellen Status des Stock Managers zurück

    Returns:
        str: Status ('not_initialized', 'initializing', 'ready', 'failed')
    """
    return st.session_state.get("stock_manager_status", "not_initialized")


def get_stock_manager_error() -> Optional[str]:
    """
    Gibt die Fehlermeldung zurück, falls der Stock Manager fehlgeschlagen ist

    Returns:
        str: Fehlermeldung oder None
    """
    return st.session_state.get("stock_manager_error")


def reset_stock_manager():
    """Setzt den Stock Manager zurück (für Tests)"""
    if "stock_manager_status" in st.session_state:
        del st.session_state["stock_manager_status"]
    if "stock_manager" in st.session_state:
        del st.session_state["stock_manager"]
    if "stock_manager_error" in st.session_state:
        del st.session_state["stock_manager_error"]
    logger.info("🔄 Stock Manager zurückgesetzt")
