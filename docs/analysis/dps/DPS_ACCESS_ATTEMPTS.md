# DPS TXT Controller - Zugriffsversuche

## 🎯 Ziel
Zugriff auf den DPS TXT Controller (192.168.0.102) für Code-Analyse der CCU-Logik.

## ❌ Fehlgeschlagene Versuche

### 1. SSH-Zugriff
**Versuchte Methoden:**
- `ssh ft@192.168.0.102` (Port 22)
- `ssh -p 22 ft@192.168.0.102`
- `ssh -p 2222 ft@192.168.0.102`
- `ssh -p 8022 ft@192.168.0.102`

**Ergebnis:** `Connection refused` auf allen Ports

### 2. Port-Forwarding über RPi
**Vorgehen:**
- SSH zum RPi: `ssh -L 2222:192.168.0.102:22 ff22@192.168.0.100`
- Port-Forwarding eingerichtet
- SSH vom RPi: `ssh -p 2222 ft@localhost`

**Ergebnis:** `Connection refused` - Port-Forwarding funktioniert nicht

### 3. Browser-Entwicklertools
**Vorgehen:**
- Chrome im Inkognito-Modus
- F12 → Network Tab
- Dateien anklicken für Response Tab

**Ergebnis:** Response Tab erscheint nicht, Code nicht zugänglich

### 4. SCP-Direktzugriff
**Vorgehen:**
- `scp ft@192.168.0.102:/path/to/file ./`

**Ergebnis:** Nicht versucht (SSH funktioniert nicht)

## ✅ Erfolgreiche Alternative

### RoBoPro mit API-Key
**Status:** Vorbereitet für morgen
- API-Keys funktionieren
- Software-Update erforderlich
- Direkter Zugriff auf alle Dateien möglich

## 📋 Dateien für Analyse

**Ziel-Dateien:**
- `.project.json` - Konfiguration (121 Bytes)
- `FF_DPD_24V.py` - Haupt-Script (5.96 KB)
- `data/*.py` - Daten-Scripts
- `data/*.json` - Daten-Konfiguration
- `lib/*.py` - Bibliotheken

## 🔍 Erwartete Erkenntnisse

### Order-ID-Management
- Wie werden Order-IDs generiert?
- Wo werden sie gespeichert?
- Wie werden sie an andere Komponenten übertragen?

### MQTT-Kommunikation
- Welche Topics werden verwendet?
- Publisher oder Subscriber?
- Client-ID und Konfiguration

### CCU-Logik
- Prozesssteuerung (Warenein- und -ausgang)
- Bestellungsverwaltung
- Integration mit anderen TXT-Controllern

## 📅 Nächste Schritte

**Morgen:**
1. **RoBoPro-Setup** - Software-Update durchführen
2. **API-Key-Zugriff** - Dateien herunterladen
3. **Code-Analyse** - CCU-Logik verstehen
4. **Dokumentation** - Vollständige Analyse erstellen

## ⚠️ Lessons Learned

- **SSH-Zugriff:** DPS TXT Controller hat SSH deaktiviert
- **Port-Forwarding:** Funktioniert nicht über RPi
- **Browser-Entwicklertools:** Response Tab nicht verfügbar
- **RoBoPro:** Einzige funktionierende Alternative

---
*Erstellt: 18. September 2025*  
*Status: Fehlgeschlagen - RoBoPro für morgen geplant*
