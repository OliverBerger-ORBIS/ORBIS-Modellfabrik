# Sprint 22 – ORBIS Feldbetrieb & Datenpfad-Stabilisierung

**Zeitraum:** 15.05.2026 – 28.05.2026 · **Status:** Abgeschlossen · **Vorheriger Sprint:** [Sprint 21](./sprint_21.md)

**Kurz:** Feldbetrieb bei ORBIS stabilisieren (Live vs. Replay Datenpfade), offene Integrations-/Testpunkte aus Sprint 21 abschliessen und Demo-Readiness fuer den Kundentermin absichern.

**Retrospektive:** Der Sprint wurde operativ durch dringende 3D-Druck-/SLS-Aufgaben fuer die Sensor-Station ueberlagert; dadurch wurden Hardware-Deliverables priorisiert und Integrations-/Testthemen teilweise in Sprint 23 verschoben.

---

## Externe Termine

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| **21.05.2026** | **Spontan-Praesentation OSF** (IT-Leiter von Hörmann USA, Name folgt) mit Richard Reiss als ORBIS-Kundenbetreuer | Kurzfristige Demo-/Argumentationsfaehigkeit gegenueber IT-Entscheidern validieren und Feedback fuer Priorisierung aufnehmen |
| **22.05.2026** | **Kunde Hager – OSF Praesentation bei ORBIS** | Demo-Readiness, Daten-/Ablaufstabilitaet unter Live-Bedingungen verifizieren |
| **26.05.2026** | **ORBIS France – Video für Messe** | Erstellen eines Videos zur Demo von OSF/DSP/MES ohne Modellfabrik; zum Abspielen als Dauerschleife |

---

## Coverage Standing

| Stand | Datum | Branches | Functions | Lines | Statements | Gates (B/F/L/S) | Gate-Margin (B/F/L/S) |
|--------|--------|----------|-----------|-------|------------|------------------|------------------------|
| Sprint-Start (Baseline aus Sprint-21-Endmessung) | 13.05.2026 | 39.44% | 49.80% | 49.18% | 48.36% | 30 / 42 / 47 / 46 | +9.44 / +7.80 / +2.18 / +2.36 pp |
| Aktuell | 13.05.2026 | 39.44% | 49.80% | 49.18% | 48.36% | 30 / 42 / 47 / 46 | +9.44 / +7.80 / +2.18 / +2.36 pp |

- **Messmethode (konstant):** `NODE_OPTIONS="--max-old-space-size=4096" BASELINE_BROWSER_MAPPING_IGNORE_OLD_DATA=true npx jest --config "osf/apps/osf-ui/jest.config.ts" --runInBand --coverage --coverageDirectory ".tmp-coverage-osf-ui" --coverageReporters=json-summary --coverageThreshold='{}'` (Quelle: `osf/apps/osf-ui/.tmp-coverage-osf-ui/coverage-summary.json`, Feld `total`)
- **Top-3 Gaps (Test-Fokus):**
  1. `osf/apps/osf-ui/src/app/tabs/shopfloor-tab.component.ts` — 42.63% Lines, 666 uncovered
  2. `osf/apps/osf-ui/src/app/tabs/agv-tab.component.ts` — 54.07% Lines, 389 uncovered
  3. `osf/apps/osf-ui/src/app/components/dsp-animation/dsp-animation.component.ts` — 41.21% Lines, 318 uncovered

---

## Aufgaben (thematisch, mit Haken)

### ORBIS Feldbetrieb / Grafana Datenpfad

- [ ] Datenpfad-Regel verbindlich dokumentieren und testen: ORBIS Live -> Broker `192.168.0.100`, Replay -> Broker `localhost`; Abweichungen als Troubleshooting-Checkliste erfassen.
- [ ] Lokalen Dashboard-Fall "keine orders" reproduzieren und Ursache dokumentieren (Ingest/Replay/Broker-Mapping/DB-Stand).
- [ ] Unterschiede localhost vs. RPi systematisch abarbeiten (insb. AGV-Erkennung/Anzeige auf RPi als Voraussetzung vor Overlay-Checks).

### Integration & Tests (Uebernahme aus Sprint 21)

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen.
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren.
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren.

### Backend & Deployment

- [ ] Grafana-Dashboards ausbauen (fachliche Panels schaerfen, offene Visualisierungs-/Abnahmepunkte systematisch schliessen).
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffaehig machen (neben local-dev als naechster Zielpfad).
- [ ] Session-Manager-Tags sauber namespacen (z. B. `session-manager-vX.Y.Z`) und Konvention in Release-Checkliste verankern.

### Sensor-Station / Mechanik & 3D-Druck

- [ ] Sensor-Station-Layout fuer Transport und Betrieb finalisieren: Sensoren, Ampel, Stromversorgung, Arduino und Breadboard auf einer 15x25 cm Acryl-Grundplatte so positionieren und befestigen, dass alles in die Acryl-Transportbox (gleiche Grundflaeche, 28 cm Hoehe) passt; Betriebskonzept festhalten (Transport: Box ueber Grundplatte stuelpen, Betrieb: Grundplatte auf umgedrehter Box als Sockel, 28 cm ueber Shopfloor-Niveau).
- [x] 3D-Druck-Umgebung aufgesetzt: Bambu P2S installiert/in Betrieb; OpenSCAD als CAD/Modellierungsplattform im Einsatz.
- [x] Fusion 360 fuer Druckvorlagen (STL-Workflow) aufgesetzt und fuer Halterungsdesigns eingesetzt.
- [x] Molex-Halter Prototyp gedruckt und auf 4-PIN-Stecker umgestellt (kleineres Bauformat).
- [ ] Halterung fuer 24V->12V DC/DC-Wandler inkl. Wago-Klemmen und 2A-Sicherung drucken und fit-checken.
- [ ] Halterung fuer 12V-DC-Rundbuchse (Barrel Jack) drucken und fit-checken.
- [x] Gehaeuse/Halterung fuer GL.iNet Router AX3000 WiFi 6 (Modell GL-MT3000) mit Fusion 360 konstruiert und umgesetzt.
- [ ] Dokumentation ergaenzen: bestehende Verdrahtung als bereits getestet referenzieren; Fokus auf mechanischem Aufbau, Druckteilen, Befestigungspunkten und Montageablauf.

### Track&Trace / APS

- [ ] APS-Erweiterung: neue NFC-IDs generierbar machen, damit Track&Trace nicht dauerhaft auf denselben NFCs basiert.

### Blog & Organisation

- [ ] Blog: Reviews A1, A2, A3
- [ ] Azure DevOps: Repo/Boards von GitHub

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [x] Sprint 22: Status Abgeschlossen, Datum
- [x] Sprint 23 anlegen, offene `[ ]` übernehmen
- [ ] PROJECT_STATUS / Roadmap kurz

---

## Später (Backlog)

- Produkt WHITE "2x Bohren" (MES/CCU/Kette)
- Customer **Netzsch** (`NETZSCH_CONFIG`)
- Arduino: optionales 7-Segment

---

## Links

- [Sprint 21](sprint_21.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [DR-25](../03-decision-records/25-session-log-topic-filters.md)

---

*Stand: 05.06.2026* · [sprints_README.md](sprints_README.md)
