# Shopfloor Route Calculation

## Overview
- Zentrale Routenberechnung liegt im `FtsRouteService`.
- Das Shopfloor-Layout liefert alle benötigten Daten (`shopfloor_layout.json`: `cells`, `intersection_map`, `modules_by_serial`, `parsed_roads`).
- Darstellung unterscheidet sich je nach Tab (Active Orders vs. FTS), die Berechnung bleibt identisch.

## Datenquellen
- `shopfloor_layout.json`
  - `cells`: Koordinaten, Rollen (module/intersection/fixed), Icons
  - `intersection_map`: Mapping numerischer IDs (`"1"..."4"`) → `cell_id`
  - `modules_by_serial`: Serial → `{ type, cell_id }`
  - `parsed_roads`: bereits aufgelöste Kanten mit `from/to.ref` (z. B. `intersection:1`, `serial:SVR3QA0022`)

## Komponenten
- **FtsRouteService**
  - `initializeLayout(config)`: baut Alias-Mapping, Node-Punkte, nutzt `intersection_map`/`modules_by_serial`.
  - `findRoutePath(start, target)`: BFS über `parsed_roads` (canonical refs: `intersection:<id>`, `serial:<id>`).
  - `buildRoadSegment(road, trimToCenter?)`: berechnet Segment mit/ohne Trimming.
    - `trimToCenter=true`: Route bis Zentrum (FTS-Tab).
    - `trimToCenter=false`: Trim nur, wenn Ziel ein Modul ist (Active Orders).
  - `computeStationaryPosition(nodeId)`: 60 % Richtung Modulzentrum (FTS-Overlay/Position).

- **ShopfloorPreviewComponent** (Active Orders)
  - Nutzt `buildRoadSegment(road)` ohne `trimToCenter` → trimmt nur bei Modul-Ziel.
  - Intersections/Feste: keine Kürzung (bis zum Zentrum).

- **FtsAnimationService / FtsTabComponent** (FTS)
  - Ruft `buildRoadSegment(road, true)` auf → kein Trimming, Route bis Zentrum.
  - Animation/Overlay getrennt vom Trimming.

## Darstellungslogik (Trimming)
- Active Orders: Orange Route endet ~1/3 in der Modul-Zelle (verkürzt von Modulzentrum Richtung Intersection). Intersections bleiben ungetrimmt.
- FTS-Tab: Route durchgehend bis Zentrum (kein Trimming), FTS-Icon überlagert Route.

## Initialisierung & Aliases
- `initializeLayout` MUSS vor Path/Segment-Aufrufen erfolgen.
- Aliases:
  - Intersections: numerisch (`"1"`) und canonical (`"intersection:1"`), plus `cell.id`/`cell.name`.
  - Module: Serial (`serial:<id>`), `cell.id`, `cell.name`, `cell.icon`.
  - Case-insensitive Auflösung.

## Tests/Checks
- Sicherstellen, dass `shopfloor_layout.json` geladen wurde, bevor Routenfunktionen genutzt werden.
- Fixtures: White_step3 deckt Routing/Trimming ab.
- Lint/Typecheck: `nx test ccu-ui`/`nx lint ccu-ui`.

## Referenzen
- `omf3/apps/ccu-ui/src/app/services/fts-route.service.ts`
- `omf3/apps/ccu-ui/src/app/components/shopfloor-preview/shopfloor-preview.component.ts`
- `omf3/apps/ccu-ui/src/app/services/fts-animation.service.ts`
- Layout: `omf3/apps/ccu-ui/public/shopfloor/shopfloor_layout.json`

