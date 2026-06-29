# Sprint 25 – LOM-Day Nachbereitung & Praesentationstechnik

**Zeitraum:** 26.06.2026 – 09.07.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 24](./sprint_24.md)

**Kurz:** Nachbereitung des LOM-Day, Stabilisierung der Praesentationstechnik (Desktop-/Fancy-Zones-Workflow) und Fortsetzung offener Integrationspunkte aus Sprint 24.

---

## Externe Termine

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| **26.06.2026** | **LOM-Day: Vorstellung der OSF** | Inhaltlich erfolgreiche OSF-Praesentation; klare Folgeaufgaben zu MES/SAP-Latenz und Praesentationstechnik abgeleitet |

---

## Aufgaben (thematisch, mit Haken)

### LOM-Day Nachbereitung / Lessons Learned

- [x] LOM-Day Ergebnis dokumentiert (26.06.2026): OSF-Praesentation inhaltlich erfolgreich.
- [ ] MES/SAP-Latenzzeiten aus dem LOM-Day technisch nachanalysieren und fuer Demo-Betrieb priorisierte Gegenmassnahmen festlegen.
- [ ] Praesentationstechnik aus LOM-Day aufarbeiten: Ursachenanalyse fuer unbefriedigende Beamer-Darstellung dokumentieren.

### Praesentationstechnik (neu)

- [ ] Handlungsanweisung erstellen: Setup A (Sharing Laptop-Monitor unter Windows) fuer Praesentationen.
- [ ] Handlungsanweisung erstellen: Setup B (Sharing zweiter Monitor) fuer Praesentationen.
- [ ] Desktop-Szenenmodell verbindlich beschreiben und testen: Desktop 1 (Vorbereitung, nie sharen), Desktop 2 (Fullscreen), Desktop 3 (Hero+2).
- [ ] Checkliste fuer Aufbau/Vorbereitung vor Kundenpraesentationen erstellen und gegen zwei Testdurchlaeufe verifizieren.
- [ ] Praesentationsvideo V1 reviewen und entscheiden: OBS-Ansatz beibehalten oder Umstellung auf Teams-Monitor + Fancy-Zones/Desktops.

### ORBIS Feldbetrieb / Integrations-Fortsetzung (Carry-over aus Sprint 24)

- [ ] Datenpfad-Regel verbindlich dokumentieren und testen: ORBIS Live -> Broker `192.168.0.100`, Replay -> Broker `localhost`; Abweichungen als Troubleshooting-Checkliste erfassen.
- [ ] Lokalen Dashboard-Fall "keine orders" reproduzieren und Ursache dokumentieren (Ingest/Replay/Broker-Mapping/DB-Stand).
- [ ] Unterschiede localhost vs. RPi systematisch abarbeiten (insb. AGV-Erkennung/Anzeige auf RPi als Voraussetzung vor Overlay-Checks).

### Integration & Tests (Carry-over aus Sprint 24)

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen.
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren.
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren.

### Backend & Deployment (Carry-over aus Sprint 24)

- [ ] Grafana-Dashboards ausbauen (fachliche Panels schaerfen, offene Visualisierungs-/Abnahmepunkte systematisch schliessen).
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffaehig machen (neben local-dev als naechster Zielpfad).
- [x] Session-Manager-Tags sauber namespacen (z. B. `session-manager-vX.Y.Z`) und Konvention in Release-Checkliste verankern.

### Sensor-Station / 3D-Druck & Mounting (Carry-over aus Sprint 24)

- [ ] Zielposition fuer `gwn6072m-mount` final entscheiden und verifizieren: ORBIS-Platte oder Platte der Charging-Station.

### Track&Trace / APS (Carry-over aus Sprint 24)

- [ ] APS-Erweiterung: neue NFC-IDs generierbar machen, damit Track&Trace nicht dauerhaft auf denselben NFCs basiert.

### Blog & Organisation (Carry-over aus Sprint 24)

- [ ] Blog: Reviews A1, A2, A3
- [ ] Azure DevOps: Repo/Boards von GitHub

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] Sprint 25: Status Abgeschlossen, Datum
- [ ] Sprint 26 anlegen, offene `[ ]` uebernehmen
- [ ] PROJECT_STATUS / Roadmap kurz

---

## Später (Backlog)

- Router-Variante / Mounting-Strategie fuer Folgehardware konsolidieren (Stabilitaet, Servicezugang, Kabelfuehrung).

---

## Links

- [Sprint 24](sprint_24.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md)

---

*Stand: 29.06.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
