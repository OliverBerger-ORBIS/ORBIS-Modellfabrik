#!/usr/bin/env bash
# Mirror all canonical SVGs from src → public (technical duplicate for serve/deploy).
# Covers: brand, business, dsp, shopfloor, ui, use-cases — entire src/assets/svg/ tree.
#
# Source of truth: osf/apps/osf-ui/src/assets/svg/
# Target:          osf/apps/osf-ui/public/assets/svg/
#
# rsync WITHOUT --delete: files that exist only under public/ (legacy) are kept.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/osf/apps/osf-ui/src/assets/svg"
DST="$ROOT/osf/apps/osf-ui/public/assets/svg"
mkdir -p "$DST"
rsync -a --exclude='.DS_Store' "$SRC/" "$DST/"
echo "Synced SVG tree (add/update only): $SRC/ -> $DST/"
