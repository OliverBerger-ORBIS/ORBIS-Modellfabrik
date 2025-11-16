# GitHub Pages Deployment für OMF3 Dashboard

Dieser Guide erklärt, wie das OMF3 Dashboard über GitHub Pages bereitgestellt werden kann.

## Voraussetzungen

- Zugriff auf das GitHub Repository
- Git installiert auf dem lokalen Rechner
- Node.js und npm installiert

## Schritt 1: Test ob GitHub Pages erreichbar ist

Bevor Sie GitHub Pages einrichten, testen Sie ob der Service von Ihren Firmenrechnern aus erreichbar ist:

### Methode A: Existierende GitHub Pages Site testen

Versuchen Sie folgende Test-Sites zu öffnen:
- https://pages.github.com (Hauptseite)
- https://docs.github.com (GitHub Docs - auch auf GitHub Pages)
- https://angular.io (Angular Docs - auf GitHub Pages gehostet)

Falls diese Sites erreichbar sind, sollte GitHub Pages funktionieren.

### Methode B: Mit einer Test-Seite prüfen

Sie können auch eine minimale Test-Seite erstellen, um die Erreichbarkeit zu prüfen (siehe Schritt 2).

## Schritt 2: GitHub Pages aktivieren (Test-Deployment)

### Option A: Schnelltest mit dem aktuellen Branch

1. **Build erstellen:**
   ```bash
   npm run build:netlify
   ```

2. **Testbranch erstellen und wechseln:**
   ```bash
   git checkout -b gh-pages-test
   ```

3. **Build-Dateien in Branch-Root kopieren:**
   ```bash
   # Alle Dateien aus dist/apps/ccu-ui/browser in Root kopieren
   cp -r dist/apps/ccu-ui/browser/* .
   
   # .nojekyll Datei erstellen (wichtig für Angular)
   touch .nojekyll
   ```

4. **Dateien committen:**
   ```bash
   git add .
   git commit -m "Test: GitHub Pages deployment"
   ```

5. **Branch pushen:**
   ```bash
   git push origin gh-pages-test
   ```

6. **GitHub Pages aktivieren:**
   - Gehe zu: `https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/settings/pages`
   - Bei "Source": Wähle Branch `gh-pages-test` und `/ (root)`
   - Klicke "Save"

7. **Warte 1-2 Minuten** und teste die URL:
   ```
   https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/
   ```

Falls die Seite erreichbar ist, funktioniert GitHub Pages bei Ihnen! ✅

### Option B: Produktives Deployment (nach erfolgreichem Test)

Nach erfolgreichem Test können Sie einen dedizierten `gh-pages` Branch erstellen:

1. **Build erstellen:**
   ```bash
   npm run build:netlify
   ```

2. **Neuen gh-pages Branch erstellen (ohne History):**
   ```bash
   git checkout --orphan gh-pages
   ```

3. **Alle Dateien löschen (außer dist/):**
   ```bash
   git rm -rf .
   ```

4. **Build-Dateien in Root kopieren:**
   ```bash
   cp -r dist/apps/ccu-ui/browser/* .
   touch .nojekyll
   ```

5. **Committen und pushen:**
   ```bash
   git add .
   git commit -m "Deploy OMF3 Dashboard to GitHub Pages"
   git push origin gh-pages
   ```

6. **GitHub Pages auf `gh-pages` Branch setzen:**
   - Gehe zu Repository Settings → Pages
   - Source: Branch `gh-pages` / `/ (root)`

## Schritt 3: URL anpassen (optional)

GitHub Pages verwendet standardmäßig URLs wie:
```
https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/
```

Falls der Repository-Name im Pfad stört, gibt es zwei Optionen:

### Option A: Base Href anpassen

Falls die App unter einem Subpath läuft (z.B. `/ORBIS-Modellfabrik/`), muss die Build-Konfiguration angepasst werden:

**In `omf3/apps/ccu-ui/project.json`:**

```json
"configurations": {
  "github-pages": {
    "outputHashing": "all",
    "optimization": true,
    "sourceMap": false,
    "baseHref": "/ORBIS-Modellfabrik/",
    "localize": false
  }
}
```

**Neues Build-Script in `package.json`:**

```json
"scripts": {
  "build:github-pages": "nx build ccu-ui --configuration=github-pages"
}
```

Dann build mit:
```bash
npm run build:github-pages
```

### Option B: Custom Domain verwenden

Falls Sie eine eigene Domain haben:

1. Erstelle Datei `CNAME` im gh-pages Branch:
   ```
   dashboard.ihredomain.de
   ```

