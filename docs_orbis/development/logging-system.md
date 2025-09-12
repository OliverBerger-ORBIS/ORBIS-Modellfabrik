# Logging-System für OMF Dashboard

## 📋 Übersicht

**Status:** ✅ **VOLLSTÄNDIG IMPLEMENTIERT** - Thread-sicheres Logging für Streamlit

**Zweck:** Strukturierte, auswertbare Logs für OMF Dashboard mit Thread-Sicherheit für MQTT-Callbacks.

## 🏗️ Architektur

### **Kern-Komponenten:**

#### **1. logging_config.py - Zentrale Konfiguration**
- **Thread-sicheres Logging:** Queue + QueueListener für MQTT-Callbacks
- **JSON-Logs:** Strukturierte Logs für Analyse (ELK/Grafana)
- **Rich-Konsole:** Schöne Console-Ausgabe für Entwicklung
- **Streamlit-fest:** Einmalige Initialisierung pro Session

#### **2. structlog_config.py - Strukturierte Logs**
- **JSON-Renderer:** Maschinenlesbare Logs
- **Kontext-Logging:** Strukturierte Metadaten
- **Optional:** Fallback zu stdlib logging

#### **3. streamlit_log_buffer.py - Live-Logs im Dashboard**
- **Ring-Buffer:** Thread-sicherer Puffer für UI
- **Live-Anzeige:** Logs direkt im Dashboard
- **Filter:** Log-Level-Filterung

#### **4. logs.py - Dashboard-Komponente**
- **Live-Logs:** Echtzeit-Anzeige im Dashboard
- **Statistiken:** Log-Level-Zählung
- **Filter:** Debug/Info/Warning/Error-Filter

## 🔧 Implementierte Features

### **✅ Thread-sicheres Logging**
```python
# Queue-basiertes Logging für MQTT-Callbacks
def on_message(client, userdata, msg):
    logger.info("mqtt_rx", extra={
        "topic": msg.topic,
        "qos": int(msg.qos),
        "size": len(msg.payload)
    })
```

### **✅ Strukturierte Logs (JSON)**
```python
# Mit structlog
struct_logger.info("module_state_change",
    module_id="MILL",
    old_state="IDLE",
    new_state="PICKBUSY"
)

# Ergibt JSON:
# {"ts": "2025-01-12T10:30:00Z", "level": "info", "logger": "omf.mqtt", 
#  "msg": "module_state_change", "module_id": "MILL", "old_state": "IDLE", "new_state": "PICKBUSY"}
```

### **✅ Live-Logs im Dashboard**
- **Logs-Tab:** Echtzeit-Anzeige aller Logs
- **Filter:** Nach Log-Level filtern
- **Statistiken:** Anzahl pro Level
- **Auto-Refresh:** Automatische Aktualisierung

### **✅ Log-Rotation**
- **Datei-Größe:** 5MB pro Datei
- **Backup-Count:** 3 Backup-Dateien
- **Verzeichnis:** `data/logs/`

## 🎯 Verwendung

### **1. Standard-Logging**
```python
import logging

logger = logging.getLogger("omf.component_name")

# Einfache Logs
logger.info("Component initialized")
logger.error("Error occurred", extra={"error_code": "E001"})
```

### **2. Strukturierte Logs (structlog)**
```python
import structlog

logger = structlog.get_logger("omf.component_name")

# Strukturierte Logs
logger.info("user_action", 
    action="button_click", 
    component="module_control",
    module_id="MILL"
)
```

### **3. MQTT-Callbacks (Thread-sicher)**
```python
def on_message(client, userdata, msg):
    # Nur Metadaten loggen, keine sensiblen Payloads
    logger.info("mqtt_rx", extra={
        "topic": msg.topic,
        "qos": int(msg.qos),
        "size": len(msg.payload)
    })
```

## 📊 Log-Formate

### **Console-Logs (Rich)**
```
[10:30:00] INFO     omf.mqtt: mqtt_rx topic=module/v1/ff/SVR3QA2098/state qos=1 size=156
[10:30:01] INFO     omf.module_state_manager: module_state_change module_id=MILL old_state=IDLE new_state=PICKBUSY
```

### **JSON-Logs (Datei)**
```json
{"app": "omf_dashboard", "level": "INFO", "logger": "omf.mqtt", "msg": "mqtt_rx", "topic": "module/v1/ff/SVR3QA2098/state", "qos": 1, "size": 156, "ts": "2025-01-12T10:30:00Z"}
{"app": "omf_dashboard", "level": "INFO", "logger": "omf.module_state_manager", "msg": "module_state_change", "module_id": "MILL", "old_state": "IDLE", "new_state": "PICKBUSY", "ts": "2025-01-12T10:30:01Z"}
```

## 🔧 Konfiguration

### **Log-Level setzen**
```python
# In logging_config.py
root, listener = configure_logging(
    level=logging.DEBUG,  # DEBUG=10, INFO=20, WARNING=30, ERROR=40
    console_pretty=True,
    log_dir="data/logs"
)
```

### **Rich-Konsole deaktivieren**
```python
# Für Produktion
root, listener = configure_logging(
    console_pretty=False  # Einfache Console-Ausgabe
)
```

## 🚨 Wichtige Regeln

### **1. Thread-Sicherheit**
- **MQTT-Callbacks:** Immer in separaten Threads
- **Queue-Handler:** Verhindert Lockups
- **Keine UI-Operationen:** In Callbacks niemals `st.rerun()`

### **2. Datenschutz**
- **Keine sensiblen Daten:** Payloads nicht loggen
- **Nur Metadaten:** Topic, QoS, Größe, etc.
- **IDs sind OK:** Module-IDs, Sequenz-IDs, etc.

### **3. Performance**
- **Kurze Logs:** In Callbacks nur essenzielle Infos
- **Asynchrone Verarbeitung:** Queue verhindert Blocking
- **Log-Rotation:** Verhindert zu große Dateien

## 📁 Dateien

### **Implementierung:**
- `src_orbis/omf/tools/logging_config.py` - Zentrale Konfiguration
- `src_orbis/omf/tools/structlog_config.py` - Strukturierte Logs
- `src_orbis/omf/tools/streamlit_log_buffer.py` - Live-Logs
- `src_orbis/omf/tools/mqtt_logging_example.py` - Beispiele

### **Dashboard-Integration:**
- `src_orbis/omf/dashboard/components/logs.py` - Logs-Komponente
- `src_orbis/omf/dashboard/omf_dashboard.py` - Integration

### **Dokumentation:**
- `docs_orbis/development/logging-system.md` - Diese Datei

## 🎯 Nächste Schritte

### **Phase 1: Integration in bestehende Komponenten**
- **ModuleStateManager:** Strukturierte Logs für Sequenz-Events
- **MQTT-Client:** Callback-Logging implementieren
- **Dashboard-Komponenten:** Logging in alle Komponenten

### **Phase 2: Erweiterte Features**
- **Log-Analyse:** Dashboard-Tools für Log-Analyse
- **Alerting:** Automatische Benachrichtigungen bei Errors
- **Metrics:** Log-basierte Metriken

### **Phase 3: Produktions-Features**
- **ELK-Integration:** Logs nach Elasticsearch
- **Grafana-Dashboards:** Log-Visualisierung
- **Alert-Management:** Automatische Alerts

---

**Erstellt:** $(date)
**Status:** ✅ **VOLLSTÄNDIG IMPLEMENTIERT**
**Nächster Schritt:** Integration in bestehende Komponenten
