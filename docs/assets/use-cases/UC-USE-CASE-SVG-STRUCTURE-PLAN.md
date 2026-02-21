# Use-Case SVG Strukturierungsplan

## Problemstellung

1. **SVG-Icons werden nicht geladen**: `<image href="assets/svg/...">` Tags in SVGs funktionieren nicht, wenn das SVG als `<img>` Tag geladen wird
2. **Fehlende einheitliche Struktur**: Keine konsistente Benennung für Animation-Metadaten
3. **Farben nicht einheitlich**: Farben sollten über Namen referenziert werden (analog zu DSP-Architecture)
4. **Dimensionen zu klein**: Columns sollten höher sein
5. **Unterschiedliche Strukturprinzipien**: Use-Cases verwenden **Columns** statt **Layers** (wie DSP-Architecture)

## Vorbild: DSP-Architecture

### Strukturprinzip: Layers (horizontal)
- `layer-bp` (Business Process) - weiß
- `layer-dsp` (DSP) - ORBIS-blau (`rgba(207, 230, 255, 0.5)`)
- `layer-sf` (Shopfloor) - grau (`rgba(241, 243, 247, 0.8)`)

### Farben (aus `color-palette.ts`)
- DSP Layer: `rgba(207, 230, 255, 0.5)` → entspricht `--orbis-blue-light` mit Opacity
- Business Process: `#ffffff`
- Shopfloor: `rgba(241, 243, 247, 0.8)`

### IDs & Metadaten
- Semantische IDs: `layer-*`, `edge-*`, `sf-system-*`, `sf-device-*`
- Step-basierte Animation mit `StepConfig`
- Icons über `icon-registry.ts` aufgelöst

## Use-Case Strukturprinzip: Columns (vertikal)

### 3-Column-Struktur für UC-00 (Interoperability)
1. **Column Sources** (`col-sources`) - Links
   - Events & Signale aus verschiedenen Quellen
   - Farbe: Weiß oder neutral (analog zu Business Process Layer)
   
2. **Column DSP** (`col-dsp`) - Mitte
   - Normalisierung, Kontext, Korrelation
   - Farbe: **ORBIS-blau** (analog zu `layer-dsp`)
   - `rgba(207, 230, 255, 0.5)` oder `var(--orbis-blue-light)` mit Opacity
   
3. **Column Targets** (`col-targets`) - Rechts
   - Process View & Zielsysteme
   - Farbe: Weiß oder neutral (analog zu Business Process Layer)

### Farbzuordnung (analog zu DSP-Architecture)

```scss
// Use-Case Column Colors (analog zu DSP Layers)
:root {
  // Column DSP (Mitte) - ORBIS-blau wie DSP Layer
  --uc-col-dsp-bg: rgba(207, 230, 255, 0.5);
  --uc-col-dsp-border: rgba(22, 65, 148, 0.15);
  
  // Column Sources/Targets (Links/Rechts) - neutral wie Business Process
  --uc-col-sources-bg: #ffffff;
  --uc-col-targets-bg: #ffffff;
  --uc-col-border: rgba(22, 65, 148, 0.1);
  
  // Panel Background (wie Shopfloor Layer)
  --uc-panel-bg: rgba(241, 243, 247, 0.8);
  --uc-panel-border: rgba(31, 54, 91, 0.12);
}
```

## Einheitliche Benennungskonvention

### Column-IDs
- `uc{NN}_col_sources` - Links (Sources)
- `uc{NN}_col_dsp` - Mitte (DSP Processing)
- `uc{NN}_col_targets` - Rechts (Targets/Outcomes)

### Lane-IDs (innerhalb Columns)
- `uc{NN}_lane_business_context`
- `uc{NN}_lane_machine_station`
- `uc{NN}_lane_agv_amr`
- `uc{NN}_lane_quality_aiqs`
- `uc{NN}_lane_env_sensors`

### Step-IDs (innerhalb DSP Column)
- `uc{NN}_step_normalize`
- `uc{NN}_step_enrich`
- `uc{NN}_step_correlate`

### Event-IDs
- `uc{NN}_ev_machine_start`
- `uc{NN}_ev_machine_status`
- `uc{NN}_ev_agv_pick`
- `uc{NN}_ev_quality_check`

