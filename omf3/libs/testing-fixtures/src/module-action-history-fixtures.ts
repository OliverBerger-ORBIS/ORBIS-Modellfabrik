import { defer, from, Observable, of } from 'rxjs';
import { concatMap, delay } from 'rxjs/operators';
import type { RawMqttMessage } from '@omf3/gateway';

/**
 * Module Action History Fixtures for testing HBW, DRILL, MILL modules
 * Contains state messages with action history for comprehensive testing
 * These fixtures simulate a complete production sequence
 */

export interface ModuleActionHistoryFixture extends RawMqttMessage {
  topic: string;
  payload: string;
  timestamp: string;
  qos: 0 | 1 | 2;
  retain: boolean;
}

const MODULE_ACTION_HISTORY_FIXTURES: ModuleActionHistoryFixture[] = [
  // HBW (High-Bay Warehouse) - Storage operations sequence
  {
    topic: 'module/v1/ff/SVR3QA0022/state',
    payload: JSON.stringify({
      orderId: 'test-order-001',
      serialNumber: 'SVR3QA0022',
      orderUpdateId: 1,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'hbw-action-1',
        command: 'PICK',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 50000).toISOString(),
        result: 'PASSED',
        metadata: {
          slot: 'A1',
          level: '2',
          workpieceId: 'WP-HBW-001',
        },
      },
      timestamp: new Date(Date.now() - 50000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 50000).toISOString(),
    qos: 0,
    retain: false,
  },
  {
    topic: 'module/v1/ff/SVR3QA0022/state',
    payload: JSON.stringify({
      orderId: 'test-order-001',
      serialNumber: 'SVR3QA0022',
      orderUpdateId: 2,
      connectionState: 'ONLINE',
      available: 'BUSY',
      actionState: {
        id: 'hbw-action-2',
        command: 'DROP',
        state: 'RUNNING',
        timestamp: new Date(Date.now() - 40000).toISOString(),
        metadata: {
          slot: 'B3',
          level: '1',
          workpieceId: 'WP-HBW-002',
        },
      },
      timestamp: new Date(Date.now() - 40000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 40000).toISOString(),
    qos: 0,
    retain: false,
  },
  {
    topic: 'module/v1/ff/SVR3QA0022/state',
    payload: JSON.stringify({
      orderId: 'test-order-001',
      serialNumber: 'SVR3QA0022',
      orderUpdateId: 3,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'hbw-action-3',
        command: 'DROP',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 30000).toISOString(),
        result: 'PASSED',
        metadata: {
          slot: 'B3',
          level: '1',
          workpieceId: 'WP-HBW-002',
        },
      },
      timestamp: new Date(Date.now() - 30000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 30000).toISOString(),
    qos: 0,
    retain: false,
  },
  {
    topic: 'module/v1/ff/SVR3QA0022/state',
    payload: JSON.stringify({
      orderId: 'test-order-001',
      serialNumber: 'SVR3QA0022',
      orderUpdateId: 4,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'hbw-action-4',
        command: 'PICK',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 20000).toISOString(),
        result: 'PASSED',
        metadata: {
          slot: 'C2',
          level: '3',
          workpieceId: 'WP-HBW-003',
        },
      },
      timestamp: new Date(Date.now() - 20000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 20000).toISOString(),
    qos: 0,
    retain: false,
  },

  // DRILL - Drilling operations sequence
  {
    topic: 'module/v1/ff/SVR4H76449/state',
    payload: JSON.stringify({
      orderId: 'test-order-002',
      serialNumber: 'SVR4H76449',
      orderUpdateId: 1,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'drill-action-1',
        command: 'PICK',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 55000).toISOString(),
        result: 'PASSED',
        metadata: {
          workpieceId: 'WP-DRILL-001',
        },
      },
      timestamp: new Date(Date.now() - 55000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 55000).toISOString(),
    qos: 0,
    retain: false,
  },
  {
    topic: 'module/v1/ff/SVR4H76449/state',
    payload: JSON.stringify({
      orderId: 'test-order-002',
      serialNumber: 'SVR4H76449',
      orderUpdateId: 2,
      connectionState: 'ONLINE',
      available: 'BUSY',
      actionState: {
        id: 'drill-action-2',
        command: 'DRILL',
        state: 'RUNNING',
        timestamp: new Date(Date.now() - 45000).toISOString(),
        metadata: {
          drillDepth: 15,
          drillSpeed: 1200,
          workpieceId: 'WP-DRILL-001',
        },
      },
      timestamp: new Date(Date.now() - 45000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 45000).toISOString(),
    qos: 0,
    retain: false,
  },
  {
    topic: 'module/v1/ff/SVR4H76449/state',
    payload: JSON.stringify({
      orderId: 'test-order-002',
      serialNumber: 'SVR4H76449',
      orderUpdateId: 3,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'drill-action-3',
        command: 'DRILL',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 35000).toISOString(),
        result: 'PASSED',
        metadata: {
          drillDepth: 15,
          drillSpeed: 1200,
          workpieceId: 'WP-DRILL-001',
        },
      },
      timestamp: new Date(Date.now() - 35000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 35000).toISOString(),
    qos: 0,
    retain: false,
  },
  {
    topic: 'module/v1/ff/SVR4H76449/state',
    payload: JSON.stringify({
      orderId: 'test-order-002',
      serialNumber: 'SVR4H76449',
      orderUpdateId: 4,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'drill-action-4',
        command: 'DROP',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 25000).toISOString(),
        result: 'PASSED',
        metadata: {
          workpieceId: 'WP-DRILL-001',
        },
      },
      timestamp: new Date(Date.now() - 25000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 25000).toISOString(),
    qos: 0,
    retain: false,
  },

  // MILL - Milling operations sequence
  {
    topic: 'module/v1/ff/SVR3QA2098/state',
    payload: JSON.stringify({
      orderId: 'test-order-003',
      serialNumber: 'SVR3QA2098',
      orderUpdateId: 1,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'mill-action-1',
        command: 'PICK',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 60000).toISOString(),
        result: 'PASSED',
        metadata: {
          workpieceId: 'WP-MILL-001',
        },
      },
      timestamp: new Date(Date.now() - 60000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 60000).toISOString(),
    qos: 0,
    retain: false,
  },
  {
    topic: 'module/v1/ff/SVR3QA2098/state',
    payload: JSON.stringify({
      orderId: 'test-order-003',
      serialNumber: 'SVR3QA2098',
      orderUpdateId: 2,
      connectionState: 'ONLINE',
      available: 'BUSY',
      actionState: {
        id: 'mill-action-2',
        command: 'MILL',
        state: 'RUNNING',
        timestamp: new Date(Date.now() - 50000).toISOString(),
        metadata: {
          millDepth: 10,
          millSpeed: 800,
          workpieceId: 'WP-MILL-001',
        },
      },
      timestamp: new Date(Date.now() - 50000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 50000).toISOString(),
    qos: 0,
    retain: false,
  },
  {
    topic: 'module/v1/ff/SVR3QA2098/state',
    payload: JSON.stringify({
      orderId: 'test-order-003',
      serialNumber: 'SVR3QA2098',
      orderUpdateId: 3,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'mill-action-3',
        command: 'MILL',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 40000).toISOString(),
        result: 'PASSED',
        metadata: {
          millDepth: 10,
          millSpeed: 800,
          workpieceId: 'WP-MILL-001',
        },
      },
      timestamp: new Date(Date.now() - 40000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 40000).toISOString(),
    qos: 0,
    retain: false,
  },
  {
    topic: 'module/v1/ff/SVR3QA2098/state',
    payload: JSON.stringify({
      orderId: 'test-order-003',
      serialNumber: 'SVR3QA2098',
      orderUpdateId: 4,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'mill-action-4',
        command: 'DROP',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 30000).toISOString(),
        result: 'PASSED',
        metadata: {
          workpieceId: 'WP-MILL-001',
        },
      },
      timestamp: new Date(Date.now() - 30000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 30000).toISOString(),
    qos: 0,
    retain: false,
  },

  // DPS - Detection Processing Station with NFC tag
  {
    topic: 'module/v1/ff/SVR4H73275/state',
    payload: JSON.stringify({
      orderId: 'test-order-004',
      serialNumber: 'SVR4H73275',
      orderUpdateId: 1,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'dps-action-1',
        command: 'INPUT_RGB',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 35000).toISOString(),
        result: 'PASSED',
        metadata: {
          type: 'BLUE',
          workpieceId: '04E19A9AA26F80',
        },
      },
      timestamp: new Date(Date.now() - 35000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 35000).toISOString(),
    qos: 0,
    retain: false,
  },
  {
    topic: 'module/v1/ff/SVR4H73275/state',
    payload: JSON.stringify({
      orderId: 'test-order-004',
      serialNumber: 'SVR4H73275',
      orderUpdateId: 2,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'dps-action-2',
        command: 'RGB_NFC',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 25000).toISOString(),
        result: 'PASSED',
        metadata: {
          type: 'RED',
          workpieceId: '04F2A2CAA26F80',
        },
      },
      timestamp: new Date(Date.now() - 25000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 25000).toISOString(),
    qos: 0,
    retain: false,
  },

  // AIQS - Quality inspection sequence
  {
    topic: 'module/v1/ff/SVR4H76530/state',
    payload: JSON.stringify({
      orderId: 'test-order-005',
      serialNumber: 'SVR4H76530',
      orderUpdateId: 1,
      connectionState: 'ONLINE',
      available: 'BUSY',
      actionState: {
        id: 'aiqs-action-1',
        command: 'CHECK_QUALITY',
        state: 'RUNNING',
        timestamp: new Date(Date.now() - 15000).toISOString(),
        metadata: {
          workpieceId: 'WP-AIQS-001',
        },
      },
      timestamp: new Date(Date.now() - 15000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 15000).toISOString(),
    qos: 0,
    retain: false,
  },
  {
    topic: 'module/v1/ff/SVR4H76530/state',
    payload: JSON.stringify({
      orderId: 'test-order-005',
      serialNumber: 'SVR4H76530',
      orderUpdateId: 2,
      connectionState: 'ONLINE',
      available: 'READY',
      actionState: {
        id: 'aiqs-action-2',
        command: 'CHECK_QUALITY',
        state: 'FINISHED',
        timestamp: new Date(Date.now() - 10000).toISOString(),
        result: 'PASSED',
        metadata: {
          workpieceId: 'WP-AIQS-001',
        },
      },
      timestamp: new Date(Date.now() - 10000).toISOString(),
    }),
    timestamp: new Date(Date.now() - 10000).toISOString(),
    qos: 0,
    retain: false,
  },
];

export interface CreateModuleActionHistoryFixtureStreamOptions {
  intervalMs?: number;
  loop?: boolean;
}

/**
 * Creates an observable stream of module action history fixtures
 * @param options Configuration options
 * @returns Observable stream of MQTT messages
 */
export function createModuleActionHistoryFixtureStream(
  options: CreateModuleActionHistoryFixtureStreamOptions = {}
): Observable<RawMqttMessage> {
  const { intervalMs = 100, loop = false } = options;

  const source$ = from(MODULE_ACTION_HISTORY_FIXTURES).pipe(
    concatMap((fixture) =>
      defer(() => {
        return of(fixture).pipe(delay(intervalMs));
      })
    )
  );

  return source$;
}
