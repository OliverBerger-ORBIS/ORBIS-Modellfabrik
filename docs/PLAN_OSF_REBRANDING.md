# Plan: OSF Rebranding (Task 13)

## Status
🔄 In Planung

## Ziel
Umbenennung von **OMF3 → OSF** und **ccu-ui → osf-ui** durch den gesamten Workspace, inkl. Code, Assets, Dokumentation, Git-Verwaltung.

## Scope

### 1. App-Umbenennung: `ccu-ui` → `osf-ui`
- [ ] **Verzeichnis umbenennen**: `omf3/apps/ccu-ui/` → `omf3/apps/osf-ui/`
- [ ] **project.json**: `name: "ccu-ui"` → `name: "osf-ui"`
- [ ] **Build-Pfade**: `dist/apps/ccu-ui` → `dist/apps/osf-ui`
- [ ] **Nx-Befehle**: `nx serve ccu-ui` → `nx serve osf-ui`
- [ ] **package.json Scripts**: `test:ccu-ui` → `test:osf-ui`
- [ ] **GitHub Actions**: Workflows anpassen (`.github/workflows/*.yml`)
- [ ] **CI/CD**: Alle Referenzen in CI-Pipelines aktualisieren

### 2. Workspace-Umbenennung: `omf3` → `osf`
- [ ] **Verzeichnis**: `omf3/` → `osf/` (ODER: Bezeichnung in Code/Doku, Verzeichnis bleibt?)
- [ ] **Nx Scope**: `nx.json` → `"npmScope": "omf3"` → `"npmScope": "osf"`
- [ ] **TypeScript Paths**: `tsconfig.base.json` → `@omf3/*` → `@osf/*`
- [ ] **Import-Statements**: Alle `@omf3/` Imports → `@osf/`
- [ ] **Library-Namen**: `omf3/libs/*` → `osf/libs/*` (wenn Verzeichnis umbenannt)

### 3. Komponenten-Umbenennung
- [ ] **module-tab** → **shopfloor-tab** (bereits teilweise gemacht, konsolidieren)
  - [ ] `module-tab.component.ts` → `shopfloor-tab.component.ts`
  - [ ] Route: `path: 'module'` → `path: 'shopfloor'`
  - [ ] Alle Referenzen in Code/Doku
- [ ] **fts-tab** → **agv-tab**
  - [ ] `fts-tab.component.ts` → `agv-tab.component.ts`
  - [ ] Route: `path: 'fts'` → `path: 'agv'`
  - [ ] `FtsTabComponent` → `AgvTabComponent`
  - [ ] Services: `fts-route.service.ts` → `agv-route.service.ts`
  - [ ] Services: `fts-animation.service.ts` → `agv-animation.service.ts`
  - [ ] Components: `fts-view.component.ts` → `agv-view.component.ts`
  - [ ] Tests: `fts-tab.component.spec.ts` → `agv-tab.component.spec.ts`
  - [ ] **WICHTIG**: FTS bleibt in:
    - MQTT Topics (extern vorgegeben): `ccu/order/fts`, etc.
    - Deutsche Übersetzungen: "FTS" als Label bleibt
    - Nur Code-Namen werden zu "agv"

### 4. Bezeichner: OMF3 → OSF
- [ ] **Code-Kommentare**: Alle `OMF3` → `OSF`
- [ ] **Dokumentation**: Alle `OMF3` → `OSF` in `docs/`
- [ ] **README.md**: `omf3/README.md` → `osf/README.md` (wenn Verzeichnis umbenannt)
- [ ] **package.json**: `"name": "omf3-workspace"` → `"name": "osf-workspace"`
- [ ] **Angular Prefix**: `project.json` → `"prefix": "app"` → `"prefix": "osf"` (optional, prüfen)
- [ ] **ENV Variablen**: Alle `OMF3_*` → `OSF_*` (falls vorhanden)

