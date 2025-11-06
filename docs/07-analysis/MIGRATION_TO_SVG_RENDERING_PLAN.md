# Migration Plan: SVG-Rendering für Produktiv-Code

## ✅ Analyse: Machbarkeit

### 1. **Route-Logik: ✅ KOMPATIBEL**

**Produktiv:**
- `get_route_for_navigation_step()` → gibt `List[Tuple[float, float]]` zurück (Pixel-Koordinaten)
- Verwendet `route_segments_to_points()` für Koordinaten-Konvertierung

**Example:**
- `compute_route_edge_points()` → gibt `List[Tuple[int, int]]` zurück (Pixel-Koordinaten)
- Verwendet `route_utils.id_to_position_map()` für Koordinaten-Konvertierung

**Fazit:** Beide geben Pixel-Koordinaten zurück → **direkt kompatibel** ✅

### 2. **Skalierung: ✅ MÖGLICH**

**Example-App:**
- `scale` Parameter: `0.25` bis `2.0` (25% bis 200%)
- SVG wird über `width` und `height` Attribute skaliert

**Anforderungen:**
- Production/Storage Orders: **60%** → `scale=0.6` ✅
- Factory Configuration: **100%** → `scale=1.0` ✅
- Shopfloor Module Selection & Details: **50%** → `scale=0.5` ✅

**Fazit:** Alle Anforderungen erfüllbar ✅

### 3. **Highlighting: ✅ MÖGLICH**

**Example-App:**
- `highlight_cells: List[Tuple[int, int]]` → unterstützt
- Render-Reihenfolge: Normal → Highlighted → Intersections → Routes
- Orange Umrandung (4px) + leichte orange Füllung

**Anforderungen:**
- View-Mode mit Highlighting: ✅ Unterstützt
- Shopfloor Module Selection & Details: ✅ Highlight über Dropdown steuerbar

**Fazit:** Alle Anforderungen erfüllbar ✅

## 🎯 Migrations-Plan

### Phase 1: Code-Übernahme

**1.1 Example-App Code nach Produktiv kopieren:**
- `render_shopfloor_svg()` → `omf2/ui/ccu/common/shopfloor_layout.py`
- Helper-Funktionen übernehmen:
  - `_get_entity_at_position()`
  - `_get_cell_size()`
  - `_is_compound_cell()`
  - `_get_background_color()`
  - `_should_show_label()`
  - `_get_label_text()`
  - `_get_icon_size_ratio()`
  - `_calculate_icon_size()`
  - `_get_compound_layout()`
  - `_scale_svg_properly()`
  - `_get_icon_svg()`

**1.2 Route-Logik Integration:**
- Produktive `get_route_for_navigation_step()` verwenden (bereits vorhanden)
- `compute_route_edge_points()` optional als Alternative
- Route-Koordinaten sind kompatibel (beide geben Pixel-Koordinaten zurück)

### Phase 2: API-Anpassung

**2.1 `show_shopfloor_layout()` API anpassen:**
- `scale` Parameter hinzufügen (statt/zusätzlich zu `max_width`/`max_height`)
- `layout_config` Parameter nutzen (bereits vorhanden)
- `asset_manager` Parameter nutzen (bereits vorhanden)
- `route_points` Parameter nutzen (bereits vorhanden)
- `enable_click` Parameter optional (für Factory Configuration)

**2.2 Kompatibilität:**
- Alte API-Parameter bleiben unterstützt (Rückwärtskompatibilität)
- Neue `scale`-Parameter wird bevorzugt verwendet

### Phase 3: Integration in Produktiv-Code

**3.1 Production Orders Subtab:**
```python
show_shopfloor_layout(
    active_module_id=active_module,
    active_intersections=active_intersections,
    route_points=route_points,
    agv_progress=agv_progress,
    scale=0.6,  # 60% Größe
    enable_click=False,  # View-Mode
)
```

**3.2 Storage Orders Subtab:**
```python
show_shopfloor_layout(
    active_module_id=active_module,
    active_intersections=active_intersections,
    route_points=route_points,
    agv_progress=agv_progress,
    scale=0.6,  # 60% Größe
    enable_click=False,  # View-Mode
)
```

**3.3 Factory Configuration:**
```python
show_shopfloor_layout(
    title="Shopfloor Layout",
    scale=1.0,  # 100% Größe
    enable_click=True,  # Interactive Mode
)
```

**3.4 Shopfloor Module Selection & Details:**
```python
col1, col2 = st.columns([1, 1])
with col1:
    # Dropdown und Details
with col2:
    show_shopfloor_layout(
        highlight_cells=display_region,
        scale=0.5,  # 50% Größe
        enable_click=False,  # View-Mode
    )
```

### Phase 4: Cleanup

**4.1 Fallbacks entfernen:**
- ✅ `display_variants` aus JSON entfernen (nicht mehr benötigt)
- ✅ Legacy aliases aus `asset_manager.py` entfernen (nicht mehr benötigt)
- ✅ Alte HTML/CSS-Grid-Logik entfernen (durch SVG ersetzt)

**4.2 Alte Code-Pfade entfernen:**
- `_generate_html_grid()` → entfernen
- `_generate_split_cell_html()` → entfernen
- `_get_split_cell_icon()` → entfernen
- Alle HTML/CSS-basierten Render-Funktionen

## 📋 Vorteile der Migration

### ✅ Code-Vereinfachung
- **Weniger Code:** HTML/CSS-Grid-Logik entfernt
- **Einheitliche Rendering-Logik:** SVG für alle Modi
- **Weniger Spezialfälle:** JSON-basierte Konfiguration statt Hardcoded

### ✅ Wartbarkeit
- **Konsistente Struktur:** Gleiche Logik wie Example-App
- **Einfachere Tests:** SVG-Rendering ist einfacher zu testen
- **Bessere Skalierbarkeit:** `scale` Parameter für alle Größen

### ✅ Features
- **Skalierbares Rendering:** Beliebig skalierbar (0.25x bis 2.0x)
- **Konsistente Highlighting:** Gleiche Logik für alle Modi
- **Bessere Route-Visualisierung:** SVG-basierte Polyline

## 🚨 Risiken & Mitigation

### Risiko 1: Route-Koordinaten-Unterschiede
- **Problem:** Produktive Route-Utils gibt center-based Koordinaten, Example edge-based
- **Mitigation:** Beide Formate unterstützen oder Konvertierung einbauen

### Risiko 2: Layout-Unterschiede
- **Problem:** Produktives HTML/CSS-Grid hat andere Positionierung als SVG
- **Mitigation:** SVG-Rendering mit gleichen Grid-Dimensionen testen

### Risiko 3: Performance
- **Problem:** SVG-Rendering könnte langsamer sein als HTML/CSS
- **Mitigation:** Performance-Tests durchführen, ggf. Caching

## ✅ Nächste Schritte

1. ⏳ **Code-Übernahme:** Example-App Code nach Produktiv kopieren
2. ⏳ **API-Anpassung:** `show_shopfloor_layout()` mit `scale` Parameter erweitern
3. ⏳ **Integration:** Alle drei Verwendungsstellen (Production/Storage/Factory) anpassen
4. ⏳ **Tests:** End-to-End Tests mit produktivem Code
5. ⏳ **Cleanup:** Fallbacks und alte Code-Pfade entfernen
6. ⏳ **Commit:** Änderungen committen und pushen

