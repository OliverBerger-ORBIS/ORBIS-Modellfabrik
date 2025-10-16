# 🏭 CCU Domain Symbol Guidelines

## 📋 Übersicht

Dieses Dokument definiert die Symbol-Guidelines für die CCU-Domain nach den massiven Änderungen. Die CCU-Domain wird erst nach Stabilisierung auf UISymbols umgestellt.

## 🎯 **WICHTIG: CCU-Domain Migration-Strategie**

### **⏳ Phase 1: Warten auf Stabilisierung**
- ⏳ **NICHT migrieren** während aktiver Entwicklung
- ⏳ Warten bis CCU-Domain stabil ist
- ⏳ Dann systematisch auf UISymbols umstellen

### **✅ Phase 2: Nach Stabilisierung**
- ✅ **Agenten anweisen** UISymbols zu verwenden
- ✅ Alle neuen CCU-Komponenten mit UISymbols entwickeln
- ✅ Bestehende Komponenten schrittweise migrieren

## 🏗️ **CCU-Domain Symbol-Mapping**

### **Haupttabs (bereits definiert)**
```python
# In UISymbols.TAB_ICONS bereits definiert:
'ccu_dashboard': '🏭',      # Factory/Overview
'ccu_orders': '📝',         # Orders/Workpieces (FINAL: 📝)
'ccu_process': '🔄',        # Process Control (FINAL: 🔄)
'ccu_configuration': '⚙️',  # Configuration
'ccu_modules': '🏗️',        # Module Control (FINAL: 🏗️)
```

### **CCU-spezifische Symbole (zu definieren)**
```python
# Diese werden nach CCU-Stabilisierung hinzugefügt:
CCU_SPECIFIC_ICONS = {
    # CCU Orders
    'order_management': '📋',      # Order Management
    'workpiece_tracking': '🔵⚪🔴', # Workpiece Tracking
    'order_status': '📊',          # Order Status
    
    # CCU Process
    'process_control': '🎛️',      # Process Control
    'sequence_control': '🔄',      # Sequence Control
    'process_monitoring': '📈',    # Process Monitoring
    
    # CCU Configuration
    'parameter_config': '⚙️',     # Parameter Configuration
    'factory_config': '🏭',        # Factory Configuration
    'module_config': '🔧',         # Module Configuration
    
    # CCU Modules
    'module_status': '📊',         # Module Status
    'module_control': '🎮',        # Module Control
    'module_monitoring': '📡',     # Module Monitoring
}
```

## 🤖 **Agent-Anweisungen für CCU-Domain**

### **Für neue CCU-Komponenten:**
```python
# IMMER verwenden:
from omf2.ui.common.symbols import UISymbols

# Tab-Icons:
icon = UISymbols.get_tab_icon('ccu_orders')  # Gibt '📝' zurück

# Status-Icons:
status_icon = UISymbols.get_status_icon('loading')  # Gibt '⏳' zurück

# Functional-Icons:
func_icon = UISymbols.get_functional_icon('stations')  # Gibt '🏢' zurück
```

### **Für CCU-spezifische Symbole:**
```python
# Nach CCU-Stabilisierung hinzufügen:
# 1. Neue Icons in UISymbols.FUNCTIONAL_ICONS definieren
# 2. CCU-spezifische Kategorie erstellen
# 3. Alle CCU-Komponenten migrieren
```

## 📋 **CCU Migration Checkliste**

### **Vor der Migration:**
- [ ] CCU-Domain ist stabil
- [ ] Alle massiven Änderungen abgeschlossen
- [ ] Test-Suite für CCU-Komponenten vorhanden
- [ ] Backup der aktuellen CCU-Implementierung

### **Während der Migration:**
- [ ] UISymbols für neue CCU-Komponenten verwenden
- [ ] Bestehende Komponenten schrittweise migrieren
- [ ] CCU-spezifische Symbole definieren
- [ ] Konsistenz mit bestehenden Symbolen prüfen

### **Nach der Migration:**
- [ ] Alle CCU-Komponenten verwenden UISymbols
- [ ] CCU-spezifische Symbole dokumentiert
- [ ] Test-Suite für Symbol-Konsistenz erweitert
- [ ] Performance validiert

## 🎯 **CCU-spezifische Symbol-Kategorien**

### **1. Order Management**
```python
# Symbole für Auftragsverwaltung
'order_creation': '➕',      # Order Creation
'order_editing': '✏️',      # Order Editing
'order_deletion': '🗑️',     # Order Deletion
'order_status': '📊',        # Order Status
'order_history': '📚',       # Order History
```

### **2. Process Control**
```python
# Symbole für Prozesssteuerung
'process_start': '▶️',       # Process Start
'process_stop': '⏹️',       # Process Stop
'process_pause': '⏸️',      # Process Pause
'process_resume': '▶️',      # Process Resume
'process_reset': '🔄',      # Process Reset
```

### **3. Module Management**
```python
# Symbole für Modulverwaltung
'module_online': '🟢',      # Module Online
'module_offline': '🔴',      # Module Offline
'module_error': '⚠️',        # Module Error
'module_maintenance': '🔧',  # Module Maintenance
'module_configuration': '⚙️', # Module Configuration
```

## 🔄 **Migration Timeline für CCU-Domain**

### **Phase 1: Warten (Aktuell)**
- ⏳ CCU-Domain wird massiv geändert
- ⏳ Keine Migration während Entwicklung
- ⏳ UISymbols-System bereit halten

### **Phase 2: Stabilisierung**
- 🔄 CCU-Domain wird stabil
- 🔄 Test-Suite wird erweitert
- 🔄 CCU-spezifische Symbole definieren

### **Phase 3: Migration**
- 🚀 Alle neuen CCU-Komponenten mit UISymbols
- 🚀 Bestehende Komponenten migrieren
- 🚀 CCU-spezifische Symbole implementieren

### **Phase 4: Validation**
- ✅ CCU-Symbol-Konsistenz testen
- ✅ Performance validieren
- ✅ Dokumentation aktualisieren

## 📊 **CCU Symbol-Statistiken**

### **Bereits definiert:**
- ✅ **5 Haupttabs** (ccu_dashboard, ccu_orders, ccu_process, ccu_configuration, ccu_modules)
- ✅ **Status-Icons** (success, error, warning, info, loading, etc.)
- ✅ **Functional-Icons** (stations, txt_controllers, workpieces, etc.)

### **Zu definieren (nach Stabilisierung):**
- 🔄 **CCU-spezifische Symbole** (order_management, process_control, etc.)
- 🔄 **Module-spezifische Symbole** (module_status, module_control, etc.)
- 🔄 **Process-spezifische Symbole** (sequence_control, process_monitoring, etc.)

## 🎯 **Erfolgskriterien für CCU-Domain**

### **Technische Kriterien:**
- ✅ Alle CCU-Komponenten verwenden UISymbols
- ✅ CCU-spezifische Symbole definiert
- ✅ Konsistenz mit bestehenden Symbolen
- ✅ Performance optimiert

### **Benutzer-Kriterien:**
- ✅ Intuitive CCU-Symbol-Verwendung
- ✅ Konsistente UI-Erfahrung
- ✅ Keine Verwirrung durch Symbol-Konflikte
- ✅ Verbesserte CCU-Benutzerfreundlichkeit

---

**Version**: 1.0  
**Datum**: 2024-12-19  
**Status**: Guidelines bereit, Migration nach CCU-Stabilisierung  
**Nächster Schritt**: Warten auf CCU-Domain Stabilisierung
