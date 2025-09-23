# APS Dashboard Topic Analysis

## Übersicht
Analyse des Original APS-Dashboards (`central-control-frontend-prod`) zur Identifikation der korrekten MQTT-Topic-Payload-Kombinationen.

## Container Details
- **Container:** `central-control-frontend-prod`
- **Image:** `ghcr.io/ommsolutions/ff-frontend-armv7:release-24v-v130`
- **Port:** 80 (extern) → 80 (intern)
- **URL:** `http://192.168.0.100/de/aps/`

## Identifizierte MQTT Topics

### 1. **y.SET_RESET** (Factory Reset)
- **Payload:** `{timestamp: new Date}`
- **QoS:** `2`
- **Verwendung:** Factory Reset
- **Code:** `this.mqtt.publish(y.SET_RESET, e, {qos:2})`

### 2. **y.SET_PARK** (Factory Park)
- **Payload:** `{timestamp: new Date}`
- **QoS:** `2`
- **Verwendung:** Factory Park
- **Code:** `this.mqtt.publish(y.SET_PARK, e, {qos:2})`

### 3. **y.SET_CHARGE** (FTS Charge)
- **Payload:** `{serialNumber: e.serialNumber, charge: o}`
- **QoS:** `2`
- **Verwendung:** FTS Charge/Discharge
- **Code:** `this.mqttService.publish(y.SET_CHARGE, {serialNumber:e.serialNumber, charge:o}, {qos:2})`

### 4. **y.PAIRING_PAIR_FTS** (FTS Pairing)
- **Payload:** `{serialNumber: e.serialNumber}`
- **QoS:** `2`
- **Verwendung:** FTS Pairing
- **Code:** `this.mqttService.publish(y.PAIRING_PAIR_FTS, {serialNumber:e.serialNumber}, {qos:2})`

### 5. **y.DELETE_MODULE** (Module löschen)
- **Payload:** `{serialNumber: e.serialNumber}`
- **QoS:** `2`
- **Verwendung:** Module löschen
- **Code:** `this.mqttService.publish(y.DELETE_MODULE, {serialNumber:e.serialNumber}, {qos:2})`

### 6. **y.SET_MODULE_DURATION** (Module Duration)
- **Payload:** `{serialNumber: this.moduleId, duration: Number(this.durationInput.nativeElement.value)}`
- **QoS:** `2`
- **Verwendung:** Module Duration setzen

### 7. **y.SET_MODULE_CALIBRATION** (Module Calibration)
- **Payload:** `{timestamp: new Date, serialNumber: this.moduleId, command: e, position: o, factory: i, references: a}`
- **QoS:** `2`
- **Verwendung:** Module Calibration

### 8. **y.CANCEL_ORDERS** (Order Abbruch)
- **Payload:** `[o]` (Array von Order IDs)
- **QoS:** `2`
- **Verwendung:** Order Abbruch
- **Code:** `this.mqttService.publish(y.CANCEL_ORDERS, [o])`

## Weitere Topics (ohne Payload-Details)

### Order Management:
- **y.ORDER_RESPONSE** (2x verwendet)
- **y.ORDER_REQUEST** (1x verwendet)
- **y.ACTIVE_ORDERS** (1x verwendet)
- **y.COMPLETED_ORDERS** (1x verwendet)

### Configuration:
- **y.SET_LAYOUT** (1x verwendet)
- **y.SET_FLOWS** (1x verwendet)
- **y.SET_DEFAULT_LAYOUT** (1x verwendet)
- **y.SET_CONFIG** (1x verwendet)
- **y.LAYOUT** (1x verwendet)
- **y.FLOWS** (1x verwendet)
- **y.CONFIG** (1x verwendet)

### Status:
- **y.PAIRING_STATE** (1x verwendet)
- **y.STOCK** (1x verwendet)
- **y.VERSION_MISMATCH** (1x verwendet)
- **y.CALIBRATION_BASE** (1x verwendet)

## Wichtige Erkenntnisse

### 1. **Konsistente QoS-Einstellungen**
- Alle Commands verwenden **QoS: 2** (Exactly Once)
- Dies entspricht der OMF Dashboard Konfiguration

### 2. **Payload-Strukturen**
- **Factory Reset:** `{timestamp: new Date}` ✅
- **FTS Charge:** `{serialNumber: string, charge: boolean}` ✅
- **FTS Pairing:** `{serialNumber: string}` ✅
- **Module Delete:** `{serialNumber: string}` ✅

### 3. **Topic-Naming**
- Alle Topics verwenden das Präfix `y.`
- Konsistente Namenskonvention: `y.SET_*`, `y.PAIRING_*`, etc.

### 4. **MQTT-Client-Verwendung**
- Direkter `mqttClient.publish()` Aufruf
- Keine Gateway-Wrapper wie im OMF Dashboard
- Konsistente `{qos:2}` Konfiguration

## Vergleich mit OMF Dashboard

### Unterschiede:
1. **OMF Dashboard:** Verwendet `MqttGateway` mit `ensure_order_id=True`
2. **APS Dashboard:** Direkter `mqttClient.publish()` ohne `orderId`

### Gemeinsamkeiten:
1. **QoS:** Beide verwenden `qos=2`
2. **Payload-Strukturen:** Ähnliche Strukturen für gleiche Commands
3. **Topic-Namen:** Ähnliche Namenskonventionen

## Empfehlungen für OMF Dashboard

### 1. **APS-Komponenten anpassen**
- Verwende direkten `mqttClient.publish()` statt `MqttGateway`
- Entferne `orderId` Generation für APS-Kompatibilität
- Behalte `qos=2` bei

### 2. **Payload-Strukturen**
- **Factory Reset:** `{timestamp: new Date().toISOString()}`
- **FTS Charge:** `{serialNumber: "5iO4", charge: true/false}`
- **FTS Pairing:** `{serialNumber: "5iO4"}`

### 3. **Topic-Mapping**
- **OMF:** `ccu/set/reset` → **APS:** `y.SET_RESET`
- **OMF:** `ccu/set/charge` → **APS:** `y.SET_CHARGE`
- **OMF:** `ccu/set/pair` → **APS:** `y.PAIRING_PAIR_FTS`

## Nächste Schritte

1. **APS-Komponenten aktualisieren** mit korrekten Topics und Payloads
2. **Topic-Mapping implementieren** zwischen OMF und APS
3. **Tests durchführen** mit realer APS-Fabrik
4. **Dokumentation aktualisieren** mit korrekten Topic-Payload-Kombinationen

## Dateien

- **Quelle:** `./docs/analysis/central-control-frontend-prod/aps-dashboard-source/main.3c3283515fab30fd.js`
- **Analyse:** `./docs/analysis/central-control-frontend-prod/APS_DASHBOARD_TOPIC_ANALYSIS.md`
- **Protokoll:** `./docs/analysis/central-control-frontend-prod/README.md`
