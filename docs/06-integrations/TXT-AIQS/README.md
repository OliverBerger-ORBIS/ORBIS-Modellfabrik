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

**Finding (2025-12-22):**
- AIQS camera images are **NOT sent via MQTT** (unlike DPS which uses `/j1/txt/1/i/cam`)
- Python code reads frames directly: `TXT_SLD_M_USB1_1_camera.read_frame()`
- **HTTP endpoint for camera images must be provided by TXT Controller firmware/web interface**
- Standard TXT Controller web interface runs on Port 80
- **API endpoint needs to be discovered** by testing common endpoints or checking TXT Controller web interface

**Possible Endpoints to Test:**
- `/cam.jpg`
- `/camera.jpg`
- `/camera`
- `/cam`
- `/api/camera`
- `/jpg`
- `/image.jpg`
- Standard fischertechnik TXT Controller camera endpoint (check TXT Controller documentation or web interface)

**Endpoint Discovery via Web Interface:**
1. Access TXT Controller web interface: `http://192.168.0.103` (login: `ft` / `fischertechnik`)
2. Check for camera/image related endpoints or API documentation
3. Test common camera endpoints programmatically via `AiqsCameraService` (automatically tests multiple endpoints)

## MQTT Topics

- **State:** `module/v1/ff/SVR4H76530/state`
- **Connection:** `module/v1/ff/SVR4H76530/connection` (direct) and `module/v1/ff/NodeRed/SVR4H76530/connection` (enriched)
- **Sensor Data:** `/j1/txt/1/i/bme680` (BME680 environmental sensor)
- **Camera:** ❌ NOT via MQTT - HTTP access required

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
2. ⏳ **Analyse:** Kamera-Logik in `lib/camera.py` und `lib/machine_learning.py` verstehen
3. ⏳ **MQTT-Topic implementieren:** Neues Topic `module/v1/ff/SVR4H76530/camera` auf TXT-Controller
4. ⏳ **ROBO Pro Coding Workflow:** Wie ändert man Sourcen und deployed sie?
5. ⏳ **OSF-UI Integration:** Topic abonnieren und Bild in Shopfloor-Tab anzeigen

**Alternative (nicht gewählt):** HTTP-Endpoint → Browser-Sicherheitsprobleme (Private Network Access)
  - Test TXT Controller web interface at `http://192.168.0.103` when available
  - Currently blocked: OSF runs only in Mock-Mode, no access to real hardware
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
  - HTTP endpoint discovery approach documented
- ✅ **Service created** (`AiqsCameraService`)
  - Implements automatic endpoint testing
  - Handles errors gracefully
  - Ready for integration once endpoint is known
- ✅ **Source files copied** (22.12.2025)
  - Complete source files from TXT-Controller (`192.168.0.158`)
  - All `lib/` files and `data/` directory copied
  - SSH access enabled and working
- ⏸️ **Integration paused**
  - HTTP endpoint discovery: All tested endpoints return 404
  - Image likely only accessible via Web-Interface file browser (not direct HTTP endpoint)
  - Requires further investigation: Browser DevTools → Network-Tab when opening image
  - Can resume when HTTP endpoint is discovered
