# Task 5: Konfigurations-Tab Layout - Plan

## Anforderung
Shopfloor-Layout links, Module rechts; bei kleiner Breite Modulbereich nach unten umbrechen (CSS Grid/Flex + Angular Breakpoints). Diese Vorgehen soll für alle Tabs gelten, bei denen wir shopfloor-Layout verwenden.

## Aktuelle Situation

### Configuration-Tab
- **Struktur:** Shopfloor oben, Detail-Panel darunter (vertikal)
- **HTML:** `.shopfloor-wrapper` → `.detail-panel`
- **CSS:** Beide in separaten Blöcken, keine Grid-Struktur

### Module-Tab (Shopfloor-Tab)
- **Struktur:** Shopfloor und Selected Module Card in Grid
- **HTML:** `.module-tab__shopfloor-grid` mit `repeat(auto-fit, minmax(320px, 1fr))`
- **Status:** Bereits Grid, aber nicht optimal (auto-fit kann beide nebeneinander oder untereinander anzeigen)

### FTS-Tab
- **Struktur:** Bereits 3-Spalten-Grid (1fr 2fr 1fr)
- **Breakpoints:** @media (max-width: 1200px) → 2 Spalten, @media (max-width: 768px) → 1 Spalte
- **Status:** ✅ Bereits gut implementiert, könnte als Referenz dienen

## Implementierungsplan

### 1. Configuration-Tab umstrukturieren

**HTML-Änderungen:**
- `.shopfloor-wrapper` und `.detail-panel` in einen gemeinsamen Container wrappen
- Container mit CSS Grid Klasse versehen (z.B. `.configuration-layout-grid`)

**CSS-Änderungen:**
- CSS Grid implementieren: `grid-template-columns: 2fr 1fr;` (Shopfloor größer als Details)
- Breakpoint bei ~1024px: `grid-template-columns: 1fr;` (vertikal)
- Gap zwischen den Bereichen: `gap: 1.5rem;`

### 2. Module-Tab optimieren

**CSS-Änderungen:**
- Aktuell: `grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));`
- Neu: `grid-template-columns: 2fr 1fr;` für Shopfloor links, Module rechts
- Breakpoint bei ~960px: `grid-template-columns: 1fr;` (vertikal)

### 3. Breakpoint-Standardisierung

**Verwendete Breakpoints im Projekt:**
- `@media (max-width: 768px)` - Mobile
- `@media (max-width: 960px)` - Tablet
- `@media (max-width: 1024px)` - Small Desktop
- `@media (max-width: 1200px)` - Medium Desktop

**Empfehlung:** 1024px als Standard-Breakpoint für Shopfloor-Layout → vertikale Anordnung

### 4. Testing

- Verschiedene Bildschirmgrößen testen
- Prüfen, ob alle Tabs konsistent aussehen
- Mobile-Ansicht prüfen

## Probleme/Potenzielle Herausforderungen

1. **Detail-Panel Höhe:** Bei vertikaler Anordnung könnte das Detail-Panel sehr hoch werden
   - Lösung: Max-height mit Scrollbar oder flexbox mit overflow

2. **Shopfloor Skalierung:** Bei kleiner Breite könnte Shopfloor zu klein werden
   - Lösung: Scale-Anpassung in shopfloor-preview component

3. **Konsistenz:** Alle Tabs sollten das gleiche Breakpoint-Verhalten haben
   - Lösung: Standardisiertes Breakpoint (1024px)
