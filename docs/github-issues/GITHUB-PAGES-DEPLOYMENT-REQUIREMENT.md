# GitHub Pages Deployment für OMF3 Dashboard

## Problem Statement

Die OMF3 Angular-Dashboard-Anwendung soll über GitHub Pages für Kollegen ohne Repository-Zugang bereitgestellt werden. Aktuell funktioniert das Deployment nicht korrekt:

- **Aktueller Status:** 404-Fehler auf https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/
- **Ziel:** Die App muss vollständig funktionieren (Mock-Mode, i18n, Routing)

## Anforderungen

### 1. Technische Constraints
- **Statisches Hosting:** GitHub Pages hostet nur statische Dateien
- **Mock-Mode:** Anwendung muss vollständig mit lokalen Fixtures funktionieren (keine MQTT-Verbindung)
- **Routing:** Client-side routing muss funktionieren (404-Problem auf GitHub Pages lösen)
- **i18n:** Runtime-Loading von Übersetzungen muss funktionieren (nicht compile-time)
- **Base-Href:** Muss auf `/ORBIS-Modellfabrik/` gesetzt werden
- **URL-Struktur:** `https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/`

### 2. Projekt-Spezifika (OMF3)

**Wichtig:** Dies ist ein **Nx Workspace**, nicht ein Standard Angular CLI Projekt!

- **Projekt-Name:** `ccu-ui` (nicht `omf3`)
- **Konfigurationsdatei:** `omf3/apps/ccu-ui/project.json` (nicht `angular.json`)
- **Build-Output:** `dist/apps/ccu-ui/browser` (nicht `dist/<project-name>`)
- **Nx-Befehle:** `nx build ccu-ui` (nicht `ng build`)

**Aktuelle Architektur:**
- **Environment-Service:** `EnvironmentService` verwaltet Mock/Replay/Live Modes
- **Mock-Mode:** Nutzt bereits Fixtures aus `omf3/testing/fixtures/`
- **Routing:** `provideRouter(appRoutes, withComponentInputBinding())` - aktuell ohne Hash-Strategy
- **i18n:** Runtime-Loading von `locale/messages.{locale}.json` (nicht compile-time)
- **Base-Href:** Aktuell `<base href="/" />` in `index.html`

### 3. Bekannte Probleme

1. **404-Fehler:** GitHub Pages findet `index.html` nicht
   - **Ursache:** Build erstellt Locale-Verzeichnisse (`de/`, `en/`, `fr/`) statt `index.html` im Root
   - **Grund:** `localize` Option in Build-Konfiguration aktiviert

2. **Routing:** Client-side routing funktioniert nicht ohne Hash-Strategy
   - **Problem:** GitHub Pages kann Routen wie `/en/overview` nicht direkt servieren
   - **Lösungsoptionen:** Hash-Routing (`/#/en/overview`) oder 404.html Redirect

3. **Base-Href:** Muss `/ORBIS-Modellfabrik/` sein für GitHub Pages Projekt-URLs

## Konkrete Aufgaben

### Aufgabe 1: Build-Konfiguration für GitHub Pages

**Datei:** `omf3/apps/ccu-ui/project.json`

Erstelle eine neue Build-Konfiguration `github-pages` mit:
- `baseHref: "/ORBIS-Modellfabrik/"`
- `localize: false` (Runtime-i18n, kein compile-time Locale-Splitting)
- Optimierungen aktiviert
- Source Maps deaktiviert

**Wichtig:** Die Konfiguration muss sicherstellen, dass `index.html` direkt im Build-Output-Root liegt, nicht in Locale-Unterverzeichnissen.

### Aufgabe 2: Routing-Strategie für GitHub Pages

**Option A: Hash-Routing (Empfohlen)**
- Aktiviere `withHashLocation()` in `app.config.ts`
- URLs werden: `/#/en/overview` statt `/en/overview`
- Funktioniert sofort ohne zusätzliche Konfiguration

**Option B: 404.html Redirect**
- Erstelle `404.html` im `public/` Verzeichnis
- Redirect-Logik für SPA-Routing
- Komplexer, aber saubere URLs ohne Hash

**Entscheidung:** Implementiere beide Optionen und teste, welche besser funktioniert. Empfehlung: Hash-Routing (einfacher, zuverlässiger).

### Aufgabe 3: Deployment-Script anpassen

**Datei:** `scripts/deploy-gh-pages-test.sh`

Stelle sicher, dass:
- `build:github-pages` verwendet wird (nicht `build:netlify`)
- `404.html` wird kopiert (falls Option B gewählt)
- `.nojekyll` Datei wird erstellt
- Build-Output korrekt in Branch kopiert wird

### Aufgabe 4: Package.json Script

