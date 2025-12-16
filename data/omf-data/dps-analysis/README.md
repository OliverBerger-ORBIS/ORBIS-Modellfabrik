# 📊 DPS Session Analysis Data

Dieses Verzeichnis enthält extrahierte und strukturierte DPS-relevante Daten aus Session-Log-Dateien.

## 🎯 Zweck

Die hier gespeicherten Daten dienen der umfassenden DPS-Auswertung und sind für GitHub geeignet (strukturiert, JSON-Format, keine großen Binärdaten).

**Fokus:**
- **STORAGE-ORDER Kontext:** Topics vor einem STORAGE-ORDER (Farberkennung, NFC-Code auslesen)
- **PRODUCTION-ORDER Kontext:** Topics nach einem PRODUCTION-ORDER (NFC-Code wird wieder ausgelesen)

## 📁 Dateinamenskonvention

### Format
```
{session_name}_{category}.json
```

### Kategorien

- **`{session_name}_metadata.json`** - Metadaten und Statistiken der Analyse
- **`{session_name}_all_dps_messages.json`** - Alle DPS-relevanten Messages (komplett)
- **`{session_name}_dps_connection.json`** - DPS Connection Status Messages
- **`{session_name}_dps_state.json`** - DPS State Updates
- **`{session_name}_dps_order.json`** - DPS Order Commands
- **`{session_name}_dps_instant_action.json`** - DPS Instant Actions
- **`{session_name}_dps_factsheet.json`** - DPS Factsheet (Capabilities)
- **`{session_name}_ccu_order_active.json`** - CCU Active Order Messages
- **`{session_name}_ccu_order_completed.json`** - CCU Completed Order Messages
- **`{session_name}_ccu_order_request.json`** - CCU Order Request Messages
- **`{session_name}_txt_controller.json`** - TXT Controller Messages (Camera, Stock)
- **`{session_name}_storage_order_context.json`** - Messages im Kontext von STORAGE-ORDER (Farberkennung, NFC)
- **`{session_name}_production_order_context.json`** - Messages im Kontext von PRODUCTION-ORDER (NFC-Auslesen)

### Beispiel
```
production_order_blue_20251110_180619_metadata.json
production_order_blue_20251110_180619_dps_state.json
production_order_blue_20251110_180619_storage_order_context.json
production_order_blue_20251110_180619_production_order_context.json
```

## 🔍 Relevante Topics

### DPS Topics (direkt)
- `module/v1/ff/SVR4H73275/connection` - DPS Connection Status
- `module/v1/ff/SVR4H73275/state` - DPS State Updates
- `module/v1/ff/SVR4H73275/order` - DPS Order Commands
- `module/v1/ff/SVR4H73275/instantAction` - DPS Instant Actions
- `module/v1/ff/SVR4H73275/factsheet` - DPS Capabilities

### DPS Topics (NodeRed enriched)
- `module/v1/ff/NodeRed/SVR4H73275/connection` - DPS Connection (NodeRed enriched)
- `module/v1/ff/NodeRed/SVR4H73275/state` - DPS State (NodeRed enriched, mit orderId)
- `module/v1/ff/NodeRed/SVR4H73275/factsheet` - DPS Factsheet (NodeRed)

### CCU Topics (relevant für DPS)
- `ccu/order/active` - Aktive Orders
- `ccu/order/completed` - Abgeschlossene Orders
- `ccu/order/request` - Order Requests

### TXT Controller Topics (DPS hat TXT-Controller)
- `/j1/txt/1/f/i/stock` - DPS Stock Information
- `/j1/txt/1/i/cam` - DPS Camera Data

## 📊 Datenformat

### Metadata-Datei
```json
{
  "session_name": "production_order_blue_20251110_180619",
  "analysis_timestamp": "2025-12-16T20:42:09.241566",
  "dps_serial": "SVR4H73275",
  "total_messages": 3625,
  "dps_relevant_messages": 1528,
  "start_time": "2025-11-10T18:16:47.561299",
  "end_time": "2025-11-10T18:28:09.534677",
  "topic_counts": {
    "module/v1/ff/SVR4H73275/state": 334,
    "ccu/order/active": 63,
    ...
  },
  "topic_categories": {
    "dps_state": 334,
    "ccu_order_active": 74,
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
    "INPUT_RGB": 12,
    "RGB_NFC": 12
  },
  "storage_order_context_count": 234,
  "production_order_context_count": 456
}
```

### Message-Dateien
Jede Message-Datei enthält ein Array von Message-Objekten:
```json
[
  {
    "timestamp": "2025-11-10T18:16:47.562237",
    "topic": "module/v1/ff/SVR4H73275/state",
    "payload": "{...}",
    "qos": 2
  },
  ...
]
```

### STORAGE-ORDER Kontext
Enthält alle Messages im Kontext von STORAGE-ORDER (50 Messages vor, 100 Messages nach):
- Topics für Farberkennung (`INPUT_RGB`)
- Topics für NFC-Code auslesen (`RGB_NFC`)
- DPS State Updates während STORAGE-ORDER
- CCU Order Messages

### PRODUCTION-ORDER Kontext
Enthält alle Messages im Kontext von PRODUCTION-ORDER (50 Messages vor, 100 Messages nach):
- Topics für NFC-Code auslesen nach PRODUCTION-ORDER
- DPS State Updates während PRODUCTION-ORDER
- CCU Order Messages

## 🚀 Verwendung

### Analyse-Skript ausführen
```bash
python scripts/analyze_dps_sessions.py data/omf-data/sessions/production_order_blue_20251110_180619.log
```

### Optionen
```bash
python scripts/analyze_dps_sessions.py <session_file> \
  --output-dir data/omf-data/dps-analysis \
  --session-name custom_name
```

### Alle Sessions analysieren
```bash
for log_file in data/omf-data/sessions/*.log; do
  python scripts/analyze_dps_sessions.py "$log_file"
done
```

## 📈 Analyse-Ergebnisse

Die Analyse extrahiert:
- ✅ Alle DPS-relevanten Topics und Payloads
- ✅ Connection und Availability (auch wenn bereits ausgewertet)
- ✅ STORAGE-ORDER Kontext (Farberkennung, NFC-Code)
- ✅ PRODUCTION-ORDER Kontext (NFC-Code-Auslesen)
- ✅ Commands (PICK, DROP, INPUT_RGB, RGB_NFC)
- ✅ Workpiece IDs und Types
- ✅ Order IDs und Update IDs

## 🔗 Verwandte Dokumentation

- [DPS Module Serial Mapping](../../../../docs/06-integrations/00-REFERENCE/module-serial-mapping.md)
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

### STORAGE-ORDER Flow
1. **Farberkennung:** `INPUT_RGB` Command erkennt Farbe des Werkstücks
2. **NFC-Auslesen:** `RGB_NFC` Command liest NFC-Code des Werkstücks
3. **Order-Erstellung:** CCU erstellt STORAGE-ORDER basierend auf Farbe und NFC-Code

### PRODUCTION-ORDER Flow
1. **Produktion:** Werkstück durchläuft Produktionsprozess
2. **NFC-Auslesen:** Nach PRODUCTION-ORDER wird NFC-Code erneut ausgelesen
3. **Verifikation:** NFC-Code wird verifiziert (gleicher Code wie vorher)
