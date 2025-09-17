# SVR4H73275 InstantAction Topic Flow

## Überblick
Das `module/v1/ff/SVR4H73275/instantAction` Topic wird für sofortige Aktionen an einem spezifischen Modul verwendet.

## Message-Statistiken
- **Empfangene Messages**: 1.509 (Received PUBLISH)
- **Gesendete Messages**: 2.630 (Sending PUBLISH)
- **Verhältnis**: ~1:1.74 (mehr Weiterleitungen als direkte Publikationen)

## SVR4H73275 InstantAction Flow

```mermaid
graph LR
    subgraph "SENDER"
        MQTTJS["MQTT.js Dashboard<br/>172.18.0.5<br/>mqttjs_1802b4e7"]
        NODERED1["Node-RED Instance 1<br/>172.18.0.3<br/>nodered_678002a407768a21"]
        NODERED2["Node-RED Instance 2<br/>172.18.0.3<br/>nodered_686f9b8f3f8dbcc7"]
    end
    
    subgraph "MQTT BROKER"
        BROKER["MQTT Broker<br/>192.168.0.100:1883<br/>Mosquitto"]
    end
    
    subgraph "RECEIVER"
        TXT["TXT-Controller<br/>192.168.0.102<br/>auto-84E1E526-F6B8-423D-8FEB-8ED1C3ECCD3C"]
        NODERED2_RECV["Node-RED Instance 2<br/>172.18.0.3<br/>nodered_686f9b8f3f8dbcc7"]
        LOGGER["Logger/Recorder<br/>192.168.0.101<br/>auto-B5711E2C-46E0-0D7B-90E6-AD95D8831099"]
    end
    
    %% Sender to Broker
    MQTTJS -->|"module/v1/ff/SVR4H73275/instantAction<br/>(~1.000 Messages)"| BROKER
    NODERED1 -->|"module/v1/ff/NodeRed/SVR4H73275/instantAction<br/>(~200 Messages)"| BROKER
    NODERED2 -->|"module/v1/ff/NodeRed/SVR4H73275/instantAction<br/>(~300 Messages)"| BROKER
    
    %% Broker to Receiver
    BROKER -->|"module/v1/ff/NodeRed/SVR4H73275/instantAction<br/>(~500 Messages)"| TXT
    BROKER -->|"module/v1/ff/SVR4H73275/instantAction<br/>(~1.000 Messages)"| NODERED2_RECV
    BROKER -->|"ALLE SVR4H73275 Topics<br/>(Vollständige Aufzeichnung)"| LOGGER
    
    %% Styling
    classDef sender fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef broker fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef receiver fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class MQTTJS,NODERED1,NODERED2 sender
    class BROKER broker
    class TXT,NODERED2_RECV,LOGGER receiver
```

## Topic-Varianten

### 1. Standard Topic
- **Topic**: `module/v1/ff/SVR4H73275/instantAction`
- **Publisher**: MQTT.js Dashboard (mqttjs_1802b4e7)
- **Subscriber**: Node-RED Instance 2 (nodered_686f9b8f3f8dbcc7)

### 2. Node-RED Topic
- **Topic**: `module/v1/ff/NodeRed/SVR4H73275/instantAction`
- **Publisher**: Node-RED Instances (nodered_678002a407768a21, nodered_686f9b8f3f8dbcc7)
- **Subscriber**: TXT-Controller (auto-84E1E526-F6B8-423D-8FEB-8ED1C3ECCD3C)

## Message-Flow-Analyse

### Publikationen (Received PUBLISH)
1. **MQTT.js Dashboard** → Broker: `module/v1/ff/SVR4H73275/instantAction`
2. **Node-RED Instance 1** → Broker: `module/v1/ff/NodeRed/SVR4H73275/instantAction`
3. **Node-RED Instance 2** → Broker: `module/v1/ff/NodeRed/SVR4H73275/instantAction`

### Weiterleitungen (Sending PUBLISH)
1. **Broker** → TXT-Controller: `module/v1/ff/NodeRed/SVR4H73275/instantAction`
2. **Broker** → Node-RED Instance 2: `module/v1/ff/SVR4H73275/instantAction`
3. **Broker** → Logger: Alle SVR4H73275 Topics

## QoS-Level
- **QoS 1**: Node-RED → TXT-Controller (zuverlässige Übertragung)
- **QoS 2**: MQTT.js → Node-RED (höchste Zuverlässigkeit)

## Hardware-Zuordnung
- **SVR4H73275**: Spezifische Modul-ID für InstantAction-Befehle
- **TXT-Controller**: Führt die InstantAction-Befehle aus
- **Node-RED**: Verarbeitet und leitet Befehle weiter
- **MQTT.js Dashboard**: Benutzeroberfläche für InstantAction-Steuerung

## Analyse-Zeitraum
- **Datum**: 17. September 2025
- **Zeitraum**: 08:00 - 10:30 Uhr
- **Gesamt-Messages**: 4.139 (1.509 + 2.630)

