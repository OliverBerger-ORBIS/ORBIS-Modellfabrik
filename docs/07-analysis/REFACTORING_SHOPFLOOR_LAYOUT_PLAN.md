# Refactoring Plan: Vereinfachung der Shopfloor Layout Spezialfälle

## Ziel
Spezialfälle aus `app.py` entfernen und durch konfigurierbare JSON-Parameter ersetzen.

## Aktuelle Spezialfälle (Hardcoded in app.py)

### 1. Compound-Zellen (HBW/DPS)
- **Code:** Zeile 319: `if (r, c) in ((1, 0), (1, 3)):`
- **Problem:** Hardcoded Positions-Checks
- **Aktuell:** `attached_assets` wird aus Module-Daten gelesen
- **Benötigt:** Flag, ob Zelle eine Compound-Zelle ist

### 2. Abweichung von Zellgröße (200×200)
- **Code:** Zeile 241-247: Spezielle Positionierung für `h == 100` und `h == 300`
- **Problem:** Hardcoded Größen und Positionen
- **Aktuell:** 
  - COMPANY/SOFTWARE: 200×100px (h=100)
  - HBW/DPS: 200×300px (h=300)
- **Benötigt:** Konfigurierbare `cell_size` im JSON

### 3. Hintergrundfarbe
- **Code:** Zeile 256: `cell_fill = "#cfe6ff" if (r, c) in ((0, 0), (0, 3)) else "none"`
- **Problem:** Hardcoded Farben und Positionen
- **Aktuell:** Nur COMPANY/SOFTWARE haben blauen Hintergrund
- **Benötigt:** Optionales `background_color` Feld

### 4. Label-Anzeige
- **Code:** Zeile 299-313: Labels werden immer erstellt
- **Problem:** Keine Option zum Ausschalten
- **Aktuell:** Labels werden immer angezeigt
- **Benötigt:** Optionales `show_label` Feld (default: false)

### 5. VIS_SPEC Dict (Hardcoded)
- **Code:** Zeile 46-59: Hardcoded Farben und Größen für alle Zellen
- **Problem:** Alle visuellen Eigenschaften hardcoded
- **Benötigt:** Migration zu JSON-basierter Konfiguration

## Vorgeschlagene JSON-Struktur

### Option 1: Felder direkt in Entity-Definitionen (empfohlen)

```json
{
  "modules": [
    {
      "id": "HBW",
      "type": "HBW",
      "position": [1, 0],
      "cell_size": [200, 300],          // [width, height] in px, default: [200, 200]
      "is_compound": true,               // default: false
      "attached_assets": ["HBW_SQUARE1", "HBW_SQUARE2"],
      "compound_layout": {               // optional, nur wenn is_compound=true
        "positions": [[0, 0], [100, 0]], // relative positions für attached_assets in px
        "size": [100, 100]               // Größe jedes attached_asset in px
      },
      "background_color": null,          // optional, default: transparent
      "show_label": false,               // default: false
      "label_text": null                 // optional, falls abweichend von id
    },
    {
      "id": "MILL",
      "type": "MILL",
      "position": [0, 1],
      // cell_size, is_compound, background_color, show_label: alle optional mit defaults
    }
  ],
  "fixed_positions": [
    {
      "id": "COMPANY",
      "type": "ORBIS",
      "position": [0, 0],
      "cell_size": [200, 100],          // Abweichung von Standard
      "background_color": "#cfe6ff",    // Blauer Hintergrund
      "show_label": false               // Kein Label
    }
  ],
  "intersections": [
    {
      "id": "1",
      "type": "INTERSECTION-1",
      "position": [1, 1],
      // cell_size, background_color, show_label: optional
    }
  ]
}
```

### Option 2: Separate `display_config` Sektion

```json
{
  "display_config": {
    "default_cell_size": [200, 200],
    "entities": {
      "HBW": {
        "cell_size": [200, 300],
        "is_compound": true,
        "background_color": null,
        "show_label": false
      },
      "COMPANY": {
        "cell_size": [200, 100],
        "background_color": "#cfe6ff",
        "show_label": false
      }
    }
  }
}
```

