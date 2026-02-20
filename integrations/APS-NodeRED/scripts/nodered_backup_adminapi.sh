#!/usr/bin/env bash
set -euo pipefail

# Node-RED Backup via Admin API
# Verwendung: BASE=http://aps-host:1880 TOKEN=... ./nodered_backup_adminapi.sh

BASE="${BASE:?BASE required (e.g. http://aps-host:1880)}"
DEST="${DEST:-integrations/APS-NodeRED/backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TOKEN="${TOKEN:-}"

echo "🔄 Erstelle Node-RED Backup via Admin API..."
echo "🌐 Node-RED: $BASE"

mkdir -p "$DEST/$STAMP"

# Auth-Header vorbereiten
authHeader=(-H "Content-Type: application/json")
if [ -n "$TOKEN" ]; then
    authHeader+=(-H "Authorization: Bearer $TOKEN")
    echo "🔐 Verwende Bearer Token"
elif [ -n "${USER:-}" ] && [ -n "${PASS:-}" ]; then
    authHeader+=(-u "$USER:$PASS")
    echo "🔐 Verwende Basic Auth: $USER"
else
    echo "⚠️  Keine Authentifizierung - funktioniert nur bei deaktivierter Auth"
fi

# Teste Verbindung
echo "🔍 Teste Verbindung zu Node-RED..."
if ! curl -sf "${authHeader[@]}" "$BASE/flows" >/dev/null 2>&1; then
    echo "❌ Verbindung zu Node-RED fehlgeschlagen"
    echo "💡 Prüfe:"
    echo "   - Node-RED läuft auf $BASE"
    echo "   - Admin API ist aktiviert"
    echo "   - Authentifizierung ist korrekt"
    exit 1
fi

# Backup flows.json
echo "📁 Lade flows.json..."
curl -sf "${authHeader[@]}" "$BASE/flows" -o "$DEST/$STAMP/flows.json" || {
    echo "❌ Fehler beim Laden der Flows"
    exit 1
}

# Prüfe ob flows.json gültig ist
if [ ! -s "$DEST/$STAMP/flows.json" ]; then
    echo "⚠️  flows.json ist leer - möglicherweise keine Flows vorhanden"
    echo "[]" > "$DEST/$STAMP/flows.json"
fi

# Backup settings.js (falls verfügbar)
echo "⚙️  Lade settings.js..."
curl -sf "${authHeader[@]}" "$BASE/settings" -o "$DEST/$STAMP/settings.json" || {
    echo "⚠️  settings.js nicht über API verfügbar - überspringe"
    touch "$DEST/$STAMP/settings.json"
}

# Backup package.json (falls verfügbar)
echo "📦 Lade package.json..."
curl -sf "${authHeader[@]}" "$BASE/nodes" -o "$DEST/$STAMP/nodes.json" || {
    echo "⚠️  nodes.json nicht über API verfügbar - überspringe"
    touch "$DEST/$STAMP/nodes.json"
}

# Backup-Info erstellen
cat > "$DEST/$STAMP/backup_info.txt" << EOF
Node-RED Backup erstellt: $(date)
Node-RED URL: $BASE
Backup-Methode: Admin API
Backup-Verzeichnis: $DEST/$STAMP

Enthaltene Dateien:
- flows.json: Node-RED Flow-Definitionen (via Admin API)
- settings.json: Node-RED Einstellungen (falls verfügbar)
- nodes.json: Installierte Nodes (falls verfügbar)

WICHTIG: flows_cred.json ist NICHT über Admin API verfügbar!
Für vollständige Wiederherstellung SSH-Restore verwenden.

Wiederherstellung:
BASE=$BASE TOKEN=$TOKEN FILE=$DEST/$STAMP/flows.json ./nodered_restore_adminapi.sh
EOF

echo "✅ Backup erfolgreich erstellt: $DEST/$STAMP"
echo "📄 Backup-Info: $DEST/$STAMP/backup_info.txt"
echo "⚠️  HINWEIS: flows_cred.json ist nicht über Admin API verfügbar!"
