# TXT-AIQS Documentation

**TXT-AIQS** - AIQS TXT Controller Documentation

## Overview

TXT-AIQS is the AI Quality System TXT controller responsible for quality control and AI image recognition in the APS Modellfabrik.

## Status

- **Implementation:** Extracted from `FF_AI_24V` in `/integrations/TXT-AIQS/`
- **Documentation:** Minimal (to be expanded)
- **Analysis:** Code structure analyzed, HTTP endpoint discovery pending

## Related Files

- **Source Code:** `/integrations/TXT-AIQS/`
- **Configuration:** `/integrations/TXT-AIQS/data/config.json`
- **Main Program:** `/integrations/TXT-AIQS/FF_AI_24V.py` (minimal, extracted)
- **Source Archive:** `FF_AI_24V.ft` (ZIP archive with complete source)

## Project Structure

**Aktuelle Struktur (23.12.2025):**
```
integrations/TXT-AIQS/
└── workspaces/              # Spiegelt Controller-Struktur (/opt/ft/workspaces/)
    └── FF_AI_24V/           # ✅ Original-Dateien vom Controller (komplett)
        ├── FF_AI_24V.py     # Haupt-Datei (15 Zeilen)
        ├── lib/             # Alle lib/*.py Dateien (11 Dateien)
        │   ├── camera.py        # Kamera-Konfiguration
        │   ├── machine_learning.py  # ML & Qualitätsprüfung
        │   ├── mqtt_utils.py    # MQTT-Utilities
        │   ├── vda5050.py       # VDA5050-Protokoll
        │   ├── controller.py    # Controller-Initialisierung
        │   ├── display.py       # Display-Funktionen
        │   ├── File.py          # File-Utilities
        │   ├── iw_log.py        # Logging
        │   ├── node_red.py      # Node-RED Integration
        │   ├── sorting_line.py  # Sortierlinie
        │   └── display.qml      # QML Display-Definition
        └── data/            # Konfigurationen
            ├── config.json      # MQTT-Konfiguration
            └── factsheet.json   # VDA5050 Factsheet
```

**Status:** ✅ Alle Original-Sourcen erfolgreich kopiert (23.12.2025)

**Status (22.12.2025):**
- ✅ Vollständige Source-Dateien vom Controller kopiert
- ✅ IP-Adresse: `192.168.0.158` (DHCP)
- ✅ 24 Dateien insgesamt (inkl. data/)

## Code Structure Analysis

### Main Program (`FF_AI_24V.py`)
- Imports libraries and starts main sorting line function
- Very minimal, delegates to `lib/` modules

### Key Libraries

#### `lib/camera.py`
- Camera configuration only
- Sets up USB camera (TXT_SLD_M_USB1_1_camera)
- Configuration: width=320, height=240, fps=15, no rotation
- **No HTTP server code found**

#### `lib/machine_learning.py`
- Image processing and quality control
- Uses `TXT_SLD_M_USB1_1_camera.read_frame()` to get frames directly
- Object detection using TensorFlow Lite model
- Processes frames for quality checks (CRACK, MIPO1, MIPO2, BOHO, etc.)

### Camera Image Access

**Strategie (23.12.2025):** MQTT-Publikation (analog zu TXT-DPS)

**Referenz-Implementierung (TXT-DPS):**
- TXT-DPS publiziert Kamera-Bilder bereits über MQTT: `/j1/txt/1/i/cam`
- Format: `{"ts":"...","data":"data:image/jpeg;base64,..."}`
- Implementierung: `integrations/TXT-DPS/workspaces/FF_DPS_24V/lib/SSC_Publisher.py`
  - `image_callback()` empfängt Kamera-Frames
  - `publish_camera()` publiziert kontinuierlich (FPS-basiert)
  - `frame_to_base64()` konvertiert Frame zu Base64-String

**TXT-AIQS Implementierung (geplant):**
- Kamera-Frames abrufen: `TXT_SLD_M_USB1_1_camera.read_frame()` (bereits vorhanden in `machine_learning.py`)
- Base64-Kodierung: Analog zu TXT-DPS `frame_to_base64()` Funktion
- MQTT-Publikation: Topic `aiqs/camera` (eigenes Topic mit `aiqs/*` Präfix zur Kennzeichnung als "nicht-Standard" Erweiterung)
- Integration: `lib/machine_learning.py` erweitern oder neue `lib/camera_publisher.py` erstellen

**OSF-UI Integration (pausiert bis TXT-Controller Deployment erfolgreich):**
- Gateway `aiqsCameraFrames$` Stream muss erstellt werden (analog zu `cameraFrames$`)
- Topic-Abonnement `aiqs/#` muss hinzugefügt werden
- Anzeige im AIQS-Tab oder als Detail im Shopfloor-Tab (bei AIQS-Station-Auswahl)
- **WICHTIG:** OSF-UI Änderungen werden erst nach erfolgreichem TXT-Controller Deployment durchgeführt

**Veralteter HTTP-Ansatz:**
- ❌ HTTP-Endpoint-Ansatz wurde verworfen (Browser-Sicherheitsprobleme, CORS)
- ❌ `AiqsCameraService` wurde gelöscht (nicht verwendet)

## MQTT Topics