### Icon-IDs
- `uc{NN}_lane_{name}_icon`
- `uc{NN}_target_{name}_icon`

## SVG-Icon-Problem: Lösung

### Problem
`<image href="assets/svg/...">` funktioniert nicht, wenn SVG als `<img>` geladen wird.

### Lösung 1: Inline SVG (empfohlen)
- SVG als String laden und inline einbetten
- `<image>` Tags funktionieren dann mit relativen Pfaden
- Analog zu `dsp-architecture.component.ts`

### Lösung 2: Absolute Pfade
- Pfade in SVG auf absolute URLs ändern
- Benötigt `baseHref`-Awareness

### Lösung 3: SVG-Sprite
- Alle Icons in ein SVG-Sprite einbetten
- `<use>` Tags verwenden

**Empfehlung**: Lösung 1 (Inline SVG) - analog zu DSP-Architecture

## Dimensionen & Größe

### Aktuelle Dimensionen (UC-00)
- Width: 1920px
- Height: 1080px
- Column Height: ~760px

### Vorgeschlagene Anpassungen
- **Column Height erhöhen**: Von 760px auf ~900-1000px
- **Gesamthöhe**: Von 1080px auf ~1200-1300px
- **Spacing**: Mehr Abstand zwischen Lanes/Steps

### ViewBox
- ViewBox sollte responsive sein: `viewBox="0 0 1920 1300"`
- Max-width für Responsiveness: `max-width: 100%`

## Vorgehen: Breite → Tiefe

### Phase 1: Breite (Alle Use-Cases anlegen)
1. **Struktur für alle Use-Cases definieren**
   - UC-01: Track & Trace
   - UC-02: 3 Data Pools
   - UC-03: AI Lifecycle
   - UC-04: Closed-Loop Quality
   - UC-05: Predictive Maintenance
   - UC-00: Interoperability ✅ (bereits vorhanden)

2. **Gemeinsame Struktur erstellen**
   - Column-Struktur definieren (welche Use-Cases haben Columns?)
   - Layer-Struktur definieren (welche Use-Cases haben Layers?)
   - Farbzuordnung festlegen
   - ID-Konventionen dokumentieren

3. **SVG-Templates erstellen**
   - Template für Column-basierte Use-Cases
   - Template für Layer-basierte Use-Cases
   - Farben über CSS-Variablen definieren

### Phase 2: Tiefe (Details hinzufügen)
1. **SVG-Icons-Problem beheben**
   - Inline SVG implementieren
   - Icon-Pfade korrigieren
   - Icon-Registry erweitern

2. **Animation-Metadaten hinzufügen**
   - Step-Definitionen (analog zu DSP-Architecture)
   - Highlighting-Logik
   - Transition-Definitionen

3. **Responsive & Accessibility**
   - ViewBox-Anpassungen
   - ARIA-Labels
   - Keyboard-Navigation

## Nächste Schritte

### Sofort (UC-00)
1. ✅ SVG-Icons-Problem beheben (Inline SVG)
2. ✅ Farben über CSS-Variablen definieren
3. ✅ Column-IDs konsistent benennen
4. ✅ Dimensionen anpassen (höhere Columns)

### Kurzfristig (Alle Use-Cases)
1. Struktur für alle Use-Cases analysieren
2. Templates erstellen (Column vs. Layer)
3. Farbzuordnung dokumentieren
4. ID-Konventionen festlegen

### Mittelfristig (Animation)
1. Step-Definitionen für alle Use-Cases
2. Animation-Component (analog zu DSP-Architecture)
3. Highlighting & Transitions

## Referenzen

- DSP-Architecture: `osf/apps/osf-ui/src/app/components/dsp-architecture/`
- DSP-Animation: `osf/apps/osf-ui/src/app/components/dsp-animation/`
- Color Palette: `osf/apps/osf-ui/src/app/assets/color-palette.ts`
- Icon Registry: `osf/apps/osf-ui/src/app/assets/icon-registry.ts`
- Layout Config: `osf/apps/osf-ui/src/app/components/dsp-animation/layout.config.ts`
