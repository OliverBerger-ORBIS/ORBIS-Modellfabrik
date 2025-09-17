# MQTT Datenfluss-Analyse

## Korrigierte Client-Rollen

### **Publishers (Wer publiziert was):**

1. **Node-RED (CCU)** (`nodered_686f9b8f3f8dbcc7`)
   - `module/v1/ff/SVR3QA0022/connection` (HBW)
   - `module/v1/ff/SVR4H73275/connection` (DPS) 
   - `module/v1/ff/SVR4H76530/connection` (AIQS)

2. **Dashboard/Web** (`mqttjs_1802b4e7`)
   - `ccu/pairing/state`
   - `module/v1/ff/SVR4H73275/instantAction`

3. **TXT-Controller** (`auto-84E1E526-F6B8-423D-8FEB-8ED1C3ECCD3C`)
   - `/j1/txt/1/i/bme680` (Umgebungssensoren)
   - `/j1/txt/1/i/cam` (Kamera)
   - `/j1/txt/1/i/ldr` (Licht)

### **Subscribers (Wer abonniert was):**

1. **Logger/Recorder** (`auto-B5711E2C-46E0-0D7B-90E6-AD95D8831099`)
   - **ALLE Topics** (vollständige Aufzeichnung)

2. **Dashboard/Web** (`mqttjs_1802b4e7`)
   - `module/v1/ff/SVR3QA0022/connection`
   - `module/v1/ff/SVR4H73275/connection` 
   - `module/v1/ff/SVR4H76530/connection`

3. **Node-RED (CCU)** (`nodered_686f9b8f3f8dbcc7`)
   - `module/v1/ff/SVR4H73275/instantAction`

## Datenfluss-Diagramm

```
TXT-Controller ──┐
                 │ /j1/txt/1/i/bme680
                 │ /j1/txt/1/i/cam  
                 │ /j1/txt/1/i/ldr
                 └─→ MQTT Broker ──┐
                                  │
Node-RED (CCU) ──┐                │
                 │ module/v1/ff/*/connection
                 └─→ MQTT Broker ──┼─→ Dashboard/Web
                                  │
Dashboard/Web ──┐                 │
                │ ccu/pairing/state
                │ module/v1/ff/*/instantAction  
                └─→ MQTT Broker ──┘
                                  │
                                  └─→ Logger/Recorder (ALLE Topics)
```

## Topic-Zuordnung zu Komponenten

### **TXT-Controller → MQTT Broker:**
- `/j1/txt/1/i/bme680` (Umgebungssensoren)
- `/j1/txt/1/i/cam` (Kamera-Daten)
- `/j1/txt/1/i/ldr` (Lichtsensor)

### **Node-RED (CCU) → MQTT Broker:**
- `module/v1/ff/SVR3QA0022/connection` (HBW Status)
- `module/v1/ff/SVR4H73275/connection` (DPS Status)
- `module/v1/ff/SVR4H76530/connection` (AIQS Status)

### **Dashboard/Web → MQTT Broker:**
- `ccu/pairing/state` (CCU Pairing-Status)
- `module/v1/ff/SVR4H73275/instantAction` (DPS Commands)

### **MQTT Broker → Dashboard/Web:**
- `module/v1/ff/SVR3QA0022/connection`
- `module/v1/ff/SVR4H73275/connection`
- `module/v1/ff/SVR4H76530/connection`

### **MQTT Broker → Node-RED (CCU):**
- `module/v1/ff/SVR4H73275/instantAction`

### **MQTT Broker → Logger/Recorder:**
- **ALLE Topics** (vollständige Aufzeichnung)

