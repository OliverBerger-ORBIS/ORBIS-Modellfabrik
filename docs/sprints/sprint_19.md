# Sprint 19 – Sensor-Station, Backend/Grafana & Hannover-Vorbereitung

**Zeitraum:** 02.04.2026 – 15.04.2026 (2 Wochen) · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 18](./sprint_18.md)

**Kurz:** Sensor-Station (Hardware + OSF), Backend/Grafana, Blog; **Hannover** (Kamera, OBS, Konftel).

---

## Externe Termine

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **20–24.04.2026** | **Hannover Messe** | Vorbereitung in diesem Sprint |
| **~Ende 04.2026** | **ORBIS Customer-Connect** | Folge-Meilenstein → [PROJECT_STATUS.md](../PROJECT_STATUS.md) |

---

## Erledigt (Stand 09.04.2026)

- [x] **DSP / OSF-Story:** Default-Kunde OSF, **Sensor Station** in Animation, **MES/EWM**-URLs (Settings), Klick → Sensor-Tab bzw. extern; Route `dsp/customer/osf` — [dsp-osf-customer-integration-plan.md](../04-howto/dsp-osf-customer-integration-plan.md), Reference `sf-system-sensor`.
- [x] **Doku:** [dsp-svg-inventory.md](../02-architecture/dsp-svg-inventory.md) Verifikation osf-ui (09.04.2026).
- [x] **OSF v1.0.10:** Replay-Defaults **ORBIS** (`mqtt-user.defaults.ts` → Shopfloor-RPi); Arduino **ORBIS** per Default, optional `wifi_mode_local.h` (DAHEIM ohne Repo-Edit).
- [x] **Session Manager / DR-25:** Topic-Aufnahme-Preset (**„Analyse“** ohne Arduino / BME680 / Kamera / LDR) — nur **Schreibpfad**; persistiert in `session_recorder.recording.recording_exclusion_preset` — [DR-25](../03-decision-records/25-session-log-topic-filters.md), [session-recorder.md](../04-howto/helper_apps/session-manager/session-recorder.md).
- [x] **Session-Meta:** optionale **erste Zeile** `session_meta` in `.log` (Dauer, Broker, Preset, OSF-Workspace-Version, CCU/Order-Kurzinfo); Replay/Loader ignorieren sie; INVENTORY-Pflegehinweise + `scripts/check_session_inventory.py`.
- [x] **Session Recorder UX:** Sprung **⚙️ Einstellungen** aus dem Recorder-Tab (`main_sidebar_tab`); Meta-Felder während Aufnahme.

---

## Session Manager – geplanter Umbau (nach Priorität)

Fokus: schlanker **Replay + Session Recorder**; Randfunktionen entlasten oder entfernen.

- [ ] **Topic Recorder**-Tab **entfernen** (oder aus App auslagern — nur noch bei Bedarf)
- [ ] **Session-Analyse**-Tab **entfernen** (Analyse über OSF / externe Tools / Notebooks)
- [ ] **Logging** verschlanken (kein eigener Top-Level-Tab nötig): Level, Live-Log-Hinweis, ggf. **Pfad** in **⚙️ Einstellungen** bündeln
- [ ] **OSF:** optionale **Replay**-Funktionalität (z. B. näher an UI-Workflows) — **später** / Backlog, nicht Blocker für den Umbau

---

## Offen (nach Priorität)

### Hannover Messe

- [ ] Kamera: Halterung, Vogelperspektive, Tests OSF/OBS
- [ ] OBS-Szenen Hannover — [obs-video-presentation-setup.md](../04-howto/presentation/obs-video-presentation-setup.md)
- [ ] Shopfloor-Rotation vs. OBS/Konftel — Optionen kurz dokumentieren (gleicher How-to)
- [ ] Konftel-20: Remote/Szenen ohne Demo-Pipeline zu blockieren

### Arduino & Sensor-Station

- [ ] **24 V:** XL4005, Mini-Fit Tap, 2 A, 12 V Ampel + R4 — [sensor-station-24v-bom-wiring.md](../05-hardware/sensor-station-24v-bom-wiring.md)
- [ ] **Transportbox:** 25×15 Deckel, Seiten 28 cm, Winkel
- [ ] **Sensor-Tab:** UX/Demo (Rest; DSP-Anbindung liegt)
- [ ] **Schwellen:** MQTT/API + OSF (Config); DAHEIM/ORBIS ohne Flash (Sprint-18-Thema)

### Backend & Grafana

- [ ] RPi-Service: Persistenz (Prozess/Shopfloor/Umwelt), Grafana; Interface später DSP-DISC-tauglich (vgl. Sprint-18-Backlog)

### OSF-UI – SVG / Presentation

- [ ] SVG: Spalten/Lanes wie UC-00 auf relevante Diagramme — [osf-ui-svg-label-text-conventions.md](../04-howto/osf-ui-svg-label-text-conventions.md)
- [ ] **Back** bei per Link geöffneten Tabs
- [ ] Zentrale Skalierung UC/Shopfloor (Konzept)

### Integration & Tests

- [ ] Sessions **2 AGVs**; weitere Aufnahmen mit **Analyse**-Preset (DR-25) bei Bedarf
- [ ] **dsp/correlation/info** E2E
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail)

### Blog & Organisation

- [ ] Blog: Reviews A1, A2, A3
- [ ] Azure DevOps: Repo/Boards von GitHub

### Sprint-Abschluss

- [ ] Sprint 19 abschließen (Datum)
- [ ] Sprint 20 aus [sprint_template.md](./sprint_template.md); offene `[ ]` übernehmen
- [ ] PROJECT_STATUS / Roadmap kurz

---

## Später (Backlog)

- Produkt WHITE „2× Bohren“ (MES/CCU/Kette)
- Customer **Netzsch** (`NETZSCH_CONFIG`)
- Arduino: optionales 7-Segment
- **OSF:** Replay näher an Produkt-Workflows (optional, nach Session-Manager-Umbau)
- UI-Test-Framework — [test-framework-replay-comparison-2026-03.md](../07-analysis/test-framework-replay-comparison-2026-03.md)
- Mixed-Session zwei AGVs: Einordnung (Analyse)

---

## Links

- [DR-25](../03-decision-records/25-session-log-topic-filters.md) · [Arduino Multi-Sensor](../05-hardware/arduino-r4-multisensor.md) · [Use-Case-Bibliothek](../02-architecture/use-case-library.md)

---

*Stand: 09.04.2026* · [sprints_README.md](sprints_README.md)
