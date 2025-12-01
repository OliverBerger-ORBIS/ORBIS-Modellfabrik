# FTS/AGV Integration Plan - Beispiel-App → OMF3

**Datum:** 2025-11-30  
**Status:** Planungsphase  
**Ziel:** Integration der FTS-Analyse-Beispiel-App in OMF3 als zwei neue Tabs

---

## ✅ Anforderung verstanden

### Ziele
1. **FTS/AGV Tab** - FTS-Status-Übersicht mit allen Features aus der Beispiel-App
2. **Track&Trace Tab** - Workpiece-Tracking mit Event-History
3. **UI-Adaptation** - Konsistente OMF3-UI mit OMF3-SVGs
4. **Shopfloor-Integration** - Route & Position im bestehenden Shopfloor-Layout

### Features aus Beispiel-App
- ✅ FTS Status Component (Position, Action States, Driving Status)
- ✅ FTS Battery Component (Voltage, Percentage, Charging)
- ✅ FTS Loads Component (Workpiece Information)
- ✅ FTS Route Component (Route & Position - **ersetzt durch ShopfloorPreview**)
- ✅ Track & Trace Component (Workpiece History, Event Timeline)

---

## 📋 Integrations-Plan

### Phase 1: Vorbereitung & Analyse (2-3 Stunden)

#### 1.1 Komponenten-Mapping
- [ ] Analysiere alle Komponenten aus `examples/fts-analysis-angular/`
- [ ] Identifiziere OMF3-Äquivalente (z.B. `ShopfloorPreviewComponent` statt `FtsRouteComponent`)
- [ ] Liste alle verwendeten SVGs in Beispiel-App auf
- [ ] Mappe SVGs zu OMF3-SVG-Pfaden

#### 1.2 Datenfluss-Analyse
- [ ] Analysiere `FtsMockService` → Ersetze durch `MessageMonitorService`
- [ ] Identifiziere benötigte MQTT-Topics:
  - `fts/v1/ff/{serial}/state`
  - `fts/v1/ff/{serial}/order`
  - `ccu/order/active` (für Order-Kontext)
- [ ] Prüfe ob `@omf3/entities` bereits FTS-Types hat

#### 1.3 SVG-Mapping
- [ ] **Headings:** Mappe Beispiel-App Headings → `headings/*.svg`
- [ ] **Workpieces:** Mappe Beispiel-App Workpieces → `workpieces/*.svg`
- [ ] **Module Icons:** Mappe Beispiel-App Module → `shopfloor/*.svg`
- [ ] **Track & Trace Icons:** Mappe Emojis → OMF3-SVGs

---

### Phase 2: FTS/AGV Tab (4-6 Stunden)

#### 2.1 Tab-Component erstellen
- [ ] Erstelle `omf3/apps/ccu-ui/src/app/tabs/fts-tab.component.ts`
- [ ] Implementiere Tab-Struktur (analog zu `overview-tab.component.ts`)
- [ ] Füge Route in `app.routes.ts` hinzu (`path: 'fts'`)
- [ ] Implementiere `OnInit`, `OnDestroy`, `ChangeDetectionStrategy.OnPush`

#### 2.2 Komponenten migrieren & adaptieren

**FtsStatusComponent → OMF3**
- [ ] Kopiere `fts-status.component.ts` nach `omf3/apps/ccu-ui/src/app/components/fts-status/`
- [ ] Ersetze `FtsMockService` durch `MessageMonitorService`
- [ ] Ersetze `MODULE_NAME_MAP` durch `ModuleNameService.getModuleDisplayText()`
- [ ] Ersetze SVG-Pfade durch OMF3-SVGs
- [ ] Füge i18n hinzu (`$localize`)

**FtsBatteryComponent → OMF3**
- [ ] Kopiere `fts-battery.component.ts` nach `omf3/apps/ccu-ui/src/app/components/fts-battery/`
- [ ] Ersetze `FtsMockService` durch `MessageMonitorService`
- [ ] Ersetze SVG-Pfade durch OMF3-SVGs
- [ ] Füge i18n hinzu

**FtsLoadsComponent → OMF3**
- [ ] Kopiere `fts-loads.component.ts` nach `omf3/apps/ccu-ui/src/app/components/fts-loads/`
- [ ] Ersetze `FtsMockService` durch `MessageMonitorService`
- [ ] Ersetze Workpiece-Icons durch `workpieces/*.svg`
- [ ] Füge i18n hinzu

