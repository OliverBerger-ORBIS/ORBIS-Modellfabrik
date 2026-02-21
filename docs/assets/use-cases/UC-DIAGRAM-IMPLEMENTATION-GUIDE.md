# UC-Diagramm Implementierungs-Guide

**Erstellt:** 21.01.2026  
**Basiert auf:** UC-00 Interoperability Implementierung

---

## 🎯 Übersicht

Dieses Dokument beschreibt das **prinzipielle Vorgehen** für die Implementierung von Use-Case-Diagrammen im OSF-UI. Die Methode wurde bei UC-00 entwickelt und sollte für alle weiteren UC-Diagramme verwendet werden.

---

## 📐 Architektur-Prinzipien

### 1. Hierarchische Struktur

Alle UC-Diagramme folgen einer **dreistufigen Hierarchie**:

```
Columns (Spalten)
  └── Lanes (Bereiche innerhalb einer Spalte)
      └── Chips (Einzelelemente innerhalb einer Lane)
```

**Beispiel UC-00:**
- **Column "Sources"** → enthält mehrere **Lanes** (Business Context, Machine/Station, AGV, Quality, Environment)
- **Lane "Business Context"** → enthält mehrere **Chips** (Production Order, Storage Order, Material, Customer, etc.)
- **Chip "Production Order"** → einzelnes Element mit Text, Icon, Position

### 2. Dynamische SVG-Generierung

**NICHT:** Statische SVG-Dateien laden  
**SONDERN:** SVG zur Laufzeit aus einer Struktur-Konfiguration generieren

**Vorteile:**
- ✅ I18n-Unterstützung (DE/EN/FR) ohne separate SVG-Dateien
- ✅ Einheitliche Layout-Berechnung
- ✅ Wartbare Struktur-Datei
- ✅ Einfache Anpassungen (Farben, Abstände, etc.)

---

## 🏗️ Implementierungs-Struktur

### Datei-Organisation

```
osf/apps/osf-ui/src/app/pages/use-cases/
└── [uc-name]/
    ├── [uc-name]-use-case.component.ts          # Haupt-Komponente
    ├── [uc-name]-use-case.component.html        # Template
    ├── [uc-name]-use-case.component.scss        # Styles
    ├── [uc-name]-structure.config.ts            # Struktur-Definition (Columns → Lanes → Chips)
    ├── [uc-name]-svg-generator.service.ts       # SVG-Generator Service
    └── [uc-name]-i18n.service.ts                # I18n-Loader Service
```

**Beispiel UC-00:**
- `interoperability-use-case.component.ts`
- `uc-00-structure.config.ts`
- `uc-00-svg-generator.service.ts`
- `uc-00-i18n.service.ts`

---

## 📝 Schritt-für-Schritt Implementierung

### Phase 1: Struktur-Definition

**Datei:** `[uc-name]-structure.config.ts`

#### 1.1 Interfaces definieren

```typescript
export interface Uc06Chip {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  textKey: string;              // I18n-Key für Text
  iconPath?: string;            // Optional: Icon-Pfad
  iconX?: number;               // Icon X-Position
  iconY?: number;               // Icon Y-Position
  iconWidth?: number;
  iconHeight?: number;
  multiline?: boolean;           // Mehrzeiliger Text?
  textLines?: string[];          // Array von I18n-Keys für Zeilen
  // Spezielle Eigenschaften:
  statusDots?: Array<{ cx: number; cy: number; color: 'running' | 'idle' | 'fail' }>;
  statusLabels?: string[];       // Labels für Status-Dots
  operationIcons?: Array<{       // Icons für Operation-Chips
    lineIndex: number;
    iconPath: string;
    offsetX: number;            // Relativ zum Text-Ende
    offsetY: number;            // Relativ zur Text-Baseline
    iconWidth: number;
    iconHeight: number;
  }>;
}

export interface Uc06Lane {
  id: string;
  titleKey: string;             // I18n-Key für Lane-Titel
  iconPath: string;
  iconX: number;
  iconY: number;
  iconWidth: number;
  iconHeight: number;
  chips: Uc06Chip[];
  // Berechnet durch Layout-Funktion:
  x?: number;
  y?: number;
  width?: number;
  height?: number;
}

export interface Uc06Column {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  headerX: number;
  headerY: number;
  headerKey: string;            // I18n-Key für Spalten-Header
  lanes?: Uc06Lane[];           // Für Sources-Column
  // Oder andere Strukturen für DSP/Targets-Column
}
```

