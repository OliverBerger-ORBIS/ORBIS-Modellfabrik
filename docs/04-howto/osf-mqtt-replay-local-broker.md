# OSF-UI: Replay-Broker (DAHEIM / gleicher Mosquitto wie Arduino)

Die **Live**-Voreinstellung in der App zeigt auf den **Shopfloor-RPi** (`192.168.0.100`). Zu Hause ist dieser Host in der Regel **nicht** erreichbar.

Für **bidirektionale** MQTT-Nutzung mit der Sensor-Station (Telemetrie + z. B. `osf/arduino/station/config`) muss die **Replay**-Verbindung auf **denselben Broker** zeigen, den der Arduino per **TCP 1883** nutzt — im Browser nur per **WebSocket** (typisch Port **9001** auf Mosquitto).

## Technische Anpassung (Code, einmal pro Rechner)

Datei: [`osf/apps/osf-ui/src/environments/mqtt-user.defaults.ts`](../../osf/apps/osf-ui/src/environments/mqtt-user.defaults.ts)

- `replayMqttHost`: IPv4 eures **LAN-Mosquitto** (Beispiel: `192.168.178.65`)
- `replayMqttPort`: WebSocket-Port (meist `9001`)
- Optional: `replayMqttUsername` / `replayMqttPassword`, wenn der Broker Auth verlangt

Leer lassen = bisheriges Standardverhalten (`localhost:9001`). **Settings** in der UI und `localStorage` überschreiben diese Defaults weiterhin.

## Alternativ

Verbindung nur in der App unter **Einstellungen** setzen (ohne Datei-Edit) — gleiche Wirkung, wenn kein Eintrag in `mqtt-user.defaults.ts` gesetzt ist.

## Dev-Server und SVG-Cache

`osf-ui:serve` setzt `Cache-Control: no-store` (siehe `project.json`), damit `/assets/…` beim Entwickeln nicht aus dem Browser-Disk-Cache mit veralteten SVG-Bytes kommt.
