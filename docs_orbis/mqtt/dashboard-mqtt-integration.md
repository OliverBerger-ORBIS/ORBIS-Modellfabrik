# 🔗 MQTT Integration - APS Dashboard

## 📋 Overview

Das **APS Dashboard** wurde erfolgreich um **echten MQTT-Versand** erweitert. Alle MQTT-Nachrichten werden jetzt **direkt aus dem Dashboard** an die APS-Module gesendet.

## ✅ Neue MQTT Features

### 1. **Echte MQTT-Verbindung**
- **Automatische Verbindung** beim Dashboard-Start
- **Broker**: `192.168.0.100:1883`
- **Credentials**: `default`/`default`
- **QoS Level**: 1 (At least once delivery)

### 2. **MQTT Control Interface**
- **Connection Status**: Live-Verbindungsstatus
- **Message Counter**: Gesendete Nachrichten und Antworten
- **Real-time Monitoring**: Live-Überwachung der MQTT-Kommunikation

### 3. **Direkter MQTT-Versand**
- **Template Messages**: Vordefinierte Nachrichten senden
- **Custom Orders**: Benutzerdefinierte Befehle senden
- **Module Overview**: Schnell-Befehle für alle Module

## 🎮 MQTT Control Tab Features

### **1. Connection Status**
```
🔗 MQTT Connection Status
├── ✅ MQTT Verbunden / ❌ MQTT Nicht verbunden
├── Broker: 192.168.0.100:1883
├── Gesendete Nachrichten: X
└── Empfangene Antworten: Y
```

### **2. Steuerungsmethoden**
- **Template Message**: Vordefinierte, funktionierende Nachrichten
- **Custom Order**: Benutzerdefinierte Befehle mit Metadaten
- **Module Overview**: Detaillierte Modul-Informationen
- **MQTT Monitor**: Live-Überwachung der Kommunikation

## 📤 MQTT Message Sending

### **Template Message Control**
```python
# Automatische Nachrichten-Erstellung
message = create_message_from_template("DRILL_PICK_WHITE")
topic = self.message_library.get_topic("DRILL", "order")
success = self.send_mqtt_message_direct(topic, message)
```

### **Custom Order Control**
```python
# Benutzerdefinierte Nachrichten
metadata = {
    "priority": "NORMAL",
    "timeout": 300,
    "type": "WHITE"
}
message = self.message_library.create_order_message("DRILL", "PICK", metadata)
topic = self.message_library.get_topic("DRILL", "order")
success = self.send_mqtt_message_direct(topic, message)
```