#### 1.2 Struktur erstellen

```typescript
export function createUc00Structure(): Uc00Structure {
  const structure: Uc00Structure = {
    viewBox: { width: 1920, height: 1300 },
    title: { x: 960, y: 80, key: 'uc00.title' },
    subtitle: { x: 960, y: 140, key: 'uc00.subtitle' },
    columns: {
      sources: {
        id: 'sources',
        x: 80,
        y: 220,
        width: 560,
        height: 950,
        headerX: 120,
        headerY: 270,
        headerKey: 'uc00.sources.header',
        lanes: [
          {
            id: 'business_context',
            titleKey: 'uc00.lane.business_context.title',
            iconPath: '/assets/svg/business/erp-application.svg',
            iconX: 520,
            iconY: 318,
            iconWidth: 70,
            iconHeight: 70,
            chips: [
              { id: 'production_order', x: 160, y: 340, width: 150, height: 50, ... },
              // ... weitere Chips
            ],
          },
          // ... weitere Lanes
        ],
      },
      // ... weitere Columns
    },
  };
  
  // Layout-Berechnung ausführen
  calculateLaneLayout(structure.columns.sources);
  
  return structure;
}
```

#### 1.3 Layout-Berechnung

**Wichtig:** Lanes müssen dynamisch positioniert werden mit gleichmäßigem Spacing.

```typescript
function calculateLaneLayout(column: Uc00Column): void {
  if (!column.lanes || column.lanes.length === 0) return;
  
  const headerHeight = 50;           // Platz für Header
  const columnHeight = column.height;
  const availableHeight = columnHeight - headerHeight;
  
  // Summe aller Lane-Höhen
  const totalLaneHeight = column.lanes.reduce((sum, lane) => {
    return sum + (lane.height || 0);
  }, 0);
  
  // Verfügbarer Platz für Spacing
  const spacingHeight = availableHeight - totalLaneHeight;
  const gapSize = spacingHeight / (column.lanes.length + 1);
  
  // Lanes positionieren
  let currentY = column.y + headerHeight + gapSize;
  column.lanes.forEach((lane, index) => {
    lane.x = column.x + 20;
    lane.y = currentY;
    lane.width = column.width - 40;
    lane.height = lane.height || 150; // Fallback
    
    // Chips relativ zur Lane positionieren
    const offsetY = currentY - baseChipY + 60;
    lane.chips.forEach((chip) => {
      chip.y = chip.y + offsetY;
      // ... weitere Anpassungen
    });
    
    currentY += lane.height + gapSize;
  });
}
```

---

### Phase 2: SVG-Generator Service

**Datei:** `[uc-name]-svg-generator.service.ts`

#### 2.1 Service-Struktur

```typescript
@Injectable({ providedIn: 'root' })
export class Uc06SvgGeneratorService {
  generateSvg(i18nTexts: Record<string, string>): string {
    const structure = createUc06Structure();
    const getText = (key: string): string => i18nTexts[key] || key;
    
    let svg = `<svg ... viewBox="0 0 ${width} ${height}">`;
    svg += this.generateDefs();        // CSS, Filter, Marker
    svg += this.generateColumns(...);  // Columns rendern
    svg += '</svg>';
    return svg;
  }
  
  private generateDefs(): string {
    // CSS-Styles, SVG-Filter, Marker-Definitionen
  }
  
  private generateSourcesColumn(...): string {
    // Sources-Column mit Lanes und Chips
  }
  
  private generateLane(...): string {
    // Lane-Box, Titel, Icon, Chips
  }
  
  private generateChip(...): string {
    // Chip-Box, Text, Icons, Status-Dots, etc.
  }
}
```

