# OMF2 Logging Implementation Guide

**Version:** 1.0  
**Last updated:** 2025-10-16  
**Author:** OMF Development Team  

---

## 🎯 **Überblick**

Dieses Dokument erklärt, wie das OMF2 Logging-System funktioniert und wie Agenten es korrekt implementieren können. Es basiert auf der **MultiLevelRingBufferHandler**-Lösung und der **System Logs UI**-Integration.

---

## 🏗️ **Architektur-Überblick**

### **Drei-Schichten-Logging-System:**

```
┌─────────────────────────────────────────────────────────┐
│  LOGGING LAYER 1: MultiLevelRingBufferHandler          │
├─────────────────────────────────────────────────────────┤
│  • Level-spezifische Ringbuffer (ERROR, WARNING, INFO, DEBUG) │
│  • Thread-sichere Buffer-Verwaltung                    │
│  • Session State Integration                           │
│  • Handler-Persistence nach Environment-Switches      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  LOGGING LAYER 2: OMF2 Logger (get_logger)             │
├─────────────────────────────────────────────────────────┤
│  • Standardisierte Logger-Erstellung                   │
│  • Konsistente Formatierung                            │
│  • Component-basierte Logging                          │
│  • Gateway-Pattern Integration                         │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  LOGGING LAYER 3: System Logs UI                       │
├─────────────────────────────────────────────────────────┤
│  • Admin > System Logs Tab                             │
│  • Level-spezifische Anzeige (ERROR & Warnings Tab)    │
│  • Log-Suche und -Analyse                              │
│  • Export-Funktionalität                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 **1. Logger-Erstellung (FÜR AGENTEN)**

### **✅ KORREKT: OMF2 Logger verwenden**

```python
#!/usr/bin/env python3
"""
Beispiel: Korrekte Logger-Erstellung in OMF2
"""

# ✅ KORREKT: OMF2 Logger importieren und verwenden
from omf2.common.logger import get_logger

# Logger für diese Komponente erstellen
logger = get_logger(__name__)

# Logging verwenden
logger.info("📋 Component initialized successfully")
logger.warning("⚠️ Configuration missing, using defaults")
logger.error("❌ Failed to connect to MQTT broker")
logger.debug("🔧 Debug information for troubleshooting")
```

### **❌ FALSCH: Standard Python Logger**

```python
# ❌ FALSCH: Standard Python Logger verwenden
import logging
logger = logging.getLogger(__name__)  # NICHT verwenden!
```

---

## 🎯 **2. Component-basiertes Logging**

### **Logger-Namen-Konvention:**

```python
# ✅ KORREKT: __name__ verwenden für automatische Komponenten-Identifikation
logger = get_logger(__name__)

# Beispiele für verschiedene Komponenten:
# omf2.ccu.production_order_manager
# omf2.ui.ccu.ccu_orders.production_orders_subtab  
# omf2.admin.admin_gateway
# omf2.common.topic_manager
```

### **Logging-Level verwenden:**

```python
# ✅ KORREKT: Sinnvolle Logging-Level
logger.debug("🔧 Detailed debug information")      # Für Entwicklung/Debugging
logger.info("📋 Normal operation information")     # Für normale Operationen
logger.warning("⚠️ Warning conditions")            # Für Warnungen
logger.error("❌ Error conditions")                # Für Fehler
logger.critical("🚨 Critical conditions")          # Für kritische Fehler
```

---

## 🏢 **3. Gateway-Pattern Integration**

### **Gateway-Komponenten loggen:**

```python
#!/usr/bin/env python3
"""
Beispiel: Gateway-Komponente mit korrektem Logging
"""

from omf2.common.logger import get_logger

class CCUGateway:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.info("🚪 CCU Gateway initialized")
    
    def process_message(self, topic: str, payload: dict):
        self.logger.debug(f"🔧 Processing message: {topic}")
        
        try:
            # Business Logic
            result = self._validate_and_route(topic, payload)
            self.logger.info(f"✅ Message processed successfully: {topic}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Message processing failed: {topic} - {e}")
            raise
