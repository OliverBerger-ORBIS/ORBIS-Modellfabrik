# UC-06 Implementation Plan: Interoperability (Event-to-Process)

**Ziel:** Route `dsp/use-case/interoperability` mit statischer SVG-Grafik implementieren

---

## 📋 Übersicht

### Status
- ✅ Use Case bereits im DSP-Tab vorhanden (`DspUseCasesComponent`)
- ✅ SVG-Dateien vorhanden (DE/EN): `uc-06-event-to-process-map-DE.svg`, `uc-06-event-to-process-map-EN.svg`
- ✅ Steps-Definition vorhanden: `uc-06-event-to-process-map.steps.json`
- ✅ Inhalte dokumentiert: `uc-06-interoperability.md`
- ⏳ Neue Route und Komponente müssen erstellt werden

### Referenz
- **Track-Trace Route:** `dsp/use-case/track-trace` → `TrackTraceTabComponent`
- **DSP Use Cases:** `DspUseCasesComponent` (bereits enthält Interoperability)

---

## 🎯 Phase 1: Statische Implementierung (MVP)

### 1.1 Route erstellen
**Datei:** `osf/apps/osf-ui/src/app/app.routes.ts`

```typescript
{
  path: 'dsp/use-case/interoperability',
  loadComponent: () =>
    import('./pages/use-cases/interoperability/interoperability-use-case.component').then(
      (m) => m.InteroperabilityUseCaseComponent
    ),
}
```

**Position:** Nach `dsp/use-case/track-trace` Route (Zeile ~23-26)

---

### 1.2 Komponente erstellen
**Datei:** `osf/apps/osf-ui/src/app/pages/use-cases/interoperability/interoperability-use-case.component.ts`

**Struktur (analog zu TrackTraceTabComponent):**
- Standalone Component
- Imports: `CommonModule`
- Template: Header + SVG-Container
- Service: `EnvironmentService` für Locale (DE/EN)
- SVG-Pfad basierend auf Locale wählen

**Komponenten-Struktur:**
```typescript
@Component({
  selector: 'app-interoperability-use-case',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './interoperability-use-case.component.html',
  styleUrls: ['./interoperability-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InteroperabilityUseCaseComponent implements OnInit {
  // SVG-Pfad basierend auf Locale
  svgPath: string = '';
  
  constructor(private environmentService: EnvironmentService) {}
  
  ngOnInit(): void {
    const locale = this.environmentService.getLocale();
    this.svgPath = locale === 'de' 
      ? 'assets/svg/use-cases/uc-06-event-to-process-map-DE.svg'
      : 'assets/svg/use-cases/uc-06-event-to-process-map-EN.svg';
  }
}
```

---

### 1.3 Template erstellen
**Datei:** `osf/apps/osf-ui/src/app/pages/use-cases/interoperability/interoperability-use-case.component.html`

**Struktur:**
```html
<section class="interoperability-use-case">
  <header class="interoperability-use-case__header">
    <div class="interoperability-use-case__title">
      <img 
        src="assets/svg/dsp/functions/edge-interoperability.svg" 
        alt="Interoperability" 
        class="interoperability-use-case__icon" 
        width="32" 
        height="32" 
      />
      <div>
        <h1 i18n="@@interoperabilityUseCaseHeadline">Interoperability: Event-to-Process Map</h1>
        <p class="interoperability-use-case__subtitle" i18n="@@interoperabilityUseCaseDescription">
          Normalize shopfloor events and enrich them with context to create a shared process view for OT and IT.
        </p>
      </div>
    </div>
  </header>

  <div class="interoperability-use-case__content">
    <div class="interoperability-use-case__diagram">
      <img 
        [src]="svgPath" 
        [alt]="'Interoperability: Event-to-Process Map' | i18n" 
        class="interoperability-use-case__svg"
      />
    </div>
  </div>
</section>
```

**Alternative:** SVG direkt einbinden (statt `<img>`) für bessere Kontrolle:
```html
<div class="interoperability-use-case__diagram" [innerHTML]="svgContent"></div>
```

