# Sprint 21 – OCC Feedback & Stabilisierung (v1.1.x)

**Zeitraum:** 01.05.2026 – 15.05.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 20](./sprint_20.md)

**Kurz:** OCC-Feedback in konkrete UX-Verbesserungen übersetzen, offene Sprint-20 Punkte fertigstellen, Korrelation Shopfloor↔Sensoren absichern.

---

## Externe Termine

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **29–30.04.2026** | **ORBIS Customer-Connect (München)** | Feedback/Anforderungen für Verbesserungen |

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

- [ ] **Shopfloor Overlay (RPi):** Z-Index/Stacking robust (RPi == localhost), systematischer Vergleich falls Regression

### Backend & Grafana (Übernahme aus Sprint 20)

- [x] Architekturentscheidung + Leitplanken dokumentiert: **DSP-Edge als Zielplattform**, Deploy in Phase 1 variabel (**local-dev**, **rpi-pilot**, **edge-prod**), MQTT-Ingest read-only, generisches Sensor-Metrikmodell — DR-28 erstellt (08.05.2026)
- [x] Edge Persistence Stack lokal implementiert (Docker Compose, Postgres/Timescale, Grafana-Provisioning, Persistence-Service, Schema/Retention) — lokale Unit-Tests + Type-Checks grün (08.05.2026, `npm run test`, `npm run lint:types`)
- [x] Lokaler Replay-Smoke-Test erfolgreich (synthetische Arduino-Session): Parsing/Normalisierung verifiziert (`station_id`, `sensor_type`), Reason-Logik mit `EVENT`/`THRESHOLD`/`INTERVAL` nachgewiesen (08.05.2026, SQL-Checks in `sensor_snapshot`)
- [ ] Grafana lokal visuell verifizieren (Dashboards: Systemstatus, Aufträge, Workpiece Trace, Sensor Snapshots, Modul-/FTS-Zustände) inkl. kurzer Abnahme-Notiz — Technikpfad lokal verifiziert (08.05.2026): Datasource-Provisioning/Grafana-Auth/Debug-Dashboard (`osf-sensor-debug-live`) zeigen Daten stabil; Update 09.05.2026: Replay-Zeitmodus im Sender reaktiviert (Timeshift), `ccu/order/active`/`ccu/order/completed` End-to-End technisch nachgewiesen (Broker + Postgres), Orders-Dashboard um Active-/State-Panels erweitert; fachliches Feintuning/Abnahme weiterhin bewusst auf echte ORBIS-Daten + neue Session-Logs verschoben
- [ ] Vor-Ort-Abnahme bei ORBIS mit echter Sensor-Station + echten Sessions (2 AGVs) und Bewertung der Datenqualität für OEE/Optimierung/PM

### Integration & Tests (Übernahme aus Sprint 20)

- [ ] Sessions **2 AGVs**; weitere Aufnahmen mit **Analyse**-Preset (DR-25) bei Bedarf — Vorab lokal: synthetische Arduino-Replay-Session erstellt; echte Sensor-Station-Aufnahmen folgen vor Ort bei ORBIS
- [ ] **dsp/correlation/info** E2E
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail)

### Blog & Organisation (Übernahme aus Sprint 20)

- [ ] Blog: Reviews A1, A2, A3
- [ ] Azure DevOps: Repo/Boards von GitHub

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] Sprint 21: Status Abgeschlossen, Datum
- [ ] Sprint 22 anlegen, offene `[ ]` übernehmen
- [ ] PROJECT_STATUS / Roadmap kurz

---

## Später (Backlog)

- Produkt WHITE „2× Bohren“ (MES/CCU/Kette)
- Customer **Netzsch** (`NETZSCH_CONFIG`)
- Arduino: optionales 7-Segment
- UI-Test-Framework — [test-framework-replay-comparison-2026-03.md](../07-analysis/test-framework-replay-comparison-2026-03.md)

---

## Links

- [Sprint 20](sprint_20.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [DR-25](../03-decision-records/25-session-log-topic-filters.md)

---

*Stand: 09.05.2026* · [sprints_README.md](sprints_README.md)

