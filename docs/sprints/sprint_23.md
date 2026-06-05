# Sprint 23 – Urlaubssprint & Hardware-Fokus

**Zeitraum:** 29.05.2026 – 11.06.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 22](./sprint_22.md)

**Kurz:** Urlaubssprint mit bewusst reduzierter Umsetzung; Fokus auf pragmatische Hardware-Fortschritte (3D-Druck, Mounting) und Fortsetzung offener Integrationspunkte aus Sprint 22.

**Rahmenbedingung:** Urlaub vom 04.06.2026 bis 12.06.2026. Sprint wird normal geplant, mit erwartbar geringerer Umsetzungsquote.

---

## Externe Termine

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| **01.06.2026** | **Praesentation OSF fuer ORBIS-Amerika-Mitarbeiter** (Christen, Adjud) | Internationales Stakeholder-Feedback zur OSF-Darstellung und Priorisierung der naechsten Schritte |

---

## Aufgaben (thematisch, mit Haken)

### ORBIS Feldbetrieb / Integrations-Fortsetzung (Carry-over aus Sprint 22)

- [ ] Datenpfad-Regel verbindlich dokumentieren und testen: ORBIS Live -> Broker `192.168.0.100`, Replay -> Broker `localhost`; Abweichungen als Troubleshooting-Checkliste erfassen.
- [ ] Lokalen Dashboard-Fall "keine orders" reproduzieren und Ursache dokumentieren (Ingest/Replay/Broker-Mapping/DB-Stand).
- [ ] Unterschiede localhost vs. RPi systematisch abarbeiten (insb. AGV-Erkennung/Anzeige auf RPi als Voraussetzung vor Overlay-Checks).

### Integration & Tests (Carry-over aus Sprint 22)

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen.
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren.
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren.

### Backend & Deployment (Carry-over aus Sprint 22)

- [ ] Grafana-Dashboards ausbauen (fachliche Panels schaerfen, offene Visualisierungs-/Abnahmepunkte systematisch schliessen).
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffaehig machen (neben local-dev als naechster Zielpfad).
- [ ] Session-Manager-Tags sauber namespacen (z. B. `session-manager-vX.Y.Z`) und Konvention in Release-Checkliste verankern.

### Sensor-Station / 3D-Druck & Mounting

- [ ] Sensor-Station-Layout fuer Transport und Betrieb finalisieren: Sensoren, Ampel, Stromversorgung, Arduino und Breadboard auf einer 15x25 cm Acryl-Grundplatte so positionieren und befestigen, dass alles in die Acryl-Transportbox (gleiche Grundflaeche, 28 cm Hoehe) passt; Betriebskonzept festhalten (Transport: Box ueber Grundplatte stuelpen, Betrieb: Grundplatte auf umgedrehter Box als Sockel, 28 cm ueber Shopfloor-Niveau).
- [x] Prototyp fuer 24V->12V DC/DC-Wandler-Halterung inkl. Sicherung und Wago-Klemmen in OpenSCAD designt.
- [ ] Halterung fuer 24V->12V DC/DC-Wandler inkl. Wago-Klemmen und 2A-Sicherung drucken und fit-checken.
- [x] `gwn6072m-mount` als neuer Router-Mount: Prototyp erstellt und gedruckt.
- [ ] Zielposition fuer `gwn6072m-mount` final entscheiden und verifizieren: ORBIS-Platte oder Platte der Charging-Station.
- [ ] Halterung fuer 12V-DC-Rundbuchse (Barrel Jack) drucken und fit-checken.
- [ ] Dokumentation ergaenzen: mechanischer Aufbau, Druckteile, Befestigungspunkte und Montageablauf.

### Track&Trace / APS (Carry-over aus Sprint 22)

- [ ] APS-Erweiterung: neue NFC-IDs generierbar machen, damit Track&Trace nicht dauerhaft auf denselben NFCs basiert.

### Blog & Organisation (Carry-over aus Sprint 22)

- [ ] Blog: Reviews A1, A2, A3
- [ ] Azure DevOps: Repo/Boards von GitHub

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] Sprint 23: Status Abgeschlossen, Datum
- [ ] Sprint 24 anlegen, offene `[ ]` uebernehmen
- [ ] PROJECT_STATUS / Roadmap kurz

---

## Später (Backlog)

- Router-Variante / Mounting-Strategie fuer Folgehardware konsolidieren (Stabilitaet, Servicezugang, Kabelfuehrung).

---

## Links

- [Sprint 22](sprint_22.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md)

---

*Stand: 05.06.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
