# UC-03 — AI Lifecycle Diagram Spec (Layer View)

## Ziel
AI-Lifecycle so darstellen, dass klar wird:
- Lifecycle ist ein **Prozess** (oben)
- DSP orchestriert **Training/Model Registry/Deployment** (Mitte)
- Deployment erfolgt **an mehrere Stationen** (unten, gruppiert nach Edge 1..n)

## Layout / Layer
### L1 (oben): Process Layer (Lifecycle)
Container: "AI Lifecycle Process"
Boxen (3):
1) Data Capture & Context
2) Train & Validate (Cloud)
3) Monitor & Feedback

Hinweis: Feedback-Loop visuell andeuten (Monitor → Data Capture) über einen Rückpfeil (L-Shape).

### L2 (Mitte): DSP Layer
Container: DSP
- DSP Edge 1 (On-Prem)
- DSP Management Cockpit (Cloud)
- DSP Edge 2..n (On-Prem) [optional, mindestens 2 zeigen]

Wichtig:
- Pfeile laufen **nicht über Boxen**, sondern nur in Gassen zwischen Boxen.
- Vermittlung: Shopfloor → DSP Edge → (Cockpit/Cloud) → DSP Edge → Shopfloor
- Das Cockpit ist die zentrale Stelle für: Model Registry, Approval, Rollout/Rollback.

### L3 (unten): Shopfloor Layer
Container: Shopfloor
- Stations Group für Edge 1: "Stations 1..m1" (als mehrfach gestapelte Kacheln)
- Stations Group für Edge 2: "Stations 1..m2" (als mehrfach gestapelte Kacheln)
- **Kein FTS/AGV** in diesem Diagramm (ist hier nicht der Fokus).

## Komponenten (Wording, DE/EN)
DE:
- Data Capture & Context: "Daten erfassen & Kontext anreichern"
- Train & Validate (Cloud): "Trainieren & Validieren (Cloud)"
- Monitor & Feedback: "Monitoring & Feedback"
- Management Cockpit: "DSP Management Cockpit"
- DSP Edge: "DSP Edge"
- Stations: "Stationen"

EN:
- Data Capture & Context
- Train & Validate (Cloud)
- Monitor & Feedback
- DSP Management Cockpit
- DSP Edge
- Stations

## Farben / CI-Logik
- DSP Layer Hintergrund: Blau (wie DSP-Tab)
- Shopfloor Layer Hintergrund: Grau (wie OSF)
- Process Layer Hintergrund/Container: Highlight-Green (deutlich als Prozess erkennbar)
- Pfeile:
  - Prozesspfeile: Highlight-Green
  - Deployment/Provisioning: DSP-Blau
  - Feedback/Loop: Neutral dunkel (oder DSP-Blau gestrichelt)

## Pfeilführung (nur Orthogonal / L-Shape)
- Keine diagonalen Pfeile
- Keine Pfeile über Boxen
- Alle Pfeile docken an Box-Kanten an (Top/Bottom/Left/Right)

## Kernmessage (muss visuell klar werden)
"Train centrally → Deploy to multiple stations (where needed)"
- Positionierung: Zwischen Cockpit und Edges / als Label im Deployment-Pfeil.

## Export / Technik
- Alles in **einem SVG**
- Elemente als Gruppen mit stabilen IDs (siehe Animation)
- Text als echte SVG-Text-Elemente (kein Raster), damit i18n/DE-EN einfach möglich ist
