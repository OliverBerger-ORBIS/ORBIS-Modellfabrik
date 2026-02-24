import { ActionState, BatteryState, CarryLoad, EdgeState, InstantActions, NodeState, VdaError, } from './vda';

export const NODE_ID_UNKNOWN = 'UNKNOWN';

export enum FtsErrors {
  RESET = 'RESET',
  ACTION_DISMISSED = 'ACTION_DISMISSED',
  COLLISION = 'COLLISION',
}

export type FtsState = {
  headerId?: number;
  timestamp: Date;
  serialNumber: string;
  orderId: string;
  orderUpdateId: number;
  lastNodeId: string;
  lastNodeSequenceId: number;
  nodeStates: Array<NodeState>;
  edgeStates: Array<EdgeState>;
  driving: boolean;
  waitingForLoadHandling?: boolean;
  paused: boolean;
  batteryState?: BatteryState;
  errors: Array<VdaError>;
  load: Array<CarryLoad>;
  actionState?: ActionState<FtsCommandType | InstantActions> | null;
  actionStates?: Array<ActionState<FtsCommandType | InstantActions>> | null;
  lastCode?: unknown;
};

/**
 * Actions that can be performed on a node by a FTS.
 */
export enum FtsCommandType {
  /** Start docking which uses the FTS sensors to try to dock to anything that is straight ahead */
  DOCK = 'DOCK',
  /** Drive by the node with no additional action */
  PASS = 'PASS',
  /** Turn the FTS by a specified degree and direction. Used to navigate intersections */
  TURN = 'TURN',
}

/* The loading bay position of an FTS */
export type LoadingBayId = '1' | '2' | '3';
export enum LoadingBay {
  LEFT = '1',
  MIDDLE = '2',
  RIGHT = '3',
}

/** The number of bays of an fts */
export const LOADING_BAY_COUNT = 3;
