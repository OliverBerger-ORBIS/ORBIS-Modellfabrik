# GitHub Configuration

Dieses Verzeichnis enthält die GitHub-spezifischen Konfigurationsdateien für das ORBIS-Modellfabrik Repository.

## 📁 Inhalt

### Workflows (`.github/workflows/`)

GitHub Actions Workflows für CI/CD:

- **`ci.yml`** - Haupt-CI Pipeline (läuft bei Push/PR auf main/develop)
- **`shopfloor-check.yml`** - Shopfloor Component Tests
- **`structure-validation.yml`** - Struktur-Validierung
- **`heading-icons-check.yml`** - Icon-Validierung

### Dokumentation

- **`WORKFLOW_GUIDELINES.md`** - ⚠️ **WICHTIG**: Richtlinien für Workflow-Entwicklung
  - Dokumentiert korrekte Test-Befehle
  - Verhindert bekannte Fehler
  - **Bitte lesen vor Workflow-Änderungen!**

## ⚠️ Wichtige Hinweise

### Workflows ändern?

**Vor jeder Änderung an Workflows:**

1. 📖 Lies `WORKFLOW_GUIDELINES.md`
2. ✅ Verwende `npm test` für Test-Befehle
3. ❌ Verwende NICHT `npx nx test --all` (ungültige Syntax)
4. 🧪 Teste Änderungen lokal

### Bekannte Probleme (behoben)

- ❌ **Problem**: `npx nx test --all` führt zu Fehlern
- ✅ **Lösung**: `npm test` verwenden (siehe WORKFLOW_GUIDELINES.md)
- 🔒 **Prävention**: Kommentare in allen Workflows + diese Dokumentation

## 🔧 Workflow-Entwicklung

### Neue Workflows erstellen

1. Kopiere einen bestehenden Workflow als Vorlage (z.B. `ci.yml`)
2. Folge den Konventionen in `WORKFLOW_GUIDELINES.md`
3. Füge Kommentare hinzu für wichtige Befehle
4. Teste lokal bevor du commitest

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

## 🆘 Bei Problemen

1. Prüfe `WORKFLOW_GUIDELINES.md`
2. Vergleiche mit funktionierenden Workflows
3. Teste Befehle lokal: `npm test`
4. Bei Unsicherheit: Frage im Team nach
