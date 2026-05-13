# Sprint 21 – OCC Feedback & Stabilisierung (v1.1.x)

**Zeitraum:** 01.05.2026 – 15.05.2026 · **Status:** Abgeschlossen · **Vorheriger Sprint:** [Sprint 20](./sprint_20.md)

**Kurz:** OCC-Feedback in konkrete UX-Verbesserungen übersetzen, offene Sprint-20 Punkte fertigstellen, Korrelation Shopfloor↔Sensoren absichern.

---

## Externe Termine

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **29–30.04.2026** | **ORBIS Customer-Connect (München)** | Feedback/Anforderungen für Verbesserungen |

---

## Coverage Standing

| Stand | Datum | Branches | Functions | Lines | Statements | Gates (B/F/L/S) | Gate-Margin (B/F/L/S) |
|--------|--------|----------|-----------|-------|------------|------------------|------------------------|
| Sprint-Start (Baseline) | 10.05.2026 | 35.76% | 45.74% | 44.04% | 43.28% | 30 / 42 / 47 / 46 | +5.76 / +3.74 / -2.96 / -2.72 pp |
| Aktuell (Sprint-Ende) | 13.05.2026 | 39.44% | 49.80% | 49.18% | 48.36% | 30 / 42 / 47 / 46 | +9.44 / +7.80 / +2.18 / +2.36 pp |

- **Messmethode (konstant):** `NODE_OPTIONS="--max-old-space-size=4096" BASELINE_BROWSER_MAPPING_IGNORE_OLD_DATA=true npx jest --config "osf/apps/osf-ui/jest.config.ts" --runInBand --coverage --coverageDirectory ".tmp-coverage-osf-ui" --coverageReporters=json-summary --coverageThreshold='{}'` (Quelle: `osf/apps/osf-ui/.tmp-coverage-osf-ui/coverage-summary.json`, Feld `total`)
- **Top-3 Gaps (Test-Fokus):**
  1. `osf/apps/osf-ui/src/app/tabs/shopfloor-tab.component.ts` — 42.63% Lines, 666 uncovered
  2. `osf/apps/osf-ui/src/app/tabs/agv-tab.component.ts` — 54.07% Lines, 389 uncovered
  3. `osf/apps/osf-ui/src/app/components/dsp-animation/dsp-animation.component.ts` — 41.21% Lines, 318 uncovered
- **Schwellenwerte erhöhen:** sukzessive (z. B. +1pp), wenn Gate-Margins stabil positiv sind.

---

## Aufgaben (thematisch, mit Haken)

### OCC Feedback – Verbesserungen

