# GitHub Pages Deployment - Automatisches CI/CD

**Status:** ✅ Aktiv - Deployment erfolgt automatisch via GitHub Actions  
**Datum:** 2025-12-23  
**Methode:** Automatisches Deployment bei erfolgreichen Commits auf `main` Branch

---

## 🎯 Automatischer Deployment-Prozess

### GitHub Actions Workflow

**Workflow-Datei:** `.github/workflows/deploy.yml`

**Trigger:**
- ✅ Automatisch bei Push auf `main` Branch (wenn `osf/**`, `package.json` oder `.github/workflows/deploy.yml` geändert wurden)
- ✅ Manuell via `workflow_dispatch` (GitHub Actions UI)

**Prozess:**
1. **Build:** Angular App wird mit allen Locales gebaut (`nx build osf-ui --configuration=production --localize`)
2. **Prepare:** Build-Output wird für GitHub Pages vorbereitet (`_site/` Verzeichnis)
3. **Deploy:** Automatisches Deployment zu GitHub Pages via `actions/deploy-pages@v4`

**Deployment-URL:** `https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/`

**Build-Output:** `dist/apps/osf-ui/browser/` → `_site/`

**Wichtig:** Der Build erstellt alle benötigten Dateien inklusive:
- `index.html` (mit korrektem `baseHref="/ORBIS-Modellfabrik/"`)
- Alle Assets (SVG, JSON, etc.)
- Hash-basiertes Routing (funktioniert automatisch auf GitHub Pages)
- Alle Locales (de, en, fr)

---

## 📋 Build-Konfiguration

### CI/CD Build-Konfiguration

**Build-Befehl (im Workflow):**
```bash
npx nx build osf-ui --configuration=production --localize --baseHref=/ORBIS-Modellfabrik/
```

**Konfiguration:** `osf/apps/osf-ui/project.json` → `production`

**Wichtige Einstellungen:**
- **Base Href:** `/ORBIS-Modellfabrik/`
- **Routing:** Hash-basiert (`/#/en/overview`)
- **i18n:** Runtime-Loading (keine Locale-Unterverzeichnisse)
- **Output:** `dist/apps/osf-ui/browser/`
- **Locales:** de, en, fr (alle werden gebaut)

### Lokaler Build (für Tests)

Für lokale Tests kann der Build manuell erstellt werden:

```bash
# Production Build mit allen Locales
nx build osf-ui --configuration=production --localize --baseHref=/ORBIS-Modellfabrik/

# Build-Output lokal testen
npx serve dist/apps/osf-ui/browser -p 4200
```

---

## ✅ Verifikation nach Deployment

Nach dem Deployment prüfen:

1. ✅ **URL erreichbar:** `https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/`
2. ✅ **App lädt:** Startseite wird angezeigt
3. ✅ **Routing funktioniert:** Navigation zwischen Tabs funktioniert
4. ✅ **Mock-Daten laden:** Fixtures werden angezeigt
5. ✅ **Sprachumschaltung:** Deutsch/Französisch funktioniert
6. ✅ **Assets laden:** Alle Icons und Bilder werden angezeigt

---

## 🔧 Troubleshooting

### Problem: Deployment wird nicht automatisch ausgelöst

**Prüfen:**
1. **Workflow-Trigger:** Wurden `osf/**`, `package.json` oder `.github/workflows/deploy.yml` geändert?
2. **GitHub Actions:** Prüfe den "Actions" Tab im Repository
3. **Workflow-Status:** Ist der Workflow erfolgreich durchgelaufen?

**Lösung:**
- **Manueller Trigger:** Gehe zu "Actions" → "Deploy to GitHub Pages" → "Run workflow"
- **Oder:** Leeren Commit auf `main` pushen (z.B. `git commit --allow-empty -m "Trigger deployment"`)

### Problem: Deployment schlägt fehl

**Prüfen:**
1. **Build-Fehler:** Prüfe die Build-Logs im GitHub Actions Workflow
2. **Dependencies:** Sind alle npm Dependencies korrekt installiert?
3. **TypeScript-Fehler:** Gibt es TypeScript- oder Linting-Fehler?

**Lösung:**
- Fehler in den GitHub Actions Logs prüfen
- Lokal testen: `nx build osf-ui --configuration=production --localize`
- Pre-commit Hooks prüfen (Tests, Linting)

### Problem: Assets laden nicht

**Prüfen:**
- `baseHref` in der Build-Konfiguration ist `/ORBIS-Modellfabrik/`
- Alle Assets sind im Build-Output vorhanden
- `.nojekyll` Datei ist im Branch-Root

### Problem: 404-Fehler bei Unterseiten

✅ **Bereits gelöst:** Die App verwendet Hash-basiertes Routing (`/#/en/overview`), daher gibt es keine 404-Fehler bei direkten Links zu Unterseiten.

---

## 📝 Wichtige Hinweise

- **Hash-basiertes Routing:** URLs verwenden `#` (z.B. `/#/en/overview`)
  - ✅ Funktioniert automatisch auf GitHub Pages
  - ✅ Keine Server-Konfiguration erforderlich
  - ✅ Direkte Links zu Unterseiten funktionieren

- **Base Href:** Korrekt auf `/ORBIS-Modellfabrik/` gesetzt
- **i18n:** Runtime-Loading (Deutsch, Englisch, Französisch)
- **Mock-Mode:** Funktioniert vollständig mit lokalen Fixtures

---

## 🔗 Verwandte Dokumentation

- [Deployment Alternatives](../../deployment-alternatives.md) - Weitere Deployment-Optionen
- [Build Commands Guide](../../analysis/build-commands-guide.md) - Build-Konfiguration Details

---

**Letzte Aktualisierung:** 2025-12-23  
**Status:** ✅ Aktiv - Automatisches Deployment via GitHub Actions CI/CD
