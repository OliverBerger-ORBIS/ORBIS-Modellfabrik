import { Workpiece } from './ccu';
import { FtsCommandType, LoadingBayId } from './fts';
import { ModuleCommandType, ModuleType } from './module';

export type ReferenceValue = {
  referenceKey: string;
  referenceValue: string | number | boolean;
};

/**
 * The VDA 5050 protocol is used to communicate between the factory and the
 * modules and FTSs. It is based on the VDA 5050 standard.
 * @see https://www.vda.de/de/services/Publikationen/vda-5050-2019-04.html
 *
 * The protocol is based on the following principles:
 * - The factory is the master and the modules and FTSs are the slaves.
 * - The factory sends commands to the modules and FTSs.
 * - The modules and FTSs send status updates to the factory.
 */

/**
 * @typedef {Object} VdaError
 * @property {string} errorType - The type of error that occured.
 * @property {Date} timestamp - The timestamp of the error.
 * @property {string} errorLevel - The level of the error.
 * @property {Array<{referenceKey: string, referenceValue: string}>} errorReferences - (Optional) The references that resulted in the error.
 */
export type VdaError = {
  errorType: string; // --> PICK_error, DROP_error, DRILL_error, FIRE_error, ...
  timestamp: Date;
  errorLevel: 'WARNING' | 'FATAL';
  errorReferences?: Array<ReferenceValue>;
};

export type VdaInformation = {
  infoType: string;
  infoLevel: 'DEBUG' | 'INFO';
  infoReferences?: Array<ReferenceValue>;
};

export enum LoadType {
  BLUE = 'BLUE',
  WHITE = 'WHITE',
  RED = 'RED',
}

export type Load = {
  loadId?: string | null;
  loadType: LoadType | null;
  loadPosition?: string;
  loadTimestamp?: number;
};

export type CarryLoad = Load & {
  loadPosition: LoadingBayId;
};

export enum State {
  WAITING = 'WAITING',
  INITIALIZING = 'INITIALIZING',
  RUNNING = 'RUNNING',
  PAUSED = 'PAUSED',
  FINISHED = 'FINISHED',
  FAILED = 'FAILED',
}

/**
 * The state of an action reported by a production module or FTS.
 */
export type ActionState<
  T extends InstantActions | ModuleCommandType | FtsCommandType
> = {
  /** The uniqe id of the action, generally a UUID */
  id: string;
  /** The timestamp of the status change */
  timestamp: Date;
  /** The state of the action, failure means the action could not be finished.
   *  A finihsed with an unsatisfactory result should be reported through `result` */
  state: State;
  /** The action command or action type */
  command?: T;
  /** (Optional) The result of a finished action with multiple result options */
  result?: string;
  /** (Optional) additional metadata for this action state */
  metadata?: unknown;
};

export type NodeState = {};
export type EdgeState = {};

export type BatteryState = {
  /** The current charge state */
  charging?: boolean
  /** The current battery level in percent */
  percentage?: number;
  /** The max battery level in volts */
  maxVolt?: number;
  /** The min battery level in volts */
  minVolt?: number;
  /** The current battery level in volts */
  currentVoltage?: number;
};

export enum ConnectionState {
  ONLINE = 'ONLINE',
  OFFLINE = 'OFFLINE',
  CONNECTIONBROKEN = 'CONNECTIONBROKEN',
}

export type Connection = {
  headerId: number;
  timestamp: Date;
  version: string;
  ip: string;
  manufacturer: string;
  serialNumber: string;
  connectionState: ConnectionState;
};

export type LoadSet = {
  setName: string;
  loadType: LoadType;
  maxAmount?: number;
};

