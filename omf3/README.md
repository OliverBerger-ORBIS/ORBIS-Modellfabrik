# omf3 — Migration auf Angular

Ziel
- Neue UI‑Implementierung in Angular (omf3) parallel zum bestehenden omf2.
- Business‑Funktionen bleiben funktional wie bisher; UI wird schrittweise ersetzt.
- omf2 bleibt bis zur vollständigen Migration unverändert und produktiv.

Branch‑Konzept
- Branch: `omf3`
- Neues Quellverzeichnis: `omf3/` (enthält neue Angular‑Sources, Docs, Skripte)
- omf2 bleibt bestehen und wird nicht verändert während Migration.

## Nx Workspace

- Node/Nx Setup liegt im Repo-Root (`package.json`, `nx.json`, `tsconfig.base.json`).
- Libraries werden unter `omf3/libs/*` verwaltet; Apps folgen später unter `omf3/apps/*`.
- Nützliche Befehle:
  - `npm install` – Dependencies aufsetzen
  - `nx graph` – Abhängigkeitsgraph der OMF3-Module
  - `nx build mqtt-client` – TypeScript-Build der MQTT-Client-Library
  - `nx serve ccu-ui` – Mock-Dashboard mit Angular starten
  - `nx test ccu-ui` – Smoke-Test der UI-Komponenten
  - `npm run build:fixtures` – aktualisiert die Replay-Fixtures aus realen Sessions

### Fixtures & Replay

- Rohdaten liegen unter `data/omf-data/sessions/production_order_*.log`.
- `scripts/build_order_fixtures.py` filtert die relevanten Topics (Orders/Module/FTS)
  und schreibt kompakte JSONL-Dateien nach `omf3/testing/fixtures/orders/<name>/orders.log`.
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
- Kleine PRs in `omf3` für einzelne ToDos — Review → Merge in `omf3`.
- Finaler Cutover: When `omf3` has reached parity, plan to replace omf2.

Kontakt / Owner
- Owner: @OliverBerger-ORBIS
