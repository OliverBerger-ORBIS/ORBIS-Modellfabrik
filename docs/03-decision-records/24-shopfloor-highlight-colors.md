# 24 – Shopfloor-Highlight-Farben: Order-Tab vs. AGV-Tab

**Status:** Accepted  
**Datum:** 2026-03-10  
**Kontext:** Farbkonsistenz im Shopfloor, Fokus auf Order-Tab (aktiver Schritt) vs. AGV-Tab (AGV-Positionen)

---

## Entscheidung

1. **Order-Tab – Aktives Modul und FTS auf Route: ORBIS-Highlight-Grün**
   - Das aktive Modul (z. B. HBW bei PROCESS-Step) und das FTS auf der Route (NAVIGATION-Step) werden einheitlich in **Grün** (highlightGreen.strong) hervorgehoben.
   - **Grund:** Beide repräsentieren denselben aktiven Schritt. Eine Farbe signalisiert „dies ist der aktive Schritt“ und vermeidet semantische Uneinheitlichkeit.

2. **AGV-Farben (AGV-1 orange, AGV-2 gelb) gelten im AGV-Tab und Presentation-Tab**
   - Die farbliche Unterscheidung AGV-1 orange / AGV-2 gelb wird im **AGV-Tab** und **Presentation-Tab** verwendet (Presentation nutzt den AGV-Tab mit `presentationMode=true`, daher dieselbe `ftsPositions`-Logik).
   - **Grund:** Nur hier ist relevant, welches AGV wo steht. Im Order-Tab steht der Schritt-Fokus im Vordergrund, nicht die AGV-Identität.

---

## Gründe

### Warum Grün im Order-Tab?
- **Konsistenz:** FTS (grün) und aktives Modul (grün) bilden eine klare Einheit „aktiver Schritt“.
- **Semantik:** Grün als Akzent für „aktiv/in Bearbeitung“ passt zum FTS auf der Route.
- **Keine Überlappung:** Im Order-Tab wird kein `moduleStatusMap` (Verfügbarkeit) genutzt – Grün konkurriert dort nicht mit anderen Bedeutungen.

### Warum AGV-Farben nur im AGV-Tab?
- **Kontextbezug:** Im Order-Tab geht es um die Schritte, nicht um die Zuordnung zu einem bestimmten AGV.
- **Vereinfachung:** Weniger Farben und Bedeutungen im Order-Tab.
- **Klare Trennung:** AGV-Tab und Presentation-Tab = „Wo ist welches AGV?“ → Orange/Gelb. Order-Tab = „Welcher Schritt läuft?“ → Grün.

### Warum Blau für Auswahl (Configuration/Shopfloor)?
- Blau (orbis-blue-strong) bleibt die einheitliche Farbe für **Auswahl** und **Fokus** in Configuration- und Shopfloor-Tab.
- Im Order-Tab gibt es keine Nutzerauswahl von Modulen, daher wird hier Grün für den aktiven Schritt genutzt.

---

## Alternativen

- **Alternative 1 (verworfen):** Aktives Modul weiterhin blau – einheitliche „Highlight“-Farbe.
  - **Grund:** FTS (grün) und Modul (blau) wirkten inkonsistent für den gleichen „aktiven Schritt“.

- **Alternative 2 (verworfen):** AGV-1/2-Farben in allen Tabs.
  - **Grund:** Im Order-Tab keine `ftsPositions`, Fokus auf Schritte; technisch und konzeptionell unnötig.

---

## Konsequenzen

- **Positiv:** Klare, kontextabhängige Farbbedeutung; Order-Tab wirkt konsistent.
- **Negativ:** Keine.
- **Risiken:** Bei späterer Einführung von `moduleStatusMap` im Order-Tab müsste die Verwendung von Grün (aktiv vs. READY) geprüft werden.

---

## Implementierung

- [x] `highlightStyle: 'selection' | 'active-step'` im Shopfloor-Preview
- [x] Order-Card übergibt `highlightStyle="'active-step'"`
- [x] CSS-Klasse `.preview__element--active-step` mit highlightGreen
- [x] Doku in color-palette.ts und second-agv-2026-03.md angepasst

---

## Referenzen

- [agv-order-tab-color-analysis-2026-03.md](../07-analysis/agv-order-tab-color-analysis-2026-03.md)
- [order-tab-active-module-highlight-analysis-2026-03.md](../07-analysis/order-tab-active-module-highlight-analysis-2026-03.md)
- [14-orbis-ci-usage.md](14-orbis-ci-usage.md) – CI-Farbpalette