### **Message Format**
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "993e21ec-88b5-4e50-a478-a3f64a43097b",
  "orderUpdateId": 1,
  "action": {
    "id": "5f5f2fe2-1bdd-4f0e-84c6-33c44d75f07e",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

## 📊 MQTT Monitor

### **Gesendete Nachrichten**
- **Zeitstempel**: Wann wurde gesendet
- **Topic**: MQTT-Topic der Nachricht
- **Message**: Vollständige JSON-Nachricht
- **Result**: Send-Status (0 = Erfolg)

### **Empfangene Antworten**
- **Zeitstempel**: Wann wurde empfangen
- **Topic**: MQTT-Topic der Antwort
- **Payload**: Antwort-Payload (JSON)
- **QoS**: Quality of Service Level

### **Monitor Features**
- **Live Updates**: Echtzeit-Aktualisierung
- **Expandable Details**: Vollständige Nachrichten anzeigen
- **Clear Functions**: Nachrichten und Antworten löschen
- **Recent History**: Letzte 5 Nachrichten/Antworten

## 🔧 Technische Implementation

### **1. MQTT Client Setup**
```python
def setup_mqtt_client(self):
    self.mqtt_client = mqtt.Client()
    self.mqtt_client.username_pw_set(self.mqtt_username, self.mqtt_password)
    self.mqtt_client.on_connect = self._on_mqtt_connect
    self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
    self.mqtt_client.on_message = self._on_mqtt_message
```

### **2. Connection Management**
```python
def connect_mqtt(self):
    self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
    self.mqtt_client.loop_start()
    time.sleep(1)  # Wait for connection
    return self.mqtt_connected
```

### **3. Message Sending**
```python
def send_mqtt_message_direct(self, topic, message):
    if not self.mqtt_connected:
        self.connect_mqtt()
    
    message_json = json.dumps(message) if isinstance(message, dict) else str(message)
    result = self.mqtt_client.publish(topic, message_json, qos=1)
    
    # Store sent message
    sent_info = {
        'timestamp': datetime.now(),
        'topic': topic,
        'message': message,
        'result': result.rc
    }
    self.mqtt_messages_sent.append(sent_info)
    
    return result.rc == mqtt.MQTT_ERR_SUCCESS
```

### **4. Response Handling**
```python
def _on_mqtt_message(self, client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    response_info = {
        'timestamp': datetime.now(),
        'topic': msg.topic,
        'payload': payload,
        'qos': msg.qos
    }
    self.mqtt_responses.append(response_info)
```

## 🚀 Usage Examples

### **1. Template Message Senden**
1. **Tab öffnen**: "🎮 MQTT Control"
2. **Methode wählen**: "Template Message"
3. **Template auswählen**: `DRILL_PICK_WHITE`
4. **Message senden**: Button klicken
5. **Ergebnis**: Live-Feedback und JSON-Anzeige

### **2. Custom Order Erstellen**
1. **Methode wählen**: "Custom Order"
2. **Modul auswählen**: DRILL
3. **Befehl wählen**: PICK
4. **Metadaten konfigurieren**: Type, Priority, Timeout
5. **Message senden**: Button klicken

### **3. MQTT Monitor Nutzen**
1. **Methode wählen**: "MQTT Monitor"
2. **Gesendete Nachrichten**: Anzeige der letzten 5 Nachrichten
3. **Empfangene Antworten**: Anzeige der letzten 5 Antworten
4. **Clear Functions**: Nachrichten/Antworten löschen

## 📈 Performance Features

### **1. Connection Management**
- **Automatic Reconnection**: Automatische Wiederverbindung
- **Connection Status**: Live-Status-Anzeige
- **Error Handling**: Robuste Fehlerbehandlung

### **2. Message Tracking**
- **Message History**: Gesendete Nachrichten speichern
- **Response Monitoring**: Empfangene Antworten tracken
- **Real-time Updates**: Live-Aktualisierung der Anzeige

### **3. User Experience**
- **Loading Indicators**: Spinner während Verbindungsaufbau
- **Success/Error Messages**: Klare Feedback-Nachrichten
- **JSON Preview**: Vollständige Nachrichten-Anzeige

## 🔒 Security & Reliability

### **1. Authentication**
- **Username/Password**: `default`/`default`
- **Secure Connection**: MQTT über TCP
- **Error Handling**: Sichere Fehlerbehandlung

### **2. Message Reliability**
- **QoS Level 1**: At least once delivery
- **Message Validation**: JSON-Validierung
- **Error Recovery**: Automatische Wiederholung

### **3. Connection Stability**
- **Keep-Alive**: 60 Sekunden
- **Reconnection Logic**: Automatische Wiederverbindung
- **Graceful Shutdown**: Ordentliches Beenden

## 📝 Error Handling

### **1. Connection Errors**
```python
if not self.connect_mqtt():
    st.error("MQTT-Verbindung fehlgeschlagen")
    return False
```

### **2. Message Send Errors**
```python
success, result_message = self.send_mqtt_message_direct(topic, message)
if not success:
    st.error(f"MQTT-Versand fehlgeschlagen: {result_message}")
```

### **3. JSON Parse Errors**
```python
try:
    payload = json.loads(msg.payload.decode())
except Exception as e:
    st.warning(f"MQTT Response Parse Error: {e}")
```

## 🔄 Future Enhancements

### **1. Advanced Monitoring**
- **Message Statistics**: Detaillierte Statistiken
- **Performance Metrics**: Ausführungszeiten
- **Error Tracking**: Erweiterte Fehlerprotokollierung

### **2. Enhanced Control**
- **Batch Operations**: Mehrere Nachrichten gleichzeitig
- **Scheduled Messages**: Geplante Nachrichten
- **Conditional Logic**: Bedingte Nachrichten

### **3. Integration Features**
- **Database Logging**: MQTT-Nachrichten in DB speichern
- **Export Functions**: Nachrichten exportieren
- **API Integration**: REST-API für externe Steuerung

## 📄 Files

### **Modified Files:**
- **`aps_dashboard.py`**: Haupt-Dashboard mit MQTT-Integration

### **New Features:**
- **MQTT Client**: Vollständiger MQTT-Client
- **Connection Management**: Automatische Verbindungsverwaltung
- **Message Sending**: Echter MQTT-Versand
- **Response Monitoring**: Live-Antwort-Überwachung
- **Error Handling**: Robuste Fehlerbehandlung

---

**Status**: ✅ **COMPLETED** - Echter MQTT-Versand erfolgreich integriert
