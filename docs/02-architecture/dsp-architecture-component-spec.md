# DSP Architecture Component - Spezifikation

## Kontext & Zielsetzung

**Ziel:** Erstellen einer neuen animierten SVG-basierten Architektur-Komponente als **Alternative/Ersatz** für die bestehende `DspDetailComponent` (`src/app/components/dsp-detail/`).

**Integration:** Die neue Komponente soll die gleiche Schnittstelle wie `DspDetailComponent` implementieren, damit sie im `ConfigurationTabComponent` als Drop-in-Replacement verwendet werden kann:

- **Input:** `@Input() view!: DspDetailView` (aus `configuration-detail.types.ts`)
- **Output:** `@Output() actionTriggered = new EventEmitter<{ id: string; url: string }>()`
- **Standalone Component:** Ja (wie bestehende Komponente)
- **Asset-Mapping:** Nutzung der bestehenden `DETAIL_ASSET_MAP` aus `detail-asset-map.ts` für Icon-Pfade

**Wichtig:** Die Komponente muss die bestehende `DspDetailView`-Struktur konsumieren können, damit die Integration in `configuration-tab.component.ts` ohne Änderungen an `buildDspDetailView()` funktioniert.

---

## Funktionale Anforderungen – Diagrammstruktur

### 1. Ebenen / Layout

Das Diagramm besteht aus mehreren horizontalen Ebenen:

**a) Titelzeile oben**
- Titel: "DISTRIBUTED SHOP FLOOR PROCESSING (DSP)"
- Untertitel: z.B. "Referenzarchitektur" (i18n-ready über `$localize`)

**b) Linke vertikale Beschriftung neben dem Diagramm:**
- Text: "Business Prozesse" (aus `view.businessProcesses`)

**c) DSP-Ebene in der Mitte:**
- Ein breiter, farbiger Hintergrundbalken für den DSP-Layer.
- In dieser Ebene befinden sich **drei** Hauptboxen (statt zwei):
  - Linke Box: "SmartFactory Dashboard" (entspricht `view.architecture` mit `id: 'ux'`)
  - Mittlere Box: "DSP Edge" (entspricht `view.architecture` mit `id: 'edge'`)
  - Rechte Box: "Management Cockpit" (entspricht `view.architecture` mit `id: 'management'`)
- Zwischen den Boxen Verbindungen mit Pfeilen.

**d) Business-Prozess-Ebene oberhalb des DSP-Layers:**
- Boxen aus `view.businessProcesses` (z.B. "SAP Shopfloor", "Cloud Anwendungen", "Analytische Anwendungen", "Data Lake")
- Die Anzahl der Boxen ist dynamisch basierend auf `view.businessProcesses.length`
- Manche Boxen enthalten ein SVG-Icon (aus `DETAIL_ASSET_MAP`) + Label, andere nur Text

**e) Shopfloor-Ebene ganz unten:**
- Container-Box "Shopfloor Systeme" (aus `view.shopfloorSystems`)
- Zusätzlich mehrere Shopfloor-System-Boxen (aus `view.shopfloorPlatforms`), z.B.:
  - "FT APS"
  - "MES / SCADA"
  - "Lagersystem"
- Die Anzahl ist dynamisch basierend auf `view.shopfloorPlatforms.length` und `view.shopfloorSystems.length`

---

## Container/Box-Modell

### 2. Generisches Container-Modell

Alle visuellen Boxen (Layer, Business-Boxen, DSP-Boxen, UX, Geräte, etc.) als generische Container modellieren.

**Interface-Definition:**

