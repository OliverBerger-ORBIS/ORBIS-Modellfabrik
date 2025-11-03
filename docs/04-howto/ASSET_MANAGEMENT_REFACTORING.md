# Asset Management Refactoring Plan

**Ziel:** Vereinheitlichtes, zentrales Asset-Management mit Mapping-basierter Auflösung und Pre-Commit-Validierung.

## Aktuelle Situation

### Probleme:
1. **Zwei Asset-Manager:** `asset_manager.py` und `heading_icons.py` (separate Module)
2. **Irreführende Verzeichnisstruktur:** `svgs/` enthält sowohl Module-Icons als auch generelle Shopfloor-Icons
3. **Verstreute Mappings:** Icon-Mappings teilweise in Code, teilweise in separaten Dateien
4. **Fallback-Code:** Viele Fallback-Logik zur Laufzeit statt Pre-Commit-Validierung
5. **UI-Symbols getrennt:** Tab-Icons als Emojis in `symbols.py`, nicht im Asset-Manager

### Aktuelle Verzeichnisstruktur:
```
omf2/assets/
├── svgs/              # ❌ Irreführend: Module + Shopfloor + UI mixed
├── headings/          # ✅ Thematisch klar
├── workpiece/         # ✅ Thematisch klar
├── logos/             # ✅ Thematisch klar
├── backup/            # ❌ Sollte entfernt/archiviert werden
├── ftfe/              # ❌ Legacy? Prüfen
├── pngs/              # ⚠️ Legacy PNGs - wahrscheinlich nicht mehr benötigt
├── asset_manager.py   # Haupt-Asset-Manager
└── heading_icons.py   # ❌ Sollte in asset_manager.py integriert werden
```

## Vorschlag: Neue Struktur (Konsolidiert)

### Thematische Verzeichnisstruktur (nicht zu granular):
```
omf2/assets/
├── svg/               # ✅ Ersetzt "svgs" - klarer Name, alle SVGs hier
│   ├── headings/      # Heading-Icons für UI-Sektionen (bleibt)
│   ├── workpiece/     # Workpiece-SVGs (bleibt)
│   ├── shopfloor/     # Shopfloor-Assets (Module-Icons + generelle Shopfloor-Icons)
│   │                  # ⚠️ KEINE Unterverzeichnisse! Alles direkt in shopfloor/
│   │                  # Enthält: Module-Icons, Intersections, Company/Software-Logos
│   └── placeholders/  # UI-generische Assets (empty.svg, question.svg, camera-placeholder.svg)
├── asset_manager.py   # Zentraler Asset-Manager (ersetzt heading_icons.py)
└── __init__.py
```

**Begründung:**
- `svg/` ist klarer als `svgs/` - alle SVG-Assets unter einem Dach
- Thematische Unterverzeichnisse: `headings/`, `workpiece/`, `shopfloor/`, `placeholders/`
- **Shopfloor ohne Unterverzeichnisse** - Module-Icons und generelle Shopfloor-Icons zusammen (nicht zu granular)
- Mapping als Python Dict in `asset_manager.py` (bessere Performance, Type-Safety)

**Datei-Zuordnung:**
- `headings/` → bleibt wie bisher
- `workpiece/` → bleibt wie bisher  
- `svgs/*.svg` → `svg/shopfloor/*.svg` (Module-Icons, Intersections, Logos)
- `svgs/empty.svg`, `svgs/camera-placeholder.svg` → `svg/placeholders/`
- `headings/question.svg` → `svg/placeholders/question.svg` (optional)

## Zentrale Mapping-Struktur

### Python Dictionary (empfohlen nach Performance-Analyse)

**Performance-Analyse:**
- **Dict (Python):** ~0ms Ladezeit (bereits im Bytecode), keine File-IO, kein Parsing
- **YAML:** ~1-10ms Ladezeit (Parsing + File-IO), zusätzliche Dependency

