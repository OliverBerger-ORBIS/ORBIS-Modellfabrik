import { LoadingBay, LoadingBayId } from './fts';
import { Module, ModuleCommandType, ModuleType } from './module';
import { ReferenceValue } from './vda';

export enum AvailableState {
  BLOCKED = 'BLOCKED',
  READY = 'READY',
  BUSY = 'BUSY',
}

export type Workpiece = 'BLUE' | 'RED' | 'WHITE';
export const Workpiece = {
  BLUE: 'BLUE' as Workpiece,
  RED: 'RED' as Workpiece,
  WHITE: 'WHITE' as Workpiece,
};

export type OrderType = 'PRODUCTION' | 'STORAGE';
export const OrderType = {
  PRODUCTION: 'PRODUCTION' as OrderType,
  STORAGE: 'STORAGE' as OrderType,
};

/**
 * Device type:
 * MODULE: Production module
 * FTS:    Driverless transport vehicle
 */
export type DeviceType = 'MODULE' | 'FTS';
export const DeviceType = {
  MODULE: 'MODULE' as DeviceType,
  FTS: 'FTS' as DeviceType,
};

/**
 * Type for the stock state that is sent to the cloud.
 */
export type CloudStockItem = {
  workpiece?: CloudWorkpiece;
  location: string;
  hbw?: string;
};

export type CloudWorkpiece = {
  id: string;
  type: Workpiece;
  state: 'RAW' | 'RESERVED';
};

export type CloudStock = {
  ts: Date;
  stockItems: CloudStockItem[];
};

/** Base order production step */
export type OrderResponseStep = {
  id: string;
  type: string;
  dependentActionId?: string;
  state: OrderState;
  /** the start time of this step */
  startedAt?: Date;
  /** the end time of this step */
  stoppedAt?: Date;
};

/**
 * A navigation step is used to drive the FTS from one "source" module to a "target" module
 * Navigation steps can have dependencies to production steps that need to be executed before
 * the navigation, i.e. the module must place the workpiece on the FTS before the FTS drives
 * away to another module.
 */
export type OrderNavigationStep = OrderResponseStep & {
  type: 'NAVIGATION';
  source: ModuleType;
  target: ModuleType;
};

/**
 * Defines a specific production step that can be converted to a {@link ProductionCommand} and
 * executed by a module.
 */
export type OrderManufactureStep = OrderResponseStep & {
  type: 'MANUFACTURE';
  moduleType: ModuleType;
  command: ModuleCommandType;
  /** The serial number of the module chosen for this step */
  serialNumber?: string;
};

/** The states an order can be in */
export enum OrderState {
  ENQUEUED = 'ENQUEUED',
  IN_PROGRESS = 'IN_PROGRESS',
  FINISHED = 'FINISHED',
  CANCELLED = 'CANCELLED',
  ERROR = 'ERROR',
}

/**
 * The order request that is sent from the user via the frontend to the central control unit or
 * published by the factory itself.
 * Based on the orderType, the order is either a production or a storage order
 * - "Produce one piece of the given type"
 * - "Store the given workpiece of the given type"
 */
export type OrderRequest = {
  /** The actual color of the workpiece */
  type: Workpiece;
  /** The timestamp when the order was created */
  timestamp: Date;
  /** The type of the order, for production orders, this has to be PRODUCTION */
  orderType: OrderType;
  /** The id of the workpiece that should be stored */
  workpieceId?: string;
  /** Optional: The id of the simulation/planspiel, that this order is a part of. */
  simulationId?: string;
  /** Optional: Correlation ID from ERP/MES/DSP_Edge for request-response matching */
  requestId?: string;
};

export type OrderResponse = {
  /** The type of the order */
  orderType: OrderType;
  /** The actual color of the workpiece */
  type: Workpiece;
  /** The timestamp when the order was created */
  timestamp: Date;
  /** The generated unique order id */
  orderId: string;
  /** Optional: Echo of requestId from OrderRequest for correlation (ERP/MES) */
  requestId?: string;
  /** The steps an order has to succeed until the order if fulfilled */
  productionSteps: Array<OrderNavigationStep | OrderManufactureStep>;
  state: OrderState;
  /** The timestamp when the order was started */
  startedAt?: Date;
  /** The timestamp when the order was stopped */
  stoppedAt?: Date;
  /** The timestamp when the order was received */
  receivedAt?: Date;
  /** the workpiece id that is produced by this order */
  workpieceId?: string;
  /** Optional: The id of the simulation/planspiel, that this order is a part of. */
  simulationId?: string;
};

/**
 * Creates a new production order request for a given workpiece type.
 * @param type The type of the workpiece to produce.
 * @param simulationId The id of the simulation/planspiel, that this order is a part of.
 * @param timestamp The timestamp when the order was created. If not given, the current time is used.
 */
export function generateOrderRequestForProduction(
  type: Workpiece,
  simulationId?: string,
  timestamp?: Date,
): OrderRequest {
  return {
    type,
    timestamp: timestamp ?? new Date(),
    orderType: 'PRODUCTION',
    simulationId,
  };
}

/**
 * Information about known modules
 */
export type PairedModule = {
  /** The duration in seconds of the production if it can be configured */
  productionDuration?: number;
  /** The serial number of the module (FTS or manufacturing module) */
  serialNumber: string;
  /** The type of the module */
  type: DeviceType;
  /** The subtype of the module, the manufacutirn type in case of a manufacturing module */
  subType?: ModuleType;
  /** The timestamp of the initial pairing setup */
  pairedSince?: Date;
  /** The timestamp of the last received online message */
  lastSeen?: Date;
  /** Is the module currently connected */
  connected?: boolean;
  /** General busy state of the module */
  available?: AvailableState;
  /** Assignment of the module to a specific order */
  assigned?: boolean;
  /** The version of the software of the module */
  version?: string;
  /** The ip address of the controller of the module */
  ip?: string;
  /** Marks the module as having calibration options */
  hasCalibration?: boolean;
  /** Is the module in calibration mode? */
  calibrating?: boolean;
};

