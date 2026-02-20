# Remote MQTT Control Guide - Fischertechnik APS von macOS

**Status:** Aktive Dokumentation für OSF  
**Quelle:** Aus Legacy-Archiv übernommen (04-howto_omf_legacy entfernt 2026-02-18)

Dieser Guide erklärt, wie du die Fischertechnik APS in der Firma von deinem macOS-Rechner aus steuern kannst.

## 🎯 **Übersicht**

### **Setup:**
```
macOS (Cursor) → Remote MQTT Client → Firmennetzwerk → Fischertechnik APS
```

### **Vorteile:**
- ✅ **Entwicklung auf macOS** mit Cursor
- ✅ **Direkte Steuerung** der echten Module
- ✅ **Realistische Tests** mit echter Hardware
- ✅ **Keine Hardware** auf macOS nötig

## 🔧 **Voraussetzungen**

### **1. Netzwerkverbindung**
- Beide Rechner im gleichen Firmennetzwerk
- Oder VPN-Verbindung zur Firma
- MQTT Broker erreichbar (Port 1883)

### **2. IP-Adresse der Fischertechnik APS**
```bash
# In der Firma ermitteln:
# Auf dem Raspberry Pi oder Firmenlaptop
hostname -I
# oder
ip addr show
```

### **3. MQTT Broker Konfiguration**
- MQTT Broker läuft auf der Fischertechnik APS
- Port 1883 ist offen
- Keine Firewall-Blockierung

## 🚀 **Schnellstart**

### **1. IP-Adresse ermitteln**
```bash
# In der Firma auf dem Fischertechnik System
hostname -I
# Beispiel: 192.168.1.100
```

### **2. Verbindung testen**
```bash
# Von macOS aus
ping 192.168.1.100
telnet 192.168.1.100 1883
```

### **3. Remote Client starten**
```bash
cd src-orbis

# Interaktiver Modus
python remote_mqtt_client.py --broker 192.168.1.100

# Demo Modus
python remote_mqtt_client.py --broker 192.168.1.100 --mode demo

# Einzelne Befehle
python remote_mqtt_client.py --broker 192.168.1.100 --order FF22-001 MILL
```

## 📋 **Verwendung**

### **Interaktiver Modus**
```bash
python remote_mqtt_client.py --broker 192.168.1.100
```

**Verfügbare Befehle:**
```
> order FF22-001 MILL          # MILL-Modul steuern
> action FF22-002 reset        # DRILL-Modul zurücksetzen
> status FF22-003              # OVEN-Status abfragen
> quit                         # Beenden
```

### **Demo Modus**
```bash
python remote_mqtt_client.py --broker 192.168.1.100 --mode demo
```

**Führt automatisch aus:**
1. MILL-Modul testen
2. DRILL-Modul testen
3. OVEN-Modul testen
4. AIQS-Modul testen
5. HBW-Modul testen
6. DPS-Modul testen

### **Einzelne Befehle**
```bash
# Einzelne Order senden
python remote_mqtt_client.py --broker 192.168.1.100 --order FF22-001 MILL

# Einzelne Aktion senden
python remote_mqtt_client.py --broker 192.168.1.100 --action FF22-002 reset
```

## 🔍 **Verbindung testen**

### **1. Netzwerk-Test**
```bash
# Ping Test
ping 192.168.1.100

# Port Test
nc -zv 192.168.1.100 1883
```

### **2. MQTT-Test**
```bash
# Mit mosquitto (falls installiert)
mosquitto_pub -h 192.168.1.100 -p 1883 -t "test" -m "hello"
mosquitto_sub -h 192.168.1.100 -p 1883 -t "test"
```

### **3. Python-Test**
```python
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

client = mqtt.Client()
client.on_connect = on_connect
client.connect("192.168.1.100", 1883, 60)
client.loop_forever()
```

## 🔧 **Konfiguration**

### **MQTT Broker IP finden**

