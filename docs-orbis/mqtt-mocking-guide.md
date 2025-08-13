# MQTT Mocking Guide - Fischertechnik Agile Production Simulation

Dieser Guide erklärt, wie du die MQTT-Schnittstelle der Fischertechnik Module mocken kannst, um die Steuerung über MQTT-Nachrichten zu testen.

## 🎯 **Ziel**

- **MQTT-Schnittstelle mocken** ohne echte Hardware
- **Module über MQTT steuern** mit lokaler oder Cloud-Applikation
- **VDA 5050 State Machine** implementieren
- **Realistische Simulation** der Produktionsmodule

## 📋 **Schritt-für-Schritt Anleitung**

### **Schritt 1: MQTT Broker Setup**

#### **Option A: Lokaler MQTT Broker (Mosquitto)**
```bash
# Installation (macOS)
brew install mosquitto

# Start MQTT Broker
mosquitto -p 1883

# Oder als Service starten
brew services start mosquitto
```

#### **Option B: Docker MQTT Broker**
```bash
# MQTT Broker mit Docker
docker run -d --name mqtt-broker \
  -p 1883:1883 \
  -p 9001:9001 \
  eclipse-mosquitto:latest
```

### **Schritt 2: Python Dependencies**

```bash
# Installiere zusätzliche Dependencies
pip install paho-mqtt

# Oder füge zu requirements.txt hinzu
echo "paho-mqtt>=1.6.1" >> requirements.txt
pip install -r requirements.txt
```

### **Schritt 3: Mock System Starten**

```bash
# Starte das Mock System
cd src-orbis
python mqtt_mock.py
```

**Erwartete Ausgabe:**
```
2024-01-15 10:30:00 - INFO - Connected to MQTT broker
2024-01-15 10:30:00 - INFO - MQTT Mock System started
2024-01-15 10:30:00 - INFO - Added module: MILL (FF22-001)
2024-01-15 10:30:00 - INFO - Added module: DRILL (FF22-002)
...
```

### **Schritt 4: Test Client Starten**

```bash
# In einem neuen Terminal
cd src-orbis
python mqtt_test_client.py
```

## 🔧 **MQTT Topic Struktur**

### **Topic Format**
```
module/v1/ff/{serialNumber}/{action}
```

### **Verfügbare Topics**

| Topic | Direction | Purpose |
|-------|-----------|---------|
| `module/v1/ff/{serialNumber}/order` | → | Bestellungen senden |
| `module/v1/ff/{serialNumber}/instantAction` | → | Sofortige Aktionen |
| `module/v1/ff/{serialNumber}/state` | ← | Status-Updates empfangen |
| `module/v1/ff/{serialNumber}/connection` | ← | Verbindungsstatus |
| `module/v1/ff/{serialNumber}/factsheet` | ← | Modul-Konfiguration |

### **Serial Numbers der Mock Module**

| Modul | Serial Number | Typ |
|-------|---------------|-----|
| MILL #1 | `FF22-001` | Milling |
| DRILL #1 | `FF22-002` | Drilling |
| OVEN #1 | `FF22-003` | Heat Treatment |
| AIQS #1 | `FF22-004` | Quality Inspection |
| HBW #1 | `FF22-005` | Storage |
| DPS | `FF22-006` | Central Control |

## 📨 **MQTT Nachrichten Format**

### **Order Message (Senden)**
```json
{
  "serialNumber": "FF22-001",
  "orderId": "order-123",
  "orderUpdateId": 1,
  "action": {
    "id": "action-456",
    "command": "MILL",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300
    }
  }
}
```

### **Instant Action Message (Senden)**
```json
{
  "serialNumber": "FF22-001",
  "orderId": "order-789",
  "orderUpdateId": 1,
  "actions": [
    {
      "actionId": "action-101",
      "actionType": "reset",
      "metadata": {}
    }
  ]
}
```

### **State Message (Empfangen)**
```json
{
  "headerId": 123,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "serialNumber": "FF22-001",
  "actionState": {
    "id": "action-456",
    "state": "RUNNING",
    "command": "MILL",
    "metadata": {}
  },
  "loads": [],
  "errors": [],
  "paused": false,
  "operatingMode": "AUTOMATIC",
  "orderId": "order-123",
  "orderUpdateId": 1
}
```

