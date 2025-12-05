# Shopfloor Layout Refactoring Plan

**Status:** 📋 PLANUNG  
**Datum:** 2025-01-XX  
**Priorität:** HOCH  
**Betroffene Bereiche:** Shopfloor, Routenberechnung, MQTT-Integration

## 🎯 Ziele

### 1. Vereinheitlichung der Intersection-IDs
- **Problem:** In OMF3 werden Intersections als `"INTERSECTION-1"`, `"INTERSECTION-2"` etc. bezeichnet
- **APS/Fischertechnik:** IDs sind `"1"`, `"2"`, `"3"`, `"4"`
- **Konflikt:** IDs werden in MQTT-Payloads verwendet, was zu Verwirrung führt
- **Ziel:** Durchgängige Verwendung der numerischen IDs (`"1"`, `"2"`, `"3"`, `"4"`) in ALLEN Komponenten

### 2. Vereinheitlichung der Routenberechnung
- **Problem:** Unterschiedliche Routenberechnung in Active-Orders-Tab vs. FTS-Tab
  - Active-Orders-Tab: Route wird nicht bis zum Zentrum der Zelle geführt
  - FTS-Tab: Route wird bis zum Zentrum der Module-Cells gezeichnet
- **Ziel:** Einheitliche Routenberechnung, nur Darstellung/Animation unterschiedlich

### 3. Zentrales Mapping-System
- **Ziel:** Zentrales, von allen Komponenten verwendetes Mapping von Serial-ID zu Modul-Name
- **Architektur:** So platzieren, dass es von Entwicklern/Agenten gefunden wird

---

## 📊 Aktuelle Situation - Analyse

### Intersection-ID Verwendung

#### 1. Shopfloor Layout JSON (`shopfloor_layout.json`)
```json
{
  "cells": [
    {
      "id": "CELL_1_1",
      "name": "INTERSECTION-1",  // ❌ Problem: Name ist "INTERSECTION-1"
      "icon": "INTERSECTION-1",   // ❌ Problem: Icon ist "INTERSECTION-1"
      "role": "intersection"
    }
  ],
  "intersection_map": {
    "1": "CELL_1_1",  // ✅ Korrekt: Mapping von "1" zu CELL_1_1
    "2": "CELL_1_2"
  },
  "parsed_roads": [
    {
      "from": { "ref": "intersection:1" },  // ✅ Korrekt: Verwendet "intersection:1"
      "to": { "ref": "intersection:2" }
    }
  ]
}
```

**Erkenntnisse:**
- `intersection_map` verwendet bereits numerische IDs (`"1"`, `"2"`, `"3"`, `"4"`)
- `parsed_roads` verwendet bereits `"intersection:1"` Format
- **Problem:** `cells[].name` und `cells[].icon` verwenden `"INTERSECTION-1"` Format

#### 2. FtsRouteService (`fts-route.service.ts`)
```typescript
// Zeile 82-93: registerIntersectionAliases
const registerIntersectionAliases = (intersectionId: string, cell: ShopfloorCellConfig) => {
  const canonical = `intersection:${intersectionId}`;  // ✅ Korrekt
  [intersectionId, cell.id, cell.name]  // ⚠️ Problem: cell.name ist "INTERSECTION-1"
    .filter((alias): alias is string => Boolean(alias))
    .forEach((alias) => {
      this.aliasToNodeKey.set(alias, canonical);  // ❌ Registriert "INTERSECTION-1" als Alias
    });
};
```

**Erkenntnisse:**
- Service verwendet bereits `intersection:1` Format als canonical
- **Problem:** `cell.name` (`"INTERSECTION-1"`) wird als Alias registriert, was zu Verwirrung führt

#### 3. ShopfloorPreviewComponent (`shopfloor-preview.component.ts`)
```typescript
// Zeile 432-443: registerIntersectionAliases
const registerIntersectionAliases = (intersectionId: string, cell: ShopfloorCellConfig) => {
  const canonical = `intersection:${intersectionId}`;
  [intersectionId, cell.id, cell.name]  // ⚠️ Problem: cell.name ist "INTERSECTION-1"
    .forEach((alias) => {
      this.aliasToNodeKey.set(alias, canonical);
    });
};
```

