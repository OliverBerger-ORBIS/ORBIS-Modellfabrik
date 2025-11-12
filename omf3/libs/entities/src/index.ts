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
}

export interface StockMessage {
  moduleId: string;
  partId: string;
  amount: number;
  unit?: string;
  timestamp?: string;
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
