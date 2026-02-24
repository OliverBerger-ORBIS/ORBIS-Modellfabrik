import { Workpiece } from '../../../../common/protocol';
import { FtsCommandType, LoadingBayId } from '../../../../common/protocol/fts';

/**
 * The direction of a turn action.
 */
export enum Direction {
  /** Turns the FTS counterclockwise by 90° */
  LEFT = 'LEFT',
  /** Turns the FTS clockwise by 90° */
  RIGHT = 'RIGHT',
  /** Turns the FTS by 180° to face backwards */
  BACK = 'BACK',
}

/** Metadata for a turn action */
export interface DirectionMetadata {
  direction: Direction;
}

/** Metadata for a dock action containing the information which loading bay should be used */
export interface DockingMetadata {
  /** The id of the workpieces nfc chip */
  loadId?: string;
  loadType?: Workpiece;
  loadPosition: LoadingBayId;
  noLoadChange?: boolean;
  charge?: boolean;
}

export interface Action {
  type: FtsCommandType;
  metadata?: DirectionMetadata | DockingMetadata;
  id: string;
}

/**
 * A Navigation point on the factory's map.
 * Some way point in a long straight line, mostly on intersections though.
 */
export interface Node {
  id: string;
  linkedEdges: Array<string>;
  action?: Action;
}

/**
 * An edge between two nodes. A digital representation of a physical path that can be used
 * by the FTS to navigate the factory.
 */
export interface Edge {
  id: string;
  length: number;
  linkedNodes: Array<string>;
}

export interface FtsOrder {
  timestamp: Date;
  serialNumber: string;
  orderId: string;
  orderUpdateId: number;
  nodes: Array<Node>;
  edges: Array<Edge>;
}