---

### 1.4 Styles erstellen
**Datei:** `osf/apps/osf-ui/src/app/pages/use-cases/interoperability/interoperability-use-case.component.scss`

**Vorgaben:**
- Konsistent mit `track-trace-tab.component.scss`
- SVG-Container: `max-width: 100%`, responsive
- SVG selbst: `width: 100%`, `height: auto`, `display: block`
- ViewBox der SVG: `0 0 1920 1080` (beibehalten)

**Beispiel:**
```scss
.interoperability-use-case {
  padding: 2rem;
  max-width: 100%;

  &__header {
    margin-bottom: 2rem;
  }

  &__title {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  &__icon {
    flex-shrink: 0;
  }

  &__subtitle {
    margin-top: 0.5rem;
    color: var(--orbis-grey-dark);
  }

  &__content {
    width: 100%;
  }

  &__diagram {
    width: 100%;
    overflow-x: auto;
    background: var(--orbis-white);
    border-radius: 8px;
    padding: 1rem;
  }

  &__svg {
    width: 100%;
    height: auto;
    display: block;
    max-width: 1920px; // Original SVG Breite
  }
}
```

---

### 1.5 SVG-Dateien anpassen und kopieren

**Schritt 1: SVG-Dateien anpassen**
**Quelle:** `docs/assets/use-cases/uc-06/`
- `uc-06-event-to-process-map-DE.svg`
- `uc-06-event-to-process-map-EN.svg`

**Anpassungen:**
1. **Icon-Platzhalter ersetzen:** Alle `<path>`-Elemente in Icon-Platzhaltern durch `<image>`-Elemente ersetzen
2. **Icons einbinden:** Verwendung der Mapping-Tabelle (siehe oben)
3. **ORBIS-CI Farben prüfen:** CSS-Variablen verwenden (bereits vorhanden: `--stroke:#154194`, `--accent:#7fbf7a`)

**Beispiel für Icon-Einbindung:**

**Vorher (Platzhalter):**
```xml
<g id="uc06_lane_business_context_icon" transform="translate(520,318)">
  <rect width="70" height="70" rx="12" ry="12" fill="#ffffff" stroke="#d7dee8" stroke-width="2"/>
  <path class="iconStroke" d="M18 22h34M18 34h34M18 46h24"/>
</g>
```

**Nachher (mit Icon):**
```xml
<g id="uc06_lane_business_context_icon" transform="translate(520,318)">
  <rect width="70" height="70" rx="12" ry="12" fill="#ffffff" stroke="#d7dee8" stroke-width="2"/>
  <image href="assets/svg/business/erp-application.svg" x="10" y="10" width="50" height="50" preserveAspectRatio="xMidYMid meet"/>
</g>
```

**Alle Icon-Platzhalter ersetzen:**

1. **Business-Kontext Icon** (Zeile ~52-55):
   - Ersetze `<path>` durch `<image href="assets/svg/business/erp-application.svg" x="10" y="10" width="50" height="50"/>`

2. **Maschine/Station Icon** (Zeile ~70-73):
   - Ersetze `<path>` durch `<image href="assets/svg/shopfloor/stations/drill-station.svg" x="10" y="10" width="50" height="50"/>`

3. **FTS/AGV Icon** (Zeile ~86-89):
   - Ersetze `<path>` durch `<image href="assets/svg/shopfloor/shared/agv-vehicle.svg" x="10" y="10" width="50" height="50"/>`

4. **Qualität (AIQS) Icon** (Zeile ~102-105):
   - Ersetze `<path>` durch `<image href="assets/svg/shopfloor/stations/aiqs-station.svg" x="10" y="10" width="50" height="50"/>`

5. **Umwelt/Sensorik Icon** (Zeile ~116-119):
   - Ersetze `<path>` durch `<image href="assets/svg/ui/heading-sensors.svg" x="10" y="5" width="50" height="40" preserveAspectRatio="xMidYMid meet"/>`

