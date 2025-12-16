# 📊 AIQS Session Analysis Data

Dieses Verzeichnis enthält extrahierte und strukturierte AIQS-relevante Daten aus Session-Log-Dateien.

## 🎯 Zweck

Die hier gespeicherten Daten dienen der umfassenden AIQS-Auswertung und sind für GitHub geeignet (strukturiert, JSON-Format, keine großen Binärdaten).

**Fokus:**
- **CHECK_QUALITY:** Topics und Payloads für Qualitätsprüfung
- **ML-basierte Qualitätsprüfung:** Photo von Werkstücken, Mustererkennung
- **Qualitätsergebnisse:** PASSED/FAILED Ergebnisse der Qualitätsprüfung

## 📁 Dateinamenskonvention

### Format
```
{session_name}_{category}.json
```

### Kategorien

- **`{session_name}_metadata.json`** - Metadaten und Statistiken der Analyse
- **`{session_name}_all_aiqs_messages.json`** - Alle AIQS-relevanten Messages (komplett)
- **`{session_name}_aiqs_connection.json`** - AIQS Connection Status Messages
- **`{session_name}_aiqs_state.json`** - AIQS State Updates
- **`{session_name}_aiqs_order.json`** - AIQS Order Commands
- **`{session_name}_aiqs_instant_action.json`** - AIQS Instant Actions
- **`{session_name}_aiqs_factsheet.json`** - AIQS Factsheet (Capabilities)
- **`{session_name}_ccu_order_active.json`** - CCU Active Order Messages
- **`{session_name}_ccu_order_completed.json`** - CCU Completed Order Messages
- **`{session_name}_ccu_order_request.json`** - CCU Order Request Messages
- **`{session_name}_txt_controller.json`** - TXT Controller Messages (Environmental Sensor)
- **`{session_name}_check_quality_results.json`** - CHECK_QUALITY Ergebnisse (PASSED/FAILED)
- **`{session_name}_check_quality_context.json`** - Messages im Kontext von CHECK_QUALITY (Photo, ML, Mustererkennung)

### Beispiel
```
production_order_blue_20251110_180619_metadata.json
production_order_blue_20251110_180619_aiqs_state.json
production_order_blue_20251110_180619_check_quality_results.json
production_order_blue_20251110_180619_check_quality_context.json
```

## 🔍 Relevante Topics

### AIQS Topics (direkt)
- `module/v1/ff/SVR4H76530/connection` - AIQS Connection Status
- `module/v1/ff/SVR4H76530/state` - AIQS State Updates
- `module/v1/ff/SVR4H76530/order` - AIQS Order Commands
- `module/v1/ff/SVR4H76530/instantAction` - AIQS Instant Actions
- `module/v1/ff/SVR4H76530/factsheet` - AIQS Capabilities

### AIQS Topics (NodeRed enriched)
- `module/v1/ff/NodeRed/SVR4H76530/connection` - AIQS Connection (NodeRed enriched)
- `module/v1/ff/NodeRed/SVR4H76530/state` - AIQS State (NodeRed enriched, mit orderId)
- `module/v1/ff/NodeRed/SVR4H76530/factsheet` - AIQS Factsheet (NodeRed)

### CCU Topics (relevant für AIQS)
- `ccu/order/active` - Aktive Orders
- `ccu/order/completed` - Abgeschlossene Orders (enthält CHECK_QUALITY Ergebnisse)
- `ccu/order/request` - Order Requests

### TXT Controller Topics (AIQS hat TXT-Controller)
- `/j1/txt/1/i/bme680` - AIQS Environmental Sensor (BME680)

## 📊 Datenformat

### Metadata-Datei
```json
{
  "session_name": "production_order_blue_20251110_180619",
  "analysis_timestamp": "2025-12-16T20:42:09.241566",
  "aiqs_serial": "SVR4H76530",
  "total_messages": 3625,
  "aiqs_relevant_messages": 1528,
  "start_time": "2025-11-10T18:16:47.561299",
  "end_time": "2025-11-10T18:28:09.534677",
  "topic_counts": {
    "module/v1/ff/SVR4H76530/state": 334,
    "ccu/order/completed": 63,
    ...
  },
  "topic_categories": {
    "aiqs_state": 334,
    "ccu_order_completed": 74,
    ...
  },
  "payload_stats": {
    "has_orderId": 123,
    "has_actionState": 456,
    "has_workpieceId": 89,
    ...
  },
  "commands_found": {
    "PICK": 45,
    "DROP": 45,
    "CHECK_QUALITY": 12
  },
  "check_quality_results_count": 12,
  "check_quality_context_count": 234
}
```

