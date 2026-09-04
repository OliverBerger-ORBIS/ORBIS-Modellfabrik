#!/usr/bin/env bash
# Check V1 Query API against local Replay DB (no MQTT, no .201).
# After Session-Manager replay of a dual-AGV session, e.g.:
#   bash osf-edge-persistence/scripts/query-api-check-replay.sh
#   bash osf-edge-persistence/scripts/query-api-check-replay.sh --require
#
# Default NFC list = INVENTORY reference storage-wbr-dual-agv-rwb_20260903_094319
set -euo pipefail

BASE="${QUERY_API_BASE:-http://localhost:3081}"
REQUIRE=0
NFCS=()

usage() {
  cat <<'EOF'
Usage: bash osf-edge-persistence/scripts/query-api-check-replay.sh [options]

  --base URL     Query API (default http://localhost:3081)
  --nfc ID       Extra NFC (repeatable). If none given, dual-AGV reference NFCs.
  --require      Exit 1 when a listed NFC has zero timeline events
  -h, --help

Does not replay a session and does not truncate the DB.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base)
      BASE="${2:?}"
      shift 2
      ;;
    --nfc)
      NFCS+=("${2:?}")
      shift 2
      ;;
    --require)
      REQUIRE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ${#NFCS[@]} -eq 0 ]]; then
  # STORAGE W/B/R — docs/data/osf-data/sessions/INVENTORY.md (storage-wbr-dual-agv-rwb_20260903_094319)
  NFCS=(513601ee741a12 b8b3588da7d8f4 aaf21ca1ef1d86)
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 required to parse JSON" >&2
  exit 1
fi

health="$(curl -fsS "${BASE}/v1/health" || true)"
if [[ -z "$health" ]]; then
  echo "Query API not reachable at ${BASE} (is persistence-service up with env.replay?)" >&2
  exit 1
fi
echo "health: ${health}"

list_json="$(curl -fsS "${BASE}/v1/workpieces?limit=200")"
python3 - "$list_json" <<'PY'
import json, sys
data = json.loads(sys.argv[1])
items = data.get("items") or []
print(f"workpieces: {len(items)}")
for row in items[:20]:
    print(f"  {row.get('nfc')}  color={row.get('color')}  last={row.get('lastSeenAt')}")
if len(items) > 20:
    print(f"  … {len(items) - 20} more")
PY

fail=0
for nfc in "${NFCS[@]}"; do
  tl_json="$(curl -fsS "${BASE}/v1/workpieces/${nfc}/timeline?limit=2000")"
  python3 - "$nfc" "$tl_json" "$REQUIRE" <<'PY' || fail=1
import json, sys
nfc, raw, require = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
data = json.loads(raw)
events = data.get("events") or []
stations = sorted({e.get("station") or "?" for e in events})
sources = sorted({e.get("eventSource") or "?" for e in events})
print(f"timeline {nfc}: {len(events)} events  stations={stations}  sources={sources}")
if require and len(events) == 0:
    sys.exit(1)
PY
done

if [[ "$fail" -ne 0 ]]; then
  echo "One or more NFCs have an empty V1 timeline (replay not ingested, session-gate skip, or FINISHED filter)." >&2
  exit 1
fi