- [x] **Functional View (Default OCC):** Business-Process Lane Reihenfolge anpassen: **ERP → MES → EWM → CRM → Analytical → Data-Lake** (CRM ersetzt Planning) — umgesetzt in `OSF_OCC_2026_CONFIG.bpProcesses` (05.05.2026)
- [x] **Functional View (Default OCC):** neuen Customer „OCC“ / Default-Konfiguration anlegen (neue Lane-Reihenfolge + Links/Defaults) — `OSF_CONFIG` zeigt jetzt auf OCC-Default (Evolution FMF→LogiMAT→Hannover/CC→OCC bleibt verfügbar) (05.05.2026)
- [x] **Functional View Animation:** 9 Functional DSP Icons wieder einzeln einbauen (LogiMAT-ähnliche Variante als Default für OCC) — umgesetzt mit schrittweiser Einzel-Einblendung in der Functional Story (05.05.2026, `npx nx test osf-ui --testPathPattern=layout\.functional\.story-order\.spec\.ts`)
- [x] **Functional View Animation:** Interoperability SVG/Icon in Animation deutlich größer darstellen; zentral positioniert und DSP-Edge-Icon im Summary-Step ausgeblendet (05.05.2026, `npx nx test osf-ui --testPathPattern=layout\.functional\.story-order\.spec\.ts`)
- [x] **Use-Case „Anomaly Detection“:** CRM Integration (Vibration löst Alarm aus → DSP-Edge sendet an MS-CRM → CRM „Prozess gestartet“/Techniker-Einsatz) — als neuer UC-07 umgesetzt (Concept + Live-Demo-Button), UC-05 auf datenbasierte Predictive-Maintenance-Story ohne Anomaly-Fokus geschärft; Sensorik-Darstellung: UC-05 = Sensor-Station, UC-07 = Vibration + Tilt; Export/Inventory final verifiziert (06.05.2026, `npx nx test osf-ui --testPathPattern='predictive-maintenance|anomaly-detection|dsp-use-cases'`, `node scripts/export-use-case-svgs.js`)
- [x] **Process-Tab:** beim Wechsel in den Tab automatisch Refresh ausführen (Inventory/Lagerinfo ohne Button-Drücken) — `ProcessTabComponent.ngOnInit` ruft `refreshProcessData()` auf (05.05.2026, `nx test osf-ui --testPathPattern=process-tab.component.spec`)
- [x] **Process → Order:** nach Auslösen einer Order (`ccu/order/request`) **ohne** Tab-Wechsel (mehrere Aufträge möglich); Sprung in den Order-Tab nur per Klick auf eine **Production-Flow-Produktkarte** (Blue/White/Red) rechts → `openOrderTabFromProductionFlow` / `/:locale/order?product=…` (05.05.2026, Unit-Tests `openOrderTab`, `openOrderTabFromProductionFlow`)
- [x] **Order → Shopfloor:** aus dem Order-Tab in den Shopfloor-Tab — **Modul** auf der eingebetteten Shopfloor-Vorschau in der Order-Card anklicken → `/:locale/shopfloor?module=…` (z. B. HBW), Fokus wie Shopfloor-Tab `selectModuleByType` (05.05.2026, `order-card.component.spec`)
- [x] **UX/Navigation (Analyse):** Entscheidungsgrundlage: `BackButtonComponent` in den **Haupt-Tabs** (z. B. Process/Order/Shopfloor nach Deep-Link-Flows) einbauen **oder** bewusst nur **Sidebar-Navigation** + **Browser-Zurück**; Status quo: Use-Case-Seiten haben `app-back-button`, die Tab-Routen nicht — entschieden: kein permanenter Back-Button in Haupt-Tabs; Sidebar+Browser-Back bleibt Standard, Deep-Link-Kontext im Order-Tab über `?product=` sichtbar gemacht (07.05.2026, `npx nx test osf-ui --testPathPattern='order-tab.component.spec|process-tab.component.spec|order-card.component.spec'`)
- [x] **Track & Trace Use-Case:** Umwelt-/Sensor-Daten eventbasiert „samplen“/speichern (Snapshots zu Shopfloor-Events: HBW Pick/Drop, DPS Pick/Drop, DRILL/MILL/AIQS Prozessschritte) — umgesetzt inkl. 3-Spalten-Timeline mit zeitsynchroner Sensor-Spalte (07.05.2026, `npx nx test osf-ui --testPathPattern='track-trace.component.spec|track-trace-tab.component.spec|workpiece-history.service.spec'`)
- [x] **Analyse/Fix:** Track&Trace Live zeigt AIQS-Event-Sequenzen doppelt (Start+Ende) → Root cause + Fix (z. B. Produkt Blau: AIQS, DRILL, MILL, AIQS) — semantische Dedup-Logik stabilisiert (quellenübergreifend FTS/Module) und Klammer-Prinzip wiederhergestellt (07.05.2026, `npx nx test osf-ui --testPathPattern='workpiece-history.service.spec'`)
- [x] **Track&Trace Business-Kontext:** geplante Stationskette kurz anzeigen (z. B. Lagerauftrag: DPS→HBW; Produktion Blau: HBW→DRILL→MILL→AIQS→DPS) — sichtbar im Order-Kontext inkl. Flow-Akzenten/Lane auf Event-Höhe und Stations-Icons (07.05.2026, visuelle Verifikation Mock-Environment)

### Hannover Messe / Presentation (Übernahme aus Sprint 20)

- [x] OBS-Setup Hannover finalisiert (vereinfacht): OBS nur fuer Kamera-Quelle/-Rotation; alte komplexe OBS-Szenenansaetze verworfen — dokumentiert in [obs-video-presentation-setup.md](../04-howto/presentation/obs-video-presentation-setup.md) (06.05.2026)
- [x] Konftel-20: Stationen als Zoom-Szenen/Preset fuer Remote ohne Blockade der Demo-Pipeline festgelegt (06.05.2026)
- [x] Shopfloor-Rotation: finaler Ablauf (Kamera ueber OBS, Shopfloor ueber OSF-UI-Settings, Layout ueber FancyZones) als Checkliste in How-to dokumentiert (06.05.2026)

### OSF-UI – Bugs / UX (Übernahme aus Sprint 20)

- [x] **Shopfloor AGV-Sichtbarkeit (Live-Status 12.05.2026):** Gestern gemeldetes Problem (AGV-Tab/AGV-Sichtbarkeit auf RPi) heute nicht reproduzierbar; Test auf Windows-Client erfolgreich (Edge/Chrome/Firefox als Zielplattform). Bewertung: vermutlich umgebungs-/browserabhaengig (RPi/OS/Browser-Kombination), aktuell kein blockierender Fehler fuer den Praesentationsbetrieb. Guard: vor Demos kurzer AGV-Sichtbarkeits-Smoke-Test auf Windows durchfuehren.

### Backend & Grafana (Übernahme aus Sprint 20)

