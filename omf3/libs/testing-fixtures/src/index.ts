import { defer, from, Observable, of, OperatorFunction } from 'rxjs';
import { concatMap, delay, repeat, switchMap } from 'rxjs/operators';

import type { RawMqttMessage } from '@omf3/gateway';

export type OrderFixtureName =
  | 'white'
  | 'white_step3'
  | 'blue'
  | 'red'
  | 'mixed'
  | 'storage'
  | 'startup';
export type ModuleFixtureName =
  | 'default'
  | 'white'
  | 'blue'
  | 'red'
  | 'mixed'
  | 'storage'
  | 'startup';
export type StockFixtureName = 'default' | 'startup';
export type FlowFixtureName = 'default' | 'startup';
export type ConfigFixtureName = 'default' | 'startup';
export type SensorFixtureName = 'default' | 'startup';

/**
 * Get the base href from the document, falling back to '/'.
 * This ensures fixtures work correctly with baseHref configurations
 * (e.g., '/ORBIS-Modellfabrik/' for GitHub Pages).
 */
const getBaseHref = (): string => {
  if (typeof document === 'undefined') {
    return '/';
  }
  const baseTag = document.querySelector('base');
  if (baseTag) {
    // Use getAttribute('href') to get the raw href value (e.g., '/ORBIS-Modellfabrik/')
    // baseTag.href returns the full resolved URL which we don't need
    const href = baseTag.getAttribute('href');
    if (href) {
      // Ensure href ends with '/' for proper path concatenation
      return href.endsWith('/') ? href : `${href}/`;
    }
  }
  return '/';
};

const DEFAULT_BASE_URL = '/fixtures/orders';
const DEFAULT_MODULE_BASE_URL = '/fixtures/modules';
const DEFAULT_STOCK_BASE_URL = '/fixtures/stock';
const DEFAULT_FLOW_BASE_URL = '/fixtures/flows';
const DEFAULT_CONFIG_BASE_URL = '/fixtures/config';
const DEFAULT_SENSOR_BASE_URL = '/fixtures/sensors';

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
  white_step3: 'white/step3.json',
  blue: 'blue/orders.log',
  red: 'red/orders.log',
  mixed: 'mixed/orders.log',
  storage: 'storage/orders.log',
  startup: 'startup/orders.log',
};

const MODULE_FIXTURE_PATHS: Record<ModuleFixtureName, string> = {
  default: 'default.log',
  white: 'default.log',
  blue: 'default.log',
  red: 'default.log',
  mixed: 'default.log',
  storage: 'default.log',
  startup: 'startup.log',
};

const STOCK_FIXTURE_PATHS: Record<StockFixtureName, string> = {
  default: 'default.log',
  startup: 'startup.log',
};

const FLOW_FIXTURE_PATHS: Record<FlowFixtureName, string> = {
  default: 'default.log',
  startup: 'startup.log',
};

const CONFIG_FIXTURE_PATHS: Record<ConfigFixtureName, string> = {
  default: 'default.log',
  startup: 'startup.log',
};

const SENSOR_FIXTURE_PATHS: Record<SensorFixtureName, string> = {
  default: 'default.log',
  startup: 'startup.log',
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
  const baseHref = getBaseHref();
  const relativePath = baseUrl ?? DEFAULT_BASE_URL;
  // Remove leading slash from relativePath to combine with baseHref
  const cleanPath = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
  const fullBase = `${baseHref}${cleanPath}`;
  const suffix = FIXTURE_PATHS[name];
  return fullBase.endsWith('/') ? `${fullBase}${suffix}` : `${fullBase}/${suffix}`;
};

const resolveModulePath = (name: ModuleFixtureName, baseUrl: string | undefined): string => {
  const baseHref = getBaseHref();
  const relativePath = baseUrl ?? DEFAULT_MODULE_BASE_URL;
  const cleanPath = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
  const fullBase = `${baseHref}${cleanPath}`;
  const suffix = MODULE_FIXTURE_PATHS[name];
  return fullBase.endsWith('/') ? `${fullBase}${suffix}` : `${fullBase}/${suffix}`;
};