**Empfehlung: Option 1** (direkt in Entity-Definitionen)
- Einfacher zu warten
- Alles an einer Stelle
- Klarere Zuordnung

## Implementierungsplan

### Phase 1: JSON-Struktur erweitern
1. ✅ `cell_size` Feld hinzufügen (optional, default: [200, 200])
2. ✅ `is_compound` Feld hinzufügen (optional, default: false)
3. ✅ `background_color` Feld hinzufügen (optional, default: transparent)
4. ✅ `show_label` Feld hinzufügen (optional, default: false)
5. ✅ `label_text` Feld hinzufügen (optional, default: id)

### Phase 2: Helper-Funktionen erstellen
1. `_get_entity_at_position(layout, row, col)` → findet Entity (module/fixed/intersection)
2. `_get_cell_size(entity, default=[200, 200])` → liefert [width, height]
3. `_is_compound_cell(entity)` → prüft `is_compound` Flag
4. `_get_background_color(entity)` → liefert color oder "none"
5. `_should_show_label(entity)` → prüft `show_label` Flag
6. `_get_label_text(entity)` → liefert label_text oder id
7. `_get_icon_size_ratio(entity_type)` → liefert Ratio: Intersections=0.8, Modules=0.56, Fixed=0.8
8. `_calculate_icon_size(entity, cell_size, entity_type)` → berechnet Icon-Größe mit Grenzen-Beachtung
9. `_get_compound_layout(entity)` → liefert compound_layout mit positions Array

### Phase 3: Code-Refactoring
1. **VIS_SPEC entfernen** → vollständig durch JSON-Konfiguration ersetzen
2. **Hardcoded Position-Checks entfernen:**
   - Zeile 241: `if (r, c) in ((0, 0), (0, 3)) and h == 100:`
   - Zeile 244: `if (r, c) in ((1, 0), (1, 3)) and h == 300:`
   - Zeile 256: `cell_fill = "#cfe6ff" if (r, c) in ((0, 0), (0, 3)) else "none"`
   - Zeile 288: `if (r, c) in ((1, 0), (1, 3)) and h == 300:`
   - Zeile 319: `if (r, c) in ((1, 0), (1, 3)):`
3. **Dynamische Größenberechnung:**
   - `cell_size` aus Entity lesen
   - Positionierung basierend auf `cell_size` berechnen
4. **Compound-Rendering:**
   - Nur wenn `is_compound == true`
   - `attached_assets` über `compound_layout.positions` Array rendern
   - `compound_layout.size` für Größe verwenden
5. **Label-Rendering:**
   - Nur wenn `show_label == true`
   - `label_text` oder `id` verwenden
6. **Icon-Sizing:**
   - Intersections: 80% von Zellgröße
   - Modules: 56% von main Komponente (bei Compounds: 56% von 200×200)
   - Fixed_positions: 80% mit Grenzen-Beachtung (Höhe ist begrenzender Faktor)
