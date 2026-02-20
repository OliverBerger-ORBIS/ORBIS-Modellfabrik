# Session Manager

**Standalone MQTT Session Management Tool** für die ORBIS SmartFactory APS

Ein eigenständiges Streamlit-Tool zur Verwaltung, Aufzeichnung und Analyse von MQTT-Sessions.

---

## 🚀 Quick Start

```bash
# Session Manager starten
streamlit run session_manager/app.py

# Optional: Mit bestimmtem Port
streamlit run session_manager/app.py --server.port 8502
```

---

## 📋 Features

### 🎙️ Session Recording
- **SQLite + JSON-Logs:** Aufzeichnung aller MQTT-Messages
- **Pause/Resume:** Recording kann pausiert und fortgesetzt werden
- **Auto-Stop:** Automatisches Stoppen nach konfigurierbarer Zeit

### 🔄 Session Replay
- **Vollständiger Replay:** Wiederholung aufgezeichneter Sessions
- **Test-Topic Management:** 
  - Einzelne JSON-Testdaten laden und senden
  - Automatischer Preload aus `data/omf-data/test_topics/preloads/`
- **Speed Control:** Replay-Geschwindigkeit anpassbar

### 📊 Session Analysis
- **Timeline-Visualisierung:** Grafische Darstellung des Nachrichtenflusses
- **Topic-Filterung:** Filter nach Kategorien und Keywords
- **Order-Flow-Analyse:** Verfolgung von Order-IDs durch das System
- **Statistiken:** Nachrichten-Counts, Zeitstempel-Analyse

### 📝 Topic Recording
- **Erste Message:** Speichert erste Nachricht pro Topic
- **Test-Daten-Sammlung:** Valide Beispiele für Tests
- **JSON-Export:** Strukturierte Test-Daten

### 📋 Live-Logs
- **Ring-Buffer:** Zeigt letzte N Log-Nachrichten
- **Level-Filter:** DEBUG, INFO, WARNING, ERROR
- **Auto-Refresh:** Automatische Aktualisierung

---

## 📁 Verzeichnis-Struktur

```
session_manager/
├── __init__.py                    # Package-Init
├── app.py                         # Hauptapp (Streamlit)
├── mqtt_client.py                 # MQTT-Client
├── session_manager_settings.json  # Settings
├── README.md                      # Diese Datei
├── components/                    # UI-Komponenten
│   ├── session_analysis.py        # Session-Analyse-Tab
│   ├── session_recorder.py        # Recording-Tab
│   ├── topic_recorder.py          # Topic-Recording-Tab
│   ├── replay_station.py          # Replay-Tab
│   ├── logs.py                    # Logs-Tab
│   ├── settings_ui.py             # Settings-Tab
│   ├── session_analyzer.py        # Analyzer-Core
│   ├── ui_components.py           # UI-Helpers
│   ├── order_analyzer.py          # Order-Flow-Analyse
│   ├── auftrag_rot_analyzer.py    # Auftrag-Analyse
│   ├── topic_manager.py           # Topic-Filter-Manager
│   ├── timeline_visualizer.py     # Timeline-Visualisierung
│   └── settings_manager.py        # Settings-Manager
├── utils/                         # Utils (eigenständig)
│   ├── logging_config.py          # Thread-sicheres Logging
│   ├── path_constants.py          # Pfad-Konstanten
│   ├── ui_refresh.py              # RerunController
│   ├── session_logger.py          # Session-Logger
│   └── streamlit_log_buffer.py    # Log-Ring-Buffer
├── mqtt/                          # MQTT-Client
│   └── mqtt_client.py             # SessionManagerMQTTClient
└── tests/                         # Python-Tests (pytest)
    ├── test_session_manager_logging.py
    ├── test_session_logger.py
    └── test_logging_cleanup.py
```

---

## ⚙️ Konfiguration

### MQTT-Broker
Konfiguration über **Settings-Tab** in der App:
- Broker-Host (Default: `localhost`)
- Port (Default: `1883`)
- Client-ID (Default: `session_manager`)

