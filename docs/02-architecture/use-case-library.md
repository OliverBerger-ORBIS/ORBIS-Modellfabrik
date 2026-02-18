# Use-Case Bibliothek – Dokumentation und Konsistenzanalyse

**Erstellt:** 18.02.2026  
**Status:** Ist-Zustand der Use-Case-Bibliothek

---

## 1. Übersicht

Die **Use-Case Bibliothek** im OSF Dashboard präsentiert die DSP (Digital Shopfloor Platform) Use-Cases als interaktive Diagramme mit Schritt-für-Schritt-Animation. Jeder Use-Case visualisiert ein zentrales Konzept der Smart Factory (Datenaggregation, Track & Trace, AI Lifecycle, Closed Loop Quality, Predictive Maintenance, Interoperabilität).

**SVG-Export:** `node scripts/export-use-case-svgs.js`. Bei Fehlermeldung zu Chrome: `npx puppeteer browsers install chrome` ausführen.

### 1.1 Zentraler Einstieg

| Komponente | Beschreibung |
|------------|--------------|
| **DspUseCasesComponent** | Übersicht aller Use-Cases im DSP-Tab (Einzelklick: Details, Doppelklick: Detailseite) |
| **UseCaseSelectorPageComponent** | Vollständige Use-Case-Übersicht unter `/:locale/dsp/use-case` |
| **Detail-Komponenten** | Einzelne Use-Case-Seiten unter `/:locale/dsp/use-case/:uc-name` |

### 1.2 Routing-Matrix

| Route-Pfad | Komponente | UC-Nr. |
|------------|------------|--------|
| `dsp/use-case` | UseCaseSelectorPageComponent | – |
| `dsp/use-case/track-trace` | **TrackTraceTabComponent** (Live Demo) | – |
| `dsp/use-case/track-trace-genealogy` | TrackTraceGenealogyUseCaseComponent | UC-01 |
| `dsp/use-case/three-data-pools` | ThreeDataPoolsUseCaseComponent | UC-02 |
| `dsp/use-case/ai-lifecycle` | AiLifecycleUseCaseComponent | UC-03 |
| `dsp/use-case/closed-loop-quality` | ClosedLoopQualityUseCaseComponent | UC-04 |
| `dsp/use-case/predictive-maintenance` | PredictiveMaintenanceUseCaseComponent | UC-05 |
| `dsp/use-case/interoperability` | InteroperabilityUseCaseComponent | UC-06 |

---

## 2. Bestehende Use-Cases (Detailseiten)

### UC-01: Track & Trace Genealogie

- **Ordner:** `track-trace-genealogy/`
- **Dateien:** Component, `uc-01-structure.config.ts`, `uc-01-svg-generator.service.ts`, `uc-01-i18n.service.ts`
- **Steps:** `assets/use-cases/uc-01/uc-01-track-trace-genealogy.steps.json`
- **Inhalt:** Partiture-Diagramm mit Business Context, NFC-Thread, Shopfloor-Stationen, Genealogie

### UC-02: Three Data Pools (Datenaggregation)

- **Ordner:** `three-data-pools/`
- **Dateien:** Component, `uc-02-structure.config.ts`, `uc-02-structure-lanes.config.ts`, `uc-02-svg-generator.service.ts`, `uc-02-svg-generator-lanes.service.ts`, `uc-02-i18n.service.ts`
- **Steps:** `assets/use-cases/uc-02/uc-02-three-data-pools.steps.json`
- **Besonderheit:** Zwei Ansichten (Concept vs. Architecture Lanes) mit separaten SVG-Generatoren

### UC-03: AI Lifecycle

- **Ordner:** `ai-lifecycle/`
- **Dateien:** Component, `uc-03-structure.config.ts`, `uc-03-svg-generator.service.ts`, `uc-03-i18n.service.ts`
- **Steps:** `assets/use-cases/uc-03/uc-03-ai-lifecycle.steps.json`
- **Besonderheit:** `UC03_CONNECTION_IDS` in `uc-03-structure.config.ts` für `dim-conn` (Verbindungen abblenden)

### UC-04: Closed Loop Quality

