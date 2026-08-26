# OSF Edge Persistence Stack

Docker-based persistence and dashboard stack for OSF:

- **Microsoft SQL Server** (local Compose = same dialect as DSP VE `.201`)
- Grafana
- Read-only MQTT persistence service

Postgres/Timescale was removed from the active stack (still in git history).

**Dev how-to (Option B):** [docs/04-howto/deployment/edge-persistence-dev-mssql.md](../docs/04-howto/deployment/edge-persistence-dev-mssql.md)

## Deployment targets

The same stack supports three phases:

- `local-dev` (Mac/Notebook): primary setup for current development and tests
- `rpi-pilot`: optional transitional deployment
- `edge-prod`: target state for productive operation

## Architecture

APS/RPi keeps operational responsibilities:

- CCU / Node-RED / MQTT broker
- no heavy DB/dashboard workloads required

Edge persistence stack responsibilities:

- MQTT subscribe only (read-only)
- persistence for process/shopfloor/environment/sensor metrics
- analytics and dashboards

## Runtime modes

The stack now uses two explicit runtime profiles:

- `env.live` (default): persistence subscribes to APS broker (`192.168.0.100:1883`)
- `env.replay` (test): persistence subscribes to local host broker (`host.docker.internal:1883`)

### Mode policy (team standard)

- Use **LIVE** (`env.live`) when the stack runs on RPi / future edge node.
- Use **REPLAY** (`env.replay`) only for local tests on Mac with Replay-Station + local broker.
  - `PERSISTENCE_MODE=replay` refuses non-local DB hosts (e.g. `.201`) — live VE is `env.live` only.
  - Session-gate: Replay Station publishes `osf/persistence/replay/session` (`begin`/`commit` + log filename). Already committed sessions are not re-persisted until full reset.
- Do not use REPLAY profile on production-like deployments.

## Quick start (default = LIVE)

1. Activate LIVE profile:

```bash
cp env.live .env
```

2. Start stack:

```bash
docker compose up -d
```

3. Verify:

- Grafana: `http://localhost:3000`
- SQL Server: `localhost:1433` (DB `osf_edge`)

```bash
bash scripts/mssql-smoke.sh
bash scripts/mssql-init-schema.sh   # once / after schema changes
bash scripts/mssql-create-app-user.sh
```

- App user: `osf_edge` (reader/writer/execute; Dev-Passwort `OsfEdge_App9#`)
- Smoke without MQTT: `MSSQL_HOST=localhost MSSQL_PASSWORD='OsfEdge_App9#' npx tsx scripts/mssql-persist-smoke.ts`
- Grafana datasource: **OSF SQL Server** only

## Stop

```bash
docker compose down
```

## Topics

### Process / shopfloor

- `ccu/order/active`
- `ccu/order/completed`
- `ccu/order/request` (Soll: UI/DSP/DPS Auftrag)
- `ccu/order/response` (CCU bestätigt `orderId` / `requestId`)
- `ccu/state/stock`
- `ccu/state/layout`
- `ccu/state/config`
- `ccu/state/flows`
- `ccu/pairing/state`
- `module/v1/ff/+/state`
- `module/v1/ff/+/connection`
- `module/v1/ff/+/order`
- `module/v1/ff/NodeRed/+/state`
- `module/v1/ff/NodeRed/+/connection`
- `module/v1/ff/NodeRed/+/order`
- `fts/v1/ff/+/state`
- `fts/v1/ff/+/connection`
- `fts/v1/ff/+/order`

NFC / Universal-ID is taken from **APS payloads that exist in session logs** (Replay + Live):

- CCU `workpieceId` (often the NFC tag)
- Module `actionState.result` on `RGB_NFC` / `PICK` / `DROP`
- FTS `load[].loadId` (one event row per loaded NFC)

`osf/workpiece/intake` is subscribed live (RPi intake-bridge) and should also appear in **new** session recordings (and patched reference logs via `scripts/patch_session_intake_events.py`). Replay does **not** need a local bridge — OSF-UI / Grafana can use the facade lines in the log; APS fields remain available for station correlation.

### Sensor topics

- `/j1/txt/1/i/bme680`
- `/j1/txt/1/i/ldr`
- `osf/arduino/+/+/+` (current OSF/DR-18 compatible)
- optional compatibility subscriptions:
  - `osf/+/sensor/+`
  - `osf/+/sensor/+/+`

### Excluded

- `/j1/txt/1/i/cam` (excluded by default; configurable via `ENABLE_CAMERA_TOPIC`)

## Data model

Core tables:

- `shopfloor_event`
- `shopfloor_order` (STORAGE + PRODUCTION via `order_type`; upsert from `ccu/order/response|active`, completed only for known `orderId`s — not the CCU completed history dump)
- `production_step`
- `workpiece`
- `env_sensor_snapshot` (UC-02 Umwelt-Topf; generic metric model)
- `mqtt_raw_message` (retention-limited)
- `replay_session_ingest` (local replay session-gate)

### Generic sensor model

`env_sensor_snapshot` is metric-oriented:

- `source` (`arduino`, `txt`, `module`)
- `station_id`
- `sensor_type`
- `metric_name`
- `value_numeric` / `value_text`
- `unit`
- `reason` (`EVENT`, `INTERVAL`, `THRESHOLD`)

This keeps schema stable when adding new sensor types (MPU, current, voltage, etc.).

Routine `INTERVAL` snapshots: **5 s while `ccu/order/active` is non-empty**, **60 s when idle**. Warn/alarm payloads (`vibrationLevel` yellow/red, `flameDetected`, `gasLevel >= 1`, plus explicit `warn`/`alarm`) are always stored as `THRESHOLD`.

