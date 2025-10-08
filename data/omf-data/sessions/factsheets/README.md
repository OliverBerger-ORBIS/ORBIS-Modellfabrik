# 📋 Factsheet-Verzeichnis

> ⚠️ **VERALTET** - Dieses Verzeichnis wird durch die neue Struktur ersetzt!
> 
> **Neue Struktur ab Oktober 2025:**
> - **Preload-Factsheets:** → `data/omf-data/test_topics/preloads/`
> - **Test-Topics:** → `data/omf-data/test_topics/`
> - **Dokumentation:** → [Test-Topics README](../../test_topics/README.md)

---

Dieses Verzeichnis enthält JSON-Dateien mit Factsheet-Messages, die vor dem Session-Replay an den MQTT-Broker gesendet werden können.

## 🎯 Zweck

Die Replay Station kann optional alle verfügbaren Factsheet-Messages an den Broker senden, bevor eine Session abgespielt wird. Dies stellt sicher, dass alle Module als "konfiguriert" erkannt werden.

## 📁 Dateiformat

Jede JSON-Datei sollte folgende Struktur haben:

```json
{
  "topic": "module/v1/ff/SVR3QA0022/factsheet",
  "payload": "{\"headerId\":1,\"timestamp\":\"2025-10-01T11:29:59.065Z\",\"version\":\"1.3.0\",\"manufacturer\":\"Fischertechnik\",\"serialNumber\":\"SVR3QA0022\",\"typeSpecification\":{\"seriesName\":\"MOD-FF22+HBW+24V\",\"moduleClass\":\"HBW\"},...}",
  "qos": 0,
  "retain": false,
  "timestamp": "2025-10-01T13:29:59.071731",
  "sequence": 46,
  "type": "interesting"
}
```

## 🔧 Verwendung

1. **Automatisch**: Beim Session-Laden mit aktivierter "Factsheet-Preload" Option
2. **Manuell**: Über den "Factsheets jetzt senden" Button in der Replay Station

## 📊 Verfügbare Factsheets

- `module_v1_ff_SVR3QA0022_factsheet__000046.json` - HBW Module
- `module_v1_ff_SVR4H73275_factsheet__000054.json` - DRILL Module  
- `module_v1_ff_SVR3QA2098_factsheet__000036.json` - MILL Module
- `module_v1_ff_SVR4H76530_factsheet__000042.json` - Module
- `fts_v1_ff_5iO4_factsheet__000060.json` - FTS Module

## 🚀 Hinweise

- Alle JSON-Dateien in diesem Verzeichnis werden automatisch erkannt
- Die Payload ist bereits als JSON-String formatiert
- QoS und Retain-Flags werden aus den Dateien übernommen
- Fehlerhafte Dateien werden übersprungen und geloggt
