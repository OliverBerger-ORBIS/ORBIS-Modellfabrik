# Sprint 29 – Grafana/Persistenz, Intake-Bridge live & OD-Anbindung

**Zeitraum:** 21.08.2026 – 03.09.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 28](./sprint_28.md)

**Kurz:** Fokus **Grafana / Edge-Persistenz** und **Workpiece-Intake live** (Bridge auf RPi + optional OSF-UI-Subscribe); Carry-over Netzwerk/Blog/E2E; Vorbereitung Uni Magdeburg Deep-Dive SB (**21./22.09.**).

---

## Externe Termine & Outreach

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **21.09.2026** *(bestätigt)* | **Uni Magdeburg / Dr. Reggelin** — **Ganztägiger Workshop Saarbrücken** Deep-Dive OSF/DSP; Termin-Einladung an **Kishitz** raus; **DSP-Team informiert** und unterstützt Deep Dive; NDA-Unterschrift **Frank Wilhelm** noch offen | Hochschulkooperation / DSP-Story |
| *(erledigt 25.08.2026)* | Abstimmung DSP-Truppe für SB-Termin — Team informiert, Unterstützung Deep Dive zugesagt | Terminfixierung Deep-Dive |
| *(Follow-up)* | **Daniel Wonkam** (OD) — Intake-Topic nutzen; Workpiece-Tracking 3er-Stack | Partner über `osf/workpiece/intake` |

---

## Coverage Standing

| Stand | Datum | Branches | Functions | Lines | Statements | Gates (B/F/L/S) | Gate-Margin (B/F/L/S) |
|--------|--------|----------|-----------|-------|------------|------------------|------------------------|
| Sprint-Start (Baseline = Sprint-28-Ende) | 20.08.2026 | 49.8% | 61.3% | 66.5% | 65.5% | 42 / 52 / 58 / 58 | +7.8 / +9.3 / +8.5 / +7.5 pp |
| Aktuell | 24.08.2026 | 51.2% | 62.8% | 67.8% | 66.7% | 48 / 59 / 64 / 63 | +3.2 / +3.8 / +3.8 / +3.7 pp |

- **Messmethode:** `npm run test:coverage` (`--runInBand`; bei Nx-Daemon-Fehler: `npx nx reset` + `NX_DAEMON=false`) → `coverage/osf-ui/index.html`. Details: [test-coverage-status.md](../07-analysis/test-coverage-status.md).
- **Top-3 Gaps:**
  1. `shopfloor-tab` / `agv-tab` (große Dateien)
  2. DSP-/Customer-Pages
  3. Restzweige `shopfloor-preview` (Route/SVG)
- **Pflege:** Baseline unverändert; nach Messung nur **Aktuell** + Top-Gaps. Am Sprintende Pflicht-Messung vor Abschluss.

---

## Aufgaben (thematisch, mit Haken)

### Grafana / Edge-Persistenz *(Fokus)*

