# 🏭 Shopfloor Layout System - Complete Guide

**Status:** PRODUCTION READY ✅  
**Version:** 1.0  
**Datum:** 2025-01-07  

## 📋 Overview

Das Shopfloor Layout System ist ein wiederverwendbares UI-Komponentensystem für die Darstellung von Fabriklayouts in OMF2. Es bietet eine feste 3:4 Container-Box mit 12 quadratischen SVG-Icons für Module, Intersections und Empty-Positionen.

## 🎯 Key Features

### ✅ **Implementiert:**
- **Feste 3:4 Container-Box** - Immer korrektes Seitenverhältnis
- **12 quadratische SVG-Icons** - Professionelle Darstellung
- **SVG-Icon Mapping** - Einfacher Austausch von Symbolen
- **Aktive Station Hervorhebung** - Blaue Umrandung für aktive Module
- **Wiederverwendbare Komponenten** - Für verschiedene UI-Tabs
- **Korrekte Positionen** - Module an richtigen Stellen im Grid

### 🎨 **Visual Design:**
- **Container:** 3:4 Seitenverhältnis, grauer Rahmen, abgerundete Ecken
- **Module:** Quadratische Zellen mit SVG-Icons und Text-Labels
- **Intersections:** "Add" Kreuzungspunkte ohne Text
- **Empty-Positionen:** Leere Zellen ohne Icon oder Text
- **Aktive Station:** Blauer Rahmen (4px) mit Schatten-Effekt

## 🏗️ Architecture

### **Komponenten-Hierarchie:**
```
Shopfloor Layout System
├── Asset Manager (omf2/assets/asset_manager.py)
│   ├── SVG-Icon Loading
│   ├── HTML-Template Generation
│   └── Icon Mapping
├── Layout Engine (omf2/ui/ccu/common/shopfloor_layout.py)
│   ├── Grid Generation
│   ├── Position Mapping
│   └── Container Rendering
└── Configuration (omf2/config/ccu/shopfloor_layout.json)
    ├── Grid Dimensions
    ├── Module Positions
    └── Layout Data
```

### **Datenfluss:**
1. **Config Loader** lädt `shopfloor_layout.json`
2. **Asset Manager** lädt SVG-Icons und generiert HTML
3. **Layout Engine** erstellt 3:4 Container mit SVG-Positionen
4. **Streamlit** rendert finales HTML

## 📁 File Structure

### **Core Components:**
```
omf2/
├── assets/
│   ├── asset_manager.py          # SVG-Icon Management
│   └── svgs/                     # SVG-Icon Library
│       ├── warehouse_40dp_*.svg
│       ├── tools_power_drill_40dp_*.svg
│       ├── construction_40dp_*.svg
│       ├── robot_40dp_*.svg
│       ├── conveyor_belt_40dp_*.svg
│       ├── ev_station_40dp_*.svg
│       └── add_2_40dp_*.svg
├── ui/ccu/common/
│   ├── shopfloor_layout.py       # Main Layout Component
│   ├── shopfloor_verification.py # Layout Testing
│   ├── shopfloor_html_test.py    # HTML Rendering Test
│   └── shopfloor_fixed_aspect_test.py # Aspect Ratio Test
└── config/ccu/
    └── shopfloor_layout.json     # Layout Configuration
```

### **Integration Points:**
```
omf2/ui/ccu/ccu_configuration/
└── ccu_factory_configuration_subtab.py  # Factory Configuration Tab

omf2/docs/
├── SHOPFLOOR_LAYOUT_GUIDE.md           # This Guide
├── SHOPFLOOR_LAYOUT_FINAL_CORRECTIONS.md
└── SHOPFLOOR_LAYOUT_IMPROVEMENTS.md
```

## 🎨 SVG-Icon System

### **Icon Mapping:**
```python
# In omf2/assets/asset_manager.py (Zeilen 37-55)
icon_mapping = {
    "HBW": "warehouse_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "DRILL": "tools_power_drill_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "MILL": "construction_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "AIQS": "robot_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "DPS": "conveyor_belt_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "CHRG": "ev_station_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "INTERSECTION": "add_2_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "EMPTY": None,  # Leer - kein Icon
}
```

### **Verfügbare SVG-Icons:**
- `add_2_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg` - Kreuzungspunkt
- `barcode_scanner_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg` - Scanner
- `construction_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg` - Bau/Mill
- `conveyor_belt_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg` - Förderband/DPS
- `ev_station_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg` - Ladestation
- `robot_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg` - Roboter/AIQS
- `tools_power_drill_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg` - Bohrer
- `warehouse_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg` - Lager/HBW

## 🔧 Usage Guide

### **Basic Usage:**
```python
from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_grid_only

# Einfaches Layout anzeigen
show_shopfloor_grid_only(title="Shopfloor Layout")
```

### **Mit aktiver Station:**
```python
from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_grid_only

# Layout mit hervorgehobener aktiver Station
show_shopfloor_grid_only(
    active_module_id="SVR3QA0022",  # HBW als aktiv
    title="Production Layout"
)
```

### **In UI-Tabs integrieren:**
```python
def render_my_custom_tab():
    st.header("My Custom Tab")
    
    # Shopfloor Layout einbinden
    from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_grid_only
    show_shopfloor_grid_only(title="Custom Shopfloor View")
    
    # Weitere Tab-Inhalte...
```

## 🎯 SVG-Icon Customization