export type Factsheet = {
  headerId: number;
  /* Timestamp in ISO8601 format (YYYY-MM-DDTHH:mm:ss.ssZ). */
  timestamp: Date;
  version: string;
  manufacturer: string;
  serialNumber: string;
  typeSpecification: {
    seriesName: string;
    agvClass?: string;
    moduleClass?: ModuleType;
    navigationTypes?: Array<string>;
  };
  physicalParameters?: any;
  protocolLimits?: any;
  protocolFeatures: {
    agvActions?: Array<{
      actionType: string;
      actionScopes?: 'NODE' | 'EDGE';
      actionParameters?: {
        parameterName: string;
        parameterType: string;
        parameterDescription: string;
      };
    }>;
    moduleActions?: Array<{
      actionType: string;
      actionParameters?: {
        parameterName: string;
        parameterType: string;
        parameterDescription: string;
      };
    }>;
    moduleParameters?: {
      clearModuleOnPick?: boolean;
    };
  };
  agvGeometry?: any;
  loadSpecification?: {
    loadPositions?: LoadingBayId;
    loadSets?: Array<LoadSet>;
  };
  localizationParameters?: any;
};

export enum InstantActions {
  FACTSHEET_REQUEST = 'factsheetRequest',
  /** Request the current state `waitingForLoadHandler` of the FTS so that it can receive new commands */
  CLEAR_LOAD_HANDLER = 'clearLoadHandler',
  /** Initialize the FTS, have it perform a docking action and then assume it to be docked at the given module serial number */
  FIND_INITIAL_DOCK_POSITION = 'findInitialDockPosition',
  /** Request to set the storage of the HBW to the desired load */
  SET_STORAGE = 'SET_STORAGE',
  /** Request to reset the  */
  RESET = 'reset',
  SET_STATUS_LED = 'setStatusLED',
  CALIBRATION_SET_VALUES = 'setCalibrationValues',
  CALIBRATION_RESET = 'resetCalibration',
  CALIBRATION_STORE = 'storeCalibrationValues',
  CALIBRATION_SELECT = 'selectCalibrationPosition',
  CALIBRATION_TEST = 'testCalibrationPosition',
  CALIBRATION_START = 'startCalibration',
  CALIBRATION_STOP = 'stopCalibration',
  ANNOUNCE_OUTPUT = 'announceOutput',
  CANCEL_STORAGE_ORDER = 'cancelStorageOrder',
  STOP_CHARGING = 'stopCharging',
}

/** These instantActions do not matter for the availability state of a module */
export const passiveInstantActions = [
  InstantActions.FACTSHEET_REQUEST,
  InstantActions.SET_STATUS_LED,
];

/** The parameters to send when pairing an FTS to the factory */
export type FindInitialDockPositionMetadata = {
  /** The nodeId / serial number the FTS will be docked at */
  nodeId: string;
};

/** The parameters to send when clearing the load handler status */
export type ClearLoadHandlerMetadata = {
  /** True if the module removed the load from the FTS, otherwise false */
  loadDropped: boolean;
  /** The id of the workpiece in the active loading bay */
  loadId?: string;
  /** The type of the workpiece in the active loading bay */
  loadType?: Workpiece;
  /** The loading bay used */
  loadPosition?: string;
};

/** The parameters to send when clearing the load handler status */
export type SetStorageMetadata = {
  /** The contents of the storage bays */
  contents: {
    [storageBayId: string]: {
      type?: Workpiece;
      workpieceId?: string;
    };
  };
};
/** The parameters to send when calibrating */
export type CalibrationMetadata = {
  /** The position to use if the calibration action requires it */
  position?: string;
  /** Reset to default factory values */
  factory?: boolean;
  /** The new reference values when setting them */
  references?: Array<ReferenceValue>;
};

/** The parameters to send when announcing an output PICK command */
export type AnnounceOutputMetadata = {
  /** The orderid that will be used for the PICK command */
  orderId: string;
  /** The workpiece type to expect, optional */
  type?: Workpiece;
};

/** True turns on the colored LED on the DPS, false turns it off */
export type StatusLEDMetadata = {
  red: boolean,
  yellow: boolean,
  green: boolean
}

export type InstantAction = {
  serialNumber: string;
  timestamp: Date;
  actions: Array<{
    actionType: InstantActions;
    actionId: string;
    metadata?:
      | ClearLoadHandlerMetadata
      | FindInitialDockPositionMetadata
      | SetStorageMetadata
      | CalibrationMetadata
      | StatusLEDMetadata
      | AnnounceOutputMetadata;
  }>;
};
