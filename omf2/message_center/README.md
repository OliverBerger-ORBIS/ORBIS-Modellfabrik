# OMF2 Message Center

MQTT-basierte Nachrichtenzentrale für die ORBIS-Modellfabrik mit Singleton-Pattern und automatischer Wiederverbindung.

## 🎯 Überblick

Das Message Center bietet eine vollständige MQTT-Integration mit folgenden Funktionalitäten:

- **MQTT Singleton Client**: Thread-sicherer Singleton für mehrfache Verwendung
- **Gateway-Komponente**: High-Level Interface für MQTT-Kommunikation  
- **Umgebungsverwaltung**: Umschaltung zwischen live, replay und mock
- **Nachrichtenverwaltung**: Bis zu 1000 Nachrichten im Arbeitsspeicher
- **Automatische Wiederverbindung**: Robuste Reconnect-Logik
- **UI mit festen Spalten**: Streamlit-optimierte Tabellendarstellung

## 🏗️ Architektur

### Komponenten

```
omf2/message_center/
├── __init__.py              # Module exports
├── mqtt_config.py           # MQTT Konfiguration
├── mqtt_client.py           # Thread-sicherer MQTT Singleton Client
├── mqtt_gateway.py          # High-Level Gateway Interface
├── message_handler.py       # Nachrichtenverarbeitung und Filterung
└── README.md               # Diese Dokumentation
```

### Klassen-Diagramm

```
MqttConfig
    ↓
MqttClient (Singleton)
    ↓
MqttGateway
    ↓
MessageHandler
    ↓
UI Components
```

## 🚀 Verwendung

### Grundlegendes Setup

```python
from omf2.message_center import MqttGateway, MessageHandler
from omf2.common.env_manager import EnvironmentManager

# Environment Manager für Sidebar
env_manager = EnvironmentManager()
current_env = env_manager.show_complete_sidebar()

# MQTT Gateway initialisieren
gateway = MqttGateway(current_env)
gateway.connect()
gateway.subscribe_to_all_topics()

# Message Handler für Verarbeitung
handler = MessageHandler()
```

### Nachrichten verarbeiten

```python
# Alle Nachrichten abrufen
raw_messages = gateway.get_all_messages()

# In MessageRow-Objekte konvertieren
message_rows = handler.convert_messages_to_rows(raw_messages)

# Filtern und sortieren
filtered = handler.filter_messages_by_module(message_rows, "HBW")
sorted_messages = handler.sort_messages(filtered, "timestamp", ascending=False)

# Tabellendaten erstellen
headers, rows = handler.create_table_data(sorted_messages)
```

### Umgebung wechseln

```python
# Umgebung wechseln
success = gateway.switch_environment("live")
if success:
    gateway.subscribe_to_all_topics()
```

## 🔧 Konfiguration

### Umgebungen

- **live**: Produktions-System (`192.168.0.100:1883`)
- **replay**: Replay-Modus (`localhost:1884`)  
- **mock**: Test-Umgebung (`localhost:1883`)

### MQTT Settings

```python
from omf2.message_center.mqtt_config import MqttConfig

config = MqttConfig(
    host="localhost",
    port=1883,
    client_id="custom_client",
    keepalive=60,
    clean_session=True
)
```

## 📡 MQTT-Funktionalität

### Subscription

- Automatisches Subscribe auf **#** (alle Topics)
- Unterstützt Wildcard-Pattern (`+`, `#`)
- Idempotente Subscription-Verwaltung

### Message History

- **Maximale Kapazität**: 1000 Nachrichten (konstant)
- **Thread-sicher**: Deque mit Lock-Mechanismus
- **Memory-optimiert**: Automatische Rotation alter Nachrichten

### Reconnect-Logik

```python
# Automatische Wiederverbindung
client.reconnect_delay_set(min_delay=1, max_delay=120)

# Status-Callbacks
gateway.add_on_connect_callback(lambda: print("Connected"))
gateway.add_on_disconnect_callback(lambda: print("Disconnected"))
```

## 🎨 UI-Integration

### Sidebar-Management

```python
from omf2.common.env_manager import EnvironmentManager

env_manager = EnvironmentManager()

# Komplette Sidebar anzeigen
env_manager.show_complete_sidebar(mqtt_gateway)
```

### Message Table

- **Feste Spalten**: Zeit, Typ, Topic, Payload, QoS, Retain
- **Filteroptionen**: Topic, Modul, Nachrichtentyp
- **Sortierung**: Timestamp (neueste zuerst)
- **Pagination**: Konfigurierbares Limit

### UI-Refresh Pattern

```python
from omf.dashboard.utils.ui_refresh import request_refresh

# NIEMALS st.rerun() verwenden!
if message_sent:
    request_refresh()  # ✅ Korrekt
```

## 🧪 Testing

### Unit Tests ausführen

```bash
# Alle Message Center Tests
python -m pytest omf2/tests/test_message_center.py -v

# Spezifische Test-Klasse
python -m pytest omf2/tests/test_message_center.py::TestMqttClient -v

# Mit Coverage
python -m pytest omf2/tests/test_message_center.py --cov=omf2.message_center
```

