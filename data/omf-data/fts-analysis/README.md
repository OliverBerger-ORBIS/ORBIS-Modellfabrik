# 📊 FTS Session Analysis Data

Dieses Verzeichnis enthält extrahierte und strukturierte FTS-relevante Daten aus Session-Log-Dateien.

## 🎯 Zweck

Die hier gespeicherten Daten dienen der umfassenden FTS-Auswertung und sind für GitHub geeignet (strukturiert, JSON-Format, keine großen Binärdaten).

## 📁 Dateinamenskonvention

### Format
```
{session_name}_{category}.json
```

### Kategorien

- **`{session_name}_metadata.json`** - Metadaten und Statistiken der Analyse
- **`{session_name}_all_fts_messages.json`** - Alle FTS-relevanten Messages (komplett)
- **`{session_name}_fts_connection.json`** - FTS Connection Status Messages
- **`{session_name}_fts_state.json`** - FTS State Updates (Position, Battery, Load, ActionState)
- **`{session_name}_fts_order.json`** - FTS Navigation Orders (VDA5050)
- **`{session_name}_fts_instant_action.json`** - FTS Instant Action Commands
- **`{session_name}_fts_factsheet.json`** - FTS Factsheet (Capabilities)
- **`{session_name}_ccu_order.json`** - CCU Order Messages (relevant für FTS-Navigation)
- **`{session_name}_module_state.json`** - Module State Messages (relevant für FTS-Interaktionen)

### Beispiel
```
production_order_bwr_20251110_182819_metadata.json
production_order_bwr_20251110_182819_fts_state.json
production_order_bwr_20251110_182819_ccu_order.json
```

## 🔍 Relevante Topics

### FTS Topics (direkt)
- `fts/v1/ff/5iO4/connection` - FTS Connection Status
- `fts/v1/ff/5iO4/state` - FTS State Updates (hohe Frequenz)
- `fts/v1/ff/5iO4/order` - FTS Navigation Orders (VDA5050)
- `fts/v1/ff/5iO4/instantAction` - FTS Instant Actions
- `fts/v1/ff/5iO4/factsheet` - FTS Capabilities

### CCU Topics (relevant für FTS)
- `ccu/order/active` - Aktive Orders
- `ccu/order/completed` - Abgeschlossene Orders
- `ccu/order/request` - Order Requests
- `ccu/order/response` - Order Responses

### Module Topics (relevant für FTS-Interaktionen)
- `module/v1/ff/SVR3QA0022/state` - HBW State (FTS Pick/Drop)
- `module/v1/ff/SVR4H73275/state` - DPS State (FTS Pick/Drop)
- `module/v1/ff/SVR4H76530/state` - AIQS State (FTS Pick/Drop)
- `module/v1/ff/SVR3QA2098/state` - MILL State
- `module/v1/ff/SVR4H76449/state` - DRILL State

## 📊 Datenformat

### Metadata-Datei
```json
{
  "session_name": "production_order_bwr_20251110_182819",
  "analysis_timestamp": "2025-11-30T20:42:09.241566",
  "total_messages": 3625,
  "fts_relevant_messages": 1528,
  "start_time": "2025-11-10T18:16:47.561299",
  "end_time": "2025-11-10T18:28:09.534677",
  "topic_counts": {
    "fts/v1/ff/5iO4/state": 334,
    "ccu/order/active": 63,
    ...
  },
  "topic_categories": {
    "fts_state": 334,
    "ccu_order": 74,
    ...
  },
  "payload_stats": {
    "has_orderId": 123,
    "has_actionState": 456,
    ...
  }
}
```

### Message-Dateien
Jede Message-Datei enthält ein Array von Message-Objekten:
```json
[
  {
    "timestamp": "2025-11-10T18:16:47.562237",
    "topic": "fts/v1/ff/5iO4/state",
    "payload": "{...}",
    "qos": 2
  },
  ...
]
```

## 🚀 Verwendung

### Analyse-Skript ausführen
```bash
python scripts/analyze_fts_sessions.py data/omf-data/sessions/production_order_bwr_20251110_182819.log
```

### Optionen
```bash
python scripts/analyze_fts_sessions.py <session_file> \
  --output-dir data/omf-data/fts-analysis \
  --session-name custom_name
```

