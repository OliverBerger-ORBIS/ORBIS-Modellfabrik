# 🤖 Agent Onboarding - OMF2 Architecture Guide

**Version:** 1.0  
**Last updated:** 2025-10-19  
**Author:** OMF Development Team  

---

## 🎯 **Überblick**

Diese Dokumentation ist die **zentrale Anlaufstelle** für alle Cursor AI Agents, die mit dem OMF2-Projekt arbeiten. Sie fasst alle wichtigen Architektur-Prinzipien, Singleton-Patterns und UI-Komponenten-Patterns zusammen.

**🚨 KRITISCH:** Jeder Agent MUSS diese Prinzipien verstehen, bevor er Code-Änderungen vornimmt!

### **⚠️ STOP! MANDATORY READING REQUIRED!**

**Bevor du irgendetwas machst, MUSS du diese Dokumentation lesen:**

1. **📖 MANDATORY DEVELOPMENT METHODOLOGY:** [Development Workflow](../04-howto/development/workflow.md) - **MUSS GELESEN WERDEN!**
2. **📖 DIESE DOKUMENTATION:** [Agent Onboarding Architecture](agent-onboarding-architecture.md) - **MUSS GELESEN WERDEN!**

**🚨 NIEMALS direkt mit Implementierung beginnen ohne diese Dokumentation gelesen zu haben!**
**🚨 NIEMALS spekulieren oder raten - IMMER erst Dokumentation lesen!**
**🚨 NIEMALS "ich mache mal schnell..." - IMMER erst verstehen, dann handeln!**

### **✅ BESTÄTIGUNG ERFORDERLICH**
**Du MUSS bestätigen dass du:**
- ✅ Die Development Workflow-Dokumentation gelesen hast
- ✅ Diese Agent Onboarding Architecture-Dokumentation gelesen hast  
- ✅ Die Methodologie verstanden hast
- ✅ Die Architektur-Prinzipien verstanden hast

**NUR NACH dieser Bestätigung darfst du mit der Arbeit beginnen!**

---

## 🏗️ **OMF2 Architektur-Übersicht**

### **Drei-Schichten-Architektur**
```
┌─────────────────────────────────────────────────────────────┐
│                    UI LAYER                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Main Tabs     │ │   Sub Tabs      │ │   Components    ││
│  │   (Wrapper)     │ │   (Functions)   │ │   (UI Logic)    ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                 BUSINESS LAYER                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Gateways      │ │   Managers      │ │   Factories     ││
│  │   (Routing)     │ │   (Business)    │ │   (Singletons)  ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  TRANSPORT LAYER                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   MQTT Clients  │ │   Registry      │ │   Session State ││
│  │   (Singleton)   │ │   (Singleton)   │ │   (Streamlit)   ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **Singleton-Manager Übersicht**

### **Zentrale Singleton-Manager:**
| **Manager** | **Singleton** | **Session State** | **Factory** | **Domain** | **Zugriff** |
|-------------|---------------|-------------------|-------------|------------|-------------|
| **RegistryManager** | ✅ | ❌ | ✅ | Common | `get_registry_manager()` |
| **I18nManager** | ✅ | ✅ | ❌ | Common | `st.session_state.get("i18n_manager")` |
| **AssetManager** | ✅ | ❌ | ✅ | Common | `get_asset_manager()` |
| **ClientFactory** | ✅ | ❌ | ✅ | Common | `get_client_factory()` |
| **GatewayFactory** | ✅ | ❌ | ✅ | Common | `get_gateway_factory()` |
| **OrderManager** | ✅ | ❌ | ✅ | CCU | `get_order_manager()` |
| **StockManager** | ✅ | ❌ | ✅ | CCU | `get_stock_manager()` |
| **ModuleManager** | ✅ | ❌ | ✅ | CCU | `get_module_manager()` |
| **SensorManager** | ✅ | ❌ | ✅ | CCU | `get_sensor_manager()` |
| **MonitorManager** | ✅ | ❌ | ✅ | CCU | `get_monitor_manager()` |

---

## 🔄 **Singleton-Weitergabe-Patterns**

### **Pattern 1: Session State + Factory Pattern**
```python
# ✅ RICHTIG: Factory erstellt Singleton
def get_ccu_gateway():
    return get_gateway_factory().get_ccu_gateway()

