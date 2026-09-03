# Sprint 29 – Grafana/Persistenz, Intake-Bridge live & OD-Anbindung

**Zeitraum:** 21.08.2026 – 03.09.2026 · **Status:** Abgeschlossen · **Vorheriger Sprint:** [Sprint 28](./sprint_28.md) · **Nächster Sprint:** [Sprint 30](./sprint_30.md)

**Kurz:** Fokus **Grafana / Edge-Persistenz** und **Workpiece-Intake live** (Bridge auf RPi + OSF-UI-Subscribe); Dual-AGV Sessions + Serial-Resolver **v1.3.6**; T&T Serial-/NFC-first Code lokal; Language-Reload-T&T bewusst auf Sprint 30 verschoben.

---

## Externe Termine & Outreach

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **14.09.2026** | **Firma Bühler** — OSF-Präsentation **live** am Shopfloor | Kunden-Demo / Use-Case-Story |
| **17.09.2026** | **ORBIS Welcome Days** — OSF-Präsentation für neue ORBIS-Mitarbeiter | Onboarding / interne DSP-Story |
| **21.09.2026** *(bestätigt)* | **Uni Magdeburg / Dr. Reggelin** — **Ganztägiger Workshop Saarbrücken** Deep-Dive OSF/DSP; Termin-Einladung an **Kishitz** raus; **DSP-Team informiert** und unterstützt Deep Dive; NDA-Unterschrift **Frank Wilhelm** noch offen | Hochschulkooperation / DSP-Story |
| *(erledigt 25.08.2026)* | Abstimmung DSP-Truppe für SB-Termin — Team informiert, Unterstützung Deep Dive zugesagt | Terminfixierung Deep-Dive |
| *(erledigt 26.08.2026)* | **Daniel Wonkam** (OD) — Intake-Topic nutzen; Workpiece-Tracking 3er-Stack | [workpiece-intake-event-partner.md](../04-howto/integrations/workpiece-intake-event-partner.md) an Daniel |

---

## Coverage Standing

| Stand | Datum | Branches | Functions | Lines | Statements | Gates (B/F/L/S) | Gate-Margin (B/F/L/S) |
|--------|--------|----------|-----------|-------|------------|------------------|------------------------|
| Sprint-Start (Baseline = Sprint-28-Ende) | 20.08.2026 | 49.8% | 61.3% | 66.5% | 65.5% | 42 / 52 / 58 / 58 | +7.8 / +9.3 / +8.5 / +7.5 pp |
| Mid (Coverage D) | 27.08.2026 | 54.8% | 66.8% | 72.1% | 71.0% | 48 / 59 / 64 / 63 | +6.8 / +7.8 / +8.1 / +8.0 pp |
| **Aktuell (Sprint-Ende)** | **03.09.2026** | **54.77%** | **66.87%** | **71.97%** | **70.89%** | **48 / 59 / 64 / 63** | **+6.8 / +7.9 / +8.0 / +7.9 pp** |

- **Messmethode:** `npm run test:coverage` (`--runInBand`; bei Nx-Daemon-Fehler: `npx nx reset` + `NX_DAEMON=false`) → `coverage/osf-ui/index.html`. Details: [test-coverage-status.md](../07-analysis/test-coverage-status.md).
- **Top-3 Gaps (Stand 03.09.):**
  1. `shopfloor-tab` / `agv-tab` / `shopfloor-preview`
  2. DSP-/UC SVG-Generatoren
  3. Restzweige `workpiece-history` / große Tabs