6. **Target Icons hinzufügen:**
   - **ERP Box** (Zeile ~197-200): Füge `<image href="assets/svg/business/erp-application.svg" x="40" y="20" width="70" height="50" preserveAspectRatio="xMidYMid meet"/>` hinzu
   - **MES Box** (Zeile ~201-204): Füge `<image href="assets/svg/business/mes-application.svg" x="40" y="20" width="70" height="50" preserveAspectRatio="xMidYMid meet"/>` hinzu
   - **Analytics/KI Box** (Zeile ~205-208): Füge `<image href="assets/svg/business/analytics-application.svg" x="50" y="20" width="70" height="50" preserveAspectRatio="xMidYMid meet"/>` hinzu

7. **Process Timeline Icons hinzufügen:**
   - **Station** (Zeile ~187): Füge `<image href="assets/svg/shopfloor/stations/drill-station.svg" x="1390" y="380" width="30" height="30" preserveAspectRatio="xMidYMid meet"/>` hinzu
   - **FTS/AGV** (Zeile ~188): Füge `<image href="assets/svg/shopfloor/shared/agv-vehicle.svg" x="1470" y="380" width="30" height="30" preserveAspectRatio="xMidYMid meet"/>` hinzu
   - **Transfer** (Zeile ~189): Füge `<image href="assets/svg/shopfloor/shared/pick-event.svg" x="1550" y="380" width="30" height="30" preserveAspectRatio="xMidYMid meet"/>` hinzu
   - **Qualität** (Zeile ~190): Füge `<image href="assets/svg/shopfloor/stations/aiqs-station.svg" x="1630" y="380" width="30" height="30" preserveAspectRatio="xMidYMid meet"/>` hinzu
   - **Abschluss** (Zeile ~191): Füge `<image href="assets/svg/shopfloor/shared/order-tracking.svg" x="1710" y="380" width="30" height="30" preserveAspectRatio="xMidYMid meet"/>` hinzu

**Hinweise:**
- Alle `<image>`-Elemente müssen `preserveAspectRatio="xMidYMid meet"` haben
- Icon-Positionen müssen an die bestehenden Layout-Positionen angepasst werden
- Icons sollten zentriert in ihren Containern sein

**Schritt 2: SVG-Dateien kopieren**
**Ziel:** `osf/apps/osf-ui/src/assets/svg/use-cases/`
- `uc-06-event-to-process-map-DE.svg`
- `uc-06-event-to-process-map-EN.svg`

**Hinweis:** 
- SVG-Dateien müssen ORBIS-CI Farben verwenden (bereits korrekt)
- Icons müssen als relative Pfade eingebunden werden (`assets/svg/...`)
- Für Animation später: IDs beibehalten (bereits vorhanden)

---

### 1.6 I18n Keys hinzufügen
**Dateien:**
- `osf/apps/osf-ui/src/locale/messages.de.json`
- `osf/apps/osf-ui/src/locale/messages.en.json`
- `osf/apps/osf-ui/public/locale/messages.de.json`
- `osf/apps/osf-ui/public/locale/messages.en.json`

**Keys:**
```json
{
  "@@interoperabilityUseCaseHeadline": "Interoperabilität: Event-to-Process Map",
  "@@interoperabilityUseCaseDescription": "Shopfloor-Events normalisieren und mit Kontext anreichern – als gemeinsames Prozessbild für OT und IT."
}
```

**EN:**
```json
{
  "@@interoperabilityUseCaseHeadline": "Interoperability: Event-to-Process Map",
  "@@interoperabilityUseCaseDescription": "Normalize shopfloor events and enrich them with context to create a shared process view for OT and IT."
}
```

---

### 1.7 Link im DSP-Tab hinzufügen (optional)
**Datei:** `osf/apps/osf-ui/src/app/pages/dsp/components/dsp-use-cases/dsp-use-cases.component.html`

**Änderung:** Use-Case-Card klickbar machen und zu Route navigieren:
```html
<button
  *ngFor="let useCase of useCases; trackBy: trackById"
  class="use-case-card"
  type="button"
  [class.use-case-card--active]="useCase.id === activeUseCaseId"
  (click)="onUseCaseClick(useCase.id)"
>
```

