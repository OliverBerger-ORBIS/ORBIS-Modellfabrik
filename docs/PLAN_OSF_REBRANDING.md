# Plan: OSF Rebranding (Task 13)

## Status
✅ **~95% erledigt** - Hauptaufgaben abgeschlossen, optional: weitere Dokumentation durchsehen

## Ziel
Umbenennung von **OMF3 → OSF** und **ccu-ui → osf-ui** durch den gesamten Workspace, inkl. Code, Assets, Dokumentation, Git-Verwaltung.

## Scope

### 1. App-Umbenennung: `ccu-ui` → `osf-ui`
- [x] **Verzeichnis umbenennen**: `omf3/apps/ccu-ui/` → `osf/apps/osf-ui/`
- [x] **project.json**: `name: "osf-ui"`
- [x] **Build-Pfade**: `dist/apps/osf-ui`
- [x] **Nx-Befehle**: `nx serve osf-ui`
- [x] **package.json Scripts**: `test:osf-ui`
- [x] **GitHub Actions**: Workflows angepasst (`.github/workflows/*.yml`)
- [x] **CI/CD**: Alle Referenzen in CI-Pipelines aktualisiert

### 2. Workspace-Umbenennung: `omf3` → `osf`
- [x] **Verzeichnis**: `omf3/` → `osf/` (Option B: Verzeichnis umbenannt)
- [x] **Nx Scope**: `nx.json` → `"npmScope": "osf"`
- [x] **TypeScript Paths**: `tsconfig.base.json` → `@osf/*`
- [x] **Import-Statements**: Alle `@osf/` Imports
- [x] **Library-Namen**: `osf/libs/*`

### 3. Komponenten-Umbenennung
- [x] **module-tab** → **shopfloor-tab** (vollständig erledigt)
  - [x] `shopfloor-tab.component.ts` (und .html, .scss, .spec.ts)
  - [x] Route: `path: 'shopfloor'`
  - [x] Klasse: `ShopfloorTabComponent`
  - [x] Selector: `app-shopfloor-tab`
  - [x] CSS-Klassen: `.shopfloor-tab`, `.shopfloor-table`
  - [x] Storage Keys aktualisiert
  - [x] Tests aktualisiert
  - [x] Fixtures aktualisiert
  - [x] DSP-Architektur-Komponenten URLs aktualisiert
  - [x] Tabellen-Header: "Modules" (zurück geändert)
  - [x] UI-Label: "Shopfloor" (Navigation)
- [x] **fts-tab** → **agv-tab**
  - [x] `agv-tab.component.ts`
  - [x] Route: `path: 'agv'`
  - [x] `AgvTabComponent`
  - [x] Services: `agv-route.service.ts`, `agv-animation.service.ts`
  - [x] Tests: `agv-tab.component.spec.ts`
  - [x] **WICHTIG**: FTS bleibt in:
    - MQTT Topics (extern vorgegeben): `ccu/order/fts`, etc.
    - Deutsche Übersetzungen: "FTS" als Label bleibt
    - Nur Code-Namen werden zu "agv"

### 4. Bezeichner: OMF3 → OSF
- [x] **Code-Kommentare**: Alle `OMF3` → `OSF`
- [ ] **Dokumentation**: Alle `OMF3` → `OSF` in `docs/` (15 Dateien noch offen)
- [x] **README.md**: `osf/README.md`
- [x] **package.json**: `"name": "osf-workspace"` (aktualisiert)
- [ ] **Angular Prefix**: `project.json` → `"prefix": "app"` → `"prefix": "osf"` (optional, noch nicht geprüft)
- [ ] **ENV Variablen**: Alle `OMF3_*` → `OSF_*` (falls vorhanden, noch nicht geprüft)

