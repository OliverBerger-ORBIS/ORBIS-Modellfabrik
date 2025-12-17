# DRILL Session Analysis Data

Diese Dateien enthalten die analysierten MQTT-Session-Daten für das **DRILL (Bohrstation)** Modul.

## Zweck

Die Analyse-Scripts extrahieren alle DRILL-relevante Topics und Payloads aus Session-Log-Dateien, um strukturierte JSON-Daten für die Entwicklung von Beispiel-Anwendungen bereitzustellen.

## Datei-Namenskonvention

Jede Session generiert mehrere Dateien:

- `{session-name}_metadata.json` - Gesamt-Statistiken und Metadaten
- `{session-name}_drill_connection.json` - Connection-Status Messages
- `{session-name}_drill_state.json` - State-Update Messages
- `{session-name}_drill_order.json` - Order-Command Messages
- `{session-name}_drill_instant_action.json` - Instant Action Messages
- `{session-name}_drill_factsheet.json` - Factsheet Messages
- `{session-name}_all_drill_messages.json` - Alle DRILL-relevanten Messages
- `{session-name}_drill_operations.json` - PICK/DRILL/DROP Operationen
- `{session-name}_production_order_context.json` - Messages im PRODUCTION-ORDER Kontext
- `{session-name}_drill_commands_context.json` - Messages im Kontext von DRILL-Commands

## Relevante Topics

### Direkte DRILL-Topics
- `module/v1/ff/SVR4H76449/connection` - Connection Status
- `module/v1/ff/SVR4H76449/state` - State Updates
- `module/v1/ff/SVR4H76449/order` - Order Commands
- `module/v1/ff/SVR4H76449/instantAction` - Instant Actions
- `module/v1/ff/SVR4H76449/factsheet` - Factsheet

### NodeRed-enriched Topics
- `module/v1/ff/NodeRed/SVR4H76449/connection` - Connection (NodeRed enriched)
- `module/v1/ff/NodeRed/SVR4H76449/state` - State (NodeRed enriched)
- `module/v1/ff/NodeRed/SVR4H76449/factsheet` - Factsheet (NodeRed)

### Weitere relevante Topics
- `ccu/order/active` - CCU Active Order
- `ccu/order/completed` - CCU Completed Order
- `ccu/order/request` - CCU Order Request
- `ccu/state/calibration/SVR4H76449` - DRILL Calibration State
- `ccu/set/calibration` - CCU Calibration Commands
- `ccu/pairing/state` - CCU Pairing State (enthält DRILL Info)

## Datenformat

### Metadata-Datei
```json
{
  "session_name": "auftrag-blau_1",
  "analysis_timestamp": "2025-12-17T...",
  "drill_serial": "SVR4H76449",
  "total_messages": 1234,
  "drill_relevant_messages": 56,
  "topic_counts": {...},
  "commands_found": {"PICK": 10, "DRILL": 8, "DROP": 5},
  "drill_operations_count": 23,
  ...
}
```

### Message-Format
Jede Message enthält:
```json
{
  "timestamp": "2025-12-17T10:30:00.000Z",
  "topic": "module/v1/ff/SVR4H76449/state",
  "payload": "{...}" // JSON-String oder Objekt
}
```

## DRILL-spezifische Commands

- **PICK** - Workpiece aufnehmen
- **DRILL** - Bohren (Production-Operation)
- **DROP** - Workpiece ablegen

## Verwendung

Die Scripts können für einzelne Sessions oder alle Sessions ausgeführt werden:

```bash
# Einzelne Session
python3 scripts/analyze_drill_sessions.py data/omf-data/sessions/auftrag-blau_1.log

# Alle Sessions (Bash-Loop)
for log in data/omf-data/sessions/*.log; do
  python3 scripts/analyze_drill_sessions.py "$log"
done
```

## Wichtige Erkenntnisse

- **DRILL** ist primär für Production-Operationen zuständig (PRODUCTION-ORDER)
- **Commands**: PICK → DRILL → DROP (Standard-Produktionssequenz)
- **Kein TXT-Controller**: DRILL kommuniziert nur über OPC-UA/NodeRed
- **Production Duration**: DRILL-Operationen haben eine definierte Dauer (typisch 5-10 Sekunden)

## Nächste Schritte

Diese Daten werden verwendet, um:
1. DRILL-spezifische Beispiel-Anwendungen zu entwickeln
2. Production-Status-Visualisierungen zu erstellen
3. Command-History-Features zu implementieren