#### 2.3 Shopfloor-Integration (Route & Position)
- [ ] **NICHT** `FtsRouteComponent` verwenden
- [ ] Nutze `ShopfloorPreviewComponent` im FTS-Tab
- [ ] Berechne FTS-Position aus `lastNodeId` (aus `shopfloor_layout.json`)
- [ ] Passe `ftsPosition` Input an `ShopfloorPreviewComponent` an
- [ ] Zeige Route als Highlighting auf Shopfloor (analog zu Order-Routes)

#### 2.4 Service-Integration
- [ ] Erstelle `FtsDataService` (analog zu anderen State Services)
- [ ] Nutze `MessageMonitorService.getLastMessage('fts/v1/ff/{serial}/state')`
- [ ] Implementiere RxJS Streams mit `shareReplay({ bufferSize: 1, refCount: false })`
- [ ] Nutze `MessageMonitorService` Pattern (analog zu `OrderTabComponent`)

#### 2.5 UI-Anpassung
- [ ] Ersetze alle SVG-Pfade durch OMF3-SVGs:
  - Headings: `headings/robotic.svg` oder `headings/lieferung-bestellen.svg`
  - Module: `shopfloor/*.svg` (bohrer, milling-machine, ai-assistant, robot-arm, stock)
  - Workpieces: `workpieces/{color}_*.svg`
- [ ] Passe SCSS an OMF3-Design-System an
- [ ] Füge i18n-Übersetzungen hinzu (DE, EN, FR)

---

### Phase 3: Track&Trace Tab (4-6 Stunden)

#### 3.1 Tab-Component erstellen
- [ ] Erstelle `omf3/apps/ccu-ui/src/app/tabs/track-trace-tab.component.ts`
- [ ] Implementiere Tab-Struktur
- [ ] Füge Route in `app.routes.ts` hinzu (`path: 'track-trace'`)

#### 3.2 TrackTraceComponent migrieren
- [ ] Kopiere `track-trace.component.ts` nach `omf3/apps/ccu-ui/src/app/components/track-trace/`
- [ ] Ersetze `FtsMockService` durch `MessageMonitorService`
- [ ] Ersetze Emoji-Icons durch OMF3-SVGs:
  - DOCK: `shopfloor/robotic.svg`
  - PICK/DROP: `workpieces/*.svg`
  - TRANSPORT: `shopfloor/robotic.svg`
  - PROCESS: `shopfloor/bohrer.svg` oder `shopfloor/milling-machine.svg`
- [ ] Ersetze `MODULE_NAME_MAP` durch `ModuleNameService`
- [ ] Ersetze Station-Icons durch `shopfloor/*.svg`
- [ ] Füge i18n hinzu

#### 3.3 Workpiece-History-Service
- [ ] Erstelle `WorkpieceHistoryService` (analog zu `InventoryStateService`)
- [ ] Nutze `MessageMonitorService` für Event-Tracking
- [ ] Korreliere Events über Timestamps:
  - `fts/v1/ff/{serial}/state` → DOCK, TRANSPORT
  - `ccu/order/active` → Order-Kontext
  - `module/v1/ff/{serial}/state` → PROCESS-Events
- [ ] Implementiere Event-Grouping (Station-Gruppen)

#### 3.4 UI-Anpassung
- [ ] Ersetze alle Emoji-Icons durch OMF3-SVGs
- [ ] Passe SCSS an OMF3-Design-System an
- [ ] Füge i18n-Übersetzungen hinzu

---

### Phase 4: Types & Entities (1-2 Stunden)

#### 4.1 FTS Types prüfen
- [ ] Prüfe ob `@omf3/entities` bereits `FtsState`, `FtsOrder` Types hat
- [ ] Falls nicht: Erweitere `@omf3/entities` mit FTS-Types aus Beispiel-App
- [ ] Passe Types an OMF3-Konventionen an

#### 4.2 Gateway-Integration (optional)
- [ ] Prüfe ob Gateway bereits FTS-Topics routet
- [ ] Falls nicht: Erweitere Gateway für FTS-Topics

---

### Phase 5: Testing & Integration (2-3 Stunden)

#### 5.1 Unit Tests
- [ ] Erstelle Tests für `FtsTabComponent`
- [ ] Erstelle Tests für `TrackTraceTabComponent`
- [ ] Erstelle Tests für `FtsDataService`
- [ ] Erstelle Tests für `WorkpieceHistoryService`

#### 5.2 Integration Tests
- [ ] Teste mit Mock-Daten (analog zu anderen Tabs)
- [ ] Teste mit echten MQTT-Daten (wenn verfügbar)
- [ ] Teste Shopfloor-Integration

