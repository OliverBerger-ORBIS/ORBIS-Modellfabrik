# SSH-Befehle für Raspberry Pi

## 🔐 Zugangsdaten
- **Host**: `192.168.0.100`
- **Username**: `ff22`
- **Password**: `ff22+`
- **Port**: `22`

## 📋 SSH-Verbindung
```bash
ssh ff22@192.168.0.100
```

## 🔧 Mosquitto-Konfiguration anpassen

### 1. Aktuelle Konfiguration anzeigen
```bash
sudo cat /etc/mosquitto/mosquitto.conf
```

### 2. Backup der aktuellen Konfiguration
```bash
sudo cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.backup
```

### 3. Neue Konfiguration erstellen
```bash
sudo nano /etc/mosquitto/mosquitto.conf
```

### 4. Vereinfachte Logging-Konfiguration hinzufügen
```conf
# Vereinfachte Logging-Konfiguration für APS-Analyse (bewährt)
log_dest file /var/log/mosquitto/mosquitto_aps_analysis.log
log_type all
connection_messages true
log_timestamp true

# Bestehende Konfiguration beibehalten
port 1883
allow_anonymous true
password_file /etc/mosquitto/passwd
```

### 5. Mosquitto-Service neustarten
```bash
sudo systemctl restart mosquitto
```

### 6. Service-Status prüfen
```bash
sudo systemctl status mosquitto
```

## 📁 Log-Datei-Verwaltung

### 1. Alte Log-Datei umbenennen
```bash
sudo mv /var/log/mosquitto/mosquitto.log /var/log/mosquitto/mosquitto_old_$(date +%Y%m%d_%H%M%S).log
```

### 2. Neue Log-Datei erstellen
```bash
# System-Log für PUB/SUB Events + Payloads
sudo touch /var/log/mosquitto/mosquitto_aps_analysis.log
sudo chown mosquitto:mosquitto /var/log/mosquitto/mosquitto_aps_analysis.log
```

### 3. Log-Datei-Berechtigungen prüfen
```bash
ls -la /var/log/mosquitto/
```

## 🔄 System-Neustart

### 1. Raspberry Pi neu starten
```bash
sudo reboot
```

### 2. Nach Neustart: Log-Datei prüfen
```bash
# System-Log prüfen (PUB/SUB Events + Payloads)
tail -f /var/log/mosquitto/mosquitto_aps_analysis.log
```

## 📊 Log-Datei kopieren

### 1. Log-Datei vom RPi kopieren
```bash
# Von lokalem Mac - System-Log (PUB/SUB Events + Payloads)
scp ff22@192.168.0.100:/var/log/mosquitto/mosquitto_aps_analysis.log /Users/oliver/Projects/ORBIS-Modellfabrik/data/aps-data/mosquitto/
```

### 2. Log-Datei filtern
```bash
cd /Users/oliver/Projects/ORBIS-Modellfabrik/data/aps-data/mosquitto/

# Log-Datei filtern (periodische Topics reduzieren)
python ../../docs/06-integrations/mosquitto/log_filter_script.py mosquitto_aps_analysis.log mosquitto_aps_analysis_filtered.log
```

### 3. Log-Datei analysieren
```bash
# Gefilterte Log-Datei analysieren (PUB/SUB Events + Payloads)
head -50 mosquitto_aps_analysis_filtered.log

# Fokus auf wichtige Sequenzen suchen
grep -i "instantAction\|order\|reset\|charge" mosquitto_aps_analysis_filtered.log
```

## ✅ Erfolgskriterien
- [ ] SSH-Verbindung erfolgreich
- [ ] Mosquitto-Konfiguration erweitert (`log_type all`)
- [ ] Service neugestartet
- [ ] Log-Datei erstellt und berechtigt
- [ ] **APS komplett neugestartet** (Hardware-Schalter)
- [ ] Log-Datei kopiert
- [ ] **Log-Datei gefiltert** (periodische Topics reduziert)
- [ ] **Instant Actions** und **Orders** identifiziert
- [ ] Timestamp-Synchronisation für Sequenz-Analyse
