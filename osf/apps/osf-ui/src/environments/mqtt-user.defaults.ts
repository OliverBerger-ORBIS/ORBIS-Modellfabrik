/**
 * Optional developer defaults for the **Replay** MQTT connection (WebSocket in the browser).
 *
 * Set `replayMqttHost` to the **same Mosquitto** IPv4 your Arduino uses (TCP 1883), with WebSocket
 * enabled on `replayMqttPort` (typically 9001). Then Replay and hardware share one broker — subscribe
 * and publish (e.g. sensor station config) work without using **Live** (shopfloor RPi preset).
 *
 * Leave `replayMqttHost` empty to use `localhost` (or configure via Settings → persisted in
 * localStorage, which still overrides these defaults).
 */
export const MQTT_USER_DEFAULTS = {
  replayMqttHost: '192.168.178.65',
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
