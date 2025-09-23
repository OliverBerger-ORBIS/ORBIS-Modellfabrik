# APS-Modellfabrik Mosquitto Komponente - Analyse Plan

## 🎯 Ziel
Ersetzung von `docs/06-integrations/mqtt/*` durch neue Analyseergebnisse basierend auf echten Mosquitto-Log-Daten.

## 📋 Vorgehen

### Phase 1: Log-Konfiguration vorbereiten
1. **Alte Log-Dateien sichern**
   - Backup von `data/aps-data/mosquitto/*` erstellen
   - Alte Log-Dateien in `data/aps-data/mosquitto/backup/` verschieben
   - Verzeichnis für neue Analyse vorbereiten

2. **Neue Log-Datei auf Raspberry Pi anlegen**
   - SSH-Verbindung zu `192.168.0.100` (ff22/ff22+)
   - Alte Log-Datei umbenennen (Backup)
   - Neue Log-Datei mit Timestamp erstellen
   - Mosquitto-Konfiguration anpassen

3. **Mosquitto-Konfiguration erweitern**
   - `log_type all` - Alle Events loggen (einfach und ausreichend)
   - `connection_messages true` - Client Connect/Disconnect Events
   - `log_timestamp true` - Timestamps für Synchronisation
   - **Zusätzlich**: Terminal-Umleitung für Payload-Extraktion

### Phase 2: System-Neustart ohne OMF-Dashboard
1. **Kompletter APS-Neustart (Hardware)**
   - **APS komplett ausschalten** (Hardware-Schalter)
   - **30 Sekunden warten**
   - **APS wieder anschalten**
   - Alle APS-Komponenten hochfahren lassen
   - **KEINE OMF-Dashboard Interaktion**
   - System in "reinem" APS-Zustand

2. **Wartezeit für System-Stabilisierung**
   - 5-10 Minuten warten
   - Alle Komponenten vollständig initialisiert
   - Normale APS-Betriebsabläufe

### Phase 3: Log-Daten sammeln
1. **System-Log sammeln**
   - **System-Log**: `mosquitto_aps_analysis.log` (PUB/SUB Events, Client-IDs, Topics + Payloads)
   - SSH-Verbindung zu `192.168.0.100` (ff22/ff22+)
   - Log-Datei herunterladen nach `data/aps-data/mosquitto/`

2. **Log-Datei filtern**
   - **Filter-Script**: `log_filter_script.py` (bereits getestet)
   - **Periodische Topics**: Nur erste 10 Beispiele behalten (Kamera, Sensoren)
   - **Wichtige Topics**: Komplett behalten (Orders, Instant Actions, etc.)
   - **Filter-Rate**: ~60% Reduktion bei Kamera-Daten

3. **Log-Datei analysieren**
   - **Client-Connect/Disconnect** Events
   - **PUB/SUB Events** mit Topics und Payloads
   - **Client-ID → Komponente Mapping**
   - **Instant Actions** und **Orders** vom APS-Dashboard
   - **Timestamp-Synchronisation** für Sequenz-Analyse
   - Vergleich mit alter Analyse aus `data/aps-data/mosquitto/backup/`

### Phase 4: Datenanalyse und Dokumentation
1. **Client-ID → Komponente Mapping**
   - Identifikation aller MQTT-Clients
   - Zuordnung zu APS-Komponenten
   - Node-RED als zentrale Komponente

2. **Pub/Sub-Verhältnisse analysieren**
   - Welche Komponenten publizieren was?
   - Welche Komponenten subscribieren was?
   - Node-RED als Publisher/Subscriber
   - Topic-Hierarchie verstehen

3. **Dokumentation erstellen**
   - `docs/analysis/mqtt/aps_mosquitto_analysis.md`
   - `docs/analysis/mqtt/client_mapping.md`
   - `docs/analysis/mqtt/pubsub_analysis.md`
   - `docs/analysis/mqtt/topic_hierarchy.md`

### Phase 5: Integration in Hauptdokumentation
1. **Neue Dokumentation erstellen**
   - `docs/06-integrations/mqtt/README.md`
   - `docs/06-integrations/mqtt/aps_components.md`
   - `docs/06-integrations/mqtt/mqtt_architecture.md`
   - `docs/06-integrations/mqtt/topic_mapping.md`

