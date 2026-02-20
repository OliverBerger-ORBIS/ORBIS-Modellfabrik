# 🔴 Node-RED Integration

Node-RED Integration für die ORBIS SmartFactory - Backup, Restore und Management der Node-RED Konfiguration.

## 📁 Verzeichnisstruktur

```
integrations/APS-NodeRED/
├── backups/              # Zeitgestempelte Backups
│   └── 20250915T090000Z/ # Beispiel-Backup
│       ├── flows.json
│       ├── flows_cred.json
│       ├── settings.js
│       └── backup_info.txt
├── scripts/              # Backup/Restore-Skripte
│   ├── nodered_backup_ssh.sh
│   ├── nodered_restore_ssh.sh
│   ├── nodered_backup_adminapi.sh
│   └── nodered_restore_adminapi.sh
├── project/              # (optional) Node-RED Project Export
└── README.md
```

## 🚀 Quick Start

### SSH-Backup (Für Docker-Container nicht verfügbar)
```bash
# Node-RED läuft in Docker-Container - SSH-Backup funktioniert nicht
# Verwende stattdessen Admin API-Backup
```

### Admin API-Backup (Empfohlen für Docker-Container)
```bash
# Backup erstellen
BASE=http://192.168.0.100:1880 ./scripts/nodered_backup_adminapi.sh

# Restore durchführen
BASE=http://192.168.0.100:1880 FILE=integrations/APS-NodeRED/backups/20250915T090000Z/flows.json ./scripts/nodered_restore_adminapi.sh
```

### SSH-Backup (Nur für native Installation)
```bash
# Backup erstellen (mit SSH-Key)
HOST=ff22@192.168.0.100 SSH_KEY=~/.ssh/nodered_key ./scripts/nodered_backup_ssh.sh

# Restore durchführen (mit SSH-Key)
HOST=ff22@192.168.0.100 SRC=integrations/APS-NodeRED/backups/20250915T090000Z SSH_KEY=~/.ssh/nodered_key ./scripts/nodered_restore_ssh.sh
```

## 🔧 Makefile Integration

```bash
# Admin API-Backup (Empfohlen für Docker-Container)
make nodered-backup-api NR_BASE=http://192.168.0.100:1880

# Admin API-Restore
make nodered-restore-api NR_BASE=http://192.168.0.100:1880 FILE=integrations/APS-NodeRED/backups/20250915T090000Z/flows.json

# SSH-Backup (Nur für native Installation)
make nodered-backup-ssh NR_HOST=ff22@192.168.0.100

# SSH-Restore (Nur für native Installation)
make nodered-restore-ssh NR_HOST=ff22@192.168.0.100 SRC=integrations/APS-NodeRED/backups/20250915T090000Z
```

## 🔐 Sicherheit

### Sensible Dateien
- `flows_cred.json` - Verschlüsselte Credentials (NICHT im Klartext committen!)
- `settings.js` - Kann Secrets enthalten (HTTP Admin Auth, etc.)

### .gitignore
```gitignore
# Node-RED sensible Dateien
flows_cred.json
*.cred.json
settings.local.js
.env
```

## 📋 Backup-Methoden

### 1. SSH-Backup (Vollständig)
**Vorteile:**
- ✅ Vollständige Konfiguration (flows.json, flows_cred.json, settings.js)
- ✅ Custom Nodes (package.json)
- ✅ Custom Libraries (lib/)
- ✅ Offline-fähig

**Nachteile:**
- ❌ Benötigt SSH-Zugang
- ❌ Manueller Node-RED Neustart erforderlich

### 2. Admin API-Backup (Teilweise)
**Vorteile:**
- ✅ Kein SSH-Zugang erforderlich
- ✅ Automatische Aktivierung der Flows
- ✅ REST-API basiert

**Nachteile:**
- ❌ Nur flows.json (keine Credentials!)
- ❌ Benötigt aktivierte Admin API
- ❌ Authentifizierung erforderlich

## 🔄 Workflow

### Regelmäßige Backups
```bash
# Täglich um 2:00 Uhr (crontab)
0 2 * * * cd /path/to/project && HOST=pi@192.168.0.100 ./integrations/APS-NodeRED/scripts/nodered_backup_ssh.sh
```

### Vor Änderungen
```bash
# Backup vor Änderungen
HOST=pi@192.168.0.100 ./scripts/nodered_backup_ssh.sh

# Änderungen in Node-RED UI durchführen
# http://192.168.0.100:1880

# Backup nach Änderungen
HOST=pi@192.168.0.100 ./scripts/nodered_backup_ssh.sh
```

### Disaster Recovery
```bash
# 1. Neuestes Backup finden
ls -la integrations/APS-NodeRED/backups/ | tail -1

# 2. Restore durchführen
HOST=pi@192.168.0.100 SRC=integrations/APS-NodeRED/backups/20250915T090000Z ./scripts/nodered_restore_ssh.sh

# 3. Node-RED Status prüfen
ssh pi@192.168.0.100 "systemctl --user status nodered"
```

## 🌐 Node-RED Zugang

**URL:** http://192.168.0.100:1880/
**SSH:** pi@192.168.0.100 (ff22/ff22+)
**MQTT:** 192.168.0.100:1883 (default/default)

## 📚 Weitere Dokumentation

- [Node-RED Integration Guide](../../docs/06-integrations/node-red/node-red.md)
- [Node-RED Flows Overview](../../docs/06-integrations/node-red/flows-overview.md)
- [Node-RED State Machine](../../docs/06-integrations/node-red/state-machine.md)
- [Fischertechnik Dokumentation](../../docs/06-integrations/FISCHERTECHNIK-OFFICIAL.md)
- [System Context](../../docs/02-architecture/system-context.md)

## ⚠️ Wichtige Hinweise

1. **Credentials:** `flows_cred.json` enthält verschlüsselte Passwörter - niemals im Klartext committen!
2. **Node-RED Neustart:** Nach SSH-Restore muss Node-RED neu gestartet werden
3. **Admin API:** Funktioniert nur bei aktivierter Admin API in settings.js
4. **Backup-Strategie:** SSH-Backup für vollständige Sicherung, Admin API für schnelle Flow-Updates

## 🆘 Troubleshooting

### Node-RED startet nicht
```bash
# Logs prüfen
ssh pi@192.168.0.100 "journalctl --user -u nodered -f"

# Status prüfen
ssh pi@192.168.0.100 "systemctl --user status nodered"

# Manuell starten
ssh pi@192.168.0.100 "systemctl --user start nodered"
```

### Backup fehlgeschlagen
```bash
# SSH-Verbindung testen
ssh pi@192.168.0.100 "echo 'SSH funktioniert'"

# Node-RED Verzeichnis prüfen
ssh pi@192.168.0.100 "ls -la ~/.node-red/"

# Berechtigungen prüfen
ssh pi@192.168.0.100 "ls -la ~/.node-red/*.json"
```

### Admin API nicht erreichbar
```bash
# Node-RED läuft?
curl -f http://192.168.0.100:1880/flows

# Admin API aktiviert?
ssh pi@192.168.0.100 "grep -i 'httpAdmin' ~/.node-red/settings.js"
```
