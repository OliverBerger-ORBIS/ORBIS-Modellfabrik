# UC-01 Track & Trace Genealogy - Farben & Routing Vorschlag

**Erstellt:** 29.01.2026

---

## 🎨 Farben aus track-trace (Live-Demo)

### Identifizierte Farben:

1. **Pick Events:**
   - Border: `#9c27b0` (Lila/Purple)
   - Background: `rgba(156, 39, 176, 0.05)`

2. **Process Events:**
   - Border: `var(--shopfloor-highlight-strong)` (Orange)
   - Background: `rgba(249, 115, 22, 0.08)`

3. **Drop Events:**
   - Border: `#4caf50` (Grün)
   - Background: `rgba(76, 175, 80, 0.05)`

4. **Storage Order:**
   - Border: `#9c27b0` (Lila/Purple)
   - Background: `rgba(156, 39, 176, 0.05)`

5. **Production Order:**
   - Border: `#4caf50` (Grün)
   - Background: `rgba(76, 175, 80, 0.05)`

6. **Timeline Markers:**
   - Dock: `#4caf50` (Grün)
   - Turn: `var(--shopfloor-highlight-strong)` (Orange)
   - Pass: `var(--orbis-blue-medium)` (Blau)
   - Pick: `#9c27b0` (Lila)
   - Drop: `#e91e63` (Pink)

---

## 📐 Zentrale Farbdefinitionen (Vorschlag)

### Option A: CSS-Variablen in `_color-palette.scss`

```scss
// Track & Trace Event Colors
--track-trace-pick: #9c27b0;
--track-trace-pick-rgb: 156, 39, 176;
--track-trace-pick-bg: rgba(156, 39, 176, 0.05);

--track-trace-process: var(--shopfloor-highlight-strong);
--track-trace-process-bg: rgba(249, 115, 22, 0.08);

--track-trace-drop: #4caf50;
--track-trace-drop-rgb: 76, 175, 80;
--track-trace-drop-bg: rgba(76, 175, 80, 0.05);

--track-trace-storage-order: #9c27b0;
--track-trace-storage-order-rgb: 156, 39, 176;
--track-trace-storage-order-bg: rgba(156, 39, 176, 0.05);

--track-trace-production-order: #4caf50;
--track-trace-production-order-rgb: 76, 175, 80;
--track-trace-production-order-bg: rgba(76, 175, 80, 0.05);

--track-trace-timeline-dock: #4caf50;
--track-trace-timeline-turn: var(--shopfloor-highlight-strong);
--track-trace-timeline-pass: var(--orbis-blue-medium);
--track-trace-timeline-pick: #9c27b0;
--track-trace-timeline-drop: #e91e63;
```

### Option B: TypeScript-Konstanten in `color-palette.ts`

```typescript
export const TRACK_TRACE_COLORS = {
  pick: {
    main: '#9c27b0',
    rgb: [156, 39, 176] as const,
    background: 'rgba(156, 39, 176, 0.05)',
  },
  process: {
    main: SHOPFLOOR_HIGHLIGHT.strong, // aus bestehender Palette
    background: 'rgba(249, 115, 22, 0.08)',
  },
  drop: {
    main: '#4caf50',
    rgb: [76, 175, 80] as const,
    background: 'rgba(76, 175, 80, 0.05)',
  },
  storageOrder: {
    main: '#9c27b0',
    rgb: [156, 39, 176] as const,
    background: 'rgba(156, 39, 176, 0.05)',
  },
  productionOrder: {
    main: '#4caf50',
    rgb: [76, 175, 80] as const,
    background: 'rgba(76, 175, 80, 0.05)',
  },
  timeline: {
    dock: '#4caf50',
    turn: SHOPFLOOR_HIGHLIGHT.strong,
    pass: ORBIS_BLUE.medium,
    pick: '#9c27b0',
    drop: '#e91e63',
  },
} as const;
```

**Empfehlung:** Option A (CSS-Variablen) + Option B (TypeScript-Konstanten)
- CSS-Variablen für SCSS-Styles
- TypeScript-Konstanten für SVG-Generierung

---

## 🛣️ Routing-Strategie (Vorschlag)

