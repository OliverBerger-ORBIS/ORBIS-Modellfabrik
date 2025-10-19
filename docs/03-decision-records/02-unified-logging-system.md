# Decision Record: Einheitliches Logging-System

**Datum:** 2024-12-19  
**Status:** Accepted  
**Letzte Aktualisierung:** 2025-01-17  
**Kontext:** Das OMF-Dashboard benötigt ein einheitliches, strukturiertes Logging-System für alle Komponenten mit JSON-Formatierung und zentraler Konfiguration.

---

## Entscheidung

Verwendung des **OMF-Logging-Systems** mit JSON-Formatierung, zentraler Konfiguration und einheitlichen Logger-Instanzen.

```python
# Logging-Konfiguration
def configure_logging(level=logging.INFO):
    # Störende Logger auf WARNING setzen
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    # JSON-Formatierung für strukturierte Logs
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            return json.dumps(record_dict, ensure_ascii=False)

# Verwendung in Komponenten
from omf.dashboard.tools.logging_config import get_logger
logger = get_logger("omf.dashboard.component_name")
logger.info("📤 MQTT Publish: topic → payload")
```

## Konsequenzen

### Positiv:
- **Strukturierte Logs:** JSON-Format für bessere Analyse
- **Zentrale Konfiguration:** Ein Ort für alle Logger-Einstellungen
- **Thread-Sicherheit:** Queue-basiertes Logging
- **Filterung:** Störende DEBUG-Ausgaben unterdrückt
- **Konsistenz:** Einheitliche Log-Formatierung

### Negativ:
- **Komplexität:** Zusätzliche Abstraktionsebene
- **Performance:** JSON-Serialisierung Overhead

## Implementierung

### Version 3.0 (2025-01-17)
- [x] **QueueListener Integration** - Thread-safe RingBuffer über QueueListener
- [x] **Zentrale Logging-Konfiguration** - `configure_logging_with_ringbuffer()`
- [x] **Automatic Log Cleanup** - Alte Log-Dateien werden automatisch gelöscht
- [x] **Optimierte Log-Level** - Business-Manager von DEBUG auf INFO optimiert
- [x] **100% Log-Capture** - Alle MQTT-Callbacks erreichen Filesystem

### Version 2.0 (2024-12-19)
- [x] `logging_config.py` mit JSON-Formatter
- [x] PIL/Pillow Logger auf WARNING gesetzt
- [x] `get_logger()` Funktion für Komponenten
- [x] MQTT-Publish-Logging in `omf_mqtt_client.py`
- [x] Thread-sichere Queue-basierte Handler

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
