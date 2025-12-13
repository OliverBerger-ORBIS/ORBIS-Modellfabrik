# GitHub Workflow Guidelines

Diese Richtlinien dokumentieren wichtige Standards für GitHub Actions Workflows in diesem Repository.

## ⚠️ WICHTIG: Test-Befehle

### ✅ RICHTIG: Test-Befehl für Workflows

**Verwende immer:**
```yaml
- name: Run tests
  run: npm test
```

### ❌ FALSCH: Diese Befehle funktionieren nicht

```yaml
# ❌ NICHT verwenden - ungültige Syntax
npx nx test --all

# ❌ NICHT verwenden - funktioniert nicht für alle Projekte
npx nx test

# ❌ NICHT verwenden - falsche Syntax
nx test --all
```

### Warum `npm test`?

1. **Definiert in package.json**: Der Befehl `npm test` ist in `package.json` definiert als:
   ```json
   "scripts": {
     "test": "nx run-many -t test"
   }
   ```

2. **Führt alle Tests aus**: `nx run-many -t test` führt Tests für alle Projekte aus

3. **Konsistent**: Alle Workflows (ci.yml, shopfloor-check.yml, structure-validation.yml) verwenden denselben Befehl

4. **Bewährt**: Dieser Befehl funktioniert zuverlässig in CI/CD

## Workflow-Dateien

Folgende Workflow-Dateien führen Tests aus:

- `.github/workflows/ci.yml` - Haupt-CI Pipeline
- `.github/workflows/shopfloor-check.yml` - Shopfloor Component Tests
- `.github/workflows/structure-validation.yml` - Struktur-Validierung

**Alle verwenden `npm test` ✅**

## Historie

### Problem (behoben)

- **Symptom**: Workflow "Shopfloor Component Tests (OMF3)" schlug fehl
- **Ursache**: Verwendung von `npx nx test --all` (ungültige Syntax)
- **Lösung**: Geändert zu `npm test`
- **Commit**: b4e130c
- **Datum**: 2025-11-16

### Prävention

Um zu verhindern, dass dieser Fehler erneut auftritt:

1. ✅ Diese Dokumentation wurde erstellt
2. ✅ Alle Workflows wurden überprüft und verwenden `npm test`
3. ⚠️ Bei Workflow-Änderungen immer diese Richtlinien beachten
4. ⚠️ Bei Pull Requests Workflows auf korrekte Test-Befehle prüfen

## Weitere Nx-Befehle

Wenn du spezifische Nx-Befehle in Workflows verwenden musst:

### Einzelnes Projekt testen
```yaml
- name: Test specific project
  run: npx nx test <project-name>
```

Beispiel:
```yaml
- name: Test ccu-ui
  run: npx nx test ccu-ui
```

### Mehrere Projekte testen
```yaml
- name: Test multiple projects
  run: npx nx run-many -t test --projects=project1,project2
```

### Build-Befehle
```yaml
- name: Build for production
  run: npm run build:github-pages
```

## Checkliste für Workflow-Änderungen

Bevor du einen Workflow committest, prüfe:

- [ ] Verwendet der Workflow `npm test` für Test-Befehle?
- [ ] Sind alle Nx-Befehle korrekt (mit `npx nx` oder npm script)?
- [ ] Wurde die Änderung lokal getestet?
- [ ] Wurden diese Richtlinien befolgt?

## Bei Problemen

Falls ein Workflow fehlschlägt:

1. Prüfe, ob `npm test` verwendet wird
2. Prüfe diese Dokumentation
3. Vergleiche mit anderen funktionierenden Workflows
4. Teste den Befehl lokal: `npm test`

## Referenzen

- **package.json**: Definiert npm scripts
- **nx.json**: Nx Workspace Konfiguration
- **CI Workflow**: `.github/workflows/ci.yml` (Referenz-Implementation)
