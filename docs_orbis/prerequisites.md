# Voraussetzungen für MQTT Mock System

Dieser Guide listet alle notwendigen Voraussetzungen für das Testen des MQTT Mocking Systems auf.

## 🔧 **Systemvoraussetzungen**

### **1. Python (Version 3.7 oder höher)**

#### **Prüfung:**
```bash
python3 --version
```

#### **Installation (falls nicht vorhanden):**
```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Windows
# Download von python.org
```

### **2. MQTT Broker (Mosquitto)**

#### **Installation:**
```bash
# macOS
brew install mosquitto

# Ubuntu/Debian
sudo apt install mosquitto mosquitto-clients

# Windows
# Download von mosquitto.org
```

#### **Alternative: Docker**
```bash
docker run -d --name mqtt-broker \
  -p 1883:1883 \
  -p 9001:9001 \
  eclipse-mosquitto:latest
```

### **3. Python Dependencies**

#### **Automatische Installation:**
```bash
# Alle Dependencies installieren
pip install -r requirements.txt

# Oder nur MQTT
pip install paho-mqtt>=1.6.1
```

#### **Manuelle Installation:**
```bash
pip install paho-mqtt
pip install numpy
pip install pandas
pip install matplotlib
pip install seaborn
```

## 🚀 **Schnelltest der Voraussetzungen**

### **Automatischer Check:**
```bash
cd src_orbis
python check_prerequisites.py
```

### **Manueller Check:**

#### **1. Python Version prüfen:**
```bash
python3 --version
# Sollte 3.7 oder höher sein
```

#### **2. MQTT Broker prüfen:**
```bash
# Prüfe ob mosquitto installiert ist
which mosquitto

# Prüfe ob Port 1883 offen ist
netstat -an | grep 1883
# Oder
lsof -i :1883
```

#### **3. Python Packages prüfen:**
```bash
python3 -c "import paho.mqtt.client; print('MQTT OK')"
python3 -c "import json, datetime, logging, threading; print('Standard libs OK')"
```

#### **4. MQTT Verbindung testen:**
```bash
# Starte mosquitto (falls nicht läuft)
mosquitto -p 1883 &

# Teste Verbindung
mosquitto_pub -h localhost -p 1883 -t "test" -m "hello"
mosquitto_sub -h localhost -p 1883 -t "test"
```

## 📋 **Minimale Voraussetzungen für Testing**

### **Absolute Minimum:**
- ✅ Python 3.7+
- ✅ paho-mqtt package
- ✅ MQTT Broker (mosquitto)

### **Empfohlen:**
- ✅ Alle Python packages aus requirements.txt
- ✅ Mosquitto als Service
- ✅ Netzwerk-Zugriff auf localhost:1883

## 🔍 **Troubleshooting**

### **Problem: Python nicht gefunden**
```bash
# Prüfe Python Installation
which python3
python3 --version

# Falls nicht installiert
brew install python3
```

### **Problem: mosquitto nicht gefunden**
```bash
# Installation prüfen
which mosquitto

# Falls nicht installiert
brew install mosquitto

# Starten
mosquitto -p 1883
```

### **Problem: Port 1883 bereits belegt**
```bash
# Prüfe was auf Port 1883 läuft
lsof -i :1883

# Falls mosquitto bereits läuft
brew services list | grep mosquitto

# Stoppe und starte neu
brew services stop mosquitto
mosquitto -p 1883
```

### **Problem: paho-mqtt Import Error**
```bash
# Installiere neu
pip uninstall paho-mqtt
pip install paho-mqtt>=1.6.1

# Prüfe Installation
python3 -c "import paho.mqtt.client; print('OK')"
```

## 🎯 **Quick Start nach Installation**

### **1. Voraussetzungen prüfen:**
```bash
cd src_orbis
python check_prerequisites.py
```

### **2. Demo starten:**
```bash
python setup_mqtt_mock.py --demo
```

### **3. Oder manuell:**
```bash
# Terminal 1: Mock System
python mqtt_mock.py

# Terminal 2: Test Client
python mqtt_test_client.py
```

## 📊 **Systemanforderungen**

### **Betriebssystem:**
- ✅ macOS 10.14+
- ✅ Ubuntu 18.04+
- ✅ Windows 10+
- ✅ Docker (beliebiges OS)

### **Hardware:**
- ✅ CPU: 1 GHz
- ✅ RAM: 512 MB
- ✅ Speicher: 100 MB
- ✅ Netzwerk: localhost Verbindung

### **Netzwerk:**
- ✅ localhost:1883 (MQTT)
- ✅ Keine Firewall-Blockierung
- ✅ Keine Proxy-Einstellungen

## 🔧 **Erweiterte Konfiguration**

### **Mosquitto als Service (macOS):**
```bash
# Als Service starten
brew services start mosquitto

# Status prüfen
brew services list | grep mosquitto

# Stoppen
brew services stop mosquitto
```

### **Mosquitto Konfiguration:**
```bash
# Konfigurationsdatei erstellen
sudo nano /usr/local/etc/mosquitto/mosquitto.conf

# Inhalt:
port 1883
allow_anonymous true
persistence false
```

### **Firewall Einstellungen:**
```bash
# macOS Firewall prüfen
sudo pfctl -s rules

# Port 1883 freigeben (falls nötig)
sudo pfctl -f /etc/pf.conf
```

---

*Mit diesen Voraussetzungen kannst du das MQTT Mock System vollständig testen und entwickeln.*