- **State:** `module/v1/ff/SVR4H76530/state`
- **Connection:** `module/v1/ff/SVR4H76530/connection` (direct) and `module/v1/ff/NodeRed/SVR4H76530/connection` (enriched)
- **Sensor Data:** `/j1/txt/1/i/bme680` (BME680 environmental sensor)
- **Camera:** ⏳ `aiqs/camera` (geplant, eigenes Topic mit `aiqs/*` Präfix zur Kennzeichnung als "nicht-Standard" Erweiterung)

## Source-Zugriff

**Siehe:** [TXT-SOURCE-ACCESS.md](../TXT-SOURCE-ACCESS.md) für vollständige Anleitung

**Kurzzusammenfassung:**
- ✅ **SSH/SCP (verwendet):** Source-Dateien erfolgreich kopiert (23.12.2025)
- ⚠️ **ROBO Pro Coding:** Workflow für Änderungen/Deployment noch zu erarbeiten
- 📍 **IP-Adresse:** `192.168.0.158` (aktuell, DHCP-assigned)

## Task 18: Kamera-Bilder in OSF-UI anzeigen

**Ziel:** Kamera-Bilder von AIQS in Shopfloor-Tab anzeigen

**Strategie (23.12.2025):**
1. ✅ **Source-Dateien kopiert:** `integrations/TXT-AIQS/workspaces/FF_AI_24V/`
2. ✅ **Referenz-Implementierung identifiziert:** TXT-DPS MQTT-Kamera-Publikation (`/j1/txt/1/i/cam`)
3. ✅ **HTTP-Ansatz verworfen:** `AiqsCameraService` gelöscht (nicht verwendet)
4. ⏳ **ROBO Pro Coding Workflow erarbeiten** - **KRITISCH: Voraussetzung für alle weiteren Schritte**
   - Wie ändert man Sourcen in ROBO Pro Coding?
   - Wie deployed man geänderte Sourcen auf den Controller?
5. ⏳ **TXT-AIQS MQTT-Publikation implementieren:** 
   - `lib/machine_learning.py` erweitern oder `lib/camera_publisher.py` erstellen
   - Analog zu TXT-DPS: `publish_camera()` Funktion, `frame_to_base64()` Helper
   - Topic: `aiqs/camera` (eigenes Topic mit `aiqs/*` Präfix)
6. ⏸️ **OSF-UI Integration (pausiert):** Wird erst nach erfolgreichem TXT-Controller Deployment durchgeführt
   - Gateway `aiqsCameraFrames$` Stream erstellen
   - Topic-Abonnement `aiqs/#` hinzufügen
   - Anzeige im AIQS-Tab oder Shopfloor-Tab (bei AIQS-Auswahl)

**Referenz-Code:**
- TXT-DPS Implementierung: `integrations/TXT-DPS/workspaces/FF_DPS_24V/lib/SSC_Publisher.py`
  - Zeilen 78-87: `publish_camera()` Funktion
  - Zeilen 171-176: `frame_to_base64()` Helper
  - Zeile 100-102: `image_callback()` Event-Handler
- [ ] Functional analysis of AIQS behavior
- [ ] Image recognition workflow documentation
- [ ] Quality control process mapping
- [ ] Camera HTTP endpoint documentation once discovered
- [ ] Integration testing with real TXT Controller hardware

## Implementation Status

**Task 18 (AIQS-Kamera-Integration):**
- ✅ **Analysis completed** (2025-12-22)
  - Code structure analyzed from source archive
  - Camera access method identified (`read_frame()` in Python)
- ✅ **Referenz-Implementierung identifiziert** (23.12.2025)
  - TXT-DPS MQTT-Kamera-Publikation analysiert (`/j1/txt/1/i/cam`)
  - Implementierungs-Pattern dokumentiert (`publish_camera()`, `frame_to_base64()`)
- ✅ **HTTP-Ansatz verworfen** (23.12.2025)
  - `AiqsCameraService` gelöscht (nicht verwendet, veralteter HTTP-Ansatz)
  - MQTT-Ansatz bestätigt (analog zu TXT-DPS)
- ✅ **Source files copied** (22.12.2025)
  - Complete source files from TXT-Controller (`192.168.0.158`)
  - All `lib/` files and `data/` directory copied
  - SSH access enabled and working
- ✅ **OSF-UI vorbereitet**
  - Gateway `cameraFrames$` Stream vorhanden
  - Sensor-Tab zeigt bereits DPS-Kamera-Bilder an
  - Topic `/j1/txt/1/i/cam` wird bereits abonniert
- ⏳ **ROBO Pro Coding Workflow erarbeiten** - **KRITISCH: Voraussetzung für alle weiteren Schritte**
  - Wie ändert man Sourcen in ROBO Pro Coding?
  - Wie deployed man geänderte Sourcen auf den Controller?
- ⏳ **TXT-AIQS MQTT-Publikation implementieren** (nach erfolgreichem ROBO Pro Coding Workflow)
  - `lib/machine_learning.py` erweitern oder `lib/camera_publisher.py` erstellen
  - Analog zu TXT-DPS Pattern implementieren
  - Topic: `aiqs/camera` (eigenes Topic mit `aiqs/*` Präfix)
- ⏸️ **OSF-UI Integration (pausiert):** Wird erst nach erfolgreichem TXT-Controller Deployment durchgeführt
  - Gateway `aiqsCameraFrames$` Stream erstellen
  - Topic-Abonnement `aiqs/#` hinzufügen
  - Anzeige im AIQS-Tab oder Shopfloor-Tab (bei AIQS-Auswahl)
