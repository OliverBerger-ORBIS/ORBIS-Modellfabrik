# MultiLevelRingBufferHandler Persistence Fix

## Problem

Nach einem Environment-Switch (mock → replay) erschienen keine Logs mehr in der UI. Das MultiLevelRingBufferHandler wurde nicht korrekt am Root-Logger gehalten, wodurch neue Logs nur in der Konsole landeten, nicht in den UI-Buffers.

## Root Cause Analysis

1. **setup_multilevel_ringbuffer_logging(force_new=True)** war implementiert, entfernte alte Handler, aber verifizierte nicht, ob der neue Handler tatsächlich am Root-Logger attached war.
2. **Session State** (log_handler, log_buffers) wurde aktualisiert, aber die Referenz im Session State war nicht identisch mit dem tatsächlich am Logger hängenden Handler.
3. **apply_logging_config()** konnte Handler entfernen ohne sie wieder anzuhängen.

## Solution

### 1. Robuste Handler-Attachment-Verifikation in `setup_multilevel_ringbuffer_logging()`

**Datei:** `omf2/common/logger.py`

```python
def setup_multilevel_ringbuffer_logging(force_new=False):
    """
    Stellt sicher, dass IMMER genau EIN MultiLevelRingBufferHandler am Root-Logger hängt.
    """
    root_logger = logging.getLogger()
    
    # Entferne alte Handler bei force_new
    if force_new:
        handlers_to_remove = [h for h in root_logger.handlers 
                             if isinstance(h, MultiLevelRingBufferHandler)]
        for h in handlers_to_remove:
            root_logger.removeHandler(h)
    
    # Prüfe existierende Handler
    existing = [h for h in root_logger.handlers 
               if isinstance(h, MultiLevelRingBufferHandler)]
    
    if existing:
        handler = existing[0]
    else:
        # Erstelle und attachiere neuen Handler
        handler = MultiLevelRingBufferHandler()
        handler.setFormatter(logging.Formatter('...'))
        handler.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
    
    # KRITISCH: Verifiziere Handler-Attachment
    handler_attached = handler in root_logger.handlers
    if not handler_attached:
        root_logger.addHandler(handler)
        logging.warning("⚠️ Handler was not attached - forced re-attachment")
    
    # Finale Verifikation: Nur EINER sollte existieren
    total_handlers = len([h for h in root_logger.handlers 
                         if isinstance(h, MultiLevelRingBufferHandler)])
    if total_handlers != 1:
        logging.error(f"❌ {total_handlers} Handler (sollte 1 sein)")
    
    return handler, handler.buffers
```

**Änderungen:**
- ✅ Verifiziert, dass Handler tatsächlich attached ist
- ✅ Force-Re-Attachment wenn nötig
- ✅ Prüft, dass nur EINER existiert
- ✅ Detailliertes Logging für Debugging

### 2. Handler-Wiederherstellung nach `apply_logging_config()`

**Datei:** `omf2/common/logging_config.py`

```python
def apply_logging_config():
    """Apply logging configuration from YAML file"""
    # ... existing code ...
    
    # KRITISCH: Nach apply_logging_config() Handler prüfen
    _ensure_multilevel_handler_attached()


def _ensure_multilevel_handler_attached():
    """
    Stellt sicher, dass der Handler am Root-Logger hängt.
    Wird nach apply_logging_config() aufgerufen.
    """
    try:
        import streamlit as st
        
        handler = st.session_state.get('log_handler')
        if not handler:
            return
        
        root_logger = logging.getLogger()
        if handler not in root_logger.handlers:
            root_logger.addHandler(handler)
            logging.warning("⚠️ Handler re-attached after config apply")
        
        # Entferne Duplikate
        multilevel_handlers = [h for h in root_logger.handlers 
                              if isinstance(h, MultiLevelRingBufferHandler)]
        if len(multilevel_handlers) > 1:
            for h in multilevel_handlers:
                if h is not handler:
                    root_logger.removeHandler(h)
    except ImportError:
        pass
```

**Änderungen:**
- ✅ Handler wird nach `apply_logging_config()` geprüft und ggf. re-attached
- ✅ Duplikate werden automatisch entfernt
- ✅ Funktioniert auch ohne Streamlit (ImportError handling)

### 3. Verbesserte Environment-Switch-Verifikation

**Datei:** `omf2/ui/main_dashboard.py`