**Erkenntnisse:**
- Gleiche Problematik wie in FtsRouteService

#### 4. Tests (`fts-route.service.spec.ts`)
```typescript
// Zeile 86-88: Mock Layout
intersection_map: {
  '1': 'cell-int1',  // ✅ Korrekt: Numerische ID
},
// Zeile 70: parsed_roads
to: { ref: 'intersection:1', ... },  // ✅ Korrekt: intersection:1 Format
```

**Erkenntnisse:**
- Tests verwenden bereits korrekte Formate

### Routenberechnung - Unterschiede

#### 1. Active-Orders-Tab (`shopfloor-preview.component.ts`)
```typescript
// Zeile 898-966: computeActiveRoute()
private computeActiveRoute(): { segments: RouteSegment[]; ... } | null {
  // ...
  const path = this.findRoutePath(startRef, targetRef);  // Lokale BFS-Implementierung
  // ...
  for (let i = 0; i < path.length - 1; i += 1) {
    const road = this.findRoadBetween(from, to);
    const segment = this.buildRoadSegment(road);  // Lokale buildRoadSegment()
    // Endpunkte werden aus getrimmten Segmenten genommen
    endpoints.push({ x: segment.x1, y: segment.y1 });  // Getrimmter Startpunkt
    endpoints.push({ x: segment.x2, y: segment.x2 });   // Getrimmter Endpunkt
  }
}
```

**Erkenntnisse:**
- Verwendet **lokale** `findRoutePath()` (BFS in ShopfloorPreviewComponent, Zeile 988)
- Verwendet **lokale** `buildRoadSegment()` (Zeile 733)
- `buildRoadSegment()` verwendet `trimPointTowards()` mit 0.2 insetFraction für Module
- Endpunkte werden aus getrimmten Segmenten genommen
- **Ergebnis:** Route endet nicht am Zentrum der Zelle (getrimmt um 20%)

#### 2. FTS-Tab (`fts-tab.component.ts` + `fts-animation.service.ts`)
```typescript
// fts-tab.component.ts: Zeile 212-214
private findRoutePath(start: string, target: string): string[] | null {
  return this.ftsRouteService.findRoutePath(start, target);  // Delegiert an FtsRouteService
}

// fts-animation.service.ts: Zeile 85, 253
const fullPath = this.ftsRouteService.findRoutePath(from, to);
const segment = this.ftsRouteService.buildRoadSegment(road);  // Verwendet FtsRouteService
```

**Erkenntnisse:**
- Verwendet **FtsRouteService.findRoutePath()** (BFS in FtsRouteService, Zeile 222)
- Verwendet **FtsRouteService.buildRoadSegment()** (Zeile 296)
- `FtsRouteService.buildRoadSegment()` verwendet ebenfalls `trimPointTowards()` mit 0.2 insetFraction
- **ABER:** FTS-Position wird mit `getNodePosition()` berechnet (Zentrum der Zelle, Zeile 214)
- Route-Segmente sind getrimmt, ABER FTS-Position ist am Zentrum
- **Ergebnis:** Route ist getrimmt, ABER FTS-Position wird bis zum Zentrum gezeichnet

#### 3. Unterschiedliche Implementierungen

**Aktuelle Situation:**
- **Active-Orders-Tab:** 
  - Lokale BFS-Implementierung in `ShopfloorPreviewComponent.findRoutePath()` (Zeile 988)
  - Lokale `buildRoadSegment()` Implementierung (Zeile 733)
  - Endpunkte aus getrimmten Segmenten
  
- **FTS-Tab:**
  - Verwendet `FtsRouteService.findRoutePath()` (zentrale BFS-Implementierung, Zeile 222)
  - Verwendet `FtsRouteService.buildRoadSegment()` (zentrale Implementierung, Zeile 296)
  - Route-Segmente getrimmt, ABER FTS-Position am Zentrum

**Erkenntnisse:**
- **Routenberechnung:** Beide verwenden BFS, aber unterschiedliche Implementierungen
- **Segment-Berechnung:** Beide verwenden `buildRoadSegment()` mit `trimPointTowards()`, aber unterschiedliche Implementierungen
- **Darstellung:** 
  - **Active-Orders:** Route getrimmt (20% inset) wenn Target ein Modul ist
  - **FTS-Tab:** Route sollte bis zum Zentrum gehen (getrimmte Darstellung hat NICHT funktioniert)
    - FTS-Icon überlagert/überdeckt die Route (Animation und am Ziel)

