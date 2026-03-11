# GitHub Actions – Workflow-Übersicht

**Stand:** März 2026

---

## ⚠️ pages-build-deployment vermeiden

Der Workflow **pages-build-deployment** ist GitHub-System-Workflow und hat keinen "Disable"-Button. Er erscheint, wenn Pages auf **Deploy from a branch** steht.

**Lösung – Pages-Quelle umstellen:**
1. **Settings** → **Pages** (unter "Code and automation")
2. Unter **Build and deployment** → **Source:** **GitHub Actions** auswählen (nicht "Deploy from a branch")
3. Speichern

Danach deployt nur noch unser Workflow **Deploy to GitHub Pages**. pages-build-deployment wird nicht mehr verwendet.

---

## Aktive Workflows

| Workflow | Trigger | Zweck |
|----------|---------|-------|
| **CI** | push/PR auf main, develop | Tests, Lint, Build, Coverage |
| **Deploy to GitHub Pages** | push auf main (oder manuell) | osf-ui bauen und auf GitHub Pages deployen |
| **Pull Request Validation** | PR geöffnet/aktualisiert | Affected tests + lint für geänderte Projekte |
| **Release** | Tag `v*.*.*` | GitHub Release + Archive erstellen |

---

## Deploy to GitHub Pages

- **URL:** https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/
- **Manuell starten:** Actions → Deploy to GitHub Pages → Run workflow
- **Doku:** [github-pages-deployment.md](../docs/04-howto/deployment/github-pages-deployment.md)

---

## Entfernte/Obsolete Workflows (März 2026)

| Workflow | Grund |
|----------|--------|
| **pages-build-deployment** | GitHub-System-Workflow – nur bei „Deploy from a branch“ aktiv; Source auf „GitHub Actions“ stellen (siehe oben) |
| **Heading Icons QA (OMF3)** | Script `check_heading_svgs_omf3.py` existiert nicht; `osf/apps/ccu-ui` existiert nicht |
| **Projekt-Struktur Validierung** | Script `omf/scripts/validate_project_structure.py` existiert nicht; verweist auf alte omf/omf2-Struktur |
| **Shopfloor Component Tests** | Redundant – CI führt bereits `npm test` (inkl. Shopfloor) bei jedem Push aus |
