# RPi Deployment – CCU + OSF-UI

**Kontext:** Vollständiges Deployment der ORBIS-SmartFactory auf dem Raspberry Pi (Shopfloor).  
**Komponenten:** CCU (Central Control), OSF-UI (ORBIS Dashboard), Node-RED, Mosquitto

---

## Übersicht

| Komponente | Image | Port | Beschreibung |
|------------|-------|------|--------------|
| CCU | ff-ccu-armv7 | – | Order-Management, FTS, MQTT-Protokoll |
| OSF-UI | orbis-osf-ui | 8080 | ORBIS Dashboard (Angular) |
| Node-RED | ff-nodered-armv7 | 1880 | OPC-UA ↔ MQTT |
| Mosquitto | eclipse-mosquitto | 1883 | MQTT-Broker |

---

## CCU deployen (v1.3.0-osf.2)

**Quelle:** `integrations/APS-CCU/`  
**Doku:** [integrations/APS-CCU/DEPLOYMENT.md](../../../integrations/APS-CCU/DEPLOYMENT.md)

```bash
cd integrations/APS-CCU
npm run docker:build v1.3.0-osf.2 central
npm run docker:deploy -- ff22@192.168.0.100 v1.3.0-osf.2 central
# Passwort bei Aufforderung: ff22+
```

---

## OSF-UI deployen

**Quelle:** Repo-Root  
**Version:** Single Source of Truth = `package.json` → Build schreibt in `version.ts`, Deploy nutzt package.json-Version als Image-Tag.

**Verhalten (wie CCU):** Immer frisch bauen, Image mit Version taggen, auf Pi laden, Compose (Image-Zeile) aktualisieren, `docker compose up -d` → Container wird neu erstellt, weil Image-Referenz sich ändert.

**Plattform:** Default = armv7 (32-bit, wie CCU ff-*-armv7). Bei 64-bit RPi: `OSF_UI_RPI_PLATFORM=arm npm run docker:osf-ui:deploy -- …`

**Erstes Mal:** Compose-Datei auf den Pi kopieren (enthält osf-ui-Service):

```bash
scp integrations/APS-CCU/docker-compose-prod.yml ff22@192.168.0.100:/home/ff22/fischertechnik/ff-central-control-unit/
```

### Deploy (ein Befehl – baut, transferiert, lädt, startet)

```bash
# Aus Repo-Root – Version aus package.json
npm run docker:osf-ui:deploy -- ff22@192.168.0.100

# Optional: Andere Version deployen
npm run docker:osf-ui:deploy -- ff22@192.168.0.100 0.8.9
```

Das Skript macht: Build (update-version + Angular + Docker), Save, SCP, Load, sed Compose (orbis-osf-ui:TAG), `docker compose up -d`.

---

## OSF-UI – Release/Deployment Checkliste (kurz)

- **Version bump**: Nur `package.json` (Repo-Root) ändern, dann:

```bash
npm run update-version
```

- **Unit Tests (schnell)**:

```bash
npx nx test osf-ui --testPathPattern="track-trace|shopfloor-tab"
```

- **Production Build (RPi)**:

```bash
npx nx run osf-ui:build:production
```

- **Deploy auf den Pi**:

```bash
npm run docker:osf-ui:deploy -- ff22@192.168.0.100
```

- **Verifikation**:
  - **OSF-UI URL**: `http://192.168.0.100:8080`
  - **Container läuft**:

```bash
ssh ff22@192.168.0.100 "docker ps | grep osf-ui"
```

---

## Vollständiger Deploy (CCU + OSF-UI)

```bash
# 0. Compose auf Pi (erstes Mal oder nach Änderungen an docker-compose-prod.yml)
scp integrations/APS-CCU/docker-compose-prod.yml ff22@192.168.0.100:/home/ff22/fischertechnik/ff-central-control-unit/

# 1. CCU
cd integrations/APS-CCU
npm run docker:build v1.3.0-osf.2 central
npm run docker:deploy -- ff22@192.168.0.100 v1.3.0-osf.2 central

# 2. OSF-UI (aus Repo-Root – baut, transferiert, lädt, sed Compose, compose up -d)
cd ../..
npm run docker:osf-ui:deploy -- ff22@192.168.0.100
```

---

## Fehlerbehebung: Port 8080 belegt

**Fehler:** `Bind for 0.0.0.0:8080 failed: port is already allocated`

**Ursache (typisch):** Alter osf-ui-Container aus früherem Standalone-Deploy (`docker-compose.osf-ui.yml`) läuft noch und belegt Port 8080.

**Vorgehen:**

```bash
# 1. Alte osf-ui-Container stoppen und entfernen
ssh ff22@192.168.0.100 "docker stop osf-ui osf-ui-prod 2>/dev/null; docker rm osf-ui osf-ui-prod 2>/dev/null"

# 2. Alle Services neu starten (inkl. neue osf-ui aus docker-compose-prod)
ssh ff22@192.168.0.100 "cd /home/ff22/fischertechnik/ff-central-control-unit && docker compose -f docker-compose-prod.yml up -d"
```

**Hinweis:** Der Pfad `/home/ff22/fischertechnik/ff-central-control-unit` entspricht `REMOTE_DIR` in `integrations/APS-CCU/scripts/deploy-to-rpi.js`. Bei anderem Pi-Setup dort anpassen.

**Prüfen:** `ssh ff22@192.168.0.100 "docker ps | grep osf-ui"` – nur `osf-ui-prod` soll laufen.

**Nicht:** Auf einen anderen Port ausweichen – alte Container stoppen.

---

## Verifikation

- **OSF-UI:** http://192.168.0.100:8080 (oder raspberrypi.local:8080)
- **CCU/Frontend:** Port 80 (Fischertechnik-Dashboard)
- **MQTT:** Port 1883, WebSocket 9001

---

## Referenzen

- [DR-19: OSF-UI Deployment-Strategie](../../03-decision-records/19-osf-ui-deployment-strategy.md)
- [CCU DEPLOYMENT.md](../../../integrations/APS-CCU/DEPLOYMENT.md)
- [DR-21: CCU OSF-Versionierung](../../03-decision-records/21-ccu-osf-versioning.md)
