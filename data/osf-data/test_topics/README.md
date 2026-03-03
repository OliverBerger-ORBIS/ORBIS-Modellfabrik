# 🧪 Test-Topics Verzeichnis

Dieses Verzeichnis enthält JSON-Dateien mit MQTT-Messages für Integrationstests, die über die **Session Manager Replay Station** versendet werden können.

## 🎯 Zweck

Die Test-Topics ermöglichen es, **individuelle MQTT-Messages** gezielt an den Broker zu senden, ohne eine vollständige Session abzuspielen. Dies ist besonders nützlich für:

- **Integrationstests** einzelner Topics
- **Schnelles Testen** von Payload-Varianten
- **Debugging** von Message-Handling
- **Reproduzieren** spezifischer Szenarien

## 📁 Verzeichnisstruktur

```
test_topics/
├── *.json                    # Individuelle Test-Topics (manuell auswählbar)
└── preloads/
    └── *.json                # Automatische Preload-Topics (alle auf einmal)
```

### 🎯 Individuelles Senden (`test_topics/*.json`)

Diese JSON-Dateien können in der **Replay Station** einzeln ausgewählt und versendet werden:

- ✅ Multiselect-Auswahl in der UI
- ✅ Manuelles Versenden über Button "Ausgewählte jetzt senden"
- ✅ Flexibel für verschiedene Test-Szenarien

**Beispiele:**
- `ccu_order_active__emptyPayload.json` - CCU Order Active ohne Payload
- `ccu_order_active__payload01.json` - CCU Order Active mit Payload

### 🚀 Automatischer Preload (`test_topics/preloads/*.json`)

Diese JSON-Dateien werden **automatisch alle zusammen** gesendet:

- ✅ Automatischer Versand vor Session-Replay (wenn aktiviert)
- ✅ Manueller Versand über Button "Preloads jetzt senden"
- ✅ Typischerweise Factsheets oder andere Setup-Messages

**Beispiele:**
- `ccu_state_layout.json` - Fabrik-Layout (ccu/state/layout, retained)
- `module_v1_ff_SVR3QA0022_factsheet.json` - HBW Module Factsheet
- `module_v1_ff_SVR4H73275_factsheet.json` - DRILL Module Factsheet
- `fts_v1_ff_5iO4_factsheet.json` - FTS Module Factsheet

## 📄 Dateiformat

Jede JSON-Datei sollte folgende Struktur haben:

```json
{
  "topic": "module/v1/ff/SVR3QA0022/factsheet",
  "payload": "{\"headerId\":1,\"timestamp\":\"2025-10-01T11:29:59.065Z\",\"version\":\"1.3.0\",...}",
  "qos": 0,
  "retain": false,
  "timestamp": "2025-10-01T13:29:59.071731",
  "sequence": 46,
  "type": "interesting"
}
```

**Pflichtfelder:**
- `topic` - MQTT-Topic (String)
- `payload` - Payload (String, Dict oder List)

**Optionale Felder:**
- `qos` - Quality of Service (0, 1, 2) - Default: 0
- `retain` - Retain-Flag (Boolean) - Default: false
- `timestamp` - Zeitstempel (String, ISO-Format) - Optional
- `sequence` - Sequenznummer (Integer) - Optional
- `type` - Typ (String) - Optional

## 🔧 Verwendung in Replay Station

### Individuelles Senden

1. **Auswahl**: Wähle eine oder mehrere Test-Topics aus der Multiselect-Box
2. **Senden**: Klicke auf "📤 Ausgewählte jetzt senden"
3. **Ergebnis**: UI zeigt Erfolg/Fehler für jede gesendete Message

### Automatischer Preload

1. **Automatisch**: Aktiviere Checkbox "🚀 Test-Topics vor Session-Replay senden"
2. **Manuell**: Klicke auf "🚀 Preloads jetzt senden"
3. **Ergebnis**: Alle Preload-Messages werden in einem Batch gesendet

## 📝 Hinweise

- ✅ Alle JSON-Dateien werden automatisch erkannt
- ✅ Payload kann als String, Dict oder List angegeben werden
- ✅ QoS und Retain-Flags werden aus den Dateien übernommen
- ✅ Fehlerhafte Dateien werden übersprungen und geloggt
- ✅ Logging in `logs/session_manager/session_manager.log`

## 🚀 Best Practices

1. **Dateinamen**: Verwende sprechende Namen wie `<topic>__<variant>.json`
2. **Preloads**: Factsheets und Setup-Messages gehören in `preloads/`
3. **Test-Topics**: Payload-Varianten und Integrationstests ins Hauptverzeichnis
4. **Versionierung**: Bei Änderungen neue Varianten anlegen statt alte zu überschreiben

## 🔗 Verwandte Dokumentation

- [Session Manager README](../sessions/README.md)
- [Replay Station Dokumentation](../../../docs/04-howto/helper_apps/replay-station.md)














