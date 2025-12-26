# Deployment Options for OSF Dashboard

This guide provides options for hosting and testing the OSF Dashboard with mock fixtures.

## Option 1: Local Development (Empfohlen für Entwicklung)

**Local Builds erfolgen direkt aus der IDE heraus:**

### Entwicklungsserver

```bash
# Development-Server starten (aus IDE)
nx serve osf-ui
```

Die Anwendung ist dann unter `http://localhost:4200` erreichbar.

**Vorteile:**
- ✅ Hot Reload während der Entwicklung
- ✅ Keine Firewall-Probleme
- ✅ Sofort verfügbar
- ✅ Direkt aus IDE startbar

**Nachteile:**
- ❌ Nur lokal erreichbar (nicht für Remote-Kollegen)
- ❌ Server läuft nur während der Sitzung

### Local Production Build (für Tests)

```bash
# Production Build erstellen
nx build osf-ui --configuration=production

# Lokal hosten mit serve
npx serve dist/apps/osf-ui/browser -p 4200
```

Die Anwendung ist dann unter `http://localhost:4200` erreichbar.

## Option 2: GitHub Pages (Automatisch via CI/CD)

**Status:** ✅ Aktiv - Deployment erfolgt automatisch bei erfolgreichen Commits auf `main` Branch

GitHub Pages wird automatisch über GitHub Actions deployed. Bei jedem erfolgreichen Commit auf den `main` Branch wird die Anwendung automatisch gebaut und auf GitHub Pages deployed.

**Workflow:** `.github/workflows/deploy.yml`

**Trigger:**
- Push auf `main` Branch (wenn `osf/**`, `package.json` oder `.github/workflows/deploy.yml` geändert wurden)
- Manuell via `workflow_dispatch`

**Deployment-URL:** `https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/`

**Vorteile:**
- ✅ Vollautomatisch bei jedem Commit
- ✅ Kostenlos
- ✅ HTTPS automatisch
- ✅ Öffentlich erreichbar (auch ohne Repository-Zugriff)
- ✅ Schnelles CDN
- ✅ Keine manuelle Arbeit erforderlich

**Nachteile:**
- ❌ Repository muss öffentlich sein (oder GitHub Pro)
- ❌ Deployment erfolgt nur bei erfolgreichen Commits

**Details:** Siehe [docs/04-howto/deployment/github-pages-deployment.md](04-howto/deployment/github-pages-deployment.md)

## Option 3: Docker Container (Geplant für Rasp-Pi / Hilcher-Box)

**Status:** ⏳ Geplant (siehe Task 20 in PROJECT_STATUS.md)

Docker-basiertes Deployment für Raspberry Pi oder Hilcher-Box als Teil des DSP-Kastens.

**Geplante Verwendung:**
- Deployment auf Raspberry Pi oder Hilcher-Box
- Teil des DSP-Kastens
- Intranet-Hosting ohne Internet-Zugang

**Details:** Wird in Task 20 implementiert (siehe `docs/PROJECT_STATUS.md`)

**Vorteile (geplant):**
- ✅ Läuft auf jedem Server mit Docker
- ✅ Einfach zu teilen (Docker Image)
- ✅ Kann im Intranet gehostet werden
- ✅ Produktionsreif
- ✅ Integriert in DSP-Kasten

**Nachteile:**
- ❌ Benötigt Docker-Installation
- ❌ Benötigt Server-Zugang

## Option 4: Zip-Datei zum Teilen

Für einfaches Teilen mit Kollegen:

```bash
# Build erstellen
nx build osf-ui --configuration=production

# Zip erstellen
cd dist/apps/osf-ui/browser
zip -r osf-dashboard.zip .
```

Kollegen können die Zip-Datei entpacken und mit einem beliebigen Static Server öffnen:

```bash
# Nach dem Entpacken
cd osf-dashboard
npx serve -p 4200
```

Oder als HTML-Datei direkt im Browser öffnen (funktioniert mit Einschränkungen beim Routing).

## Option 5: Internes Server-Hosting

Falls ein interner Webserver verfügbar ist (Apache, Nginx, IIS):

### Apache (.htaccess für SPA-Routing)

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```

### Nginx (nginx.conf für SPA-Routing)

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

**Vorteile:**
- ✅ Volle Kontrolle
- ✅ Intranet-Zugang möglich
- ✅ Professionell

**Nachteile:**
- ❌ Benötigt Server-Zugang
- ❌ Benötigt Admin-Rechte

## Empfehlung

Für **lokale Entwicklung**:
→ **Option 1** (Development-Server aus IDE) ist am einfachsten

Für **automatisches öffentliches Hosting**:
→ **Option 2** (GitHub Pages via CI/CD) - automatisch bei jedem Commit

Für **Intranet-Hosting**:
→ **Option 3** (Docker Container auf Rasp-Pi/Hilcher-Box) - geplant für Task 20

Für **Teilen mit Kollegen ohne Server**:
→ **Option 4** (Zip-Datei) zum manuellen Starten

Für **permanente Hosting-Lösung**:
→ **Option 5** (Interner Server) oder **Option 2** (GitHub Pages)

## Quick Start: Lokales Testen

Die einfachste Methode zum sofortigen Testen:

```bash
# Development-Server aus IDE starten
nx serve osf-ui

# Oder Production Build lokal testen
nx build osf-ui --configuration=production
npx serve dist/apps/osf-ui/browser -p 4200

# Browser öffnen
# → http://localhost:4200
```

Die Anwendung läuft jetzt im Mock-Modus mit allen Fixtures.

## Fehlerbehebung

**Problem: SPA-Routing funktioniert nicht**
- Lösung: Nutze einen Server mit `try_files` Support (Nginx, Apache mit mod_rewrite)
- Workaround: Nutze `npx serve` mit dem `--single` Flag

**Problem: Assets laden nicht**
- Lösung: Stelle sicher, dass `baseHref` in der Build-Konfiguration korrekt ist (`/ORBIS-Modellfabrik/` für GitHub Pages)
- Prüfe, ob der Build-Output korrekt ist (`dist/apps/osf-ui/browser/`)

**Problem: Locale-Dateien laden nicht**
- Lösung: Prüfe, ob `/locale/messages.{de|en|fr}.json` im Build vorhanden ist
- Stelle sicher, dass der Server JSON-Dateien ausliefert
