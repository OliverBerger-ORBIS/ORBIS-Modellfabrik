/**
 * Type definitions for MQTT payload structures
 * Based on actual payloads from data/omf-data/test_topics/
 */

// Order completion payload types
export interface ProductionStep {
  id: string;
  type: string;
  state: string;
  source?: string;
  target?: string;
  startedAt: string;
  stoppedAt?: string;
  command?: string;
  moduleType?: string;
  serialNumber?: string;
  dependentActionId?: string;
}

export interface OrderCompleted {
  orderType: string;
  type: string; // Color: RED, BLUE, WHITE
  timestamp: string;
  orderId: string;
  productionSteps: ProductionStep[];
  receivedAt?: string;
  state: string;
  workpieceId?: string;
  startedAt: string;
  stoppedAt: string;
}

// FTS-related payload types (VDA 5050 based)
export interface FtsState {
  timestamp?: string;
  actionState?: string;
  motionState?: string;
  batteryLevel?: number;
  driving?: boolean;
  orderId?: string;
  orderUpdateId?: number;
  errors?: any[];
  loads?: any[];
  // Additional fields as per VDA 5050
  [key: string]: any;
}

export interface FtsConnection {
  connected: boolean;
  timestamp?: string;
  connectionState?: string;
  [key: string]: any;
}

export interface FtsOrder {
  orderId: string;
  orderUpdateId?: number;
  timestamp?: string;
  orderType?: string;
  loadType?: string;
  nodes?: any[];
  edges?: any[];
  [key: string]: any;
}

export interface FtsInstantAction {
  actionId: string;
  actionType: string;
  timestamp?: string;
  [key: string]: any;
}

export interface FtsFactsheet {
  serialNumber: string;
  manufacturer?: string;
  version?: string;
  timestamp?: string;
  [key: string]: any;
}

// Module state payload types
export interface ModuleState {
  state: string; // e.g., IDLE, MANUFACTURE, ERROR
  timestamp?: string;
  serialNumber?: string;
  moduleType?: string;
  orderId?: string;
  [key: string]: any;
}

// Environment sensor payload types (BME680)
export interface EnvironmentData {
  timestamp?: string;
  ts?: string;
  temperature?: number;
  humidity?: number;
  iaq?: number; // Indoor Air Quality
  pressure?: number;
  gasResistance?: number;
  [key: string]: any;
}

// Stock/inventory payload types
export interface Workpiece {
  id: string;
  type: string; // Color
  state: string; // RAW, PROCESSED
}

export interface StockItem {
  workpiece: Workpiece;
  location: string;
  hbw: string; // Serial number of HBW
}

export interface StockData {
  ts: string;
  stockItems: StockItem[];
}

// Generic MQTT message wrapper
export interface MqttMessage {
  topic: string;
  payload: string | Buffer;
  timestamp: Date;
}
