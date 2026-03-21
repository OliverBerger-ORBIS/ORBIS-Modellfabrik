# Analyse: baseHref und Fixture-Pfade – Bestandsaufnahme

**Datum:** 2026-03-16  
**Kontext:** baseHref-/Pfad-Probleme tauchen wiederholt auf. Fixes haben teilweise neue Fehler verursacht. **Kein weiterer Fix ohne klare Diagnose.**

---

## 1. Ziel dieser Analyse

- **Bestandsaufnahme** der aktuellen baseHref-Logik und aller betroffenen Stellen
- **Dokumentation** der Trade-offs und historischen Änderungen
- **Vermeidung** von Fixes, die bereits getestete Varianten reimplementieren und andere Fehler einführen

---

## 2. Aktuelle Architektur (Ist-Zustand)

### 2.1 Drei Deployment-Szenarien (DR 19)

| Szenario | Befehl | baseHref | Fixture-Pfade |
|----------|--------|----------|---------------|
| **Lokal (Dev)** | `npm run serve:osf-ui` | `/` | `/fixtures/orders/...` |
| **GitHub Pages** | CI/CD Build | `/ORBIS-Modellfabrik/` | `/ORBIS-Modellfabrik/fixtures/orders/...` |
| **Lokal (GP-Test)** | `npm run serve:local` | `/ORBIS-Modellfabrik/` | `/ORBIS-Modellfabrik/fixtures/orders/...` |

### 2.2 Stellen mit getBaseHref / baseHref-Logik

| Datei | Zweck | Erkennung |
|-------|-------|-----------|
| `osf/libs/testing-fixtures/src/index.ts` | Fixture-Fetch-Pfade | `hostname === 'oliverberger-orbis.github.io'` → `/ORBIS-Modellfabrik/`, sonst `<base href>` |
| `osf/apps/osf-ui/src/app/assets/detail-asset-map.ts` | SVG-Asset-Pfade | Gleiche Logik |
| `osf/apps/osf-ui/src/app/tabs/settings-tab.component.ts` | Export-Pfade | `getBaseHref()` aus detail-asset-map |
| `osf/apps/osf-ui/public/404.html` | Fallback-Seite | `hostname`-Check |

### 2.3 Quellen der baseHref-Werte

- **index.html (Source):** `<base href="/" />` – für Dev-Server
- **Production Build (github-pages):** Angular setzt `baseHref` via `project.json` → `<base href="/ORBIS-Modellfabrik/" />`
- **getBaseHref():** Liest entweder hostname (GitHub Pages) oder `<base>`-Tag

---

## 3. Bekannte Konflikte und Trade-offs

### 3.1 Port 4200 für serve:osf-ui und serve:local

**Beide nutzen Port 4200:**
- `serve:osf-ui` → `nx serve` → localhost:4200
- `serve:local` → `npx serve ... -p 4200` → localhost:4200

**Risiko:** Cache/Bookmark von serve:local kann beim Wechsel zu serve:osf-ui falsche HTML-Version liefern (baseHref `/ORBIS-Modellfabrik/` statt `/`).

### 3.2 Historische Fixes (aus Git)

| Commit | Änderung | Grund |
|--------|----------|-------|
| 10ca643 (Nov 2025) | getBaseHref + hostname-Check in detail-asset-map | SVG-Pfade schlugen auf GitHub Pages fehl |
| Später | Gleiche Logik in testing-fixtures | Fixtures brauchten gleiche baseHref-Erkennung |
| serve-local.js | Build in ORBIS-Modellfabrik/ kopieren | Production-Build erwartet baseHref-Pfad |

### 3.3 Was bereits versucht wurde (und warum vorsichtig sein)

- **Hostname-Check für GitHub Pages:** Notwendig, weil `<base>` auf GitHub Pages korrekt ist, aber Fetch/Asset-Pfade zur Laufzeit anders aufgelöst werden können
- **Base-Tag lesen für lokale Entwicklung:** Sollte `/` liefern bei serve:osf-ui
- **localhost-Hardcode:** Würde serve:local auf localhost brechen – dort ist baseHref `/ORBIS-Modellfabrik/` gewollt (URL: localhost:4200/ORBIS-Modellfabrik/)

---

## 4. Symptom: baseHref '/ORBIS-Modellfabrik/' bei serve:osf-ui

**Beobachtung:** Bei `npm run serve:osf-ui` erscheint in der Konsole `baseHref: '/ORBIS-Modellfabrik/'`.

**Mögliche Ursachen (ohne Code zu ändern prüfbar):**

1. **Falsche URL:** App unter `http://localhost:4200/ORBIS-Modellfabrik/` geöffnet statt `http://localhost:4200/`
2. **Cache:** Vorher serve:local genutzt → gecachtes HTML mit baseHref `/ORBIS-Modellfabrik/`
3. **Falscher Tab:** GitHub Pages in anderem Tab geöffnet, Konsole dort angesehen
4. **Browser-Extension:** Modifiziert base-Tag oder Pfade

**Erwartetes Verhalten bei korrektem serve:osf-ui:**
- URL: `http://localhost:4200/` oder `http://localhost:4200/#/en/dsp`
- index.html: `<base href="/" />`
- getBaseHref(): `/` (weil hostname !== github.io, base-Tag = "/")

---

## 5. Empfohlenes Vorgehen (ohne Code-Änderung)

### Schritt 1: Diagnose

1. **Hard-Refresh:** Ctrl+Shift+R (bzw. Cmd+Shift+R) auf localhost:4200
2. **URL prüfen:** Exakt `http://localhost:4200/` – kein `/ORBIS-Modellfabrik/` im Pfad
3. **Neuer Tab:** In neuem Inkognito-Tab `http://localhost:4200/` öffnen
4. **Konsole:** `document.querySelector('base')?.getAttribute('href')` und `window.location.hostname` ausgeben

### Schritt 2: Wenn Diagnose unklar

- **Logging temporär verstärken** (nur für Debug, nicht committen): In getBaseHref() hostname, base-Tag-Wert und Rückgabewert loggen
- **Ergebnis dokumentieren** – welcher Pfad führt zu welchem baseHref?

### Schritt 3: Fix erst nach klarer Ursache

- **Nicht** vorschnell localhost-Hardcode einbauen – das bricht serve:local auf localhost
- **Nicht** base-Tag-Logik ändern, ohne zu verstehen, warum sie aktuell falsch liefert

---

## 6. Debug-Logs in testing-fixtures

Aktuell vorhanden (können Konsole vollmüllen):
- `🔍 [testing-fixtures] resolvePath() CALLED for: ...`
- `[testing-fixtures] resolvePath() RESULT ...`
- `[testing-fixtures] baseHref: ...`
- `[testing-fixtures] Loading fixture: ...`
- `[testing-fixtures] Fetching fixture from: ...`

**Option:** Diese Logs nur bei `localStorage.getItem('OSF_DEBUG_FIXTURES') === 'true'` ausgeben – reduziert Rauschen, erhält Debug-Möglichkeit.

---

## 7. MessagePersistence-Warnung

`[MessagePersistence] Storage size limit reached, skipping persistence for ...`

- **Betrifft:** Nur localStorage-Persistenz von Nachrichten, nicht die Anzeige im Message Monitor
- **Kein baseHref-Bezug**
- Kann ignoriert oder separat adressiert werden

---

## 8. Referenzen

- [DR 19: OSF-UI Deployment-Strategie](../03-decision-records/19-osf-ui-deployment-strategy.md)
- [GitHub Pages Deployment](../04-howto/deployment/github-pages-deployment.md)
- [Build Commands Guide](build-commands-guide.md)
