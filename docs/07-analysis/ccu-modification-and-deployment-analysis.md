# Analyse: CCU-Quellen ändern und deployen

**Kontext:** Sprint 16 – ERP/MES Integration (Order/request mit request-ID, CCU sendet request-ack)  
**Frage:** Wie können wir den produktiven CCU-Code ändern und auf dem Raspberry Pi deployen?  
**Datum:** 2026-02-23  
**Update:** 2026-02-24 – Ein-Repo-Ansatz umgesetzt: 24V-Dev-Quellen in ORBIS-Modellfabrik integriert

---

## 1. Zusammenfassung

| Aspekt | Befund |
|--------|--------|
| **CCU-Location** | Docker-Container `central-control-prod` auf Raspberry Pi (192.168.0.100) |
| **Source-Upstream** | Fischertechnik [Agile-Production-Simulation-24V-Dev](https://github.com/fischertechnik/Agile-Production-Simulation-24V-Dev) (Branch `release`) |
| **Source in unserem Repo** | `integrations/APS-CCU/` – **vollständige 24V-Dev-Quelle** (central-control, common, nodeRed, mosquitto, frontend, scripts) |
| **Build/Deploy** | `cd integrations/APS-CCU && npm run docker:build` + `npm run docker:deploy` (oder Hybrid-Development) |
| **Vorteil** | Eine Cursor-Instanz, gemeinsame Entwicklung und Tests von OSF-UI + CCU im gleichen Repo |

---

## 2. CCU-Architektur (Stand)

### 2.1 Docker auf dem Raspberry Pi

| Container | Image | Rolle |
|-----------|-------|-------|
| central-control-prod | `ghcr.io/ommsolutions/ff-ccu-armv7:release-24v-v130` | CCU-Backend (Order-Management, FTS, MQTT) |
| central-control-frontend-prod | `ghcr.io/ommsolutions/ff-frontend-armv7:release-24v-v130` | Fischertechnik-Dashboard |
| mqtt-broker-prod | eclipse-mosquitto:2 | MQTT |
| nodered-prod | `ghcr.io/ommsolutions/ff-nodered-armv7:release-24v-v130` | OPC-UA ↔ MQTT |

**Start:** `start-services.sh` → `docker-compose -f docker-compose-prod.yml up -d`

**Bildquelle:** Vorgefertigte Images von OMM Solutions (Fischertechnik-Partner). **Es wird nicht aus lokalem Source gebaut**, sondern Images werden geladen (`pull_policy: never` = lokal vorhandene verwenden).

### 2.2 CCU Order-Flow (relevant für Sprint-16-Task)

```
1. Subscribes: ccu/order/request
2. Handler: modules/order/index.js → handleMessage()
3. orderId = uuid.v4()
4. sendResponse(orderRequest, orderId, productionDef) → ccu/order/response
```

**Datei:** `integrations/APS-CCU/central-control/src/modules/order/index.ts`

**Sprint-16-Anforderung:**
- DSP_Edge sendet `ccu/order/request` mit **requestId**
- CCU sendet **Order/request-ack** mit requestId + orderId (neu bzw. erweitert)

---

## 3. Source-Struktur: Ein-Repo-Ansatz (umgesetzt)

### 3.1 Aktuelle Struktur (`integrations/APS-CCU/`)

Die vollständige 24V-Dev-Quelle liegt nun in ORBIS-Modellfabrik:

```
integrations/APS-CCU/
├── central-control/     # CCU-Backend (TypeScript-Source)
│   ├── src/modules/order/   # ← Order-Handler hier
│   │   └── index.ts         # handleMessage, sendResponse
│   └── package.json
├── common/              # Protocol (CcuTopic, OrderRequest, etc.)
├── frontend/            # Fischertechnik Angular-Dashboard
├── nodeRed/              # OPC-UA ↔ MQTT Flows
├── mosquitto/            # MQTT-Config
├── raspberrypi/          # systemd-Service
├── scripts/              # Build/Deploy (build-images.js, deploy-to-rpi.js)
├── package.json          # docker:build, docker:deploy
├── DEPLOYMENT.md         # Detaillierte Anleitung
└── docker-compose-prod.yml
```

**Legacy:** Die frühere Teilkopie liegt in `integrations/APS-CCU-LEGACY/` (Archiv).

**Build:** `cd integrations/APS-CCU && npm run docker:build` erzeugt ARM-Images (QEMU-Kreuzkompilierung, ~40 Min)  
**Deploy:** `cd integrations/APS-CCU && npm run docker:deploy -- ff22@192.168.0.100` (SSH, scp, docker load)

---

## 4. Deployment-Optionen

### Option A: Vollständiger Build & Deploy (24V-Dev)

**Workflow:**
1. 24V-Dev klonen: `git clone -b release https://github.com/fischertechnik/Agile-Production-Simulation-24V-Dev.git`
2. Änderungen in `central-control/` (evtl. `common/`)
3. `npm run setup` (einmalig)
4. `npm run docker:build -- userdev central` (nur CCU, schneller)
5. `npm run docker:deploy -- ff22@192.168.0.100 userdev central`
6. Auf Pi: `docker compose -f docker-compose-prod.yml up -d`

**Voraussetzungen:** Docker buildx, Node 18.x, SSH zu 192.168.0.100

### Option B: Hybrid Development (CCU lokal, MQTT auf Pi)

**CCU lokal, MQTT auf dem Pi** – Entwicklung mit realem Fabrik-MQTT:
1. Auf Pi: `docker compose -f docker-compose-prod.yml stop central-control`
2. Lokal: `cd integrations/APS-CCU/central-control`, `.env` mit `MQTT_URL=mqtt://192.168.0.100:1883`
3. `npm start` – CCU läuft lokal, verbindet sich mit Pi-MQTT

**Vorteil:** Schneller Zyklus, echter Fabrik-Zustand. **Nachteil:** Pi muss erreichbar sein.

---

### Lokale Entwicklung (ohne Pi): Mosquitto wie Replay

**Grundprinzip:** Lokaler Mosquitto (gleich wie Session Manager / Replay) – **Entwicklung und Pi-Deployment bleiben getrennt.** Kein Pi im Netzwerk nötig, ideal für Home-Office.

| Komponente | Ort | MQTT | Referenz |
|------------|-----|------|----------|
| Mosquitto | Lokal (Homebrew) | TCP 1883, WebSocket 9001 | [mosquitto Setup](../04-howto/setup/mosquitto/README.md) |
| CCU | Lokal (Node) | `mqtt://localhost:1883` | `integrations/APS-CCU/central-control` |
| OSF-UI | Lokal | WebSocket `localhost:9001` | Replay-Umgebung in Settings |

### Variante A: E2E-Test Order/request (ohne Replay)

**Ziel:** requestId-Roundtrip testen – OSF-UI → CCU → Response.

1. **Mosquitto starten:** `brew services start mosquitto` (oder `mosquitto.conf.local-simple` nutzen)
2. **CCU starten:**
   ```bash
   cd integrations/APS-CCU/central-control
   npm install && MQTT_URL=mqtt://localhost:1883 npm start
   ```
3. **OSF-UI starten**, Replay-Umgebung wählen (→ `localhost:9001`), Order auslösen
4. **Prüfen:** `mosquitto_sub -h localhost -t 'ccu/order/#' -v`

**Ergebnis:** Vollständiger Test der requestId-Logik ohne Pi, ohne Docker-Build.

**Lagerbestand für Order-Test:** Die CCU prüft vor jeder Production-Order, ob Workpieces (BLUE, RED, WHITE) im HBW verfügbar sind. Ohne echte HBW-Hardware:
1. **Layout** mit HBW-DEMO setzen: `data/omf-data/test_topics/layout_hbw_demo.json`
2. **Preloads** senden (aus `data/omf-data/test_topics/preloads/`): `module_v1_ff_HBW-DEMO_connection.json`, `_factsheet.json`, `_state.json` – das **State-Topic** enthält den Lagerbestand im Feld `loads` (loadId, loadType, loadPosition, loadTimestamp)
3. Danach Orders – CCU bestätigt mit `ccu/order/response`

**Testskript:** `./data/omf-data/test_topics/test_order_flow.sh` führt den kompletten Ablauf aus.

**Modul-Registrierung:** Jedes Modul muss mit seiner **Serial-ID** das Factsheet-Topic senden: `module/v1/ff/<Serial>/factsheet`. Das Factsheet enthält u.a. `typeSpecification.moduleClass` (HBW, DRILL, …) und `loadSpecification` (Kapazität: loadPositions, loadSets mit maxAmount).

**Lagerbestand (HBW):** Die CCU liest den aktuellen Bestand aus `module/v1/ff/<HBW-Serial>/state` (Feld `loads`). Das Factsheet definiert nur die Kapazität; der tatsächliche Inhalt kommt aus dem State. *Hinweis:* Bei HBW könnte in manchen Implementierungen auch das Factsheet initiale Ladungsdaten enthalten – die aktuelle 24V-CCU nutzt jedoch ausschließlich das State-Topic.

**Kein MQTT-Topic zum direkten Setzen des Lagers** – Preloads simulieren Modul-Messages (connection, factsheet, state) auf `module/v1/ff/<Serial>/*`.

### Korrelation OSF-UI ↔ CCU

| Aspekt | OSF-UI | CCU |
|--------|--------|-----|
| **Order auslösen** | Publiziert `ccu/order/request` (type, orderType, timestamp) | Subscribes, prüft Lager |
| **Lagerbestand** | Liest `ccu/state/stock` (Anzeige) | Erhält von `module/v1/ff/+/state` (HBW loads) |
| **Order-Bestätigung** | Subscribes `ccu/order/response` | Reserviert Workpiece, publiziert Response |
| **Voraussetzung** | Replay-Umgebung → localhost:9001 | Lokal mit `MQTT_URL=mqtt://localhost:1883` |

**Ohne Lager:** CCU antwortet nicht mit Response, loggt „No workpiece available“. → Preloads senden.

### Variante B++: Replay-Umgebung (realistischer Fabrik-Zustand)

**Ziel:** OSF-UI mit aufgezeichneten Fabrik-Daten testen; CCU reagiert auf replayed/reale Messages.

1. **Wie Variante A** – Mosquitto + CCU lokal
2. **Session Manager** starten, **Replay Station** öffnen
3. **Session laden** (aus `data/omf-data/sessions/`), optional **Preloads** für Factsheets
4. **Replay abspielen** → MQTT-Traffic auf `localhost:1883`
5. **OSF-UI** (Replay-Umgebung) zeigt Fabrik-Zustand; **CCU** reagiert auf `ccu/order/request` aus Replay oder manuell getriggert
6. **Order testen:** Aus OSF-UI Order senden → CCU antwortet mit requestId

**Vorteil:** Realistische Modul-States, Factsheets, Connection-Topics – alles ohne Pi. Zusätzlich: [Replay Station](../04-howto/helper_apps/session-manager/replay-station.md).

---

### Option C: Pi-Deployment (nach lokaler Validierung)

→ Siehe **Option A** (Vollständiger Build & Deploy). Nach erfolgreichem Test mit Variante A/B++ auf Pi deployen.

---

## 5. Konkrete Änderungen für Sprint-16 (Order/request-ack)

### 5.1 Betroffene Stellen (in 24V-Dev)

| Datei | Änderung |
|-------|----------|
| `central-control/src/modules/order/index.ts` (bzw. .js) | `handleMessage`: `requestId` aus `orderRequest` lesen; an `sendResponse` übergeben |
| `central-control/src/modules/order/index.ts` | `sendResponse`: `requestId` in Response einbauen ODER separates Publish auf neues Topic |
| `common/protocol` (falls definiert) | Optional: OrderRequest-/Response-Typen um `requestId` erweitern |

### 5.2 Topic-Design

**Variante 1: ccu/order/response erweitern**
```json
{
  "orderId": "uuid",
  "requestId": "dsp-edge-123",   // NEU, optional
  "orderType": "PRODUCTION",
  "type": "BLUE",
  ...
}
```
- Pro: Kein neues Topic, rückwärtskompatibel (requestId optional)
- Contra: Alle Subscriber von ccu/order/response müssen ggf. angepasst werden

**Variante 2: Neues Topic ccu/order/request-ack**
```
ccu/order/request-ack  →  {"requestId":"...", "orderId":"...", "status":"ACK"}
```
- Pro: Klare Trennung, DSP_Edge kann gezielt subscriben
- Contra: Zusätzliches Topic, CCU muss zwei Publish-Calls machen (response + request-ack) oder response ersetzen

**Empfehlung:** Variante 1 (response erweitern), da OSF-UI und andere bereits `ccu/order/response` nutzen. `requestId` als optionales Feld – wenn nicht vorhanden, Verhalten wie bisher. **Bezeichnung:** `requestId` bleibt (neutral, semantisch u. a. für ERP-SAP-Customer-Order-ID nutzbar).

### 5.3 DSP_Edge / OSF-UI Anpassungen

- **DSP_Edge:** Beim Senden von `ccu/order/request` eine `requestId` (z.B. UUID) mitschicken
- **OSF-UI:** `sendCustomerOrder` in `osf/libs/business/src/index.ts` erweitern – optionales Feld `requestId` zum Payload hinzufügen
- **OSF-UI:** `ccu/order/response` weiterverwenden; wenn `requestId` vorhanden, kann sie Request-Ack-Logik nutzen (z.B. für ERP/MES-Callback)

---

## 6. Empfohlener Pfad

### Phase 1: Lokaler Test (ohne Pi) – Variante A, dann B++

1. **CCU-Quellen** in `integrations/APS-CCU/` (Ein-Repo)
2. **CCU anpassen:** `requestId` in `orderRequest` parsen, in `sendResponse` mitgeben
3. **OSF-UI erweitern:** `ccu/order/request` um optionale `requestId` ergänzen (Order-Service)
4. **Variante A:** Lokaler Mosquitto + lokale CCU + OSF-UI (Replay-Umgebung) → Order-Test, requestId-Roundtrip prüfen
5. **Variante B++** (optional): Session Manager Replay nutzen für realistischen Fabrik-Zustand
6. **MQTT prüfen:** `mosquitto_sub -h localhost -t 'ccu/order/#' -v`

**Trennung:** Entwicklung nutzt lokalen Mosquitto (wie Replay); Pi-Deployment bleibt separate Phase.

### Phase 2: Produktives Deployment

1. Änderungen in ORBIS-Modellfabrik committen (`integrations/APS-CCU/`)
2. `npm run docker:build -- userdev central`
3. `npm run docker:deploy -- ff22@192.168.0.100 userdev central`
4. Oder: Images in Registry pushen, auf Pi `docker compose pull && up -d`

### Phase 3: Repo-Strategie (umgesetzt)

→ **Ein-Repo-Ansatz:** 24V-Dev vollständig in ORBIS-Modellfabrik integriert (Abschnitt 7).

---

## 7. Repo-Strategie: Ein-Repo-Ansatz (umgesetzt)

**Entscheidung:** ORBIS-Modellfabrik enthält die vollständige 24V-Dev-Quelle – eine Cursor-Instanz für OSF-UI + CCU.

### Aktueller Stand

| Aspekt | Vorgehen |
|--------|----------|
| **Quell-Ort** | `integrations/APS-CCU/` (vollständige 24V-Dev-Struktur) |
| **Verwaltung** | Änderungen direkt im ORBIS-Modellfabrik-Repo |
| **Deployment** | `cd integrations/APS-CCU && npm run docker:build` bzw. `npm run docker:deploy` |
| **Rollback** | Zwei Optionen (siehe unten) |

**Vorteile:** Gemeinsame Entwicklung, keine separate Repo-Verwaltung, Upstream-Sync bei Bedarf möglich.

### Notfall-Rollback: Original wiederherstellen

| Variante | Vorgehen |
|----------|----------|
| **A: Image zurück** | `docker-compose-prod.yml` auf dem Pi anpassen: Image von `orbis-ccu:v1` zurück auf `ghcr.io/ommsolutions/ff-ccu-armv7:release-24v-v130`. Nach `docker compose up -d` läuft wieder die unveränderte Version (sofern das Image noch vorhanden ist). |
| **B: Tag im Repo** | Nach dem ersten Clone: `git tag orbis-baseline-24v-release`. Bei Bedarf: Checkout dieses Tags, neu bauen, neu deployen. |

**Praktisch:** Option A ist der schnellste Rollback – nur `docker-compose-prod.yml` ändern, Container neu starten. Die Original-Images von OMM Solutions bleiben als Fallback erhalten.

### RPi-Projektpfad (dokumentiert)

**Quelle:** [24V-Dev raspberrypi/fischer-techik.service](https://github.com/fischertechnik/Agile-Production-Simulation-24V-Dev/blob/release/raspberrypi/fischer-techik.service)

```
WorkingDirectory=/home/ff22/fischertechnik/ff-central-control-unit
```

Dieser Pfad ist in der offiziellen systemd-Service-Datei festgelegt. Unser Repo hat eine Kopie: `integrations/APS-CCU/raspberrypi/fischer-techik.service`. Ob der Pi tatsächlich so eingerichtet ist, prüft man mit:

```bash
ssh ff22@192.168.0.100 "ls -la /home/ff22/fischertechnik/"
```

**Weitere Prüfpunkte:** Docker-Compose-Vergleich (unser vs. Pi), Credentials siehe [credentials.md](../credentials.md) und DEPLOYMENT.md.

---

## 8. Referenzen

- [Order-Request: Erweiterung um requestId](./order-requestid-extension.md) – requestId-Roundtrip, Sequenzdiagramm
- [Fischertechnik 24V-Dev: Tests und Lagerbestand](./fischertechnik-24v-dev-testing-and-stock.md) – Testing-Doku, SET_STORAGE, BLOCKED-Analyse
- [FISCHERTECHNIK-OFFICIAL](../06-integrations/FISCHERTECHNIK-OFFICIAL.md) – Repo-Zuordnung
- [ccu-backend-orchestration](../06-integrations/00-REFERENCE/ccu-backend-orchestration.md) – Order-Flow Details
- [Mosquitto lokale Setup](../04-howto/setup/mosquitto/README.md) – Lokaler MQTT-Broker (Replay & Entwicklung)
- [Replay Station](../04-howto/helper_apps/session-manager/replay-station.md) – Session-Replay für Variante B++
- [DEPLOYMENT.md (24V-Dev)](https://github.com/fischertechnik/Agile-Production-Simulation-24V-Dev/blob/release/DEPLOYMENT.md) – Offizielle Anleitung
- [Sprint 16](../sprints/sprint_16.md) – ERP/MES Integration Task
