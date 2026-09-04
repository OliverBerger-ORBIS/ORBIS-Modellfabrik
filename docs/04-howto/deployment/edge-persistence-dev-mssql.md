# Edge Persistence – Dev SQL Server (Option B)

**Stand:** 25.08.2026 · **Bezug:** [DR-28](../../03-decision-records/28-edge-persistence-stack-and-metrics-model.md) · [DSP-Edge wo läuft was](./dsp-edge-osf-persistence.md) · Stack-README [`osf-edge-persistence/README.md`](../../../osf-edge-persistence/README.md)

Lokaler Dev-/Replay-Stack auf dem Mac: **derselbe Dialekt** wie Prod auf VE `.201` (Microsoft SQL Server). Postgres/Timescale ist aus dem aktiven Compose entfernt.

---

## Ports & Credentials (Dev)

| Dienst | Host | Hinweis |
|--------|------|---------|
| SQL Server | `localhost:1433` | Container `osf-edge-mssql` (Apple Silicon: `linux/amd64` / Rosetta) |
| Grafana | `http://localhost:3000` | Default-Home: **OSF Edge Home** (`osf-home`); Anonymous Admin, Login-Formular aus |
| Query API | `http://localhost:3081` | V1 UC-01 Read: `/v1/workpieces`, `/v1/workpieces/{nfc}/timeline` — [How-to](./edge-persistence-query-api.md) |
| Persistence | Compose-Service | MQTT laut `env.replay` / `env.live` |

| DB / User | Wert (Dev) |
|-----------|------------|
| Database | `osf_edge` |
| App-User | `osf_edge` / `OsfEdge_App9#` (kein `!` — Shell/sqlcmd) |
| SA | aus `MSSQL_SA_PASSWORD` in `env.*` |

---

## Einmalig / nach Schema-Änderung

```bash
cd osf-edge-persistence
cp env.replay .env          # Replay lokal; Live FT-LAN: env.live
docker compose up -d
bash scripts/mssql-smoke.sh
bash scripts/mssql-init-schema.sh
bash scripts/mssql-create-app-user.sh
```

Smoke ohne MQTT:

```bash
MSSQL_HOST=localhost MSSQL_PASSWORD='OsfEdge_App9#' npx tsx scripts/mssql-persist-smoke.ts
```

---

## Replay-Alltag

1. Session Manager → lokale Broker + Timeshift; Persistence `env.replay`.  
2. Session-Gate: gleiche Log-Datei wird nicht erneut persistiert bis Reset.  
3. DB leeren (inkl. `replay_session_ingest`):

```bash
bash scripts/reset-replay-db.sh --yes
# optional nur eine NFC:
bash scripts/reset-replay-db.sh --nfc <nfc> --yes
```

4. Grafana: Home → Trace / Orders / Sensors / FTS. Shared Cursor: Dashboard **Cursor sync** / nach Reload (bei Sensoren schon `graphTooltip: 2`).

Details: README Abschnitte Runtime modes, Reset, Verify.

---

## Was wohin gehört

| Thema | Dokument |
|-------|----------|
| Hosts RPi / `.201` / Mac, Inventar VE | [dsp-edge-osf-persistence.md](./dsp-edge-osf-persistence.md) |
| Live FT-LAN / MQTT-Tunnel | [edge-persistence-live-ft-lan.md](./edge-persistence-live-ft-lan.md) |
| Topics, Schema, Dashboards, Retention | [`osf-edge-persistence/README.md`](../../../osf-edge-persistence/README.md) |
| Architektur-Entscheidung MSSQL | [DR-28](../../03-decision-records/28-edge-persistence-stack-and-metrics-model.md) |

**Nicht hier:** Deploy Persistence+Grafana auf `.201` (eigene Sprint-Tasks / dsp-edge Phasen).
