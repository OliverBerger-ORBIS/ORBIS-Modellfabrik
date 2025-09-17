# MQTT Broker Logik und Message Flow Analyse

## 1. **Retained Messages Logik**

### ✅ **Broker speichert Retained Messages**
- **Flag**: `r1` in Message-Headern
- **Beispiel**: `Sending PUBLISH to omf_dashboard_live (d0, q1, r1, m245, 'ccu/state/version-mismatch', ...)`
- **Funktion**: Neue Subscriber erhalten sofort den letzten Status

### 📊 **Retained Message Pattern**
```
FTS Hardware → Broker (retained) → Neue Clients erhalten sofort Status
```

## 2. **Client Subscription Liste bei Anmeldung**

### 🔍 **Analyse der neuen Clients (10:05-10:30 Uhr)**

#### Client 1: `client-5xg72ydquas`
- **IP**: `::ffff:192.168.0.103:60106`
- **Subscriptions**:
  - `fts/v1/ff/+/state` (QoS 1)
  - `module/v1/ff/+/state` (QoS 1)
  - `module/v1/ff/+/connection` (QoS 1)

#### Client 2: `client-ofpcy1zv0si`
- **IP**: `::ffff:192.168.0.103:60109`
- **Subscriptions**:
  - `fts/v1/ff/+/state` (QoS 1)
  - `module/v1/ff/+/state` (QoS 1)
  - `module/v1/ff/+/connection` (QoS 1)
  - `fts/v1/ff/+/connection` (QoS 1)

### 📋 **Vollständige Subscription Liste**

```mermaid
graph TD
    subgraph "CLIENT SUBSCRIPTIONS"
        C1["client-5xg72ydquas<br/>192.168.0.103"]
        C2["client-ofpcy1zv0si<br/>192.168.0.103"]
        OMF["omf_dashboard_live<br/>192.168.0.103"]
        MQTTJS["mqttjs_1802b4e7<br/>172.18.0.5"]
        NODERED["nodered_686f9b8f3f8dbcc7<br/>172.18.0.3"]
    end
    
    subgraph "TOPICS"
        T1["fts/v1/ff/+/state"]
        T2["fts/v1/ff/+/connection"]
        T3["module/v1/ff/+/state"]
        T4["module/v1/ff/+/connection"]
        T5["ccu/order/request"]
        T6["ccu/order/active"]
        T7["ccu/state/*"]
        T8["/j1/txt/1/i/*"]
    end
    
    C1 --> T1
    C1 --> T3
    C1 --> T4
    C2 --> T1
    C2 --> T2
    C2 --> T3
    C2 --> T4
    OMF --> T5
    OMF --> T6
    OMF --> T7
    OMF --> T8
    MQTTJS --> T5
    MQTTJS --> T6
    NODERED --> T3
    NODERED --> T4
```

## 3. **Message Publisher Detection**

### ❌ **Problem: Publisher-Info nur beim Senden verfügbar**
- **Logik**: `Received PUBLISH from <client-id>`
- **Erkenntnis**: Publisher-Info wird nur registriert, wenn tatsächlich gesendet wird
- **Keine Vorab-Registrierung**: Clients melden nur Subscriptions an, nicht Publications

### 📊 **Publisher Pattern**
```
Client → Broker: SUBSCRIBE (bei Anmeldung)
Client → Broker: PUBLISH (bei Bedarf)
Broker → Subscriber: Weiterleitung
```

## 4. **Node-RED Message Processing Pattern**

### 🔄 **Message Flow: Sender → MQTT → Node-RED → MQTT → Empfänger**

#### Beispiel aus den Logs:
```
1. FTS Hardware → Broker: fts/v1/ff/5iO4/state
2. Broker → Node-RED: fts/v1/ff/5iO4/state
3. Node-RED verarbeitet: State-Änderung erkannt
4. Node-RED → Broker: module/v1/ff/SVR4H73275/connection
5. Broker → Subscriber: module/v1/ff/SVR4H73275/connection
```

### 📋 **Node-RED Processing Topics**

#### **Empfängt** (Input):
- `fts/v1/ff/+/state`
- `fts/v1/ff/+/connection`
- `ccu/order/request`
- `/j1/txt/1/f/o/order`

#### **Sendet** (Output):
- `module/v1/ff/+/connection`
- `module/v1/ff/+/state`
- `ccu/order/active`
- `ccu/order/response`

### 🔄 **Node-RED Message Flow Diagram**

```mermaid
graph LR
    subgraph "HARDWARE"
        FTS["FTS 5iO4<br/>192.168.0.105"]
        TXT["TXT Controller<br/>192.168.0.102"]
    end
    
    subgraph "MQTT BROKER"
        BROKER["Mosquitto<br/>192.168.0.100:1883"]
    end
    
    subgraph "NODE-RED PROCESSING"
        NR["Node-RED<br/>172.18.0.3<br/>nodered_686f9b8f3f8dbcc7"]
    end
    
    subgraph "DASHBOARDS"
        OMF["OMF Dashboard<br/>192.168.0.103"]
        MQTTJS["MQTT.js Dashboard<br/>172.18.0.5"]
    end
    
    %% Hardware to Broker
    FTS -->|"fts/v1/ff/5iO4/state"| BROKER
    TXT -->|"/j1/txt/1/f/o/order"| BROKER
    
    %% Broker to Node-RED
    BROKER -->|"fts/v1/ff/+/state"| NR
    BROKER -->|"/j1/txt/1/f/o/order"| NR
    
    %% Node-RED Processing
    NR -->|"module/v1/ff/+/connection"| BROKER
    NR -->|"module/v1/ff/+/state"| BROKER
    NR -->|"ccu/order/active"| BROKER
    
    %% Broker to Dashboards
    BROKER -->|"module/v1/ff/+/connection"| OMF
    BROKER -->|"module/v1/ff/+/state"| OMF
    BROKER -->|"ccu/order/active"| OMF
    BROKER -->|"ccu/order/active"| MQTTJS
    
    %% Styling
    classDef hardware fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef broker fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef processing fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef dashboard fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class FTS,TXT hardware
    class BROKER broker
    class NR processing
    class OMF,MQTTJS dashboard
```

## 5. **Wichtige Erkenntnisse**

### ✅ **Retained Messages funktionieren**
- Broker speichert letzte Messages mit `r1` Flag
- Neue Subscriber erhalten sofort Status-Updates

### ✅ **Subscription-Liste bei Anmeldung**
- Clients melden Subscriptions bei Anmeldung an
- Broker weiß sofort, wohin Messages weiterleiten

### ❌ **Publisher-Info nur beim Senden**
- Keine Vorab-Registrierung von Publishers
- Publisher-Info nur in `Received PUBLISH` Logs

### 🔄 **Node-RED als Message Processor**
- Empfängt Hardware-Messages
- Verarbeitet und transformiert
- Sendet verarbeitete Messages weiter
- **Pattern**: Hardware → MQTT → Node-RED → MQTT → Dashboard

### 📊 **Message Flow Komplexität**
- **Einfach**: Hardware → MQTT → Dashboard
- **Komplex**: Hardware → MQTT → Node-RED → MQTT → Dashboard
- **Node-RED**: Zentrale Verarbeitungslogik für alle Hardware-Messages

