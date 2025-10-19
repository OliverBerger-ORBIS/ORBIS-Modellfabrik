# Decision Record: Einheitliches Logging-System

**Datum:** 2024-12-19  
**Status:** Accepted  
**Letzte Aktualisierung:** 2025-01-17  
**Kontext:** Das OMF2-Dashboard benötigt ein einheitliches, thread-sicheres Logging-System für alle Komponenten mit zentraler Konfiguration, automatischer Bereinigung und 100% Log-Capture.

---

## Entscheidung

Verwendung des **OMF2-Logging-Systems** mit thread-sicherer RingBuffer-Integration, zentraler Konfiguration und automatischer Log-Bereinigung.

```python
# Zentrale Logging-Initialisierung (omf2/omf.py)
from omf2.common.logger import setup_multilevel_ringbuffer_logging, ensure_ringbufferhandler_attached

# RingBuffer über QueueListener (thread-safe)
handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
st.session_state["log_handler"] = handler
st.session_state["log_buffers"] = buffers
ensure_ringbufferhandler_attached()

# Verwendung in Komponenten
from omf2.common.logger import get_logger
logger = get_logger("omf2.component_name")
logger.info("📤 MQTT Publish: topic → payload")
```

## Konsequenzen

### Positiv:
- **Thread-Sicherheit:** RingBuffer über QueueListener für MQTT-Callbacks
- **100% Log-Capture:** Alle Logs erreichen Filesystem und RingBuffer
- **Automatische Bereinigung:** Alte Log-Dateien werden beim Start gelöscht
- **Multi-Level Buffering:** Separate Buffer für ERROR, WARNING, INFO, DEBUG
- **Zentrale Konfiguration:** YAML-basierte Log-Level-Konfiguration
- **Handler-Persistenz:** Automatische Wiederherstellung nach Environment-Switch
- **Disk Space Management:** ~14MB → 8KB durch automatische Bereinigung

### Negativ:
- **Komplexität:** Multi-Level RingBuffer und Handler-Management
- **Memory Usage:** RingBuffer hält Logs im Speicher

## Implementierung

### Version 3.0 (2025-01-17) - Thread-Safe RingBuffer Integration
- [x] **MultiLevelRingBufferHandler** - Separate Buffer für jeden Log-Level
- [x] **QueueListener Integration** - Thread-safe RingBuffer über QueueListener
- [x] **Handler-Persistenz** - `ensure_ringbufferhandler_attached()` für Session State
- [x] **Automatic Log Cleanup** - `cleanup_old_logs()` beim Start
- [x] **YAML-Konfiguration** - `omf2/config/logging_config.yml` für Log-Level
- [x] **SafeRotatingFileHandler** - Thread-safe File-Handling mit Error-Recovery
- [x] **100% Log-Capture** - Alle MQTT-Callbacks erreichen Filesystem und RingBuffer

### Version 2.0 (2024-12-19) - Legacy System
- [x] `logging_config.py` mit JSON-Formatter
- [x] PIL/Pillow Logger auf WARNING gesetzt
- [x] `get_logger()` Funktion für Komponenten
- [x] MQTT-Publish-Logging in `omf_mqtt_client.py`
- [x] Thread-sichere Queue-basierte Handler

## Architektur

### Zentrale Komponenten

#### 1. **MultiLevelRingBufferHandler** (`omf2/common/logger.py`)
```python
class MultiLevelRingBufferHandler(logging.Handler):
    """Logging-Handler mit separaten Ringbuffern für jeden Log-Level"""
    
    def __init__(self, buffer_sizes=None):
        self.buffers = {
            "ERROR": deque(maxlen=200),
            "WARNING": deque(maxlen=200), 
            "INFO": deque(maxlen=500),
            "DEBUG": deque(maxlen=300)
        }
```

#### 2. **Automatische Log-Bereinigung** (`omf2/omf.py`)
```python
def cleanup_old_logs():
    """Löscht alte Log-Dateien bei Start für saubere Agent-Analyse"""
    log_dir = Path(__file__).parent.parent / "logs"
    for log_file in log_dir.glob("omf2.log*"):
        log_file.unlink()
```

#### 3. **Handler-Persistenz** (`omf2/common/logger.py`)
```python
def ensure_ringbufferhandler_attached():
    """Stellt sicher, dass RingBufferHandler konsistent am Root-Logger hängt"""
    handler = st.session_state.get("log_handler")
    if handler not in root_logger.handlers:
        root_logger.addHandler(handler)
```

### Konfiguration

#### YAML-Konfiguration (`omf2/config/logging_config.yml`)
```yaml
global:
  level: INFO
  buffer_size: 1000
  file_logging: true

modules:
  omf2: {level: INFO}
  omf2.ccu: {level: INFO}
  omf2.admin: {level: INFO}

business_managers:
  sensor_manager: {level: INFO}
  module_manager: {level: INFO}

ringbuffer:
  ERROR: 200
  WARNING: 200
  INFO: 500
  DEBUG: 300
```

### Verwendung

#### Logger-Initialisierung
```python
from omf2.common.logger import get_logger
logger = get_logger("omf2.component_name")
logger.info("📤 MQTT Publish: topic → payload")
```

#### Log-Level-Konfiguration
```python
from omf2.common.logging_config import update_logging_config
update_logging_config("omf2.ccu.sensor_manager", "DEBUG")
```

## Testing

### Test-Coverage
- **9 Tests** in `test_logging_cleanup.py`
- **Handler-Persistenz** Tests
- **Thread-Safety** Tests
- **CodeQL Security Scan:** 0 alerts

### Verifikation
- ✅ **Disk Space:** ~14MB → 8KB durch automatische Bereinigung
- ✅ **Log-Capture:** 100% aller MQTT-Callbacks erreichen Filesystem
- ✅ **Thread-Safety:** RingBuffer über QueueListener
- ✅ **Handler-Persistenz:** Automatische Wiederherstellung nach Environment-Switch

---

*Entscheidung getroffen von: OMF-Entwicklungsteam*