**Da Icons selten getauscht werden:**
- ✅ Mapping wird 1x beim Singleton-Init geladen (Streamlit-Start)
- ✅ SVG-Inhalte werden gecacht (Memory-Cache)
- ✅ Neustart für neue SVGs ist kein Problem
- ✅ Dict ist schneller und typsicherer

**Vorteile Dict:**
- ✅ **Bessere Performance:** Kein Parsing nötig, direkt verfügbar
- ✅ **Type-Safety:** IDE-Support, Syntax-Check zur Compile-Zeit
- ✅ **Keine zusätzliche Dependency:** YAML-Parser nicht nötig
- ✅ **Bessere Wartbarkeit:** Code-Review einfacher, Versionierung klar

**YAML hätte Vorteil nur bei:**
- ❌ Häufiger Asset-Austausch ohne Neustart (nicht nötig)
- ❌ Hot-Reload-Anforderungen (nicht gewünscht)

```python
# omf2/assets/asset_manager.py

# Globale Defaults
ASSET_DEFAULTS = {
    "fallback": "placeholders/question.svg",
    "empty": "placeholders/empty.svg",
}

# Zentrale Mapping-Struktur: logical_key -> (subdirectory, filename)
# Unter assets/svg/ -> subdirectory/filename
ASSET_MAPPINGS: Dict[str, Tuple[str, str]] = {
  # === MODULE ICONS (shopfloor) ===
  "MILL": ("shopfloor", "milling-machine.svg"),
  "DRILL": ("shopfloor", "bohrer.svg"),
  "HBW": ("shopfloor", "stock.svg"),
  "DPS": ("shopfloor", "robot-arm.svg"),
  "FTS": ("shopfloor", "robotic.svg"),
  "AIQS": ("shopfloor", "ai-assistant.svg"),
  "CHRG": ("shopfloor", "fuel.svg"),
  
  # Unterstützende Objekte
  "TXT": ("shopfloor", "mixer.svg"),
  "ROUTER": ("shopfloor", "wifi-router.svg"),
  "PLATINE": ("shopfloor", "cpu.svg"),
  "RPI": ("shopfloor", "microcontroller.svg"),
  "MOSQUITTO": ("shopfloor", "wifi.svg"),
  "MACHINE": ("shopfloor", "robot-arm.svg"),
  "PC_TABLET": ("shopfloor", "responsive.svg"),
  "OPC_UA": ("shopfloor", "database.svg"),
  
  # === SHOPFLOOR ASSETS ===
  # Intersections
  "1": ("shopfloor", "intersection1.svg"),
  "2": ("shopfloor", "intersection2.svg"),
  "3": ("shopfloor", "intersection3.svg"),
  "4": ("shopfloor", "intersection4.svg"),
  
  # Company/Software Logos
  "COMPANY_rectangle": ("shopfloor", "ORBIS_logo_RGB.svg"),
  "SOFTWARE_rectangle": ("shopfloor", "information-technology.svg"),
  "ORBIS": ("shopfloor", "ORBIS_logo_RGB.svg"),  # Legacy alias
  "DSP": ("shopfloor", "information-technology.svg"),  # Legacy alias
  
  # Attached Assets
  "HBW_SQUARE1": ("shopfloor", "factory.svg"),
  "HBW_SQUARE2": ("shopfloor", "conveyor.svg"),
  "DPS_SQUARE1": ("shopfloor", "warehouse.svg"),
  "DPS_SQUARE2": ("shopfloor", "order-tracking.svg"),
  
  # === HEADING ICONS ===
  "DASHBOARD_ADMIN": ("headings", "visualisierung.svg"),
  "ORDERS": ("headings", "lieferung-bestellen.svg"),
  "PROCESS": ("headings", "gang.svg"),
  "CONFIGURATION": ("headings", "system.svg"),
  "MODULES_TAB": ("headings", "mehrere.svg"),
  "MESSAGE_CENTER": ("headings", "zentral.svg"),
  "GENERIC_STEERING": ("headings", "dezentral_1.svg"),
  "SYSTEM_LOGS": ("headings", "log.svg"),
  "ADMIN_SETTINGS": ("headings", "unterstutzung.svg"),
  "DASHBOARD": ("headings", "visualisierung.svg"),
  "MQTT_CLIENTS": ("headings", "satellitenschussel.svg"),
  "GATEWAY": ("headings", "router_1.svg"),
  "TOPIC": ("headings", "etikett.svg"),
  "TOPICS": ("headings", "etikett.svg"),
  "SCHEMAS": ("headings", "diagramm.svg"),
  "MODULES_ADMIN": ("headings", "mehrere.svg"),
  "STATIONS": ("headings", "dezentral.svg"),
  "TXT_CONTROLLERS": ("headings", "system.svg"),
  "WORKPIECES": ("headings", "box.svg"),
  "PRODUCTION_ORDERS": ("headings", "maschine.svg"),
  "STORAGE_ORDERS": ("headings", "ladung.svg"),
  "FACTORY_CONFIGURATION": ("headings", "grundriss.svg"),
  "SHOPFLOOR_LAYOUT": ("headings", "grundriss.svg"),
  "CUSTOMER_ORDERS": ("headings", "lieferung-bestellen.svg"),
  "PURCHASE_ORDERS": ("headings", "box.svg"),
  "INVENTORY": ("headings", "warehouse.svg"),
  "SENSOR_DATA": ("headings", "smart.svg"),
  
  # === PLACEHOLDERS ===
  "CAMERA_PLACEHOLDER": ("placeholders", "camera-placeholder.svg"),
  "EMPTY": ("placeholders", "empty.svg"),
  "QUESTION": ("placeholders", "question.svg"),
  
  # Special
  "EMPTY_MODULE": (None, None),  # Explizit kein Icon (für leere Shopfloor-Positionen)
}
```

