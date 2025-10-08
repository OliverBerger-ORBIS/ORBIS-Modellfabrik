# APS-Ecosystem Component Mapping

## 🎯 **Client-ID Mapping**

Basierend auf der Mosquitto-Log-Analyse vom 18.09.2025, 16:24:55 - 16:44:00:

| Komponente | Client-ID | IP-Adresse | Rolle | Will Message |
|------------|-----------|------------|-------|--------------|
| **APS Dashboard Frontend** | `mqttjs_bba12050` | 172.18.0.5 | Benutzer-Interface | ❌ Keine |
| **Node-RED (SUB)** | `nodered_abe9e421b6fe3efd` | 172.18.0.4 | Monitoring & Processing | ✅ 38 bytes |
| **Node-RED (PUB)** | `nodered_94dca81c69366ec4` | 172.18.0.4 | Command Publishing | ✅ 38 bytes |
| **TXT-DPS** | `auto-AC941349` | 192.168.0.102 | Distribution Control | ❌ Keine |
| **TXT-AIQS** | `auto-B9109AD9` | 192.168.0.103 | Quality Control | ✅ 208 bytes |
| **TXT-FTS** | `auto-F6DFC829` | 192.168.0.105 | Transport Control | ✅ 212 bytes |

## 🔄 **Verbindungs-Patterns**

### **Initiale Verbindungen (16:24:55)**
```
1758205495: New client connected from 192.168.0.105:38527 as auto-F6DFC829-567D-0985-C27D-262A31EC52D5
1758205495: New client connected from 192.168.0.103:37529 as auto-B9109AD9-6D76-62F1-C918-40D00FC40FF4
1758205495: New client connected from 192.168.0.104:44109 as auto-9BD9E2A9-61B6-66B2-CDC8-591CAEBB5591
1758205495: New client connected from 172.18.0.5:55596 as mqttjs_8e5c7d5a
1758205495: New client connected from 192.168.0.102:46035 as auto-AC941349-4637-28AC-2662-E51FFA998712
```

### **Will Messages (Connection Status)**
```
# TXT-FTS (192.168.0.105)
Will message specified (212 bytes) (r1, q1).
    fts/v1/ff/5iO4/connection

# TXT-AIQS (192.168.0.103)  
Will message specified (208 bytes) (r1, q1).
    module/v1/ff/NodeRed/SVR4H76530/connection

# TXT-DPS (192.168.0.104)
Will message specified (184 bytes) (r1, q1).
    module/v1/ff/NodeRed/SVR4H73275/connection
```

## 📊 **Publish/Subscribe-Verhalten**

### **Dashboard Frontend (mqttjs_bba12050)**
- **Publishes:** `ccu/set/reset` (QoS 2, r0)
- **Subscribes:** Alle relevanten Topics für UI-Updates
- **Rolle:** Benutzer-Interface, sendet Commands

### **Node-RED (SUB) (nodered_abe9e421b6fe3efd)**
- **Subscribes:** Alle MQTT-Topics
- **Publishes:** Verarbeitete Status-Updates
- **Rolle:** Monitoring & Message Processing

### **Node-RED (PUB) (nodered_94dca81c69366ec4)**
- **Publishes:** `ccu/global`, `ccu/order/completed` (QoS 2, r0/r1)
- **Subscribes:** Command-Topics
- **Rolle:** Command Publishing & Workflow-Orchestrierung

### **TXT-Controller**
- **TXT-DPS:** Publishes `/j1/txt/1/i/cam` (7351x, QoS 1, r0/r1)
- **TXT-AIQS:** Publishes `/j1/txt/1/i/bme680` (65x, QoS 1, r0)
- **TXT-FTS:** Publishes `fts/v1/ff/5iO4/state` (37x, QoS 2, r0)

## 🎯 **UI-Interaktions-Korrelation**

### **Factory Reset (16:25:37)**
```
User Action: "Factory Reset" Button klicken
↓
Dashboard sends: ccu/set/reset (QoS 2, r0)
↓
Node-RED (PUB) generates: ccu/global (QoS 2, r0)
Node-RED (PUB) generates: ccu/order/completed (QoS 2, r1)
```

### **Order Completion Events**
- **16:25:37:** Erste Order Completion (nach Factory Reset)
- **16:42:44:** Zweite Order Completion
- **16:43:37:** Dritte Order Completion

## 🔍 **Test-Client Identifikation**

### **Test-Client (auto-AC941349)**
- **IP:** 192.168.0.102 (gleiche IP wie TXT-DPS)
- **Vermutung:** Anderer Browser-Tab oder Dashboard-Instanz
- **Test-Messages:** `test/topic` (1x), `test/topic3` (3x)
- **QoS:** 0 (at most once)

## 📋 **Alte Client-IDs (vor Neustart)**

**Hinweis:** Diese IDs sind von vorherigen Broker-Neustarts und werden nur zur Vollständigkeit aufgeführt:

| Alte Client-ID | Neue Client-ID | Komponente |
|----------------|----------------|------------|
| `auto-F6DFC829-567D-0985-C27D-262A31EC52D5` | `auto-F6DFC829` | TXT-FTS |
| `auto-B9109AD9-6D76-62F1-C918-40D00FC40FF4` | `auto-B9109AD9` | TXT-AIQS |
| `auto-9BD9E2A9-61B6-66B2-CDC8-591CAEBB5591` | `auto-9BD9E2A9` | TXT-DPS (Alt) |
| `mqttjs_8e5c7d5a` | `mqttjs_bba12050` | Dashboard Frontend |
| `auto-AC941349-4637-28AC-2662-E51FFA998712` | `auto-AC941349` | TXT-DPS (Neu) |

## 🚨 **Connection Status Monitoring**

### **Will Message Topics**
- **FTS:** `fts/v1/ff/5iO4/connection`
- **DPS:** `module/v1/ff/NodeRed/SVR4H73275/connection`
- **AIQS:** `module/v1/ff/NodeRed/SVR4H76530/connection`

### **Connection Status Pattern**
```
Connect → Will Message registrieren → Normal Operation → Disconnect → Will Message auslösen
```

**Zweck:** Dashboard erkennt sofort, wenn TXT-Controller offline geht, ohne auf Timeouts warten zu müssen.

## 📝 **Wichtige Erkenntnisse**

1. **Node-RED Dual-Instanz** - SUB und PUB getrennt ✅
2. **TXT-Controller Will Messages** - Connection Status Monitoring ✅
3. **Dashboard-Routing** - 192.168.0.100 → 172.18.0.5 ✅
4. **UI-Interaktions-Korrelation** - Factory Reset → ccu/global ✅
5. **QoS-Patterns** - Konsistent je nach Message-Typ ✅

---

**"Wer ist wer im APS-System - Client-ID Mapping basierend auf Mosquitto-Logs"** 🎯