#### 2.2 Wichtige Prinzipien

**Asset-Pfade:**
- Verwende `getAssetPath()` aus `detail-asset-map.ts` für korrekte Pfad-Auflösung
- Unterstützt `baseHref` (z.B. für GitHub Pages)

**Icons:**
- Verwende `<image href="...">` Tags innerhalb des SVG
- `preserveAspectRatio="xMidYMid meet"` für korrekte Skalierung
- Icon-Pfade relativ zu `assets/` (ohne führendes `/`)

**Farben:**
- **NICHT:** Direkte Hex-Codes (`#154194`, `#7fbf7a`, etc.)
- **SONDERN:** CSS-Variablen aus ORBIS-CI Palette (`var(--orbis-blue-strong)`)
- In TypeScript: `ORBIS_COLORS.orbisBlue.strong` aus `color-palette.ts`
- Siehe Abschnitt "Design-Richtlinien → Farben" für Details

**Text-Positionierung:**
- `x`, `y` für Text-Baseline
- Für vertikale Zentrierung: `y = containerY + containerHeight/2 + fontSize/3`

**Rounded Corners:**
- Alle Rechtecke: `rx` und `ry` Attribute
- Columns: `rx="18" ry="18"`
- Lanes: `rx="14" ry="14"`
- Chips: `rx="12" ry="12"`

---

### Phase 3: I18n Service

**Datei:** `[uc-name]-i18n.service.ts`

```typescript
@Injectable({ providedIn: 'root' })
export class Uc00I18nService {
  async loadTexts(): Promise<Record<string, string>> {
    const locale = this.languageService.current;
    
    // Lade messages.{locale}.json
    const messages = await this.http.get<Record<string, string>>(...);
    
    // Filtere UC-spezifische Keys (z.B. @@uc00.*)
    const ucTexts: Record<string, string> = {};
    Object.keys(messages).forEach((key) => {
      if (key.startsWith('@@uc00')) {
        ucTexts[key.replace(/^@@/, '')] = messages[key];
      }
    });
    
    return ucTexts;
  }
}
```

**I18n-Keys Struktur:**
- Präfix: `@@uc00.` (für UC-00)
- Struktur: `uc00.[section].[element].[property]`
- Beispiele:
  - `uc00.title`
  - `uc00.sources.header`
  - `uc00.lane.business_context.title`
  - `uc00.chip.production_order`
  - `uc00.chip.start`
  - `uc00.chip.running`

---

### Phase 4: Komponente

**Datei:** `[uc-name]-use-case.component.ts`

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
  svgContent: SafeHtml | null = null;
  isLoading = true;

  constructor(
    private readonly svgGenerator: Uc00SvgGeneratorService,
    private readonly i18nService: Uc00I18nService,
    private readonly sanitizer: DomSanitizer,
    private readonly cdr: ChangeDetectorRef
  ) {}

  async ngOnInit(): Promise<void> {
    await this.loadAndGenerateSvg();
  }

  private async loadAndGenerateSvg(): Promise<void> {
    try {
      this.isLoading = true;
      const texts = await this.i18nService.loadTexts();
      const svgString = this.svgGenerator.generateSvg(texts);
      this.svgContent = this.sanitizer.bypassSecurityTrustHtml(svgString);
      this.isLoading = false;
      this.cdr.markForCheck();
    } catch (error) {
      console.error('Failed to load or generate SVG:', error);
      this.isLoading = false;
      this.cdr.markForCheck();
    }
  }
}
```

**Template:**
```html
<div class="interoperability-use-case">
  <header>
    <h1>{{ title }}</h1>
    <p>{{ subtitle }}</p>
  </header>
  <div class="interoperability-use-case__diagram">
    <div *ngIf="isLoading">Loading...</div>
    <div *ngIf="!isLoading && svgContent" [innerHTML]="svgContent"></div>
  </div>
