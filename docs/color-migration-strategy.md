# Color Migration Strategy - ORBIS CI Palette

## Analyse der häufigsten hart-codierten Farbwerte

Basierend auf einer Analyse des Codes wurden folgende häufig verwendete Farbwerte identifiziert:

### Häufigste Farbwerte (Top 10)

1. **`#1f54b2`** (13+ Vorkommen) - Blau
   - **Aktueller ORBIS-Wert**: `#154194` (orbis-blue-strong)
   - **Unterschied**: `#1f54b2` ist etwas heller/gesättigter
   - **Empfehlung**: 
     - Option A: Durch `orbis-blue-strong` (`#154194`) ersetzen (CI-konform)
     - Option B: Als neue Variable `orbis-blue-accent` hinzufügen, falls der Unterschied visuell wichtig ist
   - **Verwendung**: Primär für Links, Buttons, Akzente

2. **`#0f325c`** (11 Vorkommen) - Sehr dunkles Blau
   - **Aktueller ORBIS-Wert**: `#16203b` (orbis-nightblue) - sehr ähnlich
   - **Empfehlung**: Durch `orbis-nightblue` ersetzen
   - **Verwendung**: Überschriften, dunkle Textfarben

3. **`#ffffff`** (8 Vorkommen) - Weiß
   - **Status**: Standard, kann bleiben oder als Variable definiert werden
   - **Empfehlung**: Optional als `--color-white` definieren

4. **`#1f2933`** (6 Vorkommen) - Sehr dunkles Grau
   - **Aktueller ORBIS-Wert**: `#1c1c1c` (orbis-darkgrey) - sehr ähnlich
   - **Empfehlung**: Durch `orbis-darkgrey` ersetzen
   - **Verwendung**: Text, Überschriften

5. **`#5b6d84`, `#526480`, `#52606d`, `#4b627c`** (4-6 Vorkommen) - Grautöne
   - **Aktueller ORBIS-Wert**: `#a7a8aa` (orbis-grey-strong), `#bbbcbc` (orbis-grey-medium)
   - **Empfehlung**: Prüfen, ob diese durch `orbis-grey-strong` oder `orbis-grey-medium` ersetzt werden können
   - **Verwendung**: Sekundärer Text, Beschreibungen

6. **`#64a70b`** (bereits in Palette) - Highlight Green
   - **Status**: Bereits als `highlight-green-strong` definiert
   - **Empfehlung**: Durch Variable ersetzen

7. **`#bbde87`** (bereits in Palette) - Highlight Green Light
   - **Status**: Bereits als `highlight-green-light` definiert
   - **Empfehlung**: Durch Variable ersetzen

8. **`#009681`** (bereits in Palette) - Solution Petrol
   - **Status**: Bereits als `solution-petrol-strong` definiert
   - **Empfehlung**: Durch Variable ersetzen

## Migrationsstrategie

### Phase 1: Offensichtliche Ersetzungen (Niedriges Risiko)
- ✅ `#64a70b` → `var(--highlight-green-strong)`
- ✅ `#bbde87` → `var(--highlight-green-light)`
- ✅ `#009681` → `var(--solution-petrol-strong)`
- ✅ `#154194` → `var(--orbis-blue-strong)` (falls vorhanden)

### Phase 2: Ähnliche Farben (Mittleres Risiko - visuelle Prüfung nötig)
- ⚠️ `#1f54b2` → `var(--orbis-blue-strong)` (#154194)
  - **Aktion**: Visuell prüfen, ob der Unterschied akzeptabel ist
  - **Alternative**: Neue Variable `orbis-blue-accent` hinzufügen
- ⚠️ `#0f325c` → `var(--orbis-nightblue)` (#16203b)
- ⚠️ `#1f2933` → `var(--orbis-darkgrey)` (#1c1c1c)

### Phase 3: Grautöne (Niedriges Risiko)
- ⚠️ Grautöne (`#5b6d84`, `#526480`, etc.) → `var(--orbis-grey-strong)` oder `var(--orbis-grey-medium)`
  - **Aktion**: Kontextabhängig ersetzen

## Empfehlung

**Ja, die Migration ist ein geschickter Ansatz**, weil:
1. ✅ Konsistenz mit ORBIS CI
2. ✅ Einfache Wartbarkeit (zentrale Farbdefinition)
3. ✅ Einfache Anpassung bei CI-Änderungen
4. ✅ Bessere Lesbarkeit des Codes

**Vorgehen**:
1. Schrittweise Migration (Phase 1 → Phase 2 → Phase 3)
2. Nach jeder Phase visuell prüfen
3. Tests durchführen
4. Dokumentation aktualisieren

## Farb-Mapping Tabelle

| Hart-codiert | ORBIS CI Variable | RGB-Äquivalent | Status |
|-------------|-------------------|----------------|--------|
| `#1f54b2` | `--orbis-blue-strong` | `22, 65, 148` | ⚠️ Prüfen |
| `#0f325c` | `--orbis-nightblue` | `22, 32, 59` | ⚠️ Prüfen |
| `#1f2933` | `--orbis-darkgrey` | `28, 28, 28` | ⚠️ Prüfen |
| `#64a70b` | `--highlight-green-strong` | `100, 167, 11` | ✅ Direkt |
| `#bbde87` | `--highlight-green-light` | `187, 222, 143` | ✅ Direkt |
| `#009681` | `--solution-petrol-strong` | `0, 150, 129` | ✅ Direkt |
| `#154194` | `--orbis-blue-strong` | `22, 65, 148` | ✅ Direkt |

## Nächste Schritte

1. **Phase 1 starten**: Offensichtliche Ersetzungen durchführen
2. **Visuelle Prüfung**: Screenshots vor/nach Vergleich
3. **Phase 2**: Ähnliche Farben mit visueller Prüfung
4. **Phase 3**: Grautöne kontextabhängig ersetzen

