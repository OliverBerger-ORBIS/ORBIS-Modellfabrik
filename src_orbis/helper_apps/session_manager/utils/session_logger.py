"""
SessionManagerLogger - Session-spezifisches Logging-System

Basiert auf PR1 Konzepten für strukturierte, Session-spezifische Log-Ausgabe.
"""

import logging
import logging.handlers
from pathlib import Path


class SessionManagerLogger:
    """
    Session-spezifischer Logger für Session Manager Komponenten.

    Features:
    - Session-spezifische Log-Dateien
    - Strukturierte Log-Ausgabe mit Session-Kontext
    - RotatingFileHandler für automatische Log-Rotation
    - Konsistente Formatierung
    """

    def __init__(self, session_name: str, log_dir: str = "data/logs"):
        """
        Args:
            session_name: Name der Session (z.B. "session_analysis", "replay_station")
            log_dir: Verzeichnis für Log-Dateien
        """
        self.session_name = session_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Logger-Name mit Session-Kontext
        self.logger_name = f"session_manager.{session_name}"
        self.base_logger = logging.getLogger(self.logger_name)

        # Verhindere doppelte Handler
        if not self.base_logger.handlers:
            self._setup_handlers()

        # Logger-Adapter mit Session-Kontext
        self.logger = logging.LoggerAdapter(self.base_logger, {'session_name': session_name})

    def _setup_handlers(self):
        """Setup Logging-Handler für Session-spezifische Logs"""

        # 1. FileHandler mit Session-spezifischem Namen
        log_file = self.log_dir / f"session_manager_{self.session_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'  # 10MB
        )

        # 2. StreamHandler für Console-Output
        console_handler = logging.StreamHandler()

        # 3. Formatter mit Session-Kontext
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(session_name)s] - %(message)s')

        # 4. Handler konfigurieren
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 5. Handler hinzufügen
        self.base_logger.addHandler(file_handler)
        self.base_logger.addHandler(console_handler)

        # 6. Level setzen
        self.base_logger.setLevel(logging.INFO)

    def get_logger(self) -> logging.LoggerAdapter:
        """Gibt den konfigurierten Logger zurück"""
        return self.logger

    def set_level(self, level: int):
        """Setzt das Logging-Level"""
        self.base_logger.setLevel(level)

    def get_log_file_path(self) -> Path:
        """Gibt den Pfad zur Log-Datei zurück"""
        return self.log_dir / f"session_manager_{self.session_name}.log"

    def cleanup_old_logs(self, keep_days: int = 7):
        """Bereinigt alte Log-Dateien (älter als keep_days Tage)"""
        import time

        cutoff_time = time.time() - (keep_days * 24 * 60 * 60)

        for log_file in self.log_dir.glob(f"session_manager_{self.session_name}*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                self.logger.info(f"🗑️ Alte Log-Datei gelöscht: {log_file.name}")


def get_session_logger(session_name: str, log_dir: str = "data/logs") -> SessionManagerLogger:
    """
    Factory-Funktion für SessionManagerLogger.

    Args:
        session_name: Name der Session
        log_dir: Verzeichnis für Log-Dateien

    Returns:
        SessionManagerLogger-Instanz
    """
    return SessionManagerLogger(session_name, log_dir)


# Globale Logger-Instanzen für Session Manager Komponenten
_session_loggers = {}


def get_session_logger_cached(session_name: str) -> logging.LoggerAdapter:
    """
    Gibt einen gecachten Session-Logger zurück.

    Args:
        session_name: Name der Session

    Returns:
        LoggerAdapter mit Session-Kontext
    """
    if session_name not in _session_loggers:
        _session_loggers[session_name] = get_session_logger(session_name)

    return _session_loggers[session_name].get_logger()


# Convenience-Funktionen für häufige Session-Namen
def get_analysis_logger() -> logging.LoggerAdapter:
    """Logger für Session Analysis"""
    return get_session_logger_cached("analysis")


def get_replay_logger() -> logging.LoggerAdapter:
    """Logger für Replay Station"""
    return get_session_logger_cached("replay")


def get_recorder_logger() -> logging.LoggerAdapter:
    """Logger für Session Recorder"""
    return get_session_logger_cached("recorder")


def get_template_logger() -> logging.LoggerAdapter:
    """Logger für Template Analysis"""
    return get_session_logger_cached("template")


def get_settings_logger() -> logging.LoggerAdapter:
    """Logger für Settings"""
    return get_session_logger_cached("settings")