### Session-Verzeichnis
- **Sessions:** `data/omf-data/sessions/`
- **Test-Topics:** `data/omf-data/test_topics/`
- **Preloads:** `data/omf-data/test_topics/preloads/`

### Logging
- **Log-Verzeichnis:** `logs/`
- **JSON-Logs:** `logs/session_manager.jsonl`
- **Level:** Einstellbar über UI (DEBUG, INFO, WARNING, ERROR)

---

## 🔧 Abhängigkeiten

**Eigenständiges Tool** - Keine Abhängigkeiten zu `omf/` oder `omf2/`

### Python Packages (requirements)
```
streamlit
paho-mqtt
plotly
pandas
networkx
pyyaml
rich  # optional
```

### Projekt-Struktur
```
ORBIS-Modellfabrik/
├── session_manager/    ← Dieses Tool (eigenständig)
├── omf2/               ← Hauptmodul (unabhängig)
├── data/               ← Shared data directory
│   └── omf-data/
│       ├── sessions/
│       └── test_topics/
└── logs/               ← Shared logs directory
```

---

## 📖 Verwendung

### 1. Session aufzeichnen
1. Öffne **"🎙️ Session Recorder"** Tab
2. Konfiguriere Topics und Einstellungen
3. Klicke **"🎙️ Recording starten"**
4. System nimmt alle MQTT-Nachrichten auf
5. Stoppe mit **"⏹️ Recording stoppen"**

### 2. Session abspielen
1. Öffne **"🔄 Replay Station"** Tab
2. Wähle eine aufgezeichnete Session
3. Konfiguriere Replay-Geschwindigkeit
4. Klicke **"▶️ Replay starten"**

### 3. Test-Topics senden
1. Öffne **"🔄 Replay Station"** Tab
2. Sektion **"Individuelle Test-Topics"**
3. Wähle JSON-Dateien aus
4. Klicke **"📤 Ausgewählte Topics senden"**

### 4. Session analysieren
1. Öffne **"📊 Session Analysis"** Tab
2. Wähle Session-Datei (`.db` oder `.log`)
3. Nutze Filter und Suche
4. Visualisiere Timeline und Order-Flows

---

## 🐛 Troubleshooting

### MQTT-Verbindung fehlgeschlagen
- Prüfe Broker-Adresse in Settings
- Prüfe ob Broker läuft: `mosquitto -v`
- Prüfe Firewall/Ports

### Import-Fehler
```bash
# Virtual Environment aktivieren
source .venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### Streamlit startet nicht
```bash
# Port ändern
streamlit run session_manager/session_manager.py --server.port 8502

# Cache löschen
streamlit cache clear
```

### Logs nicht sichtbar
- Prüfe Logging-Level in Settings (DEBUG zeigt am meisten)
- Prüfe `logs/session_manager.jsonl`
- Refresh-Rate erhöhen (Settings)

---

## 🔍 Optional Features (deaktiviert)

Diese Features sind aktuell **auskommentiert** und können bei Bedarf reaktiviert werden:

### Registry Watch Mode
```python
# In session_manager.py
# registry_manager implementieren
# Dann: streamlit run session_manager/session_manager.py --registry-watch
```

### Topic Categorization
```python
# OmfTopicManager in utils/ implementieren
# Dann in topic_manager.py und timeline_visualizer.py aktivieren
```

---

## 📝 Entwicklung

### Code-Struktur
- **Relative Imports:** Alle imports innerhalb session_manager sind relativ
- **Eigenständig:** Keine Abhängigkeiten zu omf oder omf2
- **Modular:** Jede Komponente ist eigenständig testbar

### Logging
```python
from .utils.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Message")
```

### Pfade
```python
from .utils.path_constants import PROJECT_ROOT

session_dir = PROJECT_ROOT / "data/omf-data/sessions"
```

---

## 📄 Lizenz

ORBIS SmartFactory Internal Tool

---

## 👥 Kontakt

ORBIS SmartFactory Team