# ✅ RICHTIG: Session State speichert Instanz
if "ccu_gateway" not in st.session_state:
    st.session_state["ccu_gateway"] = get_ccu_gateway()

# ✅ RICHTIG: UI-Komponente holt aus Session State
ccu_gateway = st.session_state.get("ccu_gateway")
```

### **Pattern 2: Direkte Factory-Aufrufe**
```python
# ✅ RICHTIG: Direkter Zugriff über Factory
from omf2.registry.manager.registry_manager import get_registry_manager
registry_manager = get_registry_manager()

# ✅ RICHTIG: Direkter Zugriff über Manager-Factory
from omf2.ccu.order_manager import get_order_manager
order_manager = get_order_manager()
```

### **Pattern 3: Session State + Lazy Loading**
```python
# ✅ RICHTIG: Session State + Error Handling
i18n = st.session_state.get("i18n_manager")
if not i18n:
    logger.error("❌ I18n Manager not found in session state")
    return
```

---

## 🎨 **UI-Komponenten-Patterns**

### **Wrapper-Pattern (Haupt-Tabs)**
```python
def render_ccu_overview_tab(ccu_gateway=None, registry_manager=None):
    """Wrapper für CCU Overview mit Subtabs"""
    
    # 1. Gateway aus Factory holen
    ccu_gateway = get_ccu_gateway()
    
    # 2. Registry Manager holen
    registry_manager = get_registry_manager()
    
    # 3. i18n aus Session State
    i18n = st.session_state.get("i18n_manager")
    
    # 4. Subtabs erstellen
    tab1, tab2, tab3 = st.tabs([...])
    
    # 5. Sub-Komponenten aufrufen
    with tab1:
        render_product_catalog_subtab(ccu_gateway, registry_manager)
```

### **Sub-Komponenten-Pattern**
```python
def render_product_catalog_subtab(ccu_gateway, registry_manager):
    """Sub-Komponente für Product Catalog"""
    
    # 1. i18n aus Session State
    i18n = st.session_state.get("i18n_manager")
    
    # 2. Business Logic über Manager
    order_manager = get_order_manager()
    statistics = order_manager.get_order_statistics()
    
    # 3. UI-Rendering
    st.header("Product Catalog")
    # ... UI-Logic
```

---

## 🏭 **Factory-Patterns**

### **Client Factory (MQTT Clients)**
```python
# ✅ RICHTIG: Factory-Pattern für MQTT Clients
from omf2.factory.client_factory import get_client_factory
client_factory = get_client_factory()
mqtt_client = client_factory.get_mqtt_client("ccu_mqtt_client")
```

### **Gateway Factory (Business Gateways)**
```python
# ✅ RICHTIG: Factory-Pattern für Gateways
from omf2.factory.gateway_factory import get_ccu_gateway
ccu_gateway = get_ccu_gateway()
```

---

## 🚨 **KRITISCHE ARCHITEKTUR-REGELN**

### **Singleton-Regeln:**
1. **Thread-Safety:** Alle Singletons sind thread-safe
2. **Lazy Loading:** Kein File I/O im `__init__`
3. **Session State:** Persistenz über Streamlit-Reruns
4. **Factory Pattern:** Zentrale Erstellung und Verwaltung
5. **Registry-basiert:** Dynamische Konfiguration

### **UI-Pattern-Regeln:**
1. **Wrapper-Pattern:** Haupt-Tabs als Wrapper
2. **Sub-Komponenten:** Funktionale Unterteilung
3. **Manager-Zugriff:** Über Factory oder Session State
4. **i18n-Integration:** Alle UI-Komponenten übersetzt
5. **Error-Handling:** Graceful Fallbacks

### **Weitergabe-Regeln:**
1. **Session State:** Zentrale Instanz-Speicherung
2. **Factory-Aufrufe:** Direkte Singleton-Erstellung
3. **Parameter-Passing:** Gateway/Manager als Parameter
4. **Lazy Loading:** Erst bei Bedarf initialisieren
5. **Thread-Safety:** Lock-basierte Synchronisation

---

## ✅ **BEST PRACTICES**

### **Singleton-Erstellung:**
```python
# ✅ RICHTIG: Factory-Pattern
from omf2.registry.manager.registry_manager import get_registry_manager
registry_manager = get_registry_manager()

