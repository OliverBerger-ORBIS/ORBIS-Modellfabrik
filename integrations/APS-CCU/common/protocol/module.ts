import { Workpiece } from './ccu';
import { ActionState, InstantActions, Load, VdaError, VdaInformation } from './vda';

/**
 * A list of all supported module types in the future factory and their unique names.
 */
export enum ModuleType {
  DRILL = 'DRILL',
  /**
   * The START module is a placeholder for the first navigation step in an order.
   * As it is unknown where the FTS starts during order generation, the start module will be set to START
   * */
  START = 'START',
  MILL = 'MILL',
  DPS = 'DPS',
  AIQS = 'AIQS',
  HBW = 'HBW',
  OVEN = 'OVEN',
  CHRG = 'CHRG',
}

/** Modules that support the production, but do not perform manufacturing processes **/
export const SUPPORT_MODULES = new Set([
  ModuleType.START,
  ModuleType.HBW,
  ModuleType.DPS,
  ModuleType.CHRG,
]);

/** The default production duration if nothing is configured */
export const MODULE_DEFAULT_PRODUCTION_DURATION = 5;

export type Module = {
  serialNumber: string;
  type: ModuleType;
  placeholder?: boolean;
};
export type ModuleState = {
  headerId?: number;
  type: ModuleType;
  timestamp: Date;
  serialNumber: string;
  orderId: string;
  orderUpdateId: number;
  paused: boolean;
  actionState?: ActionState<ModuleCommandType | InstantActions> | null;
  actionStates?: Array<ActionState<ModuleCommandType | InstantActions>> | null;
  errors: Array<VdaError>;
  loads?: Array<Load>;
  information?: Array<VdaInformation>;
  operatingMode?: 'AUTOMATIC' | 'TEACHIN';
  metadata?: unknown;
};

export const ModuleInfoTypes = {
  CALIBRATION_DATA: "calibration_data",
  CALIBRATION_STATUS: "calibration_status"
};
export const ModuleCalibrationStatusKeys = {
  POSITIONS_CURRENT: 'POSITIONS.CURRENT',
  POSITIONS_AVAILABLE: 'POSITIONS.AVAILABLE',
};

/**
 * A union of all supported commands by any module.
 */
export enum ModuleCommandType {
  /** Drilling module */
  DRILL = 'DRILL',
  /** Milling module   */
  MILL = 'MILL',
  /** AIQS module */
  CHECK_QUALITY = 'CHECK_QUALITY',
  /** OVEN module */
  FIRE = 'FIRE',
  /** All modules: Load the workpiece from the module onto the FTS */
  DROP = 'DROP',
  /** All modules: take the workpiece from the FTS. Some modules like DPS or HBW will also store/output the workpiece **/
  PICK = 'PICK',
}

/** The mapping from module type to the production command it supports.
 * Some modules may not have a production command and are not listed here. */
export const MODULE_COMMAND_MAP: { [x in ModuleType]?: ModuleCommandType } = {
  [ModuleType.DRILL]: ModuleCommandType.DRILL,
  [ModuleType.AIQS]: ModuleCommandType.CHECK_QUALITY,
  [ModuleType.MILL]: ModuleCommandType.MILL,
  [ModuleType.OVEN]: ModuleCommandType.FIRE,
};

/** The result of a finished quality check action. */
export enum QualityResult {
  /** The workpiece passed the quality check.  */
  PASSED = 'PASSED',
  /** The workpiece failed the quality check. */
  FAILED = 'FAILED',
}

export type StoreMetadata = {
  type: Workpiece;
  workpieceId?: string;
};

export type DurationMetadata = {
  duration: number;
  // type: Workpiece;
};

export type ProductionCommand = {
  timestamp: Date;
  serialNumber: string;
  orderId: string;
  orderUpdateId: number;
  action: Action;
};