**Problem:** 
1. Code-Duplikation - zwei verschiedene Implementierungen für gleiche Funktionalität
2. FTS-Tab verwendet getrimmte Route, soll aber bis zum Zentrum gehen
3. Keine Unterscheidung zwischen Active-Orders (getrimmt bei Modulen) und FTS-Tab (bis zum Zentrum)

### Serial-ID zu Modul-Name Mapping

#### Aktuelle Verwendung
1. **ModuleNameService** (`module-name.service.ts`)
   - Lädt `modules_by_serial` aus `shopfloor_layout.json`
   - Bietet `getModuleTypeFromSerial()` und `getModuleFullName()`

2. **FtsRouteService** (`fts-route.service.ts`)
   - Baut eigenes Mapping: `serialToCellId` Map
   - Verwendet `config.modules_by_serial`

3. **ShopfloorPreviewComponent** (`shopfloor-preview.component.ts`)
   - Baut eigenes Mapping: `serialToCellId` Map
   - Verwendet `config.modules_by_serial`

**Erkenntnisse:**
- Mapping existiert bereits in `shopfloor_layout.json` (`modules_by_serial`)
- Wird in mehreren Komponenten dupliziert
- **Problem:** Keine zentrale, wiederverwendbare Service-Klasse

---

## 🔧 Refactoring-Plan

### Phase 1: Intersection-ID Vereinheitlichung

#### Schritt 1.1: Shopfloor Layout JSON anpassen
**Datei:** `omf3/apps/ccu-ui/public/shopfloor/shopfloor_layout.json`

**Änderungen:**
```json
{
  "cells": [
    {
      "id": "CELL_1_1",
      "name": "1",  // ✅ Änderung: "INTERSECTION-1" → "1"
      "icon": "INTERSECTION-1",  // ⚠️ Icon bleibt "INTERSECTION-1" (für Asset-Lookup)
      "role": "intersection"
    }
  ]
}
```

**Begründung:**
- `name` wird in Alias-Registrierung verwendet → sollte numerische ID sein
- `icon` bleibt `"INTERSECTION-1"` für Asset-Lookup (SVG-Dateien heißen `intersection1.svg`)

#### Schritt 1.2: FtsRouteService anpassen
**Datei:** `omf3/apps/ccu-ui/src/app/services/fts-route.service.ts`

**Änderungen:**
- Zeile 82-93: `registerIntersectionAliases()` - `cell.name` ist jetzt `"1"` statt `"INTERSECTION-1"`
- **Keine Code-Änderungen nötig**, da bereits korrekt implementiert
- **Test:** Alias-Registrierung sollte jetzt `"1"` statt `"INTERSECTION-1"` verwenden

#### Schritt 1.3: ShopfloorPreviewComponent anpassen
**Datei:** `omf3/apps/ccu-ui/src/app/components/shopfloor-preview/shopfloor-preview.component.ts`

**Änderungen:**
- Zeile 432-443: `registerIntersectionAliases()` - `cell.name` ist jetzt `"1"` statt `"INTERSECTION-1"`
- **Keine Code-Änderungen nötig**, da bereits korrekt implementiert

#### Schritt 1.4: Tests anpassen
**Dateien:**
- `omf3/apps/ccu-ui/src/app/services/__tests__/fts-route.service.spec.ts`
- `omf3/apps/ccu-ui/src/app/services/__tests__/fts-animation.service.spec.ts`
- Alle anderen Tests, die Intersection-Namen verwenden

**Änderungen:**
- Mock Layouts: `name: 'Intersection 1'` → `name: '1'`
- Test-Assertions: Prüfen auf `"1"` statt `"INTERSECTION-1"`

#### Schritt 1.5: Asset-Mapping prüfen
**Datei:** `omf3/libs/testing-fixtures/src/index.ts`

**Prüfung:**
- Zeile 484-487: Asset-Mapping verwendet `'INTERSECTION-1'` als Key
- **Keine Änderung nötig**, da `icon` in JSON weiterhin `"INTERSECTION-1"` bleibt

