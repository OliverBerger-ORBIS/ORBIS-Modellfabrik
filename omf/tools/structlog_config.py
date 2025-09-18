"""
Structlog-Konfiguration für strukturierte Logs

Bietet strukturierte, JSON-basierte Logs für bessere Analyse und Monitoring.
"""

from typing import Optional

import structlog

def configure_structlog() -> Optional[structlog.BoundLogger]:
    """
    Konfiguriert structlog für strukturierte Logs.

    Returns:
        structlog logger oder None falls nicht verfügbar
    """
    try:
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", key="ts"),
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(ensure_ascii=False),  # ergibt JSON-Dict
            ],
            context_class=dict,
            wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO
            cache_logger_on_first_use=True,
        )
        return structlog.get_logger()
    except ImportError:
        return None

def get_structlog_logger(name: str = "omf") -> structlog.BoundLogger:
    """
    Gibt einen strukturierten Logger zurück.

    Args:
        name: Name des Loggers

    Returns:
        structlog logger
    """
    try:
        return structlog.get_logger(name)
    except Exception:
        # Fallback zu stdlib logging
        import logging

        return logging.getLogger(name)
