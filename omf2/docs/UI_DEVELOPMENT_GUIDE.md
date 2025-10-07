# 🎨 OMF2 UI Development Guide

## 📋 Übersicht

Dieser Guide definiert die Standards und Best Practices für die Entwicklung von UI Tabs und Subtabs in omf2/, basierend auf der implementierten Architektur und den bewährten Patterns aus `message_center_tab.py` und `generic_steering_tab.py`.

## 🏗️ **Architektur-Prinzipien**

### **0. OBLIGATORISCHE Funktionssignatur (KRITISCH)**
```python
# ✅ KORREKT: Alle render_*_tab() Funktionen MÜSSEN diese Signatur haben
def render_my_tab(gateway=None, registry_manager=None):
    """Render My Tab
    
    Args:
        gateway: [Domain]Gateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    # Fallback-Initialisierung falls Parameter nicht übergeben
    if not gateway:
        gateway = get_my_gateway()
    if not registry_manager:
        registry_manager = get_registry_manager()
```

**🚨 KRITISCHE REGEL FÜR AGENTS:**
- **ALLE** `render_*_tab()` Funktionen MÜSSEN `(gateway, registry_manager)` Parameter haben
- **KEINE** Ausnahmen ohne explizite User-Freigabe
- **ALWAYS** prüfen vor jeder Implementierung
- **LOGGER-SYMBOLE:** Verwende UISymbols für konsistente Logger-Symbole

### **1. Gateway-Pattern (OBLIGATORISCH)**

**🚨 KRITISCH: Domain-spezifische Patterns verwenden!**

#### **Admin Domain (direkte Factory - funktioniert):**
```python
# ✅ KORREKT: Admin Gateway
from omf2.factory.gateway_factory import get_admin_gateway

def render_admin_tab():
    admin_gateway = get_admin_gateway()
    if not admin_gateway:
        st.error(f"{UISymbols.get_status_icon('error')} Admin Gateway not available")
        return
```

#### **CCU/NodeRED Domain (Session State - VERHINDERT Connection Loops):**
```python
# ✅ KORREKT: CCU Gateway mit Session State
def render_ccu_tab(ccu_gateway=None, registry_manager=None):
    if not ccu_gateway:
        if 'ccu_gateway' not in st.session_state:
            from omf2.factory.gateway_factory import get_gateway_factory
            gateway_factory = get_gateway_factory()
            st.session_state['ccu_gateway'] = gateway_factory.get_ccu_gateway()
        ccu_gateway = st.session_state['ccu_gateway']
```

**🚨 WARNUNG:** Direkter Factory-Aufruf bei CCU/NodeRED verursacht Connection Loops!
**🎯 REFERENZ:** Admin = direkte Factory | CCU/NodeRED = Session State

### **3. Environment Switch Pattern (OBLIGATORISCH)**

**🚨 KRITISCH: Verwende Environment Switch Utility für saubere Environment-Wechsel!**

#### **Environment Switch (verhindert Connection Loops):**
```python
# ✅ KORREKT: Environment Switch mit automatischem UI-Refresh
from omf2.ui.utils.environment_switch import switch_ccu_environment

def switch_environment(new_env: str):
    switch_ccu_environment(new_env)
    # UI wird automatisch refreshed!
```

**🚨 WARNUNG:** Niemals `client.reconnect_environment()` direkt verwenden!

### **2. Singleton-Pattern (OBLIGATORISCH)**
```python
# ✅ KORREKT: Singleton-Komponenten verwenden
from omf2.registry.manager.registry_manager import RegistryManager
from omf2.common.logger import get_logger

# Registry Manager aus Session State
registry_manager = st.session_state.get('registry_manager')
if not registry_manager:
    st.warning(f"{UISymbols.get_status_icon('warning')} Registry Manager not available")
    return

# Logger verwenden
logger = get_logger(__name__)
```

### **3. UI-Refresh-Pattern (OBLIGATORISCH)**
```python
# ✅ KORREKT: request_refresh() verwenden
from omf2.ui.utils.ui_refresh import request_refresh

if st.button("Action"):
    # Business Logic
    success = perform_action()
    if success:
        request_refresh()  # Statt st.rerun()
        st.success("Action completed")
```

## 📁 **Tab-Struktur Standards**

