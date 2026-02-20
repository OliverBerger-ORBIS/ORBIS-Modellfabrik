# Fischertechnik APS – Offizielle Dokumentation

**Status:** Öffentlich verfügbar (ab 2025)  
**Quelle:** Fischertechnik, per E-Mail freigeschaltet

Die offizielle Fischertechnik APS-Dokumentation (MQTT, CCU, Anleitung) liegt als **lokale Kopie** in diesem Repo vor; das Original ist auf GitHub öffentlich einsehbar. Diese Datei verweist auf unsere Kopie und auf die Upstream-Quellen.

---

## 📁 Lokale Kopie der MQTT-Dokumentation

**Pfad:** [fischertechnik-official/](fischertechnik-official/)  
**Quellangabe:** [fischertechnik-official/SOURCE.md](fischertechnik-official/SOURCE.md) (Kopiedatum, Commit)

**Inhalt u.a.:**
- `01-introduction.md` – Einführung
- `02-architecture.md` – System-Architektur
- `03-ui-integration.md` – UI-Integration
- `04-opcua-relationship.md` – OPC-UA Beziehung
- `05-message-structure.md` – MQTT-Nachrichtenstruktur
- `06-modules.md` / `06-modules/` – Modul-spezifische Befehle
- `07-calibration.md` – Kalibrierung
- `08-manual-intervention.md` – Manuelle Eingriffe
- `09-tools-and-testing.md` – Werkzeuge und Tests
- `10-scenario-examples.md` – Szenario-Beispiele
- `11-appendices.md` – Anhänge

**Empfehlung:** Für MQTT-Protokoll, Topic-Struktur und Message-Formate primär auf die lokale Kopie [fischertechnik-official/](fischertechnik-official/) zurückgreifen. Aktualisierungen siehe [SOURCE.md](fischertechnik-official/SOURCE.md).

---

## 🔗 Offizielle Upstream-Quellen (GitHub)

### 24V-Dev: CCU, MQTT, Node-RED, Dokumentation

**URL:** [Agile-Production-Simulation-24V-Dev (release)](https://github.com/fischertechnik/Agile-Production-Simulation-24V-Dev)

**Inhalt u.a.:**
- **central-control/** – CCU Backend (Node.js/TypeScript)
- **frontend/** – Angular-Dashboard
- **nodeRed/** – Node-RED Flows und Konfiguration
- **common/** – Gemeinsamer Code und Protokolle
- **mosquitto/** – MQTT-Broker-Konfiguration
- **raspberrypi/** – Raspberry-Pi-Systemkonfiguration
- **scripts/** – Build- und Deployment-Skripte
- **DEPLOYMENT.md** – Anleitung zum Deployment auf Hardware
- **README.md** – Setup, Local Development, Deployment

**Empfehlung:** Für Anleitung zum Bauen, CCU-Source und Deployment auf das offizielle Repo zurückgreifen.

### CCU-Entwicklung und Deployment (FMF/APS)

Für Änderungen am CCU-Code (z. B. MQTT-Topics, Node-RED, Backend) einen **lokalen Clone** des Repos anlegen:

```bash
git clone -b release https://github.com/fischertechnik/Agile-Production-Simulation-24V-Dev.git
```

Änderungen dort vornehmen, gemäß `DEPLOYMENT.md` bauen und in die Docker-Container der FMF/APS deployen.

### 24V (ohne Dev): TXT-Programme, PLC-Programme

**URL:** [Agile-Production-Simulation-24V](https://github.com/fischertechnik/Agile-Production-Simulation-24V)  
**Lokaler Zugriff:** Submodul `vendor/fischertechnik`

**Inhalt u.a.:**
- **TXT4.0-programs/** – `*.ft` (RoBO Pro Coding: FF_AI_24V.ft, FF_CGW.ft, FF_DPS_24V.ft, fts_main.ft, …)
- **PLC-programs/S7_1200_TIAv18/** – `*.zap18` (TIA Portal / UA-Expert: HBW, DPS, AIQS, DRILL, MILL, OVEN)
- **Node-RED/flows.json** – Node-RED Flows
- **doc/** – OPC-UA-Screenshots, etc.

---

## 🗂️ Matrix: Beide Fischertechnik-Repos

| Inhalt | 24V-Dev | 24V (ohne Dev, Submodul) |
|--------|---------|---------------------------|
| **MQTT-Dokumentation** | ✓ docs/ (lokale Kopie in fischertechnik-official/) | – |
| **CCU, Node-RED, mosquitto** | ✓ central-control, nodeRed, mosquitto | flows.json |
| **TXT-Programme (\*.ft)** | – | ✓ TXT4.0-programs/ (RoBO Pro Coding) |
| **PLC-Programme (\*.zap18)** | – | ✓ PLC-programs/S7_1200_TIAv18/ (TIA Portal) |
| **Deployment-Anleitung** | ✓ DEPLOYMENT.md | RPI_Image.md |

**Wo angreifen bei Erweiterung:** MQTT/CCU/Node-RED → 24V-Dev | TXT/PLC → 24V (ohne Dev). Siehe [README](../../README.md#-fischertechnik-quellen--wo-liegt-was).

---

## 📚 Verhältnis zu unserer Dokumentation

| Bereich | Primär | Ergänzung |
|--------|--------|-----------|
| **MQTT-Protokoll, Topics, Messages** | [fischertechnik-official/](fischertechnik-official/) (lokale Kopie) | [00-REFERENCE](00-REFERENCE/README.md) (ORBIS Session-Analysen, unsere Hardware-Mappings) |
| **CCU-Backend, Build, Deployment** | [Fischertechnik Repo](https://github.com/fischertechnik/Agile-Production-Simulation-24V-Dev) | [APS-CCU](APS-CCU/README.md) (ORBIS-spezifische Beobachtungen) |
| **OSF-Integration, Session-Replay** | Nur in unserem Repo | [00-REFERENCE](00-REFERENCE/README.md), [How-Tos](../04-howto/) |

### Was bleibt in `docs/06-integrations/` relevant?

- **00-REFERENCE/** – ORBIS-spezifisch: Module Serial Mapping (unsere Hardware), Session-basierte Verifikation, Abgleich mit OSF
- **APS-CCU, APS-NodeRED, TXT-*/** – ORBIS-spezifische Analysen, Integration mit OSF, Troubleshooting
- **APS-Ecosystem/** – High-Level Übersicht und Kontext für unser Projekt

Die offizielle Fischertechnik-Dokumentation ersetzt unsere Reverse-Engineering-Arbeit zu MQTT und CCU-Source; unsere Docs ergänzen sie um ORBIS-Integration und unsere konkrete Hardware-Umgebung.

---

## 📖 Weitere Fischertechnik-Ressourcen

- [Produktseite APS 24V](https://www.fischertechnik.de/en/products/industry-and-universities/training-models/569289-agile-production-simulation-24v)
- [Dokumentation (PDF)](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/documentation_aps_en-0424.pdf)
- [Quick Start Guide (PDF)](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/quick-start-guide-agile-production-simulation_en.pdf)

---

*Erstellt: 2025-02*  
*Quelle: Fischertechnik E-Mail-Freischaltung*
