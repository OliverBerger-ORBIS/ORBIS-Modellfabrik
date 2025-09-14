# Logging-System für OMF Dashboard

## 📋 Übersicht

**Zweck:** Thread-sicheres, strukturiertes Logging für OMF Dashboard  
**Basiert auf:** Python `logging` + `structlog` + `rich` (optional)  
**Thread-sicher:** Ja (Queue-basiert für MQTT-Callbacks)  
**Streamlit-kompatibel:** Ja (einmalige Initialisierung, Rerun-fest)

## 🏗️ Architektur

### **1. Fundament: Python `logging`**
- **Queue-basiert:** `QueueHandler` + `QueueListener` für Thread-Sicherheit
- **File-Rotation:** `RotatingFileHandler` für JSON-Logs
- **Console-Output:** `RichHandler` (Dev) oder `StreamHandler` (Prod)

### **2. Strukturierung: `structlog`**
- **JSON-Format:** Maschinenlesbare Logs für Analyse
- **Key-Value-Pairs:** Strukturierte Metadaten
- **Kontext:** Automatische Zeitstempel und Log-Level

### **3. Live-UI: Ring-Buffer**
- **Streamlit-Integration:** Live-Logs im Dashboard
- **Thread-sicher:** `deque` mit fester Größe
- **Performance:** Keine UI-Calls im Handler

## 🔧 Konfiguration

### **Zentrale Initialisierung**

```python
# In omf_dashboard.py
def _init_logging_once():
    """Initialisiert Logging einmal pro Streamlit-Session"""
    if st.session_state.get("_log_init"):
        return

    # 1. Logging konfigurieren
    root, listener = configure_logging(level=20, console_pretty=True)
    st.session_state["_log_listener"] = listener

    # 2. Structlog konfigurieren (optional)
    try:
        configure_structlog()
    except Exception:
        pass

    # 3. Log-Buffer für Live-Logs im Dashboard
    if "log_buffer" not in st.session_state:
        from collections import deque
        from src_orbis.omf.tools.streamlit_log_buffer import RingBufferHandler
        
        # Ring-Buffer erstellen
        buf = deque(maxlen=1000)
        st.session_state.log_buffer = buf
        
        # Ring-Buffer-Handler an Root-Logger anhängen
        rb = RingBufferHandler(buf)
        rb.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        root.addHandler(rb)

    st.session_state["_log_init"] = True
```

### **Logging in Komponenten**

#### **Standard Python Logging:**
```python
import logging
log = logging.getLogger("omf.mqtt")

def _on_message(client, userdata, msg):
    try:
        log.info("mqtt_rx", extra={"topic": msg.topic, "qos": int(msg.qos), "size": len(msg.payload)})
    except Exception:
        pass
```

#### **Strukturiertes Logging (structlog):**
```python
import structlog
log = structlog.get_logger("omf.mqtt")

def _on_message(client, userdata, msg):
    log.info("rx", topic=msg.topic, qos=int(msg.qos), size=len(msg.payload))
```

## 📁 Dateien

### **Konfiguration:**
- **`src_orbis/omf/tools/logging_config.py`** - Zentrale Logging-Konfiguration
- **`src_orbis/omf/tools/structlog_config.py`** - Structlog-Setup
- **`src_orbis/omf/tools/streamlit_log_buffer.py`** - Ring-Buffer-Handler

### **Dashboard-Integration:**
- **`src_orbis/omf/dashboard/omf_dashboard.py`** - `_init_logging_once()`
- **`src_orbis/omf/dashboard/components/logs.py`** - Live-Logs-UI

## 🚨 Regeln

### **R016: Logging-System-Initialisierung**

**Problem:** Logging muss thread-sicher und Streamlit-kompatibel sein

**Lösung:** Queue-basiertes Logging mit einmaliger Initialisierung

#### **Verboten:**
```python
# ❌ FALSCH - Doppelte Initialisierung
def some_function():
    configure_logging()  # Führt zu doppelten Handlern
```

#### **Erlaubt:**
```python
# ✅ RICHTIG - Einmalige Initialisierung
def _init_logging_once():
    if st.session_state.get("_log_init"):
        return
    # ... Logging konfigurieren ...
    st.session_state["_log_init"] = True
```

#### **In MQTT-Callbacks:**
```python
# ✅ RICHTIG - Thread-sichere Logs
def _on_message(client, userdata, msg):
    log.info("message_received", topic=msg.topic, qos=msg.qos)
    # KEINE UI-Operationen hier!
```

## 🔍 Debugging

### **Log-Buffer nicht verfügbar:**
1. **Prüfen:** `st.session_state.get("log_buffer")`
2. **Ursache:** Logging nicht initialisiert
3. **Lösung:** Dashboard neu starten

### **Doppelte Handler:**
1. **Symptom:** Logs erscheinen mehrfach
2. **Ursache:** `configure_logging()` mehrfach aufgerufen
3. **Lösung:** `_init_logging_once()` verwenden

### **Thread-Probleme:**
1. **Symptom:** Logs fehlen oder unvollständig
2. **Ursache:** Direkte Handler statt Queue
3. **Lösung:** `QueueHandler` + `QueueListener` verwenden

## 📊 Log-Formate

### **Console (Rich):**
```
[INFO] omf.mqtt: message_received topic=module/v1/ff/123/state qos=1
```

### **JSON-File:**
```json
{"app": "omf_dashboard", "level": "INFO", "logger": "omf.mqtt", "msg": "message_received", "topic": "module/v1/ff/123/state", "qos": 1, "ts": "2024-01-15T10:30:45.123Z"}
```

### **Live-UI:**
```
2024-01-15 10:30:45,123 [INFO] omf.mqtt: message_received
```

---

**Erstellt:** $(date)  
**Status:** ✅ **AKTIV**  
**Nächste Überprüfung:** Bei Logging-Problemen