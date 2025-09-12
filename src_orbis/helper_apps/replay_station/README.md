# Replay Station - MQTT Replay Funktionalität

## 🎯 Zweck

Die Replay Station ist eine **unabhängige Helper-App** für das Abspielen von aufgenommenen MQTT-Sessions über einen lokalen Mosquitto-Broker. Sie ermöglicht es, das OMF Dashboard im Replay-Modus zu testen, ohne dass die reale APS-Fabrik aktiv ist.

## 🏗️ Architektur

### **Unabhängige Systeme**
- **Replay Station**: Sendet Nachrichten an lokalen MQTT-Broker
- **Lokaler Mosquitto-Broker**: Vermittelt Nachrichten (localhost:1883)
- **OMF Dashboard**: Empfängt Nachrichten im Replay-Modus
- **Keine direkte Kopplung**: Alle Systeme arbeiten unabhängig

### **Replay-Workflow**
```
Session Files → Replay Station → MQTT Broker → OMF Dashboard
```

## 🚀 Funktionen

### **1. Session-Loading**
- **SQLite-Sessions**: Lädt `.db` Dateien aus `data/mqtt-data/sessions/`
- **Log-Sessions**: Lädt `.log` Dateien (JSON-Format)
- **Session-Validierung**: Prüft Datenintegrität

### **2. Replay-Kontrolle**
- **Play/Pause**: Kontrolle über Replay-Ablauf
- **Geschwindigkeit**: Zeitraffung (0.1x - 10x)
- **Loop-Modus**: Wiederholung der Session
- **Progress-Bar**: Visueller Fortschritt

### **3. MQTT-Publishing**
- **Lokaler Broker**: Verbindung zu `localhost:1883`
- **Original-Timing**: Beibehaltung der ursprünglichen Zeitabstände
- **QoS-Level**: Konfigurierbare Qualität der Nachrichtenübertragung

## 🔧 Technische Details

### **Session-Player Klasse**
```python
class SessionPlayer:
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.messages = []
        self.current_index = 0
        self.is_playing = False
        self.speed = 1.0
        self.loop = False
```

### **MQTT-Verbindung**
```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.publish(topic, payload, qos=1)
```

### **Session-Datenformat**
```json
{
  "timestamp": "2025-08-26T16:38:54.183763+00:00",
  "topic": "ccu/order/request",
  "payload": "{\"orderId\":\"uuid-123\",\"workpieceType\":\"white\"}"
}
```

## 📋 Verwendung

### **Replay Station starten**
```bash
streamlit run src_orbis/helper_apps/replay_station/replay_station_dashboard.py
```

### **Replay-Workflow**
1. **Session auswählen** aus verfügbaren Sessions
2. **Replay-Einstellungen** konfigurieren (Geschwindigkeit, Loop)
3. **Play-Button** drücken zum Starten
4. **OMF Dashboard** empfängt Nachrichten im Replay-Modus

### **Verfügbare Sessions**
- **Auftrag-Sessions**: `aps_persistent_traffic_auftrag-*.log`
- **End-to-End-Sessions**: `aps_persistent_traffic_end2end_*.log`
- **SQLite-Sessions**: `*.db` Dateien

## ⚙️ Konfiguration

### **MQTT-Broker-Einstellungen**
- **Host**: `localhost` (Standard)
- **Port**: `1883` (Standard MQTT-Port)
- **QoS**: `1` (At least once delivery)

### **Replay-Einstellungen**
- **Geschwindigkeit**: 0.1x - 10x (Standard: 1x)
- **Loop**: Einmalig oder wiederholt
- **Auto-Start**: Automatisches Starten nach Laden

## 🎯 Vorteile

### **1. Unabhängige Tests**
- **Dashboard-Tests** ohne reale Hardware
- **Verschiedene Szenarien** testbar
- **Reproduzierbare Ergebnisse**

### **2. Flexible Kontrolle**
- **Geschwindigkeitskontrolle** für schnelle Tests
- **Pause/Resume** für detaillierte Analyse
- **Loop-Modus** für wiederholte Tests

### **3. Einfache Wartung**
- **Unabhängige Entwicklung** vom OMF Dashboard
- **Klare Trennung** der Verantwortlichkeiten
- **Modulare Architektur**

## 🔗 Verwandte Dokumentation

- **[MQTT Replay Pattern](../../docs_orbis/guides/communication/mqtt-replay-pattern.md)**
- **[Session Manager README](../session_manager/README.md)**
- **[OMF Dashboard README](../../omf/dashboard/README.md)**
- **[Project Overview](../../docs_orbis/PROJECT_OVERVIEW.md)**

## ⚠️ Wichtige Hinweise

- **Lokaler MQTT-Broker** muss laufen (Mosquitto)
- **Keine direkte Kopplung** zum OMF Dashboard
- **Replay-Zweck**: Nur für Tests, nicht für Produktion
- **Unabhängige Entwicklung**: Separate Wartung und Weiterentwicklung
