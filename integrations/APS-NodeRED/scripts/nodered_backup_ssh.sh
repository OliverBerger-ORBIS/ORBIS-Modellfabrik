#!/usr/bin/env bash
set -euo pipefail

# Node-RED Backup via SSH
# Verwendung: HOST=ff22@192.168.0.100 ./nodered_backup_ssh.sh
# Oder mit SSH-Key: HOST=ff22@192.168.0.100 SSH_KEY=~/.ssh/nodered_key ./nodered_backup_ssh.sh

HOST="${HOST:?HOST required (e.g. ff22@192.168.0.100)}"
DEST="${DEST:-integrations/APS-NodeRED/backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SSH_KEY="${SSH_KEY:-}"

# SSH-Optionen vorbereiten
SSH_OPTS=()
if [ -n "$SSH_KEY" ] && [ -f "$SSH_KEY" ]; then
    SSH_OPTS+=(-i "$SSH_KEY")
    echo "🔑 Verwende SSH-Key: $SSH_KEY"
else
    echo "⚠️  Kein SSH-Key angegeben - Passwort-Authentifizierung erforderlich"
fi

echo "🔄 Erstelle Node-RED Backup für $HOST..."
mkdir -p "$DEST/$STAMP"

# Backup der Node-RED Konfigurationsdateien
echo "📁 Lade flows.json..."
scp "${SSH_OPTS[@]}" "$HOST:~/.node-red/flows.json" "$DEST/$STAMP/flows.json" || {
    echo "⚠️  flows.json nicht gefunden - möglicherweise noch keine Flows vorhanden"
    touch "$DEST/$STAMP/flows.json"
}

echo "🔐 Lade flows_cred.json..."
scp "${SSH_OPTS[@]}" "$HOST:~/.node-red/flows_cred.json" "$DEST/$STAMP/flows_cred.json" || {
    echo "⚠️  flows_cred.json nicht gefunden - keine Credentials vorhanden"
    touch "$DEST/$STAMP/flows_cred.json"
}

echo "⚙️  Lade settings.js..."
scp "${SSH_OPTS[@]}" "$HOST:~/.node-red/settings.js" "$DEST/$STAMP/settings.js" || {
    echo "⚠️  settings.js nicht gefunden - Standard-Settings werden verwendet"
    touch "$DEST/$STAMP/settings.js"
}

# Zusätzliche Node-RED Dateien (falls vorhanden)
echo "📦 Lade package.json..."
scp "${SSH_OPTS[@]}" "$HOST:~/.node-red/package.json" "$DEST/$STAMP/package.json" || {
    echo "ℹ️  package.json nicht gefunden - keine Custom Nodes"
}

echo "📋 Lade lib/ Verzeichnis..."
scp -r "${SSH_OPTS[@]}" "$HOST:~/.node-red/lib/" "$DEST/$STAMP/lib/" || {
    echo "ℹ️  lib/ Verzeichnis nicht gefunden"
}

# Backup-Info erstellen
cat > "$DEST/$STAMP/backup_info.txt" << EOF
Node-RED Backup erstellt: $(date)
Host: $HOST
Backup-Verzeichnis: $DEST/$STAMP

Enthaltene Dateien:
- flows.json: Node-RED Flow-Definitionen
- flows_cred.json: Verschlüsselte Credentials (falls vorhanden)
- settings.js: Node-RED Einstellungen
- package.json: Custom Node Dependencies (falls vorhanden)
- lib/: Custom Libraries (falls vorhanden)

Wiederherstellung:
HOST=$HOST SRC=$DEST/$STAMP ./nodered_restore_ssh.sh
EOF

echo "✅ Backup erfolgreich erstellt: $DEST/$STAMP"
echo "📄 Backup-Info: $DEST/$STAMP/backup_info.txt"
