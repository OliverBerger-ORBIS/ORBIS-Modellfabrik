/**
 * Optional developer defaults for the **Replay** MQTT connection (WebSocket in the browser).
 *
 * Default `replayMqttHost` is the **shopfloor RPi** (`192.168.0.100`) — same broker as **Live** and
 * as Arduino in ORBIS mode. For DAHEIM (e.g. LAN Mosquitto on 192.168.178.x), change this file locally
 * or use Settings (localStorage overrides these defaults).
 *
 * Leave `replayMqttHost` empty to use `localhost`.
 */
export const MQTT_USER_DEFAULTS = {
  replayMqttHost: '192.168.0.100',
  replayMqttPort: 9001,
  replayMqttUsername: undefined as string | undefined,
  replayMqttPassword: undefined as string | undefined,
};

/** @internal Exported for unit tests */
export function buildReplayConnectionDefaults(): {
  mqttHost: string;
  mqttPort: number;
  mqttPath?: string;
  mqttUsername?: string;
  mqttPassword?: string;
} {
  const host = MQTT_USER_DEFAULTS.replayMqttHost.trim();
  return {
    mqttHost: host || 'localhost',
    mqttPort: MQTT_USER_DEFAULTS.replayMqttPort,
    mqttPath: '',
    mqttUsername: MQTT_USER_DEFAULTS.replayMqttUsername,
    mqttPassword: MQTT_USER_DEFAULTS.replayMqttPassword,
  };
}
