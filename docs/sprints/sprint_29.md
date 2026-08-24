# Sprint 29 – Grafana/Persistenz, Intake-Bridge live & OD-Anbindung

**Zeitraum:** 21.08.2026 – 03.09.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 28](./sprint_28.md)

**Kurz:** Fokus **Grafana / Edge-Persistenz** und **Workpiece-Intake live** (Bridge auf RPi + optional OSF-UI-Subscribe); Carry-over Netzwerk/Blog/E2E; Vorbereitung Uni Magdeburg Deep-Dive SB (**21./22.09.**).

---

## Externe Termine & Outreach

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **21./22.09.2026** *(geplant)* | **Uni Magdeburg / Dr. Reggelin** — Meeting Saarbrücken Deep-Dive OSF/DSP; Kishitz; NDA-Unterschrift **Frank Wilhelm** noch offen | Hochschulkooperation / DSP-Story |
| *(offen)* | Abstimmung DSP-Truppe für SB-Termin | Terminfixierung Deep-Dive |
| *(Follow-up)* | **Daniel Wonkam** (OD) — Intake-Topic nutzen; Workpiece-Tracking 3er-Stack | Partner über `osf/workpiece/intake` |

---

## Coverage Standing

| Stand | Datum | Branches | Functions | Lines | Statements | Gates (B/F/L/S) | Gate-Margin (B/F/L/S) |
|--------|--------|----------|-----------|-------|------------|------------------|------------------------|
| Sprint-Start (Baseline = Sprint-28-Ende) | 20.08.2026 | 49.8% | 61.3% | 66.5% | 65.5% | 42 / 52 / 58 / 58 | +7.8 / +9.3 / +8.5 / +7.5 pp |
| Aktuell | 20.08.2026 | 49.8% | 61.3% | 66.5% | 65.5% | 42 / 52 / 58 / 58 | +7.8 / +9.3 / +8.5 / +7.5 pp |

- **Messmethode:** `npm run test:coverage` (`--runInBand`; bei Nx-Daemon-Fehler: `npx nx reset` + `NX_DAEMON=false`) → `coverage/osf-ui/index.html`. Details: [test-coverage-status.md](../07-analysis/test-coverage-status.md).
- **Top-3 Gaps:**
  1. `shopfloor-tab` / `shopfloor-preview`
  2. DSP-/Customer-Pages
  3. `agv-tab` / `workpiece-history`
- **Pflege:** Baseline unverändert; nach Messung nur **Aktuell** + Top-Gaps. Am Sprintende Pflicht-Messung vor Abschluss.

---

## Aufgaben (thematisch, mit Haken)

### Grafana / Edge-Persistenz *(Fokus)*

- *Replay-Politik (20.08.2026):* unterschiedliche Sessions mit **unterschiedlichen NFC-IDs** in der lokalen DB **akkumulieren**. Truncate **nicht** automatisch. Manuell: `bash osf-edge-persistence/scripts/reset-replay-db.sh` (optional `--nfc …`). NFC-Korrelation im Replay aus **APS-Payloads** (RGB_NFC / FTS `loadId` / CCU `workpieceId`) — `osf/workpiece/intake` ist Live-only (RPi-Bridge, nicht in Session-Logs).
- [x] **NFC first-class im Ingest (20.08.2026):** `workpiece_id` aus APS-Feldern (RGB_NFC / FTS `loadId` / CCU) — Replay-fähig ohne Bridge. Intake-Topic nur zusätzlich wenn live. Manuelles Reset-Skript. Tests 19/19.
- [x] **Modus A (Replay + Session, 24.08.2026):** Grafana `localhost:3000` mit Aug-Session `white-storage-production_20260807_111716` — NFC `92e0ad91595f63` in DB + Workpiece Trace sichtbar; weitere Sessions akkumulieren. Troubleshooting: Session Manager publisht TCP `:1883`, OSF-UI WS `:9001`, Persistence `host.docker.internal:1883`. *(Ursprung: Sprint 22)*
- [x] **Workpiece Trace Filter (24.08.2026):** Grafana-Variablen Color zuerst, NFC abhängig (nur IDs der gewählten Farbe). Ist-Ansicht: Station-Label (DPS/HBW/DRILL/MILL/AIQS/FTS), nur `FINISHED`, ohne CANCELLED/NAVIGATION-Rauschen; Farbe in der Timeline.
- [x] **Sensor um Ist-Event (24.08.2026):** Query-time SQL-Join (`sensor_snapshot` as-of, Fenster 30s), ohne Grafana und ohne `related_event_id`-Write. `npm run persistence:sensor-around-ist` (`--nfc`, `--anchors`, `--long`).
- [x] **Sensor-INTERVAL (24.08.2026):** 5 s bei aktiven Orders (`ccu/order/active`), 60 s idle; Warn/Alarm immer (`THRESHOLD`). Default 3600 s war zu grob. Persistence-Image neu bauen nach Config-Änderung.
- [x] **Soll-Topics (24.08.2026):** `ccu/order/request` + `ccu/order/response` + `module|fts/…/order` subscribed; Roharchiv + `shopfloor_event` (`REQUESTED`/`RESPONDED`, nicht im Grafana-Ist). Persistence-Image neu bauen.
- [x] **Grafana MQTT Topics raw (24.08.2026):** Panel auf Dashboard **Systemstatus** (`osf-system-status`) — `mqtt_raw_message` nach Topic, Zeitfenster wie Workpiece Trace. Explore nicht mehr nötig für den Ingest-Check.
- [ ] Grafana-Dashboards ausbauen (weitere fachliche Panels / DSP-Abnahme). *(Ursprung: Sprint 22)*
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffähig machen (neben local-dev als nächster Zielpfad). *(Ursprung: Sprint 22)*
- [ ] **Track&Trace Persistenz (Option B):** UI-Historie bleibt session-/RAM-scoped; längere NFC-Spuren über Edge/Grafana (`osf-edge-persistence`, [DR-28](../03-decision-records/28-edge-persistence-stack-and-metrics-model.md)) — kein Browser-localStorage. *(Entscheidung 21.07.2026; Ursprung: Sprint 26)*

