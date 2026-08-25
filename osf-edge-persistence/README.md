# OSF Edge Persistence Stack

Docker-based persistence and dashboard stack for OSF:

- PostgreSQL + TimescaleDB
- Grafana
- Read-only MQTT persistence service

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
- Postgres: `localhost:5432`

## Option B — local SQL Server (Dev, parallel to Postgres)

Target on DSP `.201` is **SQL Server**, not Postgres. Until Persistence/Grafana are ported, run a local MSSQL container **alongside** the existing Timescale stack:

```bash
# ensure MSSQL_* vars are in .env (see env.live / .env.example)
docker compose --profile mssql up -d mssql
bash scripts/mssql-smoke.sh
```

- Host port: `localhost:1433` (override `MSSQL_EXTERNAL_PORT`)
- SA password: `MSSQL_SA_PASSWORD` (must meet SQL Server complexity)
- Apple Silicon: image runs as `linux/amd64` (Docker Desktop Rosetta)
- Schema (DB `osf_edge`): `bash scripts/mssql-init-schema.sh` — T-SQL under `db/mssql/`
- Postgres/Grafana/Persistence stay on the default compose path until Persistence → MSSQL Häppchen

Stop only MSSQL:

```bash
docker compose --profile mssql stop mssql
```

## Stop

```bash
docker compose down
```

# To also remove the mssql profile container:
# docker compose --profile mssql down

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

`osf/workpiece/intake` is subscribed as a **live-only** bonus (RPi intake-bridge). Session recordings do not contain it. Replay does **not** need a local bridge — Grafana correlation uses the APS fields above.

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
- `production_order`
- `production_step`
- `workpiece`
- `sensor_snapshot` (generic metric model)
- `mqtt_raw_message` (retention-limited)

### Generic sensor model

`sensor_snapshot` is metric-oriented:

- `source` (`arduino`, `txt`, `module`)
- `station_id`
- `sensor_type`
- `metric_name`
- `value_numeric` / `value_text`
- `unit`
- `reason` (`EVENT`, `INTERVAL`, `THRESHOLD`)

This keeps schema stable when adding new sensor types (MPU, current, voltage, etc.).

Routine `INTERVAL` snapshots: **5 s while `ccu/order/active` is non-empty**, **60 s when idle**. Warn/alarm payloads (`vibrationLevel` yellow/red, `flameDetected`, `gasLevel >= 1`, plus explicit `warn`/`alarm`) are always stored as `THRESHOLD`. That is far below Timescale capacity (on the order of 10k snapshot rows per production hour; idle ~800/h). `mqtt_raw_message` remains the denser 14-day MQTT archive.

## Retention

- Timescale policies are created in `db/init/004_retention.sql`
- Default:
  - `mqtt_raw_message`: 14 days
  - `sensor_snapshot`: 365 days

Adjust SQL policy or env values for your deployment profile.

## Backup and restore

### Backup (Postgres)

```bash
docker exec -t osf-edge-postgres pg_dump -U osf -d osf > backup_osf.sql
```

### Restore

```bash
cat backup_osf.sql | docker exec -i osf-edge-postgres psql -U osf -d osf
```

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
- verify inserts in Postgres and panels in Grafana

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
- **Do not** expect `osf/workpiece/intake` in Replay (bridge runs on the RPi, not during session playback)

Different sessions with **different NFC ids** may accumulate in the local DB. Reset is **manual only** (not on every replay):

```bash
# clean slate
bash osf-edge-persistence/scripts/reset-replay-db.sh

# or drop one repeated NFC after replaying the same session twice
bash osf-edge-persistence/scripts/reset-replay-db.sh --nfc 92e0ad91595f63
```

### 5) Verify data arrival in Postgres

```bash
docker exec -it osf-edge-postgres psql -U osf -d osf -c "SELECT workpiece_id, count(*) FROM shopfloor_event WHERE workpiece_id IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 20;"
docker exec -it osf-edge-postgres psql -U osf -d osf -c "SELECT count(*) FROM sensor_snapshot;"
docker exec -it osf-edge-postgres psql -U osf -d osf -c "SELECT source, sensor_type, metric_name, count(*) FROM sensor_snapshot GROUP BY 1,2,3 ORDER BY 4 DESC LIMIT 20;"
```

Expected:

- `shopfloor_event` grows with CCU/module/FTS topics
- `workpiece_id` is filled from NFC on RGB_NFC / FTS load / CCU orders
- `sensor_snapshot` grows with TXT + Arduino metrics
- no camera payload flood by default (`/j1/txt/1/i/cam` excluded)
- `osf/workpiece/intake` rows only if a live bridge is publishing (not in Replay)

### 5b) Sensor values around Ist events (SQL, no Grafana)

Query-time as-of join: last `sensor_snapshot` per metric at each Ist event (same FINISHED filter as Workpiece Trace). Does **not** write `related_event_id`. Window default is 30s (active sensor INTERVAL is 5s; idle 60s).

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
  - Workpiece Trace — filter **NFC** / **Color** (All or multi); table follows the time picker
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
