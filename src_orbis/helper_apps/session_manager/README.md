# Session Manager

Session Manager implementiert zwei wesentliche Verbesserungen für Streamlit-Apps:

1. **Kontrolliertes st.rerun() Handling**
2. **Zentrales Logging-Konzept**

## 🎯 Übersicht

Das Session Manager Package stellt wiederverwendbare Komponenten zur Verfügung, die in jeder Streamlit-App eingesetzt werden können, um die Kontrolle über Reruns zu verbessern und ein professionelles Logging-System zu implementieren.

## 📁 Struktur

```
session_manager/
├── __init__.py                 # Package exports
├── logging_utils.py            # Zentrales Logging-System
├── rerun_control.py           # Kontrolliertes st.rerun() Handling
├── session_manager_dashboard.py # Demo-App
├── replay_station_improved.py # Beispiel-Integration
└── README.md                  # Diese Dokumentation
```

## 🔄 Kontrolliertes st.rerun() Handling

### Problem
- Unkontrollierte `st.rerun()` Aufrufe führen zu Rerun-Kaskaden
- Mehrfache oder unnötige Reruns verschlechtern die Performance
- Kein Feedback für User, warum ein Rerun ausgelöst wird

### Lösung
Das `RerunController` System implementiert:

- **Flag-basierte Kontrolle**: `st.session_state["needs_rerun"]` als zentrales Flag
- **Rerun-Kaskaden-Verhinderung**: Nur ein Rerun pro Zyklus
- **UI-Feedback**: User sieht, warum ein Rerun ausgelöst wird
- **Nachvollziehbarkeit**: Grund und Quelle jedes Reruns werden geloggt

### Verwendung

```python
from src_orbis.helper_apps.session_manager import request_rerun, execute_pending_rerun

# Am Anfang jeder Streamlit-App
execute_pending_rerun()

# Statt st.rerun() verwenden:
if st.button("Increment"):
    counter += 1
    request_rerun("Counter wurde erhöht", "increment_button")
```

### API

```python
# Rerun anfordern
request_rerun(reason: str, source: str = "unknown", show_ui_feedback: bool = True)

# Anstehende Reruns ausführen (am App-Anfang)
execute_pending_rerun() -> bool

# Controller-Instanz für erweiterte Kontrolle
controller = get_rerun_controller()
controller.clear_rerun_request()  # Rerun-Anfrage löschen
controller.is_rerun_pending()     # Status prüfen
```

## 📋 Zentrales Logging-Konzept

### Problem
- Streamlit-Apps haben oft nur print() oder st.write() für Debugging
- Keine Trennung zwischen User-UI und Developer-Logs
- Logs gehen verloren oder sind schwer zu analysieren

### Lösung
Das `SessionManagerLogger` System implementiert:

- **Strukturierte Logs**: Alle Events mit Timestamp, Kontext und Metadaten
- **Separate Ausgaben**: Konsole (Warnings/Errors) + Datei (alle Events)
- **Rottierende Log-Dateien**: 10MB mit 5 Backup-Dateien
- **Konfigurierbare Log-Level**: DEBUG, INFO, WARNING, ERROR
- **Wiederverwendbar**: Einfache Integration in bestehende Apps

### Verwendung

```python
from src_orbis.helper_apps.session_manager import get_session_logger

logger = get_session_logger("my_app", "INFO")

# Standard Events
logger.log_event("User logged in", "INFO", user_id=123)

# UI-Aktionen
logger.log_ui_action("button_click", {"button": "submit", "form_data": data})

# Rerun-Events (automatisch durch RerunController)
logger.log_rerun_trigger("data_updated", "load_button")

# Fehler mit Kontext
try:
    risky_operation()
except Exception as e:
    logger.log_error(e, "Failed during data processing")

# Warnungen
logger.log_warning("Session timeout approaching", remaining_time=300)
```

### Log-Ausgabe

**Datei** (`logs/session_manager.log`):
```
2024-01-15 10:30:45 - session_manager - INFO - main:123 - UI Action: button_click - Context: {'button': 'submit'}
2024-01-15 10:30:46 - session_manager - INFO - rerun_control:45 - Rerun triggered: data_updated from load_button
2024-01-15 10:30:47 - session_manager - WARNING - logging_utils:78 - Session timeout approaching - Context: {'remaining_time': 300}
```

