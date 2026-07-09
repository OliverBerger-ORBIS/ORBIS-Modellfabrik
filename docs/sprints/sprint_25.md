# Sprint 25 – LOM-Day Nachbereitung & Praesentationstechnik

**Zeitraum:** 26.06.2026 – 09.07.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 24](./sprint_24.md)

**Kurz:** Nachbereitung des LOM-Day, Stabilisierung der Praesentationstechnik (Windows-Desktops-Workflow ohne FancyZones) und transparente Bearbeitung offener Integrationspunkte mit Task-Historie.

---

## Externe Termine

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| **26.06.2026** | **LOM-Day: Vorstellung der OSF** | Inhaltlich erfolgreiche OSF-Praesentation; klare Folgeaufgaben zu MES/SAP-Latenz und Praesentationstechnik abgeleitet |

---

## Aufgaben (thematisch, mit Haken)

### LOM-Day Nachbereitung / Lessons Learned

- [x] LOM-Day Ergebnis dokumentiert (26.06.2026): OSF-Praesentation inhaltlich erfolgreich.
- [ ] MES/SAP-Latenzzeiten aus dem LOM-Day technisch nachanalysieren und fuer Demo-Betrieb priorisierte Gegenmassnahmen festlegen. *(Ursprung: Sprint 25)*
- [ ] Praesentationstechnik aus LOM-Day aufarbeiten: Ursachenanalyse fuer unbefriedigende Beamer-Darstellung dokumentieren. *(Ursprung: Sprint 25)*
### Praesentationstechnik (neu)

- [x] Handlungsanweisung erstellt: Setup A (Sharing Laptop-Monitor unter Windows) als Quick-Checklist dokumentiert. *(Ursprung: Sprint 25; 29.06.2026: `docs/04-howto/presentation/windows-desktops-teams-obs-setup-checklist.md`)*
- [x] Handlungsanweisung erstellt: Setup B (Sharing zweiter Monitor) in derselben Quick-Checklist dokumentiert. *(Ursprung: Sprint 25; 29.06.2026: `docs/04-howto/presentation/windows-desktops-teams-obs-setup-checklist.md`)*
- [x] Desktop-Szenenmodell verbindlich beschrieben und aktualisiert: Desktop 1 (`Working`), Desktop 2 (`Fullscreen`), Desktop 3 (`Hero` mit Digital Twin + Kamera-Preview). *(Ursprung: Sprint 25; fortlaufend aktualisiert in `docs/04-howto/presentation/windows-desktops-teams-obs-setup-checklist.md`)*
- [x] Checkliste fuer Aufbau/Vorbereitung gegen zwei Testdurchlaeufe verifiziert. *(29.06.2026 erster Testlauf erfolgreich; 08.07.2026 erneuter Test nach Windows-Neustart erfolgreich)*
- [x] Zielentscheidung dokumentiert: Praesentation mit Windows-Bordmitteln (virtuelle Desktops + Desktop-Wechsel), **kein FancyZones**, **keine OBS-Praesentation** (OBS nur Kamera). *(DR: `docs/03-decision-records/29-windows-desktops-presentation-without-fancyzones.md`)*
- [x] 6-Aktionen-Workflow stabilisiert und Konftel-20 in OBS final konfiguriert: Resolution Device Default, Edit Transform Bounds FIT 1920×1080, Crop Top/Bottom 10, Left/Right 120; Preview Desktop 1 + Desktop 3 verifiziert. *(09.07.2026 vor Ort bei ORBIS)*
- *Wozu: Aufbau einer stabilen, reproduzierbaren und schnell einrichtbaren Praesentations-Umgebung auf dem ORBIS-Windows-Rechner, unabhaengig vom Ziel-Setup (Beamer, zweiter Monitor oder nur Laptop-Monitor).*

### ORBIS Feldbetrieb / Integrations-Fortsetzung