#### **Option A: Auf dem Raspberry Pi**
```bash
# SSH auf den Raspberry Pi
ssh pi@fischertechnik-aps

# IP-Adresse anzeigen
hostname -I
```

#### **Option B: Auf dem Firmenlaptop**
```bash
# Netzwerk-Scan
nmap -sn 192.168.1.0/24

# Oder ARP-Tabelle
arp -a | grep -i fischer
```

#### **Option C: Router/DHCP**
- Router-Interface öffnen
- DHCP-Client-Liste prüfen
- Fischertechnik-Gerät identifizieren

### **Firewall-Konfiguration**

#### **Auf der Fischertechnik APS:**
```bash
# Port 1883 freigeben
sudo ufw allow 1883

# Oder iptables
sudo iptables -A INPUT -p tcp --dport 1883 -j ACCEPT
```

#### **Auf macOS:**
```bash
# Firewall prüfen
sudo pfctl -s rules

# Port 1883 erlauben (falls nötig)
sudo pfctl -f /etc/pf.conf
```

## 🚨 **Troubleshooting**

### **Problem: Verbindung verweigert**
```bash
# Prüfe Netzwerk
ping 192.168.1.100

# Prüfe Port
telnet 192.168.1.100 1883

# Prüfe Firewall
sudo ufw status
```

### **Problem: MQTT Broker nicht erreichbar**
```bash
# Auf der Fischertechnik APS prüfen
sudo systemctl status mosquitto
sudo netstat -tlnp | grep 1883
```

### **Problem: Authentifizierung fehlgeschlagen**
```bash
# Mit Username/Password
python remote_mqtt_client.py --broker 192.168.1.100 --username user --password pass
```

### **Problem: Module reagieren nicht**
- Prüfe Serial Numbers (FF22-001 bis FF22-006)
- Prüfe MQTT Topics
- Prüfe JSON-Format
- Prüfe Logs auf der Fischertechnik APS

## 📊 **Monitoring**

### **Status überwachen**
```bash
# Alle Module-Status empfangen
python remote_mqtt_client.py --broker 192.168.1.100
# Dann: status FF22-001
```

### **Logs überwachen**
```bash
# Auf der Fischertechnik APS
tail -f /var/log/mosquitto/mosquitto.log
tail -f /var/log/node-red.log
```

### **Web Interface**
```bash
# Falls verfügbar
# http://192.168.1.100:1880 (Node-RED)
# http://192.168.1.100:9001 (MQTT Web Client)
```

## 🔐 **Sicherheit**

### **VPN-Verbindung (Empfohlen)**
```bash
# Firmen-VPN konfigurieren
# Dann Remote Client verwenden
python remote_mqtt_client.py --broker 10.0.0.100
```

### **SSH Tunnel (Alternative)**
```bash
# SSH Tunnel erstellen
ssh -L 1883:localhost:1883 user@192.168.1.100

# Dann lokal verbinden
python remote_mqtt_client.py --broker localhost
```

### **MQTT Authentication**
```bash
# Mit Username/Password
python remote_mqtt_client.py --broker 192.168.1.100 --username user --password pass
```

## 🎯 **Praktische Anwendung**

### **Entwicklungsworkflow:**
1. **Code auf macOS** mit Cursor entwickeln
2. **Remote Client** starten
3. **Befehle senden** an echte Module
4. **Reaktionen beobachten** in Echtzeit
5. **Code anpassen** basierend auf Ergebnissen

### **Testing-Szenarien:**
- **Einzelne Module** testen
- **Produktionsabläufe** simulieren
- **Fehlerfälle** testen
- **Performance** messen

### **Integration:**
- **Eigene Apps** mit Remote Client verbinden
- **Automatisierte Tests** schreiben
- **Monitoring** implementieren

---

*Mit diesem Setup kannst du die Fischertechnik APS vollständig von deinem macOS aus steuern und entwickeln!*
