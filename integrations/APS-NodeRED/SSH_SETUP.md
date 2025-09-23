# 🔐 SSH-Key Setup für Node-RED Integration

## 📋 Übersicht

Für automatische Node-RED Backups ohne Passwort-Eingabe ist SSH-Key-Authentifizierung erforderlich.

## 🚀 Schnell-Setup

### 1. SSH-Key bereits erstellt
```bash
# SSH-Key wurde bereits erstellt:
# ~/.ssh/nodered_key (private key)
# ~/.ssh/nodered_key.pub (public key)
```

### 2. Public Key auf Node-RED Server installieren
```bash
# Kopiere den Public Key auf den Server
ssh-copy-id -i ~/.ssh/nodered_key.pub ff22@192.168.0.100

# Oder manuell:
cat ~/.ssh/nodered_key.pub | ssh ff22@192.168.0.100 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### 3. SSH-Key testen
```bash
# Test ohne Passwort
ssh -i ~/.ssh/nodered_key ff22@192.168.0.100 "echo 'SSH-Key funktioniert!'"
```

### 4. Automatische Backups testen
```bash
# Backup mit SSH-Key
make nodered-backup-ssh

# Oder direkt
HOST=ff22@192.168.0.100 SSH_KEY=~/.ssh/nodered_key ./integrations/node_red/scripts/nodered_backup_ssh.sh
```

## 🔧 Alternative: Passwort-basierte Authentifizierung

Falls SSH-Key nicht funktioniert, können die Skripte auch mit Passwort laufen:

```bash
# Backup mit Passwort (interaktiv)
HOST=ff22@192.168.0.100 ./integrations/node_red/scripts/nodered_backup_ssh.sh

# Restore mit Passwort (interaktiv)
HOST=ff22@192.168.0.100 SRC=integrations/node_red/backups/20250915T090000Z ./integrations/node_red/scripts/nodered_restore_ssh.sh
```

## 🛠️ Troubleshooting

### SSH-Key funktioniert nicht
```bash
# Prüfe SSH-Key Berechtigungen
chmod 600 ~/.ssh/nodered_key
chmod 644 ~/.ssh/nodered_key.pub

# Prüfe Server-Berechtigungen
ssh ff22@192.168.0.100 "ls -la ~/.ssh/"
ssh ff22@192.168.0.100 "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

### Verbindung fehlgeschlagen
```bash
# Teste SSH-Verbindung
ssh -v ff22@192.168.0.100

# Prüfe SSH-Config
cat ~/.ssh/config
```

### Node-RED Dateien nicht gefunden
```bash
# Finde Node-RED Verzeichnis
ssh ff22@192.168.0.100 "find /home -name '*node-red*' -type d 2>/dev/null"
ssh ff22@192.168.0.100 "find /opt -name '*node-red*' -type d 2>/dev/null"
ssh ff22@192.168.0.100 "find /var -name '*node-red*' -type d 2>/dev/null"
```

## 📚 Weitere Optionen

### SSH-Config für einfachere Nutzung
```bash
# ~/.ssh/config
Host nodered
    HostName 192.168.0.100
    User ff22
    IdentityFile ~/.ssh/nodered_key
    IdentitiesOnly yes

# Dann einfach:
ssh nodered "echo 'Test'"
```

### Automatische Backups (Crontab)
```bash
# Täglich um 2:00 Uhr
0 2 * * * cd /path/to/project && make nodered-backup-ssh

# Oder mit SSH-Key
0 2 * * * cd /path/to/project && HOST=ff22@192.168.0.100 SSH_KEY=~/.ssh/nodered_key ./integrations/node_red/scripts/nodered_backup_ssh.sh
```

## ⚠️ Sicherheitshinweise

1. **SSH-Key schützen:** Niemals den Private Key (`nodered_key`) teilen
2. **Berechtigungen:** SSH-Key-Dateien müssen korrekte Berechtigungen haben
3. **Server-Zugang:** Nur notwendige Berechtigungen auf dem Node-RED Server
4. **Backup-Strategie:** SSH-Key auch sichern (verschlüsselt)

## 🔗 Nützliche Links

- [SSH-Key Setup Guide](https://www.ssh.com/academy/ssh/key)
- [SSH-Config Dokumentation](https://www.ssh.com/academy/ssh/config)
- [Node-RED Admin API](https://nodered.org/docs/api/admin/)