- *Replay-Politik (20.08.2026, Nachzug 26.08.):* unterschiedliche Sessions mit **unterschiedlichen NFC-IDs** in der lokalen DB **akkumulieren**. Truncate **nicht** automatisch. Manuell: `bash osf-edge-persistence/scripts/reset-replay-db.sh` (optional `--nfc …`). **Ziel:** Intake über `osf/workpiece/intake` auch im Replay (neue Aufnahmen + Patch Storage-Sessions); APS-Felder bleiben Korrelation für Stationen. [DR-30 Nachtrag 26.08.](../03-decision-records/30-workpiece-intake-mqtt-facade.md).
- [x] **Replay-Gate lokal + kein Replay→`.201` (25.08.2026):** `PERSISTENCE_MODE=replay` nur Allowlist-DB-Hosts; Session-Gate via `osf/persistence/replay/session` + Tabelle `replay_session_ingest`; Truncate leert die Liste. Live ignoriert Control-Topics.- [x] **NFC first-class im Ingest (20.08.2026):** `workpiece_id` aus APS-Feldern (RGB_NFC / FTS `loadId` / CCU) — Replay-fähig ohne Bridge. Intake-Topic nur zusätzlich wenn live. Manuelles Reset-Skript. Tests 19/19.
- [x] **Modus A (Replay + Session, 24.08.2026):** Grafana `localhost:3000` mit Aug-Session `white-storage-production_20260807_111716` — NFC `92e0ad91595f63` in DB + Workpiece Trace sichtbar; weitere Sessions akkumulieren. Troubleshooting: Session Manager publisht TCP `:1883`, OSF-UI WS `:9001`, Persistence `host.docker.internal:1883`. *(Ursprung: Sprint 22)*
- [x] **Workpiece Trace Filter (24.08.2026):** Grafana-Variablen Color zuerst, NFC abhängig (nur IDs der gewählten Farbe). Ist-Ansicht: Station-Label (DPS/HBW/DRILL/MILL/AIQS/FTS), nur `FINISHED`, ohne CANCELLED/NAVIGATION-Rauschen; Farbe in der Timeline.
- [x] **Sensor um Ist-Event (24.08.2026):** Query-time SQL-Join (`sensor_snapshot` as-of, Fenster 30s), ohne Grafana und ohne `related_event_id`-Write. `npm run persistence:sensor-around-ist` (`--nfc`, `--anchors`, `--long`).
- [x] **Sensor-INTERVAL (24.08.2026):** 5 s bei aktiven Orders (`ccu/order/active`), 60 s idle; Warn/Alarm immer (`THRESHOLD`). Default 3600 s war zu grob. Persistence-Image neu bauen nach Config-Änderung.
- [x] **Soll-Topics (24.08.2026):** `ccu/order/request` + `ccu/order/response` + `module|fts/…/order` subscribed; Roharchiv + `shopfloor_event` (`REQUESTED`/`RESPONDED`, nicht im Grafana-Ist). Persistence-Image neu bauen.
- [x] **Grafana MQTT Topics raw (24.08.2026):** Panel auf Dashboard **Systemstatus** (`osf-system-status`) — `mqtt_raw_message` nach Topic, Zeitfenster wie Workpiece Trace. Explore nicht mehr nötig für den Ingest-Check.
- [x] **Live FT-LAN vorbereitet (24.08.2026):** How-to [edge-persistence-live-ft-lan.md](../04-howto/deployment/edge-persistence-live-ft-lan.md) — morgen Persistence auf dem Mac mit `env.live` (MQTT `.100`); OSF-UI armv7-Image bauen; Grafana/Timescale-Ziel bleibt **DSP `.201`**, nicht RPi (armv7, kein Timescale). Lokaler Alt-Container `osf-ui`:8080 gestoppt (`nx serve` :4200).
- [x] **DSP-Edge Stack-Doku (24.08.2026):** [dsp-edge-osf-persistence.md](../04-howto/deployment/dsp-edge-osf-persistence.md) — Mermaid Hosts/Services, Compose-Container, bekannte vs. unklare `.201`-Fakten, Fragen an DSP (Inventar/Rechte, nicht Erreichbarkeit).
- [x] **Live-Ingest FT-LAN verifiziert (25.08.2026):** Dual-Homed Mac (Gemini Wi‑Fi + FT-LAN Ethernet); Intake-Bridge auf RPi; Persistence live via SSH-Tunnel `:1884` → RPi MQTT (Docker Desktop erreicht `.100:1883` nicht). Events in Grafana **und** OSF-UI Track&Trace sichtbar (z. B. NFC `93b29ba34a2334`). Follow-up: Bridge `productRaw` oft `UNKNOWN` obwohl UI weiß/blau korrekt — später. Zielhost `.201` weiter offen.
- [x] **VE `.201` Inventar + Ziel-DB SQL Server (25.08.2026):** Docker/Compose/`pocadm` ok; SQL Host-Port **`:1433`** (`rittal_sqlserver`); Grafana-Alt gestoppt; Doku korrigiert. Ziel: neues OSF-Schema auf bestehender Instanz; Dev Option B = lokal SQL Server. DR-28 Nachtrag.
- [x] **Grafana Orders Farbe + Sensor-Skalen (25.08.2026):** Orders stacked by State×Color (BLUE/WHITE/RED); Completed-Serie nach Farbe; Recent-Orders-Tabelle. Sensor-Dashboards: getrennte Panels Vibration / Climate / Gas mit eigener Y-Achse.
- [x] **Grafana FTS/AGV Dashboard (25.08.2026):** `osf-fts` — Serial-Filter, Akku %/V + Verlauf, Loads-Timeline, Action-Bars DOCK/PASS/TURN/PICK/DROP, Last-Node, Driving/Paused; Shared Cursor.
- [x] **Grafana Overview-Home (25.08.2026):** `osf-home` — KPI-Stats, Orders×Color, Recent WP, FTS-Snapshot, Sensor-THRESHOLD-Alerts, Demo-Markdown + Deep-Links; Default-Home via Compose.
- [x] **SQL Server lokal (Option B, Compose) (25.08.2026):** Profil `mssql` → Container `osf-edge-mssql` (2022, Host `:1433`, amd64/Rosetta); `scripts/mssql-smoke.sh`; Postgres parallel. Schema/Persistence-Anbindung = nächste Häppchen. How-to: README + [dsp-edge-osf-persistence.md](../04-howto/deployment/dsp-edge-osf-persistence.md).
- [x] **Schema T-SQL (25.08.2026):** `db/mssql/` (DB `osf_edge`, Tabellen + Indizes, ohne Timescale); `scripts/mssql-init-schema.sh`. Unit-Tests: `utils.spec.ts` + `schemaContract.spec.ts` (Tabellen-Parität PG↔MSSQL).
- [x] **Mini: Tabellen-Präfixe UC-02 (25.08.2026):** Shopfloor unprefixed; Umwelt `env_sensor_snapshot`; kein `biz_*`. Postgres/Timescale aus aktivem Compose entfernt (Legacy nur Git-History). Contract-Test MSSQL-only.
- [x] **`shopfloor_order` + Ingest ohne Completed-Dump (25.08.2026):** Rename `production_order` → `shopfloor_order` (`order_type` STORAGE|PRODUCTION); Orders aus response/active; `ccu/order/completed` nur für `knownOrderIds`. CCU-HBW-Reset → mögliche STORAGE-Leichen in DB akzeptiert.
- [x] **module_type via Serial-Map (25.08.2026):** APS-Serial→DPS/HBW/DRILL/MILL/AIQS im Normalizer; Grafana Modul/FTS-Panel COALESCE-Fallback für Altzeilen.
- [x] **Persistence → MSSQL (25.08.2026):** `DB_DIALECT=mssql` + `MssqlPersistenceDb`; Factory; Compose `persistence-service-mssql`; Smoke `scripts/mssql-persist-smoke.ts`. Postgres-Pfad bleibt Default für Grafana.
- [x] **Grafana → MSSQL (25.08.2026):** Default-DS `OSF SQL Server` (`POSFMSQL001`); alle Dashboards T-SQL; Postgres als Zweit-DS. Compose übergibt `MSSQL_*` an Grafana (`host.docker.internal:1433`).
- [x] **Doku Option B (25.08.2026):** How-to [edge-persistence-dev-mssql.md](../04-howto/deployment/edge-persistence-dev-mssql.md) — Compose, Ports, Reset, Verweise README / DR-28 / dsp-edge. *(Postgres-Parallelpfad entfällt.)*
- [x] **`.201` OSF-DB + App-User (Skript 25.08.2026):** DSP-OK für DB/`osf_edge` + App-User (nicht sa). T-SQL `db/mssql/010_app_user.sql`, `scripts/mssql-create-app-user.sh` (reader/writer/execute). Lokal anlegbar; **auf `rittal_sqlserver` noch ausführen** sobald FT-LAN (Home-Office: `.201` nicht erreichbar).
- [x] **`.201` App-User + Schema live (26.08.2026):** Gegen `rittal_sqlserver` (`192.168.0.201:1433`) — DB `osf_edge`, Login/User `osf_edge` (reader/writer), 7 Tabellen inkl. `shopfloor_order` / `env_sensor_snapshot` / `replay_session_ingest`. Dev-PW wie lokal (`OsfEdge_App9#`). Compose-Deploy Persistence/Grafana = nächster Schritt.
- [x] **Deploy `.201` (26.08.2026):** `docker-compose.dsp.yml` + `env.dsp` auf VE (`~/osf-edge-persistence`); Persistence live → MQTT `.100` + SQL `host.docker.internal:1433`; Grafana `:3000` (Home `osf-home`). Verifiziert: DB wächst (Events/Raw/Sensoren), `http://192.168.0.201:3000` health OK.
- [x] **Arduino NTP v1.1.14 flashen (26.08.2026):** Sketch ORBIS: UDP→RPi zuerst. Flash OK; Serial `Zeit OK UDP idx=0`; MQTT `timestamp` ≈ wall UTC; factsheet `1.1.14`.
- [x] **Live ohne Mac-Tunnel (26.08.2026):** Checkliste [edge-persistence-live-ft-lan.md](../04-howto/deployment/edge-persistence-live-ft-lan.md) / [dsp-edge-osf-persistence.md](../04-howto/deployment/dsp-edge-osf-persistence.md) — Zielbetrieb `.201`; Tunnel nur Fallback.