const resolveStockPath = (name: StockFixtureName, baseUrl: string | undefined): string => {
  const baseHref = getBaseHref();
  const relativePath = baseUrl ?? DEFAULT_STOCK_BASE_URL;
  const cleanPath = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
  const fullBase = `${baseHref}${cleanPath}`;
  const suffix = STOCK_FIXTURE_PATHS[name];
  return fullBase.endsWith('/') ? `${fullBase}${suffix}` : `${fullBase}/${suffix}`;
};

const resolveFlowPath = (name: FlowFixtureName, baseUrl: string | undefined): string => {
  const baseHref = getBaseHref();
  const relativePath = baseUrl ?? DEFAULT_FLOW_BASE_URL;
  const cleanPath = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
  const fullBase = `${baseHref}${cleanPath}`;
  const suffix = FLOW_FIXTURE_PATHS[name];
  return fullBase.endsWith('/') ? `${fullBase}${suffix}` : `${fullBase}/${suffix}`;
};

const resolveConfigPath = (name: ConfigFixtureName, baseUrl: string | undefined): string => {
  const baseHref = getBaseHref();
  const relativePath = baseUrl ?? DEFAULT_CONFIG_BASE_URL;
  const cleanPath = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
  const fullBase = `${baseHref}${cleanPath}`;
  const suffix = CONFIG_FIXTURE_PATHS[name];
  return fullBase.endsWith('/') ? `${fullBase}${suffix}` : `${fullBase}/${suffix}`;
};

