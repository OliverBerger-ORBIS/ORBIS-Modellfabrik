# TXT Controller Modules

This directory contains the essential TXT controller programs extracted from the Fischertechnik APS Modellfabrik for our OMF (ORBIS Modellfabrik) project.

## Structure

Each TXT module is extracted from ZIP/ZAP18 archives in `vendor/fischertechnik/` or loaded directly from TXT Controller and contains:
- **Python source code** (`.py` files)
- **Blockly visual programming** (`.blockly` files) 
- **Configuration files** (`.json` files)
- **Library modules** (`lib/` directory)

### Standard Directory Structure

**Aktuelle Struktur (23.12.2025):**
```
integrations/TXT-{MODULE}/
└── workspaces/              # Spiegelt Controller-Struktur (/opt/ft/workspaces/)
    └── {PROJEKT_NAME}/      # Z.B. FF_AI_24V/, FF_DPS_24V/, fts_main/, FF_CGW/
        ├── {PROJEKT_NAME}.py    # Haupt-Datei
        ├── lib/             # Alle lib/*.py Dateien
        │   ├── camera.py
        │   ├── mqtt_utils.py
        │   └── ... (weitere lib-Dateien)
        └── data/            # Konfigurationen
            ├── config.json
            └── factsheet.json
```

**Prinzip:**
- `workspaces/` spiegelt die Struktur auf dem TXT-Controller (`/opt/ft/workspaces/`)
- Original-Sourcen werden **nicht** modifiziert
- Alle Dateien stammen direkt vom Controller (via SSH/tar kopiert)

**Source Access Methods:**
1. **SSH/SCP** (Port 22, aktiv verwendet): `ssh ft@<TXT-IP>` → tar-Archiv erstellen → `scp` kopieren
2. **Web Interface** (Port 80, alternativ): `http://<TXT-IP>` → Login `ft`/`fischertechnik` → Download files
3. **ROBO Pro Coding** (Ziel-Methode, noch zu erarbeiten): Direkter Export/Deploy-Workflow

**Detaillierte Anleitung:** Siehe [TXT-SOURCE-ACCESS.md](../docs/06-integrations/TXT-SOURCE-ACCESS.md)

## TXT Modules

### 1. **TXT-DPS** - DPS TXT Controller (Haupt-Controller)
- **Source:** `FF_DPS_24V` from TXT-Controller
- **IP:** `192.168.0.101` (aktuell, DHCP-assigned)
- **Controller-ID:** `TXT4.0-p0F4`
- **Role:** DPS-Modul-Steuerung und Sensordaten
- **Key Files:** `FF_DPS_24V.py`, `lib/DPS.py`, `lib/mqtt_utils.py`
- **Features:** Order management, MQTT integration, VDA5050, NFC-Reader, Sensoren
- **Status:** ✅ **Relevant für Fabrik-Prozesse**

### 2. **TXT-CGW** - Cloud Gateway Controller (Nicht relevant)
- **Source:** `FF_CGW` from TXT-Controller
- **IP:** `192.168.0.102` (aktuell, DHCP-assigned)
- **Controller-ID:** `TXT4.0-WiY4`
- **Role:** Cloud Gateway - transportiert MQTT-Topics in Fischertechnik-Cloud
- **Key Files:** `FF_CGW.py`, `lib/RemoteGateway.py`
- **Features:** MQTT-Forwarding zu Fischertechnik-Cloud
- **Status:** ⚠️ **Nicht relevant für lokale Fabrik-Prozesse** - Nur Cloud-Forwarding

**Hinweis:** Im DPS-Modul (`SVR4H73275`) gibt es zwei TXT-Controller. Der TXT-DPS steuert das Modul und liefert die Sensordaten, der TXT-CGW dient nur als Cloud-Gateway. Beide werden im Configuration-Tab korrekt angezeigt, aber nur TXT-DPS ist für die Fabrik-Prozesse relevant.

### 3. **TXT-FTS** - FTS TXT Controller
- **Source:** `fts_main` from TXT-Controller
- **IP:** `192.168.0.107` (aktuell, DHCP-assigned)
- **Controller-ID:** `TXT4.0-5iO4`
- **Role:** Transport system control
- **Key Files:** `fts_main.py`, `lib/line_follower.py`, `lib/charger.py`
- **Features:** Line following, battery management, collision detection
- **Status:** ✅ **Relevant für Fabrik-Prozesse**

### 4. **TXT-AIQS** - AIQS TXT Controller
- **Source:** `FF_AI_24V` from TXT-Controller
- **IP:** `192.168.0.158` (aktuell, DHCP-assigned, war `192.168.0.103`)
- **Controller-ID:** `TXT4.0-Q0Y4`
- **Role:** Quality control and AI image recognition
- **Key Files:** `FF_AI_24V.py`, `lib/machine_learning.py`, `lib/camera.py`
- **Features:** Image recognition, quality control, sorting line
- **Status:** ✅ **Relevant für Fabrik-Prozesse**

## Extraction Process

All TXT modules are extracted from the `vendor/fischertechnik/` submodule using a unified process:

1. **Source Identification:** Identify relevant `.ft` (ZIP) or `.zap18` archives
2. **Extraction:** Extract to temporary directory
3. **Restructuring:** Move content to `TXT-{MODULE}/` directory
4. **Cleanup:** Remove temporary files and directories

## Analysis Status

- ✅ **TXT-DPS**: Extracted and ready for analysis (relevant für Fabrik-Prozesse)
- ✅ **TXT-FTS**: Extracted and ready for analysis (relevant)
- ✅ **TXT-AIQS**: Extracted and ready for analysis (relevant)
- ✅ **TXT-CGW**: Extracted (nicht relevant für Fabrik-Prozesse, nur Cloud-Gateway)

## Next Steps

1. **Order ID Logic**: Analyze `TXT-DPS/FF_DPS_24V.py` for order management
2. **MQTT Topics**: Extract topic patterns from `mqtt_utils.py` files
3. **VDA5050 Integration**: Study `vda5050.py` for AGV communication
4. **Module Communication**: Map inter-module message flows

## Related Documentation

- [APS Architecture](../../docs/02-architecture/)
- [MQTT Analysis](../../docs/06-integrations/mosquitto/)
- [System Context](../../docs/02-architecture/system-context.md)