### 5. Dokumentation
- [x] **README.md**: Haupt-README aktualisiert
- [ ] **docs/**: Alle Dokumente durchsuchen und aktualisieren (15 Dateien noch offen)
- [x] **.cursorrules**: `OSF` in Regeln aktualisiert
- [x] **CHANGELOG.md**: Eintrag für Rebranding vorhanden
- [ ] **PROJECT_STATUS.md**: Task 13 Status prüfen (noch nicht als erledigt markiert)

### 6. Assets & Konfiguration
- [x] **SVG Icons**: Prüfen ob `omf3` in Pfaden/IDs vorkommt (nicht gefunden)
- [x] **Build-Konfiguration**: Alle Pfade aktualisiert
- [x] **Jest Config**: `jest.config.ts` Pfade angepasst
- [x] **ESLint Config**: Pfade/Regeln aktualisiert

### 7. Git & Repository
- [x] **Git History**: Umbenennung mit `git mv` durchgeführt (History erhalten)
- [x] **Git Submodules**: Nicht betroffen
- [ ] **GitHub Repository**: Beschreibung/Tags aktualisieren (optional, noch nicht gemacht)

## Vorgehen

### Phase 1: Analyse & Vorbereitung
1. ✅ Vollständige Codebase-Suche nach `OMF3`, `omf3`, `ccu-ui`, `fts-tab`, `module-tab`
2. ✅ Liste aller betroffenen Dateien erstellen
3. ✅ Backup/Commit vor Änderungen
4. ✅ Test-Suite sicherstellen (alle Tests müssen bestehen)

### Phase 2: Code-Änderungen (atomar)
1. [x] **Import-Pfade**: `@omf3/*` → `@osf/*` (tsconfig.base.json + alle Imports)
2. [x] **Nx Scope**: `nx.json` → `npmScope: "osf"`
3. [x] **Komponenten**: `fts-tab` → `agv-tab` (Dateien + Referenzen)
4. [x] **Komponenten**: `module-tab` → `shopfloor-tab` (vollständig erledigt)
5. [x] **App-Name**: `ccu-ui` → `osf-ui` (project.json, Scripts, CI)

### Phase 3: Verzeichnis-Umbenennung (falls gewünscht)
✅ **Entscheidung getroffen**: Option B gewählt - `omf3/` Verzeichnis wurde zu `osf/` umbenannt
- [x] Verzeichnis umbenannt: `omf3/` → `osf/`
- [x] Git History erhalten (mit `git mv`)

### Phase 4: Dokumentation
1. [ ] Alle `docs/` Dateien durchsuchen (15 Dateien noch offen)
2. [x] README.md aktualisiert
3. [x] .cursorrules aktualisiert
4. [x] CHANGELOG.md Eintrag vorhanden

### Phase 5: CI/CD & Build
1. [x] GitHub Actions Workflows angepasst
2. [x] Build-Scripts getestet
3. [x] Deployment-Pfade geprüft

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
2. ✅ User-Freigabe für Plan erhalten
3. ✅ Phase 1: Analyse abgeschlossen
4. ✅ Phase 2: Code-Änderungen (teilweise: `fts-tab` erledigt, `module-tab` noch offen)
5. ✅ Phase 3: Verzeichnis-Umbenennung abgeschlossen
6. ⏳ Phase 4: Dokumentation (teilweise: 15 Dateien noch offen)
7. ✅ Phase 5: CI/CD & Build abgeschlossen
8. ✅ Phase 6: Tests & Validierung abgeschlossen

## Offene Punkte

1. ✅ **Erledigt:** module-tab → shopfloor-tab vollständig umbenannt

2. ✅ **Erledigt:** package.json name aktualisiert (`osf-workspace`)

3. ✅ **Erledigt:** Wichtigste Dokumentation aktualisiert (project-structure.md, README.md, PROJECT_STATUS.md)

4. ⚠️ **Optional:** Weitere Dokumentation in `docs/` durchsehen (historische Referenzen können bleiben)

5. **Optional**: Angular Prefix und ENV Variablen prüfen

## Referenzen

- [SemVer Decision Record](docs/03-decision-records/15-semver-versioning.md)
- [Project Structure](docs/02-architecture/project-structure.md)
- Task 13 in [PROJECT_STATUS.md](docs/PROJECT_STATUS.md)
