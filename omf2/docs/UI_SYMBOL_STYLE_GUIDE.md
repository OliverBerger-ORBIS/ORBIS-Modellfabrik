# 🎨 OMF2 UI Symbol Style Guide

## 📋 Übersicht

Dieser Style Guide definiert die einheitliche Verwendung von Symbolen und Icons in der OMF2 Streamlit-Anwendung. Er basiert auf der Analyse der bestehenden `omf/dashboard` und `omf2/ui` Implementierungen.

## 🎯 Ziele

- **Konsistenz**: Einheitliche Symbolverwendung across alle UI-Komponenten
- **Intuitivität**: Symbole sollen sofort verständlich sein
- **Wartbarkeit**: Zentrale Definition für einfache Updates
- **Skalierbarkeit**: Erweiterbares System für neue Symbole

## 📚 Symbol-Kategorien

### 1. **Tab-Navigation Icons** (Hauptnavigation)

```python
TAB_ICONS = {
    # CCU Module
    'ccu_dashboard': '🏭',      # Factory/Overview
    'ccu_orders': '📦',         # Orders/Workpieces
    'ccu_process': '⚙️',        # Process Control
    'ccu_configuration': '⚙️',  # Configuration
    'ccu_modules': '🔧',        # Module Control
    
    # Node-RED Integration
    'nodered_overview': '🔄',   # Process Overview
    'nodered_processes': '⚙️',  # Process Management
    
    # Admin Functions
    'message_center': '📨',     # Message Center
    'generic_steering': '🎮',   # Generic Steering
    'admin_settings': '⚙️',    # Admin Settings
}
```

### 2. **Status-Feedback Icons** (User Feedback)

```python
STATUS_ICONS = {
    'success': '✅',            # Erfolgreiche Aktionen
    'error': '❌',              # Fehler und Fehlschläge
    'warning': '⚠️',            # Warnungen
    'info': 'ℹ️',               # Informationen
    'tip': '💡',                # Tipps und Hinweise
    'loading': '🔄',             # Ladevorgänge
    'refresh': '🔄',            # Aktualisieren
    'send': '📤',               # Nachrichten senden
    'receive': '📥',            # Nachrichten empfangen
}
```

### 3. **Functional Icons** (Spezifische Funktionen)

```python
FUNCTIONAL_ICONS = {
    # Factory Operations
    'factory_reset': '🏭',      # Factory Reset
    'emergency_stop': '🚨',     # Emergency Stop
    'module_control': '🔧',     # Module Control
    
    # Communication
    'topic_driven': '📡',       # Topic-driven Commands
    'schema_driven': '📋',      # Schema-driven Commands
    'mqtt_connect': '📡',       # MQTT Connection
    
    # Process States
    'running': '🟢',            # Running/Active
    'stopped': '🔴',            # Stopped/Error
    'unknown': '⚪',             # Unknown/Neutral
    'pending': '🟡',             # Pending/Waiting
    
    # Navigation
    'debug': '🔍',              # Debug/Inspection
    'history': '📚',            # History/Logs
    'settings': '⚙️',           # Settings/Configuration
    'control': '🎮',            # Control/Steering
}
```

## 🏗️ Implementierung

### 1. **Zentrale Symbol-Definition**

```python
# omf2/ui/common/symbols.py
"""
OMF2 UI Symbol Definitions
Centralized symbol management for consistent UI
"""

class UISymbols:
    """Centralized symbol definitions for OMF2 UI"""
    
    # Tab Navigation
    TAB_ICONS = {
        'ccu_dashboard': '🏭',
        'ccu_orders': '📦',
        'ccu_process': '⚙️',
        'ccu_configuration': '⚙️',
        'ccu_modules': '🔧',
        'nodered_overview': '🔄',
        'nodered_processes': '⚙️',
        'message_center': '📨',
        'generic_steering': '🎮',
        'admin_settings': '⚙️',
    }
    
    # Status Feedback
    STATUS_ICONS = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'tip': '💡',
        'loading': '🔄',
        'refresh': '🔄',
        'send': '📤',
        'receive': '📥',
    }
    
    # Functional Icons
    FUNCTIONAL_ICONS = {
        'factory_reset': '🏭',
        'emergency_stop': '🚨',
        'module_control': '🔧',
        'topic_driven': '📡',
        'schema_driven': '📋',
        'mqtt_connect': '📡',
        'running': '🟢',
        'stopped': '🔴',
        'unknown': '⚪',
        'pending': '🟡',
        'debug': '🔍',
        'history': '📚',
        'settings': '⚙️',
        'control': '🎮',
    }
    
    @classmethod
    def get_tab_icon(cls, tab_key: str) -> str:
        """Get icon for tab navigation"""
        return cls.TAB_ICONS.get(tab_key, '📋')
    
    @classmethod
    def get_status_icon(cls, status: str) -> str:
        """Get icon for status feedback"""
        return cls.STATUS_ICONS.get(status, 'ℹ️')
    
    @classmethod
    def get_functional_icon(cls, function: str) -> str:
        """Get icon for functional elements"""
        return cls.FUNCTIONAL_ICONS.get(function, '⚙️')
```

### 2. **Verwendung in UI-Komponenten**

