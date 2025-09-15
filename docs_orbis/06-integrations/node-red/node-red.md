# 🔴 Node-RED Integration Guide

Detaillierte Anleitung für die Integration von Node-RED in die ORBIS Modellfabrik.

## 📋 Übersicht

Node-RED fungiert als **Gateway zwischen OPC-UA und MQTT** in der Fischertechnik APS und ist ein kritischer Bestandteil der Systemarchitektur.

### System-Architektur
```
┌─────────────────┐    MQTT     ┌─────────────────┐    OPC-UA    ┌─────────────────┐
│   OMF Dashboard │◄───────────►│   Node-RED      │◄────────────►│   SPS Module    │
│   (Steuerung)   │             │   (Gateway)     │              │   (Hardware)    │
└─────────────────┘             └─────────────────┘              └─────────────────┘
                                        │
                                        ▼
                                ┌─────────────────┐
                                │   MQTT Broker   │
                                │ 192.168.0.100   │
                                └─────────────────┘
```

## 🌐 Zugang und Konfiguration

### Zugangsdaten
- **Node-RED UI:** http://192.168.0.100:1880/
- **SSH Zugang:** `pi@192.168.0.100` (ff22/ff22+)
- **MQTT Broker:** 192.168.0.100:1883 (default/default)

### Systemd Service
```bash
# Node-RED Status prüfen
ssh pi@192.168.0.100 "systemctl --user status nodered"

# Node-RED starten/stoppen
ssh pi@192.168.0.100 "systemctl --user start nodered"
ssh pi@192.168.0.100 "systemctl --user stop nodered"

# Node-RED Logs anzeigen
ssh pi@192.168.0.100 "journalctl --user -u nodered -f"
```

## 🔧 Backup und Restore

### SSH-Backup (Empfohlen)
```bash
# Vollständiges Backup erstellen
HOST=pi@192.168.0.100 ./integrations/node_red/scripts/nodered_backup_ssh.sh

# Backup wiederherstellen
HOST=pi@192.168.0.100 SRC=integrations/node_red/backups/20250915T090000Z ./integrations/node_red/scripts/nodered_restore_ssh.sh
```

### Admin API-Backup
```bash
# Nur Flows sichern (ohne Credentials)
BASE=http://192.168.0.100:1880 ./integrations/node_red/scripts/nodered_backup_adminapi.sh

# Flows wiederherstellen
BASE=http://192.168.0.100:1880 FILE=integrations/node_red/backups/20250915T090000Z/flows.json ./integrations/node_red/scripts/nodered_restore_adminapi.sh
```

## 📁 Verzeichnisstruktur

### Node-RED Konfiguration (auf Raspberry Pi)
```
~/.node-red/
├── flows.json          # Flow-Definitionen
├── flows_cred.json     # Verschlüsselte Credentials
├── settings.js         # Node-RED Einstellungen
├── package.json        # Custom Node Dependencies
└── lib/               # Custom Libraries
```

### Integration Management (im Projekt)
```
integrations/node_red/
├── backups/           # Zeitgestempelte Backups
├── scripts/           # Backup/Restore-Skripte
├── project/           # (optional) Node-RED Project Export
└── README.md          # Kurzanleitung
```

## 🔐 Sicherheit und Credentials

### flows_cred.json
- **Zweck:** Speichert verschlüsselte Passwörter und API-Keys
- **Verschlüsselung:** Abhängig von `credentialSecret` in settings.js
- **Git:** **NIEMALS** im Klartext committen!

### settings.js
```javascript
// Beispiel-Konfiguration
module.exports = {
    // Admin API aktivieren
    httpAdminRoot: '/admin',
    
    // Credential Secret (für flows_cred.json)
    credentialSecret: "your-secret-key",
    
    // MQTT Broker Konfiguration
    mqtt: {
        broker: "192.168.0.100",
        port: 1883,
        username: "default",
        password: "default"
    }
}
```

## 🔄 Workflow-Integration

