export type OrderLifecycleState =
  | 'ENQUEUED'
  | 'PENDING'
  | 'IN_PROGRESS'
  | 'RUNNING'
  | 'FINISHED'
  | 'COMPLETED'
  | 'FAILED'
  | string;

export interface ProductionStep {
  id: string;
  type: 'NAVIGATION' | 'MANUFACTURE' | string;
  state: OrderLifecycleState;
  command?: string;
  moduleType?: string;
  dependentActionId?: string;
  source?: string;
  target?: string;
  description?: string;
  startedAt?: string;
  stoppedAt?: string;
}

export interface OrderActive {
  orderId: string;
  requestId?: string; // From CCU response when OSF-UI sent it in request (ERP/MES correlation)
  type?: string;
  orderType?: 'PRODUCTION' | 'STORAGE' | string;
  productId?: string;
  quantity?: number;
  state?: OrderLifecycleState;
  status?: OrderLifecycleState;
  productionSteps?: ProductionStep[];
  receivedAt?: string;
  startedAt?: string;
  updatedAt?: string;
  stoppedAt?: string;
}

export interface StockMessage {
  moduleId: string;
  partId: string;
  amount: number;
  unit?: string;
  timestamp?: string;
}

export type WorkpieceType = 'BLUE' | 'WHITE' | 'RED' | string;
export type WorkpieceInventoryState = 'RAW' | 'RESERVED' | 'FINISHED' | 'PROCESSING' | string;

export interface StockWorkpiece {
  id?: string;
  type?: WorkpieceType;
  state?: WorkpieceInventoryState;
}

export interface StockSnapshotItem {
  workpiece?: StockWorkpiece | null;
  location: string;
  hbw?: string;
}

export interface StockSnapshot {
  ts?: string;
  stockItems: StockSnapshotItem[];
}

export interface ModuleState {
  moduleId: string;
  state: 'idle' | 'working' | 'error' | 'maintenance';
  lastSeen?: string;
  details?: Record<string, any>;
}

export interface FtsState {
  ftsId: string;
  position?: { x: number; y: number };
  speed?: number;
  status?: 'idle' | 'moving' | 'error';
  lastSeen?: string;
}

export type ModuleAvailabilityStatus = 'READY' | 'BUSY' | 'BLOCKED' | 'Unknown' | string;

export interface PairingModuleSnapshot {
  serialNumber: string;
  type?: string;
  subType?: string;
  connected?: boolean;
  available?: ModuleAvailabilityStatus;
  pairedSince?: string;
  assigned?: boolean;
  ip?: string;
  version?: string;
  lastSeen?: string;
  hasCalibration?: boolean;
}

export interface PairingTransportSnapshot {
  serialNumber: string;
  type?: string;
  connected?: boolean;
  available?: ModuleAvailabilityStatus;
  ip?: string;
  version?: string;
  lastSeen?: string;
  charging?: boolean;
  batteryVoltage?: number;
  batteryPercentage?: number;
  lastNodeId?: string;
  lastModuleSerialNumber?: string;
  lastLoadPosition?: string;
}

export interface ModuleFactsheetSnapshot {
  serialNumber: string;
  timestamp?: string;
  topic?: string;
  payload?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface ModulePairingState {
  modules: PairingModuleSnapshot[];
  transports: PairingTransportSnapshot[];
  timestamp?: string;
}

export interface ModuleOverviewStatus {
  id: string;
  subType?: string;
  connected: boolean;
  availability: ModuleAvailabilityStatus;
  hasCalibration?: boolean;
  assigned?: boolean;
  ip?: string;
  version?: string;
  pairedSince?: string;
  lastSeen?: string;
  configured: boolean;
  factsheetTimestamp?: string;
  messageCount: number;
  lastUpdate: string;
}

export interface TransportOverviewStatus {
  id: string;
  connected: boolean;
  availability: ModuleAvailabilityStatus;
  ip?: string;
  version?: string;
  lastSeen?: string;
  charging?: boolean;
  batteryVoltage?: number;
  batteryPercentage?: number;
  lastNodeId?: string;
  lastModuleSerialNumber?: string;
  lastLoadPosition?: string;
  messageCount: number;
  lastUpdate: string;
}

export interface ModuleOverviewState {
  modules: Record<string, ModuleOverviewStatus>;
  transports: Record<string, TransportOverviewStatus>;
}

export interface InventorySlotState {
  location: string;
  workpiece: StockWorkpiece | null;
}

export interface InventoryOverviewState {
  slots: Record<string, InventorySlotState>;
  availableCounts: Record<WorkpieceType, number>;
  reservedCounts: Record<WorkpieceType, number>;
  lastUpdated: string;
}

export interface FlowDefinition {
  steps: string[];
}

export type ProductionFlowMap = Record<WorkpieceType, FlowDefinition>;

export interface Bme680Snapshot {
  ts?: string;
  t?: number;
  rt?: number;
  h?: number;
  rh?: number;
  p?: number;
  iaq?: number;
  aq?: number;
  gr?: number;
}

export interface LdrSnapshot {
  ts?: string;
  br?: number;
  ldr?: number;
}

export interface CameraFrameSnapshot {
  ts?: string;
  data?: string;
}

export interface SensorOverviewState {
  timestamp?: string;
  temperatureC?: number;
  humidityPercent?: number;
  pressureHpa?: number;
  lightLux?: number;
  iaq?: number;
  airQualityScore?: number;
  airQualityClassification?: string;
}

export interface CameraFrame {
  timestamp?: string;
  dataUrl: string;
}

export interface ProductionDurationsConfig {
  [key: string]: number;
}

export interface ProductionSettingsConfig {
  maxParallelOrders?: number;
  [key: string]: unknown;
}

export interface FtsSettingsConfig {
  chargeThresholdPercent?: number;
  [key: string]: unknown;
}

export interface CcuConfigSnapshot {
  productionDurations?: ProductionDurationsConfig;
  productionSettings?: ProductionSettingsConfig;
  ftsSettings?: FtsSettingsConfig;
  timestamp?: string;
}

export interface ReplayEnvelope {
  topic: string;
  payload: any;
  timestamp?: string;
  seq?: number;
}

/**
 * Basic parser helpers (simple, synchronous).
 * Replace with zod/io-ts validators after extracting real payloads.
 */
export const safeJsonParse = (s: unknown) => {
  if (typeof s === 'string') {
    try {
      return JSON.parse(s);
    } catch {
      return s;
    }
  }
  return s;
};
