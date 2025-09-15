#!/usr/bin/env bash
set -euo pipefail

# Node-RED Restore via Admin API
# Verwendung: BASE=http://aps-host:1880 FILE=path/to/flows.json TOKEN=... ./nodered_restore_adminapi.sh

BASE="${BASE:?BASE required (e.g. http://aps-host:1880)}"
FILE="${FILE:?FILE required (path to flows.json)}"
TOKEN="${TOKEN:-}"

echo "🔄 Stelle Node-RED Flows via Admin API wieder her..."
echo "🌐 Node-RED: $BASE"
echo "📁 Datei: $FILE"

# Prüfe ob Datei existiert
if [ ! -f "$FILE" ]; then
    echo "❌ Datei nicht gefunden: $FILE"
    exit 1
fi

# Prüfe ob Datei gültiges JSON ist
if ! jq empty "$FILE" 2>/dev/null; then
    echo "❌ Datei ist kein gültiges JSON: $FILE"
    exit 1
fi

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

# Erstelle Backup der aktuellen Flows
echo "💾 Erstelle Backup der aktuellen Flows..."
CURRENT_BACKUP="$(date -u +%Y%m%dT%H%M%SZ)_current"
mkdir -p "integrations/node_red/backups/$CURRENT_BACKUP"
curl -sf "${authHeader[@]}" "$BASE/flows" -o "integrations/node_red/backups/$CURRENT_BACKUP/flows.json" || {
    echo "⚠️  Fehler beim Backup der aktuellen Flows - fahre trotzdem fort"
}

# Restore der Flows
echo "📤 Übertrage Flows..."
if curl -sf -X POST "${authHeader[@]}" "$BASE/flows" --data-binary "@$FILE"; then
    echo "✅ Flows erfolgreich übertragen"
else
    echo "❌ Fehler beim Übertragen der Flows"
    exit 1
fi

# Prüfe ob Flows korrekt geladen wurden
echo "🔍 Prüfe übertragene Flows..."
sleep 2
if curl -sf "${authHeader[@]}" "$BASE/flows" | jq -e 'length > 0' >/dev/null 2>&1; then
    echo "✅ Flows erfolgreich geladen"
else
    echo "⚠️  Keine Flows gefunden - möglicherweise leer oder Fehler"
fi

# Backup-Info erstellen
cat > "integrations/node_red/backups/$CURRENT_BACKUP/backup_info.txt" << EOF
Node-RED Restore Backup erstellt: $(date)
Node-RED URL: $BASE
Restore-Datei: $FILE
Backup-Verzeichnis: integrations/node_red/backups/$CURRENT_BACKUP

WICHTIG: 
- Nur flows.json wurde über Admin API wiederhergestellt
- flows_cred.json (Credentials) wurde NICHT übertragen
- Für vollständige Wiederherstellung SSH-Restore verwenden

Wiederherstellung:
BASE=$BASE FILE=integrations/node_red/backups/$CURRENT_BACKUP/flows.json TOKEN=$TOKEN ./nodered_restore_adminapi.sh
EOF

echo ""
echo "✅ Restore abgeschlossen!"
echo "💾 Aktuelle Flows gesichert in: integrations/node_red/backups/$CURRENT_BACKUP/"
echo "⚠️  HINWEIS: flows_cred.json (Credentials) wurde NICHT übertragen!"
echo "🌐 Node-RED UI: $BASE"
