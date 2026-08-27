# GitHub Workflow Guidelines

Diese Richtlinien dokumentieren wichtige Standards für GitHub Actions Workflows in diesem Repository.

## ⚠️ WICHTIG: Test-Befehle (CI)

### ✅ RICHTIG: Haupt-CI (`ci.yml`)

**Ein Durchlauf pro Projekt (A1 — keine Doppel-Suite für osf-ui):**

```yaml
- name: Run OSF tests (libs + osf-ui coverage)
  run: npm run test:ci
```

`package.json`:

```json
"test:ci": "nx run-many -t test --exclude=osf-ui && nx test osf-ui --coverage --coverageThreshold --runInBand"
```

- Libraries (mqtt-client, gateway, …) einmal parallel
- `osf-ui` einmal mit Coverage + Gates, `--runInBand` (bewusst; lokal Coverage ebenfalls runInBand)
- **Nicht** zusätzlich `npm test` im selben Job (würde osf-ui nochmal fahren)

### Lokal / alle Projekte ohne Coverage

```bash
npm test   # nx run-many -t test  (alle Projekte, parallel)
```

### ❌ FALSCH

```yaml
# ❌ ungültige Syntax
npx nx test --all

# ❌ ohne Projekt / run-many
npx nx test
```

### Pre-commit (B2)

Lokal: `scripts/pre-commit-osf-affected-tests.sh` → `nx affected -t test --files=<staged>`.  
Volle Suite + Coverage-Gates: **CI** (`npm run test:ci`). Bei Problemen: Hook wieder auf volle `nx test osf-ui` (+ mqtt-client) zurückstellen.

## Workflow-Dateien

- `.github/workflows/ci.yml` – Haupt-CI → `npm run test:ci`
- `.github/workflows/pull-request.yml` – affected tests/lint
- Pre-commit → affected tests (siehe `.pre-commit-config.yaml`)

## Historie

### 2026-08-27 — A1 + B2

- CI: Doppel-Lauf (`npm test` + `test:coverage:check`) ersetzt durch `test:ci`
- Pre-commit: volle Suite → `nx affected` auf gestagte Dateien
- Rollback: siehe vorherige Commits / diese Datei vor dem Change

### Problem (behoben, 2025-11-16)

- **Symptom**: Workflow schlug fehl wegen `npx nx test --all`
- **Lösung**: gültige Nx-/npm-Scripts (`run-many` / explizite Projekte)

## Weitere Nx-Befehle

### Einzelnes Projekt testen
```yaml
- name: Test specific project
  run: npx nx test <project-name>
```

### Alle Projekte (lokal, ohne Coverage-Gates)
```bash
npm test
```

### Coverage lokal (Mac: runInBand)
```bash
npm run test:coverage
npm run test:coverage:check
```

## Checkliste für neue/geänderte Workflows

- [ ] CI-Hauptpfad nutzt `npm run test:ci` (kein doppeltes osf-ui)
- [ ] Kein `nx test --all`
- [ ] Coverage-Gates hard-failen im `test:ci`-Schritt (kein `continue-on-error` auf dem Test-Step)
- [ ] Deploy weiterhin nur nach erfolgreichem CI
