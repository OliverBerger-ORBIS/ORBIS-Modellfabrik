# 🎨 OMF2 Symbol Implementation Guide

## 📋 Übersicht

Dieser Guide beschreibt die Implementierung der finalen Symbol-Entscheidungen in omf2/ basierend auf der `SYMBOL_DECISION_MATRIX.md`.

## 🎯 Finale Symbol-Entscheidungen

### **Haupttabs (Tab Navigation)**
```python
# FINALE ENTSCHEIDUNGEN
'ccu_dashboard': '🏭',      # Factory/Overview
'ccu_orders': '📝',         # Orders/Workpieces (FINAL: 📝)
'ccu_process': '🔄',        # Process Control (FINAL: 🔄)
'ccu_configuration': '⚙️',  # Configuration
'ccu_modules': '🏗️',       # Module Control (FINAL: 🏗️)
'message_center': '📨',    # Message Center (FINAL: 📨)
'logs': '📋',              # Logs (FINAL: 📋)
'settings': '⚙️',          # Settings
```

### **Admin-Settings Subtabs**
```python
# FINALE ENTSCHEIDUNGEN
'dashboard_settings': '📊',  # Dashboard Settings
'mqtt_clients': '🔌',        # MQTT Clients (FINAL: 🔌)
'topics': '📡',              # Topics (FINAL: 📡)
'schemas': '🧩',             # Schemas (FINAL: 🧩)
'modules': '🏗️',             # Modules (FINAL: 🏗️)
'stations': '🏢',            # Stations (FINAL: 🏢)
'txt_controllers': '🕹️',     # TXT Controllers (FINAL: 🕹️)
'workpieces': None,           # Workpieces (loaded from Registry)
```

### **Status-Feedback**
```python
# FINALE ENTSCHEIDUNGEN
'loading': '⏳',             # Ladevorgänge (FINAL: ⏳)
'receive': '📥',            # Nachrichten empfangen (FINAL: 📥)
```

### **Prozess-Status**
```python
# FINALE ENTSCHEIDUNGEN
'running': '▶️',             # Running/Active (FINAL: ▶️)
'stopped': '⏹️',             # Stopped/Error (FINAL: ⏹️)
'pending': '⏳',              # Pending/Waiting (FINAL: ⏳)
```

### **Funktionale Symbole**
```python
# FINALE ENTSCHEIDUNGEN
'module_control': '🛠️',      # Module Control (FINAL: 🛠️)
'schema_driven': '🧩',       # Schema-driven Commands (FINAL: 🧩)
'mqtt_connect': '🔌',        # MQTT Connection (FINAL: 🔌)
```

### **Modul-Entities**
```python
# FINALE ENTSCHEIDUNGEN
'dps_entladestation': '📦',  # DPS/Entladestation (FINAL: 📦)
```

## 🚀 Implementierungsschritte

### **Schritt 1: UISymbols Klasse aktualisieren**
✅ **BEREITS ERLEDIGT** - `omf2/ui/common/symbols.py` wurde mit finalen Entscheidungen aktualisiert.

### **Schritt 2: Bestehende Komponenten migrieren**

#### **2.1 Haupttabs migrieren**
```python
# In omf2/ui/main_dashboard.py
from omf2.ui.common.symbols import UISymbols

# Alte Implementierung ersetzen:
# st.tabs(["🏭 Factory", "📦 Orders", "🔄 Processes"])

# Neue Implementierung:
tab_labels = []
for tab_key in allowed_tabs:
    icon = UISymbols.get_tab_icon(tab_key)
    name = get_tab_name(tab_key)
    tab_labels.append(f"{icon} {name}")
tabs = st.tabs(tab_labels)
```

#### **2.2 Admin-Settings Subtabs migrieren**
```python
# In omf2/ui/admin/admin_settings/admin_settings_tab.py
from omf2.ui.common.symbols import UISymbols

# Alte Implementierung ersetzen:
# subtab_labels = ["📊 Dashboard", "📡 MQTT Clients", ...]

# Neue Implementierung:
subtab_labels = [
    f"{UISymbols.get_functional_icon('dashboard')} Dashboard",
    f"{UISymbols.get_functional_icon('mqtt_connect')} MQTT Clients",
    f"{UISymbols.get_functional_icon('topic_driven')} Topics",
    f"{UISymbols.get_functional_icon('schema_driven')} Schemas",
    f"{UISymbols.get_tab_icon('ccu_modules')} Modules",
    f"{UISymbols.get_functional_icon('stations')} Stations",
    f"{UISymbols.get_functional_icon('txt_controllers')} TXT Controllers",
    f"{UISymbols.get_workpiece_icon('all_workpieces')} Workpieces",  # 🔵⚪🔴
]
```

