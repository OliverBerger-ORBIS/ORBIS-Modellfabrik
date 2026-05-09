import { buildReplayConnectionDefaults, MQTT_USER_DEFAULTS } from '../mqtt-user.defaults';

describe('mqtt-user.defaults', () => {
  it('should default to localhost replay host on local dev', () => {
    expect(MQTT_USER_DEFAULTS.replayMqttHost).toBe('192.168.0.100');
    const c = buildReplayConnectionDefaults();
    expect(c.mqttHost).toBe('localhost');
    expect(c.mqttPort).toBe(9001);
  });

  it('should keep shopfloor host when served from shopfloor host', () => {
    const originalWindow = globalThis.window;
    Object.defineProperty(globalThis, 'window', {
      value: { location: { hostname: '192.168.0.100' } },
      configurable: true,
      writable: true,
    });

    const c = buildReplayConnectionDefaults();
    expect(c.mqttHost).toBe('192.168.0.100');

    Object.defineProperty(globalThis, 'window', {
      value: originalWindow,
      configurable: true,
      writable: true,
    });
  });
});
