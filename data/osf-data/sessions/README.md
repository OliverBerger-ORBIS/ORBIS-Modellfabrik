# 📊 MQTT Session Data

Dieses Verzeichnis enthält MQTT-Session-Daten für die ORBIS Smart-Factory.

## 📋 Format

- **Dateiformat:** `.log` (JSON-Zeilen – eine MQTT-Nachricht pro Zeile)
- **Pfad:** `data/osf-data/sessions/`
- **Erste Zeile (optional, Session Manager):** `session_meta` — JSON **ohne** die MQTT-Pflichtfelder `topic` / `payload` / `timestamp`. Enthält u. a. Aufnahmezeitraum, Dauer, Preset, Broker, OSF-Workspace-Version (`package.json`), CCU/Order-Kurzinfo. **Replay Station** und Loader ignorieren diese Zeile automatisch.

## 🎯 Verwendung

1. **Session Manager starten:** `streamlit run session_manager/app.py`
2. **Session Recorder** – neue Sessions aufnehmen
3. **Replay Station** – Sessions abspielen
4. **Session Analysis** – Timeline, Order-Flow, Auftrag-Analyse

## 📝 Eigene Sessions

Eigene Sessions werden als `{Session-Name}_{Timestamp}.log` gespeichert.

### 🎙️ Session Recorder (Session Manager)
- Tab „Session Recorder“ öffnen
- MQTT-Broker verbinden, Recording starten
- Sessions erscheinen in Replay Station und Session Analysis

## 🔧 Technisches

- **Log-Format:** JSON-Zeilen: `{"topic":"...","payload":"...","timestamp":"..."}`
- Keine .db-Dateien mehr – nur .log (JSON-Zeilen)

## 📋 INVENTORY.md pflegen

Die Tabelle in [INVENTORY.md](./INVENTORY.md) ist die **übersichtliche** Einordnung von Sessions (Use-Case, AGVs). **Kein automatischer Ersatz** für die Meta-Zeile in der Datei.

- **Neue Session:** Zeile in der Schnellübersicht ergänzen (oder bestehende Spalten ergänzen).
- **Session gelöscht:** Entsprechende Zeile entfernen, damit die Doku nicht irreführt.

Abgleich-Hilfe (heuristisch):

```bash
python scripts/check_session_inventory.py
```
