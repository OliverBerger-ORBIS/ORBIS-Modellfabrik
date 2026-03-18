import type { RawMqttMessage } from '@osf/gateway';

/**
 * DSP Action Fixtures for testing dsp/drill/action and dsp/aiqs/action topics
 * Contains 5 different color values for changeLight/changeColor commands
 */

export interface DspActionFixture {
  topic: string;
  payload: {
    command: string;
    value: string;
  };
  timestamp: string;
}

const DSP_DRILL_ACTION_FIXTURES: DspActionFixture[] = [
  {
    topic: 'dsp/drill/action',
    payload: {
      command: 'changeLight',
      value: '#FF0000', // Red
    },
    timestamp: new Date(Date.now() - 5000).toISOString(),
  },
  {
    topic: 'dsp/drill/action',
    payload: {
      command: 'changeLight',
      value: '#00FF00', // Green
    },
    timestamp: new Date(Date.now() - 4000).toISOString(),
  },
  {
    topic: 'dsp/drill/action',
    payload: {
      command: 'changeLight',
      value: '#0000FF', // Blue
    },
    timestamp: new Date(Date.now() - 3000).toISOString(),
  },
  {
    topic: 'dsp/drill/action',
    payload: {
      command: 'changeLight',
      value: '#FFFF00', // Yellow
    },
    timestamp: new Date(Date.now() - 2000).toISOString(),
  },
  {
    topic: 'dsp/drill/action',
    payload: {
      command: 'changeLight',
      value: '#FF00FF', // Magenta
    },
    timestamp: new Date(Date.now() - 1000).toISOString(),
  },
];

const DSP_AIQS_ACTION_FIXTURES: DspActionFixture[] = [
  {
    topic: 'dsp/aiqs/action',
    payload: {
      command: 'changeLight',
      value: '#FF0000', // Red
    },
    timestamp: new Date(Date.now() - 5000).toISOString(),
  },
  {
    topic: 'dsp/aiqs/action',
    payload: {
      command: 'changeColor',
      value: '#00FF00', // Green
    },
    timestamp: new Date(Date.now() - 4000).toISOString(),
  },
  {
    topic: 'dsp/aiqs/action',
    payload: {
      command: 'changeLight',
      value: '#0000FF', // Blue
    },
    timestamp: new Date(Date.now() - 3000).toISOString(),
  },
  {
    topic: 'dsp/aiqs/action',
    payload: {
      command: 'changeColor',
      value: '#FFFF00', // Yellow
    },
    timestamp: new Date(Date.now() - 2000).toISOString(),
  },
  {
    topic: 'dsp/aiqs/action',
    payload: {
      command: 'changeLight',
      value: '#FF00FF', // Magenta
    },
    timestamp: new Date(Date.now() - 1000).toISOString(),
  },
];

/**
 * Load DSP drill action fixtures (dsp/drill/action)
 * @returns Array of RawMqttMessage objects
 */
export const loadDspActionFixtures = (): RawMqttMessage[] => {
  return DSP_DRILL_ACTION_FIXTURES.map((fixture) => ({
    topic: fixture.topic,
    payload: JSON.stringify(fixture.payload),
    timestamp: fixture.timestamp,
    qos: 0,
    retain: false,
  }));
};

/**
 * Load DSP AIQS action fixtures (dsp/aiqs/action)
 * @returns Array of RawMqttMessage objects
 */
export const loadAiqsActionFixtures = (): RawMqttMessage[] => {
  return DSP_AIQS_ACTION_FIXTURES.map((fixture) => ({
    topic: fixture.topic,
    payload: JSON.stringify(fixture.payload),
    timestamp: fixture.timestamp,
    qos: 0,
    retain: false,
  }));
};

import { defer, from, Observable, of } from 'rxjs';
import { concatMap, delay, repeat, switchMap } from 'rxjs/operators';

/**
 * Create a stream of DSP action messages
 * Messages are sent with a configurable interval
 */
export const createDspActionFixtureStream = (
  options?: { intervalMs?: number; loop?: boolean }
): Observable<RawMqttMessage> => {
  const intervalMs = options?.intervalMs ?? 1000;
  const loop = options?.loop ?? false;

  return defer(() => of(loadDspActionFixtures())).pipe(
    switchMap((messages: RawMqttMessage[]) => from(messages)),
    concatMap((message: RawMqttMessage) => of(message).pipe(delay(intervalMs))),
    loop ? repeat() : (source) => source
  );
};

/**
 * Create a stream of DSP AIQS action messages (dsp/aiqs/action)
 * Messages are sent with a configurable interval
 */
export const createAiqsActionFixtureStream = (
  options?: { intervalMs?: number; loop?: boolean }
): Observable<RawMqttMessage> => {
  const intervalMs = options?.intervalMs ?? 1000;
  const loop = options?.loop ?? false;

  return defer(() => of(loadAiqsActionFixtures())).pipe(
    switchMap((messages: RawMqttMessage[]) => from(messages)),
    concatMap((message: RawMqttMessage) => of(message).pipe(delay(intervalMs))),
    loop ? repeat() : (source) => source
  );
};

