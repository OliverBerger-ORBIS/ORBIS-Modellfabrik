"""
Logging configuration for OMF2 Dashboard
Provides structured logging with consistent formatting and centralized log buffering
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Deque
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
    
    # Only configure if not already configured
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
        logger.setLevel(level)
        
        # Prevent duplicate logging
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

class RingBufferHandler(logging.Handler):
    """
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