import { describe, expect, it } from 'vitest';
import { ServiceConfig } from '../config';
import { normalizeMessage } from '../normalizer';
import { createSensorPolicyState } from '../sensorPolicy';

const baseConfig: ServiceConfig = {
  mqtt: { host: 'localhost', port: 1883, clientId: 'test-client' },
  postgres: { host: 'localhost', port: 5432, db: 'osf', user: 'osf', password: 'osf' },
  runtime: {
    mode: 'replay',
    rawRetentionDays: 14,
    sensorIntervalSeconds: 3600,
    enableRawMessages: true,
    enableCameraTopic: false,
    logLevel: 'debug',
  },
};

describe('normalizeMessage', () => {
  it('ignores camera topic when camera persistence is disabled', () => {
    const result = normalizeMessage({
      config: baseConfig,
      topic: '/j1/txt/1/i/cam',
      payloadText: JSON.stringify({ payload: { image: 'base64' } }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-05-08T10:00:00.000Z'),
      sensorPolicyState: createSensorPolicyState(),
    });
    expect(result).toBeUndefined();
  });

  it('normalizes order completed into order + steps + events', () => {
    const payload = [
      {
        orderId: 'order-1',
        orderType: 'PRODUCTION',
        type: 'BLUE',
        state: 'COMPLETED',
        workpieceId: 'wp-1',
        startedAt: '2026-05-08T10:00:00.000Z',
        stoppedAt: '2026-05-08T10:01:00.000Z',
        productionSteps: [
          {
            id: 'step-1',
            type: 'PROCESS',
            moduleType: 'MILL',
            serialNumber: 'SVR3QA2098',
            state: 'DONE',
            startedAt: '2026-05-08T10:00:10.000Z',
            stoppedAt: '2026-05-08T10:00:40.000Z'
          }
        ]
      }
    ];

    const result = normalizeMessage({
      config: baseConfig,
      topic: 'ccu/order/completed',
      payloadText: JSON.stringify(payload),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-05-08T10:01:00.000Z'),
      sensorPolicyState: createSensorPolicyState(),
    });

    expect(result).toBeDefined();
    expect(result?.productionOrders.length).toBe(1);
    expect(result?.productionSteps.length).toBe(1);
    expect(result?.shopfloorEvents.length).toBe(2);
    expect(result?.workpieces[0]?.workpieceId).toBe('wp-1');
  });

  it('normalizes active orders from array payloads', () => {
    const payload = [
      {
        orderId: 'order-active-1',
        orderType: 'PRODUCTION',
        type: 'WHITE',
        state: 'IN_PROGRESS',
        startedAt: '2026-05-08T10:00:00.000Z'
      }
    ];

    const result = normalizeMessage({
      config: baseConfig,
      topic: 'ccu/order/active',
      payloadText: JSON.stringify(payload),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-05-08T10:00:01.000Z'),
      sensorPolicyState: createSensorPolicyState(),
    });

    expect(result).toBeDefined();
    expect(result?.productionOrders.length).toBe(1);
    expect(result?.productionOrders[0]?.orderId).toBe('order-active-1');
    expect(result?.raw?.payloadJson).toEqual(payload);
  });

  it('creates generic sensor rows for arduino payload metrics', () => {
    const result = normalizeMessage({
      config: baseConfig,
      topic: 'osf/arduino/vibration/mpu6050-1/state',
      payloadText: JSON.stringify({
        timestamp: '2026-05-08T10:00:00.000Z',
        magnitude: 18200,
        vibrationDetected: true,
        gasLevel: 0
      }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-05-08T10:00:01.000Z'),
      sensorPolicyState: createSensorPolicyState(),
    });

    expect(result).toBeDefined();
    expect(result?.sensorSnapshots.length).toBeGreaterThanOrEqual(2);
    const metricNames = new Set(result?.sensorSnapshots.map((item) => item.metricName));
    expect(metricNames.has('magnitude')).toBe(true);
    expect(metricNames.has('vibrationDetected')).toBe(true);
    expect(result?.sensorSnapshots[0]?.sensorType).toBe('vibration');
    expect(result?.sensorSnapshots[0]?.stationId).toBe('mpu6050-1');
  });

  it('keeps explicit INTERVAL rows even inside interval window', () => {
    const state = createSensorPolicyState();
    const first = normalizeMessage({
      config: baseConfig,
      topic: 'osf/arduino/temperature/dht11-1/state',
      payloadText: JSON.stringify({
        reason: 'INTERVAL',
        temperature: 25.1,
        humidity: 51.2,
        timestamp: '2026-05-08T09:10:30.000Z'
      }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-05-08T09:10:30.000Z'),
      sensorPolicyState: state,
    });
    const second = normalizeMessage({
      config: baseConfig,
      topic: 'osf/arduino/temperature/dht11-1/state',
      payloadText: JSON.stringify({
        reason: 'INTERVAL',
        temperature: 25.2,
        humidity: 51.4,
        timestamp: '2026-05-08T09:10:30.500Z'
      }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-05-08T09:10:30.500Z'),
      sensorPolicyState: state,
    });

    expect(first?.sensorSnapshots.length).toBeGreaterThan(0);
    expect(second?.sensorSnapshots.length).toBeGreaterThan(0);
  });
});
