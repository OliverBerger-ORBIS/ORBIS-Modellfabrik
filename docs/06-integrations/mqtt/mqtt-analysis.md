# MQTT Analyse

⚠️ **WARNUNG**: Diese Analyse wurde automatisch erstellt und enthält fehlerbehaftete Angaben. Die Mosquitto-Analyse war nicht erfolgreich - zu viele Widersprüche und Inkonsistenzen in den Dokumenten. Das Ziel, ein klares PUB/SUB-Konzept zu verstehen, wurde nicht erreicht.

## Warum
Verständnis der PubSub-Architektur der APS. 
**Hintergrund**: Wenn wir die Steuerung der APS übernehmen wollen, müssen wir Topics und Nachrichtenaustausch verstehen.
**Frage**: Welche Nachrichten werden von der zentralen Einheit (CCU/Node-RED) empfangen und welche gesendet?

## Methode
1. **Log-File Analyse**: Analyse der Mosquitto-Log-Files
2. **Verbindung zum RPI**: SSH-Zugang zu 192.168.0.100 (ff22/ff22+)
3. **Log-Level Anpassung**: Änderung der Mosquitto-Config (`log_type all`, `connection_messages true`)
4. **Neustart**: Mosquitto-Container neugestartet
5. **APS in Aktion**: Wareneingang und Produktion ausgeführt
6. **Log-Extraktion**: Komplette Logs von RPI kopiert mit clientId Registration am Brokere

## Log-File Vorbereitung
**Verzeichnis**: `/Users/oliver/Projects/ORBIS-Modellfabrik/data/aps-data/mosquitto/`
**Relevanter Zeitbereich**: 17.09.2025, 08:45-10:30 Uhr
**Analyse-Methode**: Client-ID und IP-Adressen-basierte Zuordnung

## Identifizierte Clients

### Gesicherte Client-IDs aus Logs
- `nodered_686f9b8f3f8dbcc7` (IP: 172.18.0.3) - **Node-RED Container**
- `mqttjs_1802b4e7` (IP: 172.18.0.5) - **APS-dashboard**
- `omf_dashboard_live` (IP: 192.168.0.103) - **OMF Dashboard**
- `auto-84E1E526-F6B8-423D-8FEB-8ED1C3ECCD3C` (IP: 192.168.0.105) - **FTS TXT Controller**
- `auto-B5711E2C-46E0-0D7B-90E6-AD95D8831099` (IP: 192.168.0.102) - **DSP TXT Controller**

### IP-Adressen (dynamisch vergeben)
- **FTS**: 192.168.0.105 (diesmal, normalerweise 192.168.0.104)
- **DSP TXT Controller**: 192.168.0.102 
- **OMF Dashboard**: 192.168.0.103 (normalerweise 192.168.0.5)
- **Docker-Container**: 172.18.0.x (internes Netzwerk)

## Topic-Struktur

### Module Topics
- `module/v1/ff/SVR3QA0022/connection` - Modul-Verbindungsstatus
- `module/v1/ff/SVR4H73275/connection` - Modul-Verbindungsstatus  
- `module/v1/ff/SVR4H76530/connection` - Modul-Verbindungsstatus
- `module/v1/ff/SVR4H73275/instantAction` - Sofort-Aktionen

### CCU Topics
- `ccu/order/request` - Auftragsanfragen von Dashboard (APS, OMF, Cloud-APS)
- `ccu/order/active` - Aktive Aufträge
- `ccu/state/*` - CCU-Status
- `ccu/pairing/state` - Pairing-Status

### FTS Topics
- `fts/v1/ff/5iO4/state` - FTS-Status
- `fts/v1/ff/5iO4/connection` - FTS-Verbindung

### TXT Topics
- `/j1/txt/1/i/bme680` - Sensor-Daten
- `/j1/txt/1/i/cam` - Kamera-Daten
- `/j1/txt/1/i/ldr` - Lichtsensor-Daten
- `/j1/txt/1/f/o/order` - Auftragsausgabe

## Message-Flow Pattern

### Publisher-Subscriber Zuordnung
**Node-RED (CCU)**:
- **Publiziert**: `module/v1/ff/+/connection`, `module/v1/ff/+/state`
- **Abonniert**: `fts/v1/ff/+/state`, `ccu/order/request`, `/j1/txt/1/f/o/order` ??

**FTS Hardware**:
- **Publiziert**: `fts/v1/ff/5iO4/state`, `fts/v1/ff/5iO4/connection`

**TXT Controller**:
- **Publiziert**: `/j1/txt/1/i/*`, `/j1/txt/1/f/o/order` ??

**OMF Dashboard**:
- **Publiziert**: `ccu/order/request` Auftrag-Bestellung
- **Abonniert**: `module/v1/ff/+/connection`, `ccu/order/active`, ALLES, da Dashboard

## Wichtige Erkenntnisse

### Retained Messages
- Broker speichert Messages mit `r1` Flag
- Neue Subscriber erhalten sofort letzten Status
- **Pattern**: Hardware → Broker (retained) → Neue Clients

### Node-RED als Message Processor
- **Empfängt**: Hardware-Messages (FTS, TXT), 
- **empfängt keine** Messages von Modulen, die über SPS gesteuert werden
- **Verarbeitet**: State-Änderungen, Aufträge
- **Sendet**: Verarbeitete Messages an Dashboards
- **Pattern**: Hardware → MQTT → Node-RED → MQTT → Dashboard

### Docker-Netzwerk
- Container laufen im `ff-future-factory-prod` Netzwerk
- Externe IPs: 192.168.0.x (Hardware, Dashboards)
- Container-IPs: 172.18.0.x (Docker-intern)

## Visualisierungen
- **MQTT Data Flow**: `mqtt_data_flow.mermaid`
- **Node-RED Architecture**: `nodered_architecture.mermaid`
- **Order Processing Flow**: `order_processing_flow.mermaid`

## Nächste Schritte
1. **Architektur-Dokumentation aktualisieren** (IP-Adressen, Client-Zuordnungen)
2. **Topic-Mapping für OMF** überprüfen. Verwendung des Parameters direction aus Sicht von Node-RED
3. **Node-Red Flow Analyse** wie erhalten die SPS-Module (MILL, DRILL, AIQS, HBW, DPS) die Commands?