const resolveSensorPath = (name: SensorFixtureName, baseUrl: string | undefined): string => {
  const baseHref = getBaseHref();
  const relativePath = baseUrl ?? DEFAULT_SENSOR_BASE_URL;
  const cleanPath = relativePath.startsWith('/') ? relativePath.slice(1) : relativePath;
  const fullBase = `${baseHref}${cleanPath}`;
  const suffix = SENSOR_FIXTURE_PATHS[name];
  return fullBase.endsWith('/') ? `${fullBase}${suffix}` : `${fullBase}/${suffix}`;
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

export const loadModulePairingFixture = async (
  name: ModuleFixtureName,
  options?: LoadFixtureOptions
): Promise<RawMqttMessage[]> => {
  const path = resolveModulePath(name, options?.baseUrl);
  const loader = options?.loader ?? defaultLoader;
  try {
    const contents = await loader(path);
    return parseLines(contents);
  } catch (error) {
    console.warn(`[testing-fixtures] Failed to load module pairing fixture "${name}" from ${path}`, error);
    return [];
  }
};

export const loadStockFixture = async (
  name: StockFixtureName,
  options?: LoadFixtureOptions
): Promise<RawMqttMessage[]> => {
  const path = resolveStockPath(name, options?.baseUrl);
  const loader = options?.loader ?? defaultLoader;
  try {
    const contents = await loader(path);
    return parseLines(contents);
  } catch (error) {
    console.warn(`[testing-fixtures] Failed to load stock fixture "${name}" from ${path}`, error);
    return [];
  }
};

export const loadFlowFixture = async (
  name: FlowFixtureName,
  options?: LoadFixtureOptions
): Promise<RawMqttMessage[]> => {
  const path = resolveFlowPath(name, options?.baseUrl);
  const loader = options?.loader ?? defaultLoader;
  try {
    const contents = await loader(path);
    return parseLines(contents);
  } catch (error) {
    console.warn(`[testing-fixtures] Failed to load flow fixture "${name}" from ${path}`, error);
    return [];
  }
};

export const loadConfigFixture = async (
  name: ConfigFixtureName,
  options?: LoadFixtureOptions
): Promise<RawMqttMessage[]> => {
  const path = resolveConfigPath(name, options?.baseUrl);
  const loader = options?.loader ?? defaultLoader;
  try {
    const contents = await loader(path);
    return parseLines(contents);
  } catch (error) {
    console.warn(`[testing-fixtures] Failed to load config fixture "${name}" from ${path}`, error);
    return [];
  }
};

export const loadSensorFixture = async (
  name: SensorFixtureName,
  options?: LoadFixtureOptions
): Promise<RawMqttMessage[]> => {
  const path = resolveSensorPath(name, options?.baseUrl);
  const loader = options?.loader ?? defaultLoader;
  try {
    const contents = await loader(path);
    return parseLines(contents);
  } catch (error) {
    console.warn(`[testing-fixtures] Failed to load sensor fixture "${name}" from ${path}`, error);
    return [];
  }
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

export const createModulePairingFixtureStream = (
  name: ModuleFixtureName,
  options?: FixtureStreamOptions
): Observable<RawMqttMessage> => {
  return defer(() => from(loadModulePairingFixture(name, options))).pipe(
    switchMap((messages) => from(messages)),
    withInterval(options?.intervalMs),
    options?.loop ? repeat() : (source) => source
  );
};

export const createStockFixtureStream = (
  name: StockFixtureName,
  options?: FixtureStreamOptions
): Observable<RawMqttMessage> => {
  return defer(() => from(loadStockFixture(name, options))).pipe(
    switchMap((messages) => from(messages)),
    withInterval(options?.intervalMs),
    options?.loop ? repeat() : (source) => source
  );
};

export const createFlowFixtureStream = (
  name: FlowFixtureName,
  options?: FixtureStreamOptions
): Observable<RawMqttMessage> => {
  return defer(() => from(loadFlowFixture(name, options))).pipe(
    switchMap((messages) => from(messages)),
    withInterval(options?.intervalMs),
    options?.loop ? repeat() : (source) => source
  );
};

export const createConfigFixtureStream = (
  name: ConfigFixtureName,
  options?: FixtureStreamOptions
): Observable<RawMqttMessage> => {
  return defer(() => from(loadConfigFixture(name, options))).pipe(
    switchMap((messages) => from(messages)),
    withInterval(options?.intervalMs),
    options?.loop ? repeat() : (source) => source
  );
};

export const createSensorFixtureStream = (
  name: SensorFixtureName,
  options?: FixtureStreamOptions
): Observable<RawMqttMessage> => {
  return defer(() => from(loadSensorFixture(name, options))).pipe(
    switchMap((messages) => from(messages)),
    withInterval(options?.intervalMs),
    options?.loop ? repeat() : (source) => source
  );
};

export const listAvailableOrderFixtures = (): OrderFixtureName[] => Object.keys(FIXTURE_PATHS) as OrderFixtureName[];

export const listAvailableModuleFixtures = (): ModuleFixtureName[] =>
  Object.keys(MODULE_FIXTURE_PATHS) as ModuleFixtureName[];

export const listAvailableStockFixtures = (): StockFixtureName[] =>
  Object.keys(STOCK_FIXTURE_PATHS) as StockFixtureName[];

export const listAvailableFlowFixtures = (): FlowFixtureName[] =>
  Object.keys(FLOW_FIXTURE_PATHS) as FlowFixtureName[];

export const listAvailableConfigFixtures = (): ConfigFixtureName[] =>
  Object.keys(CONFIG_FIXTURE_PATHS) as ConfigFixtureName[];

export const listAvailableSensorFixtures = (): SensorFixtureName[] =>
  Object.keys(SENSOR_FIXTURE_PATHS) as SensorFixtureName[];

export const SHOPFLOOR_ASSET_MAP: Record<string, string> = {
  MILL: '/shopfloor/milling-machine.svg',
  AIQS: '/shopfloor/ai-assistant.svg',
  HBW: '/shopfloor/stock.svg',
  DPS: '/shopfloor/robot-arm.svg',
  DRILL: '/shopfloor/bohrer.svg',
  CHRG: '/shopfloor/fuel.svg',
  FTS: '/shopfloor/robotic.svg',
  HBW_SQUARE1: '/shopfloor/factory.svg',
  HBW_SQUARE2: '/shopfloor/conveyor.svg',
  DPS_SQUARE1: '/shopfloor/warehouse.svg',
  DPS_SQUARE2: '/shopfloor/order-tracking.svg',
  ORBIS: '/shopfloor/ORBIS_logo_RGB.svg',
  DSP: '/shopfloor/information-technology.svg',
  'INTERSECTION-1': '/shopfloor/intersection1.svg',
  'INTERSECTION-2': '/shopfloor/intersection2.svg',
  'INTERSECTION-3': '/shopfloor/intersection3.svg',
  'INTERSECTION-4': '/shopfloor/intersection4.svg',
  FACTORY_CONFIGURATION: '/headings/grundriss.svg',
  SHOPFLOOR_LAYOUT: '/headings/grundriss.svg',
  PARAMETER_CONFIGURATION: '/headings/system.svg',
  PRODUCTION_SETTINGS: '/headings/system.svg',
  CONFIGURATION: '/headings/system.svg',
  QUESTION: '/shopfloor/question.svg',
};

