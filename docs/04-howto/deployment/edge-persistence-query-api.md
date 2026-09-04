# Edge Persistence – Query API (V1)

**Stand:** 2026-09-04 · **Bezug:** [UC-01 Lückenanalyse](../../07-analysis/uc01-tt-persistence-gap-2026-09.md) · [DR-28](../../03-decision-records/28-edge-persistence-stack-and-metrics-model.md)

Read-only HTTP auf dem **Persistence-Container**. **UC-01-DB-Variante lokal gegen Replay-SQL entwickeln**, nicht gegen `.201`. Live-VE erst für Abnahme.

MQTT-T&T in der OSF-UI bleibt parallel (gleicher Replay-Broker möglich).

| Umgebung | Basis-URL | Wann |
|----------|-----------|------|
| **Lokal (Compose, `env.replay`)** | `http://localhost:3081` | **Dev / Tests** |
| DSP-VE `.201` | `http://192.168.0.201:3081` | Live-Abnahme, Uni-M |

Port im Container immer **3081**; Host-Mapping `QUERY_API_EXTERNAL_PORT` (Default 3081).

---

## Dev-Loop: lokale DB + Dual-AGV-Replay

`PERSISTENCE_MODE=replay` schreibt **nur** auf lokale DB-Hosts (nicht `.201`). Session-Gate: dieselbe Log-Datei wird nach `commit` nicht erneut persistiert, bis `reset-replay-db.sh`.

**Nicht** `scripts/replay-sessions.ts` verwenden — das geht in den Mock-Adapter, nicht auf Mosquitto, **kein** `osf/persistence/replay/session`.

### 1) Stack

Lokaler MQTT-Broker `:1883`. Dann:

```bash
cd osf-edge-persistence
cp env.replay .env
docker compose up -d --build
curl -sS http://localhost:3081/v1/health
```

Schema falls nötig: `bash scripts/mssql-init-schema.sh` · `bash scripts/mssql-create-app-user.sh`

Saubere Spur (löscht auch das Session-Gate):

```bash
bash scripts/reset-replay-db.sh --yes
```

### 2) Replay (Session Manager)

Projekt-Root, `.venv`:

```bash
source .venv/bin/activate
streamlit run session_manager/app.py
```

- Broker **localhost:1883**
- Session **`storage-wbr-dual-agv-rwb_20260903_094319`** (Referenz Dual-AGV; NFC `513601ee741a12`, `b8b3588da7d8f4`, `aaf21ca1ef1d86` — [INVENTORY](../../../data/osf-data/sessions/INVENTORY.md))
- Play einmal durch (begin/commit für Persistence)

Optional parallel: OSF-UI Replay auf denselben Broker → MQTT-T&T als Vergleich, nicht als Datenquelle der API.

### 3) Query-API prüfen

```bash
bash osf-edge-persistence/scripts/query-api-check-replay.sh --require
```

Ohne `--require` nur Anzeige. Andere NFCs: `--nfc <id>` (wiederholbar).

Grafana `http://localhost:3000` bleibt der visuelle Ingest-Beweis; die API ist der Vertrag für UC-01-B.

---

## Endpunkte

| Methode | Pfad | Antwort |
|---------|------|---------|
| GET | `/health` oder `/v1/health` | `{ "ok": true, "service": "osf-edge-query" }` |
| GET | `/v1/workpieces?from=&to=&limit=` | `{ "items": [ { nfc, color, currentState, lastLocation, firstSeenAt, lastSeenAt } ] }` |
| GET | `/v1/workpieces/{nfc}/timeline?from=&to=&limit=` | `{ "nfc", "events": [ TimelineEventDto ] }` |

Query-Parameter `from` / `to`: ISO-8601. `limit` Default 500, Max 2000.

**Timeline-Filter (V1):** `WORKPIECE_INTAKE` **oder** (`action_state = FINISHED` und Topic `module/%` bzw. `fts/%`), Join `shopfloor_order.order_type`. Kein Sticky, keine Mitfahrt, kein ENV, kein Quality-Bild.

CORS Default `*` (`QUERY_API_CORS_ORIGIN`).

---

## Beispiele

```bash
curl -sS http://localhost:3081/v1/health
curl -sS 'http://localhost:3081/v1/workpieces?limit=20'
curl -sS 'http://localhost:3081/v1/workpieces/92e0ad91595f63/timeline'
```

Live FT-LAN:

```bash
curl -sS http://192.168.0.201:3081/v1/health
```

Nach Compose-Änderung Persistence neu bauen:

```bash
cd osf-edge-persistence
docker compose up -d --build persistence-service
# VE:
# docker compose -f docker-compose.dsp.yml up -d --build persistence-service
```

---

## Env

| Variable | Default | Bedeutung |
|----------|---------|-----------|
| `QUERY_API_ENABLED` | `true` | HTTP-Listener |
| `QUERY_API_PORT` | `3081` | Listen-Port im Container (Compose setzt fest 3081) |
| `QUERY_API_CORS_ORIGIN` | `*` | CORS |
| `QUERY_API_EXTERNAL_PORT` | `3081` | Host-Port |

Ingest-Pfad (MQTT → SQL) ist unabhängig; `QUERY_API_ENABLED=false` schaltet nur HTTP ab.
