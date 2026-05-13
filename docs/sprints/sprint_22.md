# Sprint 22 – ORBIS Feldbetrieb & Datenpfad-Stabilisierung

**Zeitraum:** 16.05.2026 – 29.05.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 21](./sprint_21.md)

**Kurz:** Feldbetrieb bei ORBIS stabilisieren (Live vs. Replay Datenpfade), offene Integrations-/Testpunkte aus Sprint 21 abschliessen und Demo-Readiness fuer den Kundentermin absichern.

---

## Externe Termine

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| **22.05.2026** | **Kunde Hager – OSF Praesentation bei ORBIS** | Demo-Readiness, Daten-/Ablaufstabilitaet unter Live-Bedingungen verifizieren |

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

### Track&Trace / APS

- [ ] APS-Erweiterung: neue NFC-IDs generierbar machen, damit Track&Trace nicht dauerhaft auf denselben NFCs basiert.

### Blog & Organisation

- [ ] Blog: Reviews A1, A2, A3
- [ ] Azure DevOps: Repo/Boards von GitHub

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] Sprint 22: Status Abgeschlossen, Datum
- [ ] Sprint 23 anlegen, offene `[ ]` übernehmen
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

*Stand: 13.05.2026* · [sprints_README.md](sprints_README.md)