### Workpiece-Intake / Object Detection *(Fokus)*

- [ ] **Intake-Bridge auf RPi deployen:** `npm run docker:workpiece-intake-bridge:deploy -- ff22@192.168.0.100` (FT-LAN); Verifikation Topic `osf/workpiece/intake`. How-to: [workpiece-intake-bridge-rpi.md](../04-howto/deployment/workpiece-intake-bridge-rpi.md). *(Sprint 28: Image gebaut, Deploy ausstehend)*
- [ ] **OSF-UI subscribe `osf/workpiece/intake`:** optionale Nutzung für OD-View / NFC-Einstieg (Folge nach Bridge live). *(Ursprung: Sprint 28; [DR-30](../03-decision-records/30-workpiece-intake-mqtt-facade.md))*
- *Partner-Hinweis an Daniel:* [workpiece-intake-event-partner.md](../04-howto/integrations/workpiece-intake-event-partner.md)

### Integration & Tests

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen. *(Ursprung: Sprint 21)*
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren. *(Ursprung: Sprint 18)*
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren. *(Ursprung: Sprint 18)*

### Router / Netzwerk-Setup

- [ ] **Netzwerk-Topologie/Verkabelung (Rest):** ORBIS-LAN-Adressliste + MES-Pfad mit Netzwerk-Kollegen (**nur mit ORBIS-VPN testbar**); Omada Admin-URL/Modell; ggf. HTML neu exportieren. *(Ursprung: Sprint 26)*
- *Rollen: GL.iNet weiß = DPS/FT-Gateway; GL.iNet grau = LTE→Omada WAN; Omada = WLAN + Port-Hub; Proxmox = DSP Edge im FT-LAN. How-to: [orbis-shopfloor-network-topology.md](../04-howto/setup/orbis-shopfloor-network-topology.md).*

### Blog & Organisation

- [ ] Blog: Review A3 *(Von Daten zu belastbaren KPIs)* *(Ursprung: Sprint 19 / 26)*
- [ ] Blog: Review A4 *(Von Erkenntnissen zu Aktionen)* *(Ursprung: Sprint 19 / 26)*
- [ ] Azure DevOps: Repo/Boards von GitHub *(Ursprung: Sprint 19)*

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] **Coverage Standing:** Endmessung (`npm run test:coverage`) → `Aktuell` + Top-Gaps; bei Bedarf [test-coverage-status.md](../07-analysis/test-coverage-status.md) aktualisieren
- [ ] Sprint 29: Status Abgeschlossen, Datum
- [ ] Sprint 30 anlegen, offene `[ ]` übernehmen; Coverage-Baseline = Endmessung Sprint 29
- [ ] PROJECT_STATUS / Roadmap kurz

---

## Links

- [Sprint 28](sprint_28.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md) · [test-coverage-status.md](../07-analysis/test-coverage-status.md) · [DR-30 Intake](../03-decision-records/30-workpiece-intake-mqtt-facade.md)

---

*Stand: 20.08.2026 (Sprintwechsel)* · Doku-Workflow: [sprints_README.md](sprints_README.md)