#### **2.3 Status-Feedback migrieren**
```python
# In allen Komponenten
from omf2.ui.common.symbols import UISymbols

# Alte Implementierung ersetzen:
# st.info("🔄 Loading...")
# st.success("📤 Message sent!")

# Neue Implementierung:
st.info(f"{UISymbols.get_status_icon('loading')} Loading...")
st.success(f"{UISymbols.get_status_icon('send')} Message sent!")
```

### **Schritt 3: Legacy-Support implementieren**

#### **3.1 omf/dashboard Kompatibilität**
```python
# In omf2/ui/common/symbols.py
LEGACY_MAPPING = {
    'aps_overview': 'ccu_dashboard',
    'aps_orders': 'ccu_orders',
    'aps_processes': 'ccu_process',
    'aps_configuration': 'ccu_configuration',
    'aps_modules': 'ccu_modules',
    'wl_module_control': 'ccu_modules',
    'wl_system_control': 'ccu_configuration',
    'steering': 'generic_steering',
    'message_center': 'message_center',
    'logs': 'logs',
    'settings': 'settings',
}

@classmethod
def get_legacy_tab_icon(cls, legacy_key: str) -> str:
    """Get icon for legacy tab keys"""
    if legacy_key in cls.TAB_ICONS:
        return cls.TAB_ICONS[legacy_key]
    
    # Try mapping to new key
    new_key = cls.LEGACY_MAPPING.get(legacy_key)
    if new_key:
        return cls.TAB_ICONS.get(new_key, '📋')
    
    return '📋'  # Fallback
```

### **Schritt 4: Testing und Validierung**

#### **4.1 Symbol-Konsistenz testen**
```python
# Test-Script: omf2/scripts/test_symbol_consistency.py
def test_symbol_consistency():
    """Test that all symbols are consistent and unique where needed"""
    from omf2.ui.common.symbols import UISymbols
    
    # Test tab icons
    tab_icons = UISymbols.get_all_tab_icons()
    print("Tab Icons:", tab_icons)
    
    # Test status icons
    status_icons = UISymbols.get_all_status_icons()
    print("Status Icons:", status_icons)
    
    # Test functional icons
    functional_icons = UISymbols.get_all_functional_icons()
    print("Functional Icons:", functional_icons)
```

#### **4.2 UI-Komponenten testen**
```python
# Test-Script: omf2/scripts/test_ui_components.py
def test_ui_components():
    """Test that all UI components use the new symbol system"""
    # Test main dashboard
    # Test admin settings
    # Test status feedback
    # Test process status
    pass
```

## 📋 Checkliste für Entwickler

### **Vor der Implementierung:**
- [ ] `UISymbols` Klasse importiert
- [ ] Alte hardcodierte Symbole identifiziert
- [ ] Legacy-Mapping verstanden
- [ ] Test-Plan erstellt

### **Während der Implementierung:**
- [ ] Zentrale `UISymbols` Klasse verwenden
- [ ] Keine hardcodierten Symbole
- [ ] Legacy-Support implementieren
- [ ] Konsistenz prüfen

### **Nach der Implementierung:**
- [ ] Alle Komponenten getestet
- [ ] Symbol-Konsistenz validiert
- [ ] Legacy-Kompatibilität geprüft
- [ ] Dokumentation aktualisiert

## 🔄 Migration Timeline

### **Phase 1: Core Implementation (ABGESCHLOSSEN)**
- ✅ UISymbols Klasse aktualisiert
- ✅ Haupttabs migriert
- ✅ Admin-Settings Subtabs migriert
- ✅ Message Center migriert
- ✅ Generic Steering migriert

### **Phase 2: CCU-Domain (NACH Stabilisierung)**
- ⏳ **WARTEN** bis CCU-Domain stabil ist
- ⏳ **NICHT migrieren** während aktiver Entwicklung
- 🔄 CCU-spezifische Symbole definieren
- 🔄 Alle CCU-Komponenten mit UISymbols entwickeln

### **Phase 3: Testing & Validation (Laufend)**
- ✅ Symbol-Konsistenz testen
- ✅ UI-Komponenten testen
- ✅ Legacy-Support testen

### **Phase 4: Documentation & Cleanup (Laufend)**
- ✅ Style-Guide aktualisiert
- ✅ CCU-Domain Guidelines erstellt
- ✅ Dokumentation vervollständigt

## 🎯 Erfolgskriterien

### **Technische Kriterien:**
- ✅ Alle Symbole verwenden `UISymbols` Klasse
- ✅ Keine hardcodierten Symbole in Komponenten
- ✅ Legacy-Support funktioniert
- ✅ Symbol-Konsistenz gewährleistet

### **Benutzer-Kriterien:**
- ✅ Intuitive Symbol-Verwendung
- ✅ Konsistente UI-Erfahrung
- ✅ Keine Verwirrung durch Symbol-Konflikte
- ✅ Verbesserte Benutzerfreundlichkeit

---

**Version**: 1.0  
**Datum**: 2024-12-19  
**Status**: Implementierungsbereit