### Phase 2: Routenberechnung Vereinheitlichung (erledigt)

- Active-Orders und FTS nutzen nun den gemeinsamen `FtsRouteService` (keine lokalen Routings mehr).
- `buildRoadSegment(road, trimToCenter)` steuert Darstellung:
  - Active Orders: Trim, wenn Ziel ein Modul ist (Route endet vor dem Zentrum).
  - FTS-Tab: `trimToCenter=true` → Route bis ins Zentrum.
- Dokumentation erstellt: `docs/02-architecture/shopfloor-route-calculation.md`.

### Phase 3: Zentrales Mapping-System

#### Schritt 3.0: Analyse aller Mapping-Stellen

**Gefundene Verwendungen von Module-ID/Serial-Number/Module-Name Mappings:**

1. **ModuleNameService** (`module-name.service.ts`)
   - ✅ Bereits zentral, aber erweitern
   - Verwendet: `modules_by_serial` aus `shopfloor_layout.json`
   - Methoden: `getModuleTypeFromSerial()`, `getModuleFullName()`, `getLocationDisplayText()`

2. **FtsRouteService** (`fts-route.service.ts`)
   - ❌ Baut eigenes Mapping: `serialToCellId` Map (Zeile 62-65)
   - Verwendet: `config.modules_by_serial`
   - **Refactoring:** Verwende `ShopfloorMappingService`

3. **ShopfloorPreviewComponent** (`shopfloor-preview.component.ts`)
   - ❌ Baut eigenes Mapping: `serialToCellId` Map (Zeile 414-417)
   - Verwendet: `config.modules_by_serial`
   - Verwendet: `cell.serial_number` direkt (Zeile 641-643, 658-659)
   - **Refactoring:** Verwende `ShopfloorMappingService`

4. **WorkpieceHistoryService** (`workpiece-history.service.ts`)
   - ⚠️ Verwendet `ModuleNameService`, aber auch eigene Logik
   - Zeile 367: `this.moduleNameService.getModuleTypeFromSerial(serialId)`
   - Zeile 771: `this.moduleNameService.getModuleTypeFromSerial(nodeId)`
   - Zeile 330-352: `extractModuleSerialFromTopic()` - eigene Topic-Parsing-Logik
   - **Refactoring:** Verwende `ShopfloorMappingService` für Serial → Type

5. **MessageMonitorTabComponent** (`message-monitor-tab.component.ts`)
   - ❌ Hardcoded `MODULE_MAPPING` (Zeile 29-36)
   - Verwendet: `MODULE_MAPPING[serial]` für Icon-Lookup
   - Verwendet: `ModuleNameService.getModuleDisplayText()` für Namen
   - **Refactoring:** Ersetze `MODULE_MAPPING` durch `ShopfloorMappingService`

6. **ConfigurationTabComponent** (`configuration-tab.component.ts`)
   - ⚠️ Verwendet `cell.serial_number` direkt (Zeile 411-414, 477-479, 847-848)
   - Verwendet: `ModuleNameService` für Display-Namen
   - **Refactoring:** Verwende `ShopfloorMappingService` für Serial → Type/Cell-ID

7. **ModuleTabComponent** (`module-tab.component.ts`)
   - ⚠️ Verwendet `cell.serial_number` direkt (Zeile 689-690)
   - **Refactoring:** Verwende `ShopfloorMappingService`

8. **ModuleDetailsSidebarComponent** (`module-details-sidebar.component.ts`)
   - ⚠️ Verwendet `serialNumber` direkt (Zeile 118: `m.serialNumber === this.serialId`)
   - **Refactoring:** Verwende `ShopfloorMappingService` für Serial → Type

9. **OrderCardComponent** (`order-card.component.ts`)
   - ✅ Verwendet `ModuleNameService.getModuleFullName()` (Zeile 351, 354)
   - **Keine Änderung nötig** (verwendet bereits zentrale Service)

10. **ProcessTabComponent** (`process-tab.component.ts`)
    - ✅ Verwendet `ModuleNameService.getModuleFullName()` (Zeile 112)
    - **Keine Änderung nötig** (verwendet bereits zentrale Service)