**Datei:** `package.json`

Füge Script hinzu:
```json
"build:github-pages": "nx build ccu-ui --configuration=github-pages"
```

### Aufgabe 5: Test und Validierung

**Test-Checkliste:**
- [ ] Lokaler Build funktioniert: `npm run build:github-pages`
- [ ] Build-Output enthält `index.html` direkt im Root (nicht in `de/`, `en/`, `fr/`)
- [ ] `baseHref` ist korrekt in `index.html`: `/ORBIS-Modellfabrik/`
- [ ] Routing funktioniert (mit Hash oder 404-Redirect)
- [ ] i18n funktioniert (Sprachumschaltung)
- [ ] Mock-Mode funktioniert (Fixtures werden geladen)
- [ ] Alle Assets sind im Build (SVG, JSON, etc.)
- [ ] GitHub Pages Deployment funktioniert
- [ ] URL ist erreichbar: https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/

## Deployment-Prozess

**Aktueller Prozess:**
1. `npm run deploy:gh-pages-test` ausführen
2. Script erstellt `gh-pages-test` Branch
3. Build-Dateien werden in Branch kopiert
4. Branch wird gepusht
5. GitHub Pages wird in Settings aktiviert (Branch: `gh-pages-test`, Folder: `/ (root)`)

**Ziel:** Dieser Prozess soll nach der Implementierung funktionieren.

## Erwartetes Ergebnis

Nach erfolgreicher Implementierung:
- ✅ GitHub Pages URL ist erreichbar
- ✅ App lädt vollständig (kein 404, kein leeres Fenster)
- ✅ Routing funktioniert (Navigation zwischen Tabs)
- ✅ i18n funktioniert (Sprachumschaltung DE/EN/FR)
- ✅ Mock-Mode funktioniert (Fixtures werden geladen)
- ✅ Alle Tabs zeigen Daten korrekt an

## Test-Strategie

**Lokales Testen:**
```bash
npm run build:github-pages
npx serve dist/apps/ccu-ui/browser -p 4200
# Browser: http://localhost:4200/ORBIS-Modellfabrik/
```

**GitHub Pages Testen:**
1. Deployment ausführen: `npm run deploy:gh-pages-test`
2. GitHub Pages aktivieren (Settings → Pages → Branch: `gh-pages-test`)
3. Warte 1-2 Minuten
4. Teste: https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/

## Wichtige Hinweise

- **Nx Workspace:** Alle Befehle müssen `nx` statt `ng` verwenden
- **Output-Pfad:** `dist/apps/ccu-ui/browser` (nicht `dist/<project-name>`)
- **i18n:** Runtime-Loading (nicht compile-time), daher `localize: false` im Build
- **Mock-Daten:** Bereits vorhanden in `omf3/testing/fixtures/`, werden als Assets kopiert
- **Hash-Routing vs. 404-Redirect:** Beide Optionen testen und beste Lösung wählen

## Referenzen

- [Angular Deployment](https://angular.io/guide/deployment)
- [GitHub Pages](https://docs.github.com/en/pages)
- [Nx Build Configuration](https://nx.dev/reference/project-configuration)
- [Angular Hash Location Strategy](https://angular.io/api/common/HashLocationStrategy)

## Offene Fragen / Entscheidungen

1. **Routing-Strategie:** Hash (`#/en/overview`) oder 404-Redirect (`/en/overview`)?
   - **Empfehlung:** Hash (einfacher, funktioniert sofort)
   - **Test:** Beide implementieren und beste Lösung wählen

2. **Branch-Strategie:** 
   - **Option A:** `gh-pages-test` Branch (aktuell)
   - **Option B:** `gh-pages` Branch (produktiv)
   - **Option C:** Beide (Test + Produktiv)
   - **Empfehlung:** Beide (Test für Validierung, Produktiv für Live)

3. **Versionierung:**
   - Soll das Deployment versioniert werden?
   - Soll es automatisch bei jedem Push zu `main` deployen?
   - **Empfehlung:** Erst manuelles Deployment, später GitHub Actions

## Erfolgskriterien

✅ **Erfolgreich wenn:**
- GitHub Pages URL ist erreichbar (kein 404)
- App lädt vollständig und zeigt Dashboard
- Navigation zwischen Tabs funktioniert
- i18n funktioniert (Sprachumschaltung)
- Mock-Mode funktioniert (Daten werden angezeigt)
- Alle Assets werden korrekt geladen

❌ **Nicht erfolgreich wenn:**
- 404-Fehler auf GitHub Pages
- Leeres Fenster (kein JavaScript-Fehler)
- Routing funktioniert nicht
- Assets werden nicht geladen
- i18n funktioniert nicht

