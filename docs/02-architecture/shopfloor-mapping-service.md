# Shopfloor Mapping Service

## Zweck
- Zentrales Mapping von Serial-ID ↔ Modul-Typ ↔ Cell-ID sowie Intersection-Mapping und Icons.
- Single Source im Frontend für Serial-Auflösung, damit keine doppelten Mappings in Komponenten/Services nötig sind.

## Datenquellen
- `shopfloor_layout.json`
  - `modules_by_serial`: Serial → `{ type, cell_id }`
  - `intersection_map`: `"1"..."4"` → `cell_id`
  - `cells`: Icons, Rollen, Positionsdaten

## API (Auszug)
- `initializeLayout(config)`: MUSS einmalig nach Laden des Layouts aufgerufen werden.
- `getModuleBySerial(serialId)` → `{ moduleType, serialId, cellId?, icon? } | null`
- `getModuleTypeFromSerial(serialId)` / `getCellIdFromSerial(serialId)` / `getCellBySerial(serialId)`
- `getSerialFromModuleType(moduleType)` / `getAllSerialsForModuleType(moduleType)`
- `getCellIdFromIntersection(id)` / `getIntersectionIdFromCell(cellId)`
- `getCellById(cellId)`
- `getModuleIcon(serialId)` / `getModuleIconByType(moduleType)`
- `getAllModules()` → Array aller Module aus Layout/Mapping

## Konsumenten (Stand jetzt)
- **ModuleNameService**: nutzt Mapping statt eigenem Cache.
- **FtsRouteService**: init über Mapping; Module-Aliase/Cell-Refs.
- **ShopfloorPreviewComponent**: init über Mapping (keine eigene Serial→Cell-Map).
- **MessageMonitorTab**: ersetzt hartes MODULE_MAPPING (Icons/Names über Mapping + ModuleNameService).
- **ModuleTab**: Registry dynamisch aus Mapping (statt statischer Liste).
- **ConfigurationTab**: initialisiert Mapping beim Layout-Laden.
- **ModuleDetailsSidebar**: Topic-Filter nutzt bekannte Serials aus Mapping.

## Verwendung / Pattern
1) Layout laden (`shopfloor_layout.json`).
2) `mappingService.initializeLayout(layout)`.
3) Danach alle Serial-/Cell-/Icon-Lookups über Mapping-Service statt eigener Maps.

## Warum zentral?
- Vermeidet Drift zwischen Komponenten (Serial/Typ/Icon/Cell-ID).
- Nutzt das autoritative Layout (`modules_by_serial`, `intersection_map`).
- Ersetzt lokale Registries und hartcodierte Mappings (z. B. Module/Icons im MessageMonitor/Module-Tab).

## Referenzdokument
- Hardware/Serial-Ground-Truth bleibt in `docs/06-integrations/00-REFERENCE/module-serial-mapping.md`.

