# 🎯 Copilot PR-Request: Shopfloor Layout Active Module Highlighting Fix

## 📋 Problem-Statement

**Commit-Reference:** `6c2f13a` - "feat: Complete OMF2 integration of shopfloor_layout"  
**Branch:** `origin/omf2-refactoring`  

**Kernproblem:** Active Module Highlighting funktioniert nicht in der UI - Module werden nicht visuell hervorgehoben, obwohl die Funktion `show_shopfloor_layout()` den Parameter `active_module_id` unterstützt.

---

## 🔍 Was das Problem ist

### ❌ **Das Problem:**
- **Active Module Highlighting** funktioniert nicht in der UI
- Module werden nicht orange hervorgehoben, obwohl `active_module_id` übergeben wird
- Die Funktion `show_shopfloor_layout()` ist implementiert, aber das Highlighting funktioniert nicht

### ✅ **Was bereits funktioniert:**
- **Haupt-Implementation** - `shopfloor_layout.py` ist implementiert
- **API-Parameter** - `active_module_id` Parameter wird akzeptiert
- **Test-App** - `shopfloor_layout_test.py` funktioniert isoliert
- **Event-Handling** - Click/Double-Click Funktionalität implementiert

---

## 🎯 Was Copilot fixen soll

### **Hauptziel:** Active Module Highlighting in der UI reparieren

### **Konkrete Aufgaben:**

#### 1. **Highlighting-Bug fixen:**
- Problem in `show_shopfloor_layout()` identifizieren
- Orange Hervorhebung für `active_module_id` reparieren
- CSS/SVG-Styling für aktive Module korrigieren

#### 2. **Integration in Manager testen:**
- `omf2/ccu/order_manager.py` - Production Orders mit aktivem Modul testen
- `omf2/ccu/stock_manager.py` - Storage Orders mit aktivem Modul testen
- Sicherstellen dass `active_module_id` korrekt übergeben wird

#### 3. **UI-Komponenten Integration:**
- `omf2/ui/ccu/ccu_configuration/` Subtabs testen
- `omf2/ui/ccu/ccu_orders/` Subtabs testen
- Sicherstellen dass Highlighting in allen Kontexten funktioniert

---

## 📁 Relevante Dateien

### **Core Implementation:**
- ✅ `omf2/ui/ccu/common/shopfloor_layout.py` - Haupt-Implementation (Bug hier)
- ✅ `omf2/tests/test_helper_apps/shopfloor_layout_test.py` - Test-App (funktioniert)

### **Zu testende OMF2 Komponenten:**
- 🔄 `omf2/ccu/order_manager.py` - Production Order Manager
- 🔄 `omf2/ccu/stock_manager.py` - Storage Order Manager
- 🔄 `omf2/ui/ccu/ccu_configuration/` - CCU Configuration Subtabs
- 🔄 `omf2/ui/ccu/ccu_orders/` - CCU Orders Subtabs

---

## 🧪 Erfolgs-Kriterien

- [ ] **Active Module Highlighting** funktioniert in der UI
- [ ] **Production Orders** zeigen aktive Module mit orange Umrandung
- [ ] **Storage Orders** zeigen aktive Module mit orange Umrandung
- [ ] **CCU Configuration** ermöglicht Single/Double Click Navigation
- [ ] **Alle Tests bestehen**

---

## 📋 Technische Details

### **Verwendete Funktion:**
```python
from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout

show_shopfloor_layout(
    mode="view_mode",  # oder "ccu_configuration", "interactive"
    active_module_id=None,  # ID des aktiven Moduls (PROBLEM: wird nicht hervorgehoben)
    active_intersections=None,  # Liste aktiver Intersections
    title="Shopfloor Layout",
    show_controls=True,
    unique_key=None
)
```

### **Mode-Parameter:**
- **`"view_mode"`** - Nur aktive Module anzeigen, keine Klicks
- **`"ccu_configuration"`** - Single/Double Click für Auswahl/Navigation
- **`"interactive"`** - Standard-Interaktivität

---

## 🚀 Nächste Schritte für Copilot

1. **Identifiziere** das Highlighting-Problem in `show_shopfloor_layout()`
2. **Repariere** die orange Hervorhebung für `active_module_id`
3. **Teste** die Integration in Production/Storage Order Manager
4. **Validiere** dass alle Tests bestehen

---

## 💡 Wichtige Hinweise

- **Das Problem ist ein Bug** - nicht eine fehlende Integration! 🐛
- **API-Kompatibilität** muss gewährleistet bleiben
- **Alle Tests müssen bestehen**
- **Keine Breaking Changes**

---

## 📞 Support

Bei Fragen zur bereits implementierten Funktionalität:
- **Test-App:** `omf2/tests/test_helper_apps/shopfloor_layout_test.py` (funktioniert)
- **Core-Implementation:** `omf2/ui/ccu/common/shopfloor_layout.py` (Bug hier)
- **Funktion:** `show_shopfloor_layout()` (in shopfloor_layout.py)
- **Commit:** `6c2f13a` - "feat: Complete OMF2 integration of shopfloor_layout"