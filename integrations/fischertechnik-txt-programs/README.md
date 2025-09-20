# Fischertechnik TXT Controller Programs

This directory contains the extracted Fischertechnik `.ft` project files from the APS Modellfabrik.

## Structure

Each `.ft` file is a ZIP archive containing:
- **Python source code** (`.py` files)
- **Blockly visual programming** (`.blockly` files) 
- **Configuration files** (`.json` files)
- **Library modules** (`lib/` directory)

## Extracted Programs

### 1. **FF_DPS_24V** - DPS TXT Controller (CCU)
- **IP**: 192.168.0.102
- **Role**: Central Control Unit + DPS Module
- **Key Files**: `FF_DPS_24V.py`, `lib/DPS.py`, `lib/mqtt_utils.py`
- **Features**: Order management, MQTT integration, VDA5050

### 2. **FF_AI_24V** - AIQS TXT Controller  
- **IP**: 192.168.0.103
- **Role**: Quality control and AI image recognition
- **Key Files**: `FF_AI_24V.py`, `lib/AI.py`, `lib/camera.py`

### 3. **FF_CGW** - Cloud Gateway TXT Controller
- **IP**: 192.168.0.104  
- **Role**: Cloud connectivity and external communication
- **Key Files**: `FF_CGW.py`, `lib/cloud_utils.py`

### 4. **fts_main** - FTS TXT Controller
- **IP**: 192.168.0.105
- **Role**: Transport system control
- **Key Files**: `fts_main.py`, `lib/line_follower.py`, `lib/charger.py`

### 5. **ServoCalib_DPS** - DPS Servo Calibration
- **Role**: Calibration utility for DPS servos
- **Key Files**: `ServoCalib_DPS.py`, `lib/calibration_*.py`

## Analysis Status

- ✅ **FF_DPS_24V**: Extracted and ready for analysis
- ✅ **FF_AI_24V**: Extracted and ready for analysis  
- ✅ **FF_CGW**: Extracted and ready for analysis
- ✅ **fts_main**: Extracted and ready for analysis
- ✅ **ServoCalib_DPS**: Extracted and ready for analysis

## Next Steps

1. **Order ID Logic**: Analyze `FF_DPS_24V.py` for order management
2. **MQTT Topics**: Extract topic patterns from `mqtt_utils.py` files
3. **VDA5050 Integration**: Study `vda5050.py` for AGV communication
4. **Module Communication**: Map inter-module message flows

## Related Documentation

- [MQTT Analysis](../../docs/06-integrations/mqtt/)
- [APS Architecture](../../docs/02-architecture/)
