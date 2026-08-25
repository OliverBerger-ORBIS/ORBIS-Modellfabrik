# ORBIS Workpiece Intake Bridge

Schlanker MQTT-Bridge-Container (Shopfloor-RPi): erkennt DPS **NFC-Abschluss** intern am APS und publiziert ein **ORBIS-Facade-Event**.

## Publish (öffentlich Vertrag)

| | |
|--|--|
| Topic | `osf/workpiece/intake` |
| Retain | nein |
| Payload | JSON |

```json
{
  "productRaw": "WHITE",
  "nfc": "92e0ad91595f63",
  "timestamp": "2026-08-07T09:11:46.905Z"
}
```

- Abonnenten: OD-Apps, künftig OSF-UI, … — ohne APS-Topic-Kenntnis
- Kein `orderId`: zum Intake-Zeitpunkt ist APS noch `"0"`; echte Order-UUID kommt später (FTS/CCU) und gehört nicht in dieses Facade-Event

## Intern (nur Bridge)

Subscribe (DPS Serial default `SVR4H73275`):

- `module/v1/ff/NodeRed/<serial>/state` (primär)
- `module/v1/ff/<serial>/state` (Fallback)

Trigger: `actionState.command=RGB_NFC` + `state=FINISHED` + `result` (NFC-ID) **and** a known color
(`metadata.type`, `metadata.workpiece.type`, or `loads[0].type`). APS often emits NFC first without
color (~1 s later with type) — the bridge waits and does **not** publish `UNKNOWN`.

## Lokal testen

```bash
cd osf-workpiece-intake-bridge
python -m pytest tests -q
```

## Image bauen (RPi armv7, wie OSF-UI)

```bash
# aus Repo-Root
docker buildx build --platform linux/arm/v7 -t orbis-workpiece-intake-bridge:1.0.0 \
  -f osf-workpiece-intake-bridge/Dockerfile osf-workpiece-intake-bridge --load
```

Deploy-Hilfe: [workpiece-intake-bridge-rpi.md](../docs/04-howto/deployment/workpiece-intake-bridge-rpi.md)

## Architektur-Kontext

- `osf/` = ORBIS-MQTT-Namespace (nicht synonym mit osf-ui)
- Langfristig kann DSP dasselbe Topic befüllen (CCU/Node-RED-Ablösung); Konsumenten bleiben stabil
- Siehe [DR-30](../docs/03-decision-records/30-workpiece-intake-mqtt-facade.md)
