# SVG-Sizing Strategy - SOLL-Konzept

## Problem
SVG-Darstellung in verschiedenen UI-Komponenten mit unterschiedlichen Größenanforderungen:
- **Purchase Order:** Palett-SVGs sollen klein (100x100) sein
- **Lager (3x3 Grid):** Alle SVGs sollen einheitlich groß (160x160) sein  
- **Andere UI:** SVGs sollen mit Fenstergröße skalieren (AS-IS)

## Lösung: UI-Komponenten entscheiden über Größe

### 1. Asset-Manager (NEUTRAL)
```python
# omf2/assets/asset_manager.py
def get_workpiece_palett(self) -> Optional[str]:
    """Lädt Palett-SVG in ORIGINAL-Größe"""
    return scope_svg_styles(svg_content)  # Nur CSS-Scoping

def get_workpiece_svg(self, color: str, pattern: str) -> Optional[str]:
    """Lädt Workpiece-SVG in ORIGINAL-Größe"""
    return scope_svg_styles(svg_content)  # Nur CSS-Scoping
```

**Prinzip:** Asset-Manager manipuliert KEINE Größen, nur CSS-Scoping für Konfliktvermeidung.

### 2. UI-Komponenten (ENTSCHEIDUNG)

#### A) Purchase Order - Palett-SVGs auf 100x100
```python
# omf2/ui/ccu/ccu_overview/purchase_order_subtab.py
palett_content = asset_manager.get_workpiece_palett()
if palett_content:
    palett_html = f"""
    <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
        <div style="width: 100px; height: 100px; overflow: hidden;">
            {palett_content}
        </div>
    </div>
    """
```

#### B) Lager (3x3 Grid) - Zwei Varianten

**Variante 1: Konstante Größe (160x160)**
```python
# omf2/tests/test_helper_apps/stock_and_workpiece_layout_test.py
def _render_inventory_position_direct(position: str, workpiece_type: str, asset_manager):
    if workpiece_type is None:
        # Palett-SVG mit fester Größe
        palett_content = asset_manager.get_workpiece_palett()
        if palett_content:
            st.markdown(f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                <div style="width: 160px; height: 160px; overflow: hidden;">
                    {palett_content}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Workpiece-SVG mit fester Größe
        svg_content = asset_manager.get_workpiece_svg(workpiece_type, "instock_unprocessed")
        if svg_content:
            st.markdown(f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                <div style="width: 160px; height: 160px; overflow: hidden;">
                    {svg_content}
                </div>
            </div>
            """, unsafe_allow_html=True)
```

**Variante 2: Skalierbares 3x3 Lager-SVG (Ziel)**
```python
# ZUKÜNFTIG: Zusammengesetztes SVG aus 9 individuellen SVGs
def _render_inventory_grid_scalable(inventory_data, asset_manager):
    """Erstellt ein skalierbares 3x3 Lager-SVG aus 9 individuellen SVGs"""
    # Zusammensetzen der 9 SVGs zu einem großen SVG
    # Skaliert automatisch mit Fenstergröße
    # Keine feste Größe nötig
    pass
```

#### C) Andere UI - AS-IS Modus (skaliert mit Fenster)
```python
# omf2/ui/ccu/ccu_overview/product_catalog_subtab.py
svg_content = asset_manager.get_workpiece_svg("BLUE", "product")
if svg_content:
    # AS-IS Modus - skaliert mit Fenster
    st.markdown(f"""
    <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
        {svg_content}
    </div>
    """, unsafe_allow_html=True)
```

## Vorteile

### 1. Klare Trennung der Verantwortlichkeiten
- **Asset-Manager:** Nur Asset-Loading und CSS-Scoping
- **UI-Komponenten:** Entscheiden über Darstellungsmodus

### 2. Flexibilität
- Jede UI-Komponente kann ihren eigenen Modus wählen
- Keine Seiteneffekte zwischen verschiedenen UI-Komponenten

### 3. Wartbarkeit
- Änderungen an einer UI-Komponente betreffen keine anderen
- Klare Dokumentation der Größenstrategie

## Implementierung

### Geänderte Dateien:
1. **`omf2/assets/asset_manager.py`** - Asset-Manager neutral gemacht
2. **`omf2/ui/ccu/ccu_overview/purchase_order_subtab.py`** - Palett-SVGs auf 100x100
3. **`omf2/tests/test_helper_apps/stock_and_workpiece_layout_test.py`** - Lager-SVGs auf 160x160

### Auswirkungen:
- **`omf2/omf.py`:** Andere UI-Komponenten verwenden AS-IS Modus (skaliert mit Fenster)
- **`stock*_test.py`:** Lager (3x3 Grid) verwendet feste Größe (160x160), andere Tabs AS-IS Modus

## Status
✅ **IMPLEMENTIERT** - SOLL-Konzept umgesetzt und getestet