```typescript
interface FunctionIconConfig {
  iconKey: string;  // Key aus DETAIL_ASSET_MAP (z.B. 'DSP_EDGE_DATABASE')
  size: number;    // Seitenlänge in SVG-Koordinaten
}

type LogoPosition = 'top-left' | 'top-right';
type ContainerState = 'normal' | 'highlight' | 'dimmed';

interface ContainerConfig {
  id: string;
  label?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  type: 'layer' | 'box' | 'device' | 'ux' | 'other';

  // Optionales Firmenlogo (z.B. ORBIS, SAP, Azure) in der Ecke
  logoIconKey?: string;        // Key aus DETAIL_ASSET_MAP
  logoPosition?: LogoPosition;  // 'top-left' oder 'top-right'

  // Optionale Funktions-Icons, die groß und zentral dargestellt werden
  functionIcons?: FunctionIconConfig[];

  // Visualisierungszustand für Animation
  state?: ContainerState;
}
```

**Wichtig:** 
- `iconKey` und `logoIconKey` verwenden **KEINE** direkten Dateinamen, sondern Keys aus `DETAIL_ASSET_MAP`
- Die Komponente löst diese Keys über `DETAIL_ASSET_MAP` in konkrete Pfade auf (analog zu `DspDetailComponent`)

**Darstellung im SVG:**
- Pro Container eine `<g>`-Gruppe mit `<rect>` als Rahmen/Hintergrund
- Label (falls vorhanden) mittig oder gut lesbar innerhalb der Box
- Firmenlogo (`logoIconKey`) in der definierten Ecke (top-left oder top-right)
- Funktions-Icons (`functionIcons`) groß und möglichst zentral im Container; bei mehreren Icons z.B. in einer kleinen horizontalen Reihe zentriert

**Mapping von `DspDetailView` zu `ContainerConfig[]`:**
- `view.architecture` → DSP-Layer-Container (3 Boxen: ux, edge, management)
- `view.businessProcesses` → Business-Prozess-Container
- `view.shopfloorPlatforms` → Shopfloor-System-Container
- `view.shopfloorSystems` → Shopfloor-Geräte-Container

---

## Verbindungen (Pfeile)

### 3. Verbindungsmodell

Verbindungen zwischen beliebigen Containern.

**Interface-Definition:**

```typescript
type AnchorSide = 'top' | 'bottom' | 'left' | 'right';
type ConnectionState = 'highlight' | 'dimmed';

interface ConnectionConfig {
  id: string;
  fromId: string;            // Container-ID
  toId: string;              // Container-ID
  fromSide?: AnchorSide;     // optional, Standard: 'bottom'
  toSide?: AnchorSide;       // optional, Standard: 'top'
  state?: ConnectionState;   // 'highlight' = Fokus (z.B. orange), 'dimmed' = grau
}
```

**Ankerpunkte:**
- `top`: Mitte oben
- `bottom`: Mitte unten
- `left`: Mitte links
- `right`: Mitte rechts

### 4. Darstellung der Verbindungen

- Verbindungen als `polyline` in SVG gezeichnet
- Nur horizontale und vertikale Segmente (orthogonale Linien)
- Pfeilspitze am Ende (SVG marker)
- Hilfsfunktion: aus zwei Punkten (fromAnchor, toAnchor) eine Polyline mit 3–5 Punkten erzeugen (einfache "Dogleg"-Route)
- In `<defs>` des SVG einen `marker` für die Pfeilspitze anlegen und bei allen Verbindungen mit `marker-end="url(#arrow-head)"` verwenden

### 5. Verbindungszustände & Farben