</div>
```

---

### Phase 5: Routing

**Datei:** `app.routes.ts`

```typescript
{
  path: 'dsp/use-case/interoperability',
  loadComponent: () =>
    import('./pages/use-cases/interoperability/interoperability-use-case.component').then(
      (m) => m.InteroperabilityUseCaseComponent
    ),
}
```

**Settings-Tab Link:**
```typescript
// settings-tab.component.ts
directPages = [
  {
    title: 'Interoperability: Event-to-Process Map',
    route: '/dsp/use-case/interoperability',
  },
];
```

---

## 🎨 Design-Richtlinien

### Farben (ORBIS-CI)

**WICHTIG:** Farben werden über **Namen aus der ORBIS-CI Palette** zugeordnet, **NICHT** als Hex-Codes!

**Zentrale Farbpalette:**
- **TypeScript:** `osf/apps/osf-ui/src/app/assets/color-palette.ts` → `ORBIS_COLORS`
- **SCSS:** `osf/apps/osf-ui/src/app/assets/_color-palette.scss` → CSS-Variablen

**Verwendung in SVG (CSS-Variablen):**
```css
<style>
  :root {
    --stroke: var(--orbis-blue-strong);        /* NICHT: #154194 */
    --muted: var(--orbis-grey-medium);         /* NICHT: #6b7a8f */
    --bg: #ffffff;                              /* White bleibt OK */
    --panel: var(--orbis-grey-light);          /* NICHT: #f8f9fa */
    --accent: var(--highlight-green-medium);    /* NICHT: #7fbf7a */
    --uc-col-dsp-bg: rgba(var(--orbis-blue-strong-rgb), 0.1);
    --uc-col-dsp-border: rgba(var(--orbis-blue-strong-rgb), 0.2);
  }
</style>
```

**Verwendung in TypeScript:**
```typescript
import { ORBIS_COLORS } from '../../../assets/color-palette';

// RICHTIG:
const strokeColor = ORBIS_COLORS.orbisBlue.strong;  // '#154194'
const accentColor = ORBIS_COLORS.highlightGreen.medium;  // '#99cd57'

// FALSCH:
const strokeColor = '#154194';  // ❌ Direkter Hex-Code
```

**Verfügbare ORBIS-CI Farben:**
- `orbis-blue-strong` / `--orbis-blue-strong` → `#154194`
- `orbis-blue-medium` / `--orbis-blue-medium` → `#5071af`
- `orbis-blue-light` / `--orbis-blue-light` → `#8aa0ca`
- `orbis-grey-strong` / `--orbis-grey-strong` → `#a7a8aa`
- `orbis-grey-medium` / `--orbis-grey-medium` → `#bbbcbc`
- `orbis-grey-light` / `--orbis-grey-light` → `#d0d0ce`
- `highlight-green-strong` / `--highlight-green-strong` → `#64a70b`
- `highlight-green-medium` / `--highlight-green-medium` → `#99cd57`
- `highlight-green-light` / `--highlight-green-light` → `#bbde8f`
- `solution-petrol-strong` / `--solution-petrol-strong` → `#009681`
- `status-success-strong` / `--status-success-strong` → `#047857`
- `status-error-strong` / `--status-error-strong` → `#dc2626`
- `status-warning-strong` / `--status-warning-strong` → `#b45309`

**Für Opacity:** Verwende RGB-Variablen:
```css
background: rgba(var(--orbis-blue-strong-rgb), 0.1);
```

**Referenz:** `docs/03-decision-records/14-orbis-ci-usage.md`

### Typografie

- **Title:** `700 56px` Segoe UI, `#0f1e3d`
- **Subtitle:** `400 24px` Segoe UI, `#6b7a8f`
- **H2 (Column Header):** `700 26px` Segoe UI, `#1a2b3c`
- **P (Lane Title):** `400 20px` Segoe UI, `#1a2b3c`
- **Chip Text:** `400 16px` Segoe UI, `#1a2b3c`

### Abstände

