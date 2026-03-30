# 24 – Shopfloor-Highlight-Farben: Order-Tab vs. AGV-Tab

**Status:** Accepted  
**Datum:** 2026-03-10  
**Kontext:** Farbkonsistenz im Shopfloor, Fokus auf Order-Tab (aktiver Schritt) vs. AGV-Tab (AGV-Positionen)

---

## Entscheidung

1. **Order-Tab – Aktives Modul und FTS auf Route: ORBIS-Highlight-Grün**
   - Das aktive Modul (z. B. HBW bei PROCESS-Step) und das FTS auf der Route (NAVIGATION-Step) werden einheitlich in **Grün** (highlightGreen.strong) hervorgehoben.
   - **Grund:** Beide repräsentieren denselben aktiven Schritt. Eine Farbe signalisiert „dies ist der aktive Schritt“ und vermeidet semantische Uneinheitlichkeit.

2. **AGV-Akzent im AGV-Tab und Presentation-Tab**
   - **Stand 2026-03-16 (Amendment):** Beide FTS nutzen dieselbe **orange** Akzentfarbe (`shopfloorHighlight.strong`); Unterscheidung über Label/Dropdown/Seriennummer. *(Früher: AGV-1 orange / AGV-2 gelb – siehe [Amendment](#amendment-2026-03-16--agv-1agv-2-einheitlich-orange).)*
   - **Grund:** Nur hier ist relevant, welches AGV wo steht. Im Order-Tab steht der Schritt-Fokus im Vordergrund, nicht die AGV-Identität.

---

## Gründe

### Warum Grün im Order-Tab?
- **Konsistenz:** FTS (grün) und aktives Modul (grün) bilden eine klare Einheit „aktiver Schritt“.
- **Semantik:** Grün als Akzent für „aktiv/in Bearbeitung“ passt zum FTS auf der Route.
- **Keine Überlappung:** Im Order-Tab wird kein `moduleStatusMap` (Verfügbarkeit) genutzt – Grün konkurriert dort nicht mit anderen Bedeutungen.

### Warum AGV-Akzent nur im AGV-Tab?
- **Kontextbezug:** Im Order-Tab geht es um die Schritte, nicht um die Zuordnung zu einem bestimmten AGV.
- **Vereinfachung:** Weniger Farben und Bedeutungen im Order-Tab.
- **Klare Trennung:** AGV-Tab und Presentation-Tab = „Wo ist welches AGV?“ → einheitliches Orange für FTS-Routen/Overlays. Order-Tab = „Welcher Schritt läuft?“ → Grün.

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

---

## Amendment (2026-03-16) – AGV-1/AGV-2 einheitlich orange

**Kontext:** Nach Einführung von AGV-1 orange / AGV-2 gelb traten Probleme mit Shopfloor-Route-Overlay und Darstellung auf.

**Änderung:** Im **AGV-Tab** und **Presentation-Tab** nutzen **beide** FTS dieselbe Akzentfarbe (**shopfloor orange**, `shopfloorHighlight.strong` / `ORBIS_COLORS.agv.agv1`). `getAgvColor()` liefert für alle konfigurierten FTS-Serien dieselbe Farbe.

**Begründung:** Rückkehr zum stabilen Ein-AGV-Darstellungsmodell für Routen und Overlays; Unterscheidung weiterhin über **Label** und **Dropdown** (Seriennummer).

**Optional später:** Wenn Route/Overlay stabil sind, kann eine **zweite** Akzentfarbe für AGV-2 wieder eingeführt werden (Unterscheidbarkeit), ohne die Logik zu duplizieren.

---

## Amendment (2026-03-30, Sprint 18) – Zwei AGV-Akzente + beide Fahrzeuge sichtbar

**Kontext:** Visuelle Überladung durch Modul-Verfügbarkeitsfarben soll zurückgenommen werden; für visuell orientierte Betrachter sollen **beide** AGVs im Shopfloor- und Orders-Kontext erkennbar sein (auch wenn die Order-Route orange bleiben kann und AGV-1 orange ist).

**Änderung:**

- **AGV-1** nutzt **`agv1`** (orange), **AGV-2** nutzt **`agv2`** (warmes Gelb) über `ShopfloorMappingService.getAgvColor()` (Index 0 vs. ≥1).
- **Shopfloor-Tab** und **aktive** Order-Cards zeigen **mehrere FTS-Positionen** (`ftsPositions`), nicht nur ein einzelnes Highlight.
- **Review-Fixture:** `production_blue_dual_agv_step15` / Preset `order-production-blue-dual-agv-step15` – Production BLUE, bis ca. Schritt 15, zwei aktive Orders mit **5iO4** und **leJ4** sichtbar; in **Shopfloor-**, **Orders-** und **AGV-Tab** wählbar.

**Begründung:** Zweifarbigkeit verbessert die Unterscheidbarkeit bei zwei Fahrzeugen; die Order-Route kann weiterhin orange dominieren – Nutzerakzeptanz wurde explizit für diese Überlappung bestätigt.

---

## Amendment (2026-03-30b) – Route & Position: beide AGVs + Gateway `fts$`

**Kontext:** Im AGV-Tab (**Route & Position**, inkl. **Presentation**/URL) sollen **beide AGVs und ihre Routen** angezeigt werden, sobald für beide Serien die nötigen Infos vorliegen. In der Dual-Route-Demo erschien teils nur **ein** Fahrzeug, obwohl zwei Routen gezeichnet wurden: `ftsStates$` wurde durch in den FTS-Stream gemischte **`fts/.../order`**-Nachrichten überschrieben (Order-Payload ohne brauchbaren `lastNodeId`).

**Änderung:**

1. **Gateway (`@osf/gateway`):** `fts$` verarbeitet nur noch Topics, die mit **`/state`** enden (kein **`/order`**, kein **`/instantAction`** im gleichen Stream).
2. **AGV-Tab:** Positionsermittlung pro Layout-AGV primär aus **`ftsStates$`**; fehlt dort ein gültiger `lastNodeId`, Fallback auf den **MessageMonitor**-Letztwert je Topic **`fts/v1/ff/<serial>/state`**. **Presentation** nutzt `app-agv-tab` und erhält dasselbe Verhalten.

**Abweichung von älteren Formulierungen im DR:** Für die kombinierte Kartenansicht Route & Position / Presentation gilt nicht mehr „faktisch nur ein Fahrzeug sichtbar“, sondern: **beide AGVs**, sobald Telemetrie für beide existiert.