### **1. Haupttab-Struktur**
```python
#!/usr/bin/env python3
"""
My Tab - Beschreibung der Funktionalität
Gateway-Pattern konform: Nutzt [Domain]Gateway aus Gateway-Factory
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.factory.gateway_factory import get_[domain]_gateway
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_my_tab():
    """Render My Tab - Standard konform"""
    logger.info("🎯 Rendering My Tab")
    
    try:
        # Header mit UISymbols
        st.subheader(f"{UISymbols.get_tab_icon('my_tab')} My Tab")
        st.markdown("**Description of functionality**")
        
        # Gateway-Pattern: Get Gateway from Factory
        gateway = get_[domain]_gateway()
        if not gateway:
            st.error(f"{UISymbols.get_status_icon('error')} Gateway not available")
            return
        
        # Connection Info via Gateway
        conn_info = gateway.get_connection_info()
        
        # Registry Manager aus Session State
        registry_manager = st.session_state.get('registry_manager')
        
        # Status-Anzeige
        if conn_info['connected']:
            st.success(f"🔗 **Connected:** {conn_info['client_id']}")
        else:
            st.error(f"🔴 **Disconnected:** {conn_info['client_id']}")
        
        # Subtabs mit UISymbols
        tab1, tab2, tab3 = st.tabs([
            f"{UISymbols.get_functional_icon('dashboard')} Overview",
            f"{UISymbols.get_functional_icon('settings')} Configuration", 
            f"{UISymbols.get_functional_icon('debug')} Debug"
        ])
        
        with tab1:
            _render_overview_subtab(gateway, registry_manager)
        
        with tab2:
            _render_configuration_subtab(gateway, registry_manager)
        
        with tab3:
            _render_debug_subtab(gateway, registry_manager)
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} My Tab error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} My Tab failed: {e}")


def _render_overview_subtab(gateway, registry_manager):
    """Render Overview Subtab"""
    from omf2.ui.my_domain.my_tab.overview_subtab import render_overview_subtab
    render_overview_subtab(gateway, registry_manager)


def _render_configuration_subtab(gateway, registry_manager):
    """Render Configuration Subtab"""
    from omf2.ui.my_domain.my_tab.configuration_subtab import render_configuration_subtab
    render_configuration_subtab(gateway, registry_manager)


def _render_debug_subtab(gateway, registry_manager):
    """Render Debug Subtab"""
    from omf2.ui.my_domain.my_tab.debug_subtab import render_debug_subtab
    render_debug_subtab(gateway, registry_manager)
```

### **2. Subtab-Struktur**
```python
#!/usr/bin/env python3
"""
Overview Subtab - Beschreibung der Subtab-Funktionalität
Gateway-Pattern konform: Nutzt [Domain]Gateway
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_overview_subtab(gateway, registry_manager):
    """Render Overview Subtab
    
    Args:
        gateway: [Domain]Gateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("📊 Rendering Overview Subtab")
    
    try:
        st.subheader(f"{UISymbols.get_functional_icon('dashboard')} Overview")
        st.markdown("**Detailed overview functionality**")
        
        # Registry-Daten verwenden
        if registry_manager:
            stats = registry_manager.get_registry_stats()
            st.info(f"{UISymbols.get_status_icon('info')} **Registry:** {stats['topics_count']} topics loaded")
        
        # Business Logic über Gateway
        if st.button(f"{UISymbols.get_status_icon('send')} Perform Action"):
            try:
                result = gateway.perform_action()
                if result:
                    request_refresh()  # UI-Refresh
                    st.success(f"{UISymbols.get_status_icon('success')} Action completed")
                else:
                    st.error(f"{UISymbols.get_status_icon('error')} Action failed")
            except Exception as e:
                logger.error(f"Action failed: {e}")
                st.error(f"{UISymbols.get_status_icon('error')} Action failed: {e}")
        
        # Weitere UI-Elemente...
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Overview Subtab error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Overview Subtab failed: {e}")
```

## 🎯 **UISymbols Integration (OBLIGATORISCH)**

### **1. Imports**
```python
# ✅ OBLIGATORISCH: UISymbols importieren
from omf2.ui.common.symbols import UISymbols
```

### **2. Tab-Icons**
```python
# ✅ KORREKT: Tab-Icons verwenden
st.subheader(f"{UISymbols.get_tab_icon('my_tab')} My Tab")

# Für Subtabs
tab1, tab2 = st.tabs([
    f"{UISymbols.get_functional_icon('dashboard')} Overview",
    f"{UISymbols.get_functional_icon('settings')} Settings"
])
```