11. **DspArchitectureComponent** (`dsp-architecture.component.ts`)
    - ✅ Verwendet `ModuleNameService.getModuleFullName()` (Zeile 149)
    - **Keine Änderung nötig** (verwendet bereits zentrale Service)

12. **TrackTraceComponent** (`track-trace.component.ts`)
    - ✅ Verwendet `ModuleNameService` (Zeile 29)
    - **Keine Änderung nötig** (verwendet bereits zentrale Service)

13. **Business Library** (`libs/business/src/index.ts`)
    - ⚠️ Verwendet `serialNumber` in Commands (Zeile 223-253, 466-515)
    - **Keine Änderung nötig** (Commands verwenden Serial-ID direkt, kein Mapping nötig)

14. **Gateway Library** (`libs/gateway/src/index.ts`)
    - ⚠️ Extrahiert `serialNumber` aus Topics (Zeile 182-189)
    - **Keine Änderung nötig** (Topic-Parsing, kein Mapping nötig)

**Zusammenfassung:**
- **Zu refactoren:** FtsRouteService, ShopfloorPreviewComponent, MessageMonitorTabComponent, WorkpieceHistoryService, ConfigurationTabComponent, ModuleTabComponent, ModuleDetailsSidebarComponent
- **Bereits korrekt:** OrderCardComponent, ProcessTabComponent, DspArchitectureComponent, TrackTraceComponent
- **Keine Änderung:** Business Library, Gateway Library (verwenden Serial-ID direkt)

#### Schritt 3.1: ShopfloorMappingService erstellen
**Datei:** `omf3/apps/ccu-ui/src/app/services/shopfloor-mapping.service.ts` (neu)

**Zweck:**
- Zentrale Service-Klasse für alle Shopfloor-Mappings
- Serial-ID → Modul-Name/Type/Cell-ID
- Intersection-ID → Cell-ID
- Module-Type → Serial-ID (Reverse-Lookup)
- Icon-Mapping für Module
- Wiederverwendbar für alle Komponenten

**Interface:**
```typescript
@Injectable({ providedIn: 'root' })
export class ShopfloorMappingService {
  // Serial-ID → Modul-Info
  getModuleBySerial(serialId: string): SerialToModuleInfo | null;
  getModuleTypeFromSerial(serialId: string): string | null;
  getCellIdFromSerial(serialId: string): string | null;
  
  // Module-Type → Serial-ID (Reverse-Lookup)
  getSerialFromModuleType(moduleType: string): string | null;
  getAllSerialsForModuleType(moduleType: string): string[];
  
  // Intersection-ID → Cell-ID
  getCellIdFromIntersection(intersectionId: string): string | null;
  getIntersectionIdFromCell(cellId: string): string | null;
  
  // Cell-ID → Cell-Config
  getCellById(cellId: string): ShopfloorCellConfig | null;
  getCellBySerial(serialId: string): ShopfloorCellConfig | null;
  
  // Icon-Mapping
  getModuleIcon(serialId: string): string | null;
  getModuleIconByType(moduleType: string): string | null;
  
  // Initialization
  initializeLayout(config: ShopfloorLayoutConfig): void;
  isInitialized(): boolean;
}
```

**Icon-Mapping:**
- Lädt Icons aus `shopfloor_layout.json` oder verwendet Standard-Mapping
- Ersetzt hardcoded `MODULE_MAPPING` in `MessageMonitorTabComponent`

#### Schritt 3.2: ModuleNameService refactoren
**Datei:** `omf3/apps/ccu-ui/src/app/services/module-name.service.ts`

**Änderungen:**
- Verwendet `ShopfloorMappingService` intern
- Behält öffentliche API für Rückwärtskompatibilität
- Delegiert an `ShopfloorMappingService`
- **Zeile 29-34:** Entferne eigenes `serialToModuleCache`, verwende `ShopfloorMappingService`

#### Schritt 3.3: FtsRouteService refactoren
**Datei:** `omf3/apps/ccu-ui/src/app/services/fts-route.service.ts`

