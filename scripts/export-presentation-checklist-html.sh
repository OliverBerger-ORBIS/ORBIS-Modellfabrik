#!/usr/bin/env bash
# Export presentation setup checklist Markdown to standalone HTML (print-friendly).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="$ROOT/docs/04-howto/presentation/windows-desktops-teams-obs-setup-checklist.md"
TARGET="$ROOT/docs/04-howto/presentation/windows-desktops-teams-obs-setup-checklist.html"

if [[ ! -f "$SOURCE" ]]; then
  echo "Missing source: $SOURCE" >&2
  exit 1
fi

python3 "$ROOT/scripts/export_markdown_html.py" \
  "$SOURCE" \
  "$TARGET" \
  "bash scripts/export-presentation-checklist-html.sh"

echo "Open in browser: file://$TARGET"
echo "Print: Cmd+P in browser (footer hidden in print view)."
