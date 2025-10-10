# 🎨 SVG-Icon Mapping Guide

**Status:** PRODUCTION READY ✅  
**Datum:** 2025-01-07  
**Zweck:** Einfacher Austausch von SVG-Icons im Shopfloor Layout System

## 📋 Overview

Dieser Guide erklärt, wie SVG-Icons im Shopfloor Layout System getauscht werden können. Das System verwendet ein zentrales Icon-Mapping, das es ermöglicht, Symbole einfach auszutauschen, ohne den Code zu ändern.

## 🎯 Icon Mapping Location

**Datei:** `omf2/assets/asset_manager.py`  
**Zeilen:** 37-55

```python
icon_mapping = {
    "HBW": "ic_ft_hbw.svg",           # High-Bay Warehouse
    "DRILL": "ic_ft_drill.svg",       # Drilling Station
    "MILL": "ic_ft_mill.svg",         # Milling Station
    "AIQS": "ic_ft_aiqs.svg",         # Quality Control
    "DPS": "ic_ft_dps.svg",           # Delivery/Pickup Station
    "CHRG": "ic_ft_chrg.svg",         # Charging Station
    "FTS": "ic_ft_fts.svg",           # Transport System
    "INTERSECTION": "add_2_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "EMPTY": None,  # Leer - kein Icon
}
```

## 📁 Asset-Verzeichnis Struktur

### **SVG-Icons:** `omf2/assets/svgs/`
Skalierbare Vektor-Icons für Module

### **PNG-Icons:** `omf2/assets/icons/`
Raster-Icons für Module (Fallback)

### **Logos:** `omf2/assets/logos/`
Firmen-Logos (ORBIS, Partner, etc.)

### **Verfügbare SVG-Icons:**
```
omf2/assets/svgs/
├── add_2_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg          # Kreuzungspunkt
├── barcode_scanner_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg # Scanner
├── construction_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg    # Bau/Mill
├── conveyor_belt_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg   # Förderband/DPS
├── ev_station_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg      # Ladestation
├── gavel_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg          # Hammer/Gericht
├── robot_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg          # Roboter/AIQS
├── rv_hookup_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg      # Anhänger/FTS
├── shelves_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg        # Regale
├── tools_power_drill_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg # Bohrer
└── warehouse_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg      # Lager/HBW
```

## 🔧 Icon Tauschen - Schritt-für-Schritt

### **Schritt 1: Neue SVG-Datei hinzufügen**
```bash
# Neue SVG-Datei in das svgs-Verzeichnis kopieren
cp /path/to/your/new_icon.svg omf2/assets/svgs/
```

### **Schritt 2: Icon Mapping aktualisieren**
```python
# In omf2/assets/asset_manager.py (Zeilen 37-55)
icon_mapping = {
    "HBW": "your_new_warehouse_icon.svg",  # Neues Icon
    "DRILL": "tools_power_drill_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "MILL": "construction_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "AIQS": "robot_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "DPS": "conveyor_belt_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "CHRG": "ev_station_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "INTERSECTION": "add_2_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "EMPTY": None,  # Leer - kein Icon
}
```

### **Schritt 3: Layout automatisch aktualisiert**
Das Shopfloor Layout wird automatisch das neue Icon verwenden. Keine weiteren Änderungen nötig!

## 🆕 Neue Module hinzufügen

### **Schritt 1: SVG-Icon hinzufügen**
```bash
# Neues SVG-Icon in das svgs-Verzeichnis kopieren
cp /path/to/new_module_icon.svg omf2/assets/svgs/
```

### **Schritt 2: Icon Mapping erweitern**
```python
# In omf2/assets/asset_manager.py
icon_mapping = {
    "HBW": "warehouse_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "DRILL": "tools_power_drill_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "MILL": "construction_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "AIQS": "robot_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "DPS": "conveyor_belt_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "CHRG": "ev_station_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "NEW_MODULE": "new_module_icon.svg",  # Neues Modul hinzufügen
    "INTERSECTION": "add_2_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
    "EMPTY": None,
}
```

