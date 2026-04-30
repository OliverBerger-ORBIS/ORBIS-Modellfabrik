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

- [ ] **Functional View (Default OCC):** Business-Process Lane Reihenfolge anpassen: **ERP → MES → EWM → CRM → Analytical → Data-Lake** (CRM ersetzt Planning)
- [ ] **Functional View (Default OCC):** neuen Customer „OCC“ / Default-Konfiguration anlegen (neue Lane-Reihenfolge + Links/Defaults)
- [ ] **Functional View Animation:** 7 Functional DSP Icons wieder einzeln einbauen (LogiMAT-ähnliche Variante als Default für OCC)
- [ ] **Functional View Animation:** Interoperability SVG/Icon in Animation deutlich größer darstellen; ggf. zentral positionieren und DSP-Edge-Icon überdecken
- [ ] **Use-Case „Anomaly Detection“:** CRM Integration (Vibration löst Alarm aus → DSP-Edge sendet an MS-CRM → CRM „Prozess gestartet“/Techniker-Einsatz)
- [ ] **Process-Tab:** beim Wechsel in den Tab automatisch Refresh ausführen (Inventory/Lagerinfo ohne Button-Drücken)
- [ ] **Process → Order:** nach Auslösen einer Order (`ccu/order/request`) per Klick im Bereich „Kundenaufträge“ in den Order-Tab springen (Produkt Blue/White/Red)
- [ ] **Order → Shopfloor:** aus dem Order-Tab per Klick in den Shopfloor-Tab wechseln
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

*Stand: 30.04.2026* · [sprints_README.md](sprints_README.md)