```python
def _reconnect_logging_system(self):
    """Reconnect logging system after environment switch"""
    try:
        from omf2.common.logger import setup_multilevel_ringbuffer_logging, MultiLevelRingBufferHandler
        import logging
        
        # Force new handler
        handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
        
        # Update session state
        st.session_state['log_handler'] = handler
        st.session_state['log_buffers'] = buffers
        
        # VERIFICATION: Prüfe Handler-Attachment
        root_logger = logging.getLogger()
        handler_attached = handler in root_logger.handlers
        
        multilevel_handlers = [h for h in root_logger.handlers 
                              if isinstance(h, MultiLevelRingBufferHandler)]
        handler_count = len(multilevel_handlers)
        
        if not handler_attached:
            logger.error("❌ Handler NOT attached!")
            root_logger.addHandler(handler)
            logger.warning("⚠️ Forced re-attachment")
        elif handler_count != 1:
            logger.error(f"❌ {handler_count} Handler (sollte 1 sein)")
        else:
            logger.info("✅ Logging system reconnected - Handler verified")
        
        # Test message
        logger.info("🧪 TEST: Environment switch complete")
        
    except Exception as e:
        logger.error(f"❌ Failed to reconnect: {e}")
```

**Änderungen:**
- ✅ Detaillierte Verifikation nach Handler-Erstellung
- ✅ Force-Re-Attachment bei Problemen
- ✅ Test-Nachricht zur Verifikation
- ✅ Prüfung auf exakt EINEN Handler

### 4. Handler-Verifikation im Hauptprogramm

**Datei:** `omf2/omf.py`

```python
# Apply logging configuration from YAML file
apply_logging_config()
logger.info("📋 Logging configuration applied from config file")

# KRITISCH: Handler-Attachment verifizieren
from omf2.common.logging_config import _ensure_multilevel_handler_attached
_ensure_multilevel_handler_attached()
logger.info("✅ Logging handler attachment verified after config apply")
```

**Änderungen:**
- ✅ Handler-Verifikation direkt nach `apply_logging_config()`
- ✅ Stellt sicher, dass Handler beim Startup korrekt ist

## Testing

### Automated Tests

**Datei:** `tests/test_omf2/test_multilevel_handler_persistence.py`

6 umfassende Tests:
1. ✅ Handler attachment after setup
2. ✅ Handler reuse without force_new
3. ✅ Handler replacement with force_new
4. ✅ Handler persistence after apply_logging_config
5. ✅ Logging actually works (logs in buffers)
6. ✅ Environment switch simulation

Alle Tests bestehen erfolgreich.

### Manual Verification

**Datei:** `tests/manual_verify_handler_persistence.py`

Simuliert kompletten Workflow:
1. Initial dashboard setup
2. Environment switch (mock → replay)
3. UI reading logs
4. Additional logging after switch

**Ergebnis:**
- ✅ Handler correctly attached to root logger
- ✅ Exactly ONE MultiLevelRingBufferHandler exists
- ✅ Logs are being captured in UI buffers
- ✅ Handler in session_state matches actual handler

## Acceptance Criteria

✅ **Nach Environment-Switch erscheinen alle System- und Test-Logs wieder korrekt in der UI**
- Logs werden in MultiLevelRingBufferHandler geschrieben
- UI kann Logs aus session_state['log_handler'] lesen

✅ **Es existiert nie mehr als ein aktiver MultiLevelRingBufferHandler am Logger**
- Verifikation in setup_multilevel_ringbuffer_logging()
- Duplikat-Entfernung in _ensure_multilevel_handler_attached()

✅ **Handler- und Buffer-Referenz im Session-State zeigen immer auf den tatsächlich aktiven Handler**
- Session State wird bei jedem Environment-Switch aktualisiert
- Verifikation nach Update stellt Identität sicher

## Key Features

1. **Defensive Programming**: Mehrfache Verifikationen an kritischen Stellen
2. **Automatic Recovery**: Force-Re-Attachment bei Problemen
3. **Duplicate Prevention**: Automatische Entfernung von Duplikaten
4. **Comprehensive Logging**: Debug-Logs für Troubleshooting
5. **Robust Error Handling**: Try-catch blocks mit Fallbacks
6. **Tested Solution**: Sowohl automatisierte als auch manuelle Tests

## Files Modified

1. `omf2/common/logger.py` - setup_multilevel_ringbuffer_logging()
2. `omf2/common/logging_config.py` - apply_logging_config() + _ensure_multilevel_handler_attached()
3. `omf2/ui/main_dashboard.py` - _reconnect_logging_system()
4. `omf2/omf.py` - Handler-Verifikation nach config apply

## Files Created

1. `tests/test_omf2/test_multilevel_handler_persistence.py` - Automated tests
2. `tests/manual_verify_handler_persistence.py` - Manual verification script
3. `SOLUTION_DOCUMENTATION.md` - This document
