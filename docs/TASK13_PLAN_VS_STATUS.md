# Task 13: Plan vs. Status Vergleich

**Datum:** 20.12.2025  
**Version:** 0.5.1

## Vergleich: PLAN_OSF_REBRANDING.md vs. TASK13_STATUS_CHECK.md

### ✅ Vollständig erledigt (Plan vs. Status übereinstimmend)

#### 1. App-Umbenennung: `ccu-ui` → `osf-ui`
- ✅ **Verzeichnis umbenannt**: `omf3/apps/ccu-ui/` → `osf/apps/osf-ui/`
- ✅ **project.json**: `name: "osf-ui"`
- ✅ **Build-Pfade**: `dist/apps/osf-ui`
- ✅ **Nx-Befehle**: `nx serve osf-ui`
- ✅ **package.json Scripts**: `test:osf-ui`
- ✅ **GitHub Actions**: Alle Workflows aktualisiert
- ✅ **CI/CD**: Alle Referenzen aktualisiert

#### 2. Workspace-Umbenennung: `omf3` → `osf`
- ✅ **Verzeichnis**: `omf3/` → `osf/` (Option B gewählt)
- ✅ **Nx Scope**: `nx.json` → `"npmScope": "osf"`
- ✅ **TypeScript Paths**: `tsconfig.base.json` → `@osf/*`
- ✅ **Import-Statements**: Alle `@osf/` Imports
- ✅ **Library-Namen**: `osf/libs/*`

#### 3. Komponenten-Umbenennung: `fts-tab` → `agv-tab`
- ✅ `agv-tab.component.ts`
- ✅ Route: `path: 'agv'`
- ✅ `AgvTabComponent`
- ✅ Services: `agv-route.service.ts`, `agv-animation.service.ts`
- ✅ Tests: `agv-tab.component.spec.ts`
- ✅ FTS bleibt in MQTT Topics und deutschen Übersetzungen

#### 4. Bezeichner: OMF3 → OSF (Code)
- ✅ **Code-Kommentare**: `OMF3` → `OSF`
- ✅ **README.md**: `osf/README.md`
- ✅ **.cursorrules**: `OSF` aktualisiert
- ✅ **CHANGELOG.md**: Eintrag vorhanden

#### 5. Assets & Konfiguration
- ✅ **Jest Config**: Pfade angepasst
- ✅ **ESLint Config**: Pfade/Regeln aktualisiert
- ✅ **Build-Konfiguration**: Alle Pfade aktualisiert

#### 6. Git & Repository
- ✅ **Git History**: Umbenennung mit `git mv` durchgeführt
- ✅ **Git Submodules**: Nicht betroffen

---

### ⚠️ Teilweise erledigt / Inkonsistenzen

#### 3. Komponenten-Umbenennung: `module-tab` → `shopfloor-tab`
**Plan:** "bereits teilweise gemacht, konsolidieren"

**Status:**
- ✅ **Vollständig erledigt:**
  - ✅ Datei: `shopfloor-tab.component.ts` (und .html, .scss, .spec.ts)
  - ✅ Route: `path: 'shopfloor'`
  - ✅ Klasse: `ShopfloorTabComponent`
  - ✅ Selector: `app-shopfloor-tab`
  - ✅ CSS-Klassen: `.shopfloor-tab`, `.shopfloor-table` (alle aktualisiert)
  - ✅ Storage Keys: `'shopfloor-tab-shopfloor-preview-expanded'`, `'shopfloor-tab-selected-module-serial-id'`
  - ✅ Tests: `shopfloor-tab.component.spec.ts` aktualisiert
  - ✅ Fixtures: `'shopfloor-tab'` in Tests aktualisiert
  - ✅ Navigation: `route: '/shopfloor'`, `id: 'shopfloor'`
  - ✅ DSP-Architektur-Komponenten: URLs aktualisiert (`/module` → `/shopfloor`)
  - ✅ Tabellen-Header: Zurück zu "Modules" geändert (wie gewünscht)

#### 4. Bezeichner: OMF3 → OSF (Dokumentation)
**Plan:** "Alle `OMF3` → `OSF` in `docs/`"

**Status:**
- ⚠️ **Dokumentation**: Teilweise noch `OMF3`/`omf3` in `docs/` (15 Dateien gefunden)
  - Sollten systematisch durchgesehen werden
  - Beispiele: `svg-inventory.html`, verschiedene Markdown-Dateien

#### 4. Bezeichner: package.json
**Plan:** `"name": "omf3-workspace"` → `"name": "osf-workspace"`

**Status:**
- ❌ **package.json**: `"name": "omf3-workspace"` → sollte `"osf-workspace"` sein

---

### ❌ Noch offen (Plan vs. Status übereinstimmend)

#### 1. package.json name
- ❌ `"name": "omf3-workspace"` → `"name": "osf-workspace"`

#### 2. module-tab → shopfloor-tab (vollständig)
- ❌ Datei umbenennen: `module-tab.component.ts` → `shopfloor-tab.component.ts`
- ❌ Route ändern: `path: 'module'` → `path: 'shopfloor'`
- ❌ Alle Referenzen aktualisieren (CSS-Klassen, Storage Keys, Fixtures, Tests)

#### 3. Dokumentation
- ⚠️ 15 Dateien in `docs/` enthalten noch `OMF3`/`omf3` Referenzen
  - Sollten systematisch durchgesehen werden

#### 4. Angular Prefix (optional)
**Plan:** `"prefix": "app"` → `"prefix": "osf"` (optional, prüfen)

**Status:**
- ⚠️ Nicht geprüft/geändert (optional)

#### 5. ENV Variablen
**Plan:** Alle `OMF3_*` → `OSF_*` (falls vorhanden)

**Status:**
- ⚠️ Nicht geprüft (falls vorhanden)

---

## Zusammenfassung

### Erledigt: ~90%
- ✅ App-Umbenennung (`ccu-ui` → `osf-ui`): **100%**
- ✅ Workspace-Umbenennung (`omf3` → `osf`): **100%**
- ✅ `fts-tab` → `agv-tab`: **100%**
- ✅ `module-tab` → `shopfloor-tab`: **100%** (vollständig umbenannt)
- ⚠️ Bezeichner OMF3 → OSF: **~80%** (Code erledigt, Dokumentation teilweise)
- ✅ Assets & Konfiguration: **100%**
- ✅ Git & Repository: **100%**

### Noch offen:
1. **package.json name**: `omf3-workspace` → `osf-workspace`
2. **Dokumentation**: 15 Dateien in `docs/` durchsehen und aktualisieren
3. **Optional**: Angular Prefix prüfen
4. **Optional**: ENV Variablen prüfen

---

## Empfehlung

1. ✅ **Erledigt:** `module-tab` → `shopfloor-tab` vollständig umbenannt
2. **Priorität 1:** `package.json` name aktualisieren (`omf3-workspace` → `osf-workspace`)
3. **Priorität 2:** Dokumentation in `docs/` systematisch durchsehen (15 Dateien)
4. **Optional:** Angular Prefix und ENV Variablen prüfen

