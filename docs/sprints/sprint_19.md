# Sprint 19 – Sensor-Station, Backend/Grafana & Hannover-Vorbereitung

**Zeitraum:** 02.04.2026 – 15.04.2026 (2 Wochen) · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 18](./sprint_18.md)

**Kurz:** Sensor-Station (Hardware + OSF), Backend/Grafana, Blog; **Hannover** (Kamera, OBS, Konftel).

**Fortsetzung ab 13.04.2026:** Abarbeitung war **10.04.–Wochenende** durch **Netzsch-Präsentation** (Video) und Wochenende unterbrochen — offene Punkte siehe unten (**Offen**, **RPi-Bugs**, **Session-Manager-Umbau**).

### Arbeitskontext DAHEIM (Testeinschränkungen)

- **Umsetzbar ohne Fabrik:** z. B. Code, Doku, **I18n**, Teile des **Session-Manager**-Umbaus, UI-Refactors, Unit-Tests, Builds — alles, was **keinen** Live-MQTT/Shopfloor und **keinen** Zugriff auf den **RPi** braucht.
- **Nicht verifizierbar von DAHEIM:** **OSF Live-Modus** (Broker/Shopfloor **192.168.0.100**, FTS/Module) — ohne Anwesenheit in der Fabrik oder gleichwertigen Remote-Zugang.
- **RPi / v1.0.10:** Beobachtete **Shopfloor-Bugs** (AGV, Track & Trace, Locale, …) können **erst vor Ort** oder mit Zugriff auf die **deployte** Instanz **gegengetestet** werden; Fixes können vorbereitet werden, **Abnahme** bleibt offen.

---

## Externe Termine

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **20–24.04.2026** | **Hannover Messe** | Vorbereitung in diesem Sprint |
| **~Ende 04.2026** | **ORBIS Customer-Connect** | Folge-Meilenstein → [PROJECT_STATUS.md](../PROJECT_STATUS.md) |
| **10.04.2026** | **OSF-Präsentation (Video)** für Kunden **Netzsch** | Externe Demo, Remote |

---

## Präsentation / Demo-Setup (Netzsch & Messe)

- **OBS** ist für die **Kamera-Präsentation** derzeit **fragil** (Szenen, Fensterwechsel, Stabilität). OBS wird genutzt, weil **Window Capture** (gesamtes Anwendungsfenster) möglich ist und die OSF-Oberfläche so zusammenhängend gezeigt werden kann.
- **Empfehlung parallel / Messe:** **Windows-Desktop** + **PowerToys FancyZones** für feste **Bildschirmeinteilung** — weniger abhängig von OBS-Layouts; für **Hannover** vormerken. Insbesondere **Hero+2** (großes Fenster + zwei Seitenbereiche) lässt sich damit **zuverlässig** darstellen.
- How-to weiter: [obs-video-presentation-setup.md](../04-howto/presentation/obs-video-presentation-setup.md)

---

## Erledigt (Stand 13.04.2026)

- [x] **DSP / OSF-Story:** Default-Kunde OSF, **Sensor Station** in Animation, **MES/EWM**-URLs (Settings), Klick → Sensor-Tab bzw. extern; Route `dsp/customer/osf` — [dsp-osf-customer-integration-plan.md](../04-howto/dsp-osf-customer-integration-plan.md), Reference `sf-system-sensor`.
- [x] **Doku:** [dsp-svg-inventory.md](../02-architecture/dsp-svg-inventory.md) Verifikation osf-ui (09.04.2026).
- [x] **OSF v1.0.10:** Replay-Defaults **ORBIS** (`mqtt-user.defaults.ts` → Shopfloor-RPi); Arduino **ORBIS** per Default, optional `wifi_mode_local.h` (DAHEIM ohne Repo-Edit).
- [x] **Session Manager / DR-25:** Topic-Aufnahme-Preset (**„Analyse“** ohne Arduino / BME680 / Kamera / LDR) — nur **Schreibpfad**; persistiert in `session_recorder.recording.recording_exclusion_preset` — [DR-25](../03-decision-records/25-session-log-topic-filters.md), [session-recorder.md](../04-howto/helper_apps/session-manager/session-recorder.md).
- [x] **Session-Meta:** optionale **erste Zeile** `session_meta` in `.log` (Dauer, Broker, Preset, OSF-Workspace-Version, CCU/Order-Kurzinfo); Replay/Loader ignorieren sie; INVENTORY-Pflegehinweise + `scripts/check_session_inventory.py`.
- [x] **Session Recorder UX:** Sprung **⚙️ Einstellungen** aus dem Recorder-Tab (`main_sidebar_tab`); Meta-Felder während Aufnahme.
- [x] **10.04.2026:** Externe **OSF-Präsentation per Video** für Kunden **Netzsch** (Remote). Setup-Hinweise: Abschnitt **Präsentation / Demo-Setup** oben.
- [x] **OSF-UI / I18n:** Production-Build `nx run osf-ui:build:production` (Locales EN/DE/FR) **ohne** „No translation found for …“ — `messages.de.json` / `messages.fr.json` decken die IDs; Verifikation 2026-04-13.
- [x] **Session Manager v1.3.0:** Nur noch Sidebar-Tabs **Replay Station**, **Session Recorder**, **Einstellungen**; Logging in Einstellungen gebündelt (siehe Abschnitt „Session Manager – geplanter Umbau“).
- [x] **OSF-UI / External Links:** Repo-managed Config `osf/apps/osf-ui/public/assets/config/external-links.json` (kein localStorage Override); Settings-Tab bietet JSON-Export für manuelles Übernehmen ins Repo; Verifikation 2026-04-13: `nx test osf-ui`.

