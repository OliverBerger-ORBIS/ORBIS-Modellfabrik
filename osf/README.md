# OSF (ORBIS Shopfloor) — Angular Dashboard

Ziel
- Neue UI‑Implementierung in Angular (OSF) parallel zum bestehenden omf2.
- Business‑Funktionen bleiben funktional wie bisher; UI wird schrittweise ersetzt.
- omf2 bleibt bis zur vollständigen Migration unverändert und produktiv.

Branch‑Konzept
- Branch: `OSF`
- Neues Quellverzeichnis: `OSF/` (enthält neue Angular‑Sources, Docs, Skripte)
- omf2 bleibt bestehen und wird nicht verändert während Migration.

## Nx Workspace

- Node/Nx Setup liegt im Repo-Root (`package.json`, `nx.json`, `tsconfig.base.json`).
- Libraries werden unter `OSF/libs/*` verwaltet; Apps folgen später unter `OSF/apps/*`.
- Nützliche Befehle:
  - `npm install` – Dependencies aufsetzen
  - `nx graph` – Abhängigkeitsgraph der OSF-Module
  - `nx build mqtt-client` – TypeScript-Build der MQTT-Client-Library
- `nx serve osf-ui` – Mock-Dashboard mit Angular starten
- `nx test osf-ui` – Smoke-Test der UI-Komponenten
  - `npm run build:fixtures` – aktualisiert die Replay-Fixtures aus realen Sessions
- `nx serve osf-ui --configuration=development` – Entwicklungsserver (Locale `en`)
- `nx build osf-ui --configuration=production` – erstellt Bundles für `en`, `de`, `fr`

### Dashboard-Navigation & I18n

- Tabs: **Overview**, **Order**, **Process**, **Configuration**, **Module**
  - Overview zeigt das bestehende Fixture-Dashboard (Orders, Stock, Module, FTS).
  - Weitere Reiter sind vorbereitet und werden sukzessive mit Funktion gefüllt.
- Angular-i18n (`@angular/localize`) mit Locale-Dateien unter `OSF/apps/ccu-ui/src/locale/`
  - Quelle: `en`
  - Übersetzungen: `de`, `fr`
  - Build-Konfigurationen erzeugen alle drei Sprachen (`dist/apps/ccu-ui/<locale>`).

### Fixtures & Replay

- Rohdaten liegen unter `data/omf-data/sessions/production_order_*.log`.
- `scripts/build_order_fixtures.py` filtert die relevanten Topics (Orders/Module/FTS)
  und schreibt kompakte JSONL-Dateien nach `OSF/testing/fixtures/orders/<name>/orders.log`.
- `libs/testing-fixtures` stellt `createOrderFixtureStream()` bereit – der Angular Mock-Dashboard
  lädt diese Dateien als statische Assets (`/fixtures/orders/**`).
- Neue Aufzeichnungen: `python scripts/build_order_fixtures.py --only mixed` für selektiven Rebuild
  oder `npm run build:fixtures` für alle Pakete.

Sofort‑ToDos (MVP)
1. Projekt‑Scaffold
   - Angular skeleton, CI/CD placeholder, README + CONTRIBUTING.
2. MqttService (mqtt.js)
   - Live vs Replay toggle, reconnect/backoff, QoS/retain/LWT support.
3. RegistryService
   - REST‑Client zur Metadaten‑Abfrage (SVGs, topic‑mapping, display rules).
4. SvgCanvas
   - Inline SVG rendering, pan/zoom, entity components.
5. Auth & RBAC (initial: mock)
   - spätere Anbindung an OIDC/AAD; role guards.
6. Admin Module
   - Client list, retained inspector, publish tool, health checks.
7. Tests & QA
   - Unit, E2E, reconnect/flux tests, replay fidelity tests.
8. Ops
   - WSS proxy plan (falls nötig), TLS, monitoring, certs.

Akzeptanz‑Kriterien (MVP)
- UI kann zwischen Live‑Broker (192.168.0.100:1883 via WSS/proxy) und Replay umschalten.
- Gleiche Topics, QoS, Retain und LWT wie As‑Is.
- Initiale SVG‑Map zeigt korrekte Gerät‑States aus Broker‑Nachrichten.
- Admin: einfache Sicht auf retained messages + audit logging für Publishes.

Workflow
- Aufgaben werden als Issues/Tasks angelegt und Agenten (bzw. Menschen) zugewiesen.
- Kleine PRs in `OSF` für einzelne ToDos — Review → Merge in `OSF`.
- Finaler Cutover: When `OSF` has reached parity, plan to replace omf2.

Kontakt / Owner
- Owner: @OliverBerger-ORBIS
