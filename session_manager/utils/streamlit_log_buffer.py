"""
Streamlit Log Buffer für Live-Logs im Dashboard

Ermöglicht die Anzeige von Logs direkt im Streamlit-UI.
"""

import logging
from collections import deque


class RingBufferHandler(logging.Handler):
    """
    Logging-Handler, der Logs in einen Ringpuffer schreibt.

    Thread-sicher für MQTT-Callbacks und Streamlit-UI.
    """

    def __init__(self, buf: deque[str], level: int = logging.INFO):
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


def create_log_buffer(maxlen: int = 1000) -> deque[str]:
    """
    Erstellt einen neuen Log-Buffer.

    Args:
        maxlen: Maximale Anzahl von Log-Nachrichten

    Returns:
        Ringpuffer für Log-Nachrichten
    """
    return deque(maxlen=maxlen)


def add_buffer_handler(logger: logging.Logger, buffer: deque[str], level: int = logging.INFO):
    """
    Fügt einen Ring-Buffer-Handler zu einem Logger hinzu.

    Args:
        logger: Logger
        buffer: Ringpuffer
        level: Logging-Level
    """
    handler = RingBufferHandler(buffer, level)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


def render_logs_panel(buffer: deque[str], max_lines: int = 200) -> str:
    """
    Rendert Logs für Streamlit-UI.

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
