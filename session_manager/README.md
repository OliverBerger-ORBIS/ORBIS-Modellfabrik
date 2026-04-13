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
- **Log (JSON-Zeilen):** Aufzeichnung aller MQTT-Messages als `.log` Dateien
- **Pause/Resume:** Recording kann pausiert und fortgesetzt werden
- **Auto-Stop:** Automatisches Stoppen nach konfigurierbarer Zeit
- **Topic-Aufnahme (DR-25):** Preset **„Alle Topics“** oder **„Analyse: ohne Arduino / BME680 / Kamera / LDR“** — letzteres unterdrückt nur den **Schreibpfad** ins Log (`subscribe("#")` unverändert). Konfiguration: Tab *Session Recorder* oder *Einstellungen → Session Recorder*, persistiert in `session_manager_settings.json` als `session_recorder.recording.recording_exclusion_preset` (`none` | `analysis`). Details: [session-recorder.md](../docs/04-howto/helper_apps/session-manager/session-recorder.md), [DR-25](../docs/03-decision-records/25-session-log-topic-filters.md).

### 🔄 Session Replay
- **Vollständiger Replay:** Wiederholung aufgezeichneter Sessions (`.log` Dateien, JSON-Zeilen-Format)
- **Test-Topic Management:** 
  - Einzelne JSON-Testdaten laden und senden
  - Automatischer Preload aus `data/osf-data/test_topics/preloads/`
- **Speed Control:** Replay-Geschwindigkeit anpassbar

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
│   ├── session_recorder.py        # Recording-Tab
│   ├── replay_station.py          # Replay-Tab
│   ├── logs.py                    # Logs-Tab
│   ├── settings_ui.py             # Settings-Tab
│   ├── order_analyzer.py          # Order-Flow-Analyse
│   ├── auftrag_rot_analyzer.py    # Auftrag-Analyse
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
    ├── test_logging_cleanup.py
    └── test_session_log_format.py   # Session .log (JSON-Zeilen) Roundtrip
```

---

## ⚙️ Konfiguration

### MQTT-Broker
Konfiguration über **Settings-Tab** in der App:
- Broker-Host (Default: `localhost`)
- Port (Default: `1883`)
- Client-ID (Default: `session_manager`)

### Session-Verzeichnis
- **Sessions:** `data/osf-data/sessions/`
- **Test-Topics:** `data/osf-data/test_topics/`
- **Preloads:** `data/osf-data/test_topics/preloads/`

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
│   └── osf-data/
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
streamlit run session_manager/app.py --server.port 8502

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
# In app.py
# registry_manager implementieren
# Dann: streamlit run session_manager/app.py --registry-watch
```

### Topic Categorization
```python
# OmfTopicManager in utils/ implementieren
# Dann in geeigneten Komponenten aktivieren (die früheren Analysis-Komponenten wurden entfernt)
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

session_dir = PROJECT_ROOT / "data/osf-data/sessions"
```

---

## 📄 Lizenz

ORBIS SmartFactory Internal Tool

---

## 👥 Kontakt

ORBIS SmartFactory Team

