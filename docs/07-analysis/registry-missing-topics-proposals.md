# Registry Ergänzungen - Vorschläge für fehlende Topics

**Datum:** 2025-01-03  
**Basis:** Registry vs. Mosquitto-Log Analyse  
**Fehlende Topics:** 10 wichtige Topics (57 Nachrichten)

## 📋 Vorschläge für Registry-Ergänzungen

### 1. TXT Topics (txt.yml) - 3 Topics

#### `/j1/txt/1/f/i/nfc/ds`
```yaml
- topic: /j1/txt/1/f/i/nfc/ds
  qos: 2
  retain: 0
  schema: wildcard.schema.json
  description: "NFC Input Data Stream - RFID/NFC sensor data from TXT"
  assumption: "NFC sensor readings, workpiece identification"
  # APS as-IS Observation:
  observed_publisher_aps: "unknown"
  observed_subscriber_aps: "unknown"
  # OMF2 Guidance (manual configuration):
  semantic_role: nfc_sensor_data
  triggers: "unknown"
  omf2_usage: "unknown"
  omf2_note: "unknown"
  # Verification:
  verified: false
  data_source: "Mosquitto-Log: 2 messages, q2,r0"
```

#### `/j1/txt/1/f/o/nfc/ds`
```yaml
- topic: /j1/txt/1/f/o/nfc/ds
  qos: 0
  retain: 0
  schema: wildcard.schema.json
  description: "NFC Output Data Stream - RFID/NFC commands to TXT"
  assumption: "NFC commands, workpiece programming"
  # APS as-IS Observation:
  observed_publisher_aps: "unknown"
  observed_subscriber_aps: "unknown"
  # OMF2 Guidance (manual configuration):
  semantic_role: nfc_command_data
  triggers: "unknown"
  omf2_usage: "unknown"
  omf2_note: "unknown"
  # Verification:
  verified: false
  data_source: "Mosquitto-Log: 2 messages, q0,r0"
```

#### `/j1/txt/1/o/ptu`
```yaml
- topic: /j1/txt/1/o/ptu
  qos: 0
  retain: 0
  schema: wildcard.schema.json
  description: "PTU (Pan-Tilt-Unit) Control - Camera positioning commands"
  assumption: "PTU positioning, camera control commands"
  # APS as-IS Observation:
  observed_publisher_aps: "unknown"
  observed_subscriber_aps: "unknown"
  # OMF2 Guidance (manual configuration):
  semantic_role: ptu_control
  triggers: "unknown"
  omf2_usage: "unknown"
  omf2_note: "unknown"
  # Verification:
  verified: false
  data_source: "Mosquitto-Log: 4 messages, q0,r0"
```

### 2. CCU Topics (ccu.yml) - 2 Topics

#### `ccu/pairing/pair_fts`
```yaml
- topic: ccu/pairing/pair_fts
  qos: 2
  retain: 0
  schema: wildcard.schema.json
  description: "FTS Pairing Command - Initiate FTS pairing process"
  assumption: "FTS pairing request, connection establishment"
  # APS as-IS Observation:
  observed_publisher_aps: "unknown"
  observed_subscriber_aps: "unknown"
  # OMF2 Guidance (manual configuration):
  semantic_role: fts_pairing_command
  triggers: "unknown"
  omf2_usage: "unknown"
  omf2_note: "unknown"
  # Verification:
  verified: false
  data_source: "Mosquitto-Log: 1 message, q2,r0"
```

#### `ccu/state/calibration/SVR4H76530`
```yaml
- topic: ccu/state/calibration/SVR4H76530
  qos: 2
  retain: 0
  schema: wildcard.schema.json
  description: "Module Calibration State - SVR4H76530 calibration status"
  assumption: "Module calibration status, positioning accuracy"
  # APS as-IS Observation:
  observed_publisher_aps: "unknown"
  observed_subscriber_aps: "unknown"
  # OMF2 Guidance (manual configuration):
  semantic_role: module_calibration_state
  triggers: "unknown"
  omf2_usage: "unknown"
  omf2_note: "unknown"
  # Verification:
  verified: false
  data_source: "Mosquitto-Log: 3 messages, q2,r0"
```

### 3. FTS Topics (fts.yml) - 1 Topic

#### `fts/v1/ff/5iO4/instantAction`
```yaml
- topic: fts/v1/ff/5iO4/instantAction
  qos: 2
  retain: 0
  schema: wildcard.schema.json
  description: "FTS Instant Action Commands - Immediate FTS control commands"
  assumption: "FTS immediate actions, emergency stops, manual control"
  # APS as-IS Observation:
  observed_publisher_aps: "unknown"
  observed_subscriber_aps: "unknown"
  # OMF2 Guidance (manual configuration):
  semantic_role: fts_instant_action
  triggers: "unknown"
  omf2_usage: "unknown"
  omf2_note: "unknown"
  # Verification:
  verified: false
  data_source: "Mosquitto-Log: 26 messages, q2,r0"
```

