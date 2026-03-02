# Registry vs. Mosquitto-Log Analyse

**Datum:** 2025-01-03  
**Analysierte Logs:** 
- `mosquitto_analysis_period.analyse.ana` (1.894 Nachrichten, 12 Topics)
- `mosquitto_current.ana` (12.335 Nachrichten, 74 Topics)

## 📊 Gesamtstatistik

| **Metrik** | **Wert** |
|------------|----------|
| **Registry Topics** | 100 |
| **Mosquitto-Log Topics** | 74 |
| **Gemeinsame Topics** | 61 |
| **Nur im Log** | 13 |
| **Nur in Registry** | 39 |

## 🔍 Kritische Erkenntnisse

### 1. Fehlende Topics in Registry (10 wichtige Topics)

| **Kategorie** | **Topic** | **QoS/Retain** | **Anzahl** | **Priorität** |
|---------------|-----------|----------------|------------|---------------|
| **TXT-NFC** | `/j1/txt/1/f/i/nfc/ds` | q2, r0 | 2 | 🔴 **HOCH** |
| **TXT-NFC** | `/j1/txt/1/f/o/nfc/ds` | q0, r0 | 2 | 🔴 **HOCH** |
| **TXT-PTU** | `/j1/txt/1/o/ptu` | q0, r0 | 4 | 🔴 **HOCH** |
| **CCU-Pairing** | `ccu/pairing/pair_fts` | q2, r0 | 1 | 🟡 **MITTEL** |
| **CCU-Calibration** | `ccu/state/calibration/SVR4H76530` | q2, r0 | 3 | 🟡 **MITTEL** |
| **FTS-InstantAction** | `fts/v1/ff/5iO4/instantAction` | q2, r0 | 26 | 🔴 **HOCH** |
| **NodeRed-InstantAction** | `module/v1/ff/NodeRed/SVR4H73275/instantAction` | q1, r0 | 6 | 🟡 **MITTEL** |
| **NodeRed-Order** | `module/v1/ff/NodeRed/SVR4H73275/order` | q1, r0 | 7 | 🟡 **MITTEL** |
| **NodeRed-InstantAction** | `module/v1/ff/NodeRed/SVR4H76530/instantAction` | q1, r0 | 3 | 🟡 **MITTEL** |
| **NodeRed-Order** | `module/v1/ff/NodeRed/SVR4H76530/order` | q1, r0 | 3 | 🟡 **MITTEL** |

### 2. QoS/Retain Inkonsistenzen

#### Node-RED vs. Module Topics
- **Registry:** `module/v1/ff/SVR4H73275/instantAction` = q2, r0
- **Log:** `module/v1/ff/NodeRed/SVR4H73275/instantAction` = q1, r0
- **Problem:** Node-RED Topics verwenden andere QoS-Werte als direkte Module-Topics

#### FTS instantAction fehlt komplett
- **Registry:** `fts/v1/ff/5iO4/instantAction` existiert nicht
- **Log:** 26 Nachrichten mit q2, r0
- **Problem:** Wichtiger FTS-Topic fehlt in Registry

### 3. TXT-Hardware Topics fehlen
- **NFC Topics:** `/j1/txt/1/f/i/nfc/ds`, `/j1/txt/1/f/o/nfc/ds`
- **PTU Topic:** `/j1/txt/1/o/ptu`
- **Problem:** TXT-Hardware-spezifische Topics nicht in Registry

## ✅ Erfolgreiche Korrekturen

### TXT-Topics korrigiert
Die Korrektur der `txt.yml` war erfolgreich! Alle TXT-Topics verwenden jetzt konsistente QoS/Retain-Werte:
- **TXT-Sensoren:** q2,r1 (korrekt)
- **CCU-Topics:** q2,r1 (korrekt)
- **Module-Topics:** q1,r1 / q2,r0 (korrekt)

## 📈 Topic-Aktivität (Top 10)

| **Topic** | **Nachrichten** | **%** |
|-----------|-----------------|-------|
| `/j1/txt/1/i/cam` | 6.744 | 54.7% |
| `ccu/pairing/state` | 1.676 | 13.6% |
| `module/v1/ff/SVR4H73275/instantAction` | 1.646 | 13.3% |
| `fts/v1/ff/5iO4/state` | 293 | 2.4% |
| Module Connections (5 Topics) | 1.220 | 9.9% |
| Weitere Topics | 1.756 | 14.2% |

## 🎯 Handlungsbedarf für Task 2.9-C

### 1. Registry-Ergänzungen erforderlich

#### TXT Topics (txt.yml)
```yaml
- topic: /j1/txt/1/f/i/nfc/ds
  qos: 2
  retain: 0
  description: "NFC Input Data Stream"
- topic: /j1/txt/1/f/o/nfc/ds  
  qos: 0
  retain: 0
  description: "NFC Output Data Stream"
- topic: /j1/txt/1/o/ptu
  qos: 0
  retain: 0
  description: "PTU (Pan-Tilt-Unit) Control"
```

#### CCU Topics (ccu.yml)
```yaml
- topic: ccu/pairing/pair_fts
  qos: 2
  retain: 0
  description: "FTS Pairing Command"
- topic: ccu/state/calibration/SVR4H76530
  qos: 2
  retain: 0
  description: "Module Calibration State"
```

#### FTS Topics (fts.yml)
```yaml
- topic: fts/v1/ff/5iO4/instantAction
  qos: 2
  retain: 0
  description: "FTS Instant Action Commands"
```

#### Node-RED Topics (nodered.yml)
```yaml
- topic: module/v1/ff/NodeRed/SVR4H73275/instantAction
  qos: 1
  retain: 0
  description: "Node-RED SVR4H73275 Instant Action"
- topic: module/v1/ff/NodeRed/SVR4H73275/order
  qos: 1
  retain: 0
  description: "Node-RED SVR4H73275 Order"
- topic: module/v1/ff/NodeRed/SVR4H76530/instantAction
  qos: 1
  retain: 0
  description: "Node-RED SVR4H76530 Instant Action"
- topic: module/v1/ff/NodeRed/SVR4H76530/order
  qos: 1
  retain: 0
  description: "Node-RED SVR4H76530 Order"
```

### 2. QoS/Retain-Konsistenz prüfen
- **Node-RED vs. Module Topics:** Warum unterschiedliche QoS-Werte?
- **FTS instantAction:** Warum fehlt in Registry?
- **TXT-Hardware:** Warum nicht in Registry?

## 📊 QoS/Retain Verteilung im Log

| **Kombination** | **Anzahl** | **%** |
|-----------------|------------|-------|
| q2, r1 | 9.094 | 73.7% |
| q2, r0 | 1.708 | 13.8% |
| q1, r1 | 1.444 | 11.7% |
| q0, r0 | 68 | 0.6% |
| q1, r0 | 21 | 0.2% |

## 🔧 Nächste Schritte

1. **Registry-Ergänzungen implementieren** (10 fehlende Topics)
2. **QoS/Retain-Konsistenz validieren** (Node-RED vs. Module)
3. **TXT-Hardware Topics hinzufügen** (NFC, PTU)
4. **FTS instantAction Topic hinzufügen**
5. **Node-RED Topics systematisch ergänzen**

---

**Status:** ✅ **ABGESCHLOSSEN** - Registry vs. Mosquitto-Log Analyse  
**Nächster Schritt:** Task 2.9-C - Registry-Ergänzungen implementieren