### **Icons tauschen:**
1. **Neue SVG-Datei** in `omf2/assets/svgs/` ablegen
2. **Icon Mapping** in `omf2/assets/asset_manager.py` aktualisieren:
   ```python
   icon_mapping = {
       "MILL": "your_new_mill_icon.svg",  # Neues Icon
       # ... andere Mappings
   }
   ```
3. **Layout automatisch aktualisiert** - keine weiteren Änderungen nötig

### **Neue Module hinzufügen:**
1. **SVG-Icon** in `omf2/assets/svgs/` ablegen
2. **Icon Mapping** erweitern:
   ```python
   icon_mapping = {
       "NEW_MODULE": "new_module_icon.svg",
       # ... bestehende Mappings
   }
   ```
3. **Position** in `omf2/config/ccu/shopfloor_layout.json` definieren:
   ```json
   {
     "id": "NEW_MODULE",
     "type": "NEW_MODULE", 
     "serialNumber": "NEW001",
     "position": [1, 2]
   }
   ```

## 📐 Grid Layout (3×4)

### **Koordinaten-System:**
```
[0,0] [1,0] [2,0] [3,0]  ← Zeile 0
[0,1] [1,1] [2,1] [3,1]  ← Zeile 1  
[0,2] [1,2] [2,2] [3,2]  ← Zeile 2
  ↑     ↑     ↑     ↑
Spalte Spalte Spalte Spalte
  0      1      2      3
```

### **Aktuelle Module-Positionen:**
- **MILL** (SVR3QA2098): [1, 0] = Spalte 1, Zeile 0
- **AIQS** (SVR4H76530): [2, 0] = Spalte 2, Zeile 0
- **HBW** (SVR3QA0022): [0, 1] = Spalte 0, Zeile 1
- **DPS** (SVR4H73275): [3, 1] = Spalte 3, Zeile 1
- **DRILL** (SVR4H76449): [0, 2] = Spalte 0, Zeile 2
- **CHRG** (CHRG0): [3, 2] = Spalte 3, Zeile 2

### **Intersections:**
- **Intersection 1**: [1, 1] = Spalte 1, Zeile 1
- **Intersection 2**: [1, 2] = Spalte 1, Zeile 2
- **Intersection 3**: [2, 1] = Spalte 2, Zeile 1
- **Intersection 4**: [2, 2] = Spalte 2, Zeile 2

### **Empty-Positionen:**
- **EMPTY1**: [0, 0] = Spalte 0, Zeile 0
- **EMPTY2**: [3, 0] = Spalte 3, Zeile 0

## 🧪 Testing Components

### **Verification:**
```python
from omf2.ui.ccu.common.shopfloor_verification import show_shopfloor_verification
show_shopfloor_verification()
```

### **HTML Rendering Test:**
```python
from omf2.ui.ccu.common.shopfloor_html_test import show_html_rendering_test
show_html_rendering_test()
```

### **Aspect Ratio Test:**
```python
from omf2.ui.ccu.common.shopfloor_fixed_aspect_test import show_fixed_aspect_ratio_test
show_fixed_aspect_ratio_test()
```

## 🚀 Integration in andere UI-Tabs

### **Schritt 1: Import**
```python
from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_grid_only
```

### **Schritt 2: Integration**
```python
def render_production_tab():
    st.header("Production Overview")
    
    # Shopfloor Layout
    show_shopfloor_grid_only(
        active_module_id=get_current_active_module(),
        title="Production Status"
    )
    
    # Weitere Tab-Inhalte...
```

### **Schritt 3: Aktive Station ermitteln**
```python
def get_current_active_module():
    # Aus Session State, MQTT, oder Database
    return st.session_state.get("active_module_id", None)
```

## 📋 Configuration

### **Layout-Datei:** `omf2/config/ccu/shopfloor_layout.json`
```json
{
  "grid": {
    "rows": 3,
    "columns": 4,
    "cell_size": "100x100"
  },
  "modules": [
    {
      "id": "MILL",
      "type": "MILL",
      "serialNumber": "SVR3QA2098",
      "position": [1, 0]
    }
    // ... weitere Module
  ]
}
```

## 🔍 Troubleshooting

### **Problem: HTML wird als Text angezeigt**
**Lösung:** HTML-Strings müssen einzeilig sein (nicht mehrzeilig)

### **Problem: Falsches Seitenverhältnis**
**Lösung:** Container-Box verwendet CSS `aspect-ratio: 3/4`

### **Problem: SVG-Icons werden nicht angezeigt**
**Lösung:** SVG-Dateien in `omf2/assets/svgs/` prüfen und Icon Mapping aktualisieren

### **Problem: Module an falscher Position**
**Lösung:** Positionen in `shopfloor_layout.json` prüfen (Format: [x, y] = [Spalte, Zeile])

## 📈 Future Enhancements

### **Mögliche Erweiterungen:**
- **Zoom Controls** - Für größere/smallere Darstellung
- **Animation** - Für Übergänge zwischen Stationen
- **Real-time Updates** - MQTT-basierte Live-Updates
- **Custom Themes** - Verschiedene Farbschemata
- **Responsive Design** - Anpassung an verschiedene Bildschirmgrößen

## ✅ Production Checklist

- [x] **Feste 3:4 Container-Box** implementiert
- [x] **SVG-Icon System** funktional
- [x] **Position Mapping** korrekt
- [x] **HTML Rendering** optimiert
- [x] **Wiederverwendbare Komponenten** erstellt
- [x] **Test-Komponenten** verfügbar
- [x] **Dokumentation** vollständig
- [x] **Integration Guide** bereit

---

**Status:** PRODUCTION READY ✅  
**Ready for Integration in other UI-Tabs!** 🚀