- [x] Architekturentscheidung + Leitplanken dokumentiert: **DSP-Edge als Zielplattform**, Deploy in Phase 1 variabel (**local-dev**, **rpi-pilot**, **edge-prod**), MQTT-Ingest read-only, generisches Sensor-Metrikmodell — DR-28 erstellt (08.05.2026)
- [x] Edge Persistence Stack lokal implementiert (Docker Compose, Postgres/Timescale, Grafana-Provisioning, Persistence-Service, Schema/Retention) — lokale Unit-Tests + Type-Checks grün (08.05.2026, `npm run test`, `npm run lint:types`)
- [x] Lokaler Replay-Smoke-Test erfolgreich (synthetische Arduino-Session): Parsing/Normalisierung verifiziert (`station_id`, `sensor_type`), Reason-Logik mit `EVENT`/`THRESHOLD`/`INTERVAL` nachgewiesen (08.05.2026, SQL-Checks in `sensor_snapshot`)
- [x] Grafana lokal visuell verifizieren (Dashboards: Systemstatus, Aufträge, Workpiece Trace, Sensor Snapshots, Modul-/FTS-Zustände) inkl. kurzer Abnahme-Notiz — prinzipieller technischer Durchstich-Test erfolgreich (11.05.2026, lokal ohne RPi): Replay (`version1.1.6`/`version1.1.6-test2`) -> MQTT -> Persistence -> Postgres/Timescale -> Grafana durchgaengig validiert; OSF-Dashboard zeigt Orders + Sensor-Daten stabil, DB-Ingestion waehrend Replay nachgewiesen (u. a. `mqtt_raw_message`, `sensor_snapshot`, `shopfloor_event` mit frischen Timestamps/Row-Zuwachs).
- [x] Vor-Ort-Abnahme bei ORBIS mit echter Sensor-Station + echten Sessions (2 AGVs) und Bewertung der Datenqualität für OEE/Optimierung/PM — durchgeführt (13.05.2026); Folgethema Datenpfad Live (`192.168.0.100`) vs. Replay (`localhost`) in Sprint 22 konkretisiert

### Integration & Tests (Übernahme aus Sprint 20)

- [ ] **UI-Test-Framework (Start in Sprint 21):** Grundgeruest in Sprint 21 abgeschlossen (Test-Tiering dokumentiert, Coverage-Standing etabliert, 2 Pilot-Tests umgesetzt); offen bleibt der Ausbau zur stabilen Abdeckung weiterer kritischer Flows (lokale Unit/Component-Tests vs. Replay-/Integrations-Abnahme) — Basis: [test-framework-replay-comparison-2026-03.md](../07-analysis/test-framework-replay-comparison-2026-03.md)
  - Coverage-Werte und Test-Fokus stehen zentral unter **Coverage Standing** (feste Position im Sprint-Dokument).
  - Test-Tiering verbindlich in [testing-strategy.md](../04-howto/testing/testing-strategy.md) ergänzt (Tier A: Unit/Component, Tier B: Replay/Integration-Abnahme).
  - 2 automatisierte Pilot-Tests umgesetzt (10.05.2026): `process-tab.component.spec.ts` (Order-Command-Pfad), `order-tab.component.spec.ts` (Correlation-Request-Pfad).
- [x] Sessions **2 AGVs** aufgenommen und als Replay-Input verifiziert (11.05.2026): `version1.1.6_20260511_134733.log`, `version1.1.6-test2_20260511_141131.log` — weitere Aufnahmen mit **Analyse**-Preset (DR-25) bei Bedarf.
  - Update 11.05.2026: Session-Logs mit 2 AGVs liegen vor (`version1.1.6_20260511_134733.log`, `version1.1.6-test2_20260511_141131.log`) und sind als Tier-B Replay-Input vorhanden; offen bleibt die strukturierte Einbindung als verbindlicher Test-Framework-Flow inkl. klarer Akzeptanzkriterien.
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): angehen sobald DSP wieder aktiv ist und der Correlation-Flow im gemeinsamen Testfenster ausgeloest werden kann; dann End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren.
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): angehen sobald MES aktiv ist und der Quality-Fail-/Ersatzauftragspfad im grossen Team reproduzierbar getriggert werden kann; dann E2E-Nachweis mit klarer Ereigniskette dokumentieren.

### Blog & Organisation (Übernahme aus Sprint 20)

- [ ] Blog: Reviews A1, A2, A3
- [ ] Azure DevOps: Repo/Boards von GitHub

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [x] **Versioning/Release:** Session-Manager-Tags sauber namespacen (z. B. `session-manager-v1.4.0`), damit keine Kollision mit OSF-Haupttags (`vX.Y.Z`) entsteht; Konvention in Release-Checkliste verankern (13.05.2026, in Sprint 22 uebernommen)
- [x] Sprint 21: Status Abgeschlossen, Datum (13.05.2026)
- [x] Sprint 22 anlegen, offene `[ ]` übernehmen (13.05.2026)
- [x] PROJECT_STATUS / Roadmap kurz (13.05.2026)

---

## Später (Backlog)

- Produkt WHITE „2× Bohren“ (MES/CCU/Kette)
- Customer **Netzsch** (`NETZSCH_CONFIG`)
- Arduino: optionales 7-Segment

---

## Links

- [Sprint 20](sprint_20.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [DR-25](../03-decision-records/25-session-log-topic-filters.md)

---

*Stand: 13.05.2026* · [sprints_README.md](sprints_README.md)

