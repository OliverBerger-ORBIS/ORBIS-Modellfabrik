"""
Logging configuration for OMF2 Dashboard
Provides structured logging with consistent formatting and centralized log buffering
"""

import logging
import sys
import threading
from pathlib import Path
from typing import Optional, Deque, Dict
from collections import deque


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger instance for OMF2
    
    Args:
        name: Logger name (typically module name)
        level: Logging level
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Check if root logger has handlers (central buffer is set up)
    root_logger = logging.getLogger()
    has_central_buffer = any(isinstance(h, RingBufferHandler) for h in root_logger.handlers)
    
    if has_central_buffer:
        # Central buffer is active - let logs propagate to root
        logger.propagate = True
        # Don't add local handlers to avoid duplicate console output
    else:
        # No central buffer - configure local handler if needed
        if not logger.handlers:
            # Create handler
            handler = logging.StreamHandler(sys.stdout)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Prevent duplicate logging when no central buffer
            logger.propagate = False
    
    return logger


def setup_file_logging(log_dir: Optional[Path] = None) -> Path:
    """
    Setup file logging for OMF2
    
    Args:
        log_dir: Directory for log files (defaults to logs/ in project root)
    
    Returns:
        Path to log directory
    """
    if log_dir is None:
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
    
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger for file output
    log_file = log_dir / "omf2.log"
    
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    root_logger = logging.getLogger("omf2")
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)
    
    return log_dir


# ============================================================================
# Central Log Buffer Components
# ============================================================================

class MultiLevelRingBufferHandler(logging.Handler):
    """
    Logging-Handler, der für jeden Log-Level einen eigenen Ringbuffer (deque) hält.
    Ermöglicht z.B. Fehler-Logs persistent im Buffer zu halten, auch wenn viele INFO/DEBUG Logs auftreten.
    """
    def __init__(self, buffer_sizes=None):
        super().__init__()
        # Standardgrößen pro Level
        self.buffer_sizes = buffer_sizes or {
            "ERROR": 200,      # Größer für wichtige Errors
            "WARNING": 200,    # Größer für wichtige Warnings  
            "INFO": 500,       # Standard für Info-Logs
            "DEBUG": 300       # Kleinere für Debug-Logs
        }
        self.buffers = {
            level: deque(maxlen=size)
            for level, size in self.buffer_sizes.items()
        }
        self._lock = threading.Lock()

    def emit(self, record):
        msg = self.format(record)
        level = record.levelname
        with self._lock:
            # Füge in passenden Buffer ein, falls Level definiert, sonst in INFO
            self.buffers.get(level, self.buffers["INFO"]).append(msg)

    def get_buffer(self, level=None):
        # Hole Buffer für bestimmtes Level, oder alle als dict
        with self._lock:
            if level:
                return list(self.buffers.get(level, []))
            return {lvl: list(buf) for lvl, buf in self.buffers.items()}


class RingBufferHandler(logging.Handler):
    """
    Legacy RingBufferHandler für Rückwärtskompatibilität.
    
    Logging-Handler, der Logs in einen Ringpuffer schreibt.
    Thread-sicher für MQTT-Callbacks und Streamlit-UI.
    """
    
    def __init__(self, buf: Deque[str], level: int = logging.INFO):
        """
        Initialisiert den Ring-Buffer-Handler.
        
        Args:
            buf: Ringpuffer für Log-Nachrichten
            level: Logging-Level
        """
        super().__init__(level)
        self.buf = buf
    
    def emit(self, record: logging.LogRecord):
        """
        Schreibt Log-Record in den Ringpuffer.
        
        Args:
            record: Log-Record
        """
        try:
            msg = self.format(record)
            self.buf.append(msg)
        except Exception:
            # Ignoriere Fehler beim Logging
            pass


def create_log_buffer(maxlen: int = 1000) -> Deque[str]:
    """
    Erstellt einen neuen Log-Buffer.
    
    Args:
        maxlen: Maximale Anzahl von Log-Nachrichten
    
    Returns:
        Ringpuffer für Log-Nachrichten
    """
    return deque(maxlen=maxlen)


