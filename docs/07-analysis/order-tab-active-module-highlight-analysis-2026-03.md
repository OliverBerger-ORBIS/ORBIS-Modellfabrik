# ORDER-Tab: Aktives Modul – Blau vs. ORBIS-Highlight-Grün

> **→ Superseded by [DR-24 Shopfloor-Highlight-Farben](../03-decision-records/24-shopfloor-highlight-colors.md)** (2026-03-10)

**Stand:** März 2026 | **Analyse** (historisch)

---

## 1. Beobachtung

Im ORDER-Tab:
- **FTS auf Route** (aktiver NAVIGATION-Step): grün (ORBIS-Highlight-Grün / highlightGreen.strong)
- **Aktives Modul** (z. B. HBW bei PROCESS-Step): **blau** (orbis-blue-strong) – Umrandung und Hintergrund

Frage: Warum Blau? Sollte für Konsistenz ebenfalls Grün verwendet werden?

---

## 2. Aktuelle Implementierung

### 2.1 Shopfloor-Preview: Zwei Highlight-Arten

| Klasse                        | Farbe                | Verwendung                                      |
|------------------------------|----------------------|-------------------------------------------------|
| `.preview__element--highlight` | Blau (orbis-blue-strong) | Ausgewähltes Modul (Configuration, Shopfloor) oder **aktives Modul** (Order) |
| `.preview__element--current-position` | Grün (status-success-strong) | Aktuelle FTS-Position (AGV-Tab)                 |

### 2.2 Wie kommt das Highlight zustande?

- **Order Card** übergibt `[order]`, `[activeStep]` – **kein** `highlightModulesOverride`, **kein** `moduleStatusMap`
- `applyActiveStepHighlights()` fügt das Modul des aktiven Steps zu `moduleHighlightSet` hinzu
- Das Modul erhält `highlighted: true` → CSS-Klasse `.preview__element--highlight` → **blau**

### 2.3 Kommentar im Code

```scss
// shopfloor-preview.component.scss L. 202
.preview__element--highlight {
  // Blue border for selected module (Module-Tab)
  border: 3px solid var(--orbis-blue-strong) !important;
  ...
}
```

Es gibt keinen expliziten Hinweis auf eine Design-Entscheidung; der Kommentar bezieht sich auf den Module-Tab.

---

## 3. Verwendung von Highlight-Klassen pro Tab

| Tab             | highlightModulesOverride | currentPositionModulesOverride | moduleStatusMap | Ergebnis |
|-----------------|---------------------------|--------------------------------|-----------------|----------|
| **Order**       | – (nur activeStep)        | –                              | –               | Aktives Modul = blau |
| **AGV**         | null                      | currentPositionNode$           | –               | FTS-Position = grün |
| **Shopfloor**   | selectedModuleSerialNumber| –                              | ✓ (Verfügbarkeit) | Auswahl = blau, Verfügbarkeit = grün/orange/rot |
| **Configuration** | vm.highlightModules     | –                              | –               | Auswahl = blau |

---

## 4. Verfügbarkeits-Farbkodierung (Shopfloor-Tab)

Im Shopfloor-Tab hat jedes Modul eine Verfügbarkeits-Farbe:

- **READY** (verfügbar): grün (status-success-strong)
- **BUSY**: orange (status-warning)
- **BLOCKED**: rot (status-error)
- **Unknown**: grau

Wenn ein Modul **gleichzeitig** ausgewählt ist, gilt: **Blau überschreibt** die Verfügbarkeits-Farbe (`.preview__element--highlight` hat höhere Spezifität).

---

## 5. Mögliche Gründe für Blau

### 5.1 Einheitliche „Fokus/Selection“-Farbe

- **Blau (orbis-blue-strong)** = primäre Markenfarbe, für Fokus und Auswahl
- Configuration-Tab, Shopfloor-Tab, Module-Tab: Auswahl → immer blau
- Das „aktive Modul“ im Order-Tab wird wie eine Auswahl behandelt → gleiche blaue Hervorhebung

### 5.2 Vermeidung von Mehrdeutigkeit

- **Grün** wird bereits für „READY“ (Verfügbarkeit) im Shopfloor-Tab genutzt
- Wenn Order-Tab das aktive Modul ebenfalls grün hervorheben würde, könnte das mit „Modul ist bereit“ verwechselt werden
- **Einschränkung:** Order-Tab nutzt aktuell **kein** `moduleStatusMap` → es gibt dort gar keine Verfügbarkeits-Farben

### 5.3 „Nicht zu bunt“

- Viele Farben (Grün für FTS, Grün für Modul, Orange für Route, ggf. Verfügbarkeit) können optisch überladen wirken
- Blau als neutrale Fokus-Farbe reduziert die Farbvielfalt

---

## 6. Option: Grün für aktives Modul im ORDER-Tab

**Argument für Grün:**
- Konsistenz: FTS (grün) + aktives Modul (grün) = „dies ist der aktive Schritt“
- Einheitliche Semantik: „Aktiver Schritt“ = eine Farbe (grün)

**Technische Umsetzung:**
- Neuer Kontext-Parameter, z. B. `highlightVariant: 'selection' | 'active-step'`
- Oder: Zusätzliche Klasse `.preview__element--active-step` mit grüner Umrandung
- Nur aktiv, wenn `order` + `activeStep` gesetzt und das Highlight aus `applyActiveStepHighlights` stammt (nicht aus `highlightModulesOverride`)

**Konflikt mit Verfügbarkeit:**
- Im Order-Tab wird aktuell kein `moduleStatusMap` übergeben → keine Verfügbarkeits-Farben
- Ein Wechsel zu Grün im Order-Tab würde also nicht mit der Verfügbarkeits-Kodierung kollidieren

---

## 7. Empfehlung

Es gibt **keine explizite Design-Entscheidung** im Code oder in den DRs, die Blau für den Order-Tab zwingend vorschreibt. Die Gründe für Blau sind implizit (einheitliche Fokus-Farbe, Zurückhaltung bei Farbe).

**Für Konsistenz im ORDER-Tab** spricht die Variante **Grün für das aktive Modul**, weil:
1. FTS und aktives Modul dieselbe Semantik haben („aktiver Schritt“)
2. Im Order-Tab keine Verfügbarkeits-Farben genutzt werden
3. Grün für „aktiv/in Bearbeitung“ gut zur bestehenden FTS-Darstellung passt

**Gegen Grün** spricht:
1. Blau ist die etablierte „Highlight/Selection“-Farbe in anderen Tabs
2. Eventuelle spätere Erweiterung des Order-Tabs um Verfügbarkeit könnte Grün mehrdeutig machen

---

## 8. Referenzen

| Datei                                      | Relevant |
|-------------------------------------------|----------|
| `shopfloor-preview.component.scss`         | L. 202–215: `.preview__element--highlight` (blau) |
| `shopfloor-preview.component.scss`        | L. 217–222: `.preview__element--current-position` (grün) |
| `shopfloor-preview.component.scss`         | L. 224–311: Verfügbarkeits-Farben (--available, --busy, --blocked) |
| `shopfloor-preview.component.ts`          | L. 657–666: `applyActiveStepHighlights` |
| [agv-order-tab-color-analysis-2026-03.md](agv-order-tab-color-analysis-2026-03.md) | FTS-Farben im Order-Tab |