- **Column Padding:** 20px
- **Lane Spacing:** Dynamisch berechnet (gleichmäßig verteilt)
- **Chip Padding:** 10px horizontal, 17px vertikal (für erste Zeile)
- **Icon Spacing:** 8-10px vom Text

### Pfeile (DSP-Column)

- **Typ:** Nur Dreiecks-Pfeilspitze (ohne Schaft)
- **Abstand:** 5px oben und unten zu den Lanes
- **Größe:** Nutzt volle verfügbare Höhe zwischen den Abständen
- **Basisbreite:** 1.4x der Höhe

---

## 🔧 Spezielle Features

### Operation-Chip mit Icons

**Struktur:**
```typescript
{
  id: 'operation_chip',
  multiline: true,
  textLines: ['uc00.chip.operation_label', 'uc00.chip.start', 'uc00.chip.stop'],
  operationIcons: [
    { 
      lineIndex: 1,  // Für "Start"
      iconPath: '/assets/svg/shopfloor/shared/driving-status.svg',
      offsetX: 30,   // Abstand rechts vom Text-Ende
      offsetY: -8,   // Vertikaler Offset (negativ = nach oben)
      iconWidth: 16,
      iconHeight: 16
    },
    // ... weitere Icons
  ]
}
```

**Rendering:**
- Text wird Zeile für Zeile gerendert
- Für jede Zeile wird nach passendem `operationIcon` gesucht (`lineIndex`)
- Icon-Position: `textX + textWidth + offsetX` (horizontal), `lineY + offsetY` (vertikal)

### State-Chip mit Status-Dots

**Struktur:**
```typescript
{
  id: 'state_chip',
  textKey: 'uc00.chip.state_label',
  statusDots: [
    { cx: 370, cy: 600, color: 'running' },
    { cx: 370, cy: 625, color: 'idle' },
    { cx: 370, cy: 650, color: 'fail' },
  ],
  statusLabels: ['uc00.chip.running', 'uc00.chip.idle', 'uc00.chip.fail']
}
```

**Rendering:**
- Zeigt nur Überschrift (`textKey`) + Dots mit Labels
- Dots sind eingedrückt (20px zusätzlich)
- Labels sind eingedrückt (30px zusätzlich)

### Badges (Quality-Chip)

**Struktur:**
```typescript
{
  id: 'pass_badge',
  fill: '#e8f5e9',      // Light Green
  stroke: '#4caf50',   // Green
  textKey: 'uc00.chip.pass'
}
```

**Rendering:**
- Spezielle CSS-Klasse: `badgePass` oder `badgeFail`
- Text zentriert, farbig entsprechend

---

## 📊 Unterschiede zur ursprünglichen Planung (UC-00)

### Was sich geändert hat:

1. **Dynamische SVG-Generierung statt statischer Dateien**
   - **Geplant:** Statische SVG-Dateien laden (DE/EN)
   - **Umsetzung:** SVG zur Laufzeit aus Struktur generieren
   - **Grund:** Bessere I18n-Unterstützung, Wartbarkeit

2. **Struktur-Datei statt direkter SVG-Manipulation**
   - **Geplant:** SVG-Dateien manuell anpassen
   - **Umsetzung:** TypeScript-Struktur-Datei mit Layout-Berechnung
   - **Grund:** Einheitliche Positionierung, einfache Anpassungen

3. **I18n-Service statt Environment-Service**
   - **Geplant:** `EnvironmentService` für Locale
   - **Umsetzung:** Eigener `Uc00I18nService` für UC-spezifische Texte
   - **Grund:** Bessere Trennung, Filterung nach UC-Keys

4. **Enhanced-Version für EN**
   - **Neu:** Separate `Uc00SvgGeneratorEnhancedService` für optische Verbesserungen
   - **Grund:** Visuelle Verbesserungen ohne DE-Version zu beeinflussen

5. **Icon-Registry Integration**
   - **Geplant:** Direkte Pfade in SVG
   - **Umsetzung:** Verwendung von `getAssetPath()` für korrekte Pfad-Auflösung
   - **Grund:** Unterstützung für `baseHref` (GitHub Pages)

