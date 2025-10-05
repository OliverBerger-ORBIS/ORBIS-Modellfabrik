# Gateway-Routing-Pattern für CCU MQTT Topics

## Überblick

Das Gateway-Routing-Pattern implementiert eine klare Trennung der Verantwortlichkeiten für die MQTT-Nachrichtenverarbeitung im CCU-Bereich:

- **ccu_mqtt_client**: Verbindungsaufbau, Reconnect, Subscribe (KEINE Business-Logik)
- **ccu_gateway**: MQTT-Nachrichten empfangen und an zuständige Manager routen
- **sensor_manager & module_manager**: Business-Logik und State-Verarbeitung

## Architektur

```
┌─────────────────────┐
│   MQTT Broker       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  ccu_mqtt_client    │  ← Nur Verbindung & Subscribe
│  - connect()        │
│  - _on_message()    │  → ruft Gateway.on_mqtt_message()
│  - set_gateway()    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   ccu_gateway       │  ← Topic-Routing
│  - on_mqtt_message()│
│  - sensor_topics    │  → Set {'/j1/txt/1/i/bme680', ...}
│  - module_prefixes  │  → List ['module/v1/ff/', ...]
└──────────┬──────────┘
           │
           ├────────────────────┐
           ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│ sensor_manager   │  │ module_manager   │  ← Business-Logik
│ - process_sensor │  │ - process_module │
│ - sensor_data    │  │ - module_status  │
└──────────────────┘  └──────────────────┘
```

## Implementierung

### 1. ccu_mqtt_client.py

**Aufgaben:**
- MQTT-Verbindungsaufbau und -verwaltung
- Subscribe zu Topics (via Registry)
- Message-Buffering für Message Monitor
- **Gateway-Aufruf** (KEINE Business-Logik)

**Wichtige Änderungen:**
```python
class CcuMqttClient:
    def __init__(self):
        # ...
        self._gateway = None  # NEU: Gateway-Referenz
    
    def set_gateway(self, gateway):
        """Gateway für Topic-Routing registrieren"""
        self._gateway = gateway
    
    def _on_message(self, client, userdata, msg):
        """MQTT Callback - ruft NUR Gateway auf"""
        # 1. JSON-Parsing
        # 2. Buffer-Update
        # 3. Gateway-Routing (KEINE Business-Logik!)
        if self._gateway:
            self._gateway.on_mqtt_message(topic, clean_payload)
```

**Entfernt:**
- `_notify_business_functions()` ❌
- `_call_business_function_callback()` ❌

### 2. ccu_gateway.py

**Aufgaben:**
- Empfängt ALLE MQTT-Nachrichten
- Routet Nachrichten anhand von Topics
- Ruft zuständige Manager auf

**Topic-Listen:**
```python
class CcuGateway:
    def __init__(self):
        # Explizite Sensor-Topic-Liste (Set für O(1) Lookup)
        self.sensor_topics = {
            '/j1/txt/1/i/bme680',  # BME680 Sensor
            '/j1/txt/1/i/ldr',     # LDR Sensor
            '/j1/txt/1/i/cam'      # Camera
        }
        
        # Module-Topic-Präfixe (List für flexibles Matching)
        self.module_topic_prefixes = [
            'module/v1/ff/',       # Direkte Module
            'fts/v1/ff/',          # FTS Topics
            'ccu/pairing/state'    # CCU Pairing
        ]
```

**Routing-Logik:**
```python
def on_mqtt_message(self, topic: str, payload: Dict[str, Any]):
    """Gateway-Routing-Methode"""
    
    # Routing 1: Sensor Topics (Set-basiert, O(1))
    if topic in self.sensor_topics:
        sensor_manager = self._get_sensor_manager()
        sensor_manager.process_sensor_message(topic, payload)
        return
    
    # Routing 2: Module Topics (Präfix-basiert)
    for prefix in self.module_topic_prefixes:
        if topic.startswith(prefix):
            module_manager = self._get_module_manager()
            module_manager.process_module_message(topic, payload)
            return
    
    # Unbekanntes Topic: Debug-Logging
    logger.debug(f"❓ No routing for topic: {topic}")
```

