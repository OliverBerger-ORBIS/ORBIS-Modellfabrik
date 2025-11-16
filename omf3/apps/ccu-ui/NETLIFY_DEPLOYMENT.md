# OMF3 Dashboard Deployment Guide

This guide provides options for deploying and testing the OMF3 Dashboard.

## 🚀 Quick Start: Local Testing (Empfohlen)

**Am einfachsten für lokale Tests ohne externe Services:**

```bash
npm run serve:local
```

Das war's! Die Anwendung läuft jetzt unter `http://localhost:4200` im Mock-Modus.

**Alternative Methoden:**
```bash
# Mit Shell-Script (Linux/Mac)
./scripts/serve-local.sh

# Mit Batch-Script (Windows)
scripts\serve-local.bat

# Oder manuell
npm run build:netlify
npx serve dist/apps/ccu-ui/browser -p 4200
```

**Hinweis:** Lokales Testing ist ideal wenn Firewall-Einschränkungen den Zugang zu Netlify oder anderen Cloud-Services verhindern.

## 🌐 GitHub Pages Test (Empfohlen für öffentliche Sites)

**Falls Sie eine öffentlich zugängliche Site benötigen und Netlify blockiert ist:**

### Schnelltest ob GitHub Pages erreichbar ist:

```bash
# Linux/Mac
npm run deploy:gh-pages-test

# Windows (manuell)
scripts\deploy-gh-pages-test.bat
```

Dieser Befehl:
1. Erstellt einen Build
2. Erstellt Branch `gh-pages-test`
3. Kopiert Build-Dateien
4. Pusht zum Repository

**Dann:**
1. Gehe zu: https://github.com/OliverBerger-ORBIS/ORBIS-Modellfabrik/settings/pages
2. Wähle Branch `gh-pages-test` / `/ (root)`
3. Nach 1-2 Minuten teste: https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/

Falls erreichbar → **GitHub Pages funktioniert!** ✅

**Detaillierte Anleitung:** Siehe `docs/github-pages-deployment.md`

## ☁️ Netlify Deployment (Optional)

Nur notwendig wenn GitHub Pages nicht verfügbar ist.

### Prerequisites

- Node.js and npm installed
- Netlify account (free tier is sufficient)

### Deployment Steps

### 1. Build the Application

```bash
npm run build:netlify
```

This creates an optimized build in `dist/apps/ccu-ui/browser/`.

### 2. Deploy to Netlify

#### Option A: CLI Deployment

```bash
# Install Netlify CLI (one-time)
npm install -g netlify-cli

# Login to Netlify (one-time)
netlify login

# Deploy
netlify deploy --prod --dir=dist/apps/ccu-ui/browser
```

#### Option B: Drag & Drop

1. Go to https://app.netlify.com
2. Click "Add new site" → "Deploy manually"
3. Drag the `dist/apps/ccu-ui/browser` folder to the upload area

## What's Included

The build includes everything needed for Netlify:

- ✅ Optimized JavaScript and CSS bundles
- ✅ SPA routing support via `_redirects` file
- ✅ Mock data fixtures for demo mode
- ✅ i18n locale files (German, French)
- ✅ All assets (icons, images, etc.)

## Expected Result

After deployment, you'll get a URL like:
```
https://<site-name>.netlify.app
```

The application will:
- Load in mock mode with sample data
- Support English, German, and French languages
- Work without any backend or MQTT connection
- Allow navigation between all tabs

## 🔄 Alternative Deployment Options

Wenn Netlify aufgrund von Firewall-Einschränkungen nicht verfügbar ist, siehe:

**`docs/deployment-alternatives.md`** für detaillierte Alternativen:
- Local Testing mit Static Server (einfachste Option)
- GitHub Pages
- Vercel
- Docker Container (für Intranet-Hosting)
- Internes Server-Hosting (Apache/Nginx)
- Zip-Datei zum Teilen mit Kollegen

## Troubleshooting

**Build fails?**
- Ensure all dependencies are installed: `npm install`
- Clear cache: `npx nx reset`

**Routing doesn't work on Netlify?**
- Check that `_redirects` file is in the build output
- Verify deployment directory is `dist/apps/ccu-ui/browser`

**Assets not loading?**
- Check browser console for errors
- Verify base href is `/` in index.html

## Full Documentation

For detailed documentation, see:
- `docs/netlify-deployment.md` - Netlify-specific guide
- `docs/deployment-alternatives.md` - Alternative hosting options

## Support

For issues or questions, refer to:
- Netlify documentation: https://docs.netlify.com/
- Angular deployment guide: https://angular.io/guide/deployment