### Workpiece-Intake / Object Detection *(Fokus)*

- [x] **Intake-Bridge auf RPi deployen (25.08.2026):** Image `orbis-workpiece-intake-bridge:1.0.0` geladen; Service in Pi-`docker-compose-prod.yml` ergänzt (**CCU `v1.3.0-osf.4` / OSF-UI `1.2.2` unverändert**). Logs: subscribed `module/v1/ff/NodeRed/SVR4H73275/state`. Verifikation Topic `osf/workpiece/intake` am DPS-NFC. How-to: [workpiece-intake-bridge-rpi.md](../04-howto/deployment/workpiece-intake-bridge-rpi.md). *(Sprint 28: Image gebaut)*
- [x] **Intake wartet auf Farbe (25.08.2026):** kein Publish bei fehlendem/`UNKNOWN` `productRaw`; erst wenn `metadata.type` / `workpiece.type` / `loads[0].type` gesetzt. Tests 8/8; Image neu auf RPi (`--no-deps`). Live verifiziert: `productRaw":"BLUE"` NFC `59a42cb15f9e1f` (kein UNKNOWN mehr).
- [x] **Intake ohne orderId (25.08.2026):** `orderId` aus Vertrag/Code entfernt (DR-30, Partner-How-to); Storage-Order kommt später über APS, Korrelation über NFC. Redeploy Bridge.
- [x] **OSF-UI Intake als T&T-Einstieg ([DR-30](../03-decision-records/30-workpiece-intake-mqtt-facade.md) Nachtrag 26.08.):** Subscribe `osf/workpiece/intake` → History-Bootstrap; APS-Intake nicht trackable. Live OK; Version **1.3.0** Commit/Push/RPi-Deploy. **Offen:** (3) Recorder/Doku; (4) Storage-Sessions patchen / Rest inventarisieren.
- *Partner-Hinweis an Daniel:* [workpiece-intake-event-partner.md](../04-howto/integrations/workpiece-intake-event-partner.md)

### Integration & Tests

- [x] **Coverage Gates + Shopfloor-Tests (24.08.2026):** Jest-Thresholds `48 / 59 / 64 / 63` (vorher `42 / 52 / 58 / 58`). Specs für Rotation/Layout-Service, Shopfloor-Preview (Zoom, Selection, Rotation, Route-Helfer, SVG), AGV-Viewport. Messung: B/F/L/S **51.2 / 62.8 / 67.8 / 66.7**; 1451 Tests passed. How-to + [test-coverage-status.md](../07-analysis/test-coverage-status.md).
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
