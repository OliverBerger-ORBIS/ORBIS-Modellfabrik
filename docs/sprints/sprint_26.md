# Sprint 26 – NFC-Tags, Use-Case-Darstellung & Grafana Dashboard

**Zeitraum:** 10.07.2026 – 23.07.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 25](./sprint_25.md)

**Kurz:** NFC-Tag-Erweiterung fuer Track&Trace, **Landscape/Hero-Praesentationsprofile** fuer Use-Case-/DSP-Diagramme (Browser-Zoom Desktop 2/3, Diagramm-Skalierung), Grafana-Dashboard/Persistence-Datenpfad und Modus-A-Replay-Verifikation.

---

## Externe Termine

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| **14.07.2026** | **Interner Probelauf** Windows-Desktop/OBS + MES/PT (Musashi → 14.08.) | Dress rehearsal statt Kundentermin — Probelauf 14.07. + Live-Test 15.07. abgeschlossen |
| **14.08.2026** | **Kundentermin Musashi** (verschoben von 14.07.2026) | Erstverifikation Router-/Netzwerk-Setup und Windows-Desktop-Praesentation (Follow-up LOM-Day) |

---

## Aufgaben (thematisch, mit Haken)

### Router / Netzwerk-Setup

- [x] **GL.iNet-Router-Mount (DPS-Station):** 3D-Druck erstellt und passgenau an der **DPS-Station** eingebaut — ersetzt den originalen **FT-Router** vor Ort. *(14.07.2026)*
- [ ] **Netzwerk-Topologie/Verkabelung:** [How-to](../04-howto/setup/orbis-shopfloor-network-topology.md) mit Netzwerk-Kollegen vervollstaendigen (TBD: ORBIS-LAN, Router-B-Ports, DSP/MES/SAP, FT↔ORBIS-Bruecke); HTML-Review via `bash scripts/export-network-topology-html.sh`. *(Sprint 26)*
- *Rollen (Sprint 25): GL.iNet = DPS/FT-Ersatz auf **FT-LAN**; separater Router (TP-Link + LTE-USB) = **ORBIS-LAN**, DSP, MES/SAP, WLAN `ORBIS_H15_F05`.*

### Praesentation (Windows-Desktops / OSF-UI)

- [x] **OSF-UI Praesentation Landscape/Hero (Desktop 2 + 3):** UC **Landscape**, DSP **Hero** — verifiziert 14.07.2026 @ 1920×1200; Checkliste [windows-desktops-teams-obs-setup-checklist.md](../04-howto/presentation/windows-desktops-teams-obs-setup-checklist.md).
- [x] **Windows-Desktop-/OBS-Setup (Probelauf 14.07.2026):** virtuelle Desktops, OBS-Kamera, Tab-Gruppen inkl. **MES MD1** und **PT MD1** — grundsaetzlich lauffaehig.
- [x] **Praesentations-Setup Live-Test (15.07.2026):** Ablauf nach aktualisierter Checkliste — Shopfloor, Konftel-20/OBS (zwei Previews), Tab-Gruppen **OSF-RPi** + **MES** + **DSP**, Anzeige **Duplizieren**, Desktop-Verteilung (`Win + Ctrl + ←/→`), Preset-Kurztest — erfolgreich.
- [x] **Praesentations-Doku** und SmartFactory Favoriten im Azure DevOPs Projekt

### Track&Trace / NFC-Tags

- [ ] APS-Erweiterung: neue NFC-IDs generierbar machen, damit Track&Trace nicht dauerhaft auf denselben NFCs basiert. *(Ursprung: Sprint 22)*
- *Wozu: Track&Trace-Demos und Kundentermine mit frischen Werkstueck-Identitaeten statt wiederholter NFCs.*

### Grafana Dashboard

- [ ] **Modus A (Replay + Session):** Grafana `localhost:3000` mit Session-Replay erneut pruefen — Orders/Daten sichtbar; Abweichungen in Troubleshooting dokumentieren. *(Ursprung: Sprint 22; Nachfolger „keine orders“; siehe [runtime-modes-matrix.md](../04-howto/helper_apps/session-manager/runtime-modes-matrix.md))*
- [ ] Grafana-Dashboards ausbauen (fachliche Panels schaerfen, offene Visualisierungs-/Abnahmepunkte systematisch schliessen). *(Ursprung: Sprint 22)*
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffaehig machen (neben local-dev als naechster Zielpfad). *(Ursprung: Sprint 22)*

### ORBIS Feldbetrieb / Integrations-Fortsetzung

- [x] **RPi OSF-UI v1.1.8 deployen (15.07.2026):** `npm run docker:osf-ui:deploy -- ff22@192.168.0.100` — Container `orbis-osf-ui:1.1.8`, HTTP `:8080` 200 OK.
- [ ] Unterschiede zwischen localhost und RPi systematisch abarbeiten (insb. AGV-Erkennung/Anzeige auf RPi als Voraussetzung vor Overlay-Checks). *(Ursprung: Sprint 22)*

### Integration & Tests

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen. *(Ursprung: Sprint 21)*
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren. *(Ursprung: Sprint 18)*
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren. *(Ursprung: Sprint 18)*

### Blog & Organisation

- [x] **Blog A1 veröffentlicht (19.06.2026):** [Skalierbare Smart Factory](https://www.orbis-group.com/de-de/blog/branchen/manufacturing/skalierbare-smart-factory/) *(Ursprung: Sprint 24; Basis für A2, A3 und A4)*
- [ ] **Blog A2 Review (Track & Trace als konkreter Anwendungsfall) ** geplante Veröffentlichung am 20-24-Juli
- [ ] Blog: Review A3 *(Von Daten zu belastbaren KPIs)*
- [ ] Blog: Review A4 *(Von Erkenntnissen zu Aktionen)*
- [ ] Azure DevOps: Repo/Boards von GitHub *(Ursprung: Sprint 19)*

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] Sprint 26: Status Abgeschlossen, Datum *(Ursprung: Sprint 26)*
- [ ] Sprint 27 anlegen, offene `[ ]` uebernehmen *(Ursprung: Sprint 26)*
- [ ] PROJECT_STATUS / Roadmap kurz *(Ursprung: Sprint 26)*

---

## Links

- [Sprint 25](sprint_25.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md)

---

*Stand: 15.07.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
