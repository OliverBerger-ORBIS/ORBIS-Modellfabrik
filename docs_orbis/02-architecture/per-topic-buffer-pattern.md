# Per-Topic-Buffer Pattern

## Übersicht

Das **Per-Topic-Buffer Pattern** ist die aktuelle Architektur für MQTT-Nachrichtenverarbeitung im OMF Dashboard. Es bietet eine saubere, effiziente Lösung für die Verarbeitung von MQTT-Nachrichten.

## Architektur-Prinzipien

### 1. **MQTT-Singleton Pattern**
- **Eine MQTT-Client-Instanz** pro Streamlit-Session
- **Zentraler Zugriff** über `st.session_state["mqtt_client"]`
- **Keine Verletzung** des Singleton-Patterns durch direkte Client-Aufrufe

### 2. **Per-Topic-Buffer System**
- **Topic-spezifische Buffer** für jede MQTT-Subscription
- **Automatische Nachrichtensammlung** in separaten Buffers
- **Effiziente Verarbeitung** ohne Message-Processor Overhead

### 3. **Hybrid-Architektur für Publishing**
- **MessageGenerator** für Payload-Erstellung
- **Session State** für Preview/Edit-Funktionalität
- **MqttGateway** für finales Publishing

## Implementierung

### Subscription Pattern

```python
# 1. Topics subscriben
client.subscribe_many([
    "module/v1/ff/+/state",
    "module/v1/ff/+/connection", 
    "ccu/pairing/state",
    "module/v1/ff/+/factsheet"
])

# 2. Per-Topic-Buffer abrufen
state_messages = list(client.get_buffer("module/v1/ff/+/state"))
connection_messages = list(client.get_buffer("module/v1/ff/+/connection"))
pairing_messages = list(client.get_buffer("ccu/pairing/state"))
factsheet_messages = list(client.get_buffer("module/v1/ff/+/factsheet"))

# 3. Nachrichten verarbeiten
_process_module_messages(state_messages, connection_messages, pairing_messages, factsheet_messages)
```

### Publishing Pattern

```python
# 1. MessageGenerator für Payload
generator = get_omf_message_generator()
message = generator.generate_fts_navigation_message(route_type="DPS_HBW", load_type="WHITE")

# 2. Session State für Preview
st.session_state["pending_message"] = {
    "topic": message["topic"],
    "payload": message["payload"], 
    "type": "navigation"
}

# 3. MqttGateway für Publishing
gateway = MqttGateway(mqtt_client)
success = gateway.send(
    topic=message["topic"],
    builder=lambda: message["payload"],
    ensure_order_id=True
)
```

## Vorteile

### ✅ **Performance**
- **Keine Message-Processor Overhead**
- **Direkte Buffer-Zugriffe**
- **Effiziente Topic-Filterung**

### ✅ **Einfachheit**
- **Klare Separation** von Subscription und Verarbeitung
- **Weniger Abstraktionsebenen**
- **Einfacher zu debuggen**

### ✅ **Flexibilität**
- **Topic-spezifische Verarbeitung**
- **Einfache Erweiterung** für neue Topics
- **Kombinierbar** mit verschiedenen Verarbeitungslogiken

## Vergleich: Per-Topic-Buffer vs. Message-Processor

| Aspekt | Per-Topic-Buffer | Message-Processor |
|--------|------------------|-------------------|
| **Performance** | ✅ Hoch | ❌ Overhead |
| **Einfachheit** | ✅ Einfach | ❌ Komplex |
| **Debugging** | ✅ Direkt | ❌ Abstrahiert |
| **Erweiterbarkeit** | ✅ Flexibel | ❌ Starr |
| **MQTT-Singleton** | ✅ Kompatibel | ❌ Problematisch |

## Verwendung in Komponenten

### Overview_Modul_Status
```python
def show_overview_module_status():
    # Per-Topic-Buffer für Modul-Status
    state_messages = list(client.get_buffer("module/v1/ff/+/state"))
    connection_messages = list(client.get_buffer("module/v1/ff/+/connection"))
    pairing_messages = list(client.get_buffer("ccu/pairing/state"))
    factsheet_messages = list(client.get_buffer("module/v1/ff/+/factsheet"))
    
    # Verarbeitung
    _process_module_messages(state_messages, connection_messages, pairing_messages, factsheet_messages)
```