## 🔄 **State Machine (VDA 5050)**

### **Action States**
1. **PENDING** - Aktion empfangen, wartet auf Start
2. **RUNNING** - Aktion wird ausgeführt
3. **FINISHED** - Aktion erfolgreich abgeschlossen
4. **FAILED** - Aktion fehlgeschlagen

### **Verarbeitungszeiten**
| Command | Zeit (Sekunden) |
|---------|-----------------|
| PICK | 3.0 |
| DROP | 2.0 |
| MILL | 10.0 |
| DRILL | 8.0 |
| HEAT | 15.0 |
| CHECK_QUALITY | 5.0 |
| STORE | 4.0 |
| RETRIEVE | 4.0 |

## 🧪 **Testing**

### **Manuelles Testing mit MQTT Client**

#### **Order senden:**
```bash
# Mit mosquitto_pub
mosquitto_pub -h localhost -p 1883 -t "module/v1/ff/FF22-001/order" \
  -m '{"serialNumber":"FF22-001","orderId":"test-123","orderUpdateId":1,"action":{"id":"action-456","command":"MILL","metadata":{"priority":"NORMAL","timeout":300}}}'
```

#### **Status empfangen:**
```bash
# Mit mosquitto_sub
mosquitto_sub -h localhost -p 1883 -t "module/v1/ff/+/state"
```

### **Automatisiertes Testing**
```bash
# Demo ausführen
python mqtt_test_client.py
```

## 🔍 **Debugging**

### **Logs überwachen**
```bash
# Mock System Logs
tail -f mqtt_mock.log

# MQTT Broker Logs (Mosquitto)
tail -f /usr/local/var/log/mosquitto.log
```

### **MQTT Topics überwachen**
```bash
# Alle Topics überwachen
mosquitto_sub -h localhost -p 1883 -t "module/v1/ff/#" -v
```

## 🚀 **Integration mit Fischertechnik Apps**

### **Lokale Applikation**
- **MQTT Broker**: `localhost:1883`
- **Topics**: `module/v1/ff/{serialNumber}/*`
- **QoS**: 1 (At least once delivery)

### **Cloud Applikation**
- **MQTT Broker**: Fischertechnik Cloud
- **Topics**: `module/v1/ff/{serialNumber}/*`
- **Authentication**: Fischertechnik Credentials

## 📊 **Monitoring**

### **Status Dashboard**
```python
# Einfaches Status Monitoring
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}")
    print(f"Payload: {msg.payload.decode()}")

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("module/v1/ff/+/state")
client.loop_forever()
```

### **Web Interface (Optional)**
```bash
# MQTT Web Client installieren
npm install -g mqtt-web-client

# Web Interface starten
mqtt-web-client --port 8080
```

## 🔧 **Erweiterte Konfiguration**

### **Custom Module hinzufügen**
```python
# In mqtt_mock.py
mock_system = MQTTMockSystem()
mock_system.add_module("FF22-007", "CUSTOM_MODULE")
```

### **Custom Commands hinzufügen**
```python
# In FischertechnikModuleMock._get_processing_time()
processing_times = {
    "PICK": 3.0,
    "DROP": 2.0,
    "CUSTOM_COMMAND": 7.0,  # Neue Kommando
    # ...
}
```

## 🚨 **Troubleshooting**

### **Häufige Probleme**

1. **MQTT Broker nicht erreichbar**
   ```bash
   # Teste Verbindung
   mosquitto_pub -h localhost -p 1883 -t "test" -m "hello"
   ```

2. **Module reagieren nicht**
   - Prüfe Serial Numbers
   - Prüfe Topic Format
   - Prüfe JSON Format

3. **State Transitions funktionieren nicht**
   - Prüfe Logs
   - Prüfe MQTT QoS Settings
   - Prüfe Network Connectivity

### **Debug Commands**
```bash
# MQTT Broker Status
brew services list | grep mosquitto

# Port Check
netstat -an | grep 1883

# MQTT Client Test
mosquitto_pub -h localhost -p 1883 -t "test" -m "test"
mosquitto_sub -h localhost -p 1883 -t "test"
```

---

*Dieser Guide ermöglicht es dir, die Fischertechnik Module vollständig über MQTT zu steuern, ohne echte Hardware zu benötigen.*
