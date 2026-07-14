# Sprint 26 – NFC-Tags, Use-Case-Darstellung & Grafana Dashboard

**Zeitraum:** 10.07.2026 – 23.07.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 25](./sprint_25.md)

**Kurz:** NFC-Tag-Erweiterung fuer Track&Trace, Groessenanpassung der Use-Case-Diagramme fuer Windows-Desktop-Praesentation (Desktop 2 Fullscreen 100 %, Desktop 3 Hero 80 %), Grafana-Dashboard/Persistence-Datenpfad und Modus-A-Replay-Verifikation.

---

## Externe Termine

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| **14.08.2026** | **Kundentermin Musashi** (verschoben von 14.07.2026) | Erstverifikation Router-/Netzwerk-Setup und Windows-Desktop-Praesentation (Follow-up LOM-Day) |

---

## Aufgaben (thematisch, mit Haken)

### Router / Netzwerk-Setup

- [x] **GL.iNet-Router-Mount (DPS-Station):** 3D-Druck erstellt und passgenau an der **DPS-Station** eingebaut — ersetzt den originalen **FT-Router** vor Ort. *(14.07.2026)*
- [ ] **Netzwerk-Topologie/Verkabelung:** [How-to](../04-howto/setup/orbis-shopfloor-network-topology.md) mit Netzwerk-Kollegen vervollstaendigen (TBD: ORBIS-LAN, Router-B-Ports, DSP/MES/SAP, FT↔ORBIS-Bruecke); HTML-Review via `bash scripts/export-network-topology-html.sh`. *(Sprint 26)*
- *Rollen (Sprint 25): GL.iNet = DPS/FT-Ersatz auf **FT-LAN**; separater Router (TP-Link + LTE-USB) = **ORBIS-LAN**, DSP, MES/SAP, WLAN `ORBIS_H15_F05`.*

### Track&Trace / NFC-Tags

- [ ] APS-Erweiterung: neue NFC-IDs generierbar machen, damit Track&Trace nicht dauerhaft auf denselben NFCs basiert. *(Ursprung: Sprint 22)*
- *Wozu: Track&Trace-Demos und Kundentermine mit frischen Werkstueck-Identitaeten statt wiederholter NFCs.*

### OSF-UI / Use-Case-Diagramme (Praesentation)

- [ ] Use-Case-Diagramme **groessenanpassen** (kein inhaltlicher Umbau): Darstellung in **Desktop 2 (Fullscreen, Zoom 100 %)** und **Desktop 3 (Hero, Zoom 80 %)** auf Laptop-Monitor ohne Ueberlauf/Scroll-Probleme. *(Ursprung: Sprint 26; Bezug: [windows-desktops-teams-obs-setup-checklist.md](../04-howto/presentation/windows-desktops-teams-obs-setup-checklist.md))*
- *Wozu: Use-Cases im etablierten Windows-Desktop-Praesentations-Workflow (Sprint 25) sauber praesentierbar machen.*

### Grafana Dashboard

- [ ] **Modus A (Replay + Session):** Grafana `localhost:3000` mit Session-Replay erneut pruefen — Orders/Daten sichtbar; Abweichungen in Troubleshooting dokumentieren. *(Ursprung: Sprint 22; Nachfolger „keine orders“; siehe [runtime-modes-matrix.md](../04-howto/helper_apps/session-manager/runtime-modes-matrix.md))*
- [ ] Grafana-Dashboards ausbauen (fachliche Panels schaerfen, offene Visualisierungs-/Abnahmepunkte systematisch schliessen). *(Ursprung: Sprint 22)*
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffaehig machen (neben local-dev als naechster Zielpfad). *(Ursprung: Sprint 22)*

### ORBIS Feldbetrieb / Integrations-Fortsetzung

- [ ] Unterschiede zwischen localhost und RPi systematisch abarbeiten (insb. AGV-Erkennung/Anzeige auf RPi als Voraussetzung vor Overlay-Checks). *(Ursprung: Sprint 22)*

### Integration & Tests

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen. *(Ursprung: Sprint 21)*
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren. *(Ursprung: Sprint 18)*
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren. *(Ursprung: Sprint 18)*

### Blog & Organisation

- [ ] Blog: Reviews A1, A2, A3 *(Ursprung: Sprint 19)*
- [ ] Azure DevOps: Repo/Boards von GitHub *(Ursprung: Sprint 19)*

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] Sprint 26: Status Abgeschlossen, Datum *(Ursprung: Sprint 26)*
- [ ] Sprint 27 anlegen, offene `[ ]` uebernehmen *(Ursprung: Sprint 26)*
- [ ] PROJECT_STATUS / Roadmap kurz *(Ursprung: Sprint 26)*

---

## Links

- [Sprint 25](sprint_25.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md)

---

*Stand: 14.07.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
