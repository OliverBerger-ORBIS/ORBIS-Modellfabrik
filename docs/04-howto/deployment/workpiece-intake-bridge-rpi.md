# Workpiece Intake Bridge – Deploy auf den Shopfloor-RPi

**Kontext:** [DR-30](../../03-decision-records/30-workpiece-intake-mqtt-facade.md) · Code: `osf-workpiece-intake-bridge/`

Publiziert `osf/workpiece/intake` bei neuem DPS-NFC (Storage-Intake).

## Voraussetzungen

- SSH: `ff22@192.168.0.100`
- Docker-Compose APS unter `/home/ff22/fischertechnik/ff-central-control-unit/`
- Netzwerk `ff-future-factory-prod`, Broker-Hostname im Compose: `mqtt-broker`

## 1) Image bauen (Mac, armv7)

```bash
cd /path/to/ORBIS-Modellfabrik
docker buildx build --platform linux/arm/v7 \
  -t orbis-workpiece-intake-bridge:1.0.0 \
  -f osf-workpiece-intake-bridge/Dockerfile \
  osf-workpiece-intake-bridge --load

mkdir -p deploy/osf-workpiece-intake-bridge/docker-images
docker save orbis-workpiece-intake-bridge:1.0.0 \
  -o deploy/osf-workpiece-intake-bridge/docker-images/orbis-workpiece-intake-bridge-arm32-1.0.0.tar
```

## 2) Transfer + Load

```bash
scp deploy/osf-workpiece-intake-bridge/docker-images/orbis-workpiece-intake-bridge-arm32-1.0.0.tar \
  ff22@192.168.0.100:/tmp/

ssh ff22@192.168.0.100 \
  'docker load -i /tmp/orbis-workpiece-intake-bridge-arm32-1.0.0.tar'
```

## 3) Compose-Service

Snippet: `osf-workpiece-intake-bridge/docker-compose.snippet.yml`  
In `docker-compose-prod.yml` den Service `osf-workpiece-intake-bridge` ergänzen (gleicher File wie CCU/osf-ui) **oder** Repo-Stand von `integrations/APS-CCU/docker-compose-prod.yml` nach Pflege auf den Pi kopieren.

```bash
cd /home/ff22/fischertechnik/ff-central-control-unit
docker compose -f docker-compose-prod.yml up -d osf-workpiece-intake-bridge
docker logs -f osf-workpiece-intake-bridge-prod
```

Erwartung: `Subscribed module/v1/ff/NodeRed/SVR4H73275/state` und bei NFC: `Published osf/workpiece/intake …`.

## 4) Verifikation

```bash
ssh ff22@192.168.0.100 \
  "docker exec mqtt-broker-prod mosquitto_sub -h localhost -u default -P default -t 'osf/workpiece/intake' -v"
```

Am DPS ein Werkstück einlesen → eine JSON-Zeile mit `productRaw` + `nfc`.

## Partner-Kurzinfo (nur öffentlicher Vertrag)

- WebSocket: `ws://192.168.0.100:9001` (User/Pass `default`/`default`)
- Subscribe: `osf/workpiece/intake`
- Felder: `productRaw`, `nfc`, `timestamp` (kein `orderId`)
