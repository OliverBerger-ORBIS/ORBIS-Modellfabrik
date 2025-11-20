/**
 * Tab-specific fixture loading system
 * 
 * Allows each tab to independently load fixtures for the topics it needs,
 * with different variants (e.g., production vs storage orders, error states, etc.)
 */

import { defer, from, merge, Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import type { RawMqttMessage } from '@omf3/gateway';
import {
  createOrderFixtureStream,
  createModulePairingFixtureStream,
  createStockFixtureStream,
  createFlowFixtureStream,
  createConfigFixtureStream,
  createSensorFixtureStream,
  type FixtureStreamOptions,
  type OrderFixtureName,
  type ModuleFixtureName,
  type StockFixtureName,
  type FlowFixtureName,
  type ConfigFixtureName,
  type SensorFixtureName,
} from './index';

/**
 * Tab-specific fixture configuration
 * Each tab can specify which fixture types it wants to load
 */
export interface TabFixtureConfig {
  /** Order fixtures (production, storage, etc.) */
  orders?: OrderFixtureName;
  /** Module/pairing fixtures */
  modules?: ModuleFixtureName;
  /** Stock/inventory fixtures */
  stock?: StockFixtureName;
  /** Production flow fixtures */
  flows?: FlowFixtureName;
  /** Configuration fixtures */
  config?: ConfigFixtureName;
  /** Sensor fixtures (BME680, LDR, camera) */
  sensors?: SensorFixtureName;
}

/**
 * Preset fixture configurations for common tab scenarios
 */
export const TAB_FIXTURE_PRESETS: Record<string, TabFixtureConfig> = {
  // Startup/default state - used by overview and initial load
  startup: {
    orders: 'startup',
    modules: 'startup',
    stock: 'startup',
    flows: 'startup',
    config: 'startup',
    sensors: 'startup',
  },
  
  // Order tab presets
  'order-white': {
    orders: 'white',
    modules: 'white',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  'order-blue': {
    orders: 'blue',
    modules: 'blue',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  'order-red': {
    orders: 'red',
    modules: 'red',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  'order-mixed': {
    orders: 'mixed',
    modules: 'mixed',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  'order-storage': {
    orders: 'storage',
    modules: 'storage',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  
  // Module tab presets
  'module-default': {
    orders: 'startup',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  
  // Process/Flow tab presets
  'process-active': {
    orders: 'mixed',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  
  // Sensor tab presets
  'sensor-active': {
    orders: 'startup',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  
  // Configuration tab presets
  'config-default': {
    orders: 'startup',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
};

/**
 * Load fixtures for a specific tab configuration
 * 
 * @param config - Tab-specific fixture configuration
 * @param options - Fixture stream options (interval, loop, etc.)
 * @returns Observable stream of MQTT messages from all configured fixtures
 */
export const createTabFixtureStream = (
  config: TabFixtureConfig,
  options?: FixtureStreamOptions
): Observable<RawMqttMessage> => {
  const streams: Observable<RawMqttMessage>[] = [];

  // Add order fixtures if specified
  if (config.orders) {
    streams.push(createOrderFixtureStream(config.orders, options));
  }

  // Add module fixtures if specified
  if (config.modules) {
    streams.push(createModulePairingFixtureStream(config.modules, options));
  }

  // Add stock fixtures if specified
  if (config.stock) {
    streams.push(createStockFixtureStream(config.stock, options));
  }

  // Add flow fixtures if specified
  if (config.flows) {
    streams.push(createFlowFixtureStream(config.flows, options));
  }

  // Add config fixtures if specified
  if (config.config) {
    streams.push(createConfigFixtureStream(config.config, options));
  }

  // Add sensor fixtures if specified
  if (config.sensors) {
    streams.push(createSensorFixtureStream(config.sensors, options));
  }

  // Merge all streams into a single stream
  return streams.length > 0 ? merge(...streams) : defer(() => from([]));
};

/**
 * Load a preset tab fixture configuration
 * 
 * @param presetName - Name of the preset configuration
 * @param options - Fixture stream options (interval, loop, etc.)
 * @returns Observable stream of MQTT messages from the preset
 */
export const createTabFixturePreset = (
  presetName: string,
  options?: FixtureStreamOptions
): Observable<RawMqttMessage> => {
  const config = TAB_FIXTURE_PRESETS[presetName];
  if (!config) {
    console.warn(`[tab-fixtures] Unknown preset: ${presetName}, using startup default`);
    return createTabFixtureStream(TAB_FIXTURE_PRESETS.startup, options);
  }
  return createTabFixtureStream(config, options);
};

/**
 * Get available preset names
 */
export const listTabFixturePresets = (): string[] => {
  return Object.keys(TAB_FIXTURE_PRESETS);
};

/**
 * Create a custom tab fixture configuration
 * Allows fine-grained control over which fixtures are loaded
 */
export const createCustomTabFixture = (
  config: Partial<TabFixtureConfig>,
  options?: FixtureStreamOptions
): Observable<RawMqttMessage> => {
  // Use defaults for any unspecified fixture types
  const fullConfig: TabFixtureConfig = {
    orders: config.orders,
    modules: config.modules,
    stock: config.stock,
    flows: config.flows,
    config: config.config,
    sensors: config.sensors,
  };
  return createTabFixtureStream(fullConfig, options);
};