### **3. Status-Icons**
```python
# ✅ KORREKT: Status-Icons verwenden
st.success(f"{UISymbols.get_status_icon('success')} Operation completed")
st.error(f"{UISymbols.get_status_icon('error')} Operation failed")
st.warning(f"{UISymbols.get_status_icon('warning')} Warning message")
st.info(f"{UISymbols.get_status_icon('info')} Information")
```

### **4. Functional-Icons**
```python
# ✅ KORREKT: Functional-Icons verwenden
if st.button(f"{UISymbols.get_status_icon('send')} Send Message"):
    # Action

if st.button(f"{UISymbols.get_functional_icon('search')} Search"):
    # Search
```

## 🔄 **UI-Refresh-Pattern (OBLIGATORISCH)**

### **1. request_refresh() verwenden**
```python
# ✅ KORREKT: request_refresh() statt st.rerun()
from omf2.ui.utils.ui_refresh import request_refresh

if st.button("Action"):
    success = perform_action()
    if success:
        request_refresh()  # Einmaliger Refresh
        st.success("Action completed")
```

### **2. NIEMALS st.rerun() verwenden**
```python
# ❌ FALSCH: st.rerun() vermeiden
if st.button("Action"):
    st.rerun()  # Kann zu Race Conditions führen

# ✅ KORREKT: request_refresh() verwenden
if st.button("Action"):
    request_refresh()  # Thread-sicher
```

## 🏗️ **Architektur-Komponenten (OBLIGATORISCH)**

### **1. Gateway-Factory Pattern**
```python
# ✅ KORREKT: Gateway über Factory
from omf2.factory.gateway_factory import get_admin_gateway, get_ccu_gateway, get_nodered_gateway

# Admin Gateway
admin_gateway = get_admin_gateway()
if not admin_gateway:
    st.error("Admin Gateway not available")
    return

# CCU Gateway
ccu_gateway = get_ccu_gateway()
if not ccu_gateway:
    st.error("CCU Gateway not available")
    return
```

### **2. Registry Manager (Singleton)**
```python
# ✅ KORREKT: Registry Manager aus Session State
registry_manager = st.session_state.get('registry_manager')
if not registry_manager:
    st.warning("Registry Manager not available")
    return

# Registry-Daten verwenden
topics = registry_manager.get_topics()
templates = registry_manager.get_templates()
stats = registry_manager.get_registry_stats()
```

### **3. Logger (Singleton)**
```python
# ✅ KORREKT: Logger verwenden
from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Logging in Komponenten
logger.info("Rendering component")
logger.error(f"Error occurred: {e}")
```

## 📋 **Error-Handling (OBLIGATORISCH)**

### **1. Try-Catch für alle Gateway-Calls**
```python
def render_my_component():
    try:
        # Gateway-Call
        result = gateway.perform_action()
        if result:
            st.success("Action completed")
        else:
            st.error("Action failed")
    except Exception as e:
        logger.error(f"Gateway call failed: {e}")
        st.error(f"Action failed: {e}")
```

### **2. Gateway-Verfügbarkeit prüfen**
```python
def render_my_tab():
    gateway = get_my_gateway()
    if not gateway:
        st.error(f"{UISymbols.get_status_icon('error')} Gateway not available")
        return
    
    # Weitere Logik...
```

### **3. Registry Manager prüfen**
```python
def render_my_component():
    registry_manager = st.session_state.get('registry_manager')
    if not registry_manager:
        st.warning(f"{UISymbols.get_status_icon('warning')} Registry Manager not available")
        return
    
    # Registry-Daten verwenden...
```

## 🎨 **UI-Standards (OBLIGATORISCH)**

### **1. Header-Struktur**
```python
# ✅ KORREKT: Header mit UISymbols
st.subheader(f"{UISymbols.get_tab_icon('my_tab')} My Tab")
st.markdown("**Description of functionality**")
```

### **2. Status-Anzeige**
```python
# ✅ KORREKT: Status mit UISymbols
if conn_info['connected']:
    st.success(f"🔗 **Connected:** {conn_info['client_id']}")
else:
    st.error(f"🔴 **Disconnected:** {conn_info['client_id']}")
```

