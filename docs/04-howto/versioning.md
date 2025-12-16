# HowTo: Versionierung

## Übersicht

Das OMF3-Projekt verwendet Semantische Versionierung (SemVer) mit npm. Die Version wird in `package.json` verwaltet und automatisch in Builds injiziert.

## Schnellstart

```bash
# Patch-Version erhöhen (0.3.0 → 0.3.1)
npm run version:patch

# Minor-Version erhöhen (0.3.0 → 0.4.0)
npm run version:minor

# Major-Version erhöhen (0.3.0 → 1.0.0)
npm run version:major
```

## Workflow für ein Release

### 1. Änderungen vorbereiten
```bash
# Alle Änderungen committen
git add -A
git commit -m "feat: Neue ECME-Kundenkonfiguration"
```

### 2. CHANGELOG.md aktualisieren
Fügen Sie Ihre Änderungen zum CHANGELOG.md hinzu:

```markdown
## [Unreleased]

### Added
- ECME-Kundenkonfiguration mit neuen SVG-Icons
- Tests für Label-Umbrüche

## [0.3.0] - 2025-12-14
...
```

### 3. Tests ausführen
```bash
npm test
# Oder spezifisch für ccu-ui:
npm run test:ccu-ui
```

### 4. Version erhöhen
```bash
# Für Bugfixes/kleine Änderungen:
npm run version:patch

# Für neue Features:
npm run version:minor

# Für Breaking Changes:
npm run version:major
```

Das Script:
- ✅ Erhöht die Version in `package.json`
- ✅ Erstellt einen Git-Commit mit der neuen Version
- ✅ Erstellt einen Git-Tag (`v0.3.1`)
- ✅ Pusht automatisch Commit und Tag

### 5. GitHub Release
GitHub Actions erstellt automatisch ein Release, wenn ein Version-Tag gepusht wird:
- Release-Name: `OMF3 Dashboard 0.3.1`
- Release-Asset: `omf3-0.3.1.tar.gz`
- Link zu CHANGELOG.md

## Wann welche Version?

### Patch (0.3.0 → 0.3.1)
Verwenden Sie Patch für:
- Bugfixes
- Kleine UI-Verbesserungen
- Dokumentations-Updates
- Test-Verbesserungen
- Code-Refactoring ohne Funktionsänderung

**Beispiel:**
```bash
npm run version:patch
# Erstellt: v0.3.1
```

### Minor (0.3.0 → 0.4.0)
Verwenden Sie Minor für:
- Neue Features
- Neue Kundenkonfigurationen
- Neue SVG-Icons
- Neue DSP-Animation-Features
- I18n-Erweiterungen
- Neue Komponenten

**Beispiel:**
```bash
npm run version:minor
# Erstellt: v0.4.0
```

### Major (0.3.0 → 1.0.0)
Verwenden Sie Major für:
- Breaking Changes in APIs
- Große Architektur-Änderungen
- Inkompatible Änderungen an Config-Strukturen
- Entfernung von Features

**Beispiel:**
```bash
npm run version:major
# Erstellt: v1.0.0
```

## Version im Code verwenden

Die Version wird automatisch während des Builds in `omf3/apps/ccu-ui/src/environments/version.ts` injiziert:

```typescript
import { VERSION } from '../environments/version';

console.log(VERSION.full);      // "0.3.0"
console.log(VERSION.build);     // "main-abc123"
console.log(VERSION.buildDate); // "2025-12-16T12:00:00Z"
```

## Best Practices

1. ✅ **CHANGELOG.md immer aktualisieren** vor dem Versionieren
2. ✅ **Tests müssen bestehen** vor dem Versionieren
3. ✅ **Nur auf main branch** versionieren
4. ✅ **Pre-commit Hooks** werden automatisch ausgeführt
5. ✅ **Keine Versionsänderungen in Feature-Branches**

## Troubleshooting

### Version wurde nicht erhöht
```bash
# Prüfen Sie package.json
cat package.json | grep version

# Prüfen Sie Git-Tags
git tag | tail -5
```

### Release wurde nicht erstellt
- Prüfen Sie GitHub Actions: `.github/workflows/release.yml`
- Prüfen Sie, ob der Tag korrekt gepusht wurde: `git push --tags`

### Version wird nicht im Build angezeigt
- Prüfen Sie `omf3/apps/ccu-ui/src/environments/version.ts`
- Die Datei wird nur während GitHub Actions Build erstellt
- Lokal zeigt sie Test-Werte

## Weitere Informationen

- Siehe [Decision Record: Semver Versioning](../03-decision-records/15-semver-versioning.md)
- [SemVer Specification](https://semver.org/)
- [npm version Documentation](https://docs.npmjs.com/cli/v9/commands/npm-version)
