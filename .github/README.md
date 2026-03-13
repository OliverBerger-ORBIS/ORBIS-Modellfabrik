# GitHub Configuration

Dieses Verzeichnis enthält die GitHub-spezifischen Konfigurationsdateien für das ORBIS-Modellfabrik Repository.

## 📁 Inhalt

### Workflows (`.github/workflows/`)

GitHub Actions Workflows für CI/CD:

- **`ci.yml`** – Haupt-CI Pipeline (Tests, Lint, Production Build)
  - Trigger: Push/PR auf `main`/`develop`, manuell via `workflow_dispatch`
  - Jobs: test, lint, build
- **`deploy.yml`** – Deploy to GitHub Pages
  - Trigger: Nach erfolgreichem CI auf `main`, oder manuell
- **`pull-request.yml`** – Pull Request Validation (affected tests/lint)
- **`release.yml`** – Release-Erstellung bei Tag-Push (`v*.*.*`)

### Dokumentation

- **`WORKFLOW_GUIDELINES.md`** – Richtlinien für Workflow-Entwicklung (Test-Befehle, Konventionen)
- **`WORKFLOWS.md`** – Zusätzliche Workflow-Dokumentation (falls vorhanden)

## ⚠️ Wichtige Hinweise

### Workflows ändern?

**Vor jeder Änderung an Workflows:**

1. Lies `WORKFLOW_GUIDELINES.md`
2. Verwende `npm test` für Test-Befehle (nicht `npx nx test --all`)
3. Teste Änderungen lokal

### Test-Befehle

```yaml
# ✅ RICHTIG
- name: Run tests
  run: npm test

# ❌ FALSCH
- name: Run tests
  run: npx nx test --all
```

## 📚 Weitere Ressourcen

- [GitHub Actions Dokumentation](https://docs.github.com/en/actions)
- [Nx CI/CD](https://nx.dev/ci/intro/ci-with-nx)
- Repository: [ORBIS-Modellfabrik](https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik)