2. **Alte Dokumentation ersetzen**
   - Backup der alten `docs/06-integrations/mqtt/*`
   - Neue Dokumentation einfügen
   - Links und Referenzen aktualisieren

## 🔧 Technische Details

### Mosquitto-Konfiguration
```conf
# Vereinfachte Logging-Konfiguration (bewährt)
log_dest file /var/log/mosquitto/mosquitto_aps_analysis.log
log_type all
connection_messages true
log_timestamp true

# Bestehende Konfiguration beibehalten
port 1883
allow_anonymous true
password_file /etc/mosquitto/passwd
```

### Fokus auf wichtige Sequenzen
- **Instant Actions**: `module/v1/ff/SVR*/instantAction`
- **Orders**: `ccu/order/request`, `ccu/order/active`
- **Factory Reset**: Module-spezifische Reset-Befehle
- **FTS Charge**: FTS-spezifische Ladungs-Befehle
- **Synchronisation**: Über Topic und Timestamp

### Erwartete Client-IDs (basierend auf alter Analyse)
- `nodered_686f9b8f3f8dbcc7` - **Node-RED Container** (IP: 172.18.0.3)
- `mqttjs_1802b4e7` - **APS-dashboard** (IP: 172.18.0.5)
- `omf_dashboard_live` - **OMF Dashboard** (IP: 192.168.0.103)
- `auto-84E1E526-F6B8-423D-8FEB-8ED1C3ECCD3C` - **FTS TXT Controller** (IP: 192.168.0.105)
- `auto-B5711E2C-46E0-0D7B-90E6-AD95D8831099` - **DSP TXT Controller** (IP: 192.168.0.102)

### Erwartete Topics (basierend auf alter Analyse)
- `module/v1/ff/SVR3QA0022/connection` - Modul-Verbindungsstatus
- `module/v1/ff/SVR4H73275/connection` - Modul-Verbindungsstatus  
- `module/v1/ff/SVR4H76530/connection` - Modul-Verbindungsstatus
- `module/v1/ff/SVR4H73275/instantAction` - Sofort-Aktionen
- `ccu/order/request` - Auftragsanfragen von Dashboard
- `ccu/order/active` - Aktive Aufträge
- `ccu/state/*` - CCU-Status
- `ccu/pairing/state` - Pairing-Status
- `fts/v1/ff/5iO4/state` - FTS-Status
- `fts/v1/ff/5iO4/connection` - FTS-Verbindung
- `/j1/txt/1/i/bme680` - Sensor-Daten
- `/j1/txt/1/i/cam` - Kamera-Daten
- `/j1/txt/1/i/ldr` - Lichtsensor-Daten
- `/j1/txt/1/f/o/order` - Auftragsausgabe

## 📊 Analyse-Ergebnisse

### 1. Client-Mapping
- [ ] Alle MQTT-Clients identifiziert
- [ ] Komponenten-Zuordnung erstellt
- [ ] Node-RED Rolle verstanden

### 2. Pub/Sub-Analyse
- [ ] Publisher-Liste erstellt
- [ ] Subscriber-Liste erstellt
- [ ] Topic-Hierarchie dokumentiert
- [ ] Node-RED als zentrale Komponente verstanden

### 3. System-Architektur
- [ ] APS-Komponenten-Übersicht
- [ ] MQTT-Kommunikationsmuster
- [ ] Topic-Struktur dokumentiert
- [ ] Integration-Punkte identifiziert

## 🚀 Nächste Schritte

1. **Phase 1 starten** - Alte Log-Dateien sichern und Log-Konfiguration vorbereiten
2. **Raspberry Pi Zugang** - SSH-Verbindung zu `192.168.0.100` (ff22/ff22+)
3. **Mosquitto-Konfiguration** - Logging erweitern
4. **System-Neustart** - Reiner APS-Zustand ohne OMF-Dashboard
5. **Log-Analyse** - Daten sammeln und auswerten
6. **Backup aufräumen** - Alte Log-Dateien nach erfolgreicher Analyse löschen

## 📝 Notizen

- **Wichtig:** Keine OMF-Dashboard Interaktion während der Analyse
- **Ziel:** Reine APS-System-Architektur verstehen
- **Fokus:** Node-RED als zentrale Komponente
- **Ergebnis:** Vollständige MQTT-Architektur-Dokumentation