**Änderungen:**
- Verwendet `ShopfloorMappingService` für Serial-ID → Cell-ID Mapping
- **Zeile 62-65:** Entferne dupliziertes `serialToCellId` Mapping
- **Zeile 106-111:** Verwende `ShopfloorMappingService.getCellIdFromSerial()` statt eigenes Mapping
- Delegiert an `ShopfloorMappingService`

#### Schritt 3.4: ShopfloorPreviewComponent refactoren
**Datei:** `omf3/apps/ccu-ui/src/app/components/shopfloor-preview/shopfloor-preview.component.ts`

**Änderungen:**
- Verwendet `ShopfloorMappingService` für Serial-ID → Cell-ID Mapping
- **Zeile 414-417:** Entferne dupliziertes `serialToCellId` Mapping
- **Zeile 641-643, 658-659:** Verwende `ShopfloorMappingService` statt `cell.serial_number` direkt
- Delegiert an `ShopfloorMappingService`

#### Schritt 3.5: MessageMonitorTabComponent refactoren
**Datei:** `omf3/apps/ccu-ui/src/app/tabs/message-monitor-tab.component.ts`

**Änderungen:**
- **Zeile 29-36:** Entferne hardcoded `MODULE_MAPPING`
- **Zeile 296, 354-355, 367-368:** Verwende `ShopfloorMappingService.getModuleIcon()` statt `MODULE_MAPPING[serial]`
- Verwende `ShopfloorMappingService.getModuleTypeFromSerial()` für Type-Lookup

#### Schritt 3.6: WorkpieceHistoryService refactoren
**Datei:** `omf3/apps/ccu-ui/src/app/services/workpiece-history.service.ts`

**Änderungen:**
- **Zeile 367, 771:** Bereits verwendet `ModuleNameService.getModuleTypeFromSerial()`
- **Keine Änderung nötig** (verwendet bereits zentrale Service über ModuleNameService)
- Optional: Direkt `ShopfloorMappingService` verwenden für bessere Performance

#### Schritt 3.7: ConfigurationTabComponent refactoren
**Datei:** `omf3/apps/ccu-ui/src/app/tabs/configuration-tab.component.ts`

**Änderungen:**
- **Zeile 411-414, 477-479, 847-848:** Verwende `ShopfloorMappingService` statt `cell.serial_number` direkt
- Verwende `ShopfloorMappingService.getCellBySerial()` für Cell-Lookup

#### Schritt 3.8: ModuleTabComponent refactoren
**Datei:** `omf3/apps/ccu-ui/src/app/tabs/module-tab.component.ts`

**Änderungen:**
- **Zeile 689-690:** Verwende `ShopfloorMappingService.getCellBySerial()` statt `cell.serial_number` direkt

#### Schritt 3.9: ModuleDetailsSidebarComponent refactoren
**Datei:** `omf3/apps/ccu-ui/src/app/components/module-details-sidebar/module-details-sidebar.component.ts`

**Änderungen:**
- **Zeile 118:** Verwende `ShopfloorMappingService.getModuleTypeFromSerial()` für Type-Lookup
- Optional: Verwende `ShopfloorMappingService.getCellBySerial()` für Cell-Lookup

#### Schritt 3.5: Architektur-Dokumentation
**Datei:** `docs/02-architecture/shopfloor-mapping-service.md` (neu)

**Inhalt:**
- Beschreibung des `ShopfloorMappingService`
- Verwendung in verschiedenen Komponenten
- Best Practices für zukünftige Entwickler

**Aktualisierung:**
- `docs/02-architecture/project-structure.md` - ShopfloorMappingService hinzufügen

---

## 📋 Implementierungs-Checkliste

### Phase 1: Intersection-ID Vereinheitlichung
- [ ] `shopfloor_layout.json`: `name` von `"INTERSECTION-1"` → `"1"` ändern (alle 4 Intersections)
- [ ] Tests: Mock Layouts anpassen (`name: '1'` statt `'INTERSECTION-1'`)
- [ ] Tests: Assertions anpassen (prüfen auf `"1"` statt `"INTERSECTION-1"`)
- [ ] Tests ausführen: `nx test ccu-ui`
- [ ] Manuelle Prüfung: Shopfloor-Darstellung prüfen
- [ ] Manuelle Prüfung: Routenberechnung prüfen (Active-Orders-Tab, FTS-Tab)