### Caching-Strategie

**Mapping-Cache:**
- Dict wird 1x beim Singleton-Init geladen (Streamlit-Start)
- Bleibt im Memory für gesamte Session

**SVG-Content-Cache:**
- SVG-Inhalte werden gecacht in `_SVG_CACHE: Dict[str, str]`
- Einmal geladen, dann aus Memory
- Cache wird nur bei Neustart geleert (neue SVGs verfügbar)

**Performance-Charakteristika:**
- **Startup:** Dict-Loading ~0ms (bereits im Bytecode)
- **Runtime:** O(1) Dict-Lookup + gecachter SVG-Content
- **Memory:** Alle genutzten SVGs werden gecacht (trade-off: Memory vs. Speed)

## Zentrale Asset-Manager API

### Vereinfachte API:
```python
class OMF2AssetManager:
    """Zentraler Asset-Manager für alle SVG-Assets"""
    
    # === CORE METHODS ===
    def get_asset_path(self, key: str) -> Optional[Path]:
        """Gibt Pfad zu Asset zurück oder None (mit Default-Fallback)"""
        
    def get_asset_content(self, key: str, scoped: bool = True) -> Optional[str]:
        """Lädt SVG-Inhalt mit optionalem CSS-Scoping"""
        
    def get_asset_inline(
        self, 
        key: str, 
        size_px: Optional[int] = None, 
        color: Optional[str] = None
    ) -> Optional[str]:
        """Lädt SVG als inline HTML (für Headings)"""
    
    # === WORKPIECE METHODS (bleiben) ===
    def get_workpiece_svg(self, color: str, pattern: str = "product") -> Optional[str]:
        """Workpiece-SVG mit CSS-Scoping"""
    
    # === LEGACY COMPATIBILITY ===
    def get_module_icon_path(self, module_name: str) -> Optional[str]:
        """Legacy: Redirect zu get_asset_path()"""
    
    def get_svg_inline(self, key: str, size_px: Optional[int] = None) -> Optional[str]:
        """Legacy: Redirect zu get_asset_inline()"""
```