- **Ordner:** `closed-loop-quality/`
- **Dateien:** Component, `uc-04-structure.config.ts`, `uc-04-svg-generator.service.ts`, `uc-04-i18n.service.ts`
- **Steps:** `assets/use-cases/uc-04/uc-04-closed-loop-quality.steps.json`
- **Besonderheit:** `UC04_CONNECTION_IDS` in `uc-04-structure.config.ts` für `dim-conn`

### UC-05: Predictive Maintenance

- **Ordner:** `predictive-maintenance/`
- **Dateien:** Component, `uc-05-structure.config.ts`, `uc-05-svg-generator.service.ts`, `uc-05-i18n.service.ts`
- **Steps:** `assets/use-cases/uc-05/uc-05-predictive-maintenance.steps.json`
- **Besonderheit:** `UC05_CONNECTION_IDS` in `uc-05-structure.config.ts` für `dim-conn`

### UC-06: Interoperabilität (Event-to-Process)

- **Ordner:** `interoperability/`
- **Dateien:** Component, `uc-06-structure.config.ts`, `uc-06-svg-generator.service.ts`, `uc-06-i18n.service.ts`
- **Steps:** `assets/use-cases/uc-06/uc-06-event-to-process-map.steps.json`
- **Besonderheit:** Keine Connection-IDs (leeres Array)

---

## 3. Gemeinsame Struktur

### 3.1 Datei-Organisation (pro Use-Case)

```
use-cases/
├── shared/
│   ├── base-use-case.component.ts       # Abstrakte Basis-Klasse für alle Use-Case-Komponenten
│   ├── use-case-controls/               # Wiederverwendbare Header-Komponente (Nav, Step-Dots, Zoom)
│   │   ├── use-case-controls.component.ts
│   │   ├── use-case-controls.component.html
│   │   └── use-case-controls.component.scss
│   └── use-case-step-apply.ts           # Shared Auto-Dim applyStep-Logik
└── [uc-name]/
    ├── [uc-name]-use-case.component.ts
    ├── [uc-name]-use-case.component.html
    ├── [uc-name]-use-case.component.scss
    ├── uc-[nn]-structure.config.ts
    ├── uc-[nn]-svg-generator.service.ts
    └── uc-[nn]-i18n.service.ts
```

### 3.2 Basis-Klasse BaseUseCaseComponent

Alle Use-Case-Komponenten erweitern die abstrakte Klasse `BaseUseCaseComponent` (`shared/base-use-case.component.ts`).

| Abstrakte Methode | Beschreibung |
|------------------|--------------|
| `getStepsUrl()` | Pfad zur steps.json (z.B. `assets/use-cases/uc-01/uc-01-track-trace-genealogy.steps.json`) |
| `getStepPrefix()` | Prefix für SVG-Element-IDs (z.B. `uc01`, `uc02`) |
| `getConnectionIds()` | IDs von Verbindungselementen für `dim-conn` (leeres Array wenn keine) |
| `loadSvgContent()` | Gibt SVG-String zurück (nutzt I18n-Service und SVG-Generator) |

Die Basis-Klasse übernimmt: Steps laden, SVG laden/sanitisieren, Step-Animation (applyStepToSvg), Navigation (prev/next/goToStep), Auto-Play, Loop, Description-Toggle, Zoom.

**UC-02-Sonderfall:** `setViewMode()` überschreibt das Verhalten beim Wechsel zwischen Concept- und Lanes-Ansicht und ruft `loadSvg()` erneut auf.

### 3.3 Gemeinsame Komponenten-Features

| Feature | Beschreibung |
|---------|--------------|
| **SVG-Generierung** | Dynamisch zur Laufzeit aus Structure-Config |
| **I18n** | DE/EN/FR über I18n-Service und `messages.{locale}.json` |
| **Step-Animation** | `steps.json` mit `highlightIds`, `dimIds`, `hideIds` |
| **Zoom** | 40–180 %, fein/robust abhängig von Zoom-Level |
| **Navigation** | Prev/Next, Auto-Play, Loop, Step-Dots |
| **CSS-Klassen** | `.hl` (highlight), `.dim`, `.dim-conn`, `.hidden` |

### 3.4 Step-Interface (JSON)

```typescript
interface UseCaseStep {
  id: string;
  title: { de: string; en: string; fr?: string };
  description?: { de: string; en: string; fr?: string };
  highlightIds: string[];
  hideIds: string[];
}
```

`dimIds` und `showIds` wurden entfernt – Auto-Dim nutzt nur `highlightIds` und `hideIds`.