- [x] Datenpfad-Regel verbindlich dokumentieren: ORBIS Live -> Broker `192.168.0.100`; Replay -> erreichbarer Replay-Broker (lokal `localhost` oder externer Broker); Abweichungen in einer Troubleshooting-Checkliste erfassen. *(Ursprung: Sprint 22; 29.06.2026: `runtime-modes-matrix.md`, `troubleshooting.md`)*
- [x] Betriebsmodi + Konfig-Matrix fuer `OSF`/`Session Manager`/`Mosquitto` kompakt dokumentieren (Mode A: Local Replay, Mode B: Live auf RPi, Mode C: Live mit lokalem OSF) inkl. klarer No-Mix-Regel fuer Live+Replay auf denselben Topics/Brokern. *(Ursprung: Sprint 25; 29.06.2026: `docs/04-howto/helper_apps/session-manager/runtime-modes-matrix.md`)*
- [x] Windows-Startpfad fuer Replay dokumentiert und automatisiert: Mosquitto-Service auf `localhost:1883` plus WebSocket-Bridge auf `ws://localhost:9001` via `scripts/start-mosquitto-ws-bridge.ps1`; OSF- und Session-Manager-Checks auf Windows verifiziert. *(29.06.2026)*
- [x] Replay-Modus auf Windows-Rechner verifizieren (inkl. Betrieb mit lokalen Mosquitto). *(Ursprung: Sprint 25)*
- [x] Live-Modus am ORBIS-Setup verifizieren (erfolgreich getestet). *(Ursprung: Sprint 25; 09.07.2026)*
- [ ] Lokalen Dashboard-Fall "keine orders" reproduzieren und die Ursache dokumentieren (Ingest/Replay/Broker-Mapping/DB-Stand). *(Ursprung: Sprint 22)*
- [ ] Unterschiede zwischen localhost und RPi systematisch abarbeiten (insb. AGV-Erkennung/Anzeige auf RPi als Voraussetzung vor Overlay-Checks). *(Ursprung: Sprint 22)*
- *Wozu: Sicherstellen, dass OSF im Live- und Replay-Betrieb reproduzierbar funktioniert (lokal und auf RPi), damit Demo-/Messeszenarien nicht an Broker-Mapping, Datenpfad oder Umgebungsunterschieden scheitern.*

### Integration & Tests

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen. *(Ursprung: Sprint 21)*
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren. *(Ursprung: Sprint 18)*
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren. *(Ursprung: Sprint 18)*

### Backend & Deployment

- [ ] Grafana-Dashboards ausbauen (fachliche Panels schaerfen, offene Visualisierungs-/Abnahmepunkte systematisch schliessen). *(Ursprung: Sprint 22)*
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffaehig machen (neben local-dev als naechster Zielpfad). *(Ursprung: Sprint 22)*
- [x] Session-Manager-Tags sauber namespacen (z. B. `session-manager-vX.Y.Z`) und Konvention in Release-Checkliste verankern.
- [ ] **RPi OSF-UI v1.1.7 deployen** (vorbereitet, Deploy spaeter vor Ort): nach Push `npm run docker:osf-ui:deploy -- ff22@192.168.0.100` — Checkliste [rpi-deployment.md](../04-howto/deployment/rpi-deployment.md).
- *Wozu: Stabiles Deployment auf RPi sicherstellen, damit die komplette Praesentation nicht vom Arbeitsrechner, lokalen Versionen oder einer lokalen Angular-App auf `localhost` abhaengt.*

### Router GWN 7062m

- [ ] Router-Beschaffung: https://www.grandstream.com/products/networking-solutions/routers/product/gwn7062m
- [ ] 3D-Modell fuer `gwn7062m-mount` von V1 auf final erweitern (BLOCKED bis `gwn7062m` verfuegbar). *(Ursprung: Sprint 25)*
- [ ] Montageort final entscheiden und verifizieren: Option A ORBIS-Platte oder Option B Charging-Station. *(Ursprung: Sprint 23)*
- [ ] Router-Einrichtung durch IT-Abteilung koordinieren und abschliessen. *(Ursprung: Sprint 25)*
- [ ] Router im OSF-Betrieb testen (WLAN fuer OSF + VPN fuer MES/DSP/SAP). *(Ursprung: Sprint 25)*
- *Wozu: Ein Router, der OSF-WLAN und VPN-Anbindung (MES/DSP/SAP) in einer schlanken, produktionsnahen Hardware fuer Messen und ORBIS-Einsatz vereint.*

### Track&Trace / APS

- [ ] APS-Erweiterung: neue NFC-IDs generierbar machen, damit Track&Trace nicht dauerhaft auf denselben NFCs basiert. *(Ursprung: Sprint 22)*

### Blog & Organisation

- [ ] Blog: Reviews A1, A2, A3 *(Ursprung: Sprint 19)*
- [ ] Azure DevOps: Repo/Boards von GitHub *(Ursprung: Sprint 19)*

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] Sprint 25: Status Abgeschlossen, Datum *(Ursprung: Sprint 25)*
- [ ] Sprint 26 anlegen, offene `[ ]` uebernehmen *(Ursprung: Sprint 25)*
- [ ] PROJECT_STATUS / Roadmap kurz *(Ursprung: Sprint 25)*

---

## Erledigt

- [x] **OSF-UI I18n (EN-Source-Strings):** DPS-Terminologie, DSP-Architektur-Geraete-Labels, Functional Steps 4–12, Deployment-Pipeline, Sensor-/Shopfloor-UI; FR Label-Wrap AIQS/DPS — manuell EN/DE/FR verifiziert (09.07.2026). Release **v1.1.7**.

---

## Später (Backlog)

- Router-Variante / Mounting-Strategie fuer Folgehardware konsolidieren (Stabilitaet, Servicezugang, Kabelfuehrung).

---

## Links

- [Sprint 24](sprint_24.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md)

---

*Stand: 09.07.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
