# Logging Handler Persistence Fix

## Problem
Nach einem Environment-Switch (z.B. mock → replay) oder einer Logging-Konfigurationsänderung (z.B. `apply_logging_config()`) verschwanden alle Logs aus der System Logs UI. Die Logs erschienen nur noch in der Konsole, aber nicht mehr in den UI-Buffern.

## Root Cause
Der `MultiLevelRingBufferHandler` wurde beim Environment-Switch oder nach `apply_logging_config()` nicht konsistent am Root-Logger gehalten bzw. richtig re-attached. Dadurch landeten neue Log-Ausgaben nur noch in der Konsole, nicht mehr im Buffer für die Streamlit-UI.

## Solution

### New Utility Function: `ensure_ringbufferhandler_attached()`

Location: `omf2/common/logger.py`

Diese zentrale Utility-Funktion wird nach jedem Logging-Konfigurations-Update und jedem Environment-Switch aufgerufen. Sie stellt sicher, dass:

1. Der Handler aus dem Session State am Root-Logger hängt
2. Es nur EINEN `MultiLevelRingBufferHandler` gibt (keine Duplikate)
3. Detachte Handler wieder angehängt werden
4. Handler- und Buffer-Referenzen im Session State korrekt sind

```python
def ensure_ringbufferhandler_attached():
    """
    Stellt sicher, dass der MultiLevelRingBufferHandler konsistent am Root-Logger angehängt ist.
    
    Returns:
        bool: True wenn Handler erfolgreich attached/verifiziert wurde, False sonst
    """
    # Implementation details in omf2/common/logger.py
```

### Integration Points

1. **`apply_logging_config()`** (`omf2/common/logging_config.py`):
   - Ruft `ensure_ringbufferhandler_attached()` nach jeder Logging-Konfigurationsänderung auf
   - Stellt sicher, dass Handler nach Config-Änderungen attached bleibt

2. **`_reconnect_logging_system()`** (`omf2/ui/main_dashboard.py`):
   - Ruft `ensure_ringbufferhandler_attached()` nach Environment-Switch auf
   - Vereinfacht die Verifizierungs-Logik

3. **`omf.py`** (Entry Point):
   - Ruft `ensure_ringbufferhandler_attached()` nach initialem Config-Apply auf
   - Stellt sicheres Setup beim App-Start sicher

### Backward Compatibility

Die alte `_ensure_multilevel_handler_attached()` Funktion in `omf2/common/logging_config.py` wurde als DEPRECATED markiert und delegiert an die neue Utility-Funktion. Dies gewährleistet Rückwärtskompatibilität für existierenden Code.

## Testing

### Unit Tests
Location: `tests/test_omf2/test_multilevel_handler_persistence.py`

- `test_handler_attachment_after_setup()` - Handler Attachment nach Setup
- `test_handler_reuse_without_force_new()` - Handler Wiederverwendung
- `test_handler_replacement_with_force_new()` - Handler Replacement mit force_new
- `test_handler_persistence_after_apply_logging_config()` - Handler Persistenz nach Config
- `test_logging_actually_works()` - Logs werden tatsächlich gecaptured
- `test_environment_switch_simulation()` - Environment Switch Simulation
- **NEW**: `test_ensure_ringbufferhandler_attached_without_streamlit()` - Graceful Handling ohne Streamlit
- **NEW**: `test_ensure_ringbufferhandler_reattaches_detached_handler()` - Re-Attachment von detachten Handlers
- **NEW**: `test_ensure_ringbufferhandler_removes_duplicates()` - Entfernung von Duplikat-Handlers

**Result**: ✅ 9/9 tests passing

### Integration Tests
Location: `tests/test_omf2/test_logging_integration.py`

- `test_complete_workflow()` - Complete Workflow: Setup → Config Change → Env Switch → Verification
- `test_handler_persistence_across_multiple_config_changes()` - Handler Persistenz über 5 Config-Änderungen

**Result**: ✅ 2/2 tests passing

## Acceptance Criteria

- [x] Nach jedem Environment-Switch UND nach jeder Logging-Konfigurationsänderung (`apply_logging_config()`) erscheinen alle System- und Test-Logs weiterhin in der System Logs UI
- [x] Es existiert nie mehr als ein aktiver `MultiLevelRingBufferHandler` am Logger
- [x] Handler- und Buffer-Referenz im Session-State zeigen immer auf den tatsächlich aktiven Handler
- [x] Alle Tests bestehen

## Manual Verification Steps

1. OMF2 Dashboard starten
2. System Logs UI öffnen und Logs prüfen
3. `apply_logging_config()` aufrufen (z.B. über Log Management Tab)
4. **Erwartung**: Logs erscheinen weiterhin in der System Logs UI ✅
5. Environment-Switch durchführen (z.B. mock → replay)
6. **Erwartung**: Logs erscheinen weiterhin in der System Logs UI ✅

## Files Changed

- `omf2/common/logger.py` - Added `ensure_ringbufferhandler_attached()` utility function
- `omf2/common/logging_config.py` - Updated `apply_logging_config()` to use utility
- `omf2/ui/main_dashboard.py` - Updated `_reconnect_logging_system()` to use utility
- `omf2/omf.py` - Updated entry point to use utility
- `tests/test_omf2/test_multilevel_handler_persistence.py` - Added 3 new unit tests
- `tests/test_omf2/test_logging_integration.py` - NEW FILE: Added 2 integration tests

## References

- Issue: "Nach Environment-Switch oder apply_logging_config verschwinden Logs aus System Logs UI"
- Architecture: Gateway Pattern with MultiLevelRingBufferHandler for Streamlit UI
- Related: `omf2/ui/admin/system_logs/system_logs_tab.py` (UI that displays logs)