#### 5.3 UI-Tests
- [ ] Teste alle SVG-Icons werden korrekt geladen
- [ ] Teste i18n-Übersetzungen
- [ ] Teste Responsive Design

---

## 🎯 SVG-Mapping (Beispiel-App → OMF3)

### Headings
| Beispiel-App | OMF3 |
|--------------|------|
| (keine expliziten Headings) | `headings/robotic.svg` (FTS Tab) |
| | `headings/lieferung-bestellen.svg` (Track&Trace Tab) |

### Module Icons
| Beispiel-App | OMF3 |
|--------------|------|
| Emoji Icons | `shopfloor/bohrer.svg` (DRILL) |
| | `shopfloor/milling-machine.svg` (MILL) |
| | `shopfloor/ai-assistant.svg` (AIQS) |
| | `shopfloor/robot-arm.svg` (DPS) |
| | `shopfloor/stock.svg` (HBW) |
| | `shopfloor/robotic.svg` (FTS) |
| | `shopfloor/fuel.svg` (CHRG) |
| | `shopfloor/intersection{1-4}.svg` (Intersections) |

### Workpiece Icons
| Beispiel-App | OMF3 |
|--------------|------|
| (vermutlich Emojis) | `workpieces/blue_*.svg` |
| | `workpieces/white_*.svg` |
| | `workpieces/red_*.svg` |
| | `workpieces/slot_empty.svg` |

### Event Icons (Track & Trace)
| Beispiel-App | OMF3 |
|--------------|------|
| 🔗 DOCK | `shopfloor/robotic.svg` |
| 📤 PICK | `workpieces/{color}_instock_unprocessed.svg` |
| 📥 DROP | `workpieces/{color}_product.svg` |
| ↩️ TURN | `shopfloor/robotic.svg` |
| ➡️ PASS | `shopfloor/robotic.svg` |
| 🚗 TRANSPORT | `shopfloor/robotic.svg` |
| ⚙️ PROCESS | `shopfloor/bohrer.svg` oder `shopfloor/milling-machine.svg` |

---

## 📁 Dateistruktur (nach Integration)

```
omf3/apps/ccu-ui/src/app/
├── tabs/
│   ├── fts-tab.component.ts          # NEU: FTS/AGV Tab
│   ├── fts-tab.component.html
│   ├── fts-tab.component.scss
│   ├── track-trace-tab.component.ts   # NEU: Track&Trace Tab
│   ├── track-trace-tab.component.html
│   └── track-trace-tab.component.scss
├── components/
│   ├── fts-status/                   # NEU: Aus Beispiel-App
│   │   ├── fts-status.component.ts
│   │   ├── fts-status.component.html
│   │   └── fts-status.component.scss
│   ├── fts-battery/                  # NEU: Aus Beispiel-App
│   ├── fts-loads/                    # NEU: Aus Beispiel-App
│   └── track-trace/                  # NEU: Aus Beispiel-App
│       ├── track-trace.component.ts
│       ├── track-trace.component.html
│       └── track-trace.component.scss
└── services/
    ├── fts-data.service.ts           # NEU: FTS State Management
    └── workpiece-history.service.ts  # NEU: Track&Trace State Management
```

---

## 🔄 Service-Integration Pattern

### FtsDataService (analog zu InventoryStateService)

```typescript
@Injectable({ providedIn: 'root' })
export class FtsDataService {
  private ftsState$ = new BehaviorSubject<FtsState | null>(null);
  
  constructor(
    private messageMonitor: MessageMonitorService,
    private environmentService: EnvironmentService
  ) {
    // Subscribe to FTS state topic
    this.messageMonitor.getLastMessage<FtsState>('fts/v1/ff/5iO4/state')
      .pipe(
        filter(msg => msg !== null && msg.valid),
        map(msg => msg!.payload as FtsState),
        shareReplay({ bufferSize: 1, refCount: false })
      )
      .subscribe(state => this.ftsState$.next(state));
  }
  
  getFtsState$(): Observable<FtsState | null> {
    return this.ftsState$.asObservable();
  }
}
```

### Tab-Component Pattern (analog zu OrderTabComponent)

