# Dokumentations-Übersicht

## Was ist dieses Projekt?

**Dieses Repo** enthält die OSF-Entwicklung (ORBIS SmartFactory): OSF-UI (Angular-Dashboard), Session Manager (Helper-App), Anpassungen für die Fischertechnik APS als physische Testumgebung. OSF ist Demonstrator für ORBIS-Produkte (DSP, MES) – Use Cases, Demos, Messen.

**Begriffe:**  
- **ORBIS-Modellfabrik** / **ORBIS-SmartFactory** = Interne Projektzuordnung für Abrechnung (siehe [PROJECT_STATUS](PROJECT_STATUS.md)).  
- **OSF** = Produkt/Dashboard, das hier entwickelt wird.

> **nn-thema-Schema:** Verzeichnisse `01-strategy` bis `07-analysis` sowie `99-glossary` folgen dem Schema `nn-thema`. Querschnittsordner (`assets`, `sprints`, `archive`) ergänzen die Struktur.

---

## Thematische Bereiche (nn-thema)

### 01-Strategy
[01-strategy/README.md](01-strategy/README.md) – Vision (Konzept, Scope), Roadmap (Entwicklungsphasen)

### 02-Architecture
[02-architecture/README.md](02-architecture/README.md) – OSF-Architektur, APS Data Flow, Use-Cases, Namenskonventionen

### 03-Decision Records
[03-decision-records/README.md](03-decision-records/README.md) – Architektur-Entscheidungen (ADRs)

### 04-How-To
[04-howto/README.md](04-howto/README.md) – Anleitungen: Setup, MQTT, Shopfloor, Session Manager, OBS-Präsentation, Testing

### 05-Hardware
- [Messetisch-Spezifikation](05-hardware/messetisch-spezifikation.md) – für Messebauer (Beschaffung/Bau)
- [Vibrationssensor (Arduino)](05-hardware/arduino-vibrationssensor.md) – Projektplan

### 06-Integrations
Einstieg: [00-REFERENCE](06-integrations/00-REFERENCE/README.md) – ORBIS-spezifische APS-Referenz  
Offizielle Fischertechnik: [FISCHERTECHNIK-OFFICIAL](06-integrations/FISCHERTECHNIK-OFFICIAL.md) | [fischertechnik-official/](06-integrations/fischertechnik-official/) (lokale MQTT-Doku)

Weitere: APS-CCU, APS-NodeRED, APS-Ecosystem, TXT-AIQS, TXT-DPS, TXT-FTS, mosquitto

### 07-Analysis
[07-analysis/README.md](07-analysis/README.md) – Test Coverage, Build, MQTT/Registry-Analysen, Publish-Buttons

### 99-Glossary
[99-glossary.md](99-glossary.md) – Begrifflichkeiten (OSF, FMF, APS, Rollen, technische Begriffe)

---

## Querschnittsordner

| Ordner | Inhalt |
|--------|--------|
| **assets/** | Architekturdiagramme (OSF, DSP, FMF), Use-Case-SVGs, Artikel, Hardware-Drawings |
| **_shared/** | Wiederverwendbare Mermaid-Diagramme (Quellen + generierte SVGs) |
| **sprints/** | Sprint-Dokumentation ([sprints_README.md](sprints/sprints_README.md)) |
| **archive/** | Veraltete Dokumentation (OMF2-Legacy) |

---

## Wichtige Einzeldokumente

- [PROJECT_STATUS.md](PROJECT_STATUS.md) – Aktueller Projekt-Status
- [credentials.md](credentials.md) – Zugangsdaten (vertraulich)
