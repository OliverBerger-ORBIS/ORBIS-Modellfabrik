# MQTT Traffic Logging Guide - Fischertechnik APS

**Status:** Aktive Dokumentation für OSF  
**Quelle:** Aus Legacy-Archiv übernommen (04-howto_omf_legacy entfernt 2026-02-18)

Dieser Guide erklärt, wie du den MQTT-Traffic zwischen Fischertechnik Cloud und lokaler APS überwachen und analysieren kannst.

## 🎯 **Übersicht**

### **Architektur mit Traffic Logging:**
```
Fischertechnik Cloud ←→ MQTT Bridge Logger ←→ TXT 4.0 Controller ←→ Module
                              ↓
                        Traffic Logging
                              ↓
                    Log Files + Database
```

### **Comprehensive Monitoring (Empfohlen):**
```
Raspberry Pi Broker (192.168.0.100) ←→ Comprehensive Logger ←→ Alle Nachrichten
Secondary Broker (192.168.2.189)    ←→ Comprehensive Logger ←→ Alle Nachrichten  
Docker Broker (host.docker.internal) ←→ Comprehensive Logger ←→ Alle Nachrichten
Container Broker (mqtt-broker)       ←→ Comprehensive Logger ←→ Alle Nachrichten
                              ↓
                    Vollständige Transparenz
                              ↓
                    Log Files + Database + Analysis
```

### **Vorteile:**
- ✅ **Vollständige Transparenz** über alle MQTT-Nachrichten
- ✅ **Non-intrusive** - keine Änderung am bestehenden System
- ✅ **Real-time Monitoring** mit Statistiken
- ✅ **Detaillierte Analyse** mit Visualisierungen
- ✅ **Debugging** von Kommunikationsproblemen
- ✅ **Alle MQTT-Broker** werden überwacht
- ✅ **Automatische Klassifizierung** von Nachrichten-Typen
- ✅ **Broker-spezifische Statistiken**

## 🔧 **Setup**

### **1. MQTT Bridge Logger starten (Einzelner Broker)**
```bash
cd src-orbis

# Grundkonfiguration
python mqtt_bridge_logger.py --cloud-broker 192.168.0.100 --cloud-port 1883

# Mit Authentifizierung
python mqtt_bridge_logger.py \
  --cloud-broker 192.168.0.100 \
  --cloud-port 1883 \
  --username user \
  --password pass

# Mit custom Log-Dateien
python mqtt_bridge_logger.py \
  --cloud-broker 192.168.0.100 \
  --log-file fischertechnik_traffic.log \
  --db-file fischertechnik_traffic.db
```

### **2. Comprehensive MQTT Logger starten (Alle Broker)**
```bash
cd src-orbis

# Alle bekannten MQTT-Broker überwachen
python comprehensive_mqtt_logger.py

# Mit custom Log-Dateien
python comprehensive_mqtt_logger.py \
  --log-file comprehensive_traffic.log \
  --db-file comprehensive_traffic.db

# Mit angepasster Statistik-Intervall
python comprehensive_mqtt_logger.py --stats-interval 30
```

### **2. Traffic Analyzer verwenden**
```bash
# Zusammenfassung anzeigen
python mqtt_traffic_analyzer.py

# Mit Visualisierungen
python mqtt_traffic_analyzer.py --create-charts

# Export zu CSV
python mqtt_traffic_analyzer.py --export-csv traffic_export.csv
```

## 📊 **Was wird geloggt?**

### **Alle MQTT-Nachrichten:**
- **Timestamp** - Exakte Zeitstempel
- **Direction** - Cloud → Local oder Local → Cloud
- **Topic** - Vollständiger MQTT-Topic
- **Payload** - JSON oder Text-Inhalt
- **QoS** - Quality of Service Level
- **Retained** - Retained Flag

