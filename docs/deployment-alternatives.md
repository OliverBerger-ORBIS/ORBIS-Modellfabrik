# Alternative Deployment Options for OMF3 Dashboard

This guide provides alternatives to Netlify for hosting and testing the OMF3 Dashboard with mock fixtures.

## Option 1: Local Testing with Static Server (Empfohlen für Tests)

Der einfachste Weg, die Anwendung lokal zu testen, ohne externe Services:

### Methode A: Mit `serve` (npm package)

```bash
# Build erstellen
npm run build:netlify

# Lokal hosten
npx serve dist/apps/ccu-ui/browser -p 4200
```

Die Anwendung ist dann unter `http://localhost:4200` erreichbar.

**Vorteile:**
- ✅ Keine Firewall-Probleme
- ✅ Keine Registrierung erforderlich
- ✅ Sofort verfügbar
- ✅ Gleiche Funktionalität wie Netlify

**Nachteile:**
- ❌ Nur lokal erreichbar (nicht für Remote-Kollegen)
- ❌ Server läuft nur während der Sitzung

### Methode B: Mit Python HTTP Server

```bash
# Build erstellen
npm run build:netlify

# Lokal hosten mit Python 3
cd dist/apps/ccu-ui/browser
python -m http.server 4200
```

Oder mit Python 2:
```bash
cd dist/apps/ccu-ui/browser
python -m SimpleHTTPServer 4200
```

**Hinweis:** Für SPA-Routing funktioniert `_redirects` nicht mit Python's HTTP Server. 
Lösung: Nutze Hash-basiertes Routing oder Methode A.

### Methode C: Mit Live Server (VSCode Extension)

1. Build erstellen: `npm run build:netlify`
2. VSCode öffnen im Verzeichnis `dist/apps/ccu-ui/browser`
3. Rechtsklick auf `index.html` → "Open with Live Server"

## Option 2: GitHub Pages

Falls GitHub zugelassen ist, kann GitHub Pages verwendet werden:

### Setup

1. Build erstellen:
```bash
npm run build:netlify
```

2. GitHub Pages Branch erstellen:
```bash
# Neuen Branch erstellen
git checkout --orphan gh-pages

# Build-Dateien kopieren
cp -r dist/apps/ccu-ui/browser/* .

# Committen und pushen
git add .
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages
```

3. In GitHub Repository Settings:
   - Gehe zu "Settings" → "Pages"
   - Source: "Deploy from a branch"
   - Branch: `gh-pages` / `(root)`
   - Save

Die Anwendung ist dann unter `https://<username>.github.io/<repo-name>/` verfügbar.

**Vorteile:**
- ✅ Kostenlos
- ✅ HTTPS
- ✅ Für Kollegen erreichbar (mit Repository-Zugriff)

**Nachteile:**
- ❌ Benötigt GitHub-Zugriff
- ❌ Manuelles Deployment

## Option 3: Vercel

Alternative zu Netlify mit ähnlicher Funktionalität:

### Setup

```bash
# Vercel CLI installieren
npm install -g vercel

# Anmelden
vercel login

# Build erstellen
npm run build:netlify

# Deployen
vercel --prod dist/apps/ccu-ui/browser
```

**Vorteile:**
- ✅ Ähnlich wie Netlify
- ✅ Kostenloser Free Tier
- ✅ Einfaches Deployment

**Nachteile:**
- ❌ Könnte auch von Firewall blockiert sein
- ❌ Benötigt Account-Registrierung

## Option 4: Docker Container (Empfohlen für Intranet-Hosting)

Ideal für interne Server ohne Internet-Zugang:

### Dockerfile erstellen

```dockerfile
# Datei: Dockerfile
FROM nginx:alpine

# Build-Dateien kopieren
COPY dist/apps/ccu-ui/browser /usr/share/nginx/html

# Nginx-Konfiguration für SPA
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
```

### Verwendung

```bash
# Build erstellen
npm run build:netlify

# Docker Image erstellen
docker build -t omf3-dashboard .

# Container starten
docker run -d -p 8080:80 omf3-dashboard
```

Die Anwendung ist dann unter `http://localhost:8080` erreichbar.

**Vorteile:**
- ✅ Läuft auf jedem Server mit Docker
- ✅ Einfach zu teilen (Docker Image)
- ✅ Kann im Intranet gehostet werden
- ✅ Produktionsreif

**Nachteile:**
- ❌ Benötigt Docker-Installation
- ❌ Benötigt Server-Zugang

## Option 5: Zip-Datei zum Teilen

Für einfaches Teilen mit Kollegen:

```bash
# Build erstellen
npm run build:netlify

# Zip erstellen
cd dist/apps/ccu-ui/browser
zip -r omf3-dashboard.zip .
```

Kollegen können die Zip-Datei entpacken und mit einem beliebigen Static Server öffnen:

```bash
# Nach dem Entpacken
cd omf3-dashboard
npx serve -p 4200
```

Oder als HTML-Datei direkt im Browser öffnen (funktioniert mit Einschränkungen beim Routing).

## Option 6: Internes Server-Hosting

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

Für **lokale Tests**:
→ **Option 1A** (`npx serve`) ist am einfachsten und schnellsten

Für **Teilen mit Kollegen im Intranet**:
→ **Option 4** (Docker Container) ist am professionellsten und einfachsten zu teilen

Für **Teilen mit Kollegen ohne Server**:
→ **Option 5** (Zip-Datei) zum manuellen Starten

Für **permanente Hosting-Lösung**:
→ **Option 6** (Interner Server) oder **Option 2** (GitHub Pages, falls erlaubt)

## Quick Start: Lokales Testen

Die einfachste Methode zum sofortigen Testen:

```bash
# 1. Build erstellen
npm run build:netlify

# 2. Lokal hosten
npx serve dist/apps/ccu-ui/browser -p 4200

# 3. Browser öffnen
# → http://localhost:4200
```

Die Anwendung läuft jetzt im Mock-Modus mit allen Fixtures und funktioniert genauso wie auf Netlify.

## Fehlerbehebung

**Problem: SPA-Routing funktioniert nicht**
- Lösung: Stelle sicher, dass der Server die `_redirects` Datei unterstützt (Netlify, Vercel)
- Alternative: Nutze einen Server mit `try_files` Support (Nginx, Apache mit mod_rewrite)
- Workaround: Nutze `npx serve` mit dem `--single` Flag

**Problem: Assets laden nicht**
- Lösung: Stelle sicher, dass `base href="/"` in der `index.html` steht
- Prüfe, ob der Build-Output korrekt ist

**Problem: Locale-Dateien laden nicht**
- Lösung: Prüfe, ob `/locale/messages.{de|fr}.json` im Build vorhanden ist
- Stelle sicher, dass der Server JSON-Dateien ausliefert
