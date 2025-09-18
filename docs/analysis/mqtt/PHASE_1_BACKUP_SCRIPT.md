# Phase 1: Backup und Vorbereitung

## 🎯 Ziel
Alte Log-Dateien sichern und Verzeichnis für neue Analyse vorbereiten.

## 📋 Schritte

### 1. Backup-Verzeichnis erstellen
```bash
mkdir -p /Users/oliver/Projects/ORBIS-Modellfabrik/data/aps-data/mosquitto/backup
```

### 2. Alte Log-Dateien verschieben
```bash
cd /Users/oliver/Projects/ORBIS-Modellfabrik/data/aps-data/mosquitto/
mv *.log backup/
mv *.md backup/
mv *.mermaid backup/
```

### 3. Verzeichnis für neue Analyse vorbereiten
```bash
# Verzeichnis sollte jetzt leer sein (außer backup/)
ls -la
```

## ✅ Erfolgskriterien
- [ ] Backup-Verzeichnis erstellt
- [ ] Alle alten Log-Dateien in backup/ verschoben
- [ ] Hauptverzeichnis leer (außer backup/)
- [ ] Bereit für neue Log-Dateien

## 🚀 Nächster Schritt
SSH-Verbindung zu Raspberry Pi herstellen und Mosquitto-Konfiguration anpassen.