### **Comprehensive Logger zusätzlich:**
- **Broker Name** - Welcher MQTT-Broker
- **Broker Host** - IP-Adresse und Port
- **Source Type** - Automatische Klassifizierung:
  - `FISCHERTECHNIK_MODULE` - Module-Kommunikation
  - `OPC_UA` - OPC-UA Topics
  - `TXT4_CONTROLLER` - TXT4.0 Controller
  - `RASPBERRY_PI` - Raspberry Pi System
  - `DOCKER` - Container-Kommunikation
  - `SYSTEM` - System-Nachrichten
  - `STATUS` - Status-Updates
  - `CONFIGURATION` - Konfiguration
  - `DEBUG` - Debug-Nachrichten
  - `ERROR` - Fehler-Nachrichten

### **Statistiken:**
- **Message Count** - Gesamtanzahl Nachrichten
- **Direction Count** - Nachrichten pro Richtung
- **Unique Topics** - Anzahl verschiedener Topics
- **Module Activity** - Aktivität pro Modul

## 🔍 **Verwendung**

### **1. Real-time Monitoring**

#### **Bridge Logger (Einzelner Broker):**
```bash
# Bridge Logger starten
python mqtt_bridge_logger.py --cloud-broker 192.168.0.100

# Ausgabe:
# 📨 CLOUD_TO_LOCAL: module/v1/ff/FF22-001/order
#    Payload: {"serialNumber":"FF22-001","orderId":"123","action":{"command":"MILL"}}
# 📨 LOCAL_TO_CLOUD: module/v1/ff/FF22-001/state
#    Payload: {"actionState":{"state":"RUNNING"}}
```

#### **Comprehensive Logger (Alle Broker):**
```bash
# Comprehensive Logger starten
python comprehensive_mqtt_logger.py

# Ausgabe:
# 📨 RASPBERRY_PI: module/v1/ff/FF22-001/order (FISCHERTECHNIK_MODULE)
#    Payload: {"serialNumber":"FF22-001","orderId":"123","action":{"command":"MILL"}}
# 📨 DOCKER: system/status (SYSTEM)
#    Payload: {"status":"running","uptime":3600}
# 📨 SECONDARY: opcua/connection (OPC_UA)
#    Payload: {"endpoint":"192.168.0.40:4840","status":"connected"}
```

### **2. Log-Dateien analysieren**
```bash
# Log-Datei anzeigen
tail -f mqtt_traffic.log

# Beispiel Log-Eintrag:
# ================================================================================
# TIMESTAMP: 2024-01-15T14:30:25.123456
# DIRECTION: cloud_to_local
# TOPIC: module/v1/ff/FF22-001/order
# QOS: 1
# RETAINED: False
# PAYLOAD:
# {
#   "serialNumber": "FF22-001",
#   "orderId": "order-123",
#   "action": {
#     "command": "MILL"
#   }
# }
# ================================================================================
```

### **3. Datenbank-Abfragen**
```bash
# SQLite Datenbank öffnen
sqlite3 mqtt_traffic.db

# Alle Nachrichten anzeigen
SELECT timestamp, direction, topic FROM mqtt_messages LIMIT 10;

# Module-Aktivität
SELECT topic, COUNT(*) FROM mqtt_messages 
WHERE topic LIKE 'module/v1/ff/%' 
GROUP BY topic;

# Fehlerhafte Nachrichten
SELECT * FROM mqtt_messages WHERE payload LIKE '%error%';
```

## 📈 **Analyse und Visualisierung**

### **1. Zusammenfassung anzeigen**
```bash
python mqtt_traffic_analyzer.py

# Ausgabe:
# ================================================================================
# 📊 MQTT TRAFFIC ANALYSIS SUMMARY
# ================================================================================
# Total Messages (24h):     1,234
# Cloud → Local:            567
# Local → Cloud:            667
# 
# 🔝 TOP TOPICS:
#   1. module/v1/ff/FF22-001/state (234 messages)
#   2. module/v1/ff/FF22-002/state (198 messages)
#   3. module/v1/ff/FF22-001/order (156 messages)
# 
# 🏭 MODULE ACTIVITY:
#   FF22-001: 390 messages (156 ↓, 234 ↑)
#   FF22-002: 298 messages (100 ↓, 198 ↑)
# 
# ⏰ RECENT ACTIVITY:
#   2024-01-15 14:30:25 | cloud_to_local | module/v1/ff/FF22-001/order
#   2024-01-15 14:30:26 | local_to_cloud | module/v1/ff/FF22-001/state
# ================================================================================
```

