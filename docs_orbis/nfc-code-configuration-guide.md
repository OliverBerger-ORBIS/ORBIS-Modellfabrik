# NFC Code Configuration Guide

## Übersicht

Die NFC-Code-Konfiguration wurde zentralisiert und verwendet eine YAML-Konfigurationsdatei für alle NFC-Code-bezogenen Operationen im ORBIS-Projekt.

## 📁 Konfigurationsdatei

**Pfad:** `src_orbis/mqtt/config/nfc_code_config.yml`

### Struktur

```yaml
metadata:
  version: "2.0"
  description: "NFC Code Mapping mit erweiterten Informationen"
  last_updated: "2025-08-27"
  author: "Orbis Development Team"

nfc_codes:
  "040a8dca341291":
    friendly_id: "R1"
    color: "RED"
    quality_check: "OK"
    description: "Rotes Werkstück 1"
  
  # ... weitere NFC-Codes

quality_check_options:
  - "OK"
  - "NOT-OK"
  - "PENDING"
  - "FAILED"

colors:
  - "RED"
  - "WHITE" 
  - "BLUE"

template_placeholders:
  nfc_code: "<nfcCode>"
  workpiece_id: "<workpieceId>"
  color: "<color>"
  quality: "<quality>"

mqtt_paths:
  - ["workpieceId"]
  - ["metadata", "workpiece", "workpieceId"]
  - ["action", "metadata", "workpiece", "workpieceId"]
  - ["workpiece", "workpieceId"]
  - ["loadId"]
  - ["id"]
```

## 🔧 NFCCodeManager Klasse

### Verwendung

```python
from src_orbis.mqtt.tools.nfc_code_manager import NFCCodeManager

# Manager initialisieren
manager = NFCCodeManager()

# Grundfunktionen
friendly_name = manager.get_friendly_name("040a8dca341291")  # → "R1"
nfc_code = manager.get_nfc_code("R1")  # → "040a8dca341291"
is_valid = manager.validate_nfc_code("040a8dca341291")  # → True

# Erweiterte Funktionen
red_codes = manager.get_nfc_codes_by_color("RED")
ok_codes = manager.get_nfc_codes_by_quality("OK")
stats = manager.get_statistics()
```

### Backward Compatibility

```python
# Alte Funktionen funktionieren weiterhin
from src_orbis.mqtt.tools.nfc_code_manager import get_friendly_name, get_nfc_code

friendly_name = get_friendly_name("040a8dca341291")
nfc_code = get_nfc_code("R1")
```

## 📊 Dashboard Integration

### Tab "Einstellungen" → "NFC-Codes"

- **Collapsible Farb-Sektionen:** RED, WHITE, BLUE
- **Tabellarische Darstellung:** NFC-Code, Friendly-ID, Quality-Check, Beschreibung
- **Statistiken:** Gesamtanzahl und pro Farbe
- **Quelle:** Zentrale YAML-Konfiguration

## 🔄 Migration von alter Funktionalität

### Gelöschte Dateien

- ❌ `src_orbis/mqtt/tools/nfc_code_mapping.py` - Ersetzt durch NFCCodeManager
- ❌ `src_orbis/mqtt/tools/analyze_existing_nfc_codes.py` - Funktionalität integriert
- ❌ `src_orbis/mqtt/tools/nfc_analysis_session.py` - Funktionalität integriert

### Migrierte Dateien

- ✅ `ccu_template_analyzer.py` - Verwendet NFCCodeManager
- ✅ `txt_template_analyzer.py` - Verwendet NFCCodeManager
- ✅ `unified_type_recognition.py` - Verwendet NFCCodeManager
- ✅ `module_mapping_utils.py` - NFC-Funktionen verwenden NFCCodeManager
- ✅ `aps_dashboard.py` - Lädt NFC-Codes aus YAML-Konfiguration (integriert) ⚠️ **VERALTET: Wurde durch OMF Dashboard ersetzt**

## 🧪 Tests

### Unit Tests

**Pfad:** `tests_orbis/test_nfc_code_manager.py`

```bash
cd tests_orbis
python test_nfc_code_manager.py
```

### Test-Coverage

- ✅ Initialisierung mit YAML-Konfiguration
- ✅ Alle NFC-Manager-Funktionen
- ✅ Backward Compatibility
- ✅ Fehlerbehandlung
- ✅ Konfiguration-Reload

## 📋 NFC-Code Übersicht

### Rote Werkstücke (R1-R8)
- **Quality-Check OK:** R1, R2, R3
- **Quality-Check NOT-OK:** R4, R5, R6, R7, R8

### Weiße Werkstücke (W1-W8)
- **Quality-Check OK:** W1, W2, W3
- **Quality-Check NOT-OK:** W4, W5, W6, W7, W8

### Blaue Werkstücke (B1-B8)
- **Quality-Check OK:** B1, B2, B3
- **Quality-Check NOT-OK:** B4, B5, B6, B7, B8

## ⚠️ Wichtige Hinweise

1. **Friendly-IDs nur für Anzeige:** In MQTT-Nachrichten werden immer echte NFC-Codes verwendet
2. **Zentrale Konfiguration:** Änderungen nur in `nfc_code_config.yml`
3. **Backward Compatibility:** Bestehender Code funktioniert weiterhin
4. **Quality-Check:** Erste 3 NFC-Codes pro Farbe haben Status "OK"

## 🔄 Wartung

### Neue NFC-Codes hinzufügen

1. YAML-Konfiguration bearbeiten
2. Quality-Check-Status setzen
3. Beschreibung hinzufügen
4. Dashboard automatisch aktualisiert

### Konfiguration aktualisieren

```python
manager = NFCCodeManager()
success = manager.reload_config()
```

## 📈 Statistiken

- **Gesamt NFC-Codes:** 24
- **Farben:** 3 (RED, WHITE, BLUE)
- **Quality-Check-Status:** 4 (OK, NOT-OK, PENDING, FAILED)
- **MQTT-Pfade:** 6 verschiedene Pfade für NFC-Code-Erkennung

---

*Letzte Aktualisierung: 2025-08-27*