- **Pflege:** Baseline unverändert; nach Messung nur **Aktuell** + Top-Gaps. Am Sprintende Pflicht-Messung vor Abschluss.
- **Hinweis:** Gates `48 / 59 / 64 / 63` beibehalten (Margins ~7 pp); kein Gate-Bump. Endmessung flat vs. 27.08. (Dual-AGV-Code + Specs).

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
- [x] **Intake End-to-End FT-LAN (01.09.2026):** Bridge → `osf/workpiece/intake` → OSF-UI T&T (NFC `164c81af4b0d11`). Grafana: Datasource OK; Intake in **Systemstatus → MQTT Topics (raw)** prüfen (nicht Workpiece Trace). Persistence `.201`: manuell `docker logs osf-edge-persistence-service` bei Bedarf.
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
- [x] **Grafana MSSQL TLS `.201` (01.09.2026):** Datasource `encrypt: disable` (rittal_sqlserver Self-Signed / Go 1.23+ negative serial); Connection OK, Dashboards mit Daten. Repo: `datasource.yml` version 6. Manuell auf VE + `--force-recreate grafana`.
- [x] **Arduino NTP v1.1.14 flashen (26.08.2026):** Sketch ORBIS: UDP→RPi zuerst. Flash OK; Serial `Zeit OK UDP idx=0`; MQTT `timestamp` ≈ wall UTC; factsheet `1.1.14`.
- [x] **Live ohne Mac-Tunnel (26.08.2026):** Checkliste [edge-persistence-live-ft-lan.md](../04-howto/deployment/edge-persistence-live-ft-lan.md) / [dsp-edge-osf-persistence.md](../04-howto/deployment/dsp-edge-osf-persistence.md) — Zielbetrieb `.201`; Tunnel nur Fallback.

### Workpiece-Intake / Object Detection *(Fokus)*

- [x] **Intake-Bridge auf RPi deployen (25.08.2026):** Image `orbis-workpiece-intake-bridge:1.0.0` geladen; Service in Pi-`docker-compose-prod.yml` ergänzt (**CCU `v1.3.0-osf.4` / OSF-UI `1.2.2` unverändert**). Logs: subscribed `module/v1/ff/NodeRed/SVR4H73275/state`. Verifikation Topic `osf/workpiece/intake` am DPS-NFC. How-to: [workpiece-intake-bridge-rpi.md](../04-howto/deployment/workpiece-intake-bridge-rpi.md). *(Sprint 28: Image gebaut)*
- [x] **Intake wartet auf Farbe (25.08.2026):** kein Publish bei fehlendem/`UNKNOWN` `productRaw`; erst wenn `metadata.type` / `workpiece.type` / `loads[0].type` gesetzt. Tests 8/8; Image neu auf RPi (`--no-deps`). Live verifiziert: `productRaw":"BLUE"` NFC `59a42cb15f9e1f` (kein UNKNOWN mehr).
- [x] **Intake ohne orderId (25.08.2026):** `orderId` aus Vertrag/Code entfernt (DR-30, Partner-How-to); Storage-Order kommt später über APS, Korrelation über NFC. Redeploy Bridge.
- [x] **OSF-UI Intake als T&T-Einstieg ([DR-30](../03-decision-records/30-workpiece-intake-mqtt-facade.md) Nachtrag 26.08.):** Subscribe + Live-Bootstrap; APS-Intake nicht trackable; Live + RPi **1.3.0**. (3) Recorder/Doku: Intake nicht excluden. (4) Storage-Logs gepatcht (`patch_session_intake_events.py`, +38); Rest behalten (Startup / 2-AGV / synthetic).
- [x] **T&T NFC-Kacheln (26.08.2026):** Grid neueste links oben; ohne Farbe alle; 2 Zeilen + Y-Scroll; Events in Zeile 1; Ort ohne Serial. **1.3.1** RPi-Deploy.
- [x] **Intake nicht im Browser-Archiv (26.08.2026):** `osf/workpiece/intake` → `NO_PERSIST_TOPICS`; Catch-up nur RAM-`getHistory`. Soft-Refresh re-`initialize` T&T. **1.3.4** RPi-Deploy 01.09.2026 (kein `clearAll()`; `replayBufferedHistory()`). Live verifiziert: NFC `164c81af4b0d11` COLOR+NFC in T&T; Bridge publish OK.
- [x] **AGV-2 Serial `xkI4` (01.09.2026):** FT-Reset zweites FTS; Layout + `FTS_SERIALS_FALLBACK`, Tests/Fixtures/Sessions von `leJ4` → `xkI4`. **1.3.5** RPi-Deploy.
- [x] **Dual-AGV T&T Replay + Resolver (01.09.2026):** Shared `getEffectiveFtsSerials()` (`fts-serial-resolver.ts`) — Layout + Fallback `5iO4`/`xkI4` + MessageMonitor-Topics; Fixes T&T/Orders/AGV-Tab wenn Layout beim Replay noch nicht geladen. Referenz-Session `storage-blue-dual-agv-bwr_20260901_124524.log`; Commit `a1e3b57a`, Tag **v1.3.6**, RPi-Deploy. Pre-commit: `order-tab` Spec-Mock `getTopics` ergänzt (Test-Kompatibilität, kein Live-Bug).
- [x] **Unvollständige ml-Sessions entfernt (26.08.2026):** `storage-production-ml-wbr_…115849`, `…-brw_…121835`, `…-bwr_…131822` (Name vor Aufnahme, nur 2 DPS-Intakes); INVENTORY bereinigt.
- [x] **Partner-Hinweis Daniel (26.08.2026):** [workpiece-intake-event-partner.md](../04-howto/integrations/workpiece-intake-event-partner.md) an Daniel Wonkam (OD) — Intake-Topic / 3er-Stack.

