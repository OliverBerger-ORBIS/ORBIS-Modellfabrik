# 📊 MQTT Session Data

Dieses Verzeichnis enthält MQTT-Session-Daten für die ORBIS Smart-Factory.

## 📋 Format

- **Dateiformat:** `.log` (JSON-Zeilen – eine MQTT-Nachricht pro Zeile)
- **Pfad:** `data/osf-data/sessions/`

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