def setup_multilevel_ringbuffer_logging(force_new=False):
    """
    Initialisiert oder erneuert einen MultiLevelRingBufferHandler.
    
    Stellt sicher, dass IMMER genau EIN MultiLevelRingBufferHandler am Root-Logger hängt.
    
    Args:
        force_new: True = alte Handler werden entfernt und ein neuer angehängt.
    
    Returns:
        tuple: (handler, buffers) - Handler-Instanz und Buffer-Dict
    """
    root_logger = logging.getLogger()
    
    # Entferne ALLE alten MultiLevelRingBufferHandler, wenn force_new
    if force_new:
        handlers_to_remove = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
        for h in handlers_to_remove:
            root_logger.removeHandler(h)
            # Log removal for debugging
            logging.debug(f"🔧 Removed old MultiLevelRingBufferHandler from root logger")
    
    # Prüfe, ob jetzt noch einer da ist
    existing = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    
    if existing:
        # Handler existiert bereits - verwende ihn
        handler = existing[0]
        logging.debug(f"✅ Reusing existing MultiLevelRingBufferHandler")
    else:
        # Erstelle neuen Handler
        handler = MultiLevelRingBufferHandler()
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
        logging.debug(f"✅ Created and attached new MultiLevelRingBufferHandler to root logger")
    
    # KRITISCH: Verifiziere, dass Handler tatsächlich am Root-Logger hängt
    handler_attached = handler in root_logger.handlers
    if not handler_attached:
        # Handler ist nicht attached - behebe das Problem
        root_logger.addHandler(handler)
        logging.warning(f"⚠️ Handler was not attached - forced re-attachment to root logger")
    
    # Finale Verifikation
    total_multilevel_handlers = len([h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)])
    if total_multilevel_handlers != 1:
        logging.error(f"❌ FEHLER: {total_multilevel_handlers} MultiLevelRingBufferHandler am Root-Logger (sollte 1 sein)")
    else:
        logging.debug(f"✅ Verification successful: Exactly 1 MultiLevelRingBufferHandler attached to root logger")
    
    return handler, handler.buffers


def setup_level_specific_log_buffers(log_level: int = logging.INFO) -> Dict[str, Deque[str]]:
    """
    Legacy Funktion für Rückwärtskompatibilität.
    Setzt Level-spezifische Log-Buffer auf und gibt sie zurück.
    
    Args:
        log_level: Logging-Level für den Buffer
    
    Returns:
        Dict mit Level-spezifischen Ringpuffern
    """
    # Erstelle Level-spezifische Ringpuffer mit unterschiedlichen Größen
    log_buffers = {
        'ERROR': deque(maxlen=200),      # Größer für wichtige Errors
        'WARNING': deque(maxlen=200),    # Größer für wichtige Warnings  
        'INFO': deque(maxlen=500),       # Standard für Info-Logs
        'DEBUG': deque(maxlen=300)       # Kleinere für Debug-Logs
    }
    
    # Erstelle Handler
    handler = RingBufferHandler(log_buffers['INFO'], log_level)  # Use RingBufferHandler instead
    
    # Erstelle Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Konfiguriere Root-Logger
    root_logger = logging.getLogger()
    
    # Entferne existierende Handler
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
    
    # Füge neuen Handler hinzu
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)
    
    # Konfiguriere OMF2-Logger (nur wenn Level NOTSET ist)
    omf2_loggers = [
        'omf2', 'omf2.ui', 'omf2.admin', 'omf2.ccu', 'omf2.common', 'omf2.nodered',
        'omf2.admin.admin_gateway', 'omf2.admin.admin_mqtt_client',
        'omf2.ccu.ccu_gateway', 'omf2.ccu.ccu_mqtt_client'
    ]
    
    for logger_name in omf2_loggers:
        logger = logging.getLogger(logger_name)
        if logger.level == logging.NOTSET:
            logger.setLevel(log_level)
    
    return log_buffers


def setup_central_log_buffer(
    buffer_size: int = 1000,
    log_level: int = logging.INFO,
    omf2_loggers: Optional[list] = None
) -> tuple[Deque[str], RingBufferHandler]:
    """
    Initialisiert den zentralen Log-Buffer und hängt Handler an relevante Logger.
    
    Args:
        buffer_size: Maximale Größe des Log-Buffers
        log_level: Log-Level für Handler
        omf2_loggers: Liste von Logger-Namen (Standard: alle omf2-Logger)
    
    Returns:
        Tuple aus (log_buffer, ring_buffer_handler)
    """
    # Standard omf2-Logger
    if omf2_loggers is None:
        omf2_loggers = [
            "omf2",
            "omf2.dashboard",
            "omf2.admin",
            "omf2.admin.admin_gateway",
            "omf2.admin.admin_mqtt_client",
            "omf2.ccu.ccu_gateway",
            "omf2.ccu.ccu_mqtt_client",
            "omf2.ui",
            "omf2.common",
            "omf2.ccu",
            "omf2.nodered",
            "omf2.factory",
            "omf2.registry"
        ]
    
    # Log-Buffer erstellen
    log_buffer = create_log_buffer(maxlen=buffer_size)
    
    # RingBufferHandler erstellen
    ring_handler = RingBufferHandler(log_buffer, level=log_level)
    ring_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    
    # Handler an root Logger hängen
    root_logger = logging.getLogger()
    root_logger.addHandler(ring_handler)
    root_logger.setLevel(log_level)
    
    # Alle omf2-Logger konfigurieren
    for logger_name in omf2_loggers:
        logger = logging.getLogger(logger_name)
        # Nur setzen wenn noch nicht explizit gesetzt
        if logger.level == logging.NOTSET:
            logger.setLevel(log_level)
        # Logs propagieren zum root logger (der den RingBufferHandler hat)
        logger.propagate = True
    
    return log_buffer, ring_handler