6. **Relative Icon-Positionierung**
   - **Geplant:** Absolute Positionen
   - **Umsetzung:** Relative Offsets (`offsetX`, `offsetY`) für Operation-Icons
   - **Grund:** Bessere Steuerbarkeit, automatische Anpassung bei Layout-Änderungen

---

## ✅ Checkliste für neue UC-Diagramme

### Vorbereitung
- [ ] Use-Case-Beschreibung vorhanden
- [ ] Konzept-Bild/SVG-Template vorhanden
- [ ] I18n-Texte definiert (DE/EN/FR)

### Implementierung
- [ ] Struktur-Datei erstellt (`[uc-name]-structure.config.ts`)
- [ ] Interfaces definiert (Chip, Lane, Column)
- [ ] Layout-Berechnung implementiert
- [ ] SVG-Generator Service erstellt
- [ ] I18n-Service erstellt
- [ ] Komponente erstellt
- [ ] Route hinzugefügt
- [ ] Settings-Tab Link hinzugefügt

### I18n
- [ ] Keys in `messages.de.json` hinzugefügt
- [ ] Keys in `messages.en.json` hinzugefügt
- [ ] Keys in `messages.fr.json` hinzugefügt (optional)
- [ ] Keys in `public/locale/` kopiert

### Icons
- [ ] Alle benötigten Icons identifiziert
- [ ] Icons in `icon-registry.ts` eingetragen (falls neu)
- [ ] Icon-Pfade korrekt (relativ zu `assets/`)

### Farben (ORBIS-CI)
- [ ] **KEINE direkten Hex-Codes** (`#154194`, `#7fbf7a`, etc.)
- [ ] CSS-Variablen aus ORBIS-CI Palette verwendet (`var(--orbis-blue-strong)`)
- [ ] In TypeScript: `ORBIS_COLORS` aus `color-palette.ts` verwendet
- [ ] Für Opacity: RGB-Variablen verwendet (`rgba(var(--orbis-blue-strong-rgb), 0.1)`)
- [ ] Referenz: `docs/03-decision-records/14-orbis-ci-usage.md`

### Testing
- [ ] Route funktioniert
- [ ] SVG wird korrekt generiert
- [ ] I18n funktioniert (DE/EN)
- [ ] Responsive Verhalten getestet
- [ ] Icons werden korrekt geladen
- [ ] Farben entsprechen ORBIS-CI Vorgaben (über Palette, nicht Hex-Codes)

---

## 🚀 Nächste Schritte (Step-Animation)

### Phase 2: Animation vorbereiten

1. **Steps-Definition verwenden**
   - Datei: `uc-00-event-to-process-map.steps.json`
   - Ähnlich wie `DspAnimationComponent`

2. **Komponente erweitern**
   - Step-State Management
   - SVG-Elemente per ID selektieren
   - CSS-Klassen dynamisch setzen (`.hl`, `.dim`, `.hidden`)
   - Animation-Controls UI

3. **SVG-IDs für Animation**
   - Alle Elemente müssen eindeutige IDs haben
   - Format: `uc00_[type]_[id]` (z.B. `uc00_chip_production_order`)
   - IDs werden in `generateSvg()` gesetzt

---

## 📚 Referenzen

- **UC-00 Implementierung:** `osf/apps/osf-ui/src/app/pages/use-cases/interoperability/`
- **DSP Architecture:** `osf/apps/osf-ui/src/app/components/dsp-architecture/` (für Animation-Referenz)
- **Track-Trace:** `osf/apps/osf-ui/src/app/tabs/track-trace-tab.component.ts` (für Routing-Referenz)
- **Icon Registry:** `osf/apps/osf-ui/src/app/assets/icon-registry.ts`
- **Asset Path Helper:** `osf/apps/osf-ui/src/app/assets/detail-asset-map.ts`

---

*Erstellt: 21.01.2026*  
*Basierend auf UC-00 Interoperability Implementierung*
