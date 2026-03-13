# AGV-Darstellung im Shopfloor: ORDER-Tab vs. AGV-Tab – Farbanalyse

> **→ Superseded by [DR-24 Shopfloor-Highlight-Farben](../03-decision-records/24-shopfloor-highlight-colors.md)** (2026-03-10)

**Stand:** März 2026 | **Nur Analyse** (historisch)

---

## 1. Festlegung (Dokumentation)

Laut [second-agv-2026-03.md](second-agv-2026-03.md) und `color-palette.ts`:

| AGV      | Farbe                     | RGB           | Verwendung                    |
|----------|----------------------------|---------------|-------------------------------|
| AGV-1    | Orange                     | 249, 115, 22  | Shopfloor, AGV-Tab, **Orders** |
| AGV-2    | Gelb                       | 234, 179, 8   | Shopfloor, AGV-Tab, **Orders** |

> „Fixed assignment: AGV-1 orange, AGV-2 yellow – konsistent in allen Tabs“

---

## 2. Technische Umsetzung

### 2.1 AGV-Tab

- **Eingabe:** `[ftsPositions]` – Array mit `{ serial, x, y, color? }` aus `ftsStates$`
- **Darstellung:** `ftsOverlays` (`.preview__fts`) – pro AGV ein Overlay
- **Farbe:** `item.color ?? mappingService.getAgvColor(item.serial)` → AGV-1 orange, AGV-2 gelb
- **CSS:** `--fts-accent-rgb` pro Overlay, Glow/Schatten/Ring in AGV-Farbe

### 2.2 ORDER-Tab (OrderCard → Shopfloor-Preview)

- **Eingabe:** `[order]`, `[activeStep]` – **kein** `ftsPositions`
- **Darstellung:** Bei aktivem NAVIGATION-Step: `routeOverlay` (FTS auf Routen-Mittelpunkt) und orangefarbene Routen-Segmente
- **Farbe des FTS:** `loadSvgWithGreenFill()` → **highlightGreen.strong** (#64a70b)
- **CSS:** Gleiche Klasse `.preview__fts`, aber **kein** `--fts-accent-rgb` → Fallback auf orange für Glow; SVG-Füllung ist grün

---

## 3. Abweichung: ORDER-Tab nutzt Grün statt AGV-Farben

| Kontext        | FTS-Darstellung        | Farbe                         | AGV-abhängig?   |
|----------------|------------------------|-------------------------------|-----------------|
| AGV-Tab        | ftsOverlays            | Orange (AGV-1) / Gelb (AGV-2) | Ja              |
| ORDER-Tab      | routeOverlay           | Grün (highlightGreen.strong)  | Nein            |

Im ORDER-Tab wird also **nicht** AGV-1/AGV-2 verwendet, sondern eine feste grüne Farbe (ORBIS-Highlight-Grün).

---

## 4. Mögliche Erklärung

- **ORDER-Tab:** Fokus auf „aktiver NAVIGATION-Schritt“ – generisches FTS-Icon auf der Route, Farbe signalisiert „aktiv/in Bearbeitung“ (grün als Akzent).
- **AGV-Tab:** Fokus auf „welches AGV wo steht“ – Unterscheidung AGV-1 vs. AGV-2 in den Farben orange/gelb.

Die Doku spricht von „konsistent in allen Tabs“, technisch ist der ORDER-Tab jedoch derzeit grün und nicht orange/gelb.

---

## 5. Vor der 2-AGV-Änderung (User-Erinnerung)

> „Vor unserer Änderung für Unterstützung von 2 AGVs war das AGV in orange wie die Route.“

- **Möglichkeit 1:** Früher war der ORDER-Overlay orange (z. B. gleiche Farbe wie Route).
- **Möglichkeit 2:** `loadSvgWithGreenFill` existierte bereits; die Erinnerung bezieht sich auf einen anderen Kontext (z. B. AGV-Tab).
- **Möglichkeit 3:** Ein Refactoring hat den ORDER-Pfad auf Grün umgestellt.

Ohne Git-Historie ist das nicht sicher rekonstruierbar.

---

## 6. Referenzen im Code

| Datei                                   | Relevant                                      |
|-----------------------------------------|-----------------------------------------------|
| `shopfloor-preview.component.ts`        | L. 1065–1067: `loadSvgWithGreenFill` für routeOverlay |
| `shopfloor-preview.component.ts`        | L. 584–595: ftsPosition (single) → highlightGreen |
| `shopfloor-preview.component.ts`        | L. 585–588: ftsPositions (multi) → getAgvColor  |
| `color-palette.ts`                      | highlightGreen.strong: #64a70b                  |
| `second-agv-2026-03.md`                 | „AGV-1 orange, AGV-2 gelb – alle Tabs“         |

---

*Analyse ohne Änderungen am Code.*