**Lazy-Loading für Manager:**
```python
def _get_sensor_manager(self):
    """Lazy Loading - Singleton-kompatibel"""
    if self._sensor_manager is None:
        from omf2.ccu.sensor_manager import get_ccu_sensor_manager
        self._sensor_manager = get_ccu_sensor_manager()
    return self._sensor_manager
```

### 3. Manager (sensor_manager.py & module_manager.py)

**Unverändert** - Manager behalten ihre Business-Logik:

```python
class SensorManager:
    def process_sensor_message(self, topic: str, payload: Dict[str, Any]):
        """Verarbeitet Sensor-Daten und updated State"""
        processed_data = self._extract_sensor_data(topic, payload)
        self.sensor_data[topic] = processed_data

class CcuModuleManager:
    def process_module_message(self, topic: str, payload: Dict[str, Any]):
        """Verarbeitet Module-Status und updated State"""
        module_id = self._extract_module_id_from_topic(topic)
        self.update_module_status(module_id, payload, self.module_status, topic)
```

### 4. gateway_factory.py

**Verkabelung von Client und Gateway:**
```python
def get_ccu_gateway(self):
    # 1. MQTT-Client holen
    ccu_mqtt_client = client_factory.get_mqtt_client('ccu_mqtt_client')
    
    # 2. Gateway erstellen
    ccu_gateway = CcuGateway(mqtt_client=ccu_mqtt_client)
    
    # 3. Gateway im Client registrieren (WICHTIG!)
    ccu_mqtt_client.set_gateway(ccu_gateway)
    
    return ccu_gateway
```

## Topic-Routing-Strategie

### Sensor-Topics (Set-basiert)
- **Performance**: O(1) Lookup
- **Use Case**: Feste, bekannte Topic-Liste
- **Topics**:
  - `/j1/txt/1/i/bme680` → BME680 Sensor-Daten
  - `/j1/txt/1/i/ldr` → LDR Sensor-Daten
  - `/j1/txt/1/i/cam` → Camera-Daten

### Module-Topics (Präfix-basiert)
- **Performance**: O(n) mit n=Anzahl Präfixe (typisch n=3)
- **Use Case**: Flexibles Matching für verschiedene Module-IDs
- **Präfixe**:
  - `module/v1/ff/` → Direkte Module (z.B. SVR3QA0022/state)
  - `fts/v1/ff/` → FTS Topics
  - `ccu/pairing/state` → CCU Pairing State (globaler Status)
  
**Beispiele:**
```
module/v1/ff/SVR3QA0022/state       → module_manager
module/v1/ff/SVR4H76449/connection  → module_manager
fts/v1/ff/5iO4/state                → module_manager
ccu/pairing/state                   → module_manager
```

## Vorteile

### 1. Separation of Concerns
- **ccu_mqtt_client**: Nur Verbindung & Transport
- **ccu_gateway**: Nur Routing
- **Manager**: Nur Business-Logik

### 2. Wartbarkeit
- Topic-Listen sind zentral im Gateway
- Einfach erweiterbar: Neue Topics in Listen hinzufügen
- Klare Struktur für neue Entwickler

### 3. Testbarkeit
```python
# Gateway isoliert testen
gateway = CcuGateway(mqtt_client=None)
gateway.on_mqtt_message('/j1/txt/1/i/bme680', {'t': 25.5})

# Manager isoliert testen
sensor_manager = SensorManager()
sensor_manager.process_sensor_message(topic, payload)
```

### 4. Performance
- Set-basiertes Lookup für Sensor-Topics: O(1)
- Präfix-basiertes Matching für Module-Topics: O(n) mit kleinem n

