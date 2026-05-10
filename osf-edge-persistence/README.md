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

## Stop

```bash
docker compose down
```

## Topics

### Process / shopfloor

- `ccu/order/active`
- `ccu/order/completed`
- `ccu/state/stock`
- `ccu/state/layout`
- `ccu/state/config`
- `ccu/state/flows`
- `ccu/pairing/state`
- `module/v1/ff/+/state`
- `module/v1/ff/+/connection`
- `fts/v1/ff/+/state`
- `fts/v1/ff/+/connection`

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
- prefer newer recordings that already include `osf/arduino/...` topics
- run replay against local broker (`localhost:1883`)

### 5) Verify data arrival in Postgres

```bash
docker exec -it osf-edge-postgres psql -U osf -d osf -c "SELECT count(*) FROM shopfloor_event;"
docker exec -it osf-edge-postgres psql -U osf -d osf -c "SELECT count(*) FROM sensor_snapshot;"
docker exec -it osf-edge-postgres psql -U osf -d osf -c "SELECT source, sensor_type, metric_name, count(*) FROM sensor_snapshot GROUP BY 1,2,3 ORDER BY 4 DESC LIMIT 20;"
```

Expected:

- `shopfloor_event` grows with CCU/module/FTS topics
- `sensor_snapshot` grows with TXT + Arduino metrics
- no camera payload flood by default (`/j1/txt/1/i/cam` excluded)

### 6) Verify in Grafana

- open `http://localhost:3000`
- check folder `OSF Edge Persistence`
- dashboards should show replayed data:
  - Systemstatus
  - Auftraege
  - Workpiece Trace
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