export type FtsPairedModule = PairedModule & {
  /** The node id the FTS is currently at or has just left. */
  lastNodeId?: string;
  /** The module the FTS is currently at or has just left. */
  lastModuleSerialNumber?: string;
  /** The load position the FTS will be using during the next docking action. */
  lastLoadPosition?: LoadingBayId | LoadingBay;
  /** FTS currently charging? */
  charging?: boolean;
  /** Current battery voltage in V */
  batteryVoltage?: number;
  /** Current battery charge in percent */
  batteryPercentage?: number;
};

export type FtsPairingRequest = {
  /** The serial number of the FTS to pair */
  serialNumber: string;
};

/** The list of all detected or paired modules */
export type PairingState = {
  modules: Array<PairedModule>;
  transports: Array<FtsPairedModule>;
};

/**
 * This interface assumes that all roads are strictly orthogonal to each other.
 * We need to refactor this if we want to support non-orthogonal roads.
 */
export enum RoadDirection {
  NORTH = 'NORTH',
  EAST = 'EAST',
  SOUTH = 'SOUTH',
  WEST = 'WEST',
}

/** A production flow containing all the modules required to produce a workpiece in order, not including HBW and DPS */
export type ProductionFlow = {
  steps: Array<ModuleType>;
};
/** The production flows for all workpiece types */
export type ProductionFlows = {
  [wp in Workpiece]?: ProductionFlow;
};

export type FactoryLayoutResponse = {
  timestamp: Date;
  success: boolean;
  message?: string;
};

/**
 * A IntersectionNode represents a point in the factory where multiple roads meet.
 * At each intersection, the FTS can take multiple roads to reach a different module.
 */
export interface FactoryNode {
  /**
   * A factory-unique ID which is used to identify a specific node in the factory.
   * If it is a module, the serialNumber of the module is used.
   * If it is a intersection, the unique ID of the intersection is used.
   */
  id: string;
}

/** The flattened data structure to store a factory road */
export interface FactoryRoadFlat {
  /**
   * The length of the road in millimeters. This needs to represent the actual length of the road,
   * otherwise navigation won't work.
   */
  length: number;
  /**
   * The direction in which the road is pointing.
   */
  direction: RoadDirection;
  /** The id of the starting point of the road */
  from: string;
  /** The id of the end point of the road */
  to: string;
}

/**
 * Format of the JSON data the factory data is loaded from
 */
export interface FactoryLayout {
  modules: Module[];
  intersections: FactoryNode[];
  roads: FactoryRoadFlat[];
}

export interface ModuleSettings {
  serialNumber: string;
  duration: number;
}

/**
 * module calibration
 */
export enum ModuleCalibrationCommand {
  SET_VALUES = 'setCalibrationValues',
  RESET = 'resetCalibration',
  STORE = 'storeCalibrationValues',
  SELECT = 'selectCalibrationPosition',
  TEST = 'testCalibrationPosition',
  START = 'startCalibration',
  STOP = 'stopCalibration',
}

export interface ModuleCalibration {
  timestamp: Date;
  serialNumber: string;
  command: ModuleCalibrationCommand;
  factory?: boolean;
  position?: string;
  references?: Array<ReferenceValue>;
}
export interface ModuleCalibrationState {
  timestamp: Date;
  serialNumber: string;
  calibrating: boolean;
  references?: Array<ReferenceValue>;
  status_references?: Array<ReferenceValue>;
}

/**
 * Payload for a request to reset the factory to an initial state.
 */
export interface ResetRequest {
  timestamp: Date;
  withStorage?: boolean;
}
/**
 * Payload for a request to reset the factory layout to the default layout.
 */
export interface DefaultLayoutRequest {
  timestamp: Date;
}

/**
 * Payload for a request to initiate a charge navigation order or stop it for the specified FTS.
 */
export interface FtsChargeRequest {
  /** The FTS serialNumber for which the request should be executed */
  serialNumber: string;
  /** true = start charge, false = stop charge */
  charge: boolean;
}

/**
 * Payload for a request to remove a module, that is not configured in the layout
 */
export interface DeleteModuleRequest {
  serialNumber: string;
}

/**
 * Everything regarding the general configuration of the factory.
 */
export interface GeneralConfig {
  /** The planned production duration of a workpiece in seconds */
  productionDurations: {
      [wp in Workpiece]?: number;
  };
  productionSettings: {
    maxParallelOrders: number;
  };
  ftsSettings: {
    chargeThresholdPercent: number,
  };
}


/**
 * Payload for a request to park the factory.
 */
export interface ParkRequest {
  timestamp: Date;
}

/**
 * Data about a module with a mismatched version.
 */
export interface MismatchedModule {
  serialNumber: string;
  deviceType: DeviceType;
  moduleType: ModuleType | undefined;
  seriesName: string;
  seriesUnknown: boolean;
  version: string;
  requiredVersion: string | undefined;
  is24V: boolean;
  isTXT: boolean;
}

/**
 * The payload for a message that contains all modules with a mismatched version.
 */
export interface MismatchedVersionMessage {
  timestamp: Date;
  ccuVersion: string;
  mismatchedModules: MismatchedModule[];
}
