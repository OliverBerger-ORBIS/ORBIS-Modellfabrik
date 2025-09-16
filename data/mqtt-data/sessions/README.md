# 📊 MQTT Session Data

Dieses Verzeichnis enthält MQTT-Session-Daten für die ORBIS-Modellfabrik.

## 📋 Default Demo Session

Die Dateien `default_test_session.db` und `default_test_session.log` sind **Demo-Dateien** die ins Repository gepusht werden, damit neue Nutzer sofort das Dashboard testen können.

### 📁 Dateien:
- `default_test_session.db` - SQLite-Datenbank mit Demo-MQTT-Nachrichten
- `default_test_session.log` - Log-Datei mit Demo-MQTT-Nachrichten

### 🎯 Zweck:
- **Sofortige Funktionalität** für neue Nutzer
- **Demo-Daten** für Dashboard-Tests
- **Beispiel-Sessions** für Entwicklung

### 🔄 Verwendung:
1. **Dashboard starten** → Default-Session wird automatisch geladen
2. **Session-Recorder** verwenden um eigene Sessions aufzunehmen
3. **Eigene Sessions** erscheinen in der Session-Auswahl

## 📝 Eigene Sessions

Eigene Sessions werden als `aps_persistent_traffic_<NAME>_<TIMESTAMP>.db` und `.log` gespeichert.

### 📋 Naming Convention:
- `aps_persistent_traffic_` - Präfix für alle Sessions
- `<NAME>` - Benutzerdefinierter Session-Name
- `<TIMESTAMP>` - Automatischer Zeitstempel

### 🎙️ Session-Recorder:
```bash
# Manueller Aufruf über Terminal
python omf/mqtt/loggers/aps_session_logger.py --session-label my-session --auto-start

# Mit "q" beenden
```

## 🔧 Technische Details

### 📊 Datenbank-Schema:
- `mqtt_messages` - Alle MQTT-Nachrichten
- `timestamp` - Zeitstempel der Nachricht
- `topic` - MQTT-Topic
- `payload` - Nachrichteninhalt (JSON)
- `module_type` - Modul-Typ (extrahierte Info)
- `status` - Status (extrahierte Info)

### 📝 Log-Format:
- Zeilenweise MQTT-Nachrichten
- JSON-Format für jede Nachricht
- Zeitstempel und Topic-Informationen

## 🚀 Getting Started

1. **Repository klonen**
2. **Dashboard starten:** `streamlit run omf/mqtt/dashboard/aps_dashboard.py`
3. **Default-Session** wird automatisch geladen
4. **Dashboard testen** mit Demo-Daten
5. **Eigene Sessions** aufnehmen mit Session-Recorder
