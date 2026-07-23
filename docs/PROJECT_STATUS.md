# ORBIS SmartFactory – Projektstatus

**Letzte Aktualisierung:** 2026-07-23

> **Workflow:** Die Sprint-Tabelle wird bei jedem Sprint-Abschluss aktualisiert (neue Zeile, Events).  
> Details: [sprints_README.md – Dokumenten-Workflow](sprints/sprints_README.md#-dokumenten-workflow-aktualität-sicherstellen)

## 🚦 Aktueller Status
- OSF (vormals OMF3) produktionsreif für Kunden-Demos; **LogiMAT 2026 durchgeführt** (Demo mit zwei AGVs erfolgreich).
- **Messe-WLAN:** Nur **2,4 GHz** am Stand → **bekanntes Risiko** für Instabilität; angesichts der **ortsbedingten Einschränkung** keine zuverlässige technische „Lösung“ zu erwarten — **Lessons Learned** für weitere Events (Erwartungsmanagement). Siehe [sprint_18.md – Messe-Ergebnis](sprints/sprint_18.md).
- OMF2 als Legacy eingefroren.
- Aktuelle Entwicklung: **Phase 5** — **Sprint 27** (Grafana-Dashboard-Analyse & Track&Trace; Carry-over Netzwerk/FTS/Blog).
- **ORBIS-SmartFactory** ab Sprint 13 (Genehmigung ausstehend, Arbeit wird fortgeführt).

## 🔥 Aktuelle Schwerpunkte
- **Sprint 27:** Grafana-Dashboard-Analyse (Modus A, Panels, Persistenz) + offene Track&Trace-Tasks; Musashi **14.08.**; Hochschulkooperation Magdeburg (geplant). Details: [sprint_27.md](sprints/sprint_27.md).
- **02.04.2026:** ORBIS-internes **Vertriebsmeeting** — **OSF-Präsentation** für Vertrieb durchgeführt (Start Sprint 19).
- Letzter großer Außenauftritt: **Hannover Messe** + **ORBIS Customer-Connect** (siehe Roadmap).
- **Phase 5 – MES/DSP-Integration:** ORBIS MES und DSP übernehmen zunehmend die Steuerung (QM-Check, Order-Entscheidungen). APS-CCU als Interim-Layer; Modifikationen: [integrations/APS-CCU/OSF-MODIFICATIONS.md](../integrations/APS-CCU/OSF-MODIFICATIONS.md).
- MES-Integration: Prozessanpassungen (z.B. "2-mal Bohren").
- Azure DevOps Migration.
- Arduino: R4 Multi-Sensor-Station fertig (MPU-6050, SW-420, DHT11, Flamme, MQ-2, Ampel, Sirene). Doku konsolidiert.
- Storytelling-Blog-Serie.

## 📅 Roadmap & Meilensteine

| Sprint | Zeitraum | Ereignis / Fokus | Status |
|--------|----------|------------------|--------|
| **27** | **24.07.26 - 06.08.26** | Grafana-Dashboard-Analyse & Track&Trace; Musashi 14.08.; Hochschulkooperation geplant ([sprint_27](sprints/sprint_27.md)) | **Laufend** |
| **26** | **10.07.26 - 23.07.26** | NFC-Tags Track&Trace; Use-Case-Darstellung Desktop 2/3; Grafana; Blog A2 online; Office-Tower; v1.1.10 ([sprint_26](sprints/sprint_26.md)) | **Abgeschlossen** |
| **25** | **26.06.26 - 09.07.26** | LOM-Day Nachbereitung; Praesentationstechnik Windows-Desktops; Router/Netzwerk; OSF-UI v1.1.7 ([sprint_25](sprints/sprint_25.md)) | **Abgeschlossen** |
| **24** | **12.06.26 - 25.06.26** | LOM-Day Vorbereitung; AI-HUB Datenerfassung (Object Detection/Tracking); Integrations-Carry-over ([sprint_24](sprints/sprint_24.md)) | **Abgeschlossen** |
| **23** | **29.05.26 - 11.06.26** | Urlaubssprint; reduzierte Umsetzung; Hardware-/Mounting-Fokus; ORBIS-Amerika-Praesentation 01.06. ([sprint_23](sprints/sprint_23.md)) | **Abgeschlossen** |
| **22** | **15.05.26 - 28.05.26** | ORBIS Feldbetrieb; Live-vs-Replay Datenpfad; Integrationsnachweise; Hager-Praesentation ([sprint_22](sprints/sprint_22.md)) | **Abgeschlossen** |
| **21** | **01.05.26 - 14.05.26** | OCC-Feedback & Stabilisierung; Functional View Default OCC; Track&Trace Korrelation ([sprint_21](sprints/sprint_21.md)) | **Abgeschlossen** |
| **20** | **16.04.26 - 30.04.26** | Hannover Messe + Customer Connect; OSF-UI Demo-Readiness (v1.1.x) ([sprint_20](sprints/sprint_20.md)) | **Abgeschlossen** |
| **19** | **02.04.26 - 17.04.26** | Sensor-Station, Backend/Grafana, Blog, Hannover-Vorb. ([sprint_19](sprints/sprint_19.md)) | **Abgeschlossen** |
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
| 19 | 02.04 - 17.04.2026 | ORBIS-SmartFactory | Phase 5 | Hannover Messe Vorb.; Sensor-Station / Backend / Blog |
| 20 | 16.04 - 30.04.2026 | ORBIS-SmartFactory | Phase 5 | Hannover Messe (20–24.04.); Customer Connect (29–30.04.) |
| 21 | 01.05 - 14.05.2026 | ORBIS-SmartFactory | Phase 5 | OCC Follow-ups (Functional View Default OCC, UX-Flows, Track&Trace Korrelation) |
| 22 | 15.05 - 28.05.2026 | ORBIS-SmartFactory | Phase 5 | Kunde Hager: OSF-Praesentation bei ORBIS (22.05.2026); Fokus Datenpfad Live vs. Replay |
| 23 | 29.05 - 11.06.2026 | ORBIS-SmartFactory | Phase 5 | Urlaubssprint (Urlaub 04.06–12.06); ORBIS-Amerika-Praesentation (Christen, Adjud) am 01.06.2026; Hardware-Fokus (DC/DC- und Router-Mount-Prototypen) |
| 24 | 12.06 - 25.06.2026 | ORBIS-SmartFactory | Phase 5 | LOM-Day Vorbereitung; AI-HUB Kooperation (Dr. Abdul) fuer Object Detection/Tracking; OD-Sessions aufgenommen und bereitgestellt; Praesentationsvideo V1 (OBS Hero+2) erstellt |
| 25 | 26.06 - 09.07.2026 | ORBIS-SmartFactory | Phase 5 | LOM-Day (26.06); Praesentationstechnik Windows-Desktops; Router/Netzwerk; OSF-UI v1.1.7 RPi-Deploy |
| 26 | 10.07 - 23.07.2026 | ORBIS-SmartFactory | Phase 5 | Probelauf Präsentation (14.–15.07.); Blog A2 veröffentlicht (23.07., [Track und Trace in der Fertigung](https://www.orbis-group.com/de-de/blog/branchen/manufacturing/track-und-trace-in-der-fertigung/)); Office-Tower 3D-Druck; OSF-UI v1.1.10; NFC B-soft Live-Test |
| 27 | 24.07 - 06.08.2026 | ORBIS-SmartFactory | Phase 5 | Fokus Grafana-Dashboard-Analyse & Track&Trace; Kundentermin Musashi (14.08.); Hochschulkooperation Magdeburg (geplant); Carry-over Netzwerk/FTS/Blog A3–A4 |

> **Spalten-Erläuterung:**  
> - **ORBIS-Projekt:** Interne Projektzuordnung für Abrechnung (ORBIS-Modellfabrik bzw. ORBIS-SmartFactory).  
> - **OSF-Entwicklungsphase:** Entspricht den Phasen aus [Strategy/Roadmap](01-strategy/roadmap.md).  
> - **Externe Events:** Messen, Kundenpräsentationen, Demos, **Blog-/Outreach-Veröffentlichungen** (Umsatz-relevante OSF-Wirkung).  
>
> **Phase 3** (APS-NodeRED Ablösung) wurde umpriorisiert und nicht angegangen.  
> **Bericht:** [ORBIS-Projekt-Abschlussbericht Sprints 1-12](sprints/ORBIS-Projekt-Abschlussbericht_sprints_01-12.md)

## 📆 Wichtige Events (Ausblick)
- **LogiMAT 2026:** 24–26. März 2026
- **02.04.2026:** **ORBIS Vertriebsmeeting** — Präsentation **OSF** (intern, vor Hannover); erster Tag **Sprint 19** → [sprint_19.md](sprints/sprint_19.md)
- **Hannover Messe 2026:** 20–24. April 2026
- **ORBIS Customer-Connect Event 2026:** 29–30. April 2026
- **22.05.2026:** Kunde **Hager** — OSF-Praesentation bei ORBIS
- **01.06.2026:** ORBIS-Amerika-Mitarbeiter (Christen, Adjud) — OSF-Praesentation
- **26.06.2026:** LOM-Day — Vorstellung der OSF
- **19.06.2026:** **Blog A1** — [Skalierbare Smart Factory](https://www.orbis-group.com/de-de/blog/branchen/manufacturing/skalierbare-smart-factory/) (veröffentlicht)
- **23.07.2026:** **Blog A2** — [Track und Trace in der Fertigung](https://www.orbis-group.com/de-de/blog/branchen/manufacturing/track-und-trace-in-der-fertigung/) (veröffentlicht)
- **geplant:** Hochschulkooperation **Kshitiz Bohara** (Uni Magdeburg) — GenAI / Agentic AI (SmartFactory, MES, DSP); mögl. Use Case: semantische Analyse Track-&-Trace-/Qualitätsereignisse; ORBIS-interne Abstimmung nach Kennenlernen noch offen → [sprint_27.md](sprints/sprint_27.md)
- **14.08.2026:** Kunde **Musashi** — OSF-Kundentermin (Router/Netzwerk + Windows-Desktop-Praesentation; verschoben von 14.07.)

## 📚 Weitere Dokumentation
- [Roadmap & Entwicklungsphasen](01-strategy/roadmap.md)
- [Sprint-Dokumentation](sprints/) – [sprint_27.md](sprints/sprint_27.md) (aktuell)
- [Decision Records](03-decision-records/)
- [Architektur](02-architecture/)
- [HowTos & Guides](04-howto/)
