# 🏭 OMF2 - ORBIS Modellfabrik Dashboard

**Status:** VOLLSTÄNDIG IMPLEMENTIERT ✅  
**Datum:** 2025-01-07  
**Tests:** 55 Tests erfolgreich ✅  
**Registry-Migration:** ABGESCHLOSSEN ✅  
**Architektur-Cleanup:** ABGESCHLOSSEN ✅  
**Connection Loop Fixes:** IMPLEMENTIERT ✅

## 📋 Übersicht

OMF2 ist die neue, modulare und rollenbasierte Streamlit-Anwendung für die ORBIS-Modellfabrik. Sie ersetzt das bestehende OMF Dashboard mit einer gekapselten, robusten Architektur für MQTT-Kommunikation, Schema-driven Messages und UI-Refresh.

## 🎯 **Hauptziele erreicht:**

- ✅ **Weggekapselte Architektur:** UI bleibt einfach, keine Threading-Probleme
- ✅ **Gateway-Pattern:** Schlanke Fassaden für Business-Operationen  
- ✅ **Registry v2 Integration:** Zentrale Datenverwaltung
- ✅ **Thread-sichere Kommunikation:** Keine Race Conditions
- ✅ **Modulare UI-Struktur:** Rollenbasierte Tab-Generierung
- ✅ **Symbol-System:** Konsistente UI-Symbole mit UISymbols
- ✅ **Schema-driven Architecture:** Direkte JSON-Schema Integration ohne Templates
- ✅ **Connection Loop Prevention:** Robuste MQTT Connection Management
- ✅ **Environment Switch:** Automatischer UI-Refresh bei Environment-Wechsel
- ✅ **Shopfloor Layout System:** Wiederverwendbare 3×4 Grid-Komponente mit SVG-Icons

## 🏗️ **Architektur**

```
Streamlit-UI (omf2/ui/)
    │
    ▼
Business Logic (omf2/ccu/, omf2/admin/)
    ├── ModuleManager (Schema-basierte Message-Verarbeitung) ✅
    ├── WorkpieceManager (Registry-basierte Icons) ✅
    └── AdminGateway (System-Verwaltung) ✅
        │
        ▼
Gateway-Factory (Singleton) ✅
    ├── CcuGateway (Registry v2) ✅
    ├── NoderedGateway (Registry v2) ✅
    └── AdminGateway (Registry v2) ✅
        │
        ▼
Registry Manager (Singleton) ✅
    ├── Topics, Schemas (direkte Abfrage) ✅
    ├── MQTT Clients, Workpieces ✅
    └── Modules, Stations, TXT Controllers ✅
        │
        ▼
MQTT Clients (Singleton) ✅
    ├── CCU MQTT Client ✅
    ├── Node-RED MQTT Client ✅
    └── Admin MQTT Client ✅
```

## 📁 **Projektstruktur**

```
omf2/
├── docs/                           # 📚 Dokumentation
│   ├── ARCHITECTURE.md             # Architektur-Übersicht
│   ├── IMPLEMENTATION_STATUS.md    # Implementierungsstatus
│   ├── PROJECT_STRUCTURE.md        # Projektstruktur & Prinzipien
│   ├── REFACTORING_BACKLOG.md     # Migration von omf/dashboard
│   ├── UI_DEVELOPMENT_GUIDE.md    # UI-Entwicklungsstandards
│   ├── UI_SYMBOL_STYLE_GUIDE.md   # Symbol-Style-Guide
│   └── CCU_DOMAIN_SYMBOL_GUIDELINES.md # CCU-Domain Guidelines
├── registry/                       # 📊 Registry v2 (vereinfacht)
│   ├── manager/                   # Registry Manager (Singleton)
│   ├── topics/                    # Topic-Definitionen
│   ├── schemas/                   # 44 JSON-Schemas
│   └── *.yml                      # Schemas, Mappings, etc.
├── ui/                           # 🎨 Streamlit UI
│   ├── main_dashboard.py          # Hauptdashboard
│   ├── user_manager.py           # Rollenbasierte Zugriffe
│   ├── common/                    # Gemeinsame UI-Komponenten
│   │   └── symbols.py             # UISymbols (zentral)
│   ├── ccu/                       # CCU-Domain Tabs
│   ├── nodered/                   # Node-RED Tabs
│   └── admin/                     # Admin Tabs & Subtabs
├── factory/                      # 🏭 Factory-Pattern
│   └── gateway_factory.py         # Gateway-Factory
├── ccu/                          # 🏭 CCU-Domain
├── nodered/                      # 🔄 Node-RED-Domain
├── admin/                        # ⚙️ Admin-Domain
├── common/                       # 🔧 Gemeinsame Utilities
└── tests/                        # 🧪 Test-Suite (55 Tests)
```

## 🚀 **Schnellstart**

### **1. Hauptanwendung starten:**
```bash
cd omf2/
python omf.py
```

### **2. Gateway-Factory verwenden:**
```python
from omf2.factory.gateway_factory import get_ccu_gateway, get_nodered_gateway, get_admin_gateway

# Gateways erstellen (Singleton-Pattern)
ccu_gateway = get_ccu_gateway()
nodered_gateway = get_nodered_gateway()
admin_gateway = get_admin_gateway()

# Business-Operationen ausführen
ccu_gateway.reset_factory()
ccu_gateway.send_global_command("start", {"line": "1"})
```

