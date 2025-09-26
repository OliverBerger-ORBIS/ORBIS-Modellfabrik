# Architecture Documentation Index

Version: 0.1 (Draft)  
Last updated: 2025-09-14  
Author: OMF Development Team  

---

## 📑 Overview
Dieses Verzeichnis enthält die Architektur-Dokumentation der ORBIS Modellfabrik (OMF).  
Die Dokumente beschreiben den Systemkontext, die Message Flows, das Registry-Modell und die Namenskonventionen.  

---

## 🔗 Dokumente

### Core Architecture
- [System Context](system-context.md) – Überblick über Hauptkomponenten (CCU, Module, Node-RED, OMF)
- [Message Flow](message-flow.md) – End-to-End-Flows (Order → Module, State → Dashboard)
- [Registry Model](registry-model.md) – Registry-Prinzipien & Versionierung
- [Message Template System](message-template-system.md) – Template-Manager, Validierung, Topic-Resolution
- [Naming Conventions](naming-conventions.md) – Topics, Template-Keys, IDs

### APS Physical Architecture
- [APS Physical Architecture](../../06-integrations/APS-Ecosystem/system-overview.md) – Fischertechnik Netzwerk & Hardware
- [APS Data Flow](aps-data-flow.md) – Datenverarbeitung & Storage

### Dashboard Architecture
- [OMF Dashboard Architecture](omf-dashboard-architecture.md) – Dashboard-Architektur, MQTT-Patterns, Komponenten-Struktur

### Architektur-Pattern
- [Singleton Pattern Compliance](singleton-pattern-compliance.md) – MQTT-Singleton Pattern Richtlinien
- [Per-Topic-Buffer Pattern](per-topic-buffer-pattern.md) – Effiziente MQTT-Nachrichtenverarbeitung

### Implementierungs-Details
- [Module State Manager](implementation/module-state-manager.md) – Modul-Status-Management Implementierung

---

## 📌 Hinweise
- Alle Dokumente sind Work-in-Progress und werden sprintweise erweitert.  
- Änderungen an Registry und Templates sollen **immer auch hier dokumentiert** werden.  
- Ziel: Architektur bleibt konsistent mit Implementierung und CI-Validierungen.


## 📊 Top-Level Architekturdiagramm


```mermaid
%%{init: {'theme':'neutral'}}%%
flowchart TD
classDef orbis fill:#e3f2fd,stroke:#bbdefb,stroke-width:2px,color:#0b2e59;
classDef fthardware fill:#fff8e1,stroke:#ffecb3,stroke-width:2px,color:#0b3d16;
classDef ftsoftware fill:#ffebee,stroke:#ffcdd2,stroke-width:2px,color:#7a1a14;
classDef external fill:#f5f5f5,stroke:#e0e0e0,stroke-width:2px,color:#333;

  subgraph APS [APS Modellfabrik]
    CCU[APS-CCU<br/>Central Control Unit]:::ftsoftware
    MOD["Module: DRILL/MILL/AIQS/DPS/HBW/CHRG"]:::fthardware
    FTS["FTS - Transport"]:::fthardware
  end

  subgraph NodeRED [Node-RED Gateway]
    NR["MQTT ↔ OPC-UA<br/>Protocol Translator"]:::ftsoftware
  end

  subgraph OMF [OMF Umgebung]
    DASH["OMF Dashboard<br/>Streamlit App"]:::orbis
    REG["Registry<br/>(Schemas, Templates, Enums)"]:::orbis
    SM["Session Manager<br/>Replay/Recording"]:::orbis
  end

  CCU <-->|commands| MOD
  CCU <-->|navigation| FTS
  MOD <-->|opc-ua| NR
  CCU <-->|mqtt| NR
  DASH <-->|mqtt| CCU
  DASH <-->|session data| SM
  DASH -->|templates| REG
  REG -->|config| SM
```
