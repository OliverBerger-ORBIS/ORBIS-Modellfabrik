export const ANY_SERIAL = '+';

export enum CcuTopic {
  /** Generic Topic for global messages like a reset-command. */
  GLOBAL = 'ccu/global',
  ORDER_REQUEST = 'ccu/order/request',
  ORDER_RESPONSE = 'ccu/order/response',
  ACTIVE_ORDERS = 'ccu/order/active',
  /** topic for the completed (both finished and failed) orders */
  COMPLETED_ORDERS = 'ccu/order/completed',
  CANCEL_ORDERS = 'ccu/order/cancel',
  PAIRING_STATE = 'ccu/pairing/state',
  /** topic to publish additional debug information about the currently known modules */
  KNOWN_MODULES_STATE = 'ccu/pairing/known_modules',
  PAIRING_PAIR_FTS = 'ccu/pairing/pair_fts',
  /** The topic root to publish calibration data during calibrations */
  CALIBRATION_BASE = 'ccu/state/calibration',
  LOG = 'ccu/state/log',
  /** publishes the current stock in the storage module */
  STOCK = 'ccu/state/stock',
  /** publishes the current production flows for all workpiece types */
  FLOWS = 'ccu/state/flows',
  /** publishes the current  layout of the factory with modules and intersections */
  LAYOUT = 'ccu/state/layout',
  /** publishes the versions of modules that are currently out of sync with the CCU in use */
  VERSION_MISMATCH = 'ccu/state/version-mismatch',
  /** ccu subscribes to this topic to receive changes to the factory layout configuration */
  SET_LAYOUT = 'ccu/set/layout',
  /** ccu subscribes to this topic to receive the signal to reset to the default layout */
  SET_DEFAULT_LAYOUT = 'ccu/set/default_layout',
  /** ccu subscribes to this topic to receives changes to the production flows for workpiece types **/
  SET_FLOWS = 'ccu/set/flows',
  /** ccu subscribes to this and receives the production duration for a module */
  SET_MODULE_DURATION = 'ccu/set/module-duration',
  /** ccu subscribes to this and sends the calibration parameters to the target module */
  SET_MODULE_CALIBRATION = 'ccu/set/calibration',
  /** Initiate a reset of the CCU */
  SET_RESET = 'ccu/set/reset',
  /** Initiate a charge navigation order or stop it for the specified FTS */
  SET_CHARGE = 'ccu/set/charge',
  /** publishes the current configuration-map */
  CONFIG = 'ccu/state/config',
  /** ccu subscribes to this topic to receive changes to the configuration */
  SET_CONFIG = 'ccu/set/config',
  /** ccu subscribes to this topic to receive the park command */
  SET_PARK = 'ccu/set/park',
  /** Remove a module, that is not configured in the layout */
  DELETE_MODULE = 'ccu/set/delete-module',
}

export function getCcuCalibrationTopic(serial: string) {
  return CcuTopic.CALIBRATION_BASE + '/' + serial;
}

export enum FtsTopic {
  ROOT = 'fts/v1/ff',
  ORDER = 'order',
  STATE = 'state',
  CONNECTION = 'connection',
  FACTSHEET = 'factsheet',
  INSTANT_ACTION = 'instantAction',
}

export function getFtsTopic(serial: string, topic: FtsTopic) {
  if (!topic || topic === FtsTopic.ROOT) {
    throw new Error('Invalid argument for topic: ' + topic);
  }
  return `${FtsTopic.ROOT}/${serial}/${topic}`;
}

export enum ModuleTopic {
  ROOT = 'module/v1/ff',
  STATE = 'state',
  ORDER = 'order',
  CONNECTION = 'connection',
  FACTSHEET = 'factsheet',
  INSTANT_ACTION = 'instantAction',
}

export function getModuleTopic(serial: string, topic: ModuleTopic) {
  if (!topic || topic === ModuleTopic.ROOT) {
    throw new Error('Invalid argument for topic: ' + topic);
  }
  return `${ModuleTopic.ROOT}/${serial}/${topic}`;
}

export { OrderRequest, OrderResponse, OrderType, Workpiece } from './ccu';