# ❌ FALSCH: Direkte Instanziierung
registry_manager = RegistryManager()
```

### **UI-Komponenten:**
```python
# ✅ RICHTIG: Session State + Error Handling
i18n = st.session_state.get("i18n_manager")
if not i18n:
    logger.error("❌ I18n Manager not found")
    return

# ❌ FALSCH: Direkte Instanziierung
i18n = I18nManager()
```

### **Manager-Zugriff:**
```python
# ✅ RICHTIG: Factory + Business Logic
order_manager = get_order_manager()
statistics = order_manager.get_order_statistics()

# ❌ FALSCH: Direkte Instanziierung
order_manager = OrderManager()
```

---

## 🔗 **WICHTIGE DOKUMENTATION**

### **Zentrale Architektur-Dokumente:**
- **[OMF2 Architecture](02-architecture/omf2-architecture.md)** - Vollständige Architektur-Übersicht
- **[OMF2 Registry System](02-architecture/omf2-registry-system.md)** - Registry Manager und OMF-Entitäten
- **[Logging Implementation Guide](04-howto/logging-implementation-guide.md)** - Logging-System

### **Decision Records:**
- **[Singleton-Pattern für MQTT-Client](03-decision-records/01-singleton-pattern-mqtt-client.md)**
- **[Komponenten-Trennung](03-decision-records/03-component-separation-ui-business-logic.md)**
- **[Wrapper-Pattern für Dashboard-Tabs](03-decision-records/04-wrapper-pattern-dashboard-tabs.md)**
- **[Session State Management](03-decision-records/05-session-state-management.md)**
- **[MQTT-Integration](03-decision-records/06-mqtt-integration-central-client.md)**

### **Entwicklungsregeln:**
- **[Development Rules Compliance](03-decision-records/07-development-rules-compliance.md)**
- **[I18n Development Rules](03-decision-records/i18n-development-rules.md)**

---

## 🚀 **QUICK REFERENCE**

### **Häufige Singleton-Zugriffe:**
```python
# Registry Manager
from omf2.registry.manager.registry_manager import get_registry_manager
registry_manager = get_registry_manager()

# I18n Manager
i18n = st.session_state.get("i18n_manager")

# Asset Manager
from omf2.assets import get_asset_manager
asset_manager = get_asset_manager()

# Order Manager
from omf2.ccu.order_manager import get_order_manager
order_manager = get_order_manager()

# CCU Gateway
from omf2.factory.gateway_factory import get_ccu_gateway
ccu_gateway = get_ccu_gateway()
```

### **UI-Komponenten-Struktur:**
```
omf2/ui/
├── main_dashboard.py              # Haupt-Dashboard
├── ccu/
│   ├── ccu_overview_tab.py        # Wrapper-Komponente
│   ├── ccu_overview/
│   │   ├── product_catalog_subtab.py  # Sub-Komponente
│   │   └── customer_order_subtab.py   # Sub-Komponente
│   └── ccu_orders/
│       ├── ccu_orders_tab.py      # Wrapper-Komponente
│       └── production_orders_subtab.py  # Sub-Komponente
└── admin/
    └── system_logs/
        └── system_logs_tab.py     # Wrapper-Komponente
```

---

**🎯 Diese Dokumentation ist die zentrale Anlaufstelle für alle Agent-Onboarding-Fragen!**
