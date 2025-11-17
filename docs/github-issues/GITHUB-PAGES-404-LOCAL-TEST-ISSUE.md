# GitHub Pages 404-Fix: Lokales Test-Problem

## Problem Statement

Nach der Implementierung des GitHub Pages 404-Fixes (Branch `copilot/fix-url-structure-error`) funktioniert die App lokal nicht mehr korrekt. Die `404.html` wird lokal geladen und zeigt "Redirecting..." an, aber die App lädt nicht.

## Lokaler Test

### Test-Umgebung
- **Angular Dev Server:** `nx serve ccu-ui` (Port 57433)
- **Build-Konfiguration:** `development` (baseHref: `"/"`)
- **URL:** `http://localhost:57433/ORBIS-Modellfabrik/#/en/overview`

### Test-Ergebnis

**Aktuelles Verhalten:**
1. Browser zeigt "Redirecting..." (von `404.html`)
2. App lädt nicht
3. Browser bleibt auf der 404.html-Seite

**Erwartetes Verhalten:**
1. App sollte direkt laden (ohne 404.html)
2. Oder 404.html sollte korrekt zu `/` redirecten und die App dann laden

### Problem-Analyse

**Ursache:**
- Der Angular Dev Server läuft mit `baseHref: "/"` (development config)
- Zugriff auf `/ORBIS-Modellfabrik/#/en/overview` gibt 404 zurück (weil `/ORBIS-Modellfabrik/` nicht existiert)
- `404.html` wird geladen und versucht zu redirecten
- Redirect funktioniert nicht korrekt oder die App lädt danach nicht

**Aktuelle 404.html Implementierung:**
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>OMF3 Dashboard</title>
    <base href="/ORBIS-Modellfabrik/" />
    <script type="text/javascript">
      var l = window.location;
      var isGitHubPages = l.hostname === 'oliverberger-orbis.github.io' || l.hostname.endsWith('.github.io');
      
      if (isGitHubPages) {
        // GitHub Pages redirect logic
        var basePath = '/ORBIS-Modellfabrik/';
        if (!l.pathname.startsWith(basePath)) {
          var hash = l.hash || '#/en/overview';
          l.replace(l.protocol + '//' + l.hostname + (l.port ? ':' + l.port : '') + basePath + hash);
        } else {
          if (!l.hash || l.hash === '') {
            l.replace(l.href + '#/en/overview');
          }
        }
      } else {
        // Local development: redirect to root with hash
        var hash = l.hash || '#/en/overview';
        l.replace(l.protocol + '//' + l.hostname + (l.port ? ':' + l.port : '') + '/' + hash);
      }
    </script>
  </head>
  <body>
    <p>Redirecting...</p>
  </body>
</html>
```

**Versuchte Lösungen (ohne Erfolg):**
1. ✅ 404.html erkennt localhost und redirectet zu `/`
2. ❌ Redirect funktioniert nicht oder App lädt danach nicht
3. ❌ Hard Refresh (Cmd+Shift+R) hat keinen Effekt

## Anforderungen

### 1. Lokales Testen
- **Option A:** 404.html sollte lokal nicht verwendet werden
  - Dev Server sollte `index.html` für alle Routen zurückgeben (SPA-Mode)
  - 404.html sollte nur auf GitHub Pages aktiv sein

- **Option B:** 404.html sollte lokal korrekt funktionieren
  - Redirect zu `/` sollte funktionieren
  - App sollte nach Redirect korrekt laden

**Empfehlung:** Option A (404.html nur für GitHub Pages)

### 2. GitHub Pages
- 404.html muss auf GitHub Pages funktionieren
- Redirect zu `/ORBIS-Modellfabrik/#/en/overview` muss korrekt sein
- Alle Routen (mit und ohne Hash) müssen funktionieren

## Technische Details

### Angular Dev Server Konfiguration
```json
{
  "serve": {
    "executor": "@angular-devkit/build-angular:dev-server",
    "configurations": {
      "development": {
        "buildTarget": "ccu-ui:build:development"
      }
    },
    "defaultConfiguration": "development"
  }
}
```

**Development Build Config:**
- `baseHref: "/"` (nicht `/ORBIS-Modellfabrik/`)
- `localize: false`
- `optimization: false`

### GitHub Pages Build Config
```json
{
  "github-pages": {
    "baseHref": "/ORBIS-Modellfabrik/",
    "localize": false,
    "outputHashing": "all",
    "optimization": true
  }
}
```

## Lösung

### Vorschlag 1: Dev Server SPA-Mode aktivieren
Der Angular Dev Server sollte so konfiguriert werden, dass er `index.html` für alle Routen zurückgibt (SPA-Mode). Dies verhindert, dass `404.html` lokal verwendet wird.

**Konfiguration:**
```json
{
  "serve": {
    "executor": "@angular-devkit/build-angular:dev-server",
    "options": {
      "spa": true
    }
  }
}
```

### Vorschlag 2: 404.html nur auf GitHub Pages aktivieren
Die 404.html sollte so angepasst werden, dass sie lokal nicht geladen wird oder sofort zu `index.html` redirectet, ohne JavaScript-Redirect.

**Alternative:** Dev Server so konfigurieren, dass er `404.html` ignoriert und stattdessen `index.html` zurückgibt.

## Test-Checkliste

Nach der Fix-Implementierung:

### Lokal (Dev Server)
- [ ] Zugriff auf `http://localhost:57433/` → App lädt korrekt
- [ ] Zugriff auf `http://localhost:57433/#/en/overview` → App lädt korrekt
- [ ] Zugriff auf `http://localhost:57433/ORBIS-Modellfabrik/#/en/overview` → App lädt korrekt (oder redirectet zu `/`)
- [ ] 404.html wird lokal nicht verwendet (oder funktioniert korrekt)

### GitHub Pages
- [ ] Zugriff auf `https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/` → App lädt korrekt
- [ ] Zugriff auf `https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/#/en/overview` → App lädt korrekt
- [ ] Zugriff auf `https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/en/overview` (ohne Hash) → 404.html redirectet korrekt

## Wichtige Hinweise

- **Dev Server:** Läuft mit `baseHref: "/"` (development config)
- **GitHub Pages:** Läuft mit `baseHref: "/ORBIS-Modellfabrik/"` (github-pages config)
- **404.html:** Sollte nur auf GitHub Pages aktiv sein, nicht lokal
- **Hash-Routing:** Mit `withHashLocation()` wird alles nach `#` client-seitig gehandhabt

## Referenzen

- [Angular Dev Server Configuration](https://angular.io/cli/serve)
- [Angular Hash Location Strategy](https://angular.io/api/common/HashLocationStrategy)
- [GitHub Pages 404 Handling](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-custom-404-page-for-your-github-pages-site)

