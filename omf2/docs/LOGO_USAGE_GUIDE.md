# 🏢 ORBIS Logo Usage Guide

**Status:** PRODUCTION READY ✅  
**Datum:** 2025-01-09  
**Zweck:** ORBIS Company Logo Integration im OMF2 Dashboard

## 📋 Overview

Das ORBIS-Logo wird zentral über den Asset Manager verwaltet und prominent im Dashboard-Header angezeigt.

## 🎯 Logo Location

**Pfad:** `omf2/assets/logos/orbis_logo.png`  
**Größe:** 20KB  
**Format:** PNG (High-Quality)  
**Verwendung:** Dashboard Header, Dokumentation, Branding

## 🚀 Usage via Asset Manager

### **Standard-Verwendung:**

```python
from omf2.assets import get_asset_manager

# Get asset manager
asset_manager = get_asset_manager()

# Display ORBIS logo (prominent)
asset_manager.display_orbis_logo(width=150)
```

### **Custom Size:**

```python
# Smaller logo (e.g., sidebar)
asset_manager.display_orbis_logo(width=80)

# Larger logo (e.g., landing page)
asset_manager.display_orbis_logo(width=200)
```

### **Full Container Width:**

```python
# Logo fills container width (responsive)
asset_manager.display_orbis_logo(use_container_width=True)
```

### **Get Logo Path:**

```python
# Get path to logo file (for custom usage)
logo_path = asset_manager.get_orbis_logo_path()
if logo_path:
    st.image(logo_path, width=150)
```

## 🎨 Logo Specifications

### **Current Logo:**
- **File:** `orbis_logo.png`
- **Size:** 20KB
- **Dimensions:** High-quality PNG
- **Color:** Full color (ORBIS brand colors)
- **Background:** Transparent
- **Usage:** Universal (light/dark backgrounds)

### **Display Guidelines:**

| Context | Width | Usage |
|---------|-------|-------|
| **Dashboard Header** | 150px | Prominent branding |
| **Sidebar** | 80-100px | Compact branding |
| **Documentation** | 100-120px | Standard size |
| **Landing Page** | 200-250px | Large, prominent |

## 📐 Layout Examples

### **Dashboard Header (OMF2):**

```python
def _render_header(self):
    """Render dashboard header with prominent ORBIS logo"""
    from omf2.assets import get_asset_manager
    
    asset_manager = get_asset_manager()
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        # Prominent ORBIS Logo (150px)
        asset_manager.display_orbis_logo(width=150)
    
    with col2:
        st.markdown("# Modellfabrik Dashboard")
        st.markdown("### ORBIS Modellfabrik Control System")
    
    with col3:
        st.caption("OMF2 v2.0.0")
```

### **Sidebar:**

```python
with st.sidebar:
    # Compact logo in sidebar
    asset_manager.display_orbis_logo(width=80)
    st.divider()
    # ... sidebar content
```

### **Landing Page:**

```python
# Centered, large logo on landing page
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    asset_manager.display_orbis_logo(width=250)
    st.markdown("# Welcome to ORBIS Modellfabrik")
```

## 🔄 Fallback Behavior

Wenn das Logo nicht gefunden wird, zeigt der Asset Manager automatisch einen Fallback:

```
🏭
ORBIS Modellfabrik
```

### **Fallback-Code:**

```python
if logo_path:
    st.image(logo_path, width=width)
else:
    # Fallback: Factory emoji
    st.markdown("# 🏭")
    st.caption("ORBIS Modellfabrik")
```

## 🆕 Alternative Logos

Falls zukünftig andere Logo-Varianten benötigt werden:

### **Logo-Varianten:**
- `orbis_logo.png` - Standard (aktuell)
- `orbis_logo_white.png` - Für dunkle Hintergründe
- `orbis_logo_compact.png` - Kompakte Variante
- `orbis_logo.svg` - Skalierbare Variante

### **Integration:**

```python
# In asset_manager.py erweitern:

def get_orbis_logo_path(self, variant: str = "standard") -> Optional[str]:
    """Returns path to ORBIS logo variant"""
    logo_files = {
        "standard": "orbis_logo.png",
        "white": "orbis_logo_white.png",
        "compact": "orbis_logo_compact.png",
        "svg": "orbis_logo.svg"
    }
    
    logo_file = logo_files.get(variant, "orbis_logo.png")
    logo_path = self.logos_dir / logo_file
    
    return str(logo_path) if logo_path.exists() else None
```

## ✅ Best Practices

### **✅ Empfohlen:**
- Logo über Asset Manager laden (nicht direkter Pfad)
- Konsistente Größen verwenden (80px, 100px, 150px, 200px)
- Fallback-Logik nutzen (emoji)
- Logo in `logos/` Ordner ablegen (nicht `icons/`)

### **🚫 Vermeiden:**
- Direkter Pfad-Zugriff ohne Asset Manager
- Logo in `icons/` Ordner (nur für Module)
- Zu kleine Logos (< 60px) - schwer lesbar
- Zu große Logos (> 300px) - unprofessionell

## 📊 Asset-Struktur

```
omf2/assets/
├── icons/          # ❌ NICHT für Logos (nur Module)
├── logos/          # ✅ FÜR Logos (ORBIS, Partner)
│   └── orbis_logo.png
└── svgs/           # SVG-Icons (Module)
```

## 🔧 Troubleshooting

### **Problem: Logo wird nicht angezeigt**

**Lösung:**
1. Prüfen, ob `omf2/assets/logos/orbis_logo.png` existiert
2. Asset Manager neu initialisieren
3. Fallback wird automatisch verwendet

### **Problem: Logo zu groß/klein**

**Lösung:**
```python
# Width-Parameter anpassen
asset_manager.display_orbis_logo(width=100)  # Kleiner
asset_manager.display_orbis_logo(width=200)  # Größer
```

### **Problem: Logo falsche Farbe**

**Lösung:**
- Logo ist Full-Color PNG
- Für dunkle Hintergründe: `orbis_logo_white.png` verwenden

## 📋 Integration Checklist

- ✅ Logo in `omf2/assets/logos/` ablegen
- ✅ Asset Manager um Logo-Funktionalität erweitert
- ✅ Dashboard Header mit prominentem Logo (150px)
- ✅ Fallback-Logik implementiert (emoji)
- ✅ Dokumentation erstellt

---

**Status:** PRODUCTION READY ✅  
**Prominent Logo Display Implemented!** 🏢