**Komponente:** `onUseCaseClick()` Methode hinzufügen:
```typescript
onUseCaseClick(id: string): void {
  if (id === 'interoperability') {
    // Navigate to detail route
    this.router.navigate(['/dsp/use-case/interoperability']);
  } else {
    // Toggle detail in current view
    this.setActiveUseCase(id);
  }
}
```

**Hinweis:** Router importieren: `import { Router } from '@angular/router';`

---

## 🎨 Design-Vorgaben

### ORBIS-CI Farben
**Prüfen in SVG:**
- Primary: `#154194` (ORBIS Blue)
- Secondary: `#7fbf7a` (ORBIS Green)
- Neutral: `#7a8aa0` (ORBIS Grey)
- Background: `#ffffff`, `#f6f8fb`

**CSS Variables (falls SVG angepasst werden muss):**
```css
:root {
  --orbis-blue: #154194;
  --orbis-green: #7fbf7a;
  --orbis-grey: #7a8aa0;
  --orbis-white: #ffffff;
  --orbis-panel: #f6f8fb;
}
```

---

### SVG-Größen-Vorgaben
**Original SVG:**
- ViewBox: `0 0 1920 1080`
- Aspect Ratio: 16:9

**Responsive Verhalten:**
- Container: `max-width: 100%`
- SVG: `width: 100%`, `height: auto`
- Min-Breite: ~800px (für Lesbarkeit)
- Scrollbar bei kleineren Bildschirmen

---

### Vorhandene Icons verwenden

**Icon für Header:**
- `assets/svg/dsp/functions/edge-interoperability.svg` (bereits verwendet in Use-Case-Card)

**SVG-Icons innerhalb der Grafik - Mapping:**

| Begriff in SVG | Icon-Key | SVG-Pfad | Verwendung |
|---------------|----------|----------|------------|
| **Business-Kontext (ERP/MES)** | `erp-application` / `mes-application` | `assets/svg/business/erp-application.svg`<br>`assets/svg/business/mes-application.svg` | Icon-Platzhalter in Lane "Business-Kontext" |
| **Maschine / Station** | `device-drill` / `device-mill` / `device-cnc` | `assets/svg/shopfloor/stations/drill-station.svg`<br>`assets/svg/shopfloor/stations/mill-station.svg`<br>`assets/svg/shopfloor/stations/cnc-station.svg` | Icon-Platzhalter in Lane "Maschine/Station" (z.B. Drill oder Mill) |
| **FTS / AGV** | `shopfloor-fts` / `generic-device-agv` | `assets/svg/shopfloor/shared/agv-vehicle.svg` | Icon-Platzhalter in Lane "FTS/AGV" |
| **Qualität (AIQS)** | `device-aiqs` | `assets/svg/shopfloor/stations/aiqs-station.svg` | Icon-Platzhalter in Lane "Qualität (AIQS)" |
| **Umwelt / Sensorik** | `sensor-heading` | `assets/svg/ui/heading-sensors.svg` | Icon-Platzhalter in Lane "Umwelt/Sensorik" |
| **ERP (Target)** | `erp-application` | `assets/svg/business/erp-application.svg` | Icon in Target-Box "ERP" |
| **MES (Target)** | `mes-application` | `assets/svg/business/mes-application.svg` | Icon in Target-Box "MES" |
| **Analytics / KI (Target)** | `bp-analytics` | `assets/svg/business/analytics-application.svg` | Icon in Target-Box "Analytics/KI" |
| **Station (Process View)** | `device-drill` | `assets/svg/shopfloor/stations/drill-station.svg` | Icon in Process Timeline |
| **FTS/AGV (Process View)** | `shopfloor-fts` | `assets/svg/shopfloor/shared/agv-vehicle.svg` | Icon in Process Timeline |
| **Transfer (Process View)** | `pickEvent` / `dropEvent` | `assets/svg/shopfloor/shared/pick-event.svg`<br>`assets/svg/shopfloor/shared/drop-event.svg` | Icon in Process Timeline |
| **Qualität (Process View)** | `device-aiqs` | `assets/svg/shopfloor/stations/aiqs-station.svg` | Icon in Process Timeline |
| **Abschluss (Process View)** | `orderTracking` | `assets/svg/shopfloor/shared/order-tracking.svg` | Icon in Process Timeline |