### Demo & Session-Aufnahmen

- [x] **Dual-AGV Referenz-Sessions aufnehmen (01.–03.09.2026):** CCU **Step-Dispatch**; Sessions `storage-blue-dual-agv-bwr_*` (01.09.), `storage-brw-dual-agv-brw_*` + **`storage-wbr-dual-agv-rwb_20260903_094319`** (03.09., aktuelle Ref.). Grafana + T&T **live OK** (03.09.). Plan [dual-agv-session-plan-2026-09.md](../07-analysis/dual-agv-session-plan-2026-09.md); [INVENTORY.md](../../data/osf-data/sessions/INVENTORY.md).
- [x] **T&T Dual-AGV Serial-/NFC-first Code (03.09.2026):** Transportgruppen nach FTS-Serial; AGV-Label aus `moduleId`; fremde Step-`orderId` behält NFC-Phase (`coPassenger`). Specs + Attribution-How-to. **Replay-Abnahme + Commit → Sprint 30.**
- *Language-Reload vs. T&T (03.09.2026, WAD):* `setLocale` → Full Reload Locale-Build; RAM-Historie weg (Live+Replay). Kein Hotfix in Sprint 29 — Lösung **Sprint 30**. Doku: [osf-ui-track-trace-history-attribution.md](../04-howto/osf-ui-track-trace-history-attribution.md).

### Integration & Tests

