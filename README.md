# ORBIS Modellfabrik Dashboard

Ein umfassendes Dashboard für die ORBIS Modellfabrik mit MQTT-Nachrichtenüberwachung und Replay-Funktionalität.

## 🚀 Schnellstart

### Voraussetzungen

- **Python 3.8+**
- **Mosquitto MQTT Broker**
- **Git**

### Installation

1. **Repository klonen**
```bash
git clone <repository-url>
cd ORBIS-Modellfabrik
```

2. **Python-Umgebung einrichten**
```bash
# Virtual Environment erstellen
python -m venv .venv

# Aktivieren
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

3. **Abhängigkeiten installieren**
```bash
pip install -r requirements.txt
```

4. **Mosquitto installieren**
```bash
# macOS:
brew install mosquitto

# Windows: Download von https://mosquitto.org/download/

# Linux:
sudo apt-get install mosquitto mosquitto-clients
```

### Start der Anwendungen

1. **Mosquitto Broker starten**
```bash
mosquitto -p 1884 -v &
```

2. **Replay Station starten**
```bash
streamlit run src_orbis/omf/replay_station/replay_station.py --server.port 8509
```

3. **Dashboard starten**
```bash
streamlit run src_orbis/omf/dashboard/omf_dashboard.py --server.port 8506
```

### Browser-Zugriff

- **Dashboard**: http://localhost:8506
- **Replay Station**: http://localhost:8509

## 📊 Features

### 🏭 OMF Dashboard
- **Nachrichtenzentrale**: Anzeige aller MQTT-Nachrichten mit Filterung
- **Dashboard-Einstellungen**: MQTT-Modus konfigurieren (Live/Replay/Mock)
- **Steuerung**: Nachrichten an die Fabrik senden
- **Prioritäten-System**: Nachrichten nach Wichtigkeit filtern

### 🎬 OMF Replay Station
- **Session-Replay**: Aufgenommene MQTT-Sessions wiedergeben
- **Kontrollen**: Play/Pause/Stop/Resume
- **Fortschrittsanzeige**: Live-Fortschritt des Replays
- **Session-Validierung**: Automatische Prüfung der Session-Dateien

### 🔄 MQTT-Integration
- **Multi-Modus**: Live-Fabrik, Replay-Broker, Mock-Modus
- **Nachrichten-Historie**: Rolling Buffer (1000 Nachrichten)
- **Automatische Verbindung**: Intelligente Broker-Verbindung
- **Topic-Prioritäten**: System zur Nachrichtenfilterung

## 🏗️ Architektur

```
🎬 OMF Replay Station (Port 8509)
    ↓ (sendet via mosquitto_pub)
🔄 Mosquitto Broker (Port 1884)
    ↓ (verteilt MQTT-Nachrichten)
🏭 OMF Dashboard (Port 8506)
    ↓ (empfängt und zeigt an)
📊 Nachrichtenzentrale mit Filterung
```

## 📁 Projekt-Struktur

```
ORBIS-Modellfabrik/
├── src_orbis/
│   └── omf/
│       ├── dashboard/
│       │   ├── omf_dashboard.py          # Haupt-Dashboard
│       │   ├── components/
│       │   │   ├── message_center.py     # Nachrichtenzentrale
│       │   │   ├── settings.py           # Dashboard-Einstellungen
│       │   │   └── steering.py           # Steuerung
│       │   └── assets/                   # Logos und Assets
│       ├── replay_station/
│       │   └── replay_station.py         # Replay Station
│       └── tools/
│           └── mqtt_client.py            # MQTT-Client
├── mqtt-data/
│   └── sessions/                         # Session-Dateien (.db, .log)
├── docs_orbis/                           # Dokumentation
└── .venv/                                # Virtual Environment
```

## 🔧 Konfiguration

### MQTT-Modi

1. **Live-Fabrik**: Verbindung zur echten APS-Fabrik
2. **Replay-Broker**: Verbindung zum lokalen Mosquitto-Broker
3. **Mock-Modus**: Simulierte Verbindung für Tests

### Prioritäten-System

- **Prio 1**: Critical Control (Orders, Requests)
- **Prio 2**: Important Status (States, Connections)
- **Prio 3**: Normal Info (Standard-Nachrichten)
- **Prio 4**: NodeRED Topics
- **Prio 5**: High Frequency (Kamera, Sensoren)

## 🐛 Troubleshooting

### Häufige Probleme

#### "Connection refused"
```bash
# Mosquitto neu starten
pkill mosquitto
mosquitto -p 1884 -v &
```

#### "ModuleNotFoundError"
```bash
# Virtual Environment aktivieren
source .venv/bin/activate
```

#### "Port already in use"
```bash
# Prozesse beenden
pkill -f streamlit
pkill mosquitto
```

### Logs prüfen

- **Dashboard**: Terminal-Ausgabe
- **Replay Station**: Terminal-Ausgabe
- **Mosquitto**: Terminal-Ausgabe mit `-v` Flag

## 📚 Dokumentation

- **Entwicklungsstand**: `docs_orbis/omf_replay_station_progress.md`
- **API-Dokumentation**: Siehe Code-Kommentare
- **MQTT-Topics**: Siehe `src_orbis/omf/tools/mqtt_client.py`

## 🤝 Beitragen

1. Fork erstellen
2. Feature-Branch erstellen
3. Änderungen committen
4. Pull Request erstellen

## 📄 Lizenz

[Lizenz-Informationen hier einfügen]

## 👥 Team

- **Entwicklung**: ORBIS Team
- **MQTT-Integration**: [Name]
- **Dashboard-Design**: [Name]

---

**Status**: ✅ Vollständig funktionsfähig - Bereit für Produktion