### 5. Dokumentation
- [ ] **README.md**: Haupt-README aktualisieren
- [ ] **docs/**: Alle Dokumente durchsuchen und aktualisieren
- [ ] **.cursorrules**: `OMF3` → `OSF` in Regeln
- [ ] **CHANGELOG.md**: Eintrag für Rebranding
- [ ] **PROJECT_STATUS.md**: Task 13 als erledigt markieren

### 6. Assets & Konfiguration
- [ ] **SVG Icons**: Prüfen ob `omf3` in Pfaden/IDs vorkommt
- [ ] **Build-Konfiguration**: `angular.json` (falls vorhanden)
- [ ] **Jest Config**: `jest.config.ts` Pfade anpassen
- [ ] **ESLint Config**: Pfade/Regeln prüfen

### 7. Git & Repository
- [ ] **Git History**: Prüfen ob Umbenennung History erhält
- [ ] **Git Submodules**: Prüfen ob betroffen
- [ ] **GitHub Repository**: Beschreibung/Tags aktualisieren (optional)

## Vorgehen

### Phase 1: Analyse & Vorbereitung
1. ✅ Vollständige Codebase-Suche nach `OMF3`, `omf3`, `ccu-ui`, `fts-tab`, `module-tab`
2. ✅ Liste aller betroffenen Dateien erstellen
3. ✅ Backup/Commit vor Änderungen
4. ✅ Test-Suite sicherstellen (alle Tests müssen bestehen)

### Phase 2: Code-Änderungen (atomar)
1. **Import-Pfade**: `@omf3/*` → `@osf/*` (tsconfig.base.json + alle Imports)
2. **Nx Scope**: `nx.json` → `npmScope: "osf"`
3. **Komponenten**: `fts-tab` → `agv-tab` (Dateien + Referenzen)
4. **Komponenten**: `module-tab` → `shopfloor-tab` (konsolidieren)
5. **App-Name**: `ccu-ui` → `osf-ui` (project.json, Scripts, CI)

### Phase 3: Verzeichnis-Umbenennung (falls gewünscht)
⚠️ **Entscheidung nötig**: Soll `omf3/` Verzeichnis umbenannt werden?
- **Option A**: Verzeichnis bleibt `omf3/`, nur Bezeichner in Code/Doku ändern
- **Option B**: Verzeichnis umbenennen zu `osf/` (aufwändiger, aber konsistenter)

**Empfehlung**: Option A (weniger Risiko, Git-History bleibt erhalten)

### Phase 4: Dokumentation
1. Alle `docs/` Dateien durchsuchen
2. README.md aktualisieren
3. .cursorrules aktualisieren
4. CHANGELOG.md Eintrag

### Phase 5: CI/CD & Build
1. GitHub Actions Workflows anpassen
2. Build-Scripts testen
3. Deployment-Pfade prüfen

### Phase 6: Tests & Validierung
1. ✅ Alle Tests müssen bestehen
2. ✅ Linting muss bestehen
3. ✅ Build muss funktionieren
4. ✅ Manuelle UI-Tests (Navigation, Tabs, etc.)

## Risiken & Herausforderungen

### ⚠️ Breaking Changes
- **Git History**: Verzeichnis-Umbenennung kann History beeinflussen
- **CI/CD**: Workflows müssen synchron aktualisiert werden
- **Dependencies**: Externe Abhängigkeiten könnten betroffen sein

### ⚠️ Komplexität
- **Viele Dateien**: ~87 Dateien mit `OMF3`/`omf3`, ~52 mit `ccu-ui`
- **Import-Ketten**: Änderung eines Imports kann viele Dateien betreffen
- **Tests**: Alle Tests müssen nach Änderungen bestehen

### ⚠️ FTS vs AGV
- **MQTT Topics**: MÜSSEN `fts` bleiben (extern vorgegeben)
- **Deutsche Übersetzungen**: "FTS" als Label bleibt
- **Nur Code**: Komponenten-Namen werden zu `agv`

## Empfohlene Reihenfolge

1. **Kleinste Änderungen zuerst** (weniger Risiko):
   - Kommentare, Dokumentation
   - Bezeichner in Code (OMF3 → OSF)
2. **Import-Pfade** (`@omf3/*` → `@osf/*`)
3. **Komponenten** (`fts-tab` → `agv-tab`, `module-tab` → `shopfloor-tab`)
4. **App-Name** (`ccu-ui` → `osf-ui`)
5. **Verzeichnis** (falls gewünscht, zuletzt)

## Checkliste für jeden Schritt

- [ ] Datei geändert
- [ ] Tests lokal ausgeführt
- [ ] Linting bestanden
- [ ] Build erfolgreich
- [ ] Git-Commit erstellt
- [ ] Dokumentation aktualisiert

## Nächste Schritte

1. ✅ Plan erstellt
2. ⏳ User-Freigabe für Plan
3. ⏳ Phase 1: Analyse (bereits gemacht)
4. ⏳ Phase 2: Code-Änderungen
5. ⏳ Phase 3-6: Restliche Phasen

## Referenzen

- [SemVer Decision Record](docs/03-decision-records/15-semver-versioning.md)
- [Project Structure](docs/02-architecture/project-structure.md)
- Task 13 in [PROJECT_STATUS.md](docs/PROJECT_STATUS.md)
