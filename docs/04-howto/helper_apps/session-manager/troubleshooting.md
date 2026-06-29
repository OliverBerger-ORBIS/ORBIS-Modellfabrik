# 🔧 Troubleshooting - Session Manager

## 🚨 Häufige Probleme und Lösungen

### 🧭 Erstcheck: Modus und Broker-Ziel

Vor jeder Fehlersuche zuerst pruefen:

1. Welcher Modus ist aktiv (Local Replay / Live auf RPi / Live mit lokalem OSF)?
2. Passt das Broker-Ziel zum Modus?
   - Replay lokal: oft `localhost`
   - Live ORBIS/RPi: typischerweise `192.168.0.100`
3. Keine Live- und Replay-Injects gleichzeitig auf denselben Topics/Brokern (No-Mix-Regel).

### 📹 Session Recorder

#### **Problem: MQTT-Verbindung fehlgeschlagen**
```
Error: Connection failed to localhost:1883
```

**Lösung:**
1. **MQTT-Broker prüfen:** `mosquitto -v` starten
2. **Port prüfen:** Port 1883 verfügbar?
3. **Firewall:** Lokale Verbindungen erlauben
4. **Broker-Status:** `netstat -an | grep 1883`

#### **Problem: Session wird nicht gespeichert**
```
Error: Failed to save session
```

**Lösung:**
1. **Verzeichnis prüfen:** `data/osf-data/sessions/` existiert?
2. **Berechtigung:** Schreibrechte auf Verzeichnis?
3. **Speicherplatz:** Ausreichend Platz verfügbar?
4. **Format prüfen:** Recorder schreibt JSON-Lines `.log` Dateien.

### 🎬 Replay Station

#### **Problem: Session kann nicht geladen werden**
```
Error: Failed to load session file
```

**Lösung:**
1. **Datei-Format:** `.log` (JSON-Lines) Datei?
2. **Datei-Integrität:** Datei beschädigt?
3. **Pfad:** Korrekter Dateipfad?
4. **Berechtigung:** Lesezugriff auf Datei?

#### **Problem: Replay läuft zu langsam/schnell**
```
Issue: Timing-Probleme beim Replay
```

**Lösung:**
1. **Geschwindigkeit:** Speed-Control anpassen
2. **System-Performance:** CPU/Memory prüfen
3. **MQTT-Broker:** Broker-Performance prüfen
4. **Threading:** Background-Thread läuft?

### 🔍 Template Analysis

#### **Problem: Analyzer läuft nicht**
```
Error: Template analyzer failed
```

**Lösung:**
1. **Analyzer-Dateien:** Alle Analyzer vorhanden?
2. **Dependencies:** Alle Python-Pakete installiert?
3. **Session-Daten:** Ausreichend Messages für Analyse?
4. **Template-Format:** YAML-Struktur korrekt?

#### **Problem: Templates werden nicht generiert**
```
Error: No templates generated
```

**Lösung:**
1. **Message-Patterns:** Erkennbare Patterns in Session?
2. **Analyzer-Konfiguration:** Analyzer richtig konfiguriert?
3. **Schema-Validation:** Template-Schema gültig?
4. **Export-Pfad:** Export-Verzeichnis verfügbar?

## 🔍 Debugging-Tipps

### **Logs prüfen**
```bash
# Session Manager Logs
tail -f data/logs/session_manager.log

# MQTT-Broker Logs
tail -f /var/log/mosquitto/mosquitto.log
```

### **Performance-Monitoring**
```bash
# CPU/Memory Usage
top -p $(pgrep -f "streamlit run")

# MQTT-Verbindungen
netstat -an | grep 1883
```

### **Session-Daten prüfen**
```bash
# Anzahl Messages in einer Session-Datei prüfen (JSON-Lines)
wc -l "data/osf-data/sessions/<session>.log"

# Spot-Check auf Topic/Pattern
rg "ccu/order|dsp/correlation|nfc" "data/osf-data/sessions/<session>.log"
```

## 🆘 Notfall-Lösungen

### **Session Manager neu starten**
```bash
# Alle Streamlit-Prozesse beenden
pkill -f "streamlit run"

# Session Manager neu starten
streamlit run session_manager/app.py
```

### **MQTT-Broker neu starten**
```bash
# Mosquitto beenden
sudo pkill mosquitto

# Mosquitto neu starten
mosquitto -v
```

### **Session-Daten zurücksetzen**
```bash
# Session-Verzeichnis leeren
rm -rf data/osf-data/sessions/*

# Verzeichnis neu erstellen
mkdir -p data/osf-data/sessions/
```

## 📞 Support

Bei weiteren Problemen:

1. **Logs sammeln:** Alle relevanten Log-Dateien
2. **Session-Daten:** Betroffene Session-Dateien
3. **System-Info:** OS, Python-Version, installierte Pakete
4. **Reproduktion:** Schritt-für-Schritt Anleitung

## 🔗 Verwandte Dokumentation

- [**Session Recorder**](session-recorder.md) - Aufnahme-Probleme
- [**Replay Station**](replay-station.md) - Wiedergabe-Probleme
- [**Laufmodi-Matrix**](runtime-modes-matrix.md) - Modus/Broker-Regeln fuer OSF + Session Manager + Mosquitto
- [**Template Analysis**](template-analysis.md) - Template-Probleme
