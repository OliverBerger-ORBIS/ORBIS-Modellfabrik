# ORBIS SmartFactory – Projektstatus

**Letzte Aktualisierung:** 2026-04-02

> **Workflow:** Die Sprint-Tabelle wird bei jedem Sprint-Abschluss aktualisiert (neue Zeile, Events).  
> Details: [sprints_README.md – Dokumenten-Workflow](sprints/sprints_README.md#-dokumenten-workflow-aktualität-sicherstellen)

## 🚦 Aktueller Status
- OSF (vormals OMF3) produktionsreif für Kunden-Demos; **LogiMAT 2026 durchgeführt** (Demo mit zwei AGVs erfolgreich).
- **Messe-WLAN:** Nur **2,4 GHz** am Stand → **bekanntes Risiko** für Instabilität; angesichts der **ortsbedingten Einschränkung** keine zuverlässige technische „Lösung“ zu erwarten — **Lessons Learned** für weitere Events (Erwartungsmanagement). Siehe [sprint_18.md – Messe-Ergebnis](sprints/sprint_18.md).
- OMF2 als Legacy eingefroren.
- Aktuelle Entwicklung: **Phase 5** — **Sprint 19** (Sensor-Station, Backend/Grafana, Blog, **Hannover-Messe-Vorbereitung**).
- **ORBIS-SmartFactory** ab Sprint 13 (Genehmigung ausstehend, Arbeit wird fortgeführt).

## 🔥 Aktuelle Schwerpunkte
- **Sprint 19:** Arduino-Sensor-Station (OSF-Einbindung, Steuerung, **24 V**, Transportbox), **Backend** mit Persistenz und **Grafana**, **Blog**, **Hannover Messe** (Vogelperspektive, Halterung, OBS-Szenen, **Konftel-20** / Remote). Details [sprint_19.md](sprints/sprint_19.md).
- **02.04.2026:** ORBIS-internes **Vertriebsmeeting** — **OSF-Präsentation** für Vertrieb durchgeführt (Start Sprint 19).
- Nächster großer Außenauftritt v. a. **Hannover Messe** (siehe Roadmap).
- **Phase 5 – MES/DSP-Integration:** ORBIS MES und DSP übernehmen zunehmend die Steuerung (QM-Check, Order-Entscheidungen). APS-CCU als Interim-Layer; Modifikationen: [integrations/APS-CCU/OSF-MODIFICATIONS.md](../integrations/APS-CCU/OSF-MODIFICATIONS.md).
- MES-Integration: Prozessanpassungen (z.B. "2-mal Bohren").
- Azure DevOps Migration.
- Arduino: R4 Multi-Sensor-Station fertig (MPU-6050, SW-420, DHT11, Flamme, MQ-2, Ampel, Sirene). Doku konsolidiert.
- Storytelling-Blog-Serie.

## 📅 Roadmap & Meilensteine

| Sprint | Zeitraum | Ereignis / Fokus | Status |
|--------|----------|------------------|--------|
| **19** | **02.04.26 - 15.04.26** | Sensor-Station, Backend/Grafana, Blog, Hannover-Vorb. ([sprint_19](sprints/sprint_19.md)) | **Laufend** |
| **18** | **19.03.26 - 01.04.26** | **LogiMAT** (Demo **erfolgreich**, 2 AGVs); WLAN **2,4 GHz** Risiko; **Vertrieb** OSF **02.04.** ([sprint_18](sprints/sprint_18.md)) | **Abgeschlossen** |
| 17 | 05.03.26 - 18.03.26 | MES/Integration & LogiMAT Vorbereitung | Abgeschlossen |
| 16 | 19.02.26 - 04.03.26 | Vibration-Sensor, Doku-Check, Marketing-Konsistenz | Abgeschlossen |
| 15 | 05.02.26 - 18.02.26 | OSF-UI Docker, RPi-Deploy, Abschlussbericht | Abgeschlossen |

## 📊 Sprint-Übersicht

| Sprint | Zeitraum | ORBIS-Projekt | OSF-Entwicklungsphase | Externe Events |
|--------|----------|---------------|------------------------|----------------|
| 01 | 24.07 - 06.08.2025 | ORBIS-Modellfabrik | Phase 0 | — |
| 02 | 07.08 - 22.08.2025 | ORBIS-Modellfabrik | Phase 0 | — |
| 03 | 23.08 - 03.09.2025 | ORBIS-Modellfabrik | Phase 1 abgeschlossen | — |
| 04 | 04.09 - 17.09.2025 | ORBIS-Modellfabrik | Phase 2 | — |
| 05 | 18.09 - 01.10.2025 | ORBIS-Modellfabrik | Phase 2 | — |
| 06 | 02.10 - 15.10.2025 | ORBIS-Modellfabrik | Phase 2 | — |
| 07 | 16.10 - 29.10.2025 | ORBIS-Modellfabrik | Phase 2 | — |
| 08 | 30.10 - 12.11.2025 | ORBIS-Modellfabrik | Phase 2 | — |
| 09 | 13.11 - 27.11.2025 | ORBIS-Modellfabrik | Phase 2 | ORBIS-Präsentation WIN (11.11.), Messe BE5.0 Mulhouse (24.–26.11.) |
| 10 | 28.11 - 11.12.2025 | ORBIS-Modellfabrik | Phase 4 | DSP-Kundentag Bostalsee (03.–04.12.) |
| 11 | 12.12 - 24.12.2025 | ORBIS-Modellfabrik | Phase 4 | Kundenpräsentation Gedore (16.12.) |
| 12 | 25.12.2025 - 07.01.2026 | ORBIS-Modellfabrik | Phase 4 | — |
| 13 | 08.01 - 21.01.2026 | ORBIS-SmartFactory | Phase 4 | — |
| 14 | 22.01 - 04.02.2026 | ORBIS-SmartFactory | Phase 4 | — |
| 15 | 05.02 - 18.02.2026 | ORBIS-SmartFactory | Phase 4 (v0.7.10) | OSF-Präsentation Glaston (10.02.) |
| 16 | 19.02 - 04.03.2026 | ORBIS-SmartFactory | Phase 5 | — |
| 17 | 05.03 - 18.03.2026 | ORBIS-SmartFactory | Phase 5 | LogiMAT Vorbereitung |
| 18 | 19.03 - 01.04.2026 | ORBIS-SmartFactory | Phase 5 | LogiMAT Durchführung (Demo OK, 2 AGVs; Messe-WLAN 2,4 GHz); Vertrieb OSF 02.04. |
| 19 | 02.04 - 15.04.2026 | ORBIS-SmartFactory | Phase 5 | Hannover Messe Vorb.; Sensor-Station / Backend / Blog |

> **Spalten-Erläuterung:**  
> - **ORBIS-Projekt:** Interne Projektzuordnung für Abrechnung (ORBIS-Modellfabrik bzw. ORBIS-SmartFactory).  
> - **OSF-Entwicklungsphase:** Entspricht den Phasen aus [Strategy/Roadmap](01-strategy/roadmap.md).  
> - **Externe Events:** Messen, Kundenpräsentationen, Demos.  
>
> **Phase 3** (APS-NodeRED Ablösung) wurde umpriorisiert und nicht angegangen.  
> **Bericht:** [ORBIS-Projekt-Abschlussbericht Sprints 1-12](sprints/ORBIS-Projekt-Abschlussbericht_sprints_01-12.md)

## 📆 Wichtige Events (Ausblick)
- **LogiMAT 2026:** 24–26. März 2026
- **02.04.2026:** **ORBIS Vertriebsmeeting** — Präsentation **OSF** (intern, vor Hannover); erster Tag **Sprint 19** → [sprint_19.md](sprints/sprint_19.md)
- **Hannover Messe 2026:** 20–24. April 2026
- **ORBIS Customer-Connect Event 2026:** Ende April 2026

## 📚 Weitere Dokumentation
- [Roadmap & Entwicklungsphasen](01-strategy/roadmap.md)
- [Sprint-Dokumentation](sprints/) – [sprint_19.md](sprints/sprint_19.md) (aktuell)
- [Decision Records](03-decision-records/)
- [Architektur](02-architecture/)
- [HowTos & Guides](04-howto/)