## Retention

- Documented in `db/mssql/004_retention_note.sql` (no Timescale)
  - `mqtt_raw_message`: 14 days (service cleanup)
  - `env_sensor_snapshot`: 365 days (ops / SQL Agent on `.201`)

## Backup and restore

Use SQL Server backup tools against DB `osf_edge` (local Compose or `.201`).

## Local test framework

Persistence service has local unit tests for parser and sensor persistence policy.

```bash
cd services/persistence-service
npm install
npm run test
```

### Test scope (initial)

- camera topic ignore behavior
- order normalization (`ccu/order/completed`)
- Arduino metric normalization (generic key-value snapshots)
- sensor persistence policy (`EVENT`, `THRESHOLD`, `INTERVAL`)

## Local smoke test with Replay-Station

Yes, full local testing is possible in replay mode before any edge/rpi deployment.

Goal:

- run broker + persistence stack locally
- replay existing session logs (including Arduino topics in newer sessions)
- verify inserts in SQL Server and panels in Grafana

### 1) Start local Mosquitto

Use your existing local broker setup (default: `localhost:1883`).

Quick check:

```bash
mosquitto_sub -h localhost -p 1883 -t '#' -v
```

### 2) Switch stack to REPLAY profile

In `osf-edge-persistence/`:

```bash
cp env.replay .env
```

(`host.docker.internal` lets containers reach the host broker from Docker on macOS.)

### 3) Start persistence stack

```bash
cd osf-edge-persistence
docker compose up -d
```

Optional log tail:

```bash
docker logs -f osf-edge-persistence-service
```

### 4) Start Replay-Station

In project root:

```bash
streamlit run session_manager/app.py
```

In Replay-Station:

- choose a session from `data/osf-data/sessions/`
- prefer newer recordings that already include `osf/arduino/...` topics **and unique NFC tags** (Aug 2026 T&T set)
- run replay against local broker (`localhost:1883`)
- Expect `osf/workpiece/intake` in Replay when the session log contains it (patched references / new recordings with Bridge live)

Different sessions with **different NFC ids** may accumulate in the local DB. Reset is **manual only** (not on every replay). The same session **filename** is not re-persisted after a successful run (session-gate) until full truncate clears `replay_session_ingest`.

```bash
# clean slate (also clears replay_session_ingest)
bash osf-edge-persistence/scripts/reset-replay-db.sh
# MSSQL Option B:
bash osf-edge-persistence/scripts/reset-replay-db.sh --dialect mssql

# or drop one repeated NFC (session-gate list unchanged)
bash osf-edge-persistence/scripts/reset-replay-db.sh --nfc 92e0ad91595f63
```

### 5) Verify data arrival in SQL Server

```bash
docker exec -it osf-edge-mssql /opt/mssql-tools18/bin/sqlcmd -S localhost -U osf_edge -P 'OsfEdge_App9#' -C -d osf_edge \
  -Q "SELECT TOP 20 workpiece_id, COUNT(*) AS n FROM dbo.shopfloor_event WHERE workpiece_id IS NOT NULL GROUP BY workpiece_id ORDER BY n DESC;"
docker exec -it osf-edge-mssql /opt/mssql-tools18/bin/sqlcmd -S localhost -U osf_edge -P 'OsfEdge_App9#' -C -d osf_edge \
  -Q "SELECT COUNT(*) AS sensor_rows FROM dbo.env_sensor_snapshot;"
```

Expected:

- `shopfloor_event` grows with CCU/module/FTS topics
- `workpiece_id` is filled from NFC on RGB_NFC / FTS load / CCU orders
- `env_sensor_snapshot` grows with TXT + Arduino metrics
- no camera payload flood by default (`/j1/txt/1/i/cam` excluded)
- `osf/workpiece/intake` rows when the log (or live bridge) provides them

### 5b) Sensor values around Ist events (SQL, no Grafana)

Query-time as-of join: last `env_sensor_snapshot` per metric at each Ist event (same FINISHED filter as Workpiece Trace). Does **not** write `related_event_id`. Window default is 30s (active sensor INTERVAL is 5s; idle 60s).  
`scripts/sensor-around-ist.sh` / `db/queries/sensor_around_*.sql` are **legacy Postgres** (not wired to MSSQL yet) — use Grafana sensor panels until ported.

```bash
npm run persistence:sensor-around-ist
npm run persistence:sensor-around-ist -- --nfc 92e0ad91595f63 --anchors
npm run persistence:sensor-around-ist -- --long --limit 50
```

SQL: `osf-edge-persistence/db/queries/sensor_around_ist_event.sql`

### 6) Verify in Grafana

- open `http://localhost:3000`
- check folder `OSF Edge Persistence`
- dashboards should show replayed data:
  - Systemstatus — **MQTT Topics (raw)** (counts aus `mqtt_raw_message`, folgt dem Zeitfenster)
  - Auftraege
  - **OSF Edge Home** (`osf-home`) — Demo-Einstieg (KPIs + Links)
  - Workpiece Trace — filter **NFC** / **Color** (All or multi); table follows the time picker
  - **FTS / AGV** (`osf-fts`) — filter **FTS serial**; battery, loads, actions, last node
  - Sensor Snapshots
  - Modul-/FTS-Zustaende

### 7) Stop local test setup

```bash
cd osf-edge-persistence
docker compose down
```

Replay-Station can be stopped via Ctrl+C.

### 8) Switch back to default LIVE profile

```bash
cd osf-edge-persistence
cp env.live .env
docker compose up -d
```

## Notes

- Service is read-only: no MQTT publish commands are sent.
- Idempotency is implemented via deterministic `dedup_key` hashes and DB uniqueness constraints.
