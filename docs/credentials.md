# 🔐 ORBIS SmartFactory – Credentials & Access

This document contains default login credentials and access information for the ORBIS SmartFactory system components.

## ⚠️ Security Notice

**Important**: These are default credentials. For production use, always change default passwords and use secure authentication methods.

## 🏭 APS Modellfabrik Components

### CCU (Central Control Unit) - Raspberry Pi
- **Komponente**: CCU (Central Control Unit)
- **Hardware**: Raspberry Pi
- **IP Address**: `192.168.0.100`
- **Web Interface**: `http://192.168.0.100/de/aps/`
- **SSH Access**:
  - Username: `ff22`
  - Default Password: `ff22+`
  - SSH Port: `22`
- **Status**: ✅ **Web-Interface funktioniert!** - SSH zu testen
- **Beschreibung**: Zentrale Steuereinheit der APS-Modellfabrik

### MQTT Broker (Mosquitto)
- **Komponente**: MQTT Broker
- **Software**: Mosquitto
- **Host**: `192.168.0.100`
- **Port**: `1883`
- **Authentication**: Required (currently blocking connections)
- **Default Login**: `default` / `default`
- **Status**: ✅ **Funktioniert!** - Verbindung erfolgreich
- **Beschreibung**: MQTT-Broker für die Kommunikation zwischen APS-Modulen

#### Tested Credentials (All Failed)
- `admin` / `admin`
- `admin` / `password`
- `admin` / `123456`
- `mqtt` / `mqtt`
- `user` / `password`
- `guest` / `guest`
- `pi` / `raspberry`
- `root` / `root`
- `fischertechnik` / `fischertechnik`
- `aps` / `aps`
- `orbis` / `orbis`
- `default` / `default` ✅ **Funktioniert!**
- Anonymous connection

### Node-RED Dashboard
- **Komponente**: Node-RED
- **Software**: Gateway MQTT und OPC-UA
- **Host**: `192.168.0.100`
- **Port**: `1880`
- **URL**: `http://192.168.0.100:1880`
- **Authentication**: Keine (öffentlich)
- **Status**: ✅ **Funktioniert!** - Web-Interface erreichbar
- **Beschreibung**: Web-basiertes Dashboard für MQTT und OPC-UA Gateway

### Router TL (TP-Link)
- **Komponente**: Router TL
- **Software**: Konfiguration Netzwerk
- **IP Address**: `192.168.0.1` oder `http://tplinkap.net`
- **URL**: `http://192.168.0.1` oder `http://tplinkap.net`
- **Default Login**: `admin` / `admin1`
- **Status**: ✅ **Funktioniert!** - Web-Interface erreichbar
- **Beschreibung**: Netzwerk-Router für APS-Modellfabrik

#### WLAN Configuration (Updated 17.02.2026)
- **SSID (2.4GHz)**: `ORBIS-4711`
- **SSID (5GHz)**: `ORBIS-4711_5G`
- **Password**: `49117837`
- **Messe LogiMAT (2026-03):** SSID **`ORBIS-4C57`** (2.4 GHz für Arduino / Shopfloor am Messe-AP). Passwort wie oben, sofern gleiches Netz – **Arduino-Sketch:** `OSF_MultiSensor_R4WiFi` **v1.1.7+** (ORBIS: NTP via Shopfloor-RPi chrony; **v1.1.6+** `timestamp` UTC mit ms).
- **Modules Update Procedure**:
  - Connect to TXT Controller (Touchscreen).
  - Go to **Settings > Network > WLAN**.
  - Select new SSID (`ORBIS-4711` or `ORBIS-4711_5G`; **Messe:** `ORBIS-4C57` falls ausgerollt).
  - Enter Password.
  - Apply to: **TXT-FTS**, **TXT-AIQS**, **TXT-DPS** (Cloud Gateway Controller).

### TXT 4.0 Controller - SSH
- **Komponente**: TXT 4.0 Controller
- **Software**: SSH
- **IP Address**: `192.168.0.x`
- **Port**: `22`
- **Default Login**: `ft` / `fischertechnik`
- **Status**: ⚠️ **Not Tested**
- **Beschreibung**: Fischertechnik TXT 4.0 Controller SSH-Zugang

### TXT 4.0 Controller - Web-Server
- **Komponente**: TXT 4.0 Controller
- **Software**: Web-Server
- **IP Address**: `192.168.0.x`
- **Port**: `80`
- **Default Login**: `ft` / `fischertechnik`
- **Status**: ⚠️ **Not Tested**
- **Beschreibung**: Fischertechnik TXT 4.0 Controller Web-Interface