```python
# Beispiel: Tab-Erstellung
from omf2.ui.common.symbols import UISymbols

def render_tabs():
    """Render tabs with consistent icons"""
    tab_labels = []
    for tab_key in allowed_tabs:
        icon = UISymbols.get_tab_icon(tab_key)
        name = get_tab_name(tab_key)
        tab_labels.append(f"{icon} {name}")
    
    tabs = st.tabs(tab_labels)
    return tabs

# Beispiel: Status-Feedback
def show_status_message(message: str, status: str = 'info'):
    """Show status message with consistent icon"""
    icon = UISymbols.get_status_icon(status)
    if status == 'success':
        st.success(f"{icon} {message}")
    elif status == 'error':
        st.error(f"{icon} {message}")
    elif status == 'warning':
        st.warning(f"{icon} {message}")
    else:
        st.info(f"{icon} {message}")

# Beispiel: Functional Elements
def render_control_button(action: str, label: str):
    """Render control button with consistent icon"""
    icon = UISymbols.get_functional_icon(action)
    return st.button(f"{icon} {label}", key=f"btn_{action}")
```

## 📏 Style-Regeln

### 1. **Icon-Verwendung**
- **Immer mit Text**: Icons sollen immer mit beschreibendem Text verwendet werden
- **Konsistenz**: Gleiche Funktion = gleiches Icon
- **Größe**: Standard-Emoji-Größe (nicht custom icons)
- **Zugänglichkeit**: Symbole sollen auch ohne Text verständlich sein

### 2. **Tab-Navigation**
- **Hauptkategorien**: Verwende eindeutige Icons für Hauptkategorien
- **Unterkategorien**: Verwende ähnliche aber unterscheidbare Icons
- **Gruppierung**: Ähnliche Funktionen = ähnliche Icons

### 3. **Status-Feedback**
- **Farbe-Konsistenz**: 
  - ✅ Grün für Erfolg
  - ❌ Rot für Fehler
  - ⚠️ Gelb für Warnungen
  - ℹ️ Blau für Informationen
- **Kontext**: Status-Icons sollen den Kontext klar machen

### 4. **Functional Icons**
- **Aktion-basiert**: Icons sollen die Aktion widerspiegeln
- **Zustand-basiert**: Icons sollen den aktuellen Zustand zeigen
- **Hierarchie**: Wichtige Funktionen = auffälligere Icons

## 🔄 Migration von omf/dashboard

### **Bestehende Symbole beibehalten**
```python
# Alte omf/dashboard Symbole → Neue omf2/ui Symbole
LEGACY_MAPPING = {
    'aps_overview': 'ccu_dashboard',      # 🏭 → 🏭
    'aps_orders': 'ccu_orders',          # 📋 → 📦
    'aps_processes': 'ccu_process',       # 🔄 → ⚙️
    'aps_configuration': 'ccu_configuration', # ⚙️ → ⚙️
    'aps_modules': 'ccu_modules',         # 🏭 → 🔧
    'wl_module_control': 'ccu_modules',   # 🔧 → 🔧
    'wl_system_control': 'ccu_configuration', # ⚙️ → ⚙️
    'steering': 'generic_steering',       # 🎮 → 🎮
    'message_center': 'message_center',   # 📡 → 📨
    'logs': 'admin_settings',             # 📋 → ⚙️
    'settings': 'admin_settings',         # ⚙️ → ⚙️
}
```

## 📈 Erweiterbarkeit

### **Neue Symbole hinzufügen**
1. **Kategorie bestimmen**: Tab, Status, oder Functional
2. **Symbol definieren**: Emoji auswählen
3. **Dokumentation**: Verwendung dokumentieren
4. **Test**: In verschiedenen Kontexten testen

### **Beispiel: Neues Symbol hinzufügen**
```python
# 1. Symbol zur entsprechenden Kategorie hinzufügen
FUNCTIONAL_ICONS = {
    # ... existing icons ...
    'new_function': '🆕',  # Neues Symbol
}

# 2. Verwendung in UI-Komponente
def render_new_feature():
    icon = UISymbols.get_functional_icon('new_function')
    st.button(f"{icon} New Feature")
```

## ✅ Checkliste für Entwickler

### **Vor jeder UI-Implementierung prüfen:**
- [ ] Ist das Symbol bereits in `UISymbols` definiert?
- [ ] Verwendet die Komponente die zentrale Symbol-Definition?
- [ ] Ist das Symbol konsistent mit ähnlichen Funktionen?
- [ ] Ist das Symbol auch ohne Text verständlich?
- [ ] Ist die Verwendung dokumentiert?

### **Bei neuen Features:**
- [ ] Neue Symbole in `UISymbols` definiert?
- [ ] Verwendung in verschiedenen Kontexten getestet?
- [ ] Dokumentation aktualisiert?
- [ ] Bestehende Symbole überprüft auf Konflikte?

## 🎯 Nächste Schritte

1. **Implementierung**: `UISymbols` Klasse erstellen
2. **Migration**: Bestehende Komponenten auf zentrale Symbole umstellen
3. **Testing**: Symbole in verschiedenen Kontexten testen
4. **Dokumentation**: Entwickler-Dokumentation erweitern
5. **Review**: Regelmäßige Überprüfung der Symbol-Konsistenz

---

**Version**: 1.0  
**Datum**: 2024-12-19  
**Autor**: OMF Development Team