def get_log_buffer_entries(
    buffer: Deque[str],
    max_lines: int = 200
) -> str:
    """
    Gibt die letzten Log-Einträge aus dem Buffer zurück.
    
    Args:
        buffer: Ringpuffer mit Log-Nachrichten
        max_lines: Maximale Anzahl von Zeilen
    
    Returns:
        Formatierte Log-Nachrichten
    """
    if not buffer:
        return "—"
    
    # Letzte max_lines Zeilen
    recent_logs = list(buffer)[-max_lines:]
    return "\n".join(recent_logs)


def ensure_ringbufferhandler_attached():
    """
    Stellt sicher, dass der MultiLevelRingBufferHandler konsistent am Root-Logger angehängt ist.
    
    Diese Utility-Funktion wird nach jedem Environment-Switch und nach jeder 
    Logging-Konfigurationsänderung aufgerufen, um sicherzustellen, dass:
    1. Der Handler aus dem Session State am Root-Logger hängt
    2. Es nur EINEN MultiLevelRingBufferHandler gibt
    3. Handler- und Buffer-Referenzen im Session State korrekt sind
    
    Returns:
        bool: True wenn Handler erfolgreich attached/verifiziert wurde, False sonst
    """
    try:
        # Import streamlit hier, um Dependencies zu minimieren
        import streamlit as st
        
        # Handler aus Session State holen
        handler = st.session_state.get('log_handler')
        if not handler:
            logging.debug("ℹ️ No log_handler in session state - handler attachment cannot be verified")
            return False
        
        # Root-Logger holen
        root_logger = logging.getLogger()
        
        # Prüfe, ob der Handler aus Session State am Root-Logger hängt
        if handler not in root_logger.handlers:
            # Handler ist nicht attached - re-attach durchführen
            root_logger.addHandler(handler)
            logging.warning("⚠️ MultiLevelRingBufferHandler was detached - re-attached to root logger")
        else:
            logging.debug("✅ MultiLevelRingBufferHandler is correctly attached to root logger")
        
        # KRITISCH: Prüfe, dass nur EINER existiert (keine Duplikate)
        multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
        handler_count = len(multilevel_handlers)
        
        if handler_count > 1:
            # Zu viele Handler - entferne Duplikate, behalte nur den aus Session State
            for h in multilevel_handlers:
                if h is not handler:
                    root_logger.removeHandler(h)
                    logging.warning(f"⚠️ Removed duplicate MultiLevelRingBufferHandler from root logger")
            
            # Verify wieder
            multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
            handler_count = len(multilevel_handlers)
        
        # Finale Verifikation
        if handler_count != 1:
            logging.error(f"❌ FEHLER: {handler_count} MultiLevelRingBufferHandler am Root-Logger (sollte 1 sein)")
            return False
        
        if handler not in root_logger.handlers:
            logging.error(f"❌ FEHLER: Handler aus Session State ist NICHT am Root-Logger attached")
            return False
        
        # Buffers aus Session State aktualisieren (falls noch nicht gesetzt)
        if 'log_buffers' not in st.session_state or st.session_state['log_buffers'] is not handler.buffers:
            st.session_state['log_buffers'] = handler.buffers
            logging.debug("✅ Updated log_buffers in session state to match handler")
        
        logging.debug("✅ Handler attachment verification successful")
        return True
        
    except ImportError:
        # Streamlit nicht verfügbar - ignoriere (z.B. in Unit-Tests)
        logging.debug("ℹ️ Streamlit not available - skipping handler attachment check")
        return False
    except Exception as e:
        logging.error(f"❌ Error ensuring handler attachment: {e}")
        return False