# OMF Replay Station - Entwicklungsstand und nächste Schritte

## 🎯 Was wurde erreicht (Stand: 30.08.2025)

### ✅ Implementierte Features

#### 1. **Nachrichtenzentrale im OMF Dashboard**
- **Tab "Nachrichtenzentrale"** mit zwei Untertabs:
  - 📥 Empfangene Nachrichten (zuerst angezeigt)
  - 📤 Gesendete Nachrichten
- **Robuste Filterung** nach:
  - Modulen (z.B. "j1", "module")
  - Kategorien (z.B. "connection", "state")
  - Subkategorien (z.B. "pairing", "instantAction")
  - Zeitraum (Alle Nachrichten, Letzte Stunde, Letzter Tag, Letzte Woche)
- **MQTT-Integration**: Automatische Anzeige von Nachrichten aus dem MQTT-Client
- **Performance-Optimierung**: Entfernung von `st.rerun()` für stabilere WebSocket-Verbindungen

#### 2. **MQTT-Client Erweiterungen**
- **Dynamische Broker-Konfiguration** für verschiedene Modi:
  - `Live-Fabrik`: localhost:1883
  - `Replay-Station`: localhost:1884
  - `Mock-Modus`: Simulierte Verbindung
- **Message History**: Speicherung empfangener Nachrichten für Dashboard-Anzeige
- **Import-Fehler behoben**: `mqtt.MQTT_ERR_SUCCESS` statt `mqtt_client.MQTT_ERR_SUCCESS`

#### 3. **Dashboard Settings Integration**
- **Zentrale MQTT-Modus-Auswahl** in "Dashboard-Einstellungen":
  - Live-Fabrik
  - Replay-Station (Standard)
  - Mock-Modus
- **Erweiterte Status-Anzeige**: Zeigt aktuellen Verbindungsmodus an
- **Replay-Station Quick-Links**: Direkte Links zu Replay-Station (Port 8509) und Session-Verzeichnis

#### 4. **Simple Replay Station**
- **Neue Architektur "Option A"**: Separater MQTT-Broker als Service
- **`simple_replay_station.py`**: Vereinfachte Replay-Station als MQTT-Client
- **Session-Loading**: Unterstützung für SQLite- und Log-Dateien
- **Message Publishing**: Verwendung von `mosquitto_pub` für Nachrichtenversand
- **Threaded Replay**: Asynchrone Wiedergabe mit Pause/Stop-Funktionalität

#### 5. **Asset-Management**
- **Neue Asset-Struktur**: `src_orbis/omf/dashboard/assets/`
- **ORBIS Logo Update**: `ORBIS_WWW_4C.png` als neues Standard-Logo
- **Robuste Logo-Ladung**: Multiple Pfad-Varianten mit Fallback auf "🏭" Emoji
- **Browser-Icon**: "🏭" statt generischem blauen Kreis

#### 6. **Unit Tests**
- **`test_message_center.py`**: Umfassende Tests für MessageMonitorService
- **`test_replay_station.py`**: Tests für LocalMQTTBroker und SessionPlayer
- **Case-insensitive Filtering**: Korrektur der Filter-Logik

### 🔧 Technische Verbesserungen

#### Port-Konfiguration
- **Dashboard**: Port 8506
- **Replay Station**: Port 8509
- **MQTT Broker (Replay)**: Port 1884
- **Live MQTT**: Port 1883
- **Node-RED**: Port 1880
- **OPC-UA**: Port 4840

#### Architektur-Entscheidungen
- **"Option A" gewählt**: Separater Mosquitto-Broker als Service
- **Replay Station als Client**: Verwendet `mosquitto_pub` statt eigenem Broker
- **Dashboard als Client**: Verbindet sich mit externem Broker

## 🚧 Aktuelle Probleme (vor Commit)

### ❌ Mosquitto Broker Issues
- **Problem**: `mosquitto -h 0.0.0.0 -p 1884 -v` zeigt nur Help-Text
- **Ursache**: Unbekannt - möglicherweise Konfigurationsproblem
- **Auswirkung**: "Connection refused" Fehler im Dashboard
- **Workaround**: `mosquitto -p 1884 -v` funktioniert, aber nur localhost