### Test-Struktur

```
omf2/tests/
├── test_message_center.py
│   ├── TestMqttConfig
│   ├── TestMessageRow
│   ├── TestMessageHandler
│   ├── TestMqttClient
│   ├── TestMqttGateway
│   └── TestMessageCenterIntegration
```

## 📊 Performance

### Memory Management

- **Deque mit maxlen=1000**: Automatische Rotation
- **Thread-Safe Locks**: Verhindert Race Conditions
- **Efficient Filtering**: Case-insensitive String-Matching

### Responsiveness

- **Fast Rendering**: Pandas DataFrame für Tabellen
- **Debounced Updates**: UI-Refresh mit Debouncing
- **Lazy Loading**: On-demand Nachrichtenladen

## 🔒 Sicherheitsaspekte

### Thread Safety

- **Singleton Lock**: Thread-sicher mit `threading.Lock`
- **History Lock**: Separate Locks für Message History
- **Callback Safety**: Exception-Handling in Callbacks

### Error Handling

```python
try:
    gateway.connect()
except Exception as e:
    logger.error(f"Connection failed: {e}")
    # Fallback-Logik
```

## 🐛 Debugging

### Logging

```python
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.DEBUG)

# Spezifische Logger
logger = logging.getLogger("omf2.message_center.mqtt_client")
logger.setLevel(logging.DEBUG)
```

### Connection-Status prüfen

```python
status = gateway.get_connection_status()
print(f"Connected: {status['connected']}")
print(f"Messages: {status['messages']['total']}")
```

### Message History inspizieren

```python
messages = gateway.get_all_messages()
for msg in messages[-10:]:  # Letzte 10 Nachrichten
    print(f"{msg['topic']}: {msg['payload']}")
```

## 🔄 Migration von OMF1

### Unterschiede zu OMF1

| Aspekt | OMF1 | OMF2 |
|--------|------|------|
| Client Pattern | Factory | Singleton |
| UI Refresh | `st.rerun()` | `request_refresh()` |
| Environment | Config-basiert | Manager-basiert |
| Message Storage | Persistent | Memory-only |
| Testing | Minimal | Umfassend |

### Migration Steps

1. **Import-Pfade aktualisieren**:
   ```python
   # Alt
   from omf.dashboard.tools.omf_mqtt_client import OmfMqttClient
   
   # Neu
   from omf2.message_center import MqttGateway
   ```

2. **st.rerun() ersetzen**:
   ```python
   # Alt - VERBOTEN
   st.rerun()
   
   # Neu - Korrekt
   from omf.dashboard.utils.ui_refresh import request_refresh
   request_refresh()
   ```

3. **Environment Management**:
   ```python
   # Alt
   cfg = cfg_for(env)
   
   # Neu
   env_manager = EnvironmentManager()
   env = env_manager.get_current_environment()
   ```

## 📝 Entwicklungsrichtlinien

### Code Style

- **Type Hints**: Vollständige Typisierung
- **Docstrings**: Google Style für alle öffentlichen Methoden
- **Error Handling**: Explizite Exception-Behandlung
- **Logging**: Strukturiertes Logging mit passenden Levels

### Testing

- **Unit Tests**: Für alle Klassen und Methoden
- **Mocking**: MQTT-Client für Tests mocken
- **Integration Tests**: End-to-End Workflows testen
- **Coverage**: Mindestens 80% Code Coverage

### Documentation

- **README**: Umfassende Dokumentation
- **Docstrings**: Alle öffentlichen APIs dokumentieren
- **Examples**: Praktische Verwendungsbeispiele
- **Migration Guide**: Upgrade-Pfad von OMF1

## 📋 Akzeptanzkriterien

- ✅ MQTT Singleton Client implementiert
- ✅ Gateway-Komponente für High-Level API
- ✅ Umgebungsverwaltung in Sidebar
- ✅ Subscribe auf # (alle Topics)
- ✅ Automatische Wiederverbindung
- ✅ Max 1000 Nachrichten im Speicher
- ✅ UI mit festen Spalten
- ✅ request_refresh() statt st.rerun()
- ✅ Unit Tests für alle Komponenten
- ✅ Umfassende Dokumentation
- ✅ Stabile Dashboard-Starts ohne Crashes

## 🆘 Support

Bei Problemen oder Fragen:

1. **Tests prüfen**: `pytest omf2/tests/test_message_center.py -v`
2. **Logs überprüfen**: Debug-Level Logging aktivieren
3. **Singleton Reset**: `MqttClient.reset_singleton()` für Tests
4. **Environment Check**: Korrekte MQTT-Broker Konfiguration

## 🔗 Verwandte Dokumente

- [UI-Refresh Pattern](../../docs/03-decision-records/10-ui-refresh-pattern.md)
- [st.rerun() Forbidden Pattern](../../docs/03-decision-records/12-st-rerun-forbidden-pattern.md)
- [MQTT Connection-Loop Prevention](../../docs/03-decision-records/13-mqtt-connection-loop-prevention.md)