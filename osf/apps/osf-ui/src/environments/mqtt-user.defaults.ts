/**
 * Optional developer defaults for the **Replay** MQTT connection (WebSocket in the browser).
 *
 * Default `replayMqttHost` is the **shopfloor RPi** (`192.168.0.100`) — same broker as **Live** and
 * as Arduino in ORBIS mode. For DAHEIM (e.g. LAN Mosquitto on 192.168.178.x), change this file locally
 * or use Settings (localStorage overrides these defaults).
 *
 * Local dev on `localhost`/`127.0.0.1` automatically falls back to `localhost`
 * to keep replay smoke tests working without manual settings changes.
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
  const configuredHost = MQTT_USER_DEFAULTS.replayMqttHost.trim();
  const locationHost = typeof window !== 'undefined' ? window.location?.hostname : '';
  // Local/dev rule: unless the UI itself is served from the shopfloor RPi host,
  // prefer localhost for replay to avoid accidental cross-broker connections.
  const isLocalDevHost =
    locationHost === 'localhost' ||
    locationHost === '127.0.0.1' ||
    locationHost === '::1' ||
    (locationHost.length > 0 && locationHost !== '192.168.0.100');
  const host =
    isLocalDevHost && configuredHost === '192.168.0.100' ? 'localhost' : configuredHost || 'localhost';

  return {
    mqttHost: host,
    mqttPort: MQTT_USER_DEFAULTS.replayMqttPort,
    mqttPath: '',
    mqttUsername: MQTT_USER_DEFAULTS.replayMqttUsername,
    mqttPassword: MQTT_USER_DEFAULTS.replayMqttPassword,
  };
}