---

## OSF-UI v1.0.10 (RPi-Deploy) – beobachtete Bugs / Anomalien

*Stand Shopfloor nach Deploy; zur Nachverfolgung im Sprint / Backlog.*

- [ ] **Zweites AGV (Shopfloor):** Ein **altes** zweites AGV ist in der UI noch **sichtbar** und **registriert**, bleibt aber **dauerhaft unconnected** (Hardware existiert so nicht). Das **neue** zweite AGV wird **nicht** angezeigt — UI/Registrierung bereinigen bzw. an aktuelle FTS-IDs anbinden.
- [ ] **Track & Trace – Live-Daten:** Es wirkt so, als würden **mehr Events pro NFC-Tag** angezeigt werden, als **tatsächlich per MQTT** eingegangen sind (Verdacht: **Fixtures**, gecachte Streams, oder andere Quellen — Klärung/Deduplizierung).
- [x] **Settings – externe Links (MES, EWM, …):** Repo-managed Config (Deploy-Single-Source) statt **localStorage**; gleiche Links auf localhost und RPi nach Deploy.
- [ ] **Sprache / Language-Switch:** Vermutung: **Locale-Wechsel** löst **Reconnect** oder Neuinitialisierung von Streams aus — danach sind **Track & Trace**-Daten (und ggf. andere Tab-Daten) **nicht mehr sichtbar**, bis Reload/Neuverbindung. Reproduktion und Tab-Stream-Pattern prüfen ([DR-11 Tab-Stream](../03-decision-records/11-tab-stream-initialization-pattern.md)).

---

## Session Manager – geplanter Umbau (nach Priorität)

Fokus: schlanker **Replay + Session Recorder**; Randfunktionen entlasten oder entfernen.

- [x] **Topic Recorder**-Tab **entfernen** — UI-Tab weg; Modul `topic_recorder.py` bleibt im Repo für ggf. spätere Nutzung.
- [x] **Session-Analyse**-Tab **entfernen** — UI-Tab weg; Analyse über OSF / externe Tools; Modul `session_analysis.py` bleibt optional.
- [x] **Logging** verschlanken: Level, JSONL-Pfad, Live-Ring-Buffer und optionale Diagnose unter **⚙️ Einstellungen → Tab „Logging & Diagnose“** (Session Manager **v1.3.0**).
- [ ] **OSF:** optionale **Replay**-Funktionalität (z. B. näher an UI-Workflows) — **später** / Backlog, nicht Blocker für den Umbau

---

## Offen (nach Priorität)

### Hannover Messe

- [ ] Kamera: Halterung, Vogelperspektive, Tests OSF/OBS
- [ ] **Layout:** Windows + **FancyZones** für Messe-Setup (vgl. **Präsentation / Demo-Setup** — Hero+2)
- [ ] OBS-Szenen Hannover — [obs-video-presentation-setup.md](../04-howto/presentation/obs-video-presentation-setup.md) (OBS bleibt fragil; Alternative siehe oben)
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

*Stand: 13.04.2026* · [sprints_README.md](sprints_README.md)
