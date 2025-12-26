# Build-Befehle für OSF osf-ui

## 📦 Production Build

### Standard Production Build (mit i18n)

```bash
nx build osf-ui --configuration=production
```

**Oder:**
```bash
nx build osf-ui
```
(Standard-Konfiguration ist bereits `production`)

**Output:**
- `dist/apps/osf-ui/browser/en/` - Englische Version
- `dist/apps/osf-ui/browser/de/` - Deutsche Version
- `dist/apps/osf-ui/browser/fr/` - Französische Version

**Eigenschaften:**
- ✅ Optimiert (Minification, Tree-Shaking)
- ✅ Output Hashing (Cache-Busting)
- ✅ i18n für alle 3 Sprachen
- ✅ Bundle Size Budgets aktiv
- ⚠️ **Aktuell:** Fixtures werden noch eingebunden (sollte entfernt werden)

### Production Build ohne i18n (nur Englisch)

```bash
nx build osf-ui --configuration=production --localize=false
```

**Oder:** Verwende `github-pages` Konfiguration:

```bash
nx build osf-ui --configuration=github-pages
```

---

## 🛠️ Development Build

### Development Build (für lokale Tests)

```bash
nx build osf-ui --configuration=development
```

**Eigenschaften:**
- ❌ Keine Optimierung (schnellerer Build)
- ✅ Source Maps (für Debugging)
- ✅ Fixtures eingebunden
- ❌ Keine i18n (nur Englisch)
- ❌ Keine License Extraction

**Output:**
- `dist/apps/osf-ui/browser/` - Einzelner Build ohne Locale-Unterordner

### Development Build mit Production-Optimierung

```bash
nx build osf-ui --configuration=production --localize=false
```

**Verwendung:** Wenn du Production-Build testen willst, aber ohne i18n

---

## 🚀 Development Server (Live Reload)

### Standard Development Server

```bash
nx serve osf-ui
```

**Oder explizit:**
```bash
nx serve osf-ui --configuration=development
```

**Eigenschaften:**
- ✅ Live Reload (Hot Module Replacement)
- ✅ Source Maps
- ✅ Fixtures verfügbar
- ✅ Port 4200 (Standard)
- ❌ Keine Optimierung

### Production Server (für Testing)

```bash
nx serve osf-ui --configuration=production
```

**Eigenschaften:**
- ✅ Production Build (optimiert)
- ✅ i18n aktiv
- ⚠️ Langsamerer Start (wegen Optimierung)
- ⚠️ Live Reload funktioniert, aber langsamer

---

## 📊 Build-Konfigurationen im Detail

### Production Configuration

```json
{
  "production": {
    "budgets": [
      { "type": "initial", "maximumWarning": "800kb", "maximumError": "1mb" },
      { "type": "anyComponentStyle", "maximumWarning": "7kb", "maximumError": "8kb" }
    ],
    "outputHashing": "all",
    "localize": ["en", "de", "fr"]
  }
}
```

**Was passiert:**
- Code wird minifiziert
- Tree-Shaking entfernt ungenutzten Code
- CSS wird optimiert
- Assets werden gehasht (Cache-Busting)
- Bundle Size wird überwacht

### Development Configuration

```json
{
  "development": {
    "optimization": false,
    "extractLicenses": false,
    "sourceMap": true,
    "localize": false
  }
}
```

**Was passiert:**
- Keine Minification (schnellerer Build)
- Source Maps für Debugging
- Keine i18n (nur Englisch)
- Fixtures bleiben verfügbar

---

## 🔍 Build-Output prüfen

### Bundle-Größen anzeigen

```bash
# Nach dem Build
ls -lh dist/apps/osf-ui/browser/en/*.js
```

### Bundle-Analyse (optional)

```bash
# Bundle-Analyse mit webpack-bundle-analyzer
nx build osf-ui --configuration=production --stats-json
npx webpack-bundle-analyzer dist/apps/osf-ui/stats.json
```

---

## 🎯 Empfohlene Workflows

### 1. Lokale Entwicklung

```bash
# Development Server starten
nx serve osf-ui
# → Öffnet http://localhost:4200
# → Fixtures verfügbar
# → Live Reload aktiv
```

### 2. Production Build testen (lokal)

```bash
# Production Build erstellen
nx build osf-ui --configuration=production

# Statischen Server starten
nx serve-static osf-ui
# → Öffnet http://localhost:4200
# → Production Build wird serviert
```

### 3. Production Build für Deployment

```bash
# Production Build mit allen Sprachen
nx build osf-ui --configuration=production

# Output liegt in:
# dist/apps/osf-ui/browser/en/
# dist/apps/osf-ui/browser/de/
# dist/apps/osf-ui/browser/fr/
```

### 4. Development Build für schnelle Tests

```bash
# Development Build (schnell, ohne Optimierung)
nx build osf-ui --configuration=development

# Output liegt in:
# dist/apps/osf-ui/browser/
```

---

## ⚠️ Aktuelle Probleme

### Problem 1: Fixtures in Production Build

**Aktuell:** Fixtures werden in **allen** Builds eingebunden (auch Production)

**Lösung:** Siehe `docs/analysis/mock-environment-fixtures-removal-risk.md`

**Quick Fix:**
```json
// project.json - Production Configuration
"production": {
  "assets": [
    { "glob": "**/*", "input": "osf/apps/osf-ui/public" }
    // Fixtures hier entfernen
  ]
}
```

### Problem 2: Default Configuration

**Aktuell:** `"defaultConfiguration": "production"`

**Bedeutung:** `nx build ccu-ui` erstellt Production Build

**Empfehlung:** Für Development explizit `--configuration=development` verwenden

---

## 📋 Checkliste für Production Build

Vor dem Production Build:

- [ ] Tests bestehen: `nx test osf-ui`
- [ ] Linting: `nx lint osf-ui`
- [ ] Fixtures aus Production Build entfernt
- [ ] Bundle Size Budgets eingehalten
- [ ] i18n Übersetzungen vollständig
- [ ] Source Maps deaktiviert (automatisch in Production)

Nach dem Production Build:

- [ ] Bundle-Größen prüfen
- [ ] Alle 3 Sprachen gebaut (en, de, fr)
- [ ] Statischen Server testen: `nx serve-static osf-ui`
- [ ] Funktionalität in allen Sprachen testen

---

## 🚀 Deployment-Konfigurationen

### GitHub Pages

```bash
nx build osf-ui --configuration=github-pages
```

**Eigenschaften:**
- Optimiert
- `baseHref: "/ORBIS-Modellfabrik/"`
- Keine i18n (nur Englisch)

---

## 💡 Tipps

1. **Schneller Development Build:**
   ```bash
   nx build osf-ui --configuration=development
   ```
   → ~3-5x schneller als Production Build

2. **Production Build ohne i18n (schneller):**
   ```bash
   nx build osf-ui --configuration=production --localize=false
   ```
   → Nur Englisch, aber optimiert

3. **Build-Output prüfen:**
   ```bash
   # Nach dem Build
   du -sh dist/apps/osf-ui/browser/*
   ```

4. **Clean Build:**
   ```bash
   # Alten Build löschen
   rm -rf dist/apps/osf-ui
   # Neuer Build
   nx build osf-ui --configuration=production
   ```