### **2. Visualisierungen erstellen**
```bash
python mqtt_traffic_analyzer.py --create-charts

# Erstellt:
# - traffic_analysis/message_direction.png
# - traffic_analysis/top_topics.png
# - traffic_analysis/module_activity.png
```

### **3. Export zu CSV**
```bash
python mqtt_traffic_analyzer.py --export-csv fischertechnik_export.csv

# CSV enthält:
# timestamp,direction,topic,payload,qos,retained
# 2024-01-15T14:30:25,cloud_to_local,module/v1/ff/FF22-001/order,{...},1,false
```

## 🎯 **Praktische Anwendungen**

### **1. Debugging von Kommunikationsproblemen**
```bash
# Nachrichten eines spezifischen Moduls analysieren
sqlite3 mqtt_traffic.db
SELECT * FROM mqtt_messages 
WHERE topic LIKE 'module/v1/ff/FF22-001/%' 
ORDER BY timestamp DESC LIMIT 20;
```

### **2. Performance-Monitoring**
```bash
# Nachrichten pro Stunde
SELECT 
  strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
  COUNT(*) as message_count
FROM mqtt_messages 
GROUP BY hour 
ORDER BY hour DESC;
```

### **3. Fehleranalyse**
```bash
# Nachrichten mit Fehlern finden
SELECT * FROM mqtt_messages 
WHERE payload LIKE '%error%' OR payload LIKE '%fail%';
```

### **4. Modul-Verhalten analysieren**
```bash
# State-Transitions eines Moduls
SELECT timestamp, payload 
FROM mqtt_messages 
WHERE topic = 'module/v1/ff/FF22-001/state' 
ORDER BY timestamp;
```

## 🔧 **Erweiterte Konfiguration**

### **1. Filterung spezifischer Topics**
```python
# In mqtt_bridge_logger.py anpassen
def _subscribe_to_cloud_topics(self):
    topics = [
        "module/v1/ff/#",        # Alle Module
        "fischertechnik/#",      # Fischertechnik spezifisch
        "aps/#",                 # APS spezifisch
        "custom/topic/#",        # Custom Topics
    ]
```

### **2. Custom Logging-Format**
```python
# Log-Format anpassen
def _log_message(self, direction: str, msg):
    # Custom Format hier implementieren
    pass
```

### **3. Automatische Archivierung**
```bash
# Cron-Job für tägliche Archivierung
0 2 * * * cd /path/to/src-orbis && \
  python mqtt_traffic_analyzer.py --export-csv \
  /archive/fischertechnik_$(date +%Y%m%d).csv
```

## 🚨 **Troubleshooting**

### **Problem: Bridge kann nicht verbinden**
```bash
# Netzwerk-Test
ping 192.168.0.100
telnet 192.168.0.100 1883

# Firewall prüfen
sudo ufw status
```

### **Problem: Keine Nachrichten geloggt**
```bash
# Topics prüfen
sqlite3 mqtt_traffic.db
SELECT DISTINCT topic FROM mqtt_messages;

# Verbindung prüfen
python mqtt_bridge_logger.py --cloud-broker 192.168.0.100 --verbose
```

### **Problem: Datenbank wird zu groß**
```bash
# Alte Nachrichten löschen
sqlite3 mqtt_traffic.db
DELETE FROM mqtt_messages WHERE timestamp < '2024-01-01';
VACUUM;
```

## 📊 **Monitoring Dashboard**

### **1. Real-time Dashboard**
```bash
# Watch-Command für Live-Monitoring
watch -n 5 'python mqtt_traffic_analyzer.py | head -20'
```

### **2. Web-Dashboard (Optional)**
```python
# Flask-App für Web-Dashboard
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Dashboard-Logik hier
    return render_template('dashboard.html')
```

---

*Mit diesem Traffic Logging System hast du vollständige Transparenz über die MQTT-Kommunikation der Fischertechnik APS!*
