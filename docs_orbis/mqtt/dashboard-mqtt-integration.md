# 🔗 MQTT Integration - OMF Dashboard

## 📋 Overview

Das **OMF Dashboard** verwendet die **Per-Topic-Buffer Architektur** für MQTT-Nachrichtenverarbeitung. Diese moderne Architektur kombiniert das **MQTT-Singleton Pattern** mit effizienten **Per-Topic-Buffers** für optimale Performance und Einfachheit.

## ✅ Aktuelle MQTT Architektur

### 1. **MQTT-Singleton Pattern**
- **Eine MQTT-Client-Instanz** pro Streamlit-Session
- **Zentraler Zugriff** über `st.session_state["mqtt_client"]`
- **Automatische Verbindung** beim Dashboard-Start
- **Umgebungswechsel** (live/mock/replay) ohne Verbindungsabbruch

### 2. **Per-Topic-Buffer System**
- **Topic-spezifische Buffer** für jede MQTT-Subscription
- **Automatische Nachrichtensammlung** in separaten Buffers
- **Effiziente Verarbeitung** ohne Message-Processor Overhead
- **Direkte Buffer-Zugriffe** für optimale Performance

### 3. **Hybrid-Architektur für Publishing**
- **MessageGenerator** für Payload-Erstellung
- **Session State** für Preview/Edit-Funktionalität
- **MqttGateway** für finales Publishing
- **WorkflowOrderManager** für orderId/orderUpdateId Verwaltung

## 🎮 Dashboard MQTT Features

### **1. Connection Status**
```
🔗 MQTT Connection Status
├── ✅ MQTT Verbunden / ❌ MQTT Nicht verbunden
├── Broker: 192.168.0.100:1883 (live) / localhost:1883 (replay)
├── Environment: live/mock/replay
└── Session: Singleton-Instanz
```

### **2. Message Center**
- **Priority-based Subscriptions**: PRIO 1-6 für verschiedene Topic-Filter
- **Per-Topic-Buffer**: Effiziente Nachrichtenverarbeitung
- **Live Message Display**: Echtzeit-Anzeige empfangener Nachrichten
- **Test-Bereich**: MQTT-Nachrichten senden und testen

### **3. Factory Steering**
- **FTS Navigation**: DPS-HBW, HBW-DPS, Produktions-Routen
- **Module Sequences**: AIQS, MILL, DRILL mit Sequenzklammer
- **Factory Reset**: Kompletter Factory-Reset
- **Order Commands**: ROT, WEISS, BLAU Aufträge

## 📤 MQTT Message Processing

### **Per-Topic-Buffer Pattern**
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

### **Hybrid Publishing Pattern**
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

## 📊 Message Center Features

### **Priority-based Subscriptions**
- **PRIO 1**: Module-spezifische Topics
- **PRIO 2**: FTS-spezifische Topics  
- **PRIO 3**: Order-spezifische Topics
- **PRIO 4**: System-spezifische Topics
- **PRIO 5**: Erweiterte Topics
- **PRIO 6**: Alle Topics (`#`)

### **Per-Topic-Buffer Verarbeitung**
```python
def show_message_center():
    # Priority-basierte Subscriptions
    priority_level = st.session_state.get("mc_priority", 1)
    
    if priority_level >= 6:
        # Alle Topics
        client.subscribe("#")
    else:
        # Spezifische Topics basierend auf Priority
        filters = get_priority_filters(priority_level)
        client.subscribe_many(filters)
    
    # Per-Topic-Buffer abrufen und verarbeiten
    for topic_filter in active_filters:
        messages = list(client.get_buffer(topic_filter))
        _display_messages(messages)
```

## 🏭 Factory Steering Features

### **FTS Navigation**
```python
def _prepare_navigation_message(navigation_type: str):
    # MessageGenerator verwenden
    generator = get_omf_message_generator()
    
    # Route-Typ mapping
    route_mapping = {
        "DPS-HBW": "DPS_HBW",
        "HBW-DPS": "HBW_DPS", 
        "RED-Prod": "RED_Prod",
        "BLUE-Prod": "BLUE_Prod",
        "WHITE-Prod": "WHITE_Prod"
    }
    
    # Navigation Message generieren
    message = generator.generate_fts_navigation_message(
        route_type=route_mapping[navigation_type],
        load_type=load_type_mapping[navigation_type]
    )
    
    # Session State für Preview
    st.session_state["pending_message"] = {
        "topic": message["topic"],
        "payload": message["payload"],
        "type": "navigation"
    }
```

### **Module Sequences**
```python
def _prepare_module_sequence(module_name: str, commands: list):
    # Sequenz-Messages erstellen
    sequence_messages = []
    order_id = str(uuid.uuid4())
    
    for i, command in enumerate(commands, 1):
        message = {
            "topic": f"module/v1/ff/{serial_number}/order",
            "payload": {
                "serialNumber": serial_number,
                "orderId": order_id,
                "orderUpdateId": i,  # Inkrementierend
                "action": {
                    "id": str(uuid.uuid4()),
                    "command": command,
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            },
            "step": i,
            "command": command,
            "module": module_name
        }
        sequence_messages.append(message)
    
    # Im Session State speichern
    st.session_state["module_sequence"] = {
        "module": module_name,
        "order_id": order_id,
        "messages": sequence_messages,
        "total_steps": len(commands)
    }
```

## 🔧 Technische Implementation

### **1. MQTT-Singleton Factory**
```python
def ensure_dashboard_client(environment: str, config: dict) -> OMFMqttClient:
    """Erstellt oder gibt existierenden MQTT-Client zurück (Singleton)"""
    if "mqtt_client" not in st.session_state:
        st.session_state["mqtt_client"] = OMFMqttClient(environment, config)
    return st.session_state["mqtt_client"]
```