### **3. Button-Standards**
```python
# ✅ KORREKT: Buttons mit UISymbols
if st.button(f"{UISymbols.get_status_icon('send')} Send Message"):
    # Action

if st.button(f"{UISymbols.get_functional_icon('search')} Search"):
    # Search
```

## 📁 **Datei-Struktur Standards**

### **1. Tab-Struktur**
```
omf2/ui/[domain]/[tab_name]/
├── [tab_name]_tab.py          # Haupttab
├── overview_subtab.py         # Overview Subtab
├── configuration_subtab.py    # Configuration Subtab
├── debug_subtab.py           # Debug Subtab
└── __init__.py               # Package init
```

### **2. Naming Conventions**
```python
# Tab-Dateien
[tab_name]_tab.py              # Haupttab
[function]_subtab.py           # Subtab

# Funktionen
render_[tab_name]_tab()        # Haupttab-Funktion
render_[function]_subtab()      # Subtab-Funktion
_render_[function]_subtab()    # Private Subtab-Funktion
```

## 🚫 **Anti-Patterns (VERMEIDEN)**

### **1. Direkte MQTT-Client Verwendung**
```python
# ❌ FALSCH: Direkte MQTT-Client Verwendung
from omf2.admin.admin_mqtt_client import get_admin_mqtt_client
client = get_admin_mqtt_client()
client.publish(topic, message)

# ✅ KORREKT: Gateway verwenden
from omf2.factory.gateway_factory import get_admin_gateway
gateway = get_admin_gateway()
gateway.send_message(topic, message)
```

### **2. st.rerun() verwenden**
```python
# ❌ FALSCH: st.rerun() verwenden
if st.button("Action"):
    st.rerun()

# ✅ KORREKT: request_refresh() verwenden
if st.button("Action"):
    request_refresh()
```

### **3. Hardcodierte Symbole**
```python
# ❌ FALSCH: Hardcodierte Symbole
st.subheader("📊 My Tab")
st.button("📤 Send Message")

# ✅ KORREKT: UISymbols verwenden
st.subheader(f"{UISymbols.get_tab_icon('my_tab')} My Tab")
st.button(f"{UISymbols.get_status_icon('send')} Send Message")
```

### **4. Direkte Registry-Zugriffe**
```python
# ❌ FALSCH: Direkte Registry-Zugriffe
import yaml
with open("registry/topics.yml") as f:
    topics = yaml.safe_load(f)

# ✅ KORREKT: Registry Manager verwenden
registry_manager = st.session_state.get('registry_manager')
topics = registry_manager.get_topics()
```

## 🧪 **Testing Standards**

### **1. Component Testing**
```python
# Test-Script für neue Komponenten
def test_my_tab():
    """Test My Tab component"""
    try:
        from omf2.ui.my_domain.my_tab.my_tab import render_my_tab
        print("✅ My Tab imports successfully")
    except Exception as e:
        print(f"❌ My Tab import failed: {e}")
```

### **2. Symbol Consistency Testing**
```python
# Test-Script für Symbol-Konsistenz
def test_symbol_consistency():
    """Test symbol consistency"""
    from omf2.ui.common.symbols import UISymbols
    
    # Test tab icons
    tab_icon = UISymbols.get_tab_icon('my_tab')
    assert tab_icon is not None
    
    # Test status icons
    status_icon = UISymbols.get_status_icon('success')
    assert status_icon == '✅'
```

## 📋 **Checkliste für neue Komponenten**

### **Vor der Entwicklung:**
- [ ] Gateway-Pattern verstanden
- [ ] UISymbols importiert
- [ ] UI-Refresh-Pattern verstanden
- [ ] Error-Handling geplant

### **Während der Entwicklung:**
- [ ] Gateway über Factory verwenden
- [ ] UISymbols für alle Icons verwenden
- [ ] request_refresh() statt st.rerun()
- [ ] Try-Catch für Gateway-Calls
- [ ] Logger verwenden

### **Nach der Entwicklung:**
- [ ] Alle Symbole konsistent
- [ ] Error-Handling implementiert
- [ ] UI-Refresh funktioniert
- [ ] Tests erstellt
- [ ] Dokumentation aktualisiert

## 🎯 **Migration von omf/dashboard**