2. DNS-Eintrag bei Ihrem Provider erstellen:
   ```
   CNAME  dashboard  oliverberger-orbis.github.io
   ```

3. In GitHub Settings → Pages → Custom Domain eingeben

## Schritt 4: Automatisches Deployment (optional)

### GitHub Actions Workflow

Erstelle `.github/workflows/deploy-gh-pages.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]  # oder Ihr Hauptbranch
  workflow_dispatch:  # Manueller Trigger

permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build:netlify  # oder build:github-pages

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist/apps/ccu-ui/browser
          cname: dashboard.ihredomain.de  # optional
```

**Vorteil:** Automatisches Deployment bei jedem Push auf main.

## Schritt 5: Verifikation

Nach dem Deployment prüfen Sie:

1. ✅ **URL erreichbar:** `https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/`
2. ✅ **App lädt:** Startseite wird angezeigt
3. ✅ **Routing funktioniert:** Navigation zwischen Tabs funktioniert
4. ✅ **Mock-Daten laden:** Fixtures werden angezeigt
5. ✅ **Sprachumschaltung:** Deutsch/Französisch funktioniert
6. ✅ **Assets laden:** Alle Icons und Bilder werden angezeigt

### Häufige Probleme und Lösungen

**Problem: 404 Fehler bei Unterseiten**

GitHub Pages unterstützt keine nativen SPA-Redirects. Lösungen:

**Lösung A: 404.html Trick**

Erstelle `404.html` im gh-pages Branch mit folgendem Inhalt:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>OMF3 Dashboard</title>
  <script>
    // GitHub Pages SPA redirect trick
    sessionStorage.redirect = location.href;
  </script>
  <meta http-equiv="refresh" content="0;URL='/'">
</head>
<body></body>
</html>
```

Und in `index.html` (vor dem schließenden `</head>` Tag):

```html
<script>
  (function(){
    var redirect = sessionStorage.redirect;
    delete sessionStorage.redirect;
    if (redirect && redirect != location.href) {
      history.replaceState(null, null, redirect);
    }
  })();
</script>
```

**Lösung B: Hash-basiertes Routing** (nicht empfohlen)

Alternativ könnte Hash-Routing verwendet werden (`/#/en/overview`), aber das ist nicht die bevorzugte Lösung.

**Problem: Base Href falsch**

Falls Assets nicht laden:
- Prüfen Sie ob `baseHref` in der Build-Konfiguration korrekt ist
- Für `/ORBIS-Modellfabrik/`: `"baseHref": "/ORBIS-Modellfabrik/"`
- Für Custom Domain: `"baseHref": "/"`

**Problem: .nojekyll fehlt**

GitHub Pages nutzt standardmäßig Jekyll, das Dateien mit `_` ignoriert.
Lösung: `.nojekyll` Datei im Root erstellen.

## Zusammenfassung: Quick Test

Für einen schnellen Test ob GitHub Pages funktioniert:

```bash
# 1. Build erstellen
npm run build:netlify

# 2. Testbranch erstellen
git checkout -b gh-pages-test

# 3. Dateien kopieren
cp -r dist/apps/ccu-ui/browser/* .
touch .nojekyll

# 4. Committen und pushen
git add .
git commit -m "Test GitHub Pages"
git push origin gh-pages-test

# 5. In GitHub Settings → Pages aktivieren (Branch: gh-pages-test)

# 6. Warten und testen:
# https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/
```

Falls die URL erreichbar ist: ✅ GitHub Pages funktioniert bei Ihnen!

## Vorteile von GitHub Pages

- ✅ Kostenlos für öffentliche Repositories
- ✅ HTTPS automatisch
- ✅ Schnelles CDN
- ✅ Keine Build-Minuten Limits
- ✅ Custom Domains möglich
- ✅ Automatisches Deployment mit GitHub Actions

## Einschränkungen

- ⚠️ Repository muss öffentlich sein (oder GitHub Pro für private Repos)
- ⚠️ 1 GB Größenlimit
- ⚠️ 100 GB Bandbreite/Monat (sollte ausreichend sein)
- ⚠️ Kein Server-Side Code (nur statische Dateien)

## Support

Falls GitHub Pages nicht funktioniert, siehe `docs/deployment-alternatives.md` für weitere Optionen:
- Vercel
- Docker Container (Intranet)
- Interner Webserver

## Nächste Schritte

1. **Test durchführen** mit Testbranch (siehe "Quick Test")
2. **Erreichbarkeit prüfen** von Firmenrechnern
3. Falls erfolgreich: **Produktives Deployment** einrichten
4. Optional: **GitHub Actions** für automatisches Deployment einrichten