### Message-Dateien
Jede Message-Datei enthält ein Array von Message-Objekten:
```json
[
  {
    "timestamp": "2025-11-10T18:16:47.562237",
    "topic": "module/v1/ff/SVR4H76530/state",
    "payload": "{...}",
    "qos": 2
  },
  ...
]
```

### CHECK_QUALITY Ergebnisse
Enthält alle CHECK_QUALITY Ergebnisse mit Result (PASSED/FAILED):
```json
[
  {
    "timestamp": "2025-11-10T17:00:24.896410Z",
    "topic": "module/v1/ff/NodeRed/SVR4H76530/state",
    "result": "PASSED",
    "state": "FINISHED",
    "id": "b361aca3-dece-46ba-b07e-a360600c2516"
  },
  ...
]
```

### CHECK_QUALITY Kontext
Enthält alle Messages im Kontext von CHECK_QUALITY (30 Messages vor, 50 Messages nach):
- Topics für Photo-Aufnahme
- Topics für ML-basierte Qualitätsprüfung
- Topics für Mustererkennung
- AIQS State Updates während CHECK_QUALITY
- CCU Order Messages

## 🚀 Verwendung

### Analyse-Skript ausführen
```bash
python scripts/analyze_aiqs_sessions.py data/omf-data/sessions/production_order_blue_20251110_180619.log
```

### Optionen
```bash
python scripts/analyze_aiqs_sessions.py <session_file> \
  --output-dir data/omf-data/aiqs-analysis \
  --session-name custom_name
```

### Alle Sessions analysieren
```bash
for log_file in data/omf-data/sessions/*.log; do
  python scripts/analyze_aiqs_sessions.py "$log_file"
done
```

## 📈 Analyse-Ergebnisse

Die Analyse extrahiert:
- ✅ Alle AIQS-relevanten Topics und Payloads
- ✅ Connection und Availability (auch wenn bereits ausgewertet)
- ✅ CHECK_QUALITY Ergebnisse (PASSED/FAILED)
- ✅ CHECK_QUALITY Kontext (Photo, ML, Mustererkennung)
- ✅ Commands (PICK, DROP, CHECK_QUALITY)
- ✅ Workpiece IDs und Types
- ✅ Order IDs und Update IDs

## 🔗 Verwandte Dokumentation

- [AIQS Module Serial Mapping](../../../../docs/06-integrations/00-REFERENCE/module-serial-mapping.md)
- [MQTT Topic Conventions](../../../../docs/06-integrations/00-REFERENCE/mqtt-topic-conventions.md)
- [MQTT Message Examples](../../../../docs/06-integrations/00-REFERENCE/mqtt-message-examples.md)
- [Session Data README](../sessions/README.md)

## 📝 Hinweise

- Alle Dateien sind im JSON-Format für einfache Verarbeitung
- Payloads sind als JSON-Strings gespeichert (können mit `json.loads()` geparst werden)
- Timestamps sind im ISO-Format
- Die Daten sind für GitHub geeignet (keine großen Binärdaten)
- Connection und Availability werden extrahiert, auch wenn sie bereits ausgewertet werden

## 🎯 Wichtige Erkenntnisse für GitHub

### CHECK_QUALITY Flow
1. **PICK:** Werkstück wird aufgenommen
2. **Photo:** AIQS macht ein Photo vom Werkstück
3. **ML-Analyse:** Mustererkennung prüft Qualität anhand von Mustern
4. **Ergebnis:** PASSED oder FAILED wird zurückgegeben
5. **DROP:** Werkstück wird abgelegt (oder verworfen bei FAILED)

### Qualitätsprüfung Details
- **Photo-Aufnahme:** Wird durch TXT-Controller durchgeführt
- **ML-Feature:** Mustererkennung basiert auf trainierten Modellen
- **Ergebnis:** Wird in `actionState.result` zurückgegeben (PASSED/FAILED)
- **State:** Wird in `actionState.state` zurückgegeben (FINISHED/ERROR)

### Integration in Production Flow
- CHECK_QUALITY ist Teil des Production-Order-Flows
- Bei FAILED wird die Order abgebrochen (ERROR State)
- Bei PASSED wird die Order fortgesetzt (FINISHED State)