### Phase 2: Routenberechnung Vereinheitlichung
- [ ] `FtsRouteService` in `ShopfloorPreviewComponent` injizieren
- [ ] Lokale `findRoutePath()` entfernen, delegiert an `FtsRouteService`
- [ ] Lokale `buildRoadSegment()` entfernen, delegiert an `FtsRouteService`
- [ ] Lokale `findRoadBetween()` entfernen, delegiert an `FtsRouteService`
- [ ] `indexLayout()` anpassen: `FtsRouteService.initializeLayout()` aufrufen
- [ ] Lokale Maps entfernen (`nodePoints`, `aliasToNodeKey`, etc.)
- [ ] `resolveNodeRef()` anpassen: delegiert an `FtsRouteService`
- [ ] **`FtsRouteService.buildRoadSegment()` erweitern:**
  - [ ] Parameter `trimToCenter: boolean` hinzufügen
  - [ ] Logik: Wenn `trimToCenter = true` → Route bis zum Zentrum (kein Trimming)
  - [ ] Logik: Wenn `trimToCenter = false` → Route getrimmt nur wenn Target ein Modul ist
- [ ] **`FtsAnimationService` anpassen:**
  - [ ] `buildRoadSegment(road, true)` aufrufen (FTS-Tab: bis zum Zentrum)
- [ ] **`ShopfloorPreviewComponent.computeActiveRoute()` anpassen:**
  - [ ] Prüfe ob Target ein Modul ist
  - [ ] `buildRoadSegment(road, false)` aufrufen (Active-Orders: getrimmt wenn Modul)
- [ ] Tests: Routenberechnung in beiden Tabs prüfen
- [ ] Manuelle Prüfung: FTS-Tab Route bis zum Zentrum
- [ ] Manuelle Prüfung: Active-Orders-Tab Route getrimmt bei Modulen
- [ ] Dokumentation erstellen: `docs/02-architecture/shopfloor-route-calculation.md`

### Phase 3: Zentrales Mapping-System
- [ ] **Schritt 3.1:** `ShopfloorMappingService` erstellen
  - [ ] Interface definieren (Serial-ID → Type/Cell-ID, Intersection-ID → Cell-ID, Icon-Mapping)
  - [ ] Implementierung mit `modules_by_serial` und `intersection_map`
  - [ ] Icon-Mapping implementieren (ersetzt `MODULE_MAPPING`)
- [ ] **Schritt 3.2:** `ModuleNameService` refactoren
  - [ ] Entferne eigenes `serialToModuleCache`
  - [ ] Verwende `ShopfloorMappingService` intern
  - [ ] Behalte öffentliche API für Rückwärtskompatibilität
- [ ] **Schritt 3.3:** `FtsRouteService` refactoren
  - [ ] Entferne dupliziertes `serialToCellId` Mapping (Zeile 62-65)
  - [ ] Verwende `ShopfloorMappingService.getCellIdFromSerial()`
- [ ] **Schritt 3.4:** `ShopfloorPreviewComponent` refactoren
  - [ ] Entferne dupliziertes `serialToCellId` Mapping (Zeile 414-417)
  - [ ] Verwende `ShopfloorMappingService` statt `cell.serial_number` direkt
- [ ] **Schritt 3.5:** `MessageMonitorTabComponent` refactoren
  - [ ] Entferne hardcoded `MODULE_MAPPING` (Zeile 29-36)
  - [ ] Verwende `ShopfloorMappingService.getModuleIcon()` und `getModuleTypeFromSerial()`
- [ ] **Schritt 3.6:** `WorkpieceHistoryService` prüfen
  - [ ] Bereits verwendet `ModuleNameService` → Keine Änderung nötig
  - [ ] Optional: Direkt `ShopfloorMappingService` verwenden
- [ ] **Schritt 3.7:** `ConfigurationTabComponent` refactoren
  - [ ] Verwende `ShopfloorMappingService` statt `cell.serial_number` direkt
- [ ] **Schritt 3.8:** `ModuleTabComponent` refactoren
  - [ ] Verwende `ShopfloorMappingService.getCellBySerial()`
- [ ] **Schritt 3.9:** `ModuleDetailsSidebarComponent` refactoren
  - [ ] Verwende `ShopfloorMappingService.getModuleTypeFromSerial()`