### **1. Gateway-Pattern übernehmen**
```python
# omf/dashboard (Alt)
from omf.dashboard.tools.mqtt_client import get_mqtt_client
client = get_mqtt_client()
client.publish(topic, message)

# omf2/ui (Neu)
from omf2.factory.gateway_factory import get_admin_gateway
gateway = get_admin_gateway()
gateway.send_message(topic, message)
```

### **2. UISymbols übernehmen**
```python
# omf/dashboard (Alt)
st.subheader("📊 My Tab")
st.button("📤 Send Message")

# omf2/ui (Neu)
st.subheader(f"{UISymbols.get_tab_icon('my_tab')} My Tab")
st.button(f"{UISymbols.get_status_icon('send')} Send Message")
```

### **3. UI-Refresh übernehmen**
```python
# omf/dashboard (Alt)
if st.button("Action"):
    st.rerun()

# omf2/ui (Neu)
if st.button("Action"):
    request_refresh()
```

## 🚀 **Beispiel: Komplette Tab-Implementierung**

```python
#!/usr/bin/env python3
"""
Example Tab - Beispiel für korrekte Tab-Implementierung
Gateway-Pattern konform: Nutzt AdminGateway aus Gateway-Factory
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.factory.gateway_factory import get_admin_gateway
from omf2.ui.common.symbols import UISymbols
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_example_tab():
    """Render Example Tab - Standard konform"""
    logger.info("🎯 Rendering Example Tab")
    
    try:
        # Header mit UISymbols
        st.subheader(f"{UISymbols.get_tab_icon('example')} Example Tab")
        st.markdown("**Example functionality with proper architecture**")
        
        # Gateway-Pattern: Get AdminGateway from Factory
        admin_gateway = get_admin_gateway()
        if not admin_gateway:
            st.error(f"{UISymbols.get_status_icon('error')} Admin Gateway not available")
            return
        
        # Connection Info via Gateway
        conn_info = admin_gateway.get_connection_info()
        
        # Registry Manager aus Session State
        registry_manager = st.session_state.get('registry_manager')
        
        # Status-Anzeige
        if conn_info['connected']:
            st.success(f"🔗 **Connected:** {conn_info['client_id']}")
        else:
            st.error(f"🔴 **Disconnected:** {conn_info['client_id']}")
        
        # Registry Status
        if registry_manager:
            stats = registry_manager.get_registry_stats()
            st.info(f"{UISymbols.get_status_icon('info')} **Registry:** {stats['topics_count']} topics loaded")
        
        # Subtabs mit UISymbols
        tab1, tab2 = st.tabs([
            f"{UISymbols.get_functional_icon('dashboard')} Overview",
            f"{UISymbols.get_functional_icon('settings')} Configuration"
        ])
        
        with tab1:
            _render_overview_subtab(admin_gateway, registry_manager)
        
        with tab2:
            _render_configuration_subtab(admin_gateway, registry_manager)
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Example Tab error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Example Tab failed: {e}")


def _render_overview_subtab(admin_gateway, registry_manager):
    """Render Overview Subtab"""
    try:
        st.subheader(f"{UISymbols.get_functional_icon('dashboard')} Overview")
        st.markdown("**Example overview functionality**")
        
        # Business Logic über Gateway
        if st.button(f"{UISymbols.get_status_icon('send')} Send Test Message"):
            try:
                result = admin_gateway.send_test_message("test_topic", {"test": "data"})
                if result:
                    request_refresh()  # UI-Refresh
                    st.success(f"{UISymbols.get_status_icon('success')} Message sent successfully")
                else:
                    st.error(f"{UISymbols.get_status_icon('error')} Message sending failed")
            except Exception as e:
                logger.error(f"Message sending failed: {e}")
                st.error(f"{UISymbols.get_status_icon('error')} Message sending failed: {e}")
        
        # Weitere UI-Elemente...
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Overview Subtab error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Overview Subtab failed: {e}")


def _render_configuration_subtab(admin_gateway, registry_manager):
    """Render Configuration Subtab"""
    try:
        st.subheader(f"{UISymbols.get_functional_icon('settings')} Configuration")
        st.markdown("**Example configuration functionality**")
        
        # Configuration UI...
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Configuration Subtab error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Configuration Subtab failed: {e}")
```

---

**Version**: 1.0  
**Datum**: 2024-12-19  
**Status**: Implementierungsbereit  
**Nächster Schritt**: Anwendung bei neuen UI-Komponenten
