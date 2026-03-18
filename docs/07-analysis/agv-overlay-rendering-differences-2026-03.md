# AGV-Overlay: Rendering-Unterschiede (localhost vs. RPi)

**Stand:** März 2026 | **Kontext:** AGV-Tab, Shopfloor-Preview | **Status:** Bekannter Bug, ungelöst

---

## Fehlerbeschreibung (RPi)

**Umgebung:** OSF-UI auf 192.168.0.100:8080 (RPi), gleicher Build wie localhost (v0.9.3–v0.9.8).

### Symptome

| Aspekt | localhost (Mac) ✓ | RPi ✗ |
|--------|-------------------|-------|
| **Layering** | AGV-Icon überdeckt Modul-SVGs (z.B. CHRG0) | AGV wird vom Modul-SVG überdeckt |
| **AGV-Farbe** | Orange (AGV-1) / Gelb (AGV-2) | Blau – SVG-Farbe wird nicht übernommen |
| **Glow** | Orange, sichtbar hinter AGV | Nur orange Glow sichtbar, nicht im Vordergrund |
| **Weißer Kreis** | Überdeckt Modul dahinter | Nicht wirksam / falsche Reihenfolge |

### Screenshots (18.03.2026)

- **RPi:** AGV blau, CHRG0-Modul verdeckt AGV
- **localhost:** AGV orange, überdeckt CHRG0 korrekt

---

## Vergebliche Fix-Versuche (März 2026)

| Version | Änderung | Ergebnis |
|---------|----------|----------|
| **v0.9.3** | `.preview__fts-layer` mit `z-index: 100` | localhost ok, RPi: Overlay weiterhin falsch |
| **v0.9.4** | `isolation: isolate` auf `.preview__fts-layer` | Kein Effekt auf RPi |
| **v0.9.5** | `transform: translateZ(0)` auf Layer | Kein Effekt auf RPi |
| **v0.9.6** | `box-shadow` statt `filter: drop-shadow` | RPi: Glow nach innen, AGV weiterhin überdeckt |
| **v0.9.7** | FTS-Layer aus Canvas heraus → Geschwister im Wrapper | **Katastrophe:** Shopfloor komplett weiß auf localhost |
| **v0.9.8** | Revert auf exakten v0.9.3-Code (git checkout cf98835c) | localhost wieder ok, RPi: Bug unverändert |

**Keine der CSS-/Struktur-Ansätze hat das RPi-Rendering korrigiert.**

---

## Beobachtung (Original, v0.8.8)

- **Erwartetes Verhalten (Mac, Chrome/Safari):** AGV-1 (orange) und AGV-2 (gelb) überdecken die darunterliegenden Module/Cells und deren SVGs.
- **Beobachtetes Verhalten (RPi, 192.168.0.100:8080, gleiche Version):** AGV-Overlays deckten nicht – darunterliegende Cell-SVGs blieben sichtbar.
- **Zusatz (v0.9.8):** Auf RPi wird das AGV-SVG in Blau statt Orange/Gelb gerendert; nur der Glow hat die richtige Farbe.

## Relevante Implementierung

| Element | Eigenschaften |
|---------|----------------|
| `.preview__fts` | `position: absolute`, `z-index: 15`, `transform: translate(-50%, -50%)`, `filter: drop-shadow(...)` |
| `::after` | Weißer Kreis (78px), `background: #ffffff`, `z-index: -2` – soll darunterliegende Elemente abdecken |
| `::before` | Gestrichelter Kreis (80px), `z-index: -1` |
| Parent `.preview__canvas` | `transform: scale(...)` (inline), `overflow: visible` |

## Plausible Ursachen

### 1. `filter: drop-shadow()` – Stacking Context & GPU/CPU

- **`filter`** erzeugt einen eigenen Stacking Context und kann je Browser/Plattform unterschiedlich gerendert werden.
- **Drop-shadow** wird typischerweise **nicht** von der GPU kompositiert, sondern per CPU (Software-Rendering).
- Auf dem RPi: Eingeschränkte oder fehlende Hardware-Beschleunigung kann zu anderem Compositing-Verhalten führen.
- Safari: Bekannte Bugs mit `drop-shadow` (falscher First-Render, Flackern beim Scrollen).

### 2. Negative `z-index` auf Pseudo-Elementen