**Konsole** (nur Warnings/Errors):
```
2024-01-15 10:30:47 - session_manager - WARNING - Session timeout approaching
```

## 🚀 Integration in bestehende Apps

### Schritt 1: Imports hinzufügen
```python
from src_orbis.helper_apps.session_manager import (
    get_session_logger,
    get_rerun_controller, 
    request_rerun,
    execute_pending_rerun
)
```

### Schritt 2: Logger initialisieren
```python
logger = get_session_logger("my_app_name", "INFO")
logger.log_event("App started", "INFO")
```

### Schritt 3: Rerun-Handling
```python
def main():
    # WICHTIG: Am Anfang jeder App
    execute_pending_rerun()
    
    # App-Logik...
    
    if st.button("Action"):
        # Aktion ausführen
        perform_action()
        
        # Statt st.rerun()
        request_rerun("Action completed", "action_button")
```

### Schritt 4: st.rerun() ersetzen
```python
# Vorher:
if st.button("Load Data"):
    load_data()
    st.rerun()  # ❌ Unkontrolliert

# Nachher:
if st.button("Load Data"):
    load_data()
    logger.log_ui_action("data_load_requested")
    request_rerun("Data loaded", "load_button")  # ✅ Kontrolliert
```

## 📊 Demo-Apps

### session_manager_dashboard.py
Vollständige Demo-App die beide Konzepte demonstriert:
- Counter mit kontrolliertem Rerun
- Live Log-Datei Viewer
- Session-Status Anzeige
- Rerun-Status Monitoring

### replay_station_improved.py
Zeigt Integration in bestehende App (Replay Station):
- Ersetzt alle `st.rerun()` Aufrufe
- Fügt detailliertes Logging hinzu
- Behält bestehende Funktionalität bei

## 🧪 Tests

Umfassendes Test-Suite mit 20 Tests:
```bash
python -m pytest tests_orbis/test_helper_apps/test_session_manager.py -v
```

Tests abdecken:
- Logger-Initialisierung und Konfiguration
- File und Console Handler
- Rerun-Controller Flag-Management
- Rerun-Kaskaden-Verhinderung
- Error-Handling
- Integration-Workflows

## 🔧 Konfiguration

### Logging-Level anpassen
```python
# Global konfigurieren
configure_logging(log_level="DEBUG", log_to_console=True)

# Oder pro Logger
logger = SessionManagerLogger("my_app", "DEBUG")
```

### Log-Datei-Pfad
Logs werden standardmäßig in `logs/` erstellt. Das Verzeichnis wird automatisch angelegt.

### Rerun-Feedback deaktivieren
```python
request_rerun("reason", "source", show_ui_feedback=False)
```

## 💡 Best Practices

### Rerun-Kontrolle
1. **Immer** `execute_pending_rerun()` am App-Anfang aufrufen
2. **Nie** direktes `st.rerun()` verwenden
3. **Aussagekräftige** Gründe und Quellen angeben
4. **UI-Feedback** für User-Aktionen aktivieren

### Logging
1. **Strukturierte** Kontext-Daten verwenden
2. **Angemessene** Log-Level wählen (INFO für normale Events, WARNING für Probleme)
3. **Sensible Daten** nicht loggen
4. **Konsistente** Logger-Namen verwenden

### Performance
1. **Log-Level** in Produktion auf INFO oder WARNING setzen
2. **Große Datenstrukturen** nicht vollständig loggen
3. **Rerun-Anfragen** nur bei tatsächlichen Änderungen

## 🔮 Erweiterbarkeit

Das modulare Design ermöglicht einfache Erweiterungen:

- **Monitoring-Tab**: Live-Überwachung von Logs und Reruns
- **Metrics-Sammlung**: Performance-Metriken sammeln
- **Alert-System**: Benachrichtigungen bei kritischen Events
- **Dashboard-Integration**: Zentrale Überwachung mehrerer Apps

Die Basis-Infrastruktur ist bereits vorhanden und kann bei Bedarf erweitert werden.