### **2. Per-Topic-Buffer System**
```python
class OMFMqttClient:
    def __init__(self, environment: str, config: dict):
        self._buffers = {}  # Per-Topic-Buffer
        self._connected = False
        
    def subscribe_many(self, topics: list):
        """Subscribe zu mehreren Topics"""
        for topic in topics:
            self.subscribe(topic)
            
    def get_buffer(self, topic_filter: str) -> list:
        """Gibt Buffer für Topic-Filter zurück"""
        return self._buffers.get(topic_filter, [])
```

### **3. MqttGateway**
```python
class MqttGateway:
    def __init__(self, mqtt_client: OMFMqttClient):
        self.mqtt_client = mqtt_client
        
    def send(self, topic: str, builder: callable, ensure_order_id: bool = False) -> bool:
        """Sendet Nachricht über MQTT-Client"""
        payload = builder()
        
        if ensure_order_id:
            payload = self._ensure_order_id(payload)
            
        return self.mqtt_client.publish_json(topic, payload, qos=1, retain=False)
```

## 🚀 Usage Examples

### **1. Message Center nutzen**
1. **Tab öffnen**: "📨 Nachrichten-Zentrale"
2. **Priority wählen**: Slider für Topic-Filter
3. **Messages anzeigen**: Per-Topic-Buffer wird angezeigt
4. **Test-Bereich**: Eigene Nachrichten senden

### **2. Factory Steering nutzen**
1. **Tab öffnen**: "🎮 Steering" → "Factory Steering"
2. **Navigation**: FTS-Routen auswählen und senden
3. **Module Sequences**: AIQS/MILL/DRILL Sequenzen
4. **Factory Reset**: Kompletter Reset

### **3. Overview Module Status**
1. **Tab öffnen**: "📊 Übersicht" → "🏭 Modul Status"
2. **Per-Topic-Buffer**: Automatische Verarbeitung
3. **Live Updates**: Echtzeit-Status-Anzeige

## 📈 Performance Features

### **1. Per-Topic-Buffer Vorteile**
- **Keine Message-Processor Overhead**
- **Direkte Buffer-Zugriffe**
- **Effiziente Topic-Filterung**
- **Einfache Erweiterung**

### **2. MQTT-Singleton Vorteile**
- **Eine Client-Instanz** pro Session
- **Stabile Verbindungen**
- **Umgebungswechsel** ohne Probleme
- **Konsistente Architektur**

### **3. Hybrid-Architektur Vorteile**
- **MessageGenerator** für korrekte Payloads
- **Session State** für Preview/Edit
- **MqttGateway** für sauberes Publishing
- **WorkflowOrderManager** für ID-Management

## 🔒 Security & Reliability

### **1. MQTT-Singleton Pattern**
- **Eine Client-Instanz** pro Session
- **Keine Verletzung** des Singleton-Patterns
- **Stabile Verbindungen**
- **Konsistente Architektur**

### **2. Per-Topic-Buffer Reliability**
- **Topic-spezifische Buffer**
- **Automatische Nachrichtensammlung**
- **Effiziente Verarbeitung**
- **Robuste Error-Handling**

### **3. MqttGateway Security**
- **Payload-Validierung**
- **Order-ID Management**
- **QoS Level 1** (At least once delivery)
- **Error Recovery**

## 📝 Error Handling

### **1. MQTT Connection Errors**
```python
if not mqtt_client.connected:
    st.error("❌ MQTT nicht verbunden")
    return
```

### **2. Buffer Access Errors**
```python
try:
    messages = list(client.get_buffer("topic"))
    if not messages:
        st.warning("⚠️ Keine Nachrichten im Buffer")
        return
except Exception as e:
    st.error(f"❌ Buffer-Fehler: {e}")
```

### **3. Message Send Errors**
```python
success = gateway.send(topic, builder, ensure_order_id=True)
if not success:
    st.error("❌ Fehler beim Senden der Nachricht")
```

## 🔄 Architecture Patterns

### **1. Per-Topic-Buffer Pattern**
- **Subscription**: `client.subscribe_many(topics)`
- **Buffer Access**: `client.get_buffer(topic_filter)`
- **Processing**: Direkte Verarbeitung der Buffer

### **2. Hybrid Publishing Pattern**
- **Payload Generation**: `MessageGenerator`
- **Preview/Edit**: `Session State`
- **Publishing**: `MqttGateway`

### **3. MQTT-Singleton Pattern**
- **Client Creation**: `ensure_dashboard_client()`
- **Session Storage**: `st.session_state["mqtt_client"]`
- **Consistent Access**: Eine Instanz pro Session

## 📄 Files

### **Core Architecture:**
- **`omf_mqtt_factory.py`**: MQTT-Singleton Factory
- **`omf_mqtt_client.py`**: Per-Topic-Buffer Client
- **`message_gateway.py`**: Hybrid Publishing Gateway
- **`message_generator.py`**: Payload Generation

### **Dashboard Components:**
- **`message_center.py`**: Priority-based Subscriptions
- **`steering_factory.py`**: Factory Steering mit Hybrid-Architektur
- **`overview_module_status.py`**: Per-Topic-Buffer Verarbeitung
- **`fts_instantaction.py`**: FTS-spezifische Buffer-Verarbeitung

### **Configuration:**
- **`mqtt_config.py`**: MQTT-Konfiguration
- **`mqtt_topics.py`**: Topic-Definitionen und Priority-Filter

---

**Status**: ✅ **COMPLETED** - Per-Topic-Buffer Architektur erfolgreich implementiert