### 4. Node-RED Topics (nodered.yml) - 4 Topics

#### `module/v1/ff/NodeRed/SVR4H73275/instantAction`
```yaml
- topic: module/v1/ff/NodeRed/SVR4H73275/instantAction
  qos: 1
  retain: 0
  schema: module_v1_ff_serial_instantAction.schema.json
  description: "Node-RED SVR4H73275 Instant Action - Immediate module control via Node-RED"
  assumption: "Module instant actions via Node-RED OPC-UA bridge"
  # APS as-IS Observation:
  observed_publisher_aps: "unknown"
  observed_subscriber_aps: "unknown"
  # OMF2 Guidance (manual configuration):
  semantic_role: module_instant_action_bridged
  triggers: "unknown"
  omf2_usage: "unknown"
  omf2_note: "unknown"
  # Verification:
  verified: false
  data_source: "Mosquitto-Log: 6 messages, q1,r0"
```

#### `module/v1/ff/NodeRed/SVR4H73275/order`
```yaml
- topic: module/v1/ff/NodeRed/SVR4H73275/order
  qos: 1
  retain: 0
  schema: module_v1_ff_serial_order.schema.json
  description: "Node-RED SVR4H73275 Order - Production orders via Node-RED"
  assumption: "Production orders routed through Node-RED OPC-UA bridge"
  # APS as-IS Observation:
  observed_publisher_aps: "unknown"
  observed_subscriber_aps: "unknown"
  # OMF2 Guidance (manual configuration):
  semantic_role: module_production_order_bridged
  triggers: "unknown"
  omf2_usage: "unknown"
  omf2_note: "unknown"
  # Verification:
  verified: false
  data_source: "Mosquitto-Log: 7 messages, q1,r0"
```

#### `module/v1/ff/NodeRed/SVR4H76530/instantAction`
```yaml
- topic: module/v1/ff/NodeRed/SVR4H76530/instantAction
  qos: 1
  retain: 0
  schema: module_v1_ff_serial_instantAction.schema.json
  description: "Node-RED SVR4H76530 Instant Action - Immediate module control via Node-RED"
  assumption: "Module instant actions via Node-RED OPC-UA bridge"
  # APS as-IS Observation:
  observed_publisher_aps: "unknown"
  observed_subscriber_aps: "unknown"
  # OMF2 Guidance (manual configuration):
  semantic_role: module_instant_action_bridged
  triggers: "unknown"
  omf2_usage: "unknown"
  omf2_note: "unknown"
  # Verification:
  verified: false
  data_source: "Mosquitto-Log: 3 messages, q1,r0"
```

#### `module/v1/ff/NodeRed/SVR4H76530/order`
```yaml
- topic: module/v1/ff/NodeRed/SVR4H76530/order
  qos: 1
  retain: 0
  schema: module_v1_ff_serial_order.schema.json
  description: "Node-RED SVR4H76530 Order - Production orders via Node-RED"
  assumption: "Production orders routed through Node-RED OPC-UA bridge"
  # APS as-IS Observation:
  observed_publisher_aps: "unknown"
  observed_subscriber_aps: "unknown"
  # OMF2 Guidance (manual configuration):
  semantic_role: module_production_order_bridged
  triggers: "unknown"
  omf2_usage: "unknown"
  omf2_note: "unknown"
  # Verification:
  verified: false
  data_source: "Mosquitto-Log: 3 messages, q1,r0"
```

## 🎯 Implementierungsreihenfolge

### **Phase 1: Kritische Topics (🔴 HOCH)**
1. **TXT-Hardware Topics** (3 Topics) - NFC/PTU Funktionalität
2. **FTS instantAction** (1 Topic) - FTS Notfallsteuerung

### **Phase 2: Wichtige Topics (🟡 MITTEL)**
3. **CCU Topics** (2 Topics) - Pairing/Calibration
4. **Node-RED Topics** (4 Topics) - Module-Bridge-Funktionalität

## 📊 Schema-Erstellung

### **Wildcard-Schemas (neue Topics):**
- `wildcard.schema.json` - Für alle neuen Topics ohne spezifisches Schema

### **Bereits vorhandene Schemas (Node-RED Topics):**
- `module_v1_ff_serial_instantAction.schema.json` - Für Node-RED instantAction Topics
- `module_v1_ff_serial_order.schema.json` - Für Node-RED order Topics

## 🔧 Nächste Schritte

1. **Registry-Dateien erweitern** mit den vorgeschlagenen Topics
2. **Wildcard-Schema erstellen** für neue Topics ohne spezifisches Schema
3. **QoS/Retain-Konsistenz validieren** zwischen ähnlichen Topics
4. **Tests aktualisieren** für neue Registry-Einträge

---

**Status:** ✅ **VORBEREITET** - Registry-Ergänzungen definiert  
**Nächster Schritt:** Task 2.9-C - Registry-Ergänzungen implementieren