## 📈 Analyse-Ergebnisse

### Production Order BWR (2025-11-10)
- **Session**: `production_order_bwr_20251110_182819`
- **Gesamt-Messages**: 3625
- **FTS-relevante Messages**: 1528 (42%)
- **Zeitraum**: ~11 Minuten (18:16:47 - 18:28:09)
- **Haupt-Topics**:
  - `fts/v1/ff/5iO4/state`: 334 Messages (FTS State Updates)
  - `module/v1/ff/SVR4H73275/instantAction`: 672 Messages
  - `ccu/order/active`: 63 Messages
  - `fts/v1/ff/5iO4/order`: 23 Messages (Navigation Orders)
  - `fts/v1/ff/5iO4/instantAction`: 23 Messages

### Storage Order White (2025-11-10)
- **Session**: `storage_order_white_20251110_181619`
- **Gesamt-Messages**: 588
- **FTS-relevante Messages**: 211 (36%)
- **Zeitraum**: ~2 Minuten (18:14:02 - 18:16:09)
- **Haupt-Topics**:
  - `module/v1/ff/SVR4H73275/instantAction`: 81 Messages
  - `fts/v1/ff/5iO4/state`: 25 Messages (FTS State Updates)
  - `module/v1/ff/NodeRed/SVR4H73275/state`: 10 Messages
  - `ccu/order/active`: 7 Messages
  - `fts/v1/ff/5iO4/order`: 2 Messages (Navigation Orders)

### Storage Order Blue (2025-11-10)
- **Session**: `storage_order_blue_20251110_181104`
- **Gesamt-Messages**: 552
- **FTS-relevante Messages**: 201 (36%)
- **Zeitraum**: ~2 Minuten
- **Haupt-Topics**:
  - `module/v1/ff/SVR4H73275/instantAction`: 76 Messages
  - `fts/v1/ff/5iO4/state`: 25 Messages (FTS State Updates)
  - `module/v1/ff/NodeRed/SVR4H73275/state`: 10 Messages
  - `ccu/order/active`: 7 Messages
  - `fts/v1/ff/5iO4/order`: 2 Messages (Navigation Orders)

### Storage Order Red (2025-11-10)
- **Session**: `storage_order_red_20251110_181336`
- **Gesamt-Messages**: 587
- **FTS-relevante Messages**: 211 (36%)
- **Zeitraum**: ~2 Minuten
- **Haupt-Topics**:
  - `module/v1/ff/SVR4H73275/instantAction`: 81 Messages
  - `fts/v1/ff/5iO4/state`: 25 Messages (FTS State Updates)
  - `module/v1/ff/NodeRed/SVR4H73275/state`: 10 Messages
  - `ccu/order/active`: 7 Messages
  - `fts/v1/ff/5iO4/order`: 2 Messages (Navigation Orders)

### Vergleich: Production vs. Storage Orders

| Metrik | Production Order | Storage Orders |
|--------|------------------|----------------|
| **Durchschnittliche Gesamt-Messages** | 3625 | ~576 |
| **Durchschnittliche FTS-relevante Messages** | 1528 (42%) | ~208 (36%) |
| **Durchschnittliche Dauer** | ~11 Minuten | ~2 Minuten |
| **FTS State Updates** | 334 | ~25 |
| **FTS Navigation Orders** | 23 | ~2 |
| **CCU Active Orders** | 63 | ~7 |

**Erkenntnisse:**
- Production Orders sind deutlich länger und umfangreicher
- Production Orders haben mehr FTS State Updates (höhere Frequenz)
- Storage Orders sind kürzer und fokussierter
- Beide Order-Typen zeigen ähnliche Topic-Verteilungen (proportional)

## 🔗 Verwandte Dokumentation

- [FTS Topics Registry](../../../../omf2/registry/topics/fts.yml)
- [MQTT Topic Conventions](../../../../docs/06-integrations/00-REFERENCE/mqtt-topic-conventions.md)
- [Session Data README](../sessions/README.md)

## 📝 Hinweise

- Alle Dateien sind im JSON-Format für einfache Verarbeitung
- Payloads sind als JSON-Strings gespeichert (können mit `json.loads()` geparst werden)
- Timestamps sind im ISO-Format
- Die Daten sind für GitHub geeignet (keine großen Binärdaten)

