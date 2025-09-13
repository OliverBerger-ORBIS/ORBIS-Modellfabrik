#!/usr/bin/env python3
"""
Central Logging Utilities für Session Manager
Implementiert ein wiederverwendbares, konfigurierbares Logging-Setup
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class SessionManagerLogger:
    """Zentraler Logger für Session Manager mit konfigurierbaren Ausgaben"""

    def __init__(self, name: str = "session_manager", log_level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        # Handle invalid log levels gracefully
        try:
            self.log_level = getattr(logging, log_level.upper())
        except AttributeError:
            self.log_level = logging.INFO  # Default fallback
        self._setup_logger()

    def _setup_logger(self):
        """Logger-Setup mit File- und Console-Handler"""
        # Verhindere doppelte Handler
        if self.logger.handlers:
            return

        self.logger.setLevel(self.log_level)

        # Formatter für strukturierte Logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

        # Console Handler - nur für WARNING und höher
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File Handler - alle Events
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"{self.name}.log"

        file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)  # 10MB
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """Logger-Instanz zurückgeben"""
        return self.logger

    def log_event(self, message: str, level: str = "INFO", **kwargs):
        """Event mit optionalen Kontext-Daten loggen"""
        log_func = getattr(self.logger, level.lower())
        if kwargs:
            message = f"{message} - Context: {kwargs}"
        log_func(message)

    def log_ui_action(self, action: str, user_context: Optional[dict] = None):
        """UI-Aktionen spezifisch loggen"""
        context = user_context or {}
        self.log_event(f"UI Action: {action}", "INFO", **context)

    def log_rerun_trigger(self, reason: str, source: str):
        """Rerun-Events spezifisch loggen"""
        self.log_event(f"Rerun triggered: {reason} from {source}", "INFO")

    def log_error(self, error: Exception, context: Optional[str] = None):
        """Fehler mit Kontext loggen"""
        error_msg = f"Error: {str(error)}"
        if context:
            error_msg = f"{error_msg} - Context: {context}"
        self.logger.error(error_msg, exc_info=True)

    def log_warning(self, message: str, **kwargs):
        """Warnungen loggen"""
        self.log_event(message, "WARNING", **kwargs)


# Globale Logger-Instanz für einfache Nutzung
_default_logger = None


def get_session_logger(name: str = "session_manager", log_level: str = "INFO") -> SessionManagerLogger:
    """Zentrale Funktion zum Abrufen des Session-Loggers"""
    global _default_logger
    if _default_logger is None:
        _default_logger = SessionManagerLogger(name, log_level)
    return _default_logger


def configure_logging(log_level: str = "INFO", log_to_console: bool = True):
    """Globale Logging-Konfiguration"""
    global _default_logger
    _default_logger = SessionManagerLogger("session_manager", log_level)
    return _default_logger.get_logger()
