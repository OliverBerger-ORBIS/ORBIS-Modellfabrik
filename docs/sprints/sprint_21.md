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
- [x] **Use-Case „Anomaly Detection“:** CRM Integration (Vibration löst Alarm aus → DSP-Edge sendet an MS-CRM → CRM „Prozess gestartet“/Techniker-Einsatz) — als neuer UC-07 vorbereitet (Concept + Live-Demo-Button), UC-05 auf datenbasierte Predictive-Maintenance-Story ohne Anomaly-Fokus geschärft; Sensorik-Darstellung: UC-05 = Sensor-Station, UC-07 = Vibration + Tilt (05.05.2026, `npx nx test osf-ui --testPathPattern='predictive-maintenance|anomaly-detection|dsp-use-cases'`)
- [x] **Process-Tab:** beim Wechsel in den Tab automatisch Refresh ausführen (Inventory/Lagerinfo ohne Button-Drücken) — `ProcessTabComponent.ngOnInit` ruft `refreshProcessData()` auf (05.05.2026, `nx test osf-ui --testPathPattern=process-tab.component.spec`)
- [x] **Process → Order:** nach Auslösen einer Order (`ccu/order/request`) **ohne** Tab-Wechsel (mehrere Aufträge möglich); Sprung in den Order-Tab nur per Klick auf eine **Production-Flow-Produktkarte** (Blue/White/Red) rechts → `openOrderTabFromProductionFlow` / `/:locale/order?product=…` (05.05.2026, Unit-Tests `openOrderTab`, `openOrderTabFromProductionFlow`)
- [x] **Order → Shopfloor:** aus dem Order-Tab in den Shopfloor-Tab — **Modul** auf der eingebetteten Shopfloor-Vorschau in der Order-Card anklicken → `/:locale/shopfloor?module=…` (z. B. HBW), Fokus wie Shopfloor-Tab `selectModuleByType` (05.05.2026, `order-card.component.spec`)
- [ ] **UX/Navigation (Analyse):** Entscheidungsgrundlage: `BackButtonComponent` in den **Haupt-Tabs** (z. B. Process/Order/Shopfloor nach Deep-Link-Flows) einbauen **oder** bewusst nur **Sidebar-Navigation** + **Browser-Zurück**; Status quo: Use-Case-Seiten haben `app-back-button`, die Tab-Routen nicht — Empfehlung dokumentieren, danach ggf. umsetzen
- [ ] **Track & Trace Use-Case:** Umwelt-/Sensor-Daten eventbasiert „samplen“/speichern (Snapshots zu Shopfloor-Events: HBW Pick/Drop, DPS Pick/Drop, DRILL/MILL/AIQS Prozessschritte)
- [ ] **Analyse/Fix:** Track&Trace Live zeigt AIQS-Event-Sequenzen doppelt (Start+Ende) → Root cause + Fix (z. B. Produkt Blau: AIQS, DRILL, MILL, AIQS)
- [ ] **Track&Trace Business-Kontext:** geplante Stationskette kurz anzeigen (z. B. Lagerauftrag: DPS→HBW; Produktion Blau: HBW→DRILL→MILL→AIQS→DPS)

### Hannover Messe / Presentation (Übernahme aus Sprint 20)

- [ ] OBS-Szenen Hannover finalisieren — [obs-video-presentation-setup.md](../04-howto/presentation/obs-video-presentation-setup.md)
- [ ] Konftel-20: Remote/Szenen ohne Demo-Pipeline zu blockieren
- [ ] Shopfloor-Rotation: finaler Ablauf (Kamera-Quelle + OSF-UI Settings) als kurze Checkliste in How-to dokumentieren

### OSF-UI – Bugs / UX (Übernahme aus Sprint 20)

- [ ] **Shopfloor Overlay (RPi):** Z-Index/Stacking robust (RPi == localhost), systematischer Vergleich falls Regression

### Backend & Grafana (Übernahme aus Sprint 20)

- [ ] RPi-Service: Persistenz (Prozess/Shopfloor/Umwelt), Grafana; Interface später DSP-DISC-tauglich

### Integration & Tests (Übernahme aus Sprint 20)

- [ ] Sessions **2 AGVs**; weitere Aufnahmen mit **Analyse**-Preset (DR-25) bei Bedarf
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

*Stand: 05.05.2026* · [sprints_README.md](sprints_README.md)