```

---

## 🎨 **4. UI-Komponenten Logging**

### **Streamlit UI-Komponenten:**

```python
#!/usr/bin/env python3
"""
Beispiel: UI-Komponente mit korrektem Logging
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)

def render_ccu_orders_tab():
    """Render CCU Orders Tab"""
    logger.info(f"{UISymbols.get_functional_icon('orders')} Rendering CCU Orders Tab")
    
    try:
        # UI Logic
        st.header("CCU Orders")
        
        # Gateway-Zugriff
        from omf2.factory.gateway_factory import get_ccu_gateway
        ccu_gateway = get_ccu_gateway()
        
        if not ccu_gateway:
            logger.error("❌ CCU Gateway not available")
            st.error("CCU Gateway not available")
            return
        
        # Business Logic
        orders = ccu_gateway.get_orders()
        logger.info(f"📋 Retrieved {len(orders)} orders")
        
        # UI Rendering
        _render_orders_table(orders)
        
    except Exception as e:
        logger.error(f"❌ CCU Orders Tab rendering error: {e}")
        st.error(f"CCU Orders Tab failed: {e}")
```

---

## 📊 **5. System Logs UI Integration**

### **Wie Logs in der UI erscheinen:**

Das OMF2 System Logs UI liest Logs aus dem **MultiLevelRingBufferHandler**:

```python
# System Logs UI liest aus Session State
log_handler = st.session_state.get('log_handler')
if not log_handler:
    st.error("No log handler available")
    return

# Level-spezifische Buffer abrufen
error_logs = log_handler.get_buffer('ERROR')
warning_logs = log_handler.get_buffer('WARNING')
info_logs = log_handler.get_buffer('INFO')
debug_logs = log_handler.get_buffer('DEBUG')
```

### **UI-Tabs für Log-Analyse:**

1. **📋 Log History** - Alle Logs mit Filterung
2. **🔍 Log Search** - Suche in Log-Nachrichten
3. **📊 Log Analytics** - Statistiken und Metriken
4. **⚙️ Log Management** - Konfiguration und Export
5. **🚨 Error & Warnings** - Nur kritische Logs

---

## 🧪 **6. Test-Integration**

### **Logging in Tests:**

```python
#!/usr/bin/env python3
"""
Beispiel: Logging in Tests
"""

import pytest
from omf2.common.logger import get_logger

logger = get_logger(__name__)

def test_ccu_gateway_message_processing():
    """Test CCU Gateway message processing"""
    logger.info("🧪 Starting CCU Gateway message processing test")
    
    # Test Setup
    gateway = CCUGateway()
    
    # Test Execution
    result = gateway.process_message("test/topic", {"test": "data"})
    
    # Verification
    assert result is not None
    logger.info("✅ CCU Gateway message processing test passed")
```

### **Log-Analyse in Tests:**

```python
def test_logging_system_integration():
    """Test that logging system works correctly"""
    logger = get_logger(__name__)
    
    # Test logging
    logger.info("Test log message")
    logger.error("Test error message")
    
    # Verify logs appear in UI buffers
    log_handler = st.session_state.get('log_handler')
    assert log_handler is not None
    
    info_logs = log_handler.get_buffer('INFO')
    error_logs = log_handler.get_buffer('ERROR')
    
    assert len(info_logs) > 0
    assert len(error_logs) > 0
    assert "Test log message" in info_logs[-1]
    assert "Test error message" in error_logs[-1]
```

---

## 🔧 **7. Handler-Persistence (FÜR AGENTEN)**

### **Environment-Switch Handling:**

Das System stellt automatisch sicher, dass Logs nach Environment-Switches weiterhin funktionieren:

```python
# ✅ AUTOMATISCH: Handler-Persistence wird automatisch gehandhabt
# Agenten müssen nichts tun - das System kümmert sich darum

# Nach Environment-Switch (mock → replay):
# 1. setup_multilevel_ringbuffer_logging(force_new=True) wird aufgerufen
# 2. ensure_ringbufferhandler_attached() verifiziert Handler
# 3. Session State wird aktualisiert
# 4. Logs erscheinen weiterhin in der UI
```

### **Konfigurationsänderungen:**

```python
# ✅ AUTOMATISCH: Nach apply_logging_config() wird Handler verifiziert
# Agenten müssen nichts tun

# Nach Logging-Konfigurationsänderung:
# 1. apply_logging_config() wird aufgerufen
# 2. _ensure_multilevel_handler_attached() verifiziert Handler
# 3. Logs erscheinen weiterhin in der UI
```

---

## 📋 **8. Best Practices für Agenten**

### **✅ DO's:**

1. **Immer OMF2 Logger verwenden:**
   ```python
   from omf2.common.logger import get_logger
   logger = get_logger(__name__)
   ```

2. **Sinnvolle Logging-Level:**
   ```python
   logger.debug("🔧 Debug info")    # Entwicklung
   logger.info("📋 Normal ops")     # Normal
   logger.warning("⚠️ Warnings")    # Warnungen
   logger.error("❌ Errors")        # Fehler
   ```

3. **Component-basierte Logger-Namen:**
   ```python
   logger = get_logger(__name__)  # Automatische Komponenten-Identifikation
   ```

4. **UI-Icons in Log-Nachrichten:**
   ```python
   logger.info(f"{UISymbols.get_functional_icon('orders')} Processing orders")
   ```

5. **Exception-Handling mit Logging:**
   ```python
   try:
       # Business Logic
       result = process_data()
       logger.info("✅ Processing successful")
   except Exception as e:
       logger.error(f"❌ Processing failed: {e}")
       raise
   ```

### **❌ DON'Ts:**

1. **NICHT Standard Python Logger verwenden:**
   ```python
   # ❌ FALSCH
   import logging
   logger = logging.getLogger(__name__)
   ```

2. **NICHT sys.path.append verwenden:**
   ```python
   # ❌ FALSCH
   import sys
   sys.path.append("...")
   ```

3. **NICHT direkte Buffer-Zugriffe:**
   ```python
   # ❌ FALSCH - Direkter Buffer-Zugriff
   buffers = st.session_state.get('log_buffers')
   ```

4. **NICHT Handler-Persistence manuell handhaben:**
   ```python
   # ❌ FALSCH - System macht das automatisch
   # setup_multilevel_ringbuffer_logging() manuell aufrufen
   ```

---

## 🔍 **9. Log-Analyse für Agenten**

### **Logs in der UI finden:**

1. **Admin > System Logs** öffnen
2. **📋 Log History** Tab für alle Logs
3. **🚨 Error & Warnings** Tab für kritische Logs
4. **🔍 Log Search** Tab für Suche

### **Log-Filterung:**

```python
# In der UI verfügbare Filter:
# - Log Level: ALL, DEBUG, INFO, WARNING, ERROR
# - Max Entries: 10-1000
# - Component: Automatisch basierend auf Logger-Namen
# - Search Query: Text-Suche in Log-Nachrichten
```

### **Log-Export:**

```python
# Logs können exportiert werden als:
# - JSON-Format
# - Gefiltert nach Level, Component, Zeitraum
# - Für weitere Analyse oder Debugging
```

---

## 🚀 **10. Neue Komponenten integrieren**

### **Schritt-für-Schritt für neue Komponenten:**

1. **Logger erstellen:**
   ```python
   from omf2.common.logger import get_logger
   logger = get_logger(__name__)
   ```

2. **Logging implementieren:**
   ```python
   logger.info("📋 Component initialized")
   logger.debug("🔧 Debug information")
   logger.error("❌ Error occurred")
   ```

3. **Tests schreiben:**
   ```python
   def test_component():
       logger = get_logger(__name__)
       logger.info("🧪 Test started")
       # Test logic
       logger.info("✅ Test passed")
   ```

4. **UI-Integration (falls UI-Komponente):**
   ```python
   def render_component():
       logger = get_logger(__name__)
       logger.info("🎨 Rendering component")
       # UI logic
   ```

5. **Verifizieren:**
   - Logs erscheinen in **Admin > System Logs**
   - Logs sind in **Error & Warnings** Tab (falls ERROR/WARNING)
   - Logs sind durchsuchbar in **Log Search**

---

## 📚 **11. Referenz-Implementierungen**

### **Gateway-Pattern:**
- `omf2/ccu/ccu_gateway.py` - CCU Gateway mit Logging
- `omf2/admin/admin_gateway.py` - Admin Gateway mit Logging

### **UI-Komponenten:**
- `omf2/ui/ccu/ccu_orders/ccu_orders_tab.py` - UI-Tab mit Logging
- `omf2/ui/admin/system_logs/system_logs_tab.py` - System Logs UI

### **Business Manager:**
- `omf2/ccu/production_order_manager.py` - Manager mit Logging
- `omf2/ccu/module_manager.py` - Manager mit Logging

### **Tests:**
- `omf2/tests/test_multilevel_handler_persistence.py` - Logging-Tests
- `omf2/tests/test_logging_integration.py` - Integration-Tests

---

## 🎯 **Zusammenfassung für Agenten**

### **Das Wichtigste:**

1. **Immer `from omf2.common.logger import get_logger` verwenden**
2. **`logger = get_logger(__name__)` für automatische Komponenten-Identifikation**
3. **Sinnvolle Logging-Level verwenden (debug, info, warning, error)**
4. **UI-Icons in Log-Nachrichten für bessere Lesbarkeit**
5. **Exception-Handling mit Logging kombinieren**
6. **Logs erscheinen automatisch in Admin > System Logs**
7. **Handler-Persistence wird automatisch gehandhabt**

### **Verifikation:**

- ✅ Logs erscheinen in **Admin > System Logs**
- ✅ Logs sind in **Error & Warnings** Tab (falls ERROR/WARNING)
- ✅ Logs sind durchsuchbar in **Log Search**
- ✅ Logs werden nach Environment-Switches weiterhin angezeigt
- ✅ Logs werden nach Konfigurationsänderungen weiterhin angezeigt

---

*Letzte Aktualisierung: 2025-10-16*