### **3. UI-Komponenten entwickeln (Beispiel: CCU Modules):**
```python
# Immer UISymbols verwenden
from omf2.ui.common.symbols import UISymbols
from omf2.factory.gateway_factory import get_ccu_gateway
from omf2.ccu.module_manager import get_ccu_module_manager
from omf2.ui.utils.ui_refresh import request_refresh

def render_ccu_modules_tab():
    # Gateway-Pattern
    ccu_gateway = get_ccu_gateway()
    if not ccu_gateway:
        st.error(f"{UISymbols.get_status_icon('error')} CCU Gateway not available")
        return
    
    # Business Logic
    module_manager = get_ccu_module_manager()
    
    # UI mit UISymbols
    st.header(f"{UISymbols.get_tab_icon('ccu_modules')} CCU Modules")
    
    # Module-Status-Tabelle
    modules = module_manager.get_all_modules()
    for module_id, module_data in modules.items():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"{module_manager.get_module_icon(module_id)} {module_id}")
        with col2:
            st.write(module_manager.get_connection_display(module_data))
        with col3:
            st.write(module_manager.get_availability_display(module_data))
        with col4:
            st.write(module_manager.get_configuration_display(module_data))
    
    # UI-Refresh
    if st.button(f"{UISymbols.get_status_icon('refresh')} Refresh"):
        request_refresh()  # Statt st.rerun()
```

## 📚 **Kritische Dokumentation für Agents**

### **🚨 MUST-READ für alle Cursor Agents:**
- 📄 **[UI_DEVELOPMENT_GUIDE.md](docs/UI_DEVELOPMENT_GUIDE.md)** - **KRITISCH:** Gateway-Pattern & Environment Switch
- 📄 **[CONNECTION_LOOP_FIXES_DECISION_RECORD.md](docs/CONNECTION_LOOP_FIXES_DECISION_RECORD.md)** - **KRITISCH:** Connection Loop Prevention
- 📄 **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Vollständige Architektur-Übersicht

### **Architektur & Implementierung:**
- 📄 **[IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md)** - Implementierungsstatus
- 📄 **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Projektstruktur & Prinzipien
- 📄 **[ADMIN_CCU_CLIENT_BEHAVIOR_ANALYSIS.md](docs/ADMIN_CCU_CLIENT_BEHAVIOR_ANALYSIS.md)** - MQTT Client Analysis

### **Entwicklung & Migration:**
- 📄 **[REFACTORING_BACKLOG.md](docs/REFACTORING_BACKLOG.md)** - Migration von omf/dashboard
- 📄 **[UI_SYMBOL_STYLE_GUIDE.md](docs/UI_SYMBOL_STYLE_GUIDE.md)** - Symbol-Style-Guide
- 📄 **[CCU_DOMAIN_SYMBOL_GUIDELINES.md](docs/CCU_DOMAIN_SYMBOL_GUIDELINES.md)** - CCU-Domain Guidelines

### **Shopfloor Layout System:**
- 📄 **[SHOPFLOOR_LAYOUT_GUIDE.md](docs/SHOPFLOOR_LAYOUT_GUIDE.md)** - **NEU:** Kompletter Guide für wiederverwendbare 3×4 Grid-Komponente

## 🎯 **Entwicklungsstandards**

### **✅ OBLIGATORISCH:**
- **Gateway-Pattern verwenden** (nie direkte MQTT-Clients)
- **Environment Switch verwenden** (`switch_ccu_environment()` aus `environment_switch.py`)
- **UISymbols verwenden** (nie hardcodierte Symbole)
- **request_refresh() verwenden** (nie st.rerun())
- **Business Logic Manager verwenden** (ModuleManager, WorkpieceManager)
- **Schema-basierte Message-Verarbeitung** (get_topic_schema())
- **Error-Handling implementieren** (Try-Catch für Gateway-Calls)
- **Logger verwenden** (get_logger(__name__))
- **Shopfloor Layout verwenden** (`show_shopfloor_grid_only()` aus `shopfloor_layout.py`)

### **🚫 VERMEIDEN:**
- ❌ Direkte MQTT-Client Verwendung
- ❌ `client.reconnect_environment()` direkt verwenden (verursacht Connection Loops!)
- ❌ Hardcodierte Symbole
- ❌ st.rerun() verwenden
- ❌ Direkte Registry-Zugriffe
- ❌ Redundante Mappings (Schema-Info direkt aus Topics)

## 📊 **Test-Statistik**

```
============================== 55 passed in 0.88s ==============================
```

- **55 Tests erfolgreich** ✅
- **0 Fehler** ✅
- **Thread-Safety** getestet ✅
- **Registry v2 Integration** getestet ✅
- **Performance** optimiert ✅

## 🔄 **Migration von omf/dashboard**

### **Phase 1: Grundarchitektur (ABGESCHLOSSEN)**
- ✅ Registry v2 Integration
- ✅ Gateway-Pattern
- ✅ UI-Refresh-System
- ✅ Symbol-System

### **Phase 2: i18n & Erweiterungen (GEPLANT)**
- 🔄 Internationalisierung (DE/EN/FR)
- 🔄 Rollenbasierte Tab-Generierung
- 🔄 Assets-Management
- 🔄 Logging-System

## 🎉 **Mission Accomplished!**

**Die gekapselte MQTT-Architektur für Streamlit-Apps ist vollständig implementiert und getestet!**

**Ready for Production!** 🚀

---

**Letzte Aktualisierung:** 2025-01-07  
**Status:** VOLLSTÄNDIG IMPLEMENTIERT ✅  
**Registry-Migration:** ABGESCHLOSSEN ✅  
**Architektur-Cleanup:** ABGESCHLOSSEN ✅  
**Connection Loop Fixes:** IMPLEMENTIERT ✅