---

## 4. Konsistenzanalyse

### 4.1 UI-Header (Shared use-case-controls)

Alle Use-Cases nutzen die gemeinsame Komponente `UseCaseControlsComponent` mit:

| Element | Beschreibung |
|---------|--------------|
| **Title** | Content Projection `[use-case-title]` |
| **View-Toggle** | Optional per `[viewToggleTemplate]` (nur UC-02: Concept/Lanes) |
| **Navigation** | Prev, Auto-Play, Loop, ℹ (Description), Next |
| **Step-Info** | Zähler, Step-Dots |
| **Zoom** | −, Anzeige, +, Reset |

Reihenfolge: Title → [View-Toggle] → Nav → Step-Info → Zoom

### 4.2 Step-Beschreibung (applyStep-Logik)

**Einheitlich bei allen Use-Cases:** Step 0 (Overview) zeigt Subtitle, Step 1+ zeigt Beschreibung nur bei aktiviertem User-Toggle (ℹ). Shared: `applyStepToSvg()` in `use-case-step-apply.ts`.

### 4.3 Dim-/Highlight-Logik (einheitlich Auto-Dim)

| Use-Case | highlightIds | hideIds | connectionIds | Quelle |
|----------|--------------|---------|---------------|--------|
| UC-01, 02, 06 | explizit | explizit | `[]` | `getConnectionIds()` in Component |
| UC-03, 04, 05 | explizit | explizit | aus `uc-0n-structure.config.ts` | `UC0n_CONNECTION_IDS` exportiert, Component importiert |

Shared: `applyStepToSvg()` in `shared/use-case-step-apply.ts`.

### 4.4 step-dots aria-label / SVG-Container-Lookup

**Einheitlich:** `getStepTitle(step)` für Step-Dots; `svgContainer?.nativeElement?.querySelector('svg')` für Apply-Logik.

### 4.5 Service-Namen

Alle Services folgen dem Muster `Uc{NN}{SvgGenerator|I18n}Service` und sind `providedIn: 'root'`. Konsistent.

### 4.6 BEM-Klassen (SCSS)

- **Use-Case-Container:** `.[uc-name]-use-case`, `.__header`, `.__content`, `.__diagram-wrapper`, `.__diagram`, `.__svg-wrapper`, `.__loading`
- **Shared Controls:** `use-case-controls`, `use-case-controls__title`, `use-case-controls__navigation`, `use-case-controls__step-info`, `use-case-controls__zoom`, `use-case-controls__view-toggle`

### 4.7 SVG-Dimensionen (viewBox)

**Einheitlich 1920×1080** (Full-HD) für alle Use-Cases – konsistente Skalierung beim Wechsel.

---

## 5. Architektur-Diagramm (Vereinfacht)

```
DspUseCasesComponent (Übersicht)
        │
        ├── Use-Case Karten (Klick → Detail)
        │
        └── Navigate → Use-Case-Detailseiten
                │
                ├── UC-01 TrackTraceGenealogyUseCaseComponent
                ├── UC-02 ThreeDataPoolsUseCaseComponent
                ├── UC-03 AiLifecycleUseCaseComponent
                ├── UC-04 ClosedLoopQualityUseCaseComponent
                ├── UC-05 PredictiveMaintenanceUseCaseComponent
                └── UC-06 InteroperabilityUseCaseComponent
                        │
                        ├── [uc]-structure.config.ts
                        ├── [uc]-svg-generator.service.ts
                        └── [uc]-i18n.service.ts
                                │
                                └── assets/use-cases/uc-[nn]/[uc].steps.json
```

---

## 6. Referenzen

- **Use-Case Inventory:** [use-case-inventory.md](use-case-inventory.md) – Übersicht aller Use-Cases mit Step 1 und Anleitung für neue Use-Cases
- **Implementierungs-Guide:** `docs/assets/use-cases/UC-DIAGRAM-IMPLEMENTATION-GUIDE.md`
- **SVG-Struktur-Plan:** `docs/assets/use-cases/UC-USE-CASE-SVG-STRUCTURE-PLAN.md`
- **ORBIS-CI Farben:** `docs/03-decision-records/14-orbis-ci-usage.md`
- **Projekt-Struktur:** `docs/02-architecture/project-structure.md`

---

*Erstellt: 18.02.2026*
