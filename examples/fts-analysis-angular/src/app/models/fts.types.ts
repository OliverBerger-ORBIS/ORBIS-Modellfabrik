/**
 * FTS/AGV Data Types
 * Based on real MQTT message structures from data/omf-data/fts-analysis/
 * Following VDA5050 standard for AGV communication
 */

/** Battery state information from FTS state messages */
export interface FtsBatteryState {
  currentVoltage: number;
  minVolt: number;
  maxVolt: number;
  percentage: number;
  charging: boolean;
}

/** Action state from FTS state messages (VDA5050) */
export type ActionStateType = 'WAITING' | 'INITIALIZING' | 'RUNNING' | 'FINISHED' | 'FAILED' | string;

/** Action command types */
export type ActionCommandType = 'DOCK' | 'TURN' | 'PASS' | 'PICK' | 'DROP' | 'clearLoadHandler' | string;

/** Individual action state */
export interface FtsActionState {
  id: string;
  command: ActionCommandType;
  state: ActionStateType;
  timestamp: string;
}

/** Load information (workpiece on FTS) */
export interface FtsLoadInfo {
  loadId: string | null;
  loadType: 'BLUE' | 'WHITE' | 'RED' | null;
  loadPosition: string;
}

/** Complete FTS state from fts/v1/ff/{serialNumber}/state topic */
export interface FtsState {
  serialNumber: string;
  headerId: number;
  timestamp: string;
  orderId: string;
  orderUpdateId: number;
  
  // Position
  lastNodeId: string;
  lastNodeSequenceId: number;
  lastCode: string;
  
  // Status
  driving: boolean;
  paused: boolean;
  waitingForLoadHandling: boolean;
  
  // Battery
  batteryState: FtsBatteryState;
  
  // Actions
  actionState: FtsActionState;
  actionStates: FtsActionState[];
  
  // Loads
  load: FtsLoadInfo[];
  
  // Node/Edge states (VDA5050)
  nodeStates: unknown[];
  edgeStates: unknown[];
  
  // Errors
  errors: unknown[];
}

/** Action metadata for turn actions */
export interface TurnActionMetadata {
  direction: 'LEFT' | 'RIGHT';
}

/** Action metadata for dock actions */
export interface DockActionMetadata {
  loadId?: string;
  loadType?: 'BLUE' | 'WHITE' | 'RED';
  loadPosition?: string;
}

/** Node action in FTS order */
export interface FtsNodeAction {
  id: string;
  type: ActionCommandType;
  metadata?: TurnActionMetadata | DockActionMetadata;
}

/** Node in FTS order (VDA5050) */
export interface FtsOrderNode {
  id: string;
  linkedEdges: string[];
  action?: FtsNodeAction;
}

/** Edge in FTS order (VDA5050) */
export interface FtsOrderEdge {
  id: string;
  length: number;
  linkedNodes: string[];
}

/** FTS navigation order from fts/v1/ff/{serialNumber}/order topic */
export interface FtsOrder {
  timestamp: string;
  orderId: string;
  orderUpdateId: number;
  serialNumber: string;
  nodes: FtsOrderNode[];
  edges: FtsOrderEdge[];
}

/** FTS connection status from fts/v1/ff/{serialNumber}/connection topic */
export interface FtsConnection {
  serialNumber: string;
  connectionState: 'ONLINE' | 'OFFLINE' | string;
  timestamp: string;
}

/** CCU Order for FTS navigation context */
export interface CcuOrderInfo {
  orderId: string;
  type?: string;
  state?: string;
  timestamp?: string;
}

/** Track & Trace event for workpiece history */
export interface TrackTraceEvent {
  timestamp: string;
  eventType: 'DOCK' | 'PICK' | 'DROP' | 'TRANSPORT' | 'PROCESS' | string;
  workpieceId?: string;
  workpieceType?: string;
  moduleId?: string;
  location?: string;
  orderId?: string;
  orderType?: 'STORAGE' | 'PRODUCTION' | string;
  stationId?: string;    // Station/module where action takes place (e.g., DRILL, MILL)
  stationName?: string;  // Human-readable station name
  processDuration?: number; // Process duration in seconds (for PROCESS events)
  details?: Record<string, unknown>;
}

/** Station task group - groups PICK, PROCESS, DROP at a station */
export interface StationTaskGroup {
  stationId: string;
  stationName: string;
  events: TrackTraceEvent[];
  startTime?: string;
  endTime?: string;
}

/** Order context for Track & Trace */
export interface OrderContext {
  orderId: string;
  orderType: 'STORAGE' | 'PRODUCTION' | string;
  purchaseOrderId?: string;  // From ERP system
  customerOrderId?: string;  // For production orders
  startTime?: string;
  endTime?: string;
  fromLocation?: string;
  toLocation?: string;
}

/** Workpiece tracking history */
export interface WorkpieceHistory {
  workpieceId: string;
  workpieceType: 'BLUE' | 'WHITE' | 'RED' | string;
  events: TrackTraceEvent[];
  currentLocation?: string;
  currentState?: string;
  orders?: OrderContext[];  // Order context for this workpiece
}

/** Raw MQTT message wrapper */
export interface MqttMessage<T = unknown> {
  topic: string;
  payload: T;
  timestamp: string;
  qos?: number;
}

/** Helper function to parse FTS state payload */
export function parseFtsStatePayload(payloadString: string): FtsState | null {
  try {
    return JSON.parse(payloadString) as FtsState;
  } catch {
    return null;
  }
}

/** Helper function to parse FTS order payload */
export function parseFtsOrderPayload(payloadString: string): FtsOrder | null {
  try {
    return JSON.parse(payloadString) as FtsOrder;
  } catch {
    return null;
  }
}

/** Helper to get battery level classification */
export function getBatteryLevel(percentage: number): 'high' | 'medium' | 'low' {
  if (percentage >= 60) return 'high';
  if (percentage >= 30) return 'medium';
  return 'low';
}

/** Helper to get action state display class */
export function getActionStateClass(state: ActionStateType): string {
  switch (state.toUpperCase()) {
    case 'WAITING': return 'waiting';
    case 'INITIALIZING': return 'initializing';
    case 'RUNNING': return 'running';
    case 'FINISHED': return 'finished';
    case 'FAILED': return 'failed';
    default: return 'unknown';
  }
}