### 1. Regelmäßige Backups
```bash
# Crontab-Eintrag für tägliche Backups
0 2 * * * cd /path/to/project && HOST=pi@192.168.0.100 ./integrations/node_red/scripts/nodered_backup_ssh.sh
```

### 2. Vor Änderungen
```bash
# Backup vor Änderungen
HOST=pi@192.168.0.100 ./integrations/node_red/scripts/nodered_backup_ssh.sh

# Änderungen in Node-RED UI durchführen
# http://192.168.0.100:1880

# Backup nach Änderungen
HOST=pi@192.168.0.100 ./integrations/node_red/scripts/nodered_backup_ssh.sh
```

### 3. Disaster Recovery
```bash
# 1. Neuestes Backup finden
ls -la integrations/node_red/backups/ | tail -1

# 2. Restore durchführen
HOST=pi@192.168.0.100 SRC=integrations/node_red/backups/20250915T090000Z ./integrations/node_red/scripts/nodered_restore_ssh.sh

# 3. Node-RED Status prüfen
ssh pi@192.168.0.100 "systemctl --user status nodered"
```

## 🧰 Makefile Integration

```makefile
# Node-RED Makefile Targets
NR_HOST ?= pi@192.168.0.100
NR_BASE ?= http://192.168.0.100:1880

nodered-backup-ssh:
	HOST=$(NR_HOST) ./integrations/node_red/scripts/nodered_backup_ssh.sh

nodered-restore-ssh:
	HOST=$(NR_HOST) SRC=$(SRC) ./integrations/node_red/scripts/nodered_restore_ssh.sh

nodered-backup-api:
	BASE=$(NR_BASE) TOKEN=$(TOKEN) ./integrations/node_red/scripts/nodered_backup_adminapi.sh

nodered-restore-api:
	BASE=$(NR_BASE) FILE=$(FILE) TOKEN=$(TOKEN) ./integrations/node_red/scripts/nodered_restore_adminapi.sh

nodered-status:
	ssh $(NR_HOST) "systemctl --user status nodered"

nodered-logs:
	ssh $(NR_HOST) "journalctl --user -u nodered -f"
```

## 🔍 Troubleshooting

### Node-RED startet nicht
```bash
# Logs prüfen
ssh pi@192.168.0.100 "journalctl --user -u nodered -f"

# Status prüfen
ssh pi@192.168.0.100 "systemctl --user status nodered"

# Manuell starten
ssh pi@192.168.0.100 "systemctl --user start nodered"

# Konfiguration prüfen
ssh pi@192.168.0.100 "node-red --check ~/.node-red/flows.json"
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

# Firewall prüfen
ssh pi@192.168.0.100 "sudo ufw status"
```

## 📚 Weitere Dokumentation

- **[Flows Overview](./flows-overview.md)** - Tab-Struktur und Organisation
- **[State Machine](./state-machine.md)** - VDA 5050 State Transitions
- **[Fischertechnik Dokumentation](../analysis/fischertechnik-dokumentation-analyse.md)** - System-Architektur
- **[System Context](../02-architecture/system-context.md)** - Gesamtarchitektur

## ⚠️ Wichtige Hinweise

1. **Credentials:** `flows_cred.json` enthält verschlüsselte Passwörter - niemals im Klartext committen!
2. **Node-RED Neustart:** Nach SSH-Restore muss Node-RED neu gestartet werden
3. **Admin API:** Funktioniert nur bei aktivierter Admin API in settings.js
4. **Backup-Strategie:** SSH-Backup für vollständige Sicherung, Admin API für schnelle Flow-Updates
5. **MQTT Integration:** Node-RED ist kritisch für die OPC-UA ↔ MQTT Übersetzung

## 🚀 Nächste Schritte

1. **Backup-System einrichten** - Regelmäßige automatische Backups
2. **Monitoring implementieren** - Node-RED Status überwachen
3. **Documentation erweitern** - Flow-spezifische Dokumentation
4. **Testing automatisieren** - Flow-Validierung in CI/CD
5. **Performance optimieren** - Node-RED Performance-Monitoring
