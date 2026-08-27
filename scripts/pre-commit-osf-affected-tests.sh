#!/usr/bin/env bash
# Pre-commit B2: run Jest only for Nx projects affected by staged files.
# Full suite + coverage gates stay on CI (`npm run test:ci`).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

FILES="$(git diff --cached --name-only || true)"
if [[ -z "${FILES}" ]]; then
  echo "OSF Tests (affected): no staged files — skip"
  exit 0
fi

# Nx --files accepts comma- or space-delimited paths
FILE_LIST="$(printf '%s\n' "${FILES}" | paste -sd, -)"

export BASELINE_BROWSER_MAPPING_IGNORE_OLD_DATA=true

echo "OSF Tests (affected): nx affected -t test --files=<staged>"
npx nx affected -t test --files="${FILE_LIST}"
