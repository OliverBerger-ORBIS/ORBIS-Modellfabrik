#!/usr/bin/env python3
"""
Non-Blocking Order Manager Initialisierung für Streamlit
Implementierung der GitHub Copilot-Lösung für Singleton-Initialisierung
"""

import threading
import streamlit as st
from typing import Optional, Dict, Any
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def initialize_order_manager_in_background():
    """Initialisiert den Order Manager im Hintergrund-Thread"""
    try:
        logger.info("🔄 Order Manager Background-Initialisierung gestartet")
        
        # Import hier um zirkuläre Imports zu vermeiden
        from omf2.ccu.order_manager import OrderManager
        
        # Order Manager erstellen
        manager = OrderManager()
        
        # Status im Session-State aktualisieren
        st.session_state['order_manager_status'] = 'ready'
        st.session_state['order_manager'] = manager
        
        logger.info("✅ Order Manager Background-Initialisierung erfolgreich")
        logger.info(f"🏗️ Order Manager Inventory: {manager.inventory}")
        
    except Exception as e:
        logger.error(f"❌ Order Manager Background-Initialisierung fehlgeschlagen: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        
        # Fehler-Status im Session-State setzen
        st.session_state['order_manager_status'] = 'failed'
        st.session_state['order_manager_error'] = str(e)


def get_order_manager_nonblocking() -> Optional[Any]:
    """
    Non-Blocking Order Manager Zugriff
    
    Returns:
        OrderManager: Wenn initialisiert und bereit
        None: Wenn noch initialisiert wird oder Fehler aufgetreten ist
    """
    # Status im Session-State verwalten
    if 'order_manager_status' not in st.session_state:
        st.session_state['order_manager_status'] = 'not_initialized'
    
    if st.session_state['order_manager_status'] == 'not_initialized':
        # Initialisierung starten
        logger.info("🚀 Order Manager Initialisierung gestartet")
        st.session_state['order_manager_status'] = 'initializing'
        
        # Hintergrund-Thread starten
        thread = threading.Thread(target=initialize_order_manager_in_background, daemon=True)
        thread.start()
        st.session_state['order_manager_thread'] = thread
        
        return None  # Noch nicht bereit
        
    elif st.session_state['order_manager_status'] == 'initializing':
        return None  # Noch nicht bereit
        
    elif st.session_state['order_manager_status'] == 'ready':
        return st.session_state['order_manager']
        
    elif st.session_state['order_manager_status'] == 'failed':
        return None  # Fehlerbehandlung im UI


def get_order_manager_status() -> str:
    """Gibt den aktuellen Order Manager Status zurück"""
    return st.session_state.get('order_manager_status', 'not_initialized')


def get_order_manager_error() -> Optional[str]:
    """Gibt den Order Manager Fehler zurück (falls vorhanden)"""
    return st.session_state.get('order_manager_error', None)


def reset_order_manager():
    """Setzt den Order Manager Status zurück (für Retry)"""
    logger.info("🔄 Order Manager Status zurückgesetzt")
    
    # Session-State zurücksetzen
    if 'order_manager_status' in st.session_state:
        del st.session_state['order_manager_status']
    if 'order_manager' in st.session_state:
        del st.session_state['order_manager']
    if 'order_manager_error' in st.session_state:
        del st.session_state['order_manager_error']
    if 'order_manager_thread' in st.session_state:
        del st.session_state['order_manager_thread']


def get_inventory_status_nonblocking() -> Optional[Dict[str, Any]]:
    """
    Non-Blocking Inventory Status Abruf
    
    Returns:
        Dict: Inventory Status wenn Order Manager bereit
        None: Wenn Order Manager noch nicht bereit ist
    """
    order_manager = get_order_manager_nonblocking()
    
    if order_manager is None:
        return None
    
    try:
        return order_manager.get_inventory_status()
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen des Inventory Status: {e}")
        return None


def get_available_workpieces_nonblocking() -> Optional[Dict[str, int]]:
    """
    Non-Blocking Available Workpieces Abruf
    
    Returns:
        Dict: Available Workpieces wenn Order Manager bereit
        None: Wenn Order Manager noch nicht bereit ist
    """
    order_manager = get_order_manager_nonblocking()
    
    if order_manager is None:
        return None
    
    try:
        return order_manager.get_available_workpieces()
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der Available Workpieces: {e}")
        return None


def get_workpiece_need_nonblocking() -> Optional[Dict[str, int]]:
    """
    Non-Blocking Workpiece Need Abruf
    
    Returns:
        Dict: Workpiece Need wenn Order Manager bereit
        None: Wenn Order Manager noch nicht bereit ist
    """
    order_manager = get_order_manager_nonblocking()
    
    if order_manager is None:
        return None
    
    try:
        return order_manager.get_workpiece_need()
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen des Workpiece Need: {e}")
        return None
