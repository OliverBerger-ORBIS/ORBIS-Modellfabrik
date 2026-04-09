import { buildReplayConnectionDefaults, MQTT_USER_DEFAULTS } from '../mqtt-user.defaults';

describe('mqtt-user.defaults', () => {
  it('should use configured replay broker host and WebSocket port', () => {
    expect(MQTT_USER_DEFAULTS.replayMqttHost).toBe('192.168.0.100');
    const c = buildReplayConnectionDefaults();
    expect(c.mqttHost).toBe('192.168.0.100');
    expect(c.mqttPort).toBe(9001);
  });
});
