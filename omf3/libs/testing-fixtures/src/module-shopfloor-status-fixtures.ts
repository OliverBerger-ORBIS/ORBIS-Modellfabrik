import { defer, from, Observable, of } from 'rxjs';
import { concatMap, delay, repeat, switchMap } from 'rxjs/operators';
import type { RawMqttMessage } from '@omf3/gateway';

/**
 * Module Shopfloor Status Fixtures for testing module availability, connection status, and FTS position
 * in the Shopfloor Preview overlay.
 * 
 * This fixture sends ccu/pairing/state messages which update ModuleOverviewState,
 * which is then used by the Shopfloor Preview to display status overlays.
 */

export interface ModuleShopfloorStatusFixture {
  topic: string;
  payload: {
    modules: Array<{
      serialNumber: string;
      connected: boolean;
      available: 'READY' | 'BUSY' | 'BLOCKED';
      subType?: string;
      hasCalibration?: boolean;
      assigned?: boolean;
      ip?: string;
      version?: string;
      pairedSince?: string;
      lastSeen?: string;
    }>;
    transports: Array<{
      serialNumber: string;
      connected: boolean;
      available: 'READY' | 'BUSY' | 'BLOCKED';
      charging?: boolean;
      batteryVoltage?: number;
      batteryPercentage?: number;
      lastNodeId?: string;
      lastModuleSerialNumber?: string;
      lastLoadPosition?: string;
    }>;
    timestamp: string;
  };
  timestamp: string;
}

const MODULE_SHOPFLOOR_STATUS_FIXTURES: ModuleShopfloorStatusFixture[] = [
  // End-state fixture with different Connection/Availability combinations
  {
    topic: 'ccu/pairing/state',
    payload: {
      modules: [
        // DRILL (SVR4H76449) - READY, Connected
        {
          serialNumber: 'SVR4H76449',
          connected: true,
          available: 'READY',
          subType: 'DRILL',
          hasCalibration: true,
          assigned: true,
        },
        // MILL (SVR3QA2098) - BUSY, Connected
        {
          serialNumber: 'SVR3QA2098',
          connected: true,
          available: 'BUSY',
          subType: 'MILL',
          hasCalibration: true,
          assigned: true,
        },
        // HBW (SVR3QA0022) - BLOCKED, Connected
        {
          serialNumber: 'SVR3QA0022',
          connected: true,
          available: 'BLOCKED',
          subType: 'HBW',
          hasCalibration: true,
          assigned: true,
        },
        // AIQS (SVR4H76530) - READY, Disconnected
        {
          serialNumber: 'SVR4H76530',
          connected: false,
          available: 'READY',
          subType: 'AIQS',
          hasCalibration: false,
          assigned: false,
        },
        // DPS (SVR4H73275) - BUSY, Disconnected
        {
          serialNumber: 'SVR4H73275',
          connected: false,
          available: 'BUSY',
          subType: 'DPS',
          hasCalibration: false,
          assigned: false,
        },
      ],
      transports: [
        // FTS (5iO4) - READY, Connected, with position
        {
          serialNumber: '5iO4',
          connected: true,
          available: 'READY',
          charging: false,
          lastNodeId: 'NODE_1',
        },
      ],
      timestamp: new Date().toISOString(),
    },
    timestamp: new Date().toISOString(),
  },
];

/**
 * Load Module Shopfloor Status fixtures
 * @returns Array of RawMqttMessage objects
 */
export const loadModuleShopfloorStatusFixtures = (): RawMqttMessage[] => {
  return MODULE_SHOPFLOOR_STATUS_FIXTURES.map((fixture) => ({
    topic: fixture.topic,
    payload: JSON.stringify(fixture.payload),
    timestamp: fixture.timestamp,
    qos: 0,
    retain: false,
  }));
};

/**
 * Create an Observable stream of Module Shopfloor Status fixture messages
 * @param options - Stream options (interval, loop)
 * @returns Observable stream of RawMqttMessage objects
 */
export const createModuleShopfloorStatusFixtureStream = (
  options?: { intervalMs?: number; loop?: boolean }
): Observable<RawMqttMessage> => {
  const messages = loadModuleShopfloorStatusFixtures();
  return defer(() => from(messages)).pipe(
    switchMap((message) => {
      const delayMs = options?.intervalMs ?? 0;
      if (delayMs > 0) {
        return from([message]).pipe(concatMap((msg) => of(msg).pipe(delay(delayMs))));
      }
      return of(message);
    }),
    options?.loop ? repeat() : (source) => source
  );
};