### FTS InstantAction
```python
def show_fts_instantaction():
    # Per-Topic-Buffer für FTS-Nachrichten
    instantaction_messages = list(client.get_buffer("fts/v1/ff/5iO4/instantAction"))
    
    # Verarbeitung
    process_fts_instantaction_messages_from_buffers(instantaction_messages)
```

## Migration von Message-Processor

### Alte Implementierung (Veraltete Architektur)
```python
# ❌ ALT: Veraltete Architektur
processor = get_message_processor(
    component_name="overview_module_status",
    message_filter=create_topic_filter(["module/v1/ff/+/state", "module/v1/ff/+/connection"]),
    processor_function=lambda msgs: _process_module_messages(msgs, module_status_store),
)
processor.process_messages(client)
```

### Neue Implementierung (Per-Topic-Buffer)
```python
# ✅ NEU: Per-Topic-Buffer Pattern
client.subscribe_many(["module/v1/ff/+/state", "module/v1/ff/+/connection"])
state_messages = list(client.get_buffer("module/v1/ff/+/state"))
connection_messages = list(client.get_buffer("module/v1/ff/+/connection"))
_process_module_messages(state_messages, connection_messages, module_status_store)
```

## Best Practices

### 1. **Topic-Subscription**
- **Subscribe einmal** beim Komponenten-Start
- **Verwende subscribe_many()** für mehrere Topics
- **QoS-Level** entsprechend der Anforderung wählen

### 2. **Message Center Ausnahme**
```python
# ✅ ERLAUBT - Nur im Message Center
mqtt_client.subscribe("#", qos=1)  # Wildcard-Subscription
all_messages = list(mqtt_client._history)  # Globale History
```

**Warum Ausnahme:**
- **Message Center** benötigt **alle Nachrichten** für Übersichtsfunktion
- **Debugging und Monitoring** erfordert vollständige Nachrichtensicht
- **Validierungsregel** erlaubt `subscribe("#")` nur in `message_center.py`

**Regeln:**
- **Standard:** Per-Topic-Buffer Pattern für alle Komponenten
- **Ausnahme:** Wildcard-Subscription nur im Message Center
- **Verboten:** `subscribe("#")` in anderen Komponenten

### 3. **Buffer-Verarbeitung**
- **Buffer bei jedem Rerun** abrufen
- **Leere Buffer** handhaben
- **Message-Validierung** vor Verarbeitung

### 4. **Error Handling**
- **Try-Catch** um Buffer-Zugriffe
- **Fallback-Verhalten** bei Fehlern
- **User-Feedback** bei Problemen

## Validierungsregeln

Das **Per-Topic-Buffer Pattern** wird durch automatische Validierung überwacht:

### Dashboard Rules Validator
```bash
python src_orbis/scripts/validate_dashboard_rules.py
```

**Regeln:**
- **ERROR:** `subscribe("#")` in Komponenten (außer Message Center)
- **WARN:** `subscribe("#")` im Message Center (erlaubt, aber prüfen ob nötig)
- **WARN:** Sehr breite Subscribe-Patterns (`module/#`, `fts/#`, etc.)
- **WARN:** `subscribe()` in Komponenten (besser: Interesse/Buffer deklarieren)

### Message Center Ausnahme
```python
# ✅ ERLAUBT - Nur in message_center.py
mqtt_client.subscribe("#", qos=1)

# ❌ VERBOTEN - In allen anderen Komponenten
mqtt_client.subscribe("#", qos=1)  # ERROR: subscribe('#') ist verboten
```

## Troubleshooting

### Problem: Buffer ist leer
```python
# Lösung: Prüfe Subscription und MQTT-Verbindung
if not client.connected:
    st.error("❌ MQTT nicht verbunden")
    return

messages = list(client.get_buffer("topic"))
if not messages:
    st.warning("⚠️ Keine Nachrichten im Buffer")
    return
```

### Problem: Topic-Pattern funktioniert nicht
```python
# Lösung: Verwende exakte Topics statt Wildcards
# ❌ Problematisch: client.get_buffer("module/v1/ff/+/state")
# ✅ Besser: client.get_buffer("module/v1/ff/SVR4H76530/state")
```

## Fazit

Das **Per-Topic-Buffer Pattern** bietet eine moderne, effiziente Lösung für MQTT-Nachrichtenverarbeitung im OMF Dashboard. Es kombiniert die Vorteile des MQTT-Singleton Patterns mit einer einfachen, performanten Buffer-Architektur.

**Empfehlung:** Verwende dieses Pattern für alle neuen MQTT-Komponenten und migriere bestehende Message-Processor Implementierungen schrittweise.
