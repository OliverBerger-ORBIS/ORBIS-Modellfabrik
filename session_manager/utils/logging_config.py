"""
Thread-sicheres Logging-System für Session Manager
Isolierte Version ohne OMF-Dependencies
"""

from __future__ import annotations

import atexit
import json
import logging
import logging.config
import queue
import sys
from collections import deque
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from pathlib import Path

try:
    from rich.logging import RichHandler  # optional dev-Dependency

    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False


def cleanup_old_logs(log_dir: Path, pattern: str = "session_manager.jsonl*"):
    """
    Löscht alte Log-Dateien beim Neustart der Anwendung.

    Args:
        log_dir: Verzeichnis mit Log-Dateien
        pattern: Glob-Pattern für Log-Dateien
    """
    if not log_dir.exists():
        return

    deleted_count = 0
    for log_file in log_dir.glob(pattern):
        try:
            log_file.unlink()
            deleted_count += 1
        except Exception as e:
            # Ignoriere Fehler beim Löschen (z.B. wenn Datei gerade genutzt wird)
            print(f"Warnung: Konnte Log-Datei {log_file} nicht löschen: {e}", file=sys.stderr)

    if deleted_count > 0:
        print(f"🗑️  {deleted_count} alte Log-Datei(en) gelöscht", file=sys.stderr)


def configure_logging(
    app_name: str = "session_manager",
    level: int = logging.INFO,
    log_dir: str | Path = "logs/session_manager",
    json_file: str = "session_manager.jsonl",
    console_pretty: bool = True,
    ring_buffer: deque[str] | None = None,
    cleanup_on_start: bool = True,
) -> tuple[logging.Logger, QueueListener]:
    """
    Thread-sicheres Logging für Session Manager.

    Args:
        app_name: Name der Anwendung für JSON-Logs
        level: Logging-Level (DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50)
        log_dir: Verzeichnis für Log-Dateien
        json_file: Name der JSON-Log-Datei
        console_pretty: Rich-Konsole verwenden (falls verfügbar)
        ring_buffer: Optional: Deque für Ring-Buffer-Handler (UI-Logs)
        cleanup_on_start: Alte Log-Dateien beim Start löschen

    Returns:
        Tuple von (root_logger, queue_listener)
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Alte Logs löschen wenn gewünscht
    if cleanup_on_start:
        cleanup_old_logs(log_dir, f"{json_file}*")

    # 1) Ziel-Handler (werden am Listener betrieben)
    file_json = RotatingFileHandler(log_dir / json_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    file_json.setLevel(level)
    file_json.setFormatter(logging.Formatter("%(message)s"))  # wir schreiben bereits JSON-Strings

    handlers = [("file_json", file_json)]

    # Ring-Buffer-Handler für UI-Logs hinzufügen wenn bereitgestellt
    if ring_buffer is not None:
        from .streamlit_log_buffer import RingBufferHandler

        ring_handler = RingBufferHandler(ring_buffer, level=level)
        ring_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        handlers.append(("ring_buffer", ring_handler))

    if console_pretty and _HAS_RICH:
        rich = RichHandler(markup=True, show_time=True, show_level=True, show_path=False, rich_tracebacks=True)
        rich.setLevel(level)
        rich.setFormatter(logging.Formatter("%(message)s"))
        handlers.append(("console", rich))
    else:
        cons = logging.StreamHandler(sys.stderr)
        cons.setLevel(level)
        cons.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
        handlers.append(("console", cons))

    # 2) Queue + Listener
    q: queue.Queue = queue.Queue(maxsize=10000)
    qh = QueueHandler(q)
    qh.setLevel(level)

    root = logging.getLogger()
    root.setLevel(level)

    # Wichtig: alte Handler entfernen (Streamlit-Reruns!)
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(qh)

    listener = QueueListener(q, *[h for _, h in handlers], respect_handler_level=True)
    listener.start()
    atexit.register(listener.stop)

    # JSON-Wrapper: root-Logger umschreiben, damit file_json JSON bekommt
    class JsonAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            record = {
                "app": app_name,
                "level": logging.getLevelName(kwargs.get("levelno", kwargs.get("level", root.level))),
                "logger": self.logger.name,
                "msg": msg,
            }
            extra = kwargs.pop("extra", {}) or {}
            record.update(extra)
            # force JSON line
            kwargs["extra"] = {"_json": json.dumps(record, ensure_ascii=False)}
            return "%(_json)s", kwargs

    # Optional convenience method
    logging.Logger.adapter = lambda self: JsonAdapter(self, {})

    # JSON-Formatter für file_json Handler
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            if hasattr(record, "_json"):
                return record._json
            else:
                # Fallback für normale Logs
                record_dict = {
                    "app": app_name,
                    "level": record.levelname,
                    "logger": record.name,
                    "msg": record.getMessage(),
                    "timestamp": self.formatTime(record),
                }
                return json.dumps(record_dict, ensure_ascii=False)

    file_json.setFormatter(JsonFormatter())

    # Störende Logger auf WARNING setzen
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    return root, listener


def get_logger(name: str) -> logging.Logger:
    """Hilfsfunktion um Logger zu erhalten"""
    return logging.getLogger(name)


def init_logging_once(
    session_state: dict, ring_buffer: deque[str] | None = None
) -> tuple[logging.Logger, QueueListener | None]:
    """
    Initialisiert Logging einmal pro Streamlit-Session.

    Args:
        session_state: Streamlit session_state
        ring_buffer: Optional: Deque für Ring-Buffer-Handler (UI-Logs)

    Returns:
        Tuple von (root_logger, queue_listener)
    """
    if session_state.get("_session_manager_log_init"):
        return logging.getLogger(), session_state.get("_session_manager_log_listener")

    # Logging konfigurieren
    root, listener = configure_logging(
        app_name="session_manager",
        level=logging.INFO,
        log_dir="logs/session_manager",
        ring_buffer=ring_buffer,
        cleanup_on_start=True,
        console_pretty=True,
    )

    # Session-State setzen
    session_state["_session_manager_log_init"] = True
    session_state["_session_manager_log_listener"] = listener

    return root, listener