### Migration Path:
1. **Phase 1:** Neuer `asset_manager.py` mit zentralem Mapping
2. **Phase 2:** `heading_icons.py` als Wrapper (deprecated), leitet zu `asset_manager.py` weiter
3. **Phase 3:** Alle Verwendungen migrieren zu `asset_manager.get_asset_inline()`
4. **Phase 4:** `heading_icons.py` entfernen

## Default-Fallback Strategie

### Pre-Commit-Validierung (statt Laufzeit-Fallbacks):
```python
# omf2/scripts/validate_assets.py
def validate_asset_mappings():
    """Prüft, ob alle Mappings auf existierende Dateien zeigen"""
    asset_manager = get_asset_manager()
    missing = []
    
    for key, (directory, filename) in ASSET_MAPPINGS.items():
        path = asset_manager.assets_dir / directory / filename
        if not path.exists():
            missing.append((key, path))
    
    if missing:
        print("❌ Missing assets:")
        for key, path in missing:
            print(f"  - {key}: {path}")
        sys.exit(1)
    
    print(f"✅ All {len(ASSET_MAPPINGS)} assets exist")
```

### Pre-Commit Hook:
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: validate-assets
      name: Validate Asset Mappings
      entry: python omf2/scripts/validate_assets.py
      language: system
      pass_filenames: false
```

### Laufzeit-Fallback (nur für unbekannte Keys):
```python
def get_asset_path(self, key: str) -> Optional[Path]:
    """Gibt Pfad zurück, mit Default-Fallback nur für unbekannte Keys"""
    if key in ASSET_MAPPINGS:
        directory, filename = ASSET_MAPPINGS[key]
        path = self.assets_dir / directory / filename
        if path.exists():
            return path
        # Asset existiert nicht - sollte bei Pre-Commit gefangen werden
        logger.error(f"❌ Asset missing: {key} -> {path}")
        # Fallback zu default
        return self.assets_dir / "ui" / "question.svg"
    
    # Unbekannter Key
    logger.warning(f"⚠️ Unknown asset key: {key}")
    return self.assets_dir / "ui" / "question.svg"
```

## UI-Symbols (Tab-Icons)

### Option 1: Emojis bleiben (empfohlen)
- **Vorteil:** Einfach, keine SVG-Dateien nötig
- **Nachteil:** Keine Custom-Icons möglich
- **Status:** Aktuell in `symbols.py` als `TAB_ICONS` Dict

### Option 2: SVGs optional unterstützen
```python
class UISymbols:
    TAB_ICONS: Dict[str, str] = {
        "ccu_dashboard": "🏭",  # Emoji (default)
        # oder
        "ccu_dashboard": "DASHBOARD",  # Asset-Key -> lädt SVG via asset_manager
    }
    
    def get_tab_icon(self, key: str) -> str:
        icon = self.TAB_ICONS.get(key, "❓")
        # Wenn es ein Asset-Key ist, lade SVG
        if not icon.startswith(("🏭", "📋", ...)):  # Heuristik
            svg = asset_manager.get_asset_inline(icon, size_px=20)
            if svg:
                return svg
        return icon
