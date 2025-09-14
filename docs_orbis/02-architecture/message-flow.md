# Message Flow

Version: 0.1 (Draft)  
Last updated: 2025-09-14  
Author: OMF Development Team  

---

## 📑 Overview
Dieses Dokument beschreibt die End-to-End Message Flows im OMF System.  

---

## 🔄 Order Flow
```mermaid
sequenceDiagram
  participant OMF as OMF Dashboard
  participant CCU as APS CCU
  participant MOD as Module
  OMF->>CCU: Order (MQTT)
  CCU->>MOD: Command (MQTT/OPC-UA)
  MOD-->>CCU: State Update
  CCU-->>OMF: State (MQTT)
```

---

## 📊 Replay Flow
```mermaid
sequenceDiagram
  participant Session as Session Manager
  participant Broker as MQTT Broker
  participant OMF as OMF Dashboard
  Session->>Broker: Replay Messages
  Broker-->>OMF: State / Events
```