- [x] **Coverage Gates + Shopfloor-Tests (24.08.2026):** Jest-Thresholds `48 / 59 / 64 / 63` (vorher `42 / 52 / 58 / 58`). Specs für Rotation/Layout-Service, Shopfloor-Preview (Zoom, Selection, Rotation, Route-Helfer, SVG), AGV-Viewport. Messung: B/F/L/S **51.2 / 62.8 / 67.8 / 66.7**; 1451 Tests passed. How-to + [test-coverage-status.md](../07-analysis/test-coverage-status.md).
- [x] **Coverage Zwischenmessung (26.08.2026):** `npm run test:coverage` → B/F/L/S **51.7 / 63.3 / 68.3 / 67.2**; +13 Tests (Intake-RAM, Soft-Refresh/Resubscribe, Persistence-Cleanup). Gates unverändert (Margin ~3.7–4.3 pp).
- *UI-Test-Framework (Sprint 21 → 29):* [testing-strategy.md](../04-howto/testing/testing-strategy.md) Tier A/B; [test-framework-replay-comparison-2026-03.md](../07-analysis/test-framework-replay-comparison-2026-03.md). Stufen A–D = Fortsetzung des Framework-Ausbaus (nicht nur Coverage-Zahl, sondern kritische Flows absichern).*
- [x] **Coverage A – DSP/Use-Case Smokes (Tier A, 26.08.2026):** Render-Specs für `dsp-page`, DSP-Sections (Overview/Methodology/Use-Cases + Architecture mit Mock-Animation), 6 Base-Use-Case-Pages (UC-01/02/03/04/06/07). +23 Tests; B/F/L/S **51.8 / 65.3 / 70.6 / 69.5** (vorher 51.7 / 63.3 / 68.3 / 67.2).
- [x] **Coverage B – Shopfloor/AGV Helper (Tier A, 26.08.2026):** Helper-Specs für Transport-Row Dock/Charge, `getModuleMessageCount`, HBW/DRILL-MQTT-Parser, `build-fts-preview-positions`, AGV Command-Availability, `handleFtsStateChange`, `detectUnknownAgvOptions`. +20 Tests; B/F/L/S **54.2 / 66.2 / 71.5 / 70.4** (vorher 51.8 / 65.3 / 70.6 / 69.5).
- [x] **Coverage C – Shopfloor/AGV Interaktion (Tier A, 27.08.2026):** Selection/Modul-Wechsel (`selectModuleByType`, DPS→DRILL), Double-Click→Sidebar, `white_step3`-Fixture-Kette, AGV Serial-Wechsel + `sendNavigateToTarget`, Preview Highlight/Viewport/Follow-Scroll. +14 Tests; B/F/L/S **54.6 / 66.7 / 72.0 / 70.9** (vorher 54.2 / 66.2 / 71.5 / 70.4). **Tier B (Replay/Visual Gate):** manuell gem. [visual gate](../04-howto/osf-ui-shopfloor-route-agv-visual-gate.md) — nicht automatisierbar.
- [x] **Coverage D – Tab-Logik → Services (Tier A-Vorbereitung, 27.08.2026):** Extrahiert `count-module-messages`, `hbw-stock-metadata`, `agv-route-overlay.utils` (+ Specs); Tabs delegieren. +11 Tests; B/F/L/S **54.8 / 66.8 / 72.1 / 71.0** (leicht ↑, Schwerpunkt Wartbarkeit).
- [x] **Coverage E – Dual-AGV / Language-Vertrag (03.09.2026):** Specs Language full-reload WAD, FTS empty-serial, NFC-first STORAGE-Phase, serial-first AGV-Label; Endmessung B/F/L/S **54.77 / 66.87 / 71.97 / 70.89**; 1548 Tests passed.
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren. *(Ursprung: Sprint 18)* → Sprint 30
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren. *(Ursprung: Sprint 18)* → Sprint 30

### Router / Netzwerk-Setup

- [ ] **Netzwerk-Topologie/Verkabelung (Rest):** ORBIS-LAN-Adressliste + MES-Pfad mit Netzwerk-Kollegen (**nur mit ORBIS-VPN testbar**); Omada Admin-URL/Modell; ggf. HTML neu exportieren. *(Ursprung: Sprint 26)*
- *Rollen: GL.iNet weiß = DPS/FT-Gateway; GL.iNet grau = LTE→Omada WAN; Omada = WLAN + Port-Hub; Proxmox = DSP Edge im FT-LAN. How-to: [orbis-shopfloor-network-topology.md](../04-howto/setup/orbis-shopfloor-network-topology.md).*

### Blog & Organisation

- [ ] Blog: Review A3 *(Von Daten zu belastbaren KPIs)* *(Ursprung: Sprint 19 / 26)*
- [ ] Blog: Review A4 *(Von Erkenntnissen zu Aktionen)* *(Ursprung: Sprint 19 / 26)*
- [ ] Azure DevOps: Repo/Boards von GitHub *(Ursprung: Sprint 19)*

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [x] **Coverage Standing:** Endmessung (`npm run test:coverage`) → `Aktuell` + Top-Gaps; [test-coverage-status.md](../07-analysis/test-coverage-status.md) aktualisiert (03.09.2026)
- [x] Sprint 29: Status Abgeschlossen, Datum 03.09.2026
- [x] Sprint 30 anlegen, offene `[ ]` übernehmen; Coverage-Baseline = Endmessung Sprint 29
- [x] PROJECT_STATUS / Roadmap kurz

---

## Links

- [Sprint 28](sprint_28.md) · [Sprint 30](sprint_30.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md) · [test-coverage-status.md](../07-analysis/test-coverage-status.md) · [DR-30 Intake](../03-decision-records/30-workpiece-intake-mqtt-facade.md)

---

*Stand: 03.09.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