```

**Empfehlung:** Option 1 (Emojis bleiben) für Tabs, da:
- Streamlit-Tabs unterstützen keine SVGs direkt in Labels
- Emojis sind ausreichend und performant
- SVGs nur für Heading-Icons (getrennte `<img>` Tags)

## Migrationsplan

### Schritt 1: Verzeichnisse umstrukturieren
1. Neue Verzeichnisse erstellen: `svg/shopfloor/`, `svg/placeholders/`
2. Dateien verschieben:
   - `svgs/milling-machine.svg` → `svg/shopfloor/milling-machine.svg`
   - `svgs/intersection1.svg` → `svg/shopfloor/intersection1.svg`
   - `svgs/empty.svg` → `svg/placeholders/empty.svg`
   - `svgs/camera-placeholder.svg` → `svg/placeholders/camera-placeholder.svg`
   - `headings/` → `svg/headings/` (komplettes Verzeichnis verschieben)
   - `workpiece/` → `svg/workpiece/` (komplettes Verzeichnis verschieben)
   - Optional: `headings/question.svg` → `svg/placeholders/question.svg`

### Schritt 2: Mapping konsolidieren
1. Zentrales `ASSET_MAPPINGS` Dict in `asset_manager.py` erstellen
2. Alle Mappings aus `heading_icons.py` und `asset_manager.py` zusammenführen
3. `heading_icons.py` als Wrapper implementieren (für Backward Compatibility)
4. Tests anpassen

### Schritt 3: Asset-Validierung
1. `omf2/scripts/validate_assets.py` erstellen
2. Pre-Commit Hook hinzufügen
3. Testen mit fehlenden Assets

### Schritt 4: Code-Migration
1. Alle `heading_icons.get_svg_inline()` → `asset_manager.get_asset_inline()`
2. Legacy-Methoden als Deprecated markieren
3. Tests laufen lassen

### Schritt 5: Cleanup
1. `heading_icons.py` entfernen
2. Alte Verzeichnisse aufräumen (`backup/`, `ftfe/`, `pngs/`)
3. Dokumentation aktualisieren

## Vorteile

1. ✅ **Ein zentraler Asset-Manager:** Keine Duplikation zwischen `asset_manager.py` und `heading_icons.py`
2. ✅ **Klarere Verzeichnisstruktur:** Thematische Ordnung ohne zu feingranular
3. ✅ **Mapping-basierte Auflösung:** Einfacher Austausch von Assets
4. ✅ **Pre-Commit-Validierung:** Fehlende Assets werden vor Commit erkannt
5. ✅ **Weniger Fallback-Code:** Validierung zur Build-Zeit statt Laufzeit
6. ✅ **Bessere Wartbarkeit:** Alle Mappings an einem Ort

## Offene Fragen

1. **SVGs in Tab-Labels:** Sollen Tab-Icons auch SVGs unterstützen oder bleiben bei Emojis?
   - **Empfehlung:** Emojis bleiben (schneller, einfacher)
   
2. **YAML vs. Python Dictionary:** Soll das Mapping in YAML ausgelagert werden?
   - **Entscheidung:** Python Dict (bessere Performance, Type-Safety, keine zusätzliche Dependency)
   - YAML würde nur bei Hot-Reload-Anforderungen Vorteile bringen (nicht nötig)
   
3. **Default-SVG:** `question.svg` oder `empty.svg` als Fallback?
   - **Empfehlung:** `question.svg` für unbekannte Keys, `empty.svg` für explizite Leer-Stellen

4. **Legacy-Verzeichnisse:** Wann werden `backup/`, `ftfe/`, `pngs/` entfernt?
   - **Empfehlung:** Nach erfolgreicher Migration und Validierung

## Nächste Schritte

1. ✅ Plan dokumentiert
2. ✅ User-Feedback eingearbeitet (Shopfloor ohne Unterverzeichnisse, Dict-Mapping für Performance)
3. ⏳ **Branch erstellen:** `refactor/asset-management-unified`
4. ⏳ Verzeichnisse umstrukturieren
5. ⏳ Mapping-Dict in `asset_manager.py` erstellen (`ASSET_MAPPINGS`)
6. ⏳ Asset-Manager umbauen (Dict-basiertes Mapping, einheitliche API)
7. ⏳ Asset-Validierung implementieren (`omf2/scripts/validate_assets.py`)
8. ⏳ Pre-Commit Hook hinzufügen
9. ⏳ Code migrieren (alle `heading_icons.get_svg_inline()` → `asset_manager.get_asset_inline()`)
10. ⏳ Tests anpassen und erweitern
11. ⏳ Cleanup (`heading_icons.py` entfernen, Legacy-Verzeichnisse aufräumen)

## Branch-Strategie

**Empfehlung:** Ja, definitiv einen Branch anlegen!
- Branch: `refactor/asset-management-unified`
- Grund: Größere Refactoring-Änderung, mehrere Dateien betroffen
- Vorteil: Saubere Entwicklung, Tests isoliert, einfaches Review

