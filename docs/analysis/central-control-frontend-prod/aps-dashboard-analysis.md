# Original APS-Dashboard Analyse

## Ziel
Das Original APS-Dashboard (`central-control-frontend-prod`) analysieren, um die korrekten Commands, Topics und Payloads zu identifizieren.

## Container Details
- **Container:** `central-control-frontend-prod`
- **Image:** `ghcr.io/ommsolutions/ff-frontend-armv7:release-24v-v130`
- **Port:** 80 (extern) → 80 (intern)
- **URL:** `http://192.168.0.100/de/aps/`

## Analyse-Methodik

### 1. SSH-Zugang zum Raspberry Pi
```bash
ssh ff22@192.168.0.100
```

### 2. Container-Status prüfen
```bash
docker ps
```

### 3. In den Frontend Container
```bash
docker exec -it central-control-frontend-prod /bin/sh
```

### 4. Container-Inhalt analysieren
```bash
# Web-Root finden
find / -name "*.html" -o -name "*.js" -o -name "*.css" 2>/dev/null | head -20

# Nginx Web-Root
ls -la /usr/share/nginx/html/de/aps/
```

### 5. JavaScript-Analyse
```bash
# Haupt-JavaScript-Datei analysieren
head -50 /usr/share/nginx/html/de/aps/main.3c3283515fab30fd.js

# MQTT Topics extrahieren
grep -o "y\.[A-Z_]*" /usr/share/nginx/html/de/aps/main.3c3283515fab30fd.js | sort | uniq
```

## Ergebnisse

### Extrahierte MQTT Topics
Basierend auf der JavaScript-Analyse wurden folgende Topics identifiziert:

- `y.SET_RESET` → `ccu/set/reset`
- `y.SET_CHARGE` → `ccu/set/charge`
- `y.SET_PARK` → `ccu/set/park`
- `y.PAIRING_PAIR_FTS` → `ccu/set/pairFts`
- `y.DELETE_MODULE` → `ccu/set/deleteModule`
- `y.ORDER_RESPONSE` → `ccu/order/response`
- `y.ORDER_REQUEST` → `ccu/order/request`

### Payload-Strukturen
Aus der JavaScript-Analyse extrahierte Payload-Strukturen:

#### Factory Reset
```javascript
// sendFactoryPark() function
this.mqtt.publish(y.SET_RESET, {timestamp: new Date}, {qos:2})
```

#### FTS Charge
```javascript
// setFtsCharge() function
this.mqtt.publish(y.SET_CHARGE, {serialNumber, charge}, {qos:2})
```

#### Factory Park
```javascript
// sendFactoryPark() function
this.mqtt.publish(y.SET_PARK, {timestamp: new Date}, {qos:2})
```

#### FTS Pairing
```javascript
// connectFts() function
this.mqtt.publish(y.PAIRING_PAIR_FTS, {serialNumber}, {qos:2})
```

#### Module Delete
```javascript
// deleteModule() function
this.mqtt.publish(y.DELETE_MODULE, {serialNumber}, {qos:2})
```

### Technische Erkenntnisse

1. **MQTT Client:** Direkter `mqttClient.publish()` Aufruf
2. **QoS:** Immer `qos:2` (höchste Qualität)
3. **Retain:** Nicht explizit gesetzt (Standard: false)
4. **Payload:** JSON-Objekte mit spezifischen Feldern
5. **Topics:** Alle beginnen mit `ccu/` (Central Control Unit)

### Original-Sourcen
Die kompletten Original-Sourcen wurden extrahiert und sind verfügbar unter:
- **Lokaler Pfad:** `integrations/ff-central-control-unit/aps-dashboard-source/`
- **Hauptdatei:** `main.3c3283515fab30fd.js` (kompilierte Angular-Anwendung)

## Implementierung im OMF-Dashboard

### Erfolgreich implementiert:
- ✅ **Factory Reset:** `ccu/set/reset` mit `{timestamp, withStorage}`
- ✅ **FTS Charging:** `ccu/set/charge` mit `{serialNumber, charge, timestamp}`
- ✅ **APS Control Tab:** Konsolidierte System Commands
- ✅ **APS Steering Tab:** Funktionale Steuerung

### Nächste Schritte:
- 🔄 **Systematischer Aufbau** aller APS-Dashboard Tabs
- 🔄 **Verwendung der Original-Sourcen** als Referenz
- 🔄 **Vollständige APS-Funktionalität** implementieren

## Dateien
- **Analyse-Protokoll:** `docs/analysis/central-control-frontend-prod/README.md`
- **Original-Sourcen:** `integrations/ff-central-control-unit/aps-dashboard-source/`
- **Implementierung:** `omf/dashboard/components/aps_*.py`
