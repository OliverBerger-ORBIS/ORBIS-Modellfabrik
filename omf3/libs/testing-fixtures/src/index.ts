import { defer, from, Observable, of, OperatorFunction } from 'rxjs';
import { concatMap, delay, repeat, switchMap } from 'rxjs/operators';

import type { RawMqttMessage } from '@omf3/gateway';

export type OrderFixtureName = 'white' | 'blue' | 'red' | 'mixed';

const DEFAULT_BASE_URL = '/fixtures/orders';

export interface LoadFixtureOptions {
  /**
   * Override the base URL used to fetch fixture files.
   * Defaults to `/fixtures/orders`.
   */
  baseUrl?: string;

  /**
   * Custom loader implementation. Receives the resolved path (including base
   * URL) and must return the raw file contents. Useful in unit tests where a
   * Node based loader is injected.
   */
  loader?: (resolvedPath: string) => Promise<string>;
}

export interface FixtureStreamOptions extends LoadFixtureOptions {
  /**
   * Delay between emitted messages. Defaults to emitting as fast as possible.
   */
  intervalMs?: number;

  /**
   * When true the stream restarts from the beginning after the last message.
   */
  loop?: boolean;
}

const FIXTURE_PATHS: Record<OrderFixtureName, string> = {
  white: 'white/orders.log',
  blue: 'blue/orders.log',
  red: 'red/orders.log',
  mixed: 'mixed/orders.log',
};

const defaultLoader = async (resolvedPath: string): Promise<string> => {
  if (typeof fetch !== 'function') {
    throw new Error(
      `global fetch is not available. Inject a custom loader via LoadFixtureOptions.loader when running outside the browser.`
    );
  }

  const response = await fetch(resolvedPath);
  if (!response.ok) {
    throw new Error(`Failed to fetch fixture from ${resolvedPath}: ${response.status} ${response.statusText}`);
  }

  return response.text();
};

const parseLines = (contents: string): RawMqttMessage[] => {
  return contents
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line) => JSON.parse(line) as RawMqttMessage);
};

const resolvePath = (name: OrderFixtureName, baseUrl: string | undefined): string => {
  const base = baseUrl ?? DEFAULT_BASE_URL;
  const suffix = FIXTURE_PATHS[name];
  return base.endsWith('/') ? `${base}${suffix}` : `${base}/${suffix}`;
};

export const loadOrderFixture = async (
  name: OrderFixtureName,
  options?: LoadFixtureOptions
): Promise<RawMqttMessage[]> => {
  const path = resolvePath(name, options?.baseUrl);
  const loader = options?.loader ?? defaultLoader;
  const contents = await loader(path);
  return parseLines(contents);
};

const withInterval = (intervalMs: number | undefined): OperatorFunction<RawMqttMessage, RawMqttMessage> =>
  intervalMs && intervalMs > 0
    ? concatMap((message: RawMqttMessage) => of(message).pipe(delay(intervalMs)))
    : (source: Observable<RawMqttMessage>) => source;

export const createOrderFixtureStream = (
  name: OrderFixtureName,
  options?: FixtureStreamOptions
): Observable<RawMqttMessage> => {
  return defer(() => from(loadOrderFixture(name, options))).pipe(
    switchMap((messages) => from(messages)),
    withInterval(options?.intervalMs),
    options?.loop ? repeat() : (source) => source
  );
};

export const listAvailableOrderFixtures = (): OrderFixtureName[] => Object.keys(FIXTURE_PATHS) as OrderFixtureName[];