- [ ] Tests: Alle Tests anpassen
- [ ] Tests ausführen: `nx test ccu-ui`
- [ ] Dokumentation erstellen: `docs/02-architecture/shopfloor-mapping-service.md`
- [ ] `docs/02-architecture/project-structure.md` aktualisieren

---

## 🧪 Test-Strategie

### Unit Tests
- **FtsRouteService:** Intersection-ID Resolution prüfen
- **ShopfloorMappingService:** Alle Mapping-Methoden testen
- **ShopfloorPreviewComponent:** Alias-Registrierung prüfen

### Integration Tests
- **Active-Orders-Tab:** Route-Berechnung prüfen
- **FTS-Tab:** Route-Berechnung prüfen
- **MQTT-Integration:** Intersection-IDs in Payloads prüfen

### Manuelle Tests
- Shopfloor-Darstellung: Intersections korrekt dargestellt?
- Routenberechnung: Funktioniert in beiden Tabs?
- MQTT-Payloads: Intersection-IDs korrekt?

---

## 📝 Risiken und Mitigation

### Risiko 1: Breaking Changes in MQTT-Payloads
**Risiko:** APS sendet `"1"`, OMF3 erwartet `"INTERSECTION-1"`  
**Mitigation:** 
- Prüfen: Welche Komponenten lesen Intersection-IDs aus MQTT-Payloads?
- Alias-System beibehalten: `"INTERSECTION-1"` → `"intersection:1"` (Rückwärtskompatibilität)

### Risiko 2: Asset-Lookup bricht
**Risiko:** SVG-Assets heißen `intersection1.svg`, aber `icon` ist jetzt `"1"`  
**Mitigation:**
- `icon` in JSON bleibt `"INTERSECTION-1"` (nur `name` ändert sich)
- Asset-Mapping prüfen: Funktioniert weiterhin?

### Risiko 3: Tests brechen
**Risiko:** Viele Tests verwenden `"INTERSECTION-1"`  
**Mitigation:**
- Systematisch alle Tests durchgehen
- Mock Layouts anpassen
- Assertions anpassen

---

## 🎯 Erfolgskriterien

### Phase 1: Intersection-ID Vereinheitlichung
- ✅ Alle Intersections verwenden numerische IDs (`"1"`, `"2"`, `"3"`, `"4"`)
- ✅ Keine Verwendung von `"INTERSECTION-1"` Format mehr (außer `icon` für Asset-Lookup)
- ✅ Alle Tests bestehen
- ✅ Shopfloor-Darstellung funktioniert korrekt
- ✅ Routenberechnung funktioniert korrekt

### Phase 2: Routenberechnung Vereinheitlichung
- ✅ Routenberechnung ist dokumentiert
- ✅ Unterschiede zwischen Tabs sind klar beschrieben
- ✅ Entscheidung getroffen: Option A, B oder C

### Phase 3: Zentrales Mapping-System
- ✅ `ShopfloorMappingService` existiert und wird verwendet
- ✅ Keine duplizierten Mappings mehr
- ✅ Alle Komponenten verwenden `ShopfloorMappingService`
- ✅ Dokumentation existiert
- ✅ Alle Tests bestehen

---

## 📚 Referenzen

- `omf3/apps/ccu-ui/public/shopfloor/shopfloor_layout.json` - Shopfloor Layout Definition
- `omf3/apps/ccu-ui/src/app/services/fts-route.service.ts` - Routenberechnung Service
- `omf3/apps/ccu-ui/src/app/components/shopfloor-preview/shopfloor-preview.component.ts` - Shopfloor Preview Component
- `omf3/apps/ccu-ui/src/app/services/module-name.service.ts` - Modul-Name Service
- `docs/02-architecture/project-structure.md` - Projekt-Struktur Dokumentation

---

## 🔄 Nächste Schritte

1. **User-Freigabe:** Plan prüfen und freigeben
2. **Phase 1 starten:** Intersection-ID Vereinheitlichung
3. **Phase 2 starten:** Routenberechnung Dokumentation
4. **Phase 3 starten:** Zentrales Mapping-System
5. **Abschluss:** Tests, Dokumentation, Code-Review

