# Decision Record: Semver Versioning

## Status
Accepted

## Context
Das OMF3-Projekt benötigt eine leichtgewichtige Versionierungsstrategie, die:
- Semantische Versionierung (SemVer) verwendet
- Automatisch in Builds integriert wird
- GitHub Releases unterstützt
- Keine komplexe Toolchain erfordert

## Decision
Wir verwenden **npm version** mit SemVer für die Versionierung:

- **Patch** (0.3.0 → 0.3.1): Bugfixes, kleine Verbesserungen
- **Minor** (0.3.0 → 0.4.0): Neue Features, neue Kundenkonfigurationen
- **Major** (0.3.0 → 1.0.0): Breaking Changes

## Implementation

### Version in package.json
Die Version wird in `package.json` im Root-Verzeichnis verwaltet:
```json
{
  "version": "0.3.0"
}
```

### NPM Scripts
```bash
npm run version:patch    # 0.3.0 → 0.3.1
npm run version:minor    # 0.3.0 → 0.4.0
npm run version:major    # 0.3.0 → 1.0.0
```

Diese Scripts:
1. Erhöhen die Version in `package.json`
2. Erstellen einen Git-Commit mit der neuen Version
3. Erstellen einen Git-Tag (`v0.3.1`)
4. Pushen Commit und Tag (via `postversion` hook)

### Automatische Version-Injection
Während des Builds (GitHub Actions) wird die Version automatisch in `osf/apps/osf-ui/src/environments/version.ts` injiziert:

```typescript
export const VERSION = {
  full: '0.3.0',
  build: 'main-abc123',
  buildDate: '2025-12-16T12:00:00Z',
};
```

### GitHub Releases
Bei Push eines Version-Tags (`v*.*.*`) wird automatisch ein GitHub Release erstellt:
- Release-Name: `OMF3 Dashboard {version}`
- Release-Asset: `omf3-{version}.tar.gz`
- Link zu CHANGELOG.md

## Workflow

### Für normale Commits
1. Entwickeln und committen
2. Push zu `main`
3. Keine Versionsänderung nötig

### Für Releases
1. Änderungen committen
2. CHANGELOG.md aktualisieren
3. Version erhöhen:
   ```bash
   npm run version:patch  # oder :minor, :major
   ```
4. Script erstellt automatisch:
   - Commit mit Version
   - Git Tag
   - Push (inkl. Tag)
5. GitHub Actions erstellt automatisch Release

## Wann welche Version?

### Patch (0.3.0 → 0.3.1)
- Bugfixes
- Kleine UI-Verbesserungen
- Dokumentations-Updates
- Test-Verbesserungen

### Minor (0.3.0 → 0.4.0)
- Neue Features
- Neue Kundenkonfigurationen (z.B. ECME)
- Neue SVG-Icons
- Neue DSP-Animation-Features
- I18n-Erweiterungen

### Major (0.3.0 → 1.0.0)
- Breaking Changes in APIs
- Große Architektur-Änderungen
- Inkompatible Änderungen an Config-Strukturen

## Best Practices

1. **CHANGELOG.md aktualisieren** vor dem Versionieren
2. **Tests müssen bestehen** vor dem Versionieren
3. **Pre-commit Hooks** werden automatisch ausgeführt
4. **Version nur auf main** - keine Versionsänderungen in Feature-Branches

## Vorteile

- ✅ Leichtgewichtig: Nur npm, keine zusätzlichen Tools
- ✅ Automatisch: GitHub Actions übernimmt Release-Erstellung
- ✅ Standard: SemVer ist weit verbreitet
- ✅ Integriert: Version wird automatisch in Build injiziert

## Nachteile

- ⚠️ Manuelles Versionieren (kein automatisches Bump)
- ⚠️ CHANGELOG.md muss manuell gepflegt werden

## Alternatives Considered

1. **Conventional Commits + Semantic Release**: Zu komplex für aktuellen Workflow
2. **GitHub Actions mit automatischem Bump**: Erfordert komplexe Workflows
3. **Keine Versionierung**: Nicht geeignet für Releases

## References

- [SemVer Specification](https://semver.org/)
- [npm version](https://docs.npmjs.com/cli/v9/commands/npm-version)
- [GitHub Actions Release Workflow](.github/workflows/release.yml)