### 5. Singleton-Kompatibilität
- Lazy-Loading der Manager
- Manager-Singleton-Pattern bleibt erhalten
- Factory-Funktion-basierte Instanziierung

## Erweiterung

### Neue Sensor-Topics hinzufügen:
```python
# In ccu_gateway.py
self.sensor_topics = {
    '/j1/txt/1/i/bme680',
    '/j1/txt/1/i/ldr',
    '/j1/txt/1/i/cam',
    '/j1/txt/1/i/new_sensor'  # ← NEU
}
```

### Neue Module-Topic-Präfixe hinzufügen:
```python
# In ccu_gateway.py
self.module_topic_prefixes = [
    'module/v1/ff/',
    'fts/v1/ff/',
    'ccu/pairing/state',
    'new_module_prefix/'  # ← NEU
]
```

### Neuen Manager hinzufügen:
```python
# 1. Manager-Instanz als Lazy-Loading
self._new_manager = None

def _get_new_manager(self):
    if self._new_manager is None:
        from omf2.ccu.new_manager import get_new_manager
        self._new_manager = get_new_manager()
    return self._new_manager

# 2. Routing-Logik erweitern
def on_mqtt_message(self, topic: str, payload: Dict[str, Any]):
    # ... existing routing ...
    
    # Routing 3: New Manager Topics
    if topic.startswith('new_prefix/'):
        new_manager = self._get_new_manager()
        new_manager.process_message(topic, payload)
        return
```

## Registry-Integration

Die Topic-Listen im Gateway sind aktuell **hardcodiert** für maximale Klarheit und Wartbarkeit.

**Alternative**: Registry-basierte Topic-Listen (aus mqtt_clients.yml):
```python
def __init__(self):
    # Load topics from registry
    business_functions = self.registry_manager.get_business_functions('ccu_mqtt_client')
    
    self.sensor_topics = set(
        business_functions['sensor_manager']['subscribed_topics']
    )
    
    self.module_topics = set(
        business_functions['module_manager']['subscribed_topics']
    )
```

**Vorteil**: Zentralisierung in Registry
**Nachteil**: Weniger explizit, schwerer zu debuggen

## Tests

Siehe `tests/test_omf2/test_ccu_gateway_routing.py`:

```bash
python3 tests/test_omf2/test_ccu_gateway_routing.py
```

**Test-Coverage:**
- ✅ Gateway hat korrekte Topic-Listen
- ✅ Gateway kann Manager instanziieren
- ✅ MQTT-Client hat keine Business-Logik mehr
- ✅ Gateway-Routing funktioniert
- ✅ Manager haben ihre Callback-Methoden
- ✅ Factory verbindet Gateway und Client korrekt

## Migration

Falls bestehende Code-Stellen direkt auf den MQTT-Client zugreifen:

**Alt (DEPRECATED):**
```python
# NICHT MEHR: Business-Functions direkt im MQTT-Client
mqtt_client._notify_business_functions(topic, payload)
```

**Neu:**
```python
# Über Gateway routen
gateway = get_ccu_gateway()
gateway.on_mqtt_message(topic, payload)
```

## Zusammenfassung

✅ **Akzeptanzkriterien erfüllt:**
- ccu_mqtt_client hat KEINE Business-Logik mehr
- ccu_gateway routet alle Topics klar und wartbar
- Manager behalten ihre Business-Logik und State
- Topic-Listen sind leicht erweiterbar und testbar
- Lösung ist kompatibel mit Singleton-Pattern

✅ **Implementation Pattern:**
- Gateway-Pattern für Topic-Routing
- Lazy-Loading für Manager-Instanzen
- Set-basiertes Lookup für Performance
- Präfix-basiertes Matching für Flexibilität

✅ **Code-Qualität:**
- Klare Separation of Concerns
- Gut testbar (Unit-Tests vorhanden)
- Einfach erweiterbar
- Singleton-kompatibel