### Problem:
- `dsp/use-case/track-trace` → Live-Demo (`TrackTraceTabComponent`)
- Neue Schema-Diagramm soll nicht die Live-Demo überschreiben

### Lösung: Separate Route für Schema

**Option 1: Neue Route `track-trace-genealogy` (EMPFOHLEN)**

```
dsp/use-case/track-trace              → Live-Demo (TrackTraceTabComponent)
dsp/use-case/track-trace-genealogy    → Schema-Diagramm (TrackTraceGenealogyUseCaseComponent)
```

**Vorteile:**
- ✅ Klare Trennung
- ✅ Beide Versionen verfügbar
- ✅ Keine Breaking Changes

**Nachteile:**
- ⚠️ Zwei separate Einträge im DSP-Tab nötig (oder Toggle)

---

**Option 2: Toggle in Live-Demo**

```
dsp/use-case/track-trace → Live-Demo mit Toggle "Schema-Ansicht" / "Live-Ansicht"
```

**Vorteile:**
- ✅ Ein Eintrag im DSP-Tab
- ✅ Einheitliche Navigation

**Nachteile:**
- ⚠️ Komplexere Komponente
- ⚠️ Live-Demo wird erweitert

---

**Option 3: Zwei Einträge im DSP-Tab**

Im `DspUseCasesComponent`:
- "Track & Trace (Live)" → `track-trace`
- "Track & Trace (Schema)" → `track-trace-genealogy`

**Vorteile:**
- ✅ Klare Unterscheidung
- ✅ Beide verfügbar

**Nachteile:**
- ⚠️ Zwei Einträge für einen Use-Case

---

### Empfehlung: **Option 1 + Option 3 (Kombination)**

1. **Neue Route:** `dsp/use-case/track-trace-genealogy`
2. **Im DSP-Tab:** Zwei Einträge:
   - "Track & Trace (Live Demo)" → `track-trace`
   - "Track & Trace (Schema)" → `track-trace-genealogy`

**Oder:** Ein Eintrag "Track & Trace" mit zwei Buttons:
- "Live Demo" → `track-trace`
- "Schema" → `track-trace-genealogy`

---

## 📋 Implementierungs-Schritte

### 1. Farben zentral definieren

**Datei:** `osf/apps/osf-ui/src/app/assets/_color-palette.scss`
- CSS-Variablen für Track & Trace hinzufügen

**Datei:** `osf/apps/osf-ui/src/app/assets/color-palette.ts`
- TypeScript-Konstanten für Track & Trace hinzufügen

### 2. Routing anpassen

**Datei:** `osf/apps/osf-ui/src/app/app.routes.ts`
```typescript
{
  path: 'dsp/use-case/track-trace',
  loadComponent: () =>
    import('./tabs/track-trace-tab.component').then((m) => m.TrackTraceTabComponent),
},
{
  path: 'dsp/use-case/track-trace-genealogy', // NEU
  loadComponent: () =>
    import('./pages/use-cases/track-trace-genealogy/track-trace-genealogy-use-case.component').then(
      (m) => m.TrackTraceGenealogyUseCaseComponent
    ),
},
```

### 3. DSP-Tab anpassen

**Option A: Zwei Einträge**
```typescript
useCases: UseCase[] = [
  {
    id: 'track-trace-live',
    title: 'Track & Trace (Live Demo)',
    detailRoute: '/dsp/use-case/track-trace',
    // ...
  },
  {
    id: 'track-trace-genealogy',
    title: 'Track & Trace (Schema)',
    detailRoute: '/dsp/use-case/track-trace-genealogy',
    // ...
  },
  // ...
];
```

**Option B: Ein Eintrag mit zwei Buttons**
- Im `DspUseCasesComponent` Template:
  - "View Live Demo" Button → `track-trace`
  - "View Schema" Button → `track-trace-genealogy`

---

## ✅ Entscheidung erforderlich

1. **Farben:** Option A (CSS) + Option B (TypeScript) verwenden?
2. **Routing:** Option 1 (separate Route) + Option 3 (zwei Einträge) verwenden?
3. **DSP-Tab:** Zwei Einträge oder ein Eintrag mit zwei Buttons?

---

*Letzte Aktualisierung: 29.01.2026*
