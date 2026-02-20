# 14 – ORBIS CI Usage (Colors & Fonts)

## Status
Accepted

## Context
- ORBIS CI definiert Farbwelt und Typografie im CI-Guide (PDF, Quelle: ORBIS Shared Folder).
- In OSF existiert eine zentrale Farbpalette (`osf/apps/osf-ui/src/app/assets/_color-palette.scss` und `color-palette.ts`) mit CI-Farben plus ergänzenden Statusfarben für UI-Zustände.
- Open Sans ist als Hausschrift eingebunden (`index.html`, `styles.scss`). HR-Schmuckschrift (Grit Sans) ist im CI-PDF erwähnt, aber nicht produktrelevant für das UI.

## Decision
- Farben im UI kommen ausschließlich aus der Palette:
  - In SCSS: `var(--orbis-... )` / `var(--solution-petrol-... )` etc. aus `_color-palette.scss`.
  - In TS: `ORBIS_COLORS` bzw. `getOrbisColor()` aus `color-palette.ts`.
- Statusfarben (error/success/warning) bleiben als ergänzende UI-Farben erlaubt, obwohl nicht Teil des PDF, solange sie über die zentrale Palette referenziert werden.
- Typografie: Standard ist Open Sans (über Google Fonts in `index.html` geladen), wie im CI-Guide vorgegeben.
- HR-spezifische Schrift (Grit Sans) und HR-Grafiken werden nicht im Produkt-UI verwendet.

## Consequences
- Neue Komponenten nutzen nur die zentralen Farb- und Font-Definitionen; keine direkten Hexwerte und keine zusätzlichen Webfonts ohne CI- oder Product-Design-Abstimmung.
- Bei Bedarf neuer Farbabstufungen: erst prüfen, ob die Palette reicht; ansonsten Erweiterung der Palette statt Inline-Hex.
- Review-Kriterium: Farb- und Font-Nutzung gegen Palette/CI-Guide prüfen, bevor gemergt wird.

