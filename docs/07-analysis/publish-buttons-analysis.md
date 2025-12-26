# Publish Buttons Analysis: OSF vs OMF2

## Übersicht

Diese Analyse vergleicht alle Buttons in OSF (vormals OMF3), die MQTT Topics publishen sollten, mit der OMF2 (Streamlit) Implementierung.

## OSF Buttons - Status

### ✅ Implementiert (publishen bereits Topics)

1. **Order Button** (`overview-tab.component.ts:159`)
   - **Button**: "Order" für BLUE/WHITE/RED
   - **Topic**: `ccu/order/request`
   - **Payload**: `{ type: workpieceType, timestamp: ISO, orderType: 'PRODUCTION' }`
   - **Implementation**: `dashboard.commands.sendCustomerOrder(type)`
   - **Status**: ✅ Funktioniert

2. **Charge Button** (`module-tab.component.ts:260`)
   - **Button**: "Charge" / "Stop Charging" für FTS
   - **Topic**: `ccu/set/charge`
   - **Payload**: `{ serialNumber, charge: boolean, timestamp: ISO }`
   - **Implementation**: `dashboard.commands.setFtsCharge(transport.id, !charging)`
   - **Status**: ✅ Funktioniert

3. **Dock Button** (`module-tab.component.ts:251`)
   - **Button**: "Dock" für FTS (wenn `lastModuleSerialNumber` fehlt)
   - **Topic**: `fts/v1/ff/{serialNumber}/instantAction`
   - **Payload**: `{ timestamp, serialNumber, actions: [{ actionType: 'findInitialDockPosition', actionId, metadata: { nodeId } }] }`
   - **Implementation**: `dashboard.commands.dockFts(transport.id, transport.lastNodeId)`
   - **Status**: ✅ Funktioniert

4. **Calibrate Module Button** (`module-tab.component.ts:217`)
   - **Button**: "Calibrate" für Module mit `hasCalibration`
   - **Topic**: `ccu/set/calibration`
   - **Payload**: `{ timestamp, serialNumber, command: 'startCalibration' }`
   - **Implementation**: `dashboard.commands.calibrateModule(module.id)`
   - **Status**: ✅ Funktioniert

### ⚠️ Teilweise implementiert

5. **Reset Factory Button** (`app.component.ts:252`)
   - **Button**: "Reset factory" im Header
   - **Topic**: `ccu/set/reset` (sollte publisht werden)
   - **Payload**: `{ timestamp: ISO, withStorage: false }` (aus OMF2)
   - **Implementation**: 
     - Mock-Mode: Lädt Fixture `'startup'` ✅
     - Live/Replay-Mode: Nur `console.info('[reset]', environment, 'reset not implemented yet')` ❌
   - **Status**: ⚠️ Nur Mock-Mode funktioniert, Live-Mode fehlt

### ❌ Nicht implementiert

6. **Camera Control Buttons** (`sensor-tab.component.ts:123`)
   - **Buttons**: "Up", "Down", "Left", "Right", "Center" für Kamera-Steuerung
   - **Topic**: `/j1/txt/1/o/ptu` (aus OMF2)
   - **Payload**: 
     - Move: `{ ts: ISO+Z, cmd: 'relmove_up'|'relmove_down'|'relmove_left'|'relmove_right'|'center', degree: number }`
     - Photo: `{ ts: ISO+Z, cmd: 'photo' }`
   - **Implementation**: Nur `console.info('[sensor-tab] camera control action', action, 'step', this.stepSize)`
   - **Status**: ❌ Nicht implementiert

7. **Emergency Stop Button**
   - **Button**: Existiert nicht in OMF3
   - **Topic**: `ccu/set/emergency` (aus OMF2)
   - **Payload**: `{ timestamp: ISO, emergency: true }`
   - **Status**: ❌ Komplett fehlend

## OMF2 Topics - Vergleich

### Topics die in OMF2 publisht werden:

| Topic | OMF2 Location | OSF Status | OSF Location |
|-------|--------------|------------|---------------|
| `ccu/set/reset` | `factory_steering_subtab.py:99` | ⚠️ Teilweise | `app.component.ts:252` (nur Mock) |
| `ccu/set/emergency` | `factory_steering_subtab.py:122` | ❌ Fehlt | - |
| `fts/v1/ff/{serial}/instantAction` | `factory_steering_subtab.py:154` | ✅ Implementiert | `shopfloor-tab.component.ts:251` |
| `ccu/set/charge` | `factory_steering_subtab.py:176,198` | ✅ Implementiert | `shopfloor-tab.component.ts:260` |
| `ccu/order/request` | `factory_steering_subtab.py:220` | ✅ Implementiert | `overview-tab.component.ts:159` |
| `/j1/txt/1/o/ptu` | `sensor_data_subtab.py:802,821` | ❌ Fehlt | `sensor-tab.component.ts:123` (nur console.info) |
| `ccu/set/calibration` | - | ✅ Implementiert | `shopfloor-tab.component.ts:217` |

## Fehlende Features in OSF

### 1. Reset Factory (Live-Mode)
- **Problem**: Funktioniert nur im Mock-Mode
- **Lösung**: `dashboard.commands.resetFactory()` implementieren in `osf/libs/business/src/index.ts`
- **Topic**: `ccu/set/reset`
- **Payload**: `{ timestamp: ISO, withStorage: false }`

### 2. Emergency Stop
- **Problem**: Button existiert nicht
- **Lösung**: 
  - Button im Header hinzufügen (neben Reset Factory)
  - `dashboard.commands.emergencyStop()` implementieren
- **Topic**: `ccu/set/emergency`
- **Payload**: `{ timestamp: ISO, emergency: true }`
- **QoS**: 2 (höchste Priorität)

### 3. Camera Control
- **Problem**: Buttons existieren, publishen aber nichts
- **Lösung**: 
  - `dashboard.commands.moveCamera(action, stepSize)` implementieren
  - `dashboard.commands.takeCameraPhoto()` implementieren
- **Topic**: `/j1/txt/1/o/ptu`
- **Payload**: 
  - Move: `{ ts: ISO+Z, cmd: 'relmove_up'|'relmove_down'|'relmove_left'|'relmove_right'|'center', degree: number }`
  - Photo: `{ ts: ISO+Z, cmd: 'photo' }`

## Nächste Schritte

1. **Test-First Approach**: Tests für alle Publish-Buttons erstellen
2. **Implementierung**: Fehlende Funktionen in `business` Layer implementieren
3. **UI Integration**: Buttons mit Business-Layer verbinden

## Referenzen

- OMF2 Factory Steering: `omf2/ui/admin/generic_steering/factory_steering_subtab.py`
- OMF2 Camera Control: `omf2/ui/ccu/ccu_overview/sensor_data_subtab.py:799-833`
- OSF Business Layer: `osf/libs/business/src/index.ts:464-543`
- OSF MQTT Topics Registry: `omf2/registry/mqtt_clients.yml:44-104` (historische Referenz)