7. **Stroke-Farben:**
   - Zell-Umrandung: Einheitlich leichtes Grau (#e0e0e0)
   - Container-Umrandung: Mittelgrau (#888888)
   - Entfernen aller farbigen Stroke-Logik

### Phase 4: Migration bestehender Daten
1. Beispiel-JSON (`examples/shopfloor_test_app/shopfloor_layout.json`) aktualisieren
2. Produktiv-JSON (`omf2/config/ccu/shopfloor_layout.json`) aktualisieren
3. Rückwärtskompatibilität: Defaults für fehlende Felder

## Rückwärtskompatibilität

### Fallback-Strategie
- **Fehlende `cell_size`:** Default [200, 200]
- **Fehlende `is_compound`:** Default false
- **Fehlende `background_color`:** Default "none" (transparent)
- **Fehlende `show_label`:** Default false (kein Label)
- **Fehlende `label_text`:** Default `id` oder `entity_id`

### VIS_SPEC Migration
- Solange VIS_SPEC existiert, kann es als Fallback verwendet werden
- Nach vollständiger Migration: VIS_SPEC entfernen

## Vorteile

1. **Weniger Code:** Hardcoded Spezialfälle entfernt
2. **Flexibler:** Neue Zelltypen ohne Code-Änderung
3. **Wartbarer:** Konfiguration an einer Stelle (JSON)
4. **Konsistent:** Gleiche Struktur für alle Entity-Typen
5. **Testbar:** Einfacher zu testen mit verschiedenen Konfigurationen

## Offene Fragen - BEANTWORTET

1. **Compound-Positionierung:** ✅ GELÖST
   - `attached_assets` über `positions` Array konfigurierbar
   - Beispiel: `"compound_layout": { "positions": [[0, 0], [100, 0]] }` für 100×100px Quadrate
   
2. **Stroke-Farben:** ✅ GELÖST
   - **Stroke = Umrandung der Zellen**
   - Zell-Umrandung: Einheitlich leichtes Grau (z.B. `#e0e0e0`)
   - Shopfloor-Container (800×600): Mittelgraue Umrandung (z.B. `#888888`)

3. **Icon-Sizing:** ✅ GELÖST
   - **Intersections:** 80% von Zellgröße
   - **Modules:** 56% von "main" Komponente (bei Compounds: 56% von 200×200 main compartment)
   - **Fixed_positions:** 80% (mit Grenzen beachten - Höhe ist begrenzender Faktor)
   - Beispiel: Zellgröße 200×100, SVG 512×512 → Höhe ist Limit → 100px × 80% = 80px → SVG wird 80×80px

## Nächste Schritte

1. ✅ Plan erstellen (dieses Dokument)
2. ✅ User-Review des Plans
3. ✅ JSON-Struktur finalisieren
4. ✅ Helper-Funktionen implementieren
5. ✅ Code-Refactoring durchführen (examples/shopfloor_test_app/app.py)
6. ✅ JSON-Dateien aktualisieren (examples/shopfloor_test_app/shopfloor_layout.json)
7. ✅ Tests durchführen (lokal getestet)
8. ⏳ **NÄCHSTER SCHRITT:** Produktiv-JSON aktualisieren (`omf2/config/ccu/shopfloor_layout.json`)
9. ⏳ Produktiv-Code migrieren (`omf2/ui/ccu/common/shopfloor_layout.py`)
10. ⏳ End-to-End Tests mit produktivem Code
11. ⏳ Committen und pushen

## ✅ Abgeschlossene Implementierung (Example-App)

### Helper-Funktionen
- ✅ `_get_entity_at_position()` - findet Entity an Position
- ✅ `_get_cell_size()` - liest Zellgröße aus JSON
- ✅ `_is_compound_cell()` - prüft Compound-Flag
- ✅ `_get_background_color()` - liest Hintergrundfarbe
- ✅ `_should_show_label()` / `_get_label_text()` - Label-Logik
- ✅ `_get_icon_size_ratio()` / `_calculate_icon_size()` - Icon-Sizing mit automatischer Begrenzungsfaktor-Erkennung
- ✅ `_get_compound_layout()` - liest Compound-Layout

### Code-Refactoring
- ✅ VIS_SPEC entfernt (nur noch in `main()` für Route-Selection)
- ✅ Hardcoded Position-Checks entfernt
- ✅ Dynamische Größenberechnung implementiert
- ✅ Compound-Rendering über `positions` Array
- ✅ Icon-Sizing: Intersections 80%, Modules 56%, Fixed 80% (automatische Begrenzungsfaktor-Erkennung)
- ✅ Stroke-Farben: Einheitlich leichtes Grau (#e0e0e0)
- ✅ Container-Umrandung: Mittelgrau (#888888)
- ✅ Render-Reihenfolge: Normal → Highlighted → Intersections → Routes
- ✅ Interactive Mode: Hover/Click Zellen werden per JavaScript ans Ende verschoben

### UI-Verbesserungen
- ✅ View-Mode: Orange Umrandung (4px) + leichte orange Füllung
- ✅ Interactive Mode: Hover (2px orange) + Click (4px orange) mit korrekter Render-Reihenfolge
- ✅ Route-Dicke: 6px (reduziert von 8px)
- ✅ Labels: Konfigurierbar über `show_label` Flag

### JSON-Struktur
- ✅ Beispiel-JSON aktualisiert mit allen neuen Feldern

