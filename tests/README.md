# ORBIS SmartFactory Tests

Dieses Verzeichnis enthält Tests für die aktiven Komponenten des Projekts.

## Test-Struktur

### ✅ Session Manager Tests
- **`test_helper_apps/test_session_manager_logging.py`** - Session Manager Logging Tests
- **`test_helper_apps/test_session_logger.py`** - Session Logger Tests
- **`test_helper_apps/test_logging_cleanup.py`** - Logging Cleanup Tests

### ✅ OMF3 Tests
OMF3 Tests befinden sich in:
- `omf3/apps/ccu-ui/src/app/.../__tests__/` - Angular/Jest Tests

## Test-Ausführung

### Session Manager Tests
```bash
# Alle Session Manager Tests
python -m pytest tests/test_helper_apps/ -v

# Einzelne Tests
python -m pytest tests/test_helper_apps/test_session_manager_logging.py -v
```

### OMF3 Tests
```bash
# Alle OMF3 Tests
nx test ccu-ui

# Alle Tests (OMF3 + MQTT Client)
nx run-many -t test
```

## Legacy Tests

**Hinweis:** OMF2/Streamlit Tests wurden entfernt, da OMF2 als Legacy markiert ist und durch OMF3 ersetzt wurde.
