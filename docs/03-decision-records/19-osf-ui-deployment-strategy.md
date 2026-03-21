# 19 – OSF-UI Deployment-Strategie

**Datum:** 2026-02-18  
**Status:** Accepted  
**Kontext:** Vereinheitlichung der Deployment-Dokumentation; Klärung von Deployment-Zielen, Betriebsmodi und Build-Strategie.

---

## Entscheidung

### Deployment-Ziele (drei Ziele)

| Ziel | Verwendung | Zugang |
|------|------------|--------|
| **Lokal** | Entwicklung, Test, Debug | `nx serve osf-ui` oder `npx serve dist/...` |
| **GitHub Pages** | Test für ORBIS-Mitarbeiter ohne Live-Anbindung | `https://oliverberger-orbis.github.io/ORBIS-Modellfabrik/` |
| **Docker auf RPi** | Produktive Nutzung am Shopfloor | `deploy/osf-ui/Dockerfile`, Port 8080 |

### Betriebsmodi (Environments) pro Deployment

| Deployment | Mock | Replay | Live |
|------------|------|--------|------|
| **Lokal** | ✅ Fixtures, Session Manager lokal | ✅ Replay-Station lokal | ✅ MQTT im lokalen Netz |
| **GitHub Pages** | ✅ Einziger zuverlässiger Modus (statisch) | ⚠️ Nur wenn Replay-Broker öffentlich erreichbar | ⚠️ Nur wenn MQTT-Broker erreichbar (VPN o.ä.) |
| **RPi** | ✅ Möglich, aber nicht Hauptnutzung | ✅ Bei Replay-Station im Netz | ✅ Primärer Modus |

### Build-Strategie

**Ein Build für alle Deployments.**

- **Gleicher Build-Inhalt:** Alle drei Environments (mock, replay, live) sind in jedem Build enthalten.
- **Deployment-spezifisch:** Nur `baseHref` und Auslieferung unterscheiden sich:
  - GitHub Pages: `--baseHref=/ORBIS-Modellfabrik/`
  - RPi / lokal: `--baseHref=/`
- **Kein env-spezifischer Build:** Es gibt keine separaten Builds „nur Mock“ oder „nur Live“. Gründe:
  - Einfacherer Build-Prozess, keine zusätzlichen Konfigurationen
  - Environment-Auswahl ist Laufzeit-Feature (localStorage, UI)
  - Reduktion des Bundle für GitHub Pages (nur Mock) wäre möglich, aber derzeit nicht umgesetzt
- **Fixtures im Production-Build (seit 2026-03):** Die Fixture-Assets (orders, modules, stock, flows, config, sensors) sind im Production-Build enthalten. Ermöglicht Mock-Fixture-Playback auf RPi – Demo ohne Hardware, vorbereitete Sessions für den digitalen Ablauf. Live-Modus unverändert.

---

## Alternativen

- **Deployment-spezifische Builds:** z.B. `production-github` mit nur Mock, `production-rpi` mit nur Live. Verworfen: Mehr Konfiguration, größerer Wartungsaufwand, geringer Nutzen (Mock-Daten sind klein).
- **Environment zur Build-Zeit entfernen:** z.B. Mock in RPi-Build ausblenden. Verworfen: Komplexität (fileReplacements, Conditional Imports) ohne klaren Mehrwert; Nutzer kann weiterhin Mock wählen für Demos.
- **Bestehendes deployment-alternatives.md beibehalten:** Verworfen: Inhalt in DR überführt, Dokumentation vereinheitlicht.

---

## Konsequenzen

### Positiv
- Klare, einheitliche Dokumentation der Deployment-Ziele
- Ein Build-Prozess für alle Ziele
- GitHub Pages ermöglicht Tests ohne lokale Installation

### Negativ
- GitHub Pages: Live/Replay für externe Nutzer in der Regel nicht nutzbar (kein Netzwerkzugang zum MQTT-Broker)

### Offene Punkte / Optionale Erweiterungen
- **GitHub Pages:** Falls später ein Replay-Broker öffentlich erreichbar wäre (z.B. über VPN oder Tunnel), könnte Replay auch auf GitHub Pages funktionieren.
- **RPi Default:** Derzeit wird die letzte Environment-Auswahl in localStorage gespeichert. Für RPi-Deployment könnte ein Default „live“ sinnvoll sein (bereits über EnvironmentService möglich).

---

## Implementierung

- [x] Deployment-Ziele dokumentiert
- [x] Build-Strategie festgelegt
- [x] `deployment-alternatives.md` durch diesen DR ersetzt
- [x] Fixtures in Production-Build (project.json) – Mock-Playback auf RPi (2026-03)
- [ ] Bei Bedarf: GitHub Pages Workflow um Build-Varianten erweitern (derzeit nicht geplant)

---

## Referenzen

- [GitHub Pages Deployment](../04-howto/deployment/github-pages-deployment.md)
- [Docker/RPi Deployment](../04-howto/deployment/) (Dockerfile: `deploy/osf-ui/`)
- EnvironmentService: `osf/apps/osf-ui/src/app/services/environment.service.ts`