### 🔄 Connection Problems
- **Dashboard**: Kann sich nicht mit Replay-Broker verbinden
- **Replay Station**: Sendet Nachrichten erfolgreich (Logs zeigen Aktivität)
- **Broker**: Läuft auf localhost, aber Dashboard erreicht ihn nicht

## 📋 Nächste Schritte nach Commit

### 1. **Mosquitto Broker Problem lösen**
```bash
# Test 1: Standard Mosquitto starten
mosquitto -p 1884 -v

# Test 2: Mit Konfigurationsdatei
echo "listener 1884 0.0.0.0" > mosquitto_replay.conf
mosquitto -c mosquitto_replay.conf -v

# Test 3: Als Service starten
mosquitto -d -p 1884 -v
```

### 2. **Systematischer Test des Ablaufs**
```bash
# Schritt 1: Broker starten
mosquitto -p 1884 -v &

# Schritt 2: Replay Station starten
streamlit run src_orbis/omf/replay_station/simple_replay_station.py --server.port 8509 &

# Schritt 3: Dashboard starten
streamlit run src_orbis/omf/dashboard/omf_dashboard.py --server.port 8506 &

# Schritt 4: Verbindung testen
python -c "
import paho.mqtt.client as mqtt
client = mqtt.Client()
client.connect('localhost', 1884, 60)
print('✅ Verbindung erfolgreich')
client.disconnect()
"
```

### 3. **Dashboard Integration testen**
- [ ] Dashboard verbindet sich mit Replay-Broker
- [ ] Nachrichten erscheinen in Nachrichtenzentrale
- [ ] Filter funktionieren korrekt
- [ ] MQTT-Modus-Wechsel funktioniert

### 4. **Replay Station Features testen**
- [ ] Session-Loading funktioniert
- [ ] Replay-Controls sind sichtbar
- [ ] Nachrichten werden korrekt gesendet
- [ ] Pause/Stop funktioniert

## 🎯 Ziel nach Commit

**Funktionierender End-to-End Test:**
1. Mosquitto Broker läuft stabil auf Port 1884
2. Replay Station lädt Session und sendet Nachrichten
3. Dashboard empfängt und zeigt Nachrichten in Nachrichtenzentrale
4. Filter und MQTT-Modus-Wechsel funktionieren

## 📝 Commit Message Vorschlag

```
feat: Implement OMF Replay Station with Message Center

- Add Nachrichtenzentrale tab with filtering capabilities
- Implement simple_replay_station.py with mosquitto_pub
- Add MQTT mode selection (Live/Replay/Mock) to dashboard settings
- Update ORBIS logo and asset structure
- Add comprehensive unit tests for message center and replay station
- Fix MQTT client import errors and connection issues
- Set default MQTT mode to Replay-Station

Architecture: Separate mosquitto broker (port 1884) with replay station
and dashboard as clients. Replay station uses mosquitto_pub for message
publishing.
```

## 🔍 Debugging Checklist

### Mosquitto Broker
- [ ] Läuft auf Port 1884
- [ ] Bindet an alle Interfaces (nicht nur localhost)
- [ ] Akzeptiert Verbindungen von Dashboard und Replay Station
- [ ] Logs zeigen erfolgreiche Verbindungen

### Replay Station
- [ ] Lädt Sessions korrekt
- [ ] Sendet Nachrichten via mosquitto_pub
- [ ] Replay-Controls sind sichtbar
- [ ] Keine Session State Fehler

### Dashboard
- [ ] Verbindet sich mit Replay-Broker
- [ ] Zeigt Nachrichten in Nachrichtenzentrale
- [ ] Filter funktionieren
- [ ] MQTT-Modus-Wechsel funktioniert

---

**Status**: Bereit für Commit - Mosquitto Broker Problem muss nach Commit gelöst werden.
