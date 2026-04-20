# Sprint 20 – Hannover Messe & Customer Connect (v1.1.x)

**Zeitraum:** 16.04.2026 – 30.04.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 19](./sprint_19.md)

**Kurz:** Hannover Messe (Kamera/OBS/Konftel, Rotation, Präsentations-Stabilität) + Customer Connect München. Fokus: OSF-UI Demo-Readiness, Sensor-Station UX, Bugs (Refresh/Scrollbars/State), Release-Ziel **v1.1.x**.

---

## Externe Termine

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **20–24.04.2026** | **Hannover Messe** | Live-Demo / Präsentations-Setup |
| **29–30.04.2026** | **ORBIS Customer-Connect (München)** | Folge-Meilenstein / Stakeholder |

---

## Aufgaben (thematisch, mit Haken)

### Hannover Messe / Presentation

- [x] **Hannover-Messe Präsentationstest** (16.04.2026) erfolgreich (Kamera + OSF-UI).
- [ ] OBS-Szenen Hannover finalisieren — [obs-video-presentation-setup.md](../04-howto/presentation/obs-video-presentation-setup.md)
- [ ] Konftel-20: Remote/Szenen ohne Demo-Pipeline zu blockieren
- [ ] Shopfloor-Rotation: finaler Ablauf (Kamera-Quelle + OSF-UI Settings) als kurze Checkliste in How-to dokumentieren

### OSF-UI – DSP Architecture & Links

- [x] **Business-Layer Box „Bp-Planning“** zwischen ERP Apps und MES Apps (ORBIS Branding, Planungs-Icon, klickbar)
- [x] **Settings:** URL-Konfiguration für Bp-Planning Link (Pattern wie MES/EWM)
- [x] **Animation-Variante:** Hannover-Messe-Animation vs. LogiMAT-Variante sauber als benannte Variante (Entscheidung + Umsetzung)

### OSF-UI – Bugs / UX

- [x] **Process/Order Refresh:** Refresh aktualisiert Stock/Bestände sichtbar ohne Locale-Wechsel (Root cause + Fix)
- [x] **DSP Architecture Scrollbars:** keine Scrollbars bei ausreichend Platz; kein „grauer Leerraum“ (2026-04-19: visuell verifiziert)
- [x] **Use-Case Diagramme Scrollbars:** Fix generisch (DSP-Muster: skalierte px-Größe am Diagramm, kein `transform: scale`; Wrapper `overflow:auto`, volle Breite; SVG ohne erzwungenes `min-width`) — 2026-04-19: verifiziert, Zoom-Verhalten vs. DSP bewusst akzeptiert
- [x] **DSP Akkordeon State:** Kontext beim Zurücknavigieren erhalten (Section + optional Scrollpos) — 2026-04-19: `sessionStorage` + `?section=` + `NavigationBackService` vor `history.back`; Scroll zu `#dsp-accordion-*`
- [ ] **Shopfloor Overlay (RPi):** Z-Index/Stacking robust (RPi == localhost), systematischer Vergleich falls Regression

### Arduino & Sensor-Station

- [ ] **Sensor-Tab:** UX/Demo (Rest; DSP-Anbindung liegt)
- [ ] **Schwellenwerte:** Configuration-Tab → MQTT/API → Arduino wirksam (E2E, Payload, Subscribe/Parse, optional ACK)

### Backend & Grafana

- [ ] RPi-Service: Persistenz (Prozess/Shopfloor/Umwelt), Grafana; Interface später DSP-DISC-tauglich

### Integration & Tests

- [ ] Sessions **2 AGVs**; weitere Aufnahmen mit **Analyse**-Preset (DR-25) bei Bedarf
- [ ] **dsp/correlation/info** E2E
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail)

### Blog & Organisation

- [ ] Blog: Reviews A1, A2, A3
- [ ] Azure DevOps: Repo/Boards von GitHub

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] Sprint 20: Status Abgeschlossen, Datum
- [ ] Sprint 21 anlegen, offene `[ ]` übernehmen
- [ ] PROJECT_STATUS / Roadmap kurz

---

## Später (Backlog)

- Produkt WHITE „2× Bohren“ (MES/CCU/Kette)
- Customer **Netzsch** (`NETZSCH_CONFIG`)
- Arduino: optionales 7-Segment
- UI-Test-Framework — [test-framework-replay-comparison-2026-03.md](../07-analysis/test-framework-replay-comparison-2026-03.md)

---

## Links

- [Sprint 19](sprint_19.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [DR-25](../03-decision-records/25-session-log-topic-filters.md)

---

*Stand: 17.04.2026* · [sprints_README.md](sprints_README.md)
