# TXT Controller Modules

This directory contains the essential TXT controller programs extracted from the Fischertechnik APS Modellfabrik for our OMF (ORBIS Modellfabrik) project.

## Structure

Each TXT module is extracted from ZIP/ZAP18 archives in `vendor/fischertechnik/` and contains:
- **Python source code** (`.py` files)
- **Blockly visual programming** (`.blockly` files) 
- **Configuration files** (`.json` files)
- **Library modules** (`lib/` directory)

## TXT Modules

### 1. **TXT-DPS** - DPS TXT Controller (CCU)
- **Source:** `FF_DPS_24V` from `vendor/fischertechnik/`
- **IP:** 192.168.0.102
- **Role:** Central Control Unit + DPS Module
- **Key Files:** `FF_DPS_24V.py`, `lib/DPS.py`, `lib/mqtt_utils.py`
- **Features:** Order management, MQTT integration, VDA5050

### 2. **TXT-FTS** - FTS TXT Controller
- **Source:** `fts_main` from `vendor/fischertechnik/`
- **IP:** 192.168.0.105
- **Role:** Transport system control
- **Key Files:** `fts_main.py`, `lib/line_follower.py`, `lib/charger.py`
- **Features:** Line following, battery management, collision detection

### 3. **TXT-AIQS** - AIQS TXT Controller
- **Source:** `FF_AI_24V` from `vendor/fischertechnik/`
- **IP:** 192.168.0.103
- **Role:** Quality control and AI image recognition
- **Key Files:** `FF_AI_24V.py`, `lib/machine_learning.py`, `lib/camera.py`
- **Features:** Image recognition, quality control, sorting line

## Extraction Process

All TXT modules are extracted from the `vendor/fischertechnik/` submodule using a unified process:

1. **Source Identification:** Identify relevant `.ft` (ZIP) or `.zap18` archives
2. **Extraction:** Extract to temporary directory
3. **Restructuring:** Move content to `TXT-{MODULE}/` directory
4. **Cleanup:** Remove temporary files and directories

## Analysis Status

- ✅ **TXT-DPS**: Extracted and ready for analysis
- ✅ **TXT-FTS**: Extracted and ready for analysis  
- ✅ **TXT-AIQS**: Extracted and ready for analysis

## Next Steps

1. **Order ID Logic**: Analyze `TXT-DPS/FF_DPS_24V.py` for order management
2. **MQTT Topics**: Extract topic patterns from `mqtt_utils.py` files
3. **VDA5050 Integration**: Study `vda5050.py` for AGV communication
4. **Module Communication**: Map inter-module message flows

## Related Documentation

- [APS Architecture](../../docs/02-architecture/)
- [MQTT Analysis](../../docs/06-integrations/mosquitto/)
- [System Context](../../docs/02-architecture/system-context.md)
