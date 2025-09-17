# SVR4H73275 InstantAction Topic Flow (Korrigiert)

## Überblick
Das `module/v1/ff/SVR4H73275/instantAction` Topic wird für sofortige Aktionen an einem spezifischen Modul verwendet.

## Zeitabschnitt-Korrektur
**Problem identifiziert:** Das ursprüngliche Log (8:00-10:30 Uhr) enthielt mehrere Broker-Neustarts mit unterschiedlichen Node-RED Client-IDs.

**Korrigierter Zeitabschnitt:** 10:05-10:30 Uhr (Auftrag-Rot Periode)
- **Log-Datei:** `mosquitto_auftrag_rot_period.log` (4.931 Zeilen)
- **Relevante SVR4H73275 Messages:** 263 (statt 5.097)

## Message-Statistiken (Korrigiert)
- **Empfangene Messages**: 61 (Received PUBLISH)
- **Gesendete Messages**: 122 (Sending PUBLISH)
- **Verhältnis**: 1:2 (doppelte Weiterleitungen)
- **Gesamt SVR4H73275 Messages**: 263

## SVR4H73275 InstantAction Flow (Korrigiert)

```mermaid
graph LR
    subgraph "SENDER"
        MQTTJS["MQTT.js Dashboard<br/>172.18.0.5<br/>mqttjs_1802b4e7"]
        NODERED["Node-RED (CCU)<br/>172.18.0.3<br/>nodered_686f9b8f3f8dbcc7"]
    end
    
    subgraph "MQTT BROKER"
        BROKER["MQTT Broker<br/>192.168.0.100:1883<br/>Mosquitto"]
    end
    
    subgraph "RECEIVER"
        TXT["TXT-Controller<br/>192.168.0.102<br/>auto-84E1E526-F6B8-423D-8FEB-8ED1C3ECCD3C"]
        NODERED_RECV["Node-RED (CCU)<br/>172.18.0.3<br/>nodered_686f9b8f3f8dbcc7"]
        LOGGER["Logger/Recorder<br/>192.168.0.101<br/>auto-B5711E2C-46E0-0D7B-90E6-AD95D8831099"]
    end
    
    %% Sender to Broker
    MQTTJS -->|"module/v1/ff/SVR4H73275/instantAction<br/>(~30 Messages)"| BROKER
    NODERED -->|"module/v1/ff/NodeRed/SVR4H73275/instantAction<br/>(~31 Messages)"| BROKER
    
    %% Broker to Receiver
    BROKER -->|"module/v1/ff/NodeRed/SVR4H73275/instantAction<br/>(~60 Messages)"| TXT
    BROKER -->|"module/v1/ff/SVR4H73275/instantAction<br/>(~30 Messages)"| NODERED_RECV
    BROKER -->|"ALLE SVR4H73275 Topics<br/>(Vollständige Aufzeichnung)"| LOGGER
    
    %% Styling
    classDef sender fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef broker fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef receiver fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class MQTTJS,NODERED sender
    class BROKER broker
    class TXT,NODERED_RECV,LOGGER receiver
```

## Korrigierte Topic-Varianten

### 1. Standard Topic
- **Topic**: `module/v1/ff/SVR4H73275/instantAction`
- **Publisher**: MQTT.js Dashboard (mqttjs_1802b4e7)
- **Subscriber**: Node-RED (nodered_686f9b8f3f8dbcc7)

### 2. Node-RED Topic
- **Topic**: `module/v1/ff/NodeRed/SVR4H73275/instantAction`
- **Publisher**: Node-RED (nodered_686f9b8f3f8dbcc7)
- **Subscriber**: TXT-Controller (auto-84E1E526-F6B8-423D-8FEB-8ED1C3ECCD3C)

## Korrigierte Message-Flow-Analyse

### Publikationen (Received PUBLISH) - 61 Messages
1. **MQTT.js Dashboard** → Broker: `module/v1/ff/SVR4H73275/instantAction` (~30)
2. **Node-RED** → Broker: `module/v1/ff/NodeRed/SVR4H73275/instantAction` (~31)

### Weiterleitungen (Sending PUBLISH) - 122 Messages
1. **Broker** → TXT-Controller: `module/v1/ff/NodeRed/SVR4H73275/instantAction` (~60)
2. **Broker** → Node-RED: `module/v1/ff/SVR4H73275/instantAction` (~30)
3. **Broker** → Logger: Alle SVR4H73275 Topics (~32)

## Client-ID-Stabilität
**Korrigiert:** Nur eine stabile Node-RED Instanz (nodered_686f9b8f3f8dbcc7) im relevanten Zeitabschnitt.

## QoS-Level
- **QoS 1**: Node-RED → TXT-Controller (zuverlässige Übertragung)
- **QoS 2**: MQTT.js → Node-RED (höchste Zuverlässigkeit)

## Hardware-Zuordnung
- **SVR4H73275**: Spezifische Modul-ID für InstantAction-Befehle
- **TXT-Controller**: Führt die InstantAction-Befehle aus
- **Node-RED**: Verarbeitet und leitet Befehle weiter
- **MQTT.js Dashboard**: Benutzeroberfläche für InstantAction-Steuerung

## Analyse-Zeitraum (Korrigiert)
- **Datum**: 17. September 2025
- **Zeitraum**: 10:05 - 10:30 Uhr (Auftrag-Rot Periode)
- **Log-Datei**: `mosquitto_auftrag_rot_period.log` (4.931 Zeilen)
- **Relevante Messages**: 183 (61 + 122)
- **Reduktion**: 95% weniger Messages durch Zeitabschnitt-Filterung

