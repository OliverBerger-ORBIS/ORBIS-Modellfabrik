# APS-Mosquitto Analyse

## 🎯 Ziel
Vollständige Analyse der APS-Modellfabrik Mosquitto-Komponente basierend auf echten Log-Daten.

## 📋 MQTT Broker Details

**Broker:** Mosquitto auf Raspberry Pi Docker  
**Port:** 1883  
**Config:** `integrations/mosquitto/config/mosquitto.conf`

> 📖 Für System-Architektur und Topic-Details siehe [00-REFERENCE](../00-REFERENCE/README.md)

## 🗂️ Archivierte Analysen

Historische MQTT-Log-Analysen wurden in die zentrale Referenz konsolidiert:
→ [00-REFERENCE](../00-REFERENCE/README.md)

## 🔧 Technische Voraussetzungen

### Raspberry Pi Zugang
- SSH-Verbindung zum APS Raspberry Pi
- Mosquitto-Broker Konfiguration
- Log-Datei Zugriff

### Erwartete Komponenten
- **Node-RED** - Zentrale Steuerung
- **TXT Controller** - Modul-Steuerung
- **CCU** - Central Control Unit
- **APS Module** - MILL, DRILL, AIQS, DPS, HBW
- **Sensoren** - BME680, CAM

### Erwartete Topics
- `module/v1/ff/*/state` - Modul-Status
- `module/v1/ff/*/command` - Modul-Befehle
- `txt/v1/ff/*/data` - TXT-Daten
- `ccu/v1/ff/*/status` - CCU-Status
- `sensor/v1/ff/*/data` - Sensor-Daten

## 📊 Analyse-Ergebnisse

### Phase 1: Log-Konfiguration
- [ ] Mosquitto-Konfiguration erweitert
- [ ] Neue Log-Datei angelegt
- [ ] Client-Connect/Disconnect Logging aktiviert

### Phase 2: System-Neustart
- [ ] Raspberry Pi neu gestartet
- [ ] Alle APS-Komponenten hochgefahren
- [ ] System ohne OSF-UI stabilisiert

### Phase 3: Log-Analyse
- [ ] Log-Datei vom RPi kopiert
- [ ] Client-IDs identifiziert
- [ ] Topic-Patterns analysiert
- [ ] Pub/Sub-Verhältnisse verstanden

### Phase 4: Dokumentation
- [ ] Client-Mapping erstellt
- [ ] Pub/Sub-Analyse dokumentiert
- [ ] Topic-Hierarchie verstanden
- [ ] Node-RED Rolle analysiert

### Phase 5: Integration
- [ ] Neue Dokumentation erstellt
- [ ] Alte Dokumentation ersetzt
- [ ] Links aktualisiert

## 🚀 Status
**✅ Abgeschlossen** - Mosquitto-Log-Analyse vollständig durchgeführt

## 📝 Notizen
- **Wichtig:** Keine OSF-UI Interaktion während der Analyse
- **Ziel:** Reine APS-System-Architektur verstehen
- **Fokus:** Node-RED als zentrale Komponente