- `::after` hat `z-index: -2` – liegt damit hinter dem Hauptinhalt des Overlays.
- In einigen Rendering-Pfaden können Pseudo-Elemente mit negativem `z-index` in edge cases anders eingordnet werden.
- RPi-Chromium (oft ältere Version) könnte hier abweichend verhalten.

### 3. Browser-Version & Cache

- RPi nutzt oft **älteres Chromium** (z. B. Raspberry Pi OS mit Midori/Chromium).
- Unterschiedliche Implementierung von Stacking Context / Compositing-Layers zwischen Chrome-Versionen.
- **Cache:** Auf dem RPi könnte noch alte CSS/JS-Version liegen (ohne `::after` oder mit anderem z-index).

### 4. Kombination `transform` + `filter`

- Sowohl `.preview__canvas` (transform) als auch `.preview__fts` (transform + filter) erzeugen Stacking Contexts.
- Diese Kombination kann plattformabhängig zu unterschiedlicher Schicht-Einordnung führen.

### 5. Umgebung (GPU, Compositor)

- Mac: Stabile GPU-Komposition, typischerweise vollen Hardware-Support.
- RPi: Schwächere GPU, möglicherweise Software-Rendering, andere Compositing-Strategie.
- Je nach `chrome://gpu`-Status können Layer unterschiedlich angelegt werden.

## Bewertung: Kann es Unterschiede geben?

**Ja.** Es ist plausibel, dass sich das Rendering je nach Umgebung, Cache, Browser und GPU unterscheidet:

1. **Cache:** Klare Möglichkeit – RPi mit altem Build würde erklären, warum es gestern anders aussah.
2. **Browser/Version:** Chromium auf RPi ist oft älter; bekannte Abweichungen bei z-index/stacking.
3. **GPU/Compositing:** Software-Rendering und fehlende Hardware-Beschleunigung können das Layer-Verhalten ändern.
4. **Filter + negative z-index:** Ungünstige Kombination für plattformübergreifende Stabilität.

## Optionen bei erneutem Auftreten

1. **Cache auf RPi leeren / Hard Reload** (Strg+Shift+R), Deployment prüfen.
2. **`isolation: isolate`** auf `.preview__fts` – erzwingt einen klaren Stacking-Context-Boundary.
3. **Weißen Kreis als DOM-Kind statt `::after`** – weniger abhängig von Pseudo-Element-Rendering.
4. **`filter` auf Wrapper verschieben** – Overlay-Inhalt ohne filter, Glow nur um ein äußeres Wrapper-Element.
5. **`box-shadow` statt `filter: drop-shadow`** – `box-shadow` erzeugt keinen Stacking Context (visuell ggf. angepasst).

## Mögliche Ursache: AGV-Farbe Blau auf RPi

Die SVG-Farbe wird per `loadSvgWithColor()` gesetzt (`#154194` → AGV-Farbe Orange/Gelb). Auf RPi bleibt das SVG blau – mögliche Ursachen:

- Caching/Race: SVG wird vor dem Farb-Update angezeigt
- `innerHTML`/Sanitizer-Verhalten je nach Umgebung
- Andere Asset-Pfade oder Lade-Reihenfolge

**Code:** `ShopfloorPreviewComponent.loadSvgWithColor()`, Aufruf in `updateViewModel()`.

---

## Aktueller Stand (v0.9.8)

- **localhost:** Darstellung korrekt
- **RPi:** Bekannter Bug – AGV hinter Modulen, AGV blau
- **Kein weiterer Fix geplant** – CSS/Struktur-Ansätze haben nicht gegriffen

---

## Offene Ideen für später

1. **AGV-Farbe:** Prüfen, ob `loadSvgWithColor` auf RPi greift (Logs, Timing).
2. **Weißer Kreis als DOM-Element** statt `::after` (nicht getestet).
3. **Anderer Browser auf RPi** (z.B. Firefox) – Rendering-Unterschiede prüfen.
4. **Production vs. Dev Build:** localhost meist `nx serve`, RPi Production – Build-Unterschiede analysieren.

---

## Referenzen

- Shopfloor-Preview: `osf/apps/osf-ui/src/app/components/shopfloor-preview/`
- `.preview__fts` Styles: `shopfloor-preview.component.scss` (ca. Zeilen 380–437)
- MDN: [filter - drop-shadow](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/filter-function/drop-shadow)
- Safari drop-shadow Bugs: [mdn/browser-compat-data #17726](https://github.com/mdn/browser-compat-data/issues/17726)