- `highlight`: z.B. orange (#ff9900), ggf. etwas dicker
- `dimmed`: grau (#999999)
- Farb- und Linienstärkenwechsel mit CSS-Transition weich animieren

**Standard-Verbindungen (aus `DspDetailView` ableitbar):**
- Business-Prozesse → DSP-Layer (basierend auf `actionId`-Mapping)
- DSP-Layer-Boxen untereinander (ux ↔ edge ↔ management)
- Shopfloor-Systeme → DSP-Layer

---

## Zustände & Highlighting von Boxen

### 6. Container-Zustände

Jeder Container hat einen `state`:
- `normal`
- `highlight` (z.B. farbiger Rand + leicht eingefärbter Hintergrund)
- `dimmed` (grauer Rand, blasser Hintergrund)

**Für `highlight`:**
- Hintergrund leicht einfärben (z.B. hellblau/hellorange) und/oder
- Rahmen farbig und etwas dicker machen

**Darstellung:** Über CSS-Klassen und Transition (fill, stroke, stroke-width), damit der Wechsel beim Einblenden bzw. Fokus weich animiert wird.

---

## Animations-Schritte (wie Folien)

### 7. Schrittweiser Ablauf (Slides)

Abfolge von Animations-Schritten, die dem Verhalten einer animierten PowerPoint-Folie entspricht.

**Mindestens 6 Schritte, z.B.:**

1. Nur Titel/Untertitel, linke Beschriftung ("Business Prozesse") und untere Shopfloor-Ebene mit "Shopfloor Systeme" + Geräte-Icons.
2. DSP-Layer wird eingeblendet (Hintergrund + SmartFactory Dashboard + DSP Edge + Management Cockpit + Verbindungen zwischen diesen drei).
3. Funktions-Icons innerhalb der DSP-Box(en) (z.B. Connectivity, Digital Twin, Data Storage, Analytics, Processes) werden eingeblendet und hervorgehoben.
4. Business-Prozess-Box "SAP Shopfloor" wird eingeblendet, inkl. Verbindungen zu relevanten DSP-Boxen, zunächst als highlight.
5. Weitere Business-Prozess-Boxen werden eingeblendet ("Cloud Anwendungen", "Analytische Anwendungen", "Data Lake" + optional weitere), inklusive Verbindungen zu DSP-Boxen/Management und entsprechendem Highlight.
6. Eine UX-Box (z.B. "SmartFactory Dashboard" mit Monitor-Icon) im DSP-Layer wird eingeblendet, wiederum mit Verbindungen z.B. zur SmartFactory Dashboard-Box.

**Konfiguration:**

```typescript
interface StepConfig {
  id: string;
  label: string;  // i18n-ready
  visibleContainerIds: string[];
  highlightedContainerIds: string[];
  visibleConnectionIds: string[];
  highlightedConnectionIds: string[];
}

const DEFAULT_STEPS: StepConfig[] = [
  // Schritt 1: Titel + Shopfloor
  {
    id: 'step-1',
    label: $localize`:@@dspArchStep1:Shopfloor Overview`,
    visibleContainerIds: ['title', 'shopfloor-systems', 'shopfloor-device-1', 'shopfloor-device-2', ...],
    highlightedContainerIds: [],
    visibleConnectionIds: [],
    highlightedConnectionIds: [],
  },
  // ... weitere Schritte
];
```

**Wichtig:** Die Schritt-Konfiguration sollte aus `DspDetailView` ableitbar sein, damit sie automatisch mit den Daten synchronisiert wird.

### 8. Steuerung

Unterhalb des Diagramms Buttons:
- "Zurück" (i18n: `@@dspArchPrev`)
- "Weiter" (i18n: `@@dspArchNext`)
- "Auto Play" (i18n: `@@dspArchAutoPlay`)

**Funktionalität:**
- "Weiter"/"Zurück": Wechsel zum nächsten/vorherigen Schritt
- "Auto Play": Alle Schritte automatisch mit z.B. 2–3 Sekunden Verzögerung abspielen; am letzten Schritt stoppen

---

## Responsiveness & Zoom

### 9. SVG & Responsiveness

- Das Diagramm in einem `<svg>` mit `viewBox` gezeichnet, damit es sich bei Fenstergrößenänderung proportional skaliert
- Alle Positionen (`x`, `y`, `width`, `height`) arbeiten in einem konsistenten Diagramm-Koordinatensystem (z.B. 0–1200 x 0–700)

### 10. Zoom-Funktion

- Gesamtdiagramm zusätzlich zoom-/skalierbar (unabhängig von der Fenstergröße)
- Umsetzung: Eine Wrapper-Div um das SVG, deren `transform: scale(...)` über einen Zoom-Faktor gesteuert wird
- Rechts oben im Diagramm einfache Controls: "+", "–", "Reset" (i18n-ready)
- Zoom-Logik als Komponenteneigenschaft `zoom` als Zahl implementieren

---

## Icons & Assets

### 11. SVG-Icons

**Wichtig:** Alle Icons über die bestehende `DETAIL_ASSET_MAP` aus `detail-asset-map.ts` verwenden!

- ContainerConfig.functionIcons und logoIconKey greifen über Keys aus `DETAIL_ASSET_MAP` auf Icons zu (z.B. `'DSP_EDGE_DATABASE'`, `'DSP_BUSINESS_SAP'`)
- Die Komponente löst diese Keys über `DETAIL_ASSET_MAP` in konkrete Pfade auf (analog zu `DspDetailComponent.assetPath()`)
- Es reicht, wenn zunächst Platzhalter-SVGs erstellt werden; wichtig ist eine saubere Struktur, so dass wir später echte Firmen- und Funktions-Icons austauschen können

**Icon-Mapping-Beispiel:**

```typescript
// In der Komponente:
import { DETAIL_ASSET_MAP } from '../../assets/detail-asset-map';

private resolveIconPath(iconKey: string): string {
  const path = DETAIL_ASSET_MAP[iconKey as keyof typeof DETAIL_ASSET_MAP];
  return path ? (path.startsWith('/') ? path.slice(1) : path) : '';
}
```

**Konfiguration:**
- Die Listen der Shopfloor-Geräte-Icons, Edge-Funktions-Icons und Business-Prozess-Icons werden aus `DspDetailView` abgeleitet (nicht in separater Config-Datei)
- Für zusätzliche Icons, die nicht in `DspDetailView` enthalten sind, kann eine Erweiterung in `dsp-architecture.config.ts` erfolgen

---

## Struktur & Code-Qualität

### 12. Projektstruktur

**Neue Komponente unter `src/app/components/dsp-architecture/`:**
- `dsp-architecture.component.ts`
- `dsp-architecture.component.html`
- `dsp-architecture.component.scss`
- `dsp-architecture.config.ts` (optional, für zusätzliche Konfiguration)

**Wichtig:**
- Angular Standalone Component (wie `DspDetailComponent`)
- Gleiche Schnittstelle wie `DspDetailComponent`: `@Input() view!: DspDetailView`, `@Output() actionTriggered`
- Nutzung von `ChangeDetectionStrategy.OnPush` (wie bestehende Komponente)

### 13. Konfiguration & Erweiterbarkeit

**In `dsp-architecture.config.ts` (optional):**
- Zusätzliche Konfiguration für:
  - Standard-Verbindungen (falls nicht aus `DspDetailView` ableitbar)
  - Standard-Animation-Schritte (falls nicht aus `DspDetailView` ableitbar)
  - Layout-Parameter (Koordinatensystem, Abstände, etc.)

**TypeScript-Interfaces:**
- `ContainerConfig`, `ConnectionConfig`, `StepConfig` etc. in `dsp-architecture.component.ts` oder separater Types-Datei definieren

### 14. Internationalisierung (i18n)

**Wichtig:** Alle Text-Labels müssen i18n-ready sein!

- Titel, Untertitel, Button-Labels: `$localize` verwenden
- Neue i18n-Keys in `messages.de.json` und `messages.fr.json` hinzufügen:
  - `@@dspArchTitle`: "DISTRIBUTED SHOP FLOOR PROCESSING (DSP)"
  - `@@dspArchSubtitle`: "Referenzarchitektur"
  - `@@dspArchPrev`: "Zurück"
  - `@@dspArchNext`: "Weiter"
  - `@@dspArchAutoPlay`: "Auto Play"
  - `@@dspArchStep1`: "Shopfloor Overview"
  - etc.

### 15. Integration in Configuration Tab

**Austausch der Komponente:**

In `configuration-tab.component.html`:

```html
<!-- Alte Komponente (auskommentiert): -->
<!-- <app-dsp-detail
  [view]="viewModel.dspDetail"
  (actionTriggered)="handleDspAction($event)"
></app-dsp-detail> -->

<!-- Neue Komponente: -->
<app-dsp-architecture
  [view]="viewModel.dspDetail"
  (actionTriggered)="handleDspAction($event)"
></app-dsp-architecture>
```

**Wichtig:** Die `handleDspAction()`-Methode in `configuration-tab.component.ts` bleibt unverändert, da beide Komponenten das gleiche `actionTriggered`-Event emittieren.

---

## Dokumentation

### 16. README / Kommentare

In Kommentaren oder einer kurzen README-Sektion dokumentieren:

- **Wie die Komponente als Ersatz für `DspDetailComponent` verwendet wird:**
  - Einfach `<app-dsp-detail>` durch `<app-dsp-architecture>` in `configuration-tab.component.html` ersetzen
  - Keine Änderungen an `buildDspDetailView()` nötig

- **Wie neue Icons hinzugefügt werden:**
  - Icons als SVG-Dateien unter `public/details/dsp/` oder `public/details/orbis/` ablegen
  - Key in `detail-asset-map.ts` hinzufügen
  - Key in `ContainerConfig.functionIcons` oder `logoIconKey` verwenden

- **Wie die Anzahl der Geräte in der Shopfloor-Ebene erhöht wird:**
  - Automatisch über `view.shopfloorSystems.length` und `view.shopfloorPlatforms.length`
  - Keine manuelle Konfiguration nötig

- **Wie neue Business-Prozess-Boxen ergänzt werden:**
  - Automatisch über `view.businessProcesses` Array
  - In `buildDspDetailView()` in `configuration-tab.component.ts` hinzufügen

- **Wie zusätzliche Animations-Schritte hinzugefügt werden:**
  - `StepConfig[]` in `dsp-architecture.config.ts` erweitern
  - Oder: Automatische Schritt-Generierung aus `DspDetailView`-Struktur

---

## Technische Standards (OMF3)

### 17. Code-Qualität

- **TypeScript:** Strikte Typisierung, keine `any` ohne Begründung
- **ESLint:** Alle Linting-Regeln müssen erfüllt sein
- **RxJS:** Observable Patterns korrekt verwenden (falls nötig)
- **Angular:** Component-basierte Architektur, Services für Business Logic
- **Pre-commit Hooks:** Immer befolgen, nie mit --no-verify überspringen
- **Tests:** Nach jeder Änderung ausführen, MÜSSEN vor Commit bestehen

### 18. Asset-Pfade

- **Absolute Imports für externe Libraries:** `from '@osf/gateway'` ✅
- **Relative Imports für Paket-interne Module:** `from './component'` ✅
- **Asset-Pfade:** Über `DETAIL_ASSET_MAP` (wie bestehende Komponente) ✅

---

## Migration & Rollout

### 19. Phasenweise Einführung

**Phase 1:** Neue Komponente parallel entwickeln
- Neue Komponente unter `src/app/components/dsp-architecture/` erstellen
- Beide Komponenten parallel im Code behalten

**Phase 2:** Testing & Validierung
- Beide Komponenten im Configuration Tab testen (Feature-Flag oder Kommentar)
- Visuelle Validierung gegen PowerPoint-Vorlage

**Phase 3:** Rollout
- `<app-dsp-detail>` durch `<app-dsp-architecture>` ersetzen
- Alte Komponente optional entfernen oder als Fallback behalten

---

## Offene Fragen / Annahmen

- **Screenshots:** Werden Screenshots der PowerPoint-Folie(n) als visuelle Referenz bereitgestellt?
- **Animation-Timing:** Standard-Verzögerung zwischen Schritten (2–3 Sekunden) konfigurierbar?
- **Responsive Breakpoints:** Gibt es spezifische Breakpoints für mobile/tablet/desktop?
- **Accessibility:** Sollen ARIA-Labels und Keyboard-Navigation implementiert werden?

