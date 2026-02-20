#!/usr/bin/env bash
set -euo pipefail

# Node-RED Restore via SSH
# Verwendung: HOST=ff22@192.168.0.100 SRC=integrations/APS-NodeRED/backups/20250915T090000Z ./nodered_restore_ssh.sh
# Oder mit SSH-Key: HOST=ff22@192.168.0.100 SRC=... SSH_KEY=~/.ssh/nodered_key ./nodered_restore_ssh.sh

HOST="${HOST:?HOST required (e.g. ff22@192.168.0.100)}"
SRC="${SRC:?SRC backup dir required (e.g. integrations/APS-NodeRED/backups/20250915T090000Z)}"
SSH_KEY="${SSH_KEY:-}"

# SSH-Optionen vorbereiten
SSH_OPTS=()
if [ -n "$SSH_KEY" ] && [ -f "$SSH_KEY" ]; then
    SSH_OPTS+=(-i "$SSH_KEY")
    echo "🔑 Verwende SSH-Key: $SSH_KEY"
else
    echo "⚠️  Kein SSH-Key angegeben - Passwort-Authentifizierung erforderlich"
fi

echo "🔄 Stelle Node-RED Konfiguration für $HOST wieder her..."
echo "📁 Quelle: $SRC"

# Prüfe ob Backup-Verzeichnis existiert
if [ ! -d "$SRC" ]; then
    echo "❌ Backup-Verzeichnis nicht gefunden: $SRC"
    exit 1
fi

# Prüfe ob Node-RED läuft
echo "🔍 Prüfe Node-RED Status..."
if ssh "${SSH_OPTS[@]}" "$HOST" "systemctl --user is-active nodered" >/dev/null 2>&1; then
    echo "⚠️  Node-RED läuft - wird nach Restore neu gestartet"
    NODERED_RUNNING=true
else
    echo "ℹ️  Node-RED läuft nicht"
    NODERED_RUNNING=false
fi

# Stoppe Node-RED falls es läuft
if [ "$NODERED_RUNNING" = true ]; then
    echo "⏹️  Stoppe Node-RED..."
    ssh "${SSH_OPTS[@]}" "$HOST" "systemctl --user stop nodered" || {
        echo "⚠️  Fehler beim Stoppen von Node-RED - fahre trotzdem fort"
    }
fi

# Erstelle Backup der aktuellen Konfiguration
echo "💾 Erstelle Backup der aktuellen Konfiguration..."
CURRENT_BACKUP="$(date -u +%Y%m%dT%H%M%SZ)_current"
ssh "${SSH_OPTS[@]}" "$HOST" "mkdir -p ~/.node-red/backup_$CURRENT_BACKUP"
ssh "${SSH_OPTS[@]}" "$HOST" "cp ~/.node-red/flows.json ~/.node-red/backup_$CURRENT_BACKUP/ 2>/dev/null || true"
ssh "${SSH_OPTS[@]}" "$HOST" "cp ~/.node-red/flows_cred.json ~/.node-red/backup_$CURRENT_BACKUP/ 2>/dev/null || true"
ssh "${SSH_OPTS[@]}" "$HOST" "cp ~/.node-red/settings.js ~/.node-red/backup_$CURRENT_BACKUP/ 2>/dev/null || true"

# Restore der Konfigurationsdateien
echo "📤 Übertrage flows.json..."
if [ -f "$SRC/flows.json" ] && [ -s "$SRC/flows.json" ]; then
    scp "${SSH_OPTS[@]}" "$SRC/flows.json" "$HOST:~/.node-red/flows.json"
    echo "✅ flows.json übertragen"
else
    echo "⚠️  flows.json nicht gefunden oder leer - überspringe"
fi

echo "🔐 Übertrage flows_cred.json..."
if [ -f "$SRC/flows_cred.json" ] && [ -s "$SRC/flows_cred.json" ]; then
    scp "${SSH_OPTS[@]}" "$SRC/flows_cred.json" "$HOST:~/.node-red/flows_cred.json"
    echo "✅ flows_cred.json übertragen"
else
    echo "⚠️  flows_cred.json nicht gefunden oder leer - überspringe"
fi

echo "⚙️  Übertrage settings.js..."
if [ -f "$SRC/settings.js" ] && [ -s "$SRC/settings.js" ]; then
    scp "${SSH_OPTS[@]}" "$SRC/settings.js" "$HOST:~/.node-red/settings.js"
    echo "✅ settings.js übertragen"
else
    echo "⚠️  settings.js nicht gefunden oder leer - überspringe"
fi

# Restore zusätzlicher Dateien
if [ -f "$SRC/package.json" ] && [ -s "$SRC/package.json" ]; then
    echo "📦 Übertrage package.json..."
    scp "${SSH_OPTS[@]}" "$SRC/package.json" "$HOST:~/.node-red/package.json"
    echo "✅ package.json übertragen"
fi

if [ -d "$SRC/lib" ]; then
    echo "📚 Übertrage lib/ Verzeichnis..."
    scp -r "${SSH_OPTS[@]}" "$SRC/lib/" "$HOST:~/.node-red/"
    echo "✅ lib/ Verzeichnis übertragen"
fi

# Setze korrekte Berechtigungen
echo "🔒 Setze Berechtigungen..."
ssh "${SSH_OPTS[@]}" "$HOST" "chmod 644 ~/.node-red/*.json ~/.node-red/*.js 2>/dev/null || true"

# Starte Node-RED neu
echo "🚀 Starte Node-RED neu..."
ssh "${SSH_OPTS[@]}" "$HOST" "systemctl --user start nodered"

# Warte kurz und prüfe Status
sleep 3
if ssh "${SSH_OPTS[@]}" "$HOST" "systemctl --user is-active nodered" >/dev/null 2>&1; then
    echo "✅ Node-RED erfolgreich gestartet"
    echo "🌐 Node-RED UI: http://$(echo $HOST | cut -d'@' -f2):1880"
else
    echo "❌ Fehler beim Starten von Node-RED"
    echo "📋 Prüfe Logs: ssh $HOST 'journalctl --user -u nodered -f'"
fi

echo ""
echo "✅ Restore abgeschlossen!"
echo "💾 Aktuelle Konfiguration gesichert in: ~/.node-red/backup_$CURRENT_BACKUP/"
echo "📄 Backup-Info: $SRC/backup_info.txt"
