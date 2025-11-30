import { defer, from, Observable, of } from 'rxjs';
import { concatMap, delay, repeat, switchMap } from 'rxjs/operators';
import type { RawMqttMessage } from '@omf3/gateway';

/**
 * Module Status Fixtures for testing module availability, connection status, and FTS position
 * Contains various module states with different availability (READY, BUSY, BLOCKED) and connection status
 * Also includes FTS position data
 */

export interface ModuleStatusFixture {
  topic: string;
  payload: {
    // For modules
    moduleId?: string;
    serialNumber?: string;
    availability?: 'READY' | 'BUSY' | 'BLOCKED';
    connected?: boolean;
    moduleStatus?: string; // Module status (operational, processing, error, offline)
    // For FTS
    ftsId?: string;
    position?: { x: number; y: number };
    speed?: number;
    ftsStatus?: 'idle' | 'moving' | 'error'; // FTS status
  };
  timestamp: string;
}

const MODULE_STATUS_FIXTURES: ModuleStatusFixture[] = [
  // Module: DRILL (SVR4H76449) - READY, Connected
  // Use module/v1/ff/<serial> format (will be processed by gateway.modules$)
  {
    topic: 'module/v1/ff/SVR4H76449',
    payload: {
      moduleId: 'SVR4H76449',
      serialNumber: 'SVR4H76449',
      availability: 'READY',
      connected: true,
      moduleStatus: 'operational',
    },
    timestamp: new Date(Date.now() - 10000).toISOString(),
  },
  // Module: MILL (SVR3QA2098) - BUSY, Connected
  {
    topic: 'module/v1/ff/SVR3QA2098',
    payload: {
      moduleId: 'SVR3QA2098',
      serialNumber: 'SVR3QA2098',
      availability: 'BUSY',
      connected: true,
      moduleStatus: 'processing',
    },
    timestamp: new Date(Date.now() - 9000).toISOString(),
  },
  // Module: HBW (SVR3QA0022) - BLOCKED, Connected
  {
    topic: 'module/v1/ff/SVR3QA0022',
    payload: {
      moduleId: 'SVR3QA0022',
      serialNumber: 'SVR3QA0022',
      availability: 'BLOCKED',
      connected: true,
      moduleStatus: 'error',
    },
    timestamp: new Date(Date.now() - 8000).toISOString(),
  },
  // Module: AIQS (SVR4H76530) - READY, Disconnected
  {
    topic: 'module/v1/ff/SVR4H76530',
    payload: {
      moduleId: 'SVR4H76530',
      serialNumber: 'SVR4H76530',
      availability: 'READY',
      connected: false,
      moduleStatus: 'offline',
    },
    timestamp: new Date(Date.now() - 7000).toISOString(),
  },
  // Module: DPS (SVR4H73275) - BUSY, Disconnected
  {
    topic: 'module/v1/ff/SVR4H73275',
    payload: {
      moduleId: 'SVR4H73275',
      serialNumber: 'SVR4H73275',
      availability: 'BUSY',
      connected: false,
      moduleStatus: 'offline',
    },
    timestamp: new Date(Date.now() - 6000).toISOString(),
  },
  // FTS (5iO4) - Position and Status
  // Use fts/v1/ff/<serial> format (will be processed by gateway.fts$)
  {
    topic: 'fts/v1/ff/5iO4',
    payload: {
      ftsId: '5iO4',
      position: { x: 450, y: 300 }, // Example position in shopfloor coordinates
      speed: 0.5,
      ftsStatus: 'idle',
    },
    timestamp: new Date(Date.now() - 5000).toISOString(),
  },
  // Additional FTS position update (moving)
  {
    topic: 'fts/v1/ff/5iO4',
    payload: {
      ftsId: '5iO4',
      position: { x: 500, y: 350 }, // Updated position
      speed: 1.2,
      ftsStatus: 'moving',
    },
    timestamp: new Date(Date.now() - 2000).toISOString(),
  },
];

/**
 * Load Module Status fixtures
 * @returns Array of RawMqttMessage objects
 */
export const loadModuleStatusFixtures = (): RawMqttMessage[] => {
  return MODULE_STATUS_FIXTURES.map((fixture) => ({
    topic: fixture.topic,
    payload: JSON.stringify(fixture.payload),
    timestamp: fixture.timestamp,
    qos: 0,
    retain: false,
  }));
};

/**
 * Create an Observable stream of Module Status fixture messages
 * @returns Observable stream of RawMqttMessage objects
 */
export const createModuleStatusFixtureStream = (
  options?: { intervalMs?: number; loop?: boolean }
): Observable<RawMqttMessage> => {
  const messages = loadModuleStatusFixtures();
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

