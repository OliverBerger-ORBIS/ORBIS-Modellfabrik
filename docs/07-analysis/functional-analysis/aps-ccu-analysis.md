# APS-CCU Backend-Code Analyse

**Datum:** 2025-09-23  
**Chat:** Chat-A (Architecture & Documentation)  
**Status:** ✅ Backend-Code erfolgreich extrahiert und strukturiert

## 🎯 Ziel

Extraktion und Analyse des APS-CCU Backend-Codes aus dem Docker-Container für die Entwicklung der OMF-CCU.

## 🔧 Durchgeführte Schritte

### 1. Docker-Container Analyse
- **Container-ID:** `4562fcc8838b`
- **Image:** `ghcr.io/ommsolutions/ff-ccu-armv7:release-24v-v130`
- **Plattform:** Raspberry Pi (ARM64)

### 2. Code-Extraktion
```bash
# Container-Struktur analysiert
docker exec -it 4562fcc8838b /bin/sh
ls -la /app/central-control

# Code extrahiert
docker cp 4562fcc8838b:/app/central-control ./central-control-backend
```

### 3. Code-Transfer
```bash
# Vom RPi auf Mac kopiert
scp -r ff22@192.168.0.100:~/central-control-backend ./

# Auf RPi gelöscht (Sicherheit)
rm -rf ~/central-control-backend
```

### 4. Projekt-Integration
```bash
# In APS-CCU Struktur integriert
mkdir -p integrations/APS-CCU/
mv integrations/ff-central-control-unit integrations/APS-CCU/
cp -r integrations/APS-CCU/backend/* integrations/APS-CCU/ff-central-control-unit/central-control/
```

## 📁 Finale Struktur

```
integrations/APS-CCU/
└── ff-central-control-unit/     # Original (funktionsfähig)
    ├── central-control/         # Backend-Code (aktualisiert)
    │   ├── src/                # TypeScript Source-Code
    │   │   ├── index.js        # Hauptdatei (9930 Bytes)
    │   │   ├── config.js       # Konfiguration
    │   │   ├── helpers.js      # Hilfsfunktionen
    │   │   ├── models/         # Datenmodelle
    │   │   ├── modules/        # 16 Module
    │   │   │   ├── calibration/
    │   │   │   ├── fts/
    │   │   │   ├── order/
    │   │   │   ├── pairing/
    │   │   │   ├── production/
    │   │   │   ├── reset/
    │   │   │   ├── park/
    │   │   │   ├── settings/
    │   │   │   └── version-checker/
    │   │   ├── mqtt/           # MQTT-Integration
    │   │   └── services/       # Services
    │   ├── data/               # Datenverzeichnis
    │   ├── static-data/        # Statische Daten
    │   └── package.json        # Node.js Projekt
    ├── aps-dashboard-source/    # Frontend-Code (Angular)
    ├── docker-compose*.yml      # Docker-Konfiguration
    └── start-services.sh        # Start-Script
```

## 🔍 Backend-Code Analyse

### Technologie-Stack
- **Runtime:** Node.js (>=18.14.0 <19.0.0)
- **Language:** TypeScript (kompiliert zu JavaScript)
- **MQTT:** async-mqtt (^2.6.3)
- **Testing:** Jest
- **Linting:** ESLint + Prettier

### Hauptmodule
1. **calibration** - Kalibrierung
2. **fts** - FTS (Fischertechnik Transport System)
3. **order** - Auftragsverwaltung
4. **pairing** - Modul-Paarung
5. **production** - Produktion
6. **reset** - Reset-Funktionen
7. **park** - Park-Funktionen
8. **settings** - Einstellungen
9. **version-checker** - Versionsprüfung

### MQTT-Integration
- **Client:** async-mqtt
- **Connection:** `connectMqtt()`
- **Topics:** Werden in den Modulen definiert

### Services
- **GeneralConfigService** - Allgemeine Konfiguration
- **FactoryLayoutService** - Fabrik-Layout
- **OrderFlowService** - Auftragsfluss

## 🎯 Nächste Schritte

### Für Chat-A (Architecture & Documentation)
1. **Dokumentation erweitern** - Detaillierte Modul-Analyse
2. **Architektur-Diagramme** - APS-CCU Komponenten
3. **API-Dokumentation** - MQTT-Topics und Commands

### Für Chat-B (Code & Implementation)
1. **Code-Analyse** - Detaillierte Funktions-Analyse
2. **OMF-CCU Entwicklung** - Nachbau der APS-CCU Funktionalität
3. **MQTT-Integration** - OMF-Dashboard Integration

### Für Chat-C (Testing & Validation)
1. **Backend-Tests** - Jest-Tests analysieren
2. **Integration-Tests** - Mit realer Fabrik
3. **Performance-Tests** - MQTT-Performance

## 📋 Wichtige Erkenntnisse

1. **TypeScript-Backend** - Professionell entwickelt mit Tests
2. **Modulare Architektur** - 16 spezialisierte Module
3. **MQTT-zentriert** - Alle Kommunikation über MQTT
4. **Docker-Container** - Läuft auf Raspberry Pi
5. **Funktionsfähig** - Original-Struktur beibehalten

## 🔗 Verwandte Dokumente

- [APS-CCU Integration](../06-integrations/APS-Ecosystem/APS-CCU/)
- [MQTT-Analyse](../../06-integrations/mosquitto/)
- [System-Context](../02-architecture/system-context.md)

---

**✅ Status:** Backend-Code erfolgreich extrahiert und strukturiert  
**📅 Nächste Analyse:** Detaillierte Modul-Analyse (Chat-A)