**Hinweise:**
- Alle Icons sind bereits im `icon-registry.ts` verfügbar
- Icons müssen in der SVG-Datei als `<image>` oder `<use>` eingebunden werden
- Icon-Größe: 70x70px (für Lane-Icons), 40x40px (für Process Timeline Icons)
- Icons sollten ORBIS-CI Farben verwenden (falls SVG-Icons selbst farbig sind, ggf. mit CSS filtern)

---

## 📝 Acceptance Criteria (Phase 1)

- [ ] Route `dsp/use-case/interoperability` funktioniert
- [ ] Komponente zeigt SVG-Grafik (DE/EN basierend auf Locale)
- [ ] SVG ist responsive und scrollbar bei kleineren Bildschirmen
- [ ] Header mit Icon und Beschreibung vorhanden
- [ ] I18n Keys für DE/EN vorhanden
- [ ] Styles konsistent mit anderen Use-Case-Seiten
- [ ] ORBIS-CI Farben korrekt verwendet
- [ ] Link von DSP-Tab Use-Case-Card funktioniert (optional)

---

## 🚀 Phase 2: Animation (später)

### 2.1 Steps-Definition verwenden
**Datei:** `docs/assets/use-cases/uc-06/uc-06-event-to-process-map.steps.json`

**Umsetzung:**
- Ähnlich wie `DspAnimationComponent`
- Step-Controls (Vor/Zurück)
- Highlight/Dim-Logik basierend auf Steps-Definition
- CSS-Klassen für `.hl`, `.dim`, `.hidden`

### 2.2 Komponente erweitern
- Step-State Management
- SVG-Elemente per ID selektieren
- CSS-Klassen dynamisch setzen
- Animation-Controls UI

**Hinweis:** Phase 2 erst nach Phase 1 und Review

---

## 📁 Datei-Struktur

```
osf/apps/osf-ui/src/app/
├── pages/
│   └── use-cases/
│       └── interoperability/
│           ├── interoperability-use-case.component.ts
│           ├── interoperability-use-case.component.html
│           └── interoperability-use-case.component.scss
├── assets/
│   └── svg/
│       └── use-cases/
│           ├── uc-06-event-to-process-map-DE.svg
│           └── uc-06-event-to-process-map-EN.svg
└── app.routes.ts (Route hinzufügen)
```

---

## 🔍 Prüfungen vor Implementierung

1. **SVG-Dateien prüfen:**
   - ORBIS-CI Farben korrekt?
   - ViewBox korrekt (`0 0 1920 1080`)?
   - IDs für Animation vorhanden? (für Phase 2)

2. **Vorhandene Komponenten analysieren:**
   - `TrackTraceTabComponent` als Referenz
   - `DspUseCasesComponent` für Use-Case-Struktur
   - `DspAnimationComponent` für spätere Animation

3. **Routing prüfen:**
   - Route-Pattern konsistent mit `dsp/use-case/track-trace`
   - Locale-Handling korrekt

---

## 📚 Referenzen

- **Use-Case Beschreibung:** `docs/assets/use-cases/uc-06/uc-06-interoperability.md`
- **SVG Steps:** `docs/assets/use-cases/uc-06/uc-06-event-to-process-map.steps.json`
- **Track-Trace Referenz:** `osf/apps/osf-ui/src/app/tabs/track-trace-tab.component.ts`
- **DSP Use Cases:** `osf/apps/osf-ui/src/app/pages/dsp/components/dsp-use-cases/dsp-use-cases.component.ts`

---

*Erstellt: 21.01.2026*