/** The result of a production action
 * In Delivery          = 100  --> ModuleType.DPS and command ModuleCommandType.DROP
 * Quality Assurance    = 200  --> ModuleType.AIQS and command ModuleCommandType.CHECK_QUALITY
 * Stockpiling          = 300  --> ModuleType.HBW and command ModuleCommandType.PICK
 * Stock removal        = 400  --> ModuleType.HBW and command ModuleCommandType.DROP
 * Processing OVEN      = 500  --> ModuleType.OVEN and command ModuleCommandType.FIRE
 * Processing Mill      = 600  --> ModuleType.MILL and command ModuleCommandType.MILL
 * Processing Drill     = 700  --> ModuleType.DRILL and command ModuleCommandType.DRILL
 * Shipping             = 800  --> ModuleType.DPS and command ModuleCommandType.PICK
 *
 * use getNfcPosition to get the correct NFC position for the ModuleType and ModuleCommandType.
 * */
export type NfcPosition = 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800;

/** Metadata for delivery Process */
export type DeliveryMetadata = {
  workpiece: {
    workpieceId: string;
    type: Workpiece;
    state: 'PROCESSED',
    history: Array<HistoryPoint>;
  }
};
/** History Point defines a timestamp with a <finished/started>(?) (has to be clarified) process on a specific module */
export type HistoryPoint = {
  ts: number; // the timestamp has to be a unix timestamp because ROBO Pro Coding is unable to create it from an ISO string
  // number defined as <100/200/300/400/500/600/700/800/>
  code: NfcPosition;
};

export type Action = {
  id: string;
  command: ModuleCommandType;
  metadata?: DurationMetadata | StoreMetadata | DeliveryMetadata;
};

/**
 * Generates a unique key for the mapping of ModuleCommandType and ModuleType to NFC position
 * @param moduleType the module type
 * @param moduleCommand the module command
 */
const generateAssociationKeyNfcModuleCommand = (moduleType: ModuleType, moduleCommand: ModuleCommandType): string => {
  return `${moduleType}_${moduleCommand}`;
}

/**
 * Mapping of ModuleCommandType and ModuleType to NFC position
 */
const nfcModuleCommandMap: Map<string, NfcPosition> = new Map<string, NfcPosition>([
  [
    generateAssociationKeyNfcModuleCommand(ModuleType.DPS, ModuleCommandType.DROP), 100
  ],
  [
    generateAssociationKeyNfcModuleCommand(ModuleType.AIQS, ModuleCommandType.CHECK_QUALITY), 200
  ],
  [
    generateAssociationKeyNfcModuleCommand(ModuleType.HBW, ModuleCommandType.PICK), 300
  ],
  [
    generateAssociationKeyNfcModuleCommand(ModuleType.HBW, ModuleCommandType.DROP), 400
  ],
  [
    generateAssociationKeyNfcModuleCommand(ModuleType.OVEN, ModuleCommandType.FIRE), 500
  ],
  [
    generateAssociationKeyNfcModuleCommand(ModuleType.MILL, ModuleCommandType.MILL), 600
  ],
  [
    generateAssociationKeyNfcModuleCommand(ModuleType.DRILL, ModuleCommandType.DRILL), 700
  ],
  [
    generateAssociationKeyNfcModuleCommand(ModuleType.DPS, ModuleCommandType.PICK), 800
  ],
]);

/**
 * Returns the NFC position for the given module type and module command.
 * @param moduleType
 * @param moduleCommand
 * @returns the NFC position, undefined if the combination is not supported
 */
export const getNfcPosition = (moduleType: ModuleType, moduleCommand: ModuleCommandType): NfcPosition | undefined => {
  const key = generateAssociationKeyNfcModuleCommand(moduleType, moduleCommand);
  return nfcModuleCommandMap.get(key);
}

export enum StorageModuleBayPosition {
  A1 = "A1",
  A2 = "A2",
  A3 = "A3",
  B1 = "B1",
  B2 = "B2",
  B3 = "B3",
  C1 = "C1",
  C2 = "C2",
  C3 = "C3",
}
