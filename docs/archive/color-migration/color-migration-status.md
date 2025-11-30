# ORBIS CI Farbpalette - Migrationsstatus

## ✅ Abgeschlossen (Phase 1)

### Ersetzte Farben
- ✅ `#64a70b` → `var(--highlight-green-strong)` - ORBIS Detail Component
- ✅ `#bbde87` → `var(--highlight-green-light)` - ORBIS Detail Component  
- ✅ `#009681` → `var(--solution-petrol-strong)` - DSP Architecture & Detail
- ✅ `#8fccc4` → `var(--solution-petrol-light)` - DSP Architecture
- ✅ `#f97316` → `var(--shopfloor-highlight-strong)` - Shopfloor Preview, App Component, Tabs
- ✅ `#fb923c` → `var(--shopfloor-highlight-medium)` - App Component Gradient

### Neue Farbdefinitionen hinzugefügt
- ✅ Shopfloor Highlight Orange (strong/medium/light) zur Palette hinzugefügt
- ✅ Schriftfarbe auf `var(--orbis-darkgrey)` angepasst

## ⚠️ Noch zu erledigen (Phase 2 - Ähnliche Farben)

### Häufigste noch hart-codierte Farben

1. **`#1f54b2`** (13+ Vorkommen) - Blau für Links/Buttons
   - **ORBIS CI**: `#154194` (orbis-blue-strong)
   - **Unterschied**: Etwas heller/gesättigter
   - **Status**: ⚠️ Sollte durch `var(--orbis-blue-strong)` ersetzt werden
   - **Dateien**: app.component.scss, dsp-detail.component.scss, dsp-architecture.component.scss, tabs/*.scss

2. **`#0f325c`** (11 Vorkommen) - Sehr dunkles Blau für Überschriften
   - **ORBIS CI**: `#16203b` (orbis-nightblue)
   - **Unterschied**: Sehr ähnlich, minimal heller
   - **Status**: ⚠️ Sollte durch `var(--orbis-nightblue)` ersetzt werden

3. **`#1f2933`** (6 Vorkommen) - Sehr dunkles Grau für Text
   - **ORBIS CI**: `#1c1c1c` (orbis-darkgrey)
   - **Unterschied**: Sehr ähnlich
   - **Status**: ⚠️ Sollte durch `var(--orbis-darkgrey)` ersetzt werden

## ⚠️ Noch zu erledigen (Phase 3 - Grautöne)

### Grautöne für sekundären Text

4. **`#5b6d84`, `#526480`, `#52606d`, `#4b627c`** (4-6 Vorkommen)
   - **ORBIS CI**: `#a7a8aa` (orbis-grey-strong), `#bbbcbc` (orbis-grey-medium)
   - **Status**: ⚠️ Kontextabhängig durch ORBIS Grey ersetzen
   - **Verwendung**: Sekundärer Text, Beschreibungen

5. **`#6b7280`** (9 Vorkommen) - Neutrales Grau
   - **Status**: ⚠️ Könnte durch `var(--orbis-grey-strong)` ersetzt werden

## ✅ OK - Bleibt wie es ist

- **`#ffffff`** (8 Vorkommen) - Weiß
  - Standard-Farbe, kann bleiben
  - Optional: Als `--color-white` definieren

- **`#000000`** - Schwarz
  - Standard-Farbe, kann bleiben

## ❓ Zu prüfen - Nicht in ORBIS CI

- **`#b91c1c`** (3 Vorkommen) - Rot
- **`#dc2626`** (3 Vorkommen) - Rot
- **`#047857`** (2 Vorkommen) - Grün
- **`#b45309`** (2 Vorkommen) - Orange/Braun
- **`#4b5563`** (3 Vorkommen) - Grau
- **`#475569`** (3 Vorkommen) - Grau

**Frage**: Sollen diese durch ORBIS CI Farben ersetzt werden oder bleiben sie als Status-Farben (z.B. Error, Success)?

## Zusammenfassung

### Status: ~40% abgeschlossen

- ✅ **Phase 1**: Abgeschlossen (Highlight Green, Solution Petrol, Shopfloor Highlight)
- ⚠️ **Phase 2**: Noch offen (~30 Vorkommen von #1f54b2, #0f325c, #1f2933)
- ⚠️ **Phase 3**: Noch offen (~20 Vorkommen von Grautönen)

### Empfehlung

**Ja, weitere Anpassungen sind sinnvoll**, um vollständige ORBIS CI Konformität zu erreichen:

1. **Phase 2 durchführen**: Die häufigsten Farben (#1f54b2, #0f325c, #1f2933) ersetzen
2. **Phase 3 durchführen**: Grautöne kontextabhängig ersetzen
3. **Status-Farben klären**: Entscheidung über Error/Success/Warning Farben

### Nächste Schritte

1. Phase 2: #1f54b2 → var(--orbis-blue-strong) (mit visueller Prüfung)
2. Phase 2: #0f325c → var(--orbis-nightblue)
3. Phase 2: #1f2933 → var(--orbis-darkgrey)
4. Phase 3: Grautöne kontextabhängig ersetzen