### SPS Siemens S7-1200 - OPC-UA
- **Komponente**: SPS Siemens S7-1200
- **Software**: OPC-UA
- **IP Ranges**:
  - **MILL**: `192.168.0.40-45`
  - **DRILL**: `192.168.0.50-55`
  - **OVEN**: `192.168.0.60-65`
  - **AIQS**: `192.168.0.70-75`
  - **HBW**: `192.168.0.80-83`
  - **DPS**: `192.168.0.90`
  - **ORBIS Extensions** (Arduino, Sensoren): `192.168.0.91-99` (Arduino sw420-1: `.95`)
- **Port**: `4840`
- **Authentication**: Keine (OPC-UA Standard)
- **Status**: ⚠️ **Not Tested**
- **Beschreibung**: Siemens S7-1200 SPS mit OPC-UA Protokoll

## 🔧 Development Environment

### Local MQTT Broker (macOS)
- **Host**: `localhost`
- **Port**: `1883`
- **Authentication**: None (open)
- **Status**: ✅ **Working**

### Python Virtual Environment
- **Path**: `/Users/oliver/Projects/ORBIS-Modellfabrik/.venv`
- **Activation**: `source .venv/bin/activate`
- **Status**: ✅ **Working**

## 📋 Network Configuration

### APS Modellfabrik Network Setup
- **CCU IP**: `192.168.0.100`
- **MQTT Port**: `1883`
- **Network**: `192.168.0.0/24`
- **Gateway**: Likely `192.168.0.1`
- **DNS**: Likely `192.168.0.1`
- **Beschreibung**: Netzwerk-Konfiguration der APS-Modellfabrik

### Connectivity Status
- **Ping**: ✅ **Working** (3ms average)
- **Port 1883**: ✅ **Open**
- **MQTT**: ✅ **Working** (default/default credentials)
- **SSH**: 🔴 **Not tested**

## 🛠️ Troubleshooting

### MQTT Authentication Issues
**Problem**: Return Code 5 - "Not authorized"

**Possible Solutions**:
1. **Check MQTT Configuration**:
   ```bash
   ssh pi@192.168.0.100
   sudo cat /etc/mosquitto/mosquitto.conf
   sudo cat /etc/mosquitto/passwd
   ```

2. **Enable Anonymous Access** (Temporary):
   ```bash
   # On Raspberry Pi
   sudo nano /etc/mosquitto/mosquitto.conf
   # Add: allow_anonymous true
   sudo systemctl restart mosquitto
   ```

3. **Create MQTT User**:
   ```bash
   # On Raspberry Pi
   sudo mosquitto_passwd -c /etc/mosquitto/passwd orbis
   sudo systemctl restart mosquitto
   ```

### SSH Access Issues
**Problem**: Cannot connect via SSH

**Solutions**:
1. **Enable SSH** (if disabled):
   ```bash
   # On Raspberry Pi (if you have physical access)
   sudo raspi-config
   # Navigate to: Interface Options > SSH > Enable
   ```

2. **Reset Password**:
   ```bash
   # On Raspberry Pi (if you have physical access)
   sudo passwd pi
   ```

## 📝 Configuration Files

### MQTT Configuration Template
```ini
# /etc/mosquitto/mosquitto.conf
port 1883
allow_anonymous true
password_file /etc/mosquitto/passwd
log_type all
log_dest file /var/log/mosquitto/mosquitto.log
```

### Network Configuration Template
```bash
# /etc/network/interfaces or /etc/dhcpcd.conf
interface eth0
static ip_address=192.168.0.100/24
static routers=192.168.0.1
static domain_name_servers=192.168.0.1
```

## 🔄 Next Steps

### Immediate Actions Needed
1. **SSH Access**: Test SSH connection to CCU (ff22/ff22+)
2. **MQTT Credentials**: ✅ **Working** (default/default)
3. **Node-RED Access**: Test web interface access (Port 1880)
4. **Router TL**: Test TP-Link Router (admin/admin1)
5. **TXT 4.0 Controller**: Test SSH und Web (ft/fischertechnik)
6. **SPS Siemens**: Test OPC-UA Verbindungen (Port 4840)
7. **Documentation**: ✅ **Updated** with all credentials

### Long-term Security
1. **Change Default Passwords**: Update all default credentials
2. **Secure MQTT**: Implement proper MQTT authentication
3. **Network Security**: Configure firewall rules
4. **Access Control**: Implement role-based access

## 📞 Support Information

### Contact Information
- **System Administrator**: [To be added]
- **Network Administrator**: [To be added]
- **Orbis Development Team**: [To be added]

### Emergency Access
- **Physical Access**: Available at APS location
- **Reset Procedures**: Document hardware reset procedures
- **Backup Credentials**: Store secure backup access methods

---

**Last Updated**: 2025-08-14  
**Version**: 2.0  
**Status**: 🟡 **Partially Complete - MQTT Working, Others Need Testing**

*This document should be updated as credentials are discovered and tested.*
