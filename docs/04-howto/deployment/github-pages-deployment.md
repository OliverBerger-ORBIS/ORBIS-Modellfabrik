# GitHub Pages Deployment - Aktueller Prozess

**Status:** ✅ Aktiv - Deployment erfolgt direkt in GitHub  
**Datum:** 2025-12-13  
**Methode:** Manuelles Deployment über GitHub UI

---

## 🎯 Aktueller Deployment-Prozess

### Schritt 1: Build lokal erstellen

```bash
npm run build:github-pages
```

**Build-Output:** `dist/apps/ccu-ui/browser/`

**Wichtig:** Der Build erstellt alle benötigten Dateien inklusive:
- `index.html` (mit korrektem `baseHref="/ORBIS-Modellfabrik/"`)
- Alle Assets (SVG, JSON, etc.)
- Hash-basiertes Routing (funktioniert automatisch auf GitHub Pages)

### Schritt 2: Build-Dateien hochladen (direkt in GitHub UI)

1. **Gehe zu GitHub Repository:**
   - `https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik`

2. **Navigiere zum `gh-pages` Branch:**
   - Falls nicht vorhanden: Erstelle neuen Branch `gh-pages` (oder verwende `gh-pages-test` für Tests)

3. **Lösche alle Dateien im Branch-Root:**
   - Alle Dateien löschen (außer `.nojekyll`, falls vorhanden)
   - Wichtig: Branch komplett leeren vor dem Upload

4. **Lade Build-Dateien hoch:**
   - **Upload-Methode:** "Add file" → "Upload files" in GitHub UI
   - **Dateien:** Alle Dateien aus `dist/apps/ccu-ui/browser/` hochladen
   - **Wichtig:** `.nojekyll` Datei muss vorhanden sein (für Angular - verhindert Jekyll-Processing)

5. **Commit und Push:**
   - Commit-Message: z.B. "Deploy: Update GitHub Pages - [Datum]"
   - Commit direkt in GitHub UI

### Schritt 3: GitHub Pages aktivieren/aktualisieren

1. **Gehe zu Repository Settings:**
   - `https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/settings/pages`

2. **Konfiguration:**
   - **Source:** "Deploy from a branch"
   - **Branch:** `gh-pages` (oder `gh-pages-test` für Tests) / `/ (root)`
   - **Save**

3. **Warte 1-2 Minuten** bis GitHub Pages den Build verarbeitet
   - Status wird in Settings angezeigt
   - Oder: Prüfe "Actions" Tab für "pages build and deployment" Workflow

4. **Teste die URL:**
   - `https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/`
   - Hash-basierte URLs: `https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/#/en/overview`

---

## 📋 Build-Konfiguration

### Aktuelle Konfiguration

**Build-Befehl:**
```bash
npm run build:github-pages
```

**Konfiguration:** `omf3/apps/ccu-ui/project.json` → `github-pages`

**Wichtige Einstellungen:**
- **Base Href:** `/ORBIS-Modellfabrik/`
- **Routing:** Hash-basiert (`/#/en/overview`)
- **i18n:** Runtime-Loading (keine Locale-Unterverzeichnisse)
- **Output:** `dist/apps/ccu-ui/browser/`

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

### Problem: GitHub Pages baut nicht automatisch neu

**Lösung:** Manuell in GitHub Settings einen neuen Build triggern:
1. Gehe zu: `https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/settings/pages`
2. Ändere die Branch-Einstellung (z.B. von `gh-pages` zu einem anderen Branch und zurück)
3. Oder: Warte auf den automatischen "pages build and deployment" Workflow

**Alternative:** Ein leerer Commit auf den `gh-pages` Branch kann auch einen neuen Build triggern.

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

**Letzte Aktualisierung:** 2025-12-13  
**Status:** ✅ Aktiv - Manuelles Deployment über GitHub UI
