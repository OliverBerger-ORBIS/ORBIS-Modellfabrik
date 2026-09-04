import { describe, expect, it } from 'vitest';
import { ServiceConfig } from '../config';
import { normalizeMessage } from '../normalizer';
import { createSensorPolicyState } from '../sensorPolicy';

const baseConfig: ServiceConfig = {
  mqtt: { host: 'localhost', port: 1883, clientId: 'test-client' },
  mssql: {
    host: 'localhost',
    port: 1433,
    db: 'osf_edge',
    user: 'osf_edge',
    password: 'OsfEdge_App9#',
    encrypt: false,
    trustServerCertificate: true,
  },
  runtime: {
    mode: 'replay',
    rawRetentionDays: 14,
    sensorIntervalSeconds: 5,
    sensorIdleIntervalSeconds: 60,
    enableRawMessages: true,
    enableCameraTopic: false,
    logLevel: 'debug',
  },
  queryApi: {
    enabled: false,
    port: 3081,
    corsOrigin: '*',
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

  it('normalizes order completed only for known orderIds (ignores CCU history dump)', () => {
    const state = createSensorPolicyState();
    state.knownOrderIds.add('order-1');
    const payload = [
      {
        orderId: 'order-legacy',
        orderType: 'STORAGE',
        type: 'RED',
        state: 'FINISHED',
        workpieceId: 'wp-old',
      },
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
      sensorPolicyState: state,
    });

    expect(result).toBeDefined();
    expect(result?.shopfloorOrders.length).toBe(1);
    expect(result?.shopfloorOrders[0]?.orderId).toBe('order-1');
    expect(result?.productionSteps.length).toBe(1);
    expect(result?.shopfloorEvents.length).toBe(2);
    expect(result?.workpieces[0]?.workpieceId).toBe('wp-1');
  });

  it('registers shopfloor_order from ccu/order/response', () => {
    const state = createSensorPolicyState();
    const result = normalizeMessage({
      config: baseConfig,
      topic: 'ccu/order/response',
      payloadText: JSON.stringify({
        orderId: 'ord-resp-1',
        orderType: 'STORAGE',
        type: 'WHITE',
        workpieceId: 'nfc-1',
        timestamp: '2026-05-08T10:00:00.000Z',
      }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-05-08T10:00:00.000Z'),
      sensorPolicyState: state,
    });
    expect(result?.shopfloorOrders).toHaveLength(1);
    expect(result?.shopfloorOrders[0]?.orderType).toBe('STORAGE');
    expect(state.knownOrderIds.has('ord-resp-1')).toBe(true);
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
    expect(result?.shopfloorOrders.length).toBe(1);
    expect(result?.shopfloorOrders[0]?.orderId).toBe('order-active-1');
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

  it('always persists Arduino flame/gas/vibration alarms even inside the idle window', () => {
    const state = createSensorPolicyState();
    const quiet = normalizeMessage({
      config: baseConfig,
      topic: 'osf/arduino/flame/flame-1/state',
      payloadText: JSON.stringify({
        flameDetected: false,
        rawValue: 40,
        timestamp: '2026-05-08T10:00:00.000Z',
      }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-05-08T10:00:00.000Z'),
      sensorPolicyState: state,
    });
    const alarm = normalizeMessage({
      config: baseConfig,
      topic: 'osf/arduino/flame/flame-1/state',
      payloadText: JSON.stringify({
        flameDetected: true,
        rawValue: 12,
        timestamp: '2026-05-08T10:00:02.000Z',
      }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-05-08T10:00:02.000Z'),
      sensorPolicyState: state,
    });
    expect(quiet?.sensorSnapshots.length).toBeGreaterThan(0);
    expect(alarm?.sensorSnapshots.some((row) => row.reason === 'THRESHOLD')).toBe(true);
  });

  it('keeps 5s INTERVAL samples only while ccu/order/active is non-empty', () => {
    const state = createSensorPolicyState();
    const dht = (iso: string) =>
      normalizeMessage({
        config: baseConfig,
        topic: 'osf/arduino/temperature/dht11-1/state',
        payloadText: JSON.stringify({ temperature: 22.0, humidity: 40, timestamp: iso }),
        qos: 0,
        retain: false,
        receivedAt: new Date(iso),
        sensorPolicyState: state,
      });

    expect(dht('2026-05-08T10:00:00.000Z')?.sensorSnapshots.length).toBeGreaterThan(0);
    expect(dht('2026-05-08T10:00:05.000Z')?.sensorSnapshots.length).toBe(0);

    normalizeMessage({
      config: baseConfig,
      topic: 'ccu/order/active',
      payloadText: JSON.stringify([{ orderId: 'ord-1', orderType: 'PRODUCTION' }]),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-05-08T10:00:06.000Z'),
      sensorPolicyState: state,
    });
    expect(dht('2026-05-08T10:00:11.000Z')?.sensorSnapshots.length).toBeGreaterThan(0);

    normalizeMessage({
      config: baseConfig,
      topic: 'ccu/order/active',
      payloadText: JSON.stringify([]),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-05-08T10:00:12.000Z'),
      sensorPolicyState: state,
    });
    expect(dht('2026-05-08T10:00:16.000Z')?.sensorSnapshots.length).toBe(0);
  });

  it('tags module RGB_NFC events with NFC from actionState.result (Replay)', () => {
    const result = normalizeMessage({
      config: baseConfig,
      topic: 'module/v1/ff/NodeRed/SVR4H73275/state',
      payloadText: JSON.stringify({
        timestamp: '2026-08-07T09:11:46.905Z',
        serialNumber: 'SVR4H73275',
        moduleType: 'DPS',
        actionState: {
          command: 'RGB_NFC',
          state: 'FINISHED',
          result: '92e0ad91595f63',
          metadata: { type: 'WHITE' },
        },
      }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-08-07T09:11:46.905Z'),
      sensorPolicyState: createSensorPolicyState(),
    });

    expect(result?.shopfloorEvents).toHaveLength(1);
    expect(result?.shopfloorEvents[0]?.workpieceId).toBe('92e0ad91595f63');
    expect(result?.shopfloorEvents[0]?.workpieceType).toBe('WHITE');
    expect(result?.shopfloorEvents[0]?.action).toBe('RGB_NFC');
    expect(result?.workpieces[0]?.workpieceId).toBe('92e0ad91595f63');
  });

  it('fans out FTS state to one event per loaded NFC', () => {
    const result = normalizeMessage({
      config: baseConfig,
      topic: 'fts/v1/ff/AGV1/state',
      payloadText: JSON.stringify({
        timestamp: '2026-08-07T09:12:00.000Z',
        command: 'DOCK',
        load: [
          { loadId: 'nfcwhite1', loadType: 'WHITE', loadPosition: '1' },
          { loadId: 'nfcred222', loadType: 'RED', loadPosition: '2' },
        ],
      }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-08-07T09:12:00.000Z'),
      sensorPolicyState: createSensorPolicyState(),
    });

    const ids = result?.shopfloorEvents.map((row) => row.workpieceId).sort();
    expect(ids).toEqual(['nfcred222', 'nfcwhite1']);
  });

  it('persists live-only intake facade when the topic is present', () => {
    const result = normalizeMessage({
      config: baseConfig,
      topic: 'osf/workpiece/intake',
      payloadText: JSON.stringify({
        productRaw: 'WHITE',
        nfc: '92e0ad91595f63',
        timestamp: '2026-08-07T09:11:46.905Z',
      }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-08-07T09:11:46.905Z'),
      sensorPolicyState: createSensorPolicyState(),
    });

    expect(result?.shopfloorEvents[0]?.eventType).toBe('WORKPIECE_INTAKE');
    expect(result?.shopfloorEvents[0]?.workpieceId).toBe('92e0ad91595f63');
  });

  it('persists ccu/order/request as Soll event with color and orderType', () => {
    const result = normalizeMessage({
      config: baseConfig,
      topic: 'ccu/order/request',
      payloadText: JSON.stringify({
        type: 'WHITE',
        orderType: 'PRODUCTION',
        requestId: 'OSF-UI_aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee',
        timestamp: '2026-08-24T10:00:00.000Z',
      }),
      qos: 1,
      retain: false,
      receivedAt: new Date('2026-08-24T10:00:00.000Z'),
      sensorPolicyState: createSensorPolicyState(),
    });

    expect(result?.raw?.topic).toBe('ccu/order/request');
    expect(result?.shopfloorEvents).toHaveLength(1);
    expect(result?.shopfloorEvents[0]?.eventType).toBe('ORDER_REQUEST');
    expect(result?.shopfloorEvents[0]?.action).toBe('PRODUCTION');
    expect(result?.shopfloorEvents[0]?.actionState).toBe('REQUESTED');
    expect(result?.shopfloorEvents[0]?.workpieceType).toBe('WHITE');
  });

  it('reads module /order command from action.command (Soll)', () => {
    const result = normalizeMessage({
      config: baseConfig,
      topic: 'module/v1/ff/SVR4H76449/order',
      payloadText: JSON.stringify({
        serialNumber: 'SVR4H76449',
        orderId: 'ord-1',
        timestamp: '2026-08-24T10:00:05.000Z',
        action: {
          id: 'act-1',
          command: 'PICK',
          metadata: { type: 'WHITE' },
        },
      }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-08-24T10:00:05.000Z'),
      sensorPolicyState: createSensorPolicyState(),
    });

    expect(result?.raw?.topic).toBe('module/v1/ff/SVR4H76449/order');
    expect(result?.shopfloorEvents[0]?.action).toBe('PICK');
    expect(result?.shopfloorEvents[0]?.workpieceType).toBe('WHITE');
    expect(result?.shopfloorEvents[0]?.orderId).toBe('ord-1');
    expect(result?.shopfloorEvents[0]?.moduleSerial).toBe('SVR4H76449');
    expect(result?.shopfloorEvents[0]?.moduleType).toBe('DRILL');
  });

  it('resolves module_type from topic serial when payload has no moduleType', () => {
    const result = normalizeMessage({
      config: baseConfig,
      topic: 'module/v1/ff/SVR3QA0022/connection',
      payloadText: JSON.stringify({
        timestamp: '2026-08-25T10:00:00.000Z',
        connected: true,
      }),
      qos: 0,
      retain: false,
      receivedAt: new Date('2026-08-25T10:00:00.000Z'),
      sensorPolicyState: createSensorPolicyState(),
    });

    expect(result?.shopfloorEvents[0]?.moduleSerial).toBe('SVR3QA0022');
    expect(result?.shopfloorEvents[0]?.moduleType).toBe('HBW');
  });
});