### **Schritt 3: Position in Layout-Konfiguration definieren**
```json
// In omf2/config/ccu/shopfloor_layout.json
{
  "modules": [
    {
      "id": "NEW_MODULE",
      "type": "NEW_MODULE",
      "serialNumber": "NEW001",
      "position": [1, 2]  // [Spalte, Zeile]
    }
    // ... bestehende Module
  ]
}
```

## 📐 SVG-Icon Spezifikationen

### **Icon-Größen:**
- **Zellengröße:** 100px → **Icon-Größe:** 66px (66%)

### **Icon-Typen:**
- **ic_ft_*.svg:** 24x24px, #0069b4 (ORBIS Blau) - Fischertechnik-Icons
- **omf_*.svg:** 24x24px, #0069b4 (ORBIS Blau) - OMF-spezifische Icons
- **intersection_*.svg:** 24x24px, #1f1f1f (Schwarz) - Intersection-Icons

## 🎨 Icon-Bibliotheken

### **Empfohlene Quellen:**
- **Google Material Icons:** https://fonts.google.com/icons
- **Material Design Icons:** https://materialdesignicons.com/
- **Heroicons:** https://heroicons.com/
- **Feather Icons:** https://feathericons.com/

### **Icon-Naming Convention:**
```
ic_ft_{module_name}.svg     # Fischertechnik-Icons (24x24)
omf_{component_name}.svg    # OMF-spezifische Icons (24x24)
intersection_{type}.svg     # Intersection-Icons (24x24)

Beispiele:
- ic_ft_hbw.svg (Fischertechnik High-Bay Warehouse)
- omf_machine.svg (OMF Machine Icon)
- add_2.svg (Intersection Icon)
```

## 🔍 Troubleshooting

### **Problem: Icon wird nicht angezeigt**
**Lösung:** 
1. SVG-Datei in `omf2/assets/svgs/` prüfen
2. Dateiname im Icon Mapping prüfen
3. SVG-Format und -Struktur prüfen

### **Problem: Icon zu groß/klein**
**Lösung:** SVG wird automatisch auf 60% der Zellengröße skaliert

### **Problem: Icon falsche Farbe**
**Lösung:** SVG `fill` Attribut auf `#1f1f1f` setzen

### **Problem: Icon verzerrt**
**Lösung:** SVG `viewBox` auf `0 -960 960 960` setzen

## 🧪 Icon Testing

### **Test-Komponente:**
```python
from omf2.ui.ccu.common.shopfloor_html_test import show_html_rendering_test
show_html_rendering_test()
```

### **Verification:**
```python
from omf2.ui.ccu.common.shopfloor_verification import show_shopfloor_verification
show_shopfloor_verification()
```

## 📋 Icon Mapping Reference

### **Aktuelle Module:**
| Modul | Icon | Beschreibung |
|-------|------|--------------|
| HBW | warehouse_40dp_*.svg | High-Bay Warehouse |
| DRILL | tools_power_drill_40dp_*.svg | Drilling Station |
| MILL | construction_40dp_*.svg | Milling Station |
| AIQS | robot_40dp_*.svg | Quality Control |
| DPS | conveyor_belt_40dp_*.svg | Delivery/Pickup Station |
| CHRG | ev_station_40dp_*.svg | Charging Station |

### **Spezielle Icons:**
| Typ | Icon | Beschreibung |
|-----|------|--------------|
| INTERSECTION | add_2_40dp_*.svg | Kreuzungspunkt |
| EMPTY | None | Leere Position |

## ✅ Best Practices

### **✅ Empfohlen:**
- SVG-Icons verwenden (skalierbar)
- Material Design Icons verwenden
- Konsistente Naming Convention
- Icons in `omf2/assets/svgs/` ablegen
- Icon Mapping zentral verwalten

### **🚫 Vermeiden:**
- PNG/JPG Icons (nicht skalierbar)
- Hardcodierte Icon-Pfade
- Icons in verschiedenen Verzeichnissen
- Inkonsistente Icon-Größen
- Komplexe SVG-Pfade (Performance)

---

**Status:** PRODUCTION READY ✅  
**Ready for Icon Customization!** 🎨
