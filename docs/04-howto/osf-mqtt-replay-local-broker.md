# OSF-UI: Replay-Broker (ORBIS-Standard / DAHEIM anpassen)

Die **Live**-Voreinstellung zeigt auf den **Shopfloor-RPi** (`192.168.0.100`). **Replay** kann denselben Broker nutzen (WebSocket, typisch Port **9001**).

Im Repo ist **`mqtt-user.defaults.ts`** standardmäßig auf **`192.168.0.100`** gesetzt (ORBIS / APS) — gleicher Host wie MQTT auf dem RPi für Arduino im ORBIS-Modus.

**DAHEIM** (z. B. Mosquitto `192.168.178.65`): `replayMqttHost` in dieser Datei lokal auf eure LAN-IP stellen oder nur in der App unter **Einstellungen** (wird in `localStorage` gespeichert und überschreibt die Defaults).

## Technische Anpassung (optional)

Datei: [`osf/apps/osf-ui/src/environments/mqtt-user.defaults.ts`](../../osf/apps/osf-ui/src/environments/mqtt-user.defaults.ts)

- `replayMqttHost`: IPv4 des Brokers (ORBIS: `192.168.0.100`; DAHEIM: z. B. `192.168.178.65`)
- `replayMqttPort`: WebSocket-Port (meist `9001`)
- Optional: `replayMqttUsername` / `replayMqttPassword`

`replayMqttHost` leer lassen → `localhost` für Replay.

## Dev-Server und SVG-Cache

`osf-ui:serve` setzt `Cache-Control: no-store` (siehe `project.json`), damit `/assets/…` beim Entwickeln nicht aus dem Browser-Disk-Cache mit veralteten SVG-Bytes kommt.
