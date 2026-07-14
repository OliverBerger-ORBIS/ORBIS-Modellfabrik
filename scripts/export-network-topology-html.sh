#!/usr/bin/env bash
# Export network topology Markdown to a standalone HTML file (Mermaid via CDN).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="$ROOT/docs/04-howto/setup/orbis-shopfloor-network-topology.md"
TARGET="$ROOT/docs/04-howto/setup/orbis-shopfloor-network-topology.html"

if [[ ! -f "$SOURCE" ]]; then
  echo "Missing source: $SOURCE" >&2
  exit 1
fi

python3 "$ROOT/scripts/export_network_topology_html.py" "$SOURCE" "$TARGET"
echo "Open in browser: file://$TARGET"
echo "Share: attach HTML or host on internal file share (Mermaid needs CDN/internet once)."
