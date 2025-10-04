# OMF2 Logging Configuration

## 🎯 Übersicht

Das OMF2 Dashboard verwendet ein **zentrales Logging-System** mit konfigurierbaren Log-Leveln. Du kannst die Logging-Konfiguration einfach über die YAML-Datei oder Python-Funktionen anpassen.

## 📁 Konfigurationsdateien

- **`omf2/config/logging_config.yml`** - Hauptkonfigurationsdatei
- **`omf2/common/logging_config.py`** - Python-Konfigurationsfunktionen

## ⚙️ Logging konfigurieren

### 1. YAML-Konfiguration (Empfohlen)

Bearbeite `omf2/config/logging_config.yml`:

```yaml
# Global logging configuration
global:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  buffer_size: 1000
  file_logging: true

# Module-specific logging levels
modules:
  omf2.ccu:
    level: DEBUG  # Set to DEBUG for detailed CCU debugging

# Business Manager specific logging
business_managers:
  sensor_manager:
    level: DEBUG  # Set to DEBUG for sensor data debugging
  module_manager:
    level: DEBUG  # Set to DEBUG for module status debugging

# MQTT Client logging
mqtt_clients:
  ccu_mqtt_client:
    level: DEBUG  # Set to DEBUG for MQTT message debugging
```

### 2. Python-Funktionen (Programmatisch)

```python
from omf2.common.logging_config import *

# Debug-Modus für alle Module aktivieren
enable_debug_logging()

# Debug-Modus für spezifische Module
enable_sensor_debug()      # Sensor-Manager
enable_module_debug()      # Module-Manager  
enable_mqtt_debug()        # MQTT-Clients

# Debug-Modus deaktivieren
disable_debug_logging()

# Aktuelle Log-Level anzeigen
levels = get_current_log_levels()
print(levels)
```

## 🔧 Häufige Konfigurationen

### Sensor-Daten debuggen
```yaml
business_managers:
  sensor_manager:
    level: DEBUG
```

### Module-Status debuggen
```yaml
business_managers:
  module_manager:
    level: DEBUG
```

### MQTT-Messages debuggen
```yaml
mqtt_clients:
  ccu_mqtt_client:
    level: DEBUG
```

### Alles debuggen
```yaml
global:
  level: DEBUG
```

## 📊 Log-Viewer

Das System Logs Tab in der Admin-UI zeigt alle Logs an:
- **Log History** - Letzte Log-Einträge
- **Log Search** - Logs durchsuchen
- **Log Analytics** - Log-Statistiken

## 🚨 Wichtig

- **DEBUG-Level** erzeugt viele Logs - nur bei Bedarf aktivieren
- **INFO-Level** ist der Standard für normale Nutzung
- Logs werden im **zentralen Buffer** gespeichert (1000 Einträge)
- **File-Logging** ist standardmäßig aktiviert

## 🔄 Änderungen anwenden

1. **YAML-Datei bearbeiten** → Dashboard neu starten
2. **Python-Funktionen** → Sofort wirksam (während Laufzeit)

## 📝 Beispiel-Konfigurationen

### Minimal (wenig Logs)
```yaml
global:
  level: WARNING
```

### Normal (Standard)
```yaml
global:
  level: INFO
```

### Debug (viele Logs)
```yaml
global:
  level: DEBUG
```

### Gemischt (nur bestimmte Module debuggen)
```yaml
global:
  level: INFO
business_managers:
  sensor_manager:
    level: DEBUG
```
