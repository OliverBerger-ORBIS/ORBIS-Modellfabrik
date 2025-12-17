# Module Analysis Summary

Diese Datei enthält aggregierte Statistiken aus allen Modul-Analysen (HBW, DRILL, MILL, DPS, AIQS).

**Erstellt:** 1765991251.5199885
**Sessions analysiert:** 13 Session-Log-Dateien

## Übersicht

| Modul | Serial | Sessions | Module-Messages | Operations | Haupt-Commands |
|-------|--------|----------|-----------------|-----------|----------------|
| HBW | SVR3QA0022 | 13 | 2169 | 45 | DROP(24), PICK(21), factsheetRequest(2) |
| DRILL | SVR4H76449 | 13 | 2182 | 55 | DROP(22), DRILL(18), PICK(15) |
| MILL | SVR3QA2098 | 13 | 2173 | 45 | DROP(18), PICK(14), MILL(13) |
| DPS | SVR4H73275 | 13 | 11630 | 0 | DROP(61), PICK(60), startCalibration(45) |
| AIQS | SVR4H76530 | 13 | 9843 | 53 | CHECK_QUALITY(53), DROP(18), PICK(16) |

## Detaillierte Statistiken

### HBW (Serial: SVR3QA0022)

- **Sessions analysiert:** 13
- **Gesamt-Messages (alle Sessions):** 13642
- **HBW-relevante Messages:** 2169
- **Operations gefunden:** 45
- **Order-Context Messages:** 98

**Commands gefunden:**
- `DROP`: 24x
- `PICK`: 21x
- `factsheetRequest`: 2x

### DRILL (Serial: SVR4H76449)

- **Sessions analysiert:** 13
- **Gesamt-Messages (alle Sessions):** 13642
- **DRILL-relevante Messages:** 2182
- **Operations gefunden:** 55
- **Order-Context Messages:** 139

**Commands gefunden:**
- `DROP`: 22x
- `DRILL`: 18x
- `PICK`: 15x
- `factsheetRequest`: 2x

### MILL (Serial: SVR3QA2098)

- **Sessions analysiert:** 13
- **Gesamt-Messages (alle Sessions):** 13642
- **MILL-relevante Messages:** 2173
- **Operations gefunden:** 45
- **Order-Context Messages:** 139

**Commands gefunden:**
- `DROP`: 18x
- `PICK`: 14x
- `MILL`: 13x
- `factsheetRequest`: 2x

### DPS (Serial: SVR4H73275)

- **Sessions analysiert:** 13
- **Gesamt-Messages (alle Sessions):** 13642
- **DPS-relevante Messages:** 11630
- **Operations gefunden:** 0
- **Order-Context Messages:** 423

**Commands gefunden:**
- `DROP`: 61x
- `PICK`: 60x
- `startCalibration`: 45x
- `RGB_NFC`: 21x
- `INPUT_RGB`: 18x
- `factsheetRequest`: 11x
- `reset`: 2x

### AIQS (Serial: SVR4H76530)

- **Sessions analysiert:** 13
- **Gesamt-Messages (alle Sessions):** 13642
- **AIQS-relevante Messages:** 9843
- **Operations gefunden:** 53
- **Order-Context Messages:** 1113

**Commands gefunden:**
- `CHECK_QUALITY`: 53x
- `DROP`: 18x
- `PICK`: 16x
- `factsheetRequest`: 9x

## Nächste Schritte

Diese Daten werden verwendet, um:
1. Modul-spezifische Beispiel-Anwendungen zu entwickeln
2. Status-Visualisierungen zu erstellen
3. Command-History-Features zu implementieren
4. Integration in OMF3 Module-Tab vorzubereiten

## Verwandte Dokumentation

- [DPS Analysis README](./dps-analysis/README.md)
- [AIQS Analysis README](./aiqs-analysis/README.md)
- [HBW Analysis README](./hbw-analysis/README.md)
- [DRILL Analysis README](./drill-analysis/README.md)
- [MILL Analysis README](./mill-analysis/README.md)
- [GitHub Requirement](./GITHUB_REQUIREMENT.md)