```typescript
export class FtsTabComponent implements OnInit, OnDestroy {
  private subscriptions = new Subscription();
  
  ftsState$!: Observable<FtsState | null>;
  batteryState$!: Observable<FtsBatteryState | null>;
  loads$!: Observable<FtsLoadInfo[]>;
  
  constructor(
    private ftsData: FtsDataService,
    private messageMonitor: MessageMonitorService,
    private environmentService: EnvironmentService
  ) {}
  
  ngOnInit(): void {
    // Pattern 2: MessageMonitor + Streams
    this.ftsState$ = this.messageMonitor.getLastMessage<FtsState>('fts/v1/ff/5iO4/state')
      .pipe(
        filter(msg => msg !== null && msg.valid),
        map(msg => msg!.payload as FtsState),
        startWith(null),
        shareReplay({ bufferSize: 1, refCount: false })
      );
  }
}
```

---

## 🎨 UI-Adaptation Checkliste

### SVG-Ersetzung
- [ ] Alle Headings → `headings/*.svg`
- [ ] Alle Module-Icons → `shopfloor/*.svg`
- [ ] Alle Workpiece-Icons → `workpieces/*.svg`
- [ ] Alle Event-Icons → OMF3-SVGs (siehe Mapping-Tabelle)

### Design-System
- [ ] SCSS-Variablen aus OMF3 verwenden
- [ ] Farben aus `_color-palette.scss`
- [ ] Typography aus OMF3-Design-System
- [ ] Spacing/Layout konsistent mit anderen Tabs

### i18n
- [ ] Alle Texte mit `$localize` versehen
- [ ] Übersetzungen für DE, EN, FR hinzufügen
- [ ] Translation Keys konsistent benennen

---

## 🚀 Implementierungs-Reihenfolge

### Schritt 1: FTS Types & Service (Foundation)
1. Prüfe/Erweitere `@omf3/entities` mit FTS-Types
2. Erstelle `FtsDataService`
3. Teste Service mit Mock-Daten

### Schritt 2: FTS Tab (Hauptfunktionalität)
1. Erstelle `FtsTabComponent` (Grundstruktur)
2. Migriere `FtsStatusComponent` → OMF3
3. Migriere `FtsBatteryComponent` → OMF3
4. Migriere `FtsLoadsComponent` → OMF3
5. Integriere `ShopfloorPreviewComponent` für Route & Position
6. Ersetze alle SVGs
7. Füge i18n hinzu

### Schritt 3: Track&Trace Tab
1. Erstelle `WorkpieceHistoryService`
2. Erstelle `TrackTraceTabComponent` (Grundstruktur)
3. Migriere `TrackTraceComponent` → OMF3
4. Ersetze alle SVGs
5. Füge i18n hinzu

### Schritt 4: Testing & Polish
1. Unit Tests
2. Integration Tests
3. UI-Tests
4. Finale Anpassungen

---

## 📊 Geschätzter Aufwand

| Phase | Aufwand | Priorität |
|-------|---------|-----------|
| Phase 1: Vorbereitung | 2-3h | Hoch |
| Phase 2: FTS Tab | 4-6h | Hoch |
| Phase 3: Track&Trace Tab | 4-6h | Hoch |
| Phase 4: Types & Entities | 1-2h | Mittel |
| Phase 5: Testing | 2-3h | Hoch |
| **Gesamt** | **13-20h** | |

---

## ✅ Erfolgs-Kriterien

1. **FTS Tab funktioniert:**
   - Zeigt FTS-Status (Position, Action States, Driving Status)
   - Zeigt Batteriestatus
   - Zeigt Ladungsinformationen
   - Zeigt Route & Position auf Shopfloor-Layout

2. **Track&Trace Tab funktioniert:**
   - Zeigt Workpiece-Liste
   - Zeigt Event-History pro Workpiece
   - Gruppiert Events nach Stationen
   - Zeigt Order-Kontext

3. **UI konsistent:**
   - Alle SVGs aus OMF3-Assets
   - Design konsistent mit anderen Tabs
   - i18n vollständig

4. **Integration funktioniert:**
   - Nutzt `MessageMonitorService` (kein Mock)
   - Nutzt `ShopfloorPreviewComponent` für Route
   - Nutzt `ModuleNameService` für Modul-Namen
   - Folgt OMF3-Patterns (OnPush, RxJS, etc.)

---

## 🔍 Offene Fragen

1. **FTS Serial Number:** Ist `5iO4` fest oder konfigurierbar?
2. **Multiple FTS:** Sollen mehrere FTS gleichzeitig unterstützt werden?
3. **Route-Visualisierung:** Soll Route als Highlighting auf Shopfloor oder als separate Overlay?
4. **Track&Trace Datenquelle:** Reichen MQTT-Topics aus oder benötigen wir Session-Daten?

---

**Nächster Schritt:** Phase 1 starten - Komponenten-Mapping und SVG-Analyse


