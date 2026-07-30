import { Injectable, OnDestroy, inject } from '@angular/core';
import { utcIsoTimestampMs } from '@osf/entities';
import { BehaviorSubject, Observable, combineLatest, Subscription, merge } from 'rxjs';
import { map, distinctUntilChanged, shareReplay, startWith, filter } from 'rxjs/operators';
import { MessageMonitorService } from './message-monitor.service';
import { ModuleNameService } from './module-name.service';
import { ShopfloorMappingService } from './shopfloor-mapping.service';
import { EnvironmentService } from './environment.service';
import { AgvRouteService } from './agv-route.service';
import { ErpOrderDataService } from './erp-order-data.service';
import { CorrelationInfoService } from './correlation-info.service';
import {
  TrackTraceEnvironmentService,
  type TrackTraceEnvironmentSnapshot,
} from './track-trace-environment.service';

/**
 * Track & Trace event for workpiece history
 */
export interface TrackTraceEvent {
  timestamp: string;
  eventType: 'DOCK' | 'PICK' | 'DROP' | 'TRANSPORT' | 'PROCESS' | 'TURN' | 'PASS' | string;
  workpieceId?: string;
  workpieceType?: string;
  moduleId?: string; // Module serial ID (extracted from topic)
  moduleName?: string; // Module display name (FTS, MILL, DRILL, HBW, DPS, AIQS)
  location?: string;
  orderId?: string; // Main order ID
  orderUpdateId?: number; // Order update ID
  subOrderId?: string; // Sub-order ID (for events within an order)
  actionId?: string; // Action ID (for sorting when subOrderId is identical)
  orderType?: 'STORAGE' | 'PRODUCTION' | string;
  stationId?: string; // Station/module where action takes place (e.g., DRILL, MILL)
  stationName?: string; // Human-readable station name
  processDuration?: number; // Process duration in seconds (for PROCESS events)
  /** Publisher of this timeline row — FTS MQTT synthesis vs module device MQTT (B1). */
  eventSource?: 'FTS' | 'MODULE';
  details?: Record<string, unknown>;
}

/**
 * Station task group - groups PICK, PROCESS, DROP at a station
 */
export interface StationTaskGroup {
  stationId: string;
  stationName: string;
  events: TrackTraceEvent[];
  startTime?: string;
  endTime?: string;
  duration?: number; // Duration in seconds
}

/**
 * Order context for Track & Trace
 */
export interface OrderContext {
  orderId: string;
  orderType: 'STORAGE' | 'PRODUCTION' | string;
  purchaseOrderId?: string; // From ERP system (e.g., "ERP-PO-XYZ...")
  supplierId?: string; // Supplier ID from ERP
  orderDate?: string; // Order date from ERP (timestamp) - Bestellung-Datum RAW-Material / Customer-Order
  customerOrderId?: string; // For production orders (e.g., "ERP-CO-XYZ...")
  customerId?: string; // Customer ID from ERP
  startTime?: string; // Production-Start (Auslagerung aus HBW) / Storage-Start
  endTime?: string; // Auslieferungs-Datum (Production-Ende im DPS) / Storage-Ende
  fromLocation?: string;
  toLocation?: string;
  status?: 'ACTIVE' | 'COMPLETED' | 'FAILED' | 'ERROR'; // Order status (FAILED/ERROR = quality-check failure, aborted)
  // Additional date fields for better tracking
  rawMaterialOrderDate?: string; // Bestellung-Datum RAW-Material (wann bestellt im Process-Tab)
  deliveryDate?: string; // Lieferung-Datum (wann angeliefert im DPS)
  storageDate?: string; // Storage-Datum (wann im HBW eingelagert)
  customerOrderDate?: string; // Bestellung-Datum Customer-Order (wann erfolgte Kunden-Bestellung)
  productionStartDate?: string; // Produktions-Start (Auslagerung aus HBW)
  deliveryEndDate?: string; // Auslieferungs-Datum (Production-Ende im DPS)
  plannedStationChain?: string[]; // Planned station sequence (business context)
}

/**
 * Workpiece tracking history
 */
export interface WorkpieceHistory {
  workpieceId: string;
  workpieceType: 'BLUE' | 'WHITE' | 'RED' | string;
  events: TrackTraceEvent[];
  currentLocation?: string;
  currentState?: string;
  orders?: OrderContext[]; // Order context for this workpiece
}

/**
 * FTS State interface (from MQTT messages)
 */
interface FtsState {
  serialNumber: string;
  timestamp: string;
  orderId: string;
  orderUpdateId?: number; // Order update ID from FTS state
  lastNodeId: string;
  driving: boolean;
  actionState: {
    id: string;
    command: string;
    state: string;
    timestamp: string;
  };
  load: Array<{
    loadId: string | null;
    loadType: 'BLUE' | 'WHITE' | 'RED' | null;
    loadPosition: string;
  }>;
  _topic?: string; // Topic from MQTT message
  _moduleSerialId?: string; // Module serial ID extracted from topic
}

/**
 * Module State interface (from MQTT messages)
 */
interface ModuleState {
  serialNumber: string;
  timestamp: string;
  orderId?: string;
  orderUpdateId?: number;
  actionState?: {
    id: string;
    command: string;
    state: string;
    timestamp: string;
    metadata?: Record<string, unknown>;
    result?: unknown;
  } | null;
  loads?: Array<{
    loadType?: 'BLUE' | 'WHITE' | 'RED' | null;
    loadId?: string | null;
    loadPosition?: string | null;
    type?: 'BLUE' | 'WHITE' | 'RED' | null;
  }>;
  actionStates?: Array<{
    id?: string;
    command?: string;
    state?: string;
    timestamp?: string;
    metadata?: Record<string, unknown>;
    result?: unknown;
  }>;
  _topic?: string; // Topic from MQTT message
  _moduleSerialId?: string; // Module serial ID extracted from topic
}

/**
 * Manufacturing station serial numbers
 */
// All modules that can have grouped events (PICK → PROCESS → DROP)
// Includes manufacturing stations (MILL, DRILL, AIQS) and storage/processing stations (HBW, DPS)
const MODULE_STATIONS = ['SVR3QA0022', 'SVR4H76449', 'SVR3QA2098', 'SVR4H76530', 'SVR4H73275'] as const;
const MANUFACTURING_STATIONS = ['SVR4H76449', 'SVR3QA2098', 'SVR4H76530'] as const;
/** Fallback when shopfloor layout is not loaded yet (tests / early boot). */
const MODULE_SERIAL_TYPES: Record<string, string> = {
  SVR3QA0022: 'HBW',
  SVR4H76449: 'DRILL',
  SVR3QA2098: 'MILL',
  SVR4H76530: 'AIQS',
  SVR4H73275: 'DPS',
};

/**
 * Production workflows: Which workpiece types go to which stations
 * Based on production_workflows.json
 */
const PRODUCTION_WORKFLOWS: Record<string, string[]> = {
  BLUE: ['DRILL', 'MILL', 'AIQS'],
  WHITE: ['DRILL', 'AIQS'],
  RED: ['MILL', 'AIQS'], // RED does NOT go to DRILL!
};

/**
 * Process durations in seconds for each station
 */
const PROCESS_DURATIONS: Record<string, number> = {
  'DRILL': 15,
  'MILL': 20,
  'AIQS': 10,
};

/**
 * Service for tracking workpiece history from FTS and module events
 * Aggregates MQTT messages into workpiece tracking history
 */
@Injectable({ providedIn: 'root' })
export class WorkpieceHistoryService implements OnDestroy {
  private readonly stores = new Map<string, BehaviorSubject<Map<string, WorkpieceHistory>>>();
  private subscriptions = new Map<string, Subscription>();
  private readonly messageMonitor = inject(MessageMonitorService);
  private readonly moduleNameService = inject(ModuleNameService);
  private readonly mappingService = inject(ShopfloorMappingService);
  private readonly environmentService = inject(EnvironmentService);
  private readonly ftsRouteService = inject(AgvRouteService);
  private readonly erpOrderDataService = inject(ErpOrderDataService);
  private readonly correlationInfoService = inject(CorrelationInfoService);
  private readonly trackTraceEnvironmentService = inject(TrackTraceEnvironmentService);
  // TURN direction lookup (from order stream) - similar to FTS-Tab
  private readonly turnDirectionByActionId = new Map<string, 'LEFT' | 'RIGHT' | string>();
  private latestEnvironmentSnapshot: TrackTraceEnvironmentSnapshot | null = null;
  private environmentSnapshotSub?: Subscription;
  /**
   * Dedup cache to avoid duplicate events in Track & Trace history.
   * Keyed by environment -> workpieceId -> eventKey -> lastSeenEpochMs.
   */
  private readonly dedupSeen = new Map<string, Map<string, Map<string, number>>>();
  /**
   * DPS intake before NFC id is known (INPUT_RGB). Flushed when RGB_NFC provides workpieceId.
   * Key: `${environmentKey}::${moduleSerialId}`
   */
  private readonly pendingDpsIntake = new Map<
    string,
    Array<{
      timestamp: string;
      actionId: string;
      orderId?: string;
      orderUpdateId?: number;
      command: string;
    }>
  >();
  private static readonly DEDUP_TTL_MS = 30 * 60 * 1000; // 30 min is enough for reconnect/replay duplicates
  private static readonly DEDUP_MAX_KEYS_PER_WORKPIECE = 400;

  ngOnDestroy(): void {
    // Clean up all subscriptions
    this.subscriptions.forEach((sub) => sub.unsubscribe());
    this.subscriptions.clear();
    this.environmentSnapshotSub?.unsubscribe();
    this.environmentSnapshotSub = undefined;
  }

  /**
   * Get workpiece history observable for an environment
   */
  getHistory$(environmentKey: string): Observable<Map<string, WorkpieceHistory>> {
    return this.getStore(environmentKey).asObservable();
  }

  /**
   * Get workpiece history snapshot for an environment
   */
  getSnapshot(environmentKey: string): Map<string, WorkpieceHistory> {
    return this.getStore(environmentKey).value;
  }

  /**
   * Get history for a specific workpiece
   */
  getWorkpieceHistory(environmentKey: string, workpieceId: string): Observable<WorkpieceHistory | undefined> {
    return this.getHistory$(environmentKey).pipe(
      map((historyMap) => historyMap.get(workpieceId)),
      distinctUntilChanged(),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  /**
   * Clear history for an environment
   */
  clear(environmentKey: string): void {
    this.getStore(environmentKey).next(new Map());
    this.subscriptions.get(environmentKey)?.unsubscribe();
    this.subscriptions.delete(environmentKey);
    this.dedupSeen.delete(environmentKey);
    for (const key of [...this.pendingDpsIntake.keys()]) {
      if (key.startsWith(`${environmentKey}::`)) {
        this.pendingDpsIntake.delete(key);
      }
    }
  }

  /**
   * Initialize tracking for an environment
   * Subscribes to relevant MQTT topics and aggregates events
   */
  initialize(environmentKey: string): void {
    if (this.subscriptions.has(environmentKey)) {
      return; // Already initialized
    }
    if (!this.environmentSnapshotSub) {
      this.environmentSnapshotSub = this.trackTraceEnvironmentService.snapshot$.subscribe((snapshot) => {
        this.latestEnvironmentSnapshot = snapshot;
      });
    }

    const historyMap = this.getStore(environmentKey);

    // FTS serials from layout (AGV-1, AGV-2, …); fallback to 5iO4 if layout not loaded
    const ftsSerials = this.mappingService.getAgvOptions().map((o) => o.serial);
    const ftsTopics = ftsSerials.length > 0 ? ftsSerials : ['5iO4'];

    // Subscribe to FTS state messages (all configured AGVs)
    const ftsStateStreams = ftsTopics.map((serial) =>
      this.messageMonitor.getLastMessage(`fts/v1/ff/${serial}/state`).pipe(
        map((msg) => {
          if (!msg?.valid || !msg.payload) return null;
          try {
            const payload = typeof msg.payload === 'string' ? JSON.parse(msg.payload) : msg.payload;
            const moduleSerialId = this.extractModuleSerialFromTopic(msg.topic);
            return {
              ...payload,
              _topic: msg.topic,
              _moduleSerialId: moduleSerialId,
            };
          } catch {
            return null;
          }
        }),
        filter((state): state is NonNullable<typeof state> => state !== null)
      )
    );
    const ftsState$ = merge(...ftsStateStreams);

    // Subscribe to active orders for order context
    // Subscribe to FTS order stream to extract TURN direction information
    const ftsOrder$ = this.messageMonitor.getLastMessage('ccu/order/fts').pipe(
      map((msg) => msg?.payload ?? null),
      filter((order) => order !== null)
    );
    
    ftsOrder$.subscribe((order: any) => {
      if (!order) return;
      // Build actionId -> direction map for TURN actions (same logic as FTS-Tab)
      // Order schema: nodes[].action.id / type / metadata.direction
      if (Array.isArray(order.nodes)) {
        order.nodes.forEach((node: any) => {
          const action = node?.action;
          if (action?.type === 'TURN' && action?.id && action?.metadata?.direction) {
            this.turnDirectionByActionId.set(action.id, action.metadata.direction);
          }
        });
      }
    });
    
    const activeOrders$ = this.messageMonitor.getLastMessage('ccu/order/active').pipe(
      map((msg) => {
        if (!msg?.valid || !msg.payload) return null;
        try {
          return typeof msg.payload === 'string' ? JSON.parse(msg.payload) : msg.payload;
        } catch {
          return null;
        }
      })
    );

    // Subscribe to module state messages for manufacturing stations (DRILL, MILL, AIQS)
    // These modules send PROCESS events via module/v1/ff/<serial>/state
    const moduleStateStreams = MODULE_STATIONS.map((serial) => {
      // Try both patterns: module/v1/ff/<serial>/state and module/v1/ff/NodeRed/<serial>/state
      const topic1 = `module/v1/ff/${serial}/state`;
      const topic2 = `module/v1/ff/NodeRed/${serial}/state`;
      
      const stream1$ = this.messageMonitor.getLastMessage(topic1).pipe(
        map((msg) => {
          if (!msg?.valid || !msg.payload) return null;
          try {
            const payload = typeof msg.payload === 'string' ? JSON.parse(msg.payload) : msg.payload;
            const moduleSerialId = this.extractModuleSerialFromTopic(msg.topic);
            return {
              ...payload,
              _topic: msg.topic,
              _moduleSerialId: moduleSerialId || serial,
            };
          } catch {
            return null;
          }
        }),
        filter((state): state is ModuleState => state !== null && state.actionState !== null && state.actionState !== undefined)
      );
      
      const stream2$ = this.messageMonitor.getLastMessage(topic2).pipe(
        map((msg) => {
          if (!msg?.valid || !msg.payload) return null;
          try {
            const payload = typeof msg.payload === 'string' ? JSON.parse(msg.payload) : msg.payload;
            const moduleSerialId = this.extractModuleSerialFromTopic(msg.topic);
            return {
              ...payload,
              _topic: msg.topic,
              _moduleSerialId: moduleSerialId || serial,
            };
          } catch {
            return null;
          }
        }),
        filter((state): state is ModuleState => state !== null && state.actionState !== null && state.actionState !== undefined)
      );
      
      return merge(stream1$, stream2$);
    });
    
    const moduleState$ = merge(...moduleStateStreams);

    // Subscribe to completed orders for order status
    const completedOrders$ = this.messageMonitor.getLastMessage('ccu/order/completed').pipe(
      map((msg) => {
        if (!msg?.valid || !msg.payload) return null;
        try {
          const payload = typeof msg.payload === 'string' ? JSON.parse(msg.payload) : msg.payload;
          return Array.isArray(payload) ? payload : [payload];
        } catch {
          return null;
        }
      }),
      map((orders) => {
        if (!orders) return {};
        const completedMap: Record<string, any> = {};
        orders.forEach((order: any) => {
          if (order && order.orderId) {
            completedMap[order.orderId] = order;
          }
        });
        return completedMap;
      })
    );
    
    // Combine active and completed orders
    const allOrders$ = combineLatest([
      activeOrders$.pipe(startWith(null)),
      completedOrders$.pipe(startWith({}))
    ]).pipe(
      map(([active, completed]) => ({
        active: active || {},
        completed: completed || {},
      }))
    );
    
    // Correlation map: when it changes, refresh order context for ALL workpieces in Track & Trace
    const correlationMap$ = this.correlationInfoService.map$.pipe(
      startWith(this.correlationInfoService.mapSnapshot)
    );

    // Combine FTS state and orders to update history
    const ftsSubscription = combineLatest([
      ftsState$.pipe(startWith(null)),
      allOrders$.pipe(startWith({ active: {}, completed: {} }))
    ]).subscribe(([ftsState, orders]) => {
      if (ftsState) {
        try {
          this.updateWorkpieceHistory(environmentKey, ftsState as FtsState, orders);
        } catch (error) {
          console.error('[WorkpieceHistoryService] Error updating history from FTS:', error);
        }
      }
    });

    // Subscribe to module state messages to process PICK/PROCESS/DROP events
    const moduleSubscription = combineLatest([
      moduleState$.pipe(startWith(null)),
      allOrders$.pipe(startWith({ active: {}, completed: {} }))
    ]).subscribe(([moduleState, orders]) => {
      if (moduleState) {
        try {
          this.updateWorkpieceHistoryFromModule(environmentKey, moduleState as ModuleState, orders);
        } catch (error) {
          console.error('[WorkpieceHistoryService] Error updating history from module:', error);
        }
      }
    });

    // When correlation info changes, refresh order context for ALL workpieces (Order-Tab and Track & Trace stay in sync)
    const correlationSubscription = combineLatest([
      correlationMap$,
      allOrders$.pipe(startWith({ active: {}, completed: {} }))
    ]).subscribe(([, orders]) => {
      try {
        this.refreshAllOrderContexts(environmentKey, orders);
      } catch (error) {
        console.error('[WorkpieceHistoryService] Error refreshing order contexts from correlation:', error);
      }
    });

    // Combine all subscriptions
    const combinedSubscription = new Subscription();
    combinedSubscription.add(ftsSubscription);
    combinedSubscription.add(moduleSubscription);
    combinedSubscription.add(correlationSubscription);

    this.subscriptions.set(environmentKey, combinedSubscription);
  }

  /**
   * Extract module serial ID from MQTT topic
   * Patterns: fts/v1/ff/<serial>/state, module/v1/ff/<serial>/state, module/v1/ff/NodeRed/<serial>/state
   */
  private extractModuleSerialFromTopic(topic: string): string | null {
    const parts = topic.split('/');
    if (parts.length < 4) {
      return null;
    }

    // FTS topics: fts/v1/ff/<serial>/state
    if (parts[0] === 'fts' && parts[1] === 'v1' && parts[2] === 'ff' && parts.length >= 4) {
      return parts[3];
    }

    // Module topics: module/v1/ff/<serial>/state or module/v1/ff/NodeRed/<serial>/state
    if (parts[0] === 'module' && parts[1] === 'v1' && parts[2] === 'ff') {
      if (parts.length >= 5 && parts[3] === 'NodeRed') {
        return parts[4];
      }
      if (parts.length >= 4) {
        return parts[3];
      }
    }

    return null;
  }

  /**
   * Get module name from serial ID or location
   */
  private getModuleNameFromSerial(serialNumber: string | null | undefined): string | null {
    if (!serialNumber) return null;
    
    // Check if it's an intersection using AgvRouteService mapping
    const resolved = this.ftsRouteService.resolveNodeRef(serialNumber);
    if (resolved && resolved.startsWith('intersection:')) {
      return null; // Intersections are handled separately
    }

    // Try to resolve via ModuleNameService (uses layout: 5iO4→FTS, leJ4→FTS, etc.)
    const moduleType = this.moduleNameService.getModuleTypeFromSerial(serialNumber);
    if (moduleType) {
      return moduleType;
    }

    // Fallback: FTS from layout getAgvOptions, or known serials if layout not yet loaded
    const agvSerials = this.mappingService.getAgvOptions().map((o) => o.serial);
    const knownFtsSerials = agvSerials.length > 0 ? agvSerials : ['5iO4'];
    if (knownFtsSerials.includes(serialNumber) || serialNumber.toLowerCase().includes('fts')) {
      return 'FTS';
    }

    return null;
  }

  /**
   * Check if a workpiece type can be processed at a specific station
   * Based on production workflows: RED does not go to DRILL, etc.
   */
  private canWorkpieceBeProcessedAtStation(
    workpieceType: string | null | undefined,
    stationName: string | null | undefined
  ): boolean {
    if (!workpieceType || !stationName) {
      return true; // Allow if we can't determine (fallback)
    }

    const workflow = PRODUCTION_WORKFLOWS[workpieceType.toUpperCase()];
    if (!workflow) {
      return true; // Unknown workpiece type - allow (fallback)
    }

    // Check if station is in the workflow for this workpiece type
    return workflow.includes(stationName.toUpperCase());
  }

  /**
   * Refresh order context for all workpieces when correlation info changes.
   * Ensures Track & Trace shows updated ERP data (customerOrderId, customerId, etc.) in sync with Order-Tab.
   */
  private refreshAllOrderContexts(
    environmentKey: string,
    orders: { active: Record<string, any>; completed: Record<string, any> } | unknown
  ): void {
    const historyMap = new Map(this.getStore(environmentKey).value);
    let hasChanges = false;

    for (const [, history] of historyMap) {
      const newOrders = this.rebuildOrderContexts(history, orders);
      if (JSON.stringify(history.orders ?? []) !== JSON.stringify(newOrders)) {
        history.orders = newOrders;
        hasChanges = true;
      }
    }

    if (hasChanges) {
      this.getStore(environmentKey).next(historyMap);
    }
  }

  /**
   * Update workpiece history from FTS state
   */
  private updateWorkpieceHistory(
    environmentKey: string,
    state: FtsState,
    orders: { active: Record<string, any>; completed: Record<string, any> } | unknown
  ): void {
    const historyMap = new Map(this.getStore(environmentKey).value);

    // Extract module serial ID from topic
    const moduleSerialId = state._moduleSerialId || state.serialNumber || '5iO4';
    // For FTS: use layout label (AGV-1, AGV-2) instead of generic 'FTS' for event display
    const moduleType = this.getModuleNameFromSerial(moduleSerialId);
    const moduleName =
      (moduleType === 'FTS' ? this.mappingService.getAgvLabel(moduleSerialId) : null) || moduleType || 'FTS';

    // Debug: Log FTS state
    if (state.load && state.load.length > 0) {
      console.log('[WorkpieceHistoryService] FTS state:', {
        timestamp: state.timestamp,
        lastNodeId: state.lastNodeId,
        loadCount: state.load.length,
        loadItems: state.load.map(l => ({ loadId: l.loadId, loadType: l.loadType })),
      });
    }

    // Debug: Log load array processing
    console.log('[WorkpieceHistoryService] Processing load array:', {
      loadArrayLength: state.load?.length || 0,
      loadItems: state.load?.map(l => ({ 
        loadId: l.loadId, 
        loadType: l.loadType,
        loadPosition: l.loadPosition,
        hasLoadId: !!l.loadId,
        hasLoadType: !!l.loadType
      })) || [],
    });

    state.load?.forEach((loadItem) => {
      if (loadItem.loadId && loadItem.loadType) {
        // Normalize orders parameter
        const normalizedOrders = orders && typeof orders === 'object' && 'active' in orders
          ? orders as { active: Record<string, any>; completed: Record<string, any> }
          : { active: orders as any || {}, completed: {} };
        
        const existingHistory = historyMap.get(loadItem.loadId) || {
          workpieceId: loadItem.loadId,
          workpieceType: loadItem.loadType,
          events: [],
          currentLocation: state.lastNodeId,
          currentState: 'IN_TRANSPORT',
          orders: this.generateOrderContext(loadItem.loadType, normalizedOrders, state.orderId ? [state.orderId] : [], []),
        };

        // Determine order type based on location
        const orderType = this.determineOrderType(state.lastNodeId, existingHistory.events);

        // Get station info
        const stationName = this.getStationName(state.lastNodeId);
        const isManufacturingStation = MANUFACTURING_STATIONS.includes(
          state.lastNodeId as typeof MANUFACTURING_STATIONS[number]
        );

        // Emit on location change, or same-node DOCK after PASS/TURN (Ist arrival).
        // B3: FTS only records transport (DOCK/PASS/TURN); station process stays MODULE SoT.
        const eventType = this.mapActionCommandToEventType(state.actionState.command);
        const lastEvent = existingHistory.events[existingHistory.events.length - 1];
        const locationChanged = !lastEvent || lastEvent.location !== state.lastNodeId;
        const lastFtsAtLocation = [...existingHistory.events]
          .reverse()
          .find((e) => e.eventSource === 'FTS' && e.location === state.lastNodeId);
        const commandChangedAtSameNode =
          !locationChanged &&
          !!lastFtsAtLocation &&
          (lastFtsAtLocation.eventType || '').toUpperCase() !== eventType;
        const shouldEmitTransport =
          locationChanged || (commandChangedAtSameNode && eventType === 'DOCK');

        if (shouldEmitTransport) {
          console.log('[WorkpieceHistoryService] Transport event for workpiece:', {
            workpieceId: loadItem.loadId,
            workpieceType: loadItem.loadType,
            oldLocation: lastEvent?.location,
            newLocation: state.lastNodeId,
            stationName,
            orderType,
            eventType,
            locationChanged,
            commandChangedAtSameNode,
            isManufacturingStation,
          });
          const baseEvent: Partial<TrackTraceEvent> = {
            timestamp: state.timestamp,
            workpieceId: loadItem.loadId,
            workpieceType: loadItem.loadType,
            location: state.lastNodeId,
            moduleId: moduleSerialId,
            moduleName: moduleName,
            orderId: state.orderId,
            orderUpdateId: state.orderUpdateId,
            orderType: orderType,
            stationId: stationName || undefined,
            stationName: stationName ? this.getStationDisplayName(stationName) : undefined,
            eventSource: 'FTS',
          };

          const subOrderId = `${state.orderId}-${existingHistory.events.length + 1}`;
          const actionId = state.actionState.id;

          let turnDirection: string | undefined;
          if (eventType === 'TURN') {
            const actionStateMeta = (state.actionState as { metadata?: { direction?: string } })?.metadata;
            if (actionStateMeta?.direction) {
              turnDirection = actionStateMeta.direction;
            } else {
              turnDirection = this.turnDirectionByActionId.get(state.actionState.id);
            }
          }

          const nodeRef = this.ftsRouteService.resolveNodeRef(state.lastNodeId);
          const intersectionNumber = nodeRef?.startsWith('intersection:')
            ? nodeRef.replace('intersection:', '')
            : null;

          const agvLoads = (state.load ?? [])
            .filter((l) => !!l.loadId && !!l.loadType)
            .map((l) => ({
              loadId: l.loadId as string,
              loadType: l.loadType as string,
              loadPosition: l.loadPosition,
            }));

          const details: Record<string, unknown> = {
            actionState: state.actionState.state,
            loadPosition: loadItem.loadPosition,
            loadType: loadItem.loadType || undefined,
            direction: turnDirection,
            intersectionNumber,
            agvLoads,
          };

          // Ist-only: manufacturing stop not in this workpiece's planned workflow (e.g. RED @ DRILL),
          // or co-passenger on another color's order (e.g. BLUE @ MILL while RED order is active).
          const mfgStation = (stationName || '').toUpperCase();
          const orderWorkpieceType = this.resolveOrderWorkpieceType(normalizedOrders, state.orderId);
          const isForeignOrder =
            !!orderWorkpieceType &&
            !!loadItem.loadType &&
            orderWorkpieceType !== String(loadItem.loadType).toUpperCase();
          if (['DRILL', 'MILL', 'AIQS'].includes(mfgStation)) {
            const inPlannedWorkflow = this.canWorkpieceBeProcessedAtStation(
              loadItem.loadType,
              stationName
            );
            details['visitKind'] = inPlannedWorkflow && !isForeignOrder ? 'PLANNED' : 'IST_ONLY';
            details['coPassenger'] = !inPlannedWorkflow || isForeignOrder;
          } else if (isForeignOrder) {
            details['visitKind'] = 'IST_ONLY';
            details['coPassenger'] = true;
          }

          const transportEvent: TrackTraceEvent = {
            ...baseEvent,
            eventType,
            timestamp: state.timestamp,
            subOrderId,
            actionId,
            details,
          } as TrackTraceEvent;
          this.attachEnvironmentSnapshotIfRelevant(transportEvent);
          this.tryAppendEvent(environmentKey, existingHistory, transportEvent);

          console.log('[WorkpieceHistoryService] Generated event for workpiece:', {
            workpieceId: loadItem.loadId,
            eventType,
            location: state.lastNodeId,
            visitKind: details['visitKind'],
            eventsCount: existingHistory.events.length,
          });
        }

        existingHistory.currentLocation = state.lastNodeId;
        existingHistory.currentState = state.driving ? 'IN_TRANSPORT' : 'STATIONARY';

        // A1: rebuild STORAGE + PRODUCTION contexts from all distinct orderIds on this workpiece
        existingHistory.orders = this.rebuildOrderContexts(
          existingHistory,
          normalizedOrders,
          state.orderId
        );

        historyMap.set(loadItem.loadId, existingHistory);
      }
    });

    this.getStore(environmentKey).next(historyMap);
  }

  /**
   * Update workpiece history from module state messages
   * Processes PICK, PROCESS, DROP events from manufacturing stations (DRILL, MILL, AIQS)
   */
  private updateWorkpieceHistoryFromModule(
    environmentKey: string,
    moduleState: ModuleState,
    orders: { active: Record<string, any>; completed: Record<string, any> } | unknown
  ): void {

    const historyMap = new Map(this.getStore(environmentKey).value);

    // Extract module serial ID
    const moduleSerialId = moduleState._moduleSerialId || moduleState.serialNumber;
    const moduleName = this.getModuleNameFromSerial(moduleSerialId);
    const stationName = this.getStationName(moduleSerialId);

    const resolvedActionState = this.resolveModuleActionState(moduleState);
    if (!resolvedActionState) {
      return;
    }

    const command = resolvedActionState.command.toUpperCase();
    const actionStateValue = resolvedActionState.state.toUpperCase();
    // Only commit finished actions (RUNNING would duplicate PROCESS/PICK/DROP)
    if (actionStateValue !== 'FINISHED') {
      return;
    }
    if (!this.isTrackableModuleCommand(command)) {
      return;
    }

    // Antwort A refined: keep real MQTT names (DRILL/MILL/CHECK_QUALITY/INPUT_RGB/RGB_NFC)
    const mappedCommand = this.mapModuleCommandToEventType(command);
    const actionResult = resolvedActionState.result;

    const workpieceIdFromModule = this.resolveModuleWorkpieceId(
      moduleState,
      { ...resolvedActionState, command },
      actionResult
    );
    const workpieceType = this.resolveModuleWorkpieceType(moduleState, resolvedActionState);

    // Always buffer Color (INPUT_RGB) until NFC — never append with a late wall-clock time via PICK/DROP flush.
    if (command === 'INPUT_RGB') {
      const bufKey = `${environmentKey}::${moduleSerialId}`;
      const list = this.pendingDpsIntake.get(bufKey) ?? [];
      // Keep a single pending Color sample (first FINISHED wins chronologically)
      if (list.length === 0) {
        list.push({
          timestamp:
            resolvedActionState.timestamp ||
            moduleState.timestamp ||
            utcIsoTimestampMs(),
          actionId: resolvedActionState.id,
          orderId: moduleState.orderId,
          orderUpdateId: moduleState.orderUpdateId,
          command,
        });
        this.pendingDpsIntake.set(bufKey, list);
      }
      return;
    }

    // DROP events at manufacturing stations have loads=[] after release —
    // allow matching via orderId if present, even without workpiece identity in payload.
    const canMatchByOrderId = !!(moduleState.orderId && moduleState.orderId !== '0');
    if (!workpieceType && !workpieceIdFromModule && !canMatchByOrderId) {
      return; // No workpiece identity and no orderId to match against
    }

    // Prefer explicit NFC from payload; never let orderId fallback override it.
    let matchingWorkpieceId: string | null = workpieceIdFromModule;
    let matchingHistory: WorkpieceHistory | null = matchingWorkpieceId
      ? historyMap.get(matchingWorkpieceId) ?? null
      : null;

    if (workpieceIdFromModule && !matchingHistory) {
      matchingHistory = {
        workpieceId: workpieceIdFromModule,
        workpieceType: workpieceType || 'UNKNOWN',
        events: [],
        orders: [],
      };
      historyMap.set(workpieceIdFromModule, matchingHistory);
      matchingWorkpieceId = workpieceIdFromModule;
    }

    if (!matchingHistory && workpieceType) {
      for (const [workpieceId, history] of historyMap.entries()) {
        if (history.workpieceType !== workpieceType) {
          continue;
        }
        const hasMatchingOrder = history.events.some(
          (event) =>
            event.orderId === moduleState.orderId &&
            (moduleState.orderUpdateId === undefined || event.orderUpdateId === moduleState.orderUpdateId)
        );
        if (hasMatchingOrder) {
          matchingWorkpieceId = workpieceId;
          matchingHistory = history;
          break;
        }
      }
    }

    // Empty loads (DROP/process): bind by orderId, but prefer the workpiece that
    // actually docked at this module (co-passengers share one FTS orderId).
    if (!matchingHistory && canMatchByOrderId) {
      const normalizedOrders =
        orders && typeof orders === 'object' && 'active' in orders
          ? (orders as { active: Record<string, unknown>; completed: Record<string, unknown> })
          : { active: {}, completed: {} };
      const orderWorkpieceType =
        workpieceType ||
        this.resolveOrderWorkpieceType(normalizedOrders, moduleState.orderId as string);
      const docked = this.findWorkpieceDockedAtModule(
        historyMap,
        moduleState.orderId as string,
        moduleSerialId,
        orderWorkpieceType
      );
      if (docked) {
        matchingWorkpieceId = docked.workpieceId;
        matchingHistory = docked;
      } else {
        for (const [workpieceId, history] of historyMap.entries()) {
          if (orderWorkpieceType && history.workpieceType !== orderWorkpieceType) {
            continue;
          }
          const hasOrderMatch = history.events.some(
            (event) => event.orderId === moduleState.orderId && event.orderId && event.orderId !== '0'
          );
          if (hasOrderMatch) {
            matchingWorkpieceId = workpieceId;
            matchingHistory = history;
            break;
          }
        }
      }
    }

    // RGB_NFC: create history early so Color/NFC appear before first FTS DOCK
    if ((!matchingWorkpieceId || !matchingHistory) && command === 'RGB_NFC' && workpieceIdFromModule) {
      matchingWorkpieceId = workpieceIdFromModule;
      matchingHistory = {
        workpieceId: matchingWorkpieceId,
        workpieceType: workpieceType || 'UNKNOWN',
        events: [],
        orders: [],
      };
      historyMap.set(matchingWorkpieceId, matchingHistory);
    }

    if (!matchingWorkpieceId || !matchingHistory) {
      console.warn('[WorkpieceHistoryService] No matching workpiece found for module state:', {
        moduleSerialId,
        moduleName,
        orderId: moduleState.orderId,
        orderUpdateId: moduleState.orderUpdateId,
        workpieceType,
        command,
      });
      return;
    }

    if (workpieceType && matchingHistory.workpieceType === 'UNKNOWN') {
      matchingHistory.workpieceType = workpieceType;
    }

    // Flush Color only when NFC arrives (keeps Color timestamp before NFC / AGV)
    let intakeOrderIdFromBuffer: string | undefined;
    if (command === 'RGB_NFC') {
      // Capture storage order UUID before flush clears the buffer (RGB_NFC often has orderId "0")
      const pendingBeforeFlush = this.pendingDpsIntake.get(`${environmentKey}::${moduleSerialId}`);
      intakeOrderIdFromBuffer = pendingBeforeFlush?.[0]?.orderId;
      this.flushPendingDpsIntake(
        environmentKey,
        moduleSerialId,
        matchingHistory,
        matchingWorkpieceId,
        stationName
      );
      // MQTT often publishes RGB_NFC twice (id only, then + type) — keep one NFC row
      const alreadyHasNfc = matchingHistory.events.some((e) => e.eventType === 'RGB_NFC');
      if (alreadyHasNfc) {
        matchingHistory.events.sort((a, b) => {
          const timeA = new Date(a.timestamp).getTime();
          const timeB = new Date(b.timestamp).getTime();
          if (timeA !== timeB) return timeA - timeB;
          return (a.actionId || '').localeCompare(b.actionId || '');
        });
        historyMap.set(matchingWorkpieceId, matchingHistory);
        this.getStore(environmentKey).next(historyMap);
        return;
      }
    }

    // Generate event
    // IMPORTANT: For module events, use stationName (DRILL, AIQS, etc.) as moduleName
    // This ensures that events in Level 3 show "DRILL PICK" instead of "FTS PICK"
    const eventModuleName = stationName || moduleName || 'UNKNOWN';
    let eventOrderType = this.resolveModuleOrderType(matchingHistory, moduleState, moduleSerialId);
    // DPS intake is always STORAGE (MQTT often sends orderId "0" for RGB_NFC)
    if (command === 'RGB_NFC' || command === 'INPUT_RGB') {
      eventOrderType = 'STORAGE';
    }
    const loadPosition =
      mappedCommand === 'PICK' || mappedCommand === 'DROP'
        ? this.resolveLoadPosition(moduleState, matchingWorkpieceId)
        : null;

    // Prefer real storage order UUID from buffered Color over MQTT placeholder "0"
    const intakeOrderId =
      command === 'RGB_NFC' && (!moduleState.orderId || moduleState.orderId === '0')
        ? intakeOrderIdFromBuffer ||
          matchingHistory.events.find((e) => e.eventType === 'INPUT_RGB' && e.orderId && e.orderId !== '0')
            ?.orderId
        : undefined;
    const resolvedOrderId = intakeOrderId || moduleState.orderId;

    const baseEvent: Partial<TrackTraceEvent> = {
      timestamp: moduleState.timestamp || resolvedActionState.timestamp || utcIsoTimestampMs(),
      workpieceId: matchingWorkpieceId,
      workpieceType: matchingHistory.workpieceType,
      location: moduleSerialId,
      moduleId: moduleSerialId,
      moduleName: eventModuleName,
      orderId: resolvedOrderId,
      orderUpdateId: moduleState.orderUpdateId,
      orderType: eventOrderType,
      stationId: stationName || undefined,
      stationName: stationName ? this.getStationDisplayName(stationName) : undefined,
      eventType: mappedCommand,
      actionId: resolvedActionState.id,
      eventSource: 'MODULE',
      processDuration:
        (mappedCommand === 'PROCESS' ||
          mappedCommand === 'DRILL' ||
          mappedCommand === 'MILL' ||
          mappedCommand === 'CHECK_QUALITY') &&
        stationName
          ? PROCESS_DURATIONS[stationName]
          : undefined,
      details: {
        actionState: actionStateValue,
        command: command,
        originalCommand: command,
        ...(loadPosition ? { loadPosition } : {}),
        ...(typeof actionResult === 'string' ? { result: actionResult } : {}),
      },
    };

    // Generate sub-order ID - find the most recent FTS event that brought the workpiece to this module
    // This ensures Module-Events use the same Sub-Order-ID as the FTS DOCK event
    const ftsDockEvent = matchingHistory.events
      .filter((e) =>
        e.orderId === resolvedOrderId &&
        e.location === moduleSerialId &&
        e.eventType === 'DOCK' &&
        this.getModuleNameFromSerial(e.moduleId ?? '') === 'FTS'
      )
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0];
    
    // If we found a DOCK event, use its subOrderId
    // Otherwise, try to find any event with matching orderId and orderUpdateId
    let subOrderId: string;
    if (command === 'RGB_NFC') {
      const colorEvent = matchingHistory.events.find((e) => e.eventType === 'INPUT_RGB' && e.subOrderId);
      subOrderId =
        colorEvent?.subOrderId ||
        `${resolvedOrderId || moduleState.orderId || 'dps-intake'}-intake`;
    } else if (ftsDockEvent?.subOrderId) {
      subOrderId = ftsDockEvent.subOrderId;
    } else {
      // Fallback: find the most recent event with matching orderId and orderUpdateId
      const matchingEvent = matchingHistory.events
        .filter((e) => 
          e.orderId === resolvedOrderId &&
          (moduleState.orderUpdateId === undefined || e.orderUpdateId === moduleState.orderUpdateId)
        )
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0];
      
      subOrderId = matchingEvent?.subOrderId || `${resolvedOrderId || moduleState.orderId}-${matchingHistory.events.length + 1}`;
    }
    
    baseEvent.subOrderId = subOrderId;
    this.attachEnvironmentSnapshotIfRelevant(baseEvent as TrackTraceEvent);

    // Add event to history
    this.tryAppendEvent(environmentKey, matchingHistory, baseEvent as TrackTraceEvent);

    // Sort events by timestamp, then subOrderId, then actionId
    matchingHistory.events.sort((a, b) => {
      const timeA = new Date(a.timestamp).getTime();
      const timeB = new Date(b.timestamp).getTime();
      if (timeA !== timeB) return timeA - timeB;
      
      if (a.subOrderId && b.subOrderId) {
        const subOrderCompare = a.subOrderId.localeCompare(b.subOrderId);
        if (subOrderCompare !== 0) return subOrderCompare;
      }
      
      if (a.actionId && b.actionId) {
        return a.actionId.localeCompare(b.actionId);
      }
      
      return 0;
    });

    // A1: keep Production order context when module events carry a new orderId
    const normalizedOrders = orders && typeof orders === 'object' && 'active' in orders
      ? (orders as { active: Record<string, any>; completed: Record<string, any> })
      : { active: (orders as any) || {}, completed: {} };
    matchingHistory.orders = this.rebuildOrderContexts(
      matchingHistory,
      normalizedOrders,
      moduleState.orderId
    );

    historyMap.set(matchingWorkpieceId, matchingHistory);
    this.getStore(environmentKey).next(historyMap);
  }

  private resolveModuleActionState(
    moduleState: ModuleState
  ): {
    id: string;
    command: string;
    state: string;
    timestamp: string;
    metadata?: Record<string, unknown>;
    result?: unknown;
  } | null {
    const primary = moduleState.actionState as
      | {
          id?: string;
          command?: string;
          state?: string;
          timestamp?: string;
          metadata?: Record<string, unknown>;
          result?: unknown;
        }
      | null
      | undefined;
    if (
      primary &&
      typeof primary.id === 'string' &&
      typeof primary.command === 'string' &&
      typeof primary.state === 'string' &&
      this.isTrackableModuleCommand(primary.command)
    ) {
      return {
        id: primary.id,
        command: primary.command,
        state: primary.state,
        timestamp: primary.timestamp || moduleState.timestamp,
        metadata: primary.metadata,
        result: primary.result,
      };
    }

    const fallbackStates = Array.isArray(moduleState.actionStates) ? moduleState.actionStates : [];
    const fallback = [...fallbackStates].reverse().find(
      (state) =>
        typeof state?.id === 'string' &&
        typeof state?.command === 'string' &&
        typeof state?.state === 'string' &&
        this.isTrackableModuleCommand(state.command)
    );
    if (!fallback || typeof fallback.id !== 'string' || typeof fallback.command !== 'string' || typeof fallback.state !== 'string') {
      return null;
    }
    return {
      id: fallback.id,
      command: fallback.command,
      state: fallback.state,
      timestamp: (fallback as { timestamp?: string }).timestamp || moduleState.timestamp,
      metadata: fallback.metadata as Record<string, unknown> | undefined,
      result: (fallback as { result?: unknown }).result,
    };
  }

  private isTrackableModuleCommand(command: string): boolean {
    const normalized = command.toUpperCase();
    return [
      'PICK',
      'DROP',
      'PROCESS',
      'CHECK_QUALITY',
      'DRILL',
      'MILL',
      'INPUT_RGB',
      'RGB_NFC',
    ].includes(normalized);
  }

  /**
   * When module loads[] is empty, pick the workpiece that most recently FTS-docked
   * at this module for the given order — avoids attributing co-passenger orderIds to
   * the wrong color (e.g. BLUE stealing RED MILL while co-riding).
   *
   * Prefer: (1) order workpiece type filter, (2) non-coPassenger DOCK, (3) planned station,
   * (4) latest DOCK timestamp.
   */
  private findWorkpieceDockedAtModule(
    historyMap: Map<string, WorkpieceHistory>,
    orderId: string,
    moduleSerialId: string,
    workpieceType: string | null
  ): WorkpieceHistory | null {
    const stationName = this.getStationName(moduleSerialId);
    type Candidate = {
      history: WorkpieceHistory;
      ts: number;
      planned: boolean;
      coPassenger: boolean;
    };
    const candidates: Candidate[] = [];

    for (const history of historyMap.values()) {
      if (workpieceType && history.workpieceType.toUpperCase() !== workpieceType.toUpperCase()) {
        continue;
      }
      for (const event of history.events) {
        if (event.eventSource !== 'FTS' || (event.eventType || '').toUpperCase() !== 'DOCK') {
          continue;
        }
        if (event.location !== moduleSerialId) {
          continue;
        }
        if (event.orderId !== orderId) {
          continue;
        }
        const ts = new Date(event.timestamp).getTime();
        const planned = this.canWorkpieceBeProcessedAtStation(history.workpieceType, stationName);
        const coPassenger = event.details?.['coPassenger'] === true;
        candidates.push({ history, ts, planned, coPassenger });
      }
    }

    if (candidates.length === 0) {
      return null;
    }

    candidates.sort((a, b) => {
      if (a.coPassenger !== b.coPassenger) {
        return a.coPassenger ? 1 : -1;
      }
      if (a.planned !== b.planned) {
        return a.planned ? -1 : 1;
      }
      return b.ts - a.ts;
    });

    return candidates[0]?.history ?? null;
  }

  /**
   * CCU order color (`type`) for attribution — primary signal for empty-load module events.
   */
  private resolveOrderWorkpieceType(
    orders: { active: Record<string, unknown>; completed: Record<string, unknown> },
    orderId: string | undefined
  ): 'BLUE' | 'WHITE' | 'RED' | null {
    if (!orderId || orderId === '0') {
      return null;
    }
    const raw = orders.active[orderId] ?? orders.completed[orderId];
    if (!raw || typeof raw !== 'object') {
      return null;
    }
    const type = String((raw as { type?: unknown }).type ?? '').toUpperCase();
    if (type === 'BLUE' || type === 'WHITE' || type === 'RED') {
      return type;
    }
    return null;
  }

  /**
   * Keep MQTT command names for the timeline (DRILL/MILL/CHECK_QUALITY, not generic PROCESS).
   */
  private mapModuleCommandToEventType(command: string): string {
    return command.toUpperCase();
  }

  private resolveLoadPosition(moduleState: ModuleState, workpieceId: string): string | null {
    const loads = moduleState.loads as
      | Array<{ loadId?: string; loadType?: string; loadPosition?: string }>
      | undefined;
    if (!Array.isArray(loads)) {
      return null;
    }
    const byId = loads.find((load) => load?.loadId === workpieceId && !!load.loadPosition);
    if (byId?.loadPosition) {
      return String(byId.loadPosition);
    }
    const byType = loads.find((load) => !!load?.loadType && !!load.loadPosition && !!load.loadId);
    return byType?.loadPosition ? String(byType.loadPosition) : null;
  }

  private resolveModuleWorkpieceId(
    moduleState: ModuleState,
    resolvedActionState: { metadata?: Record<string, unknown>; command?: string },
    result: unknown
  ): string | null {
    if (typeof result === 'string' && result.length >= 6 && resolvedActionState.command?.toUpperCase() === 'RGB_NFC') {
      return result;
    }
    const metaWp = resolvedActionState.metadata?.['workpiece'];
    if (metaWp && typeof metaWp === 'object') {
      const id = (metaWp as Record<string, unknown>)['workpieceId'];
      if (typeof id === 'string' && id.length >= 6) {
        return id;
      }
    }
    const loads = moduleState.loads as Array<{ loadId?: string }> | undefined;
    const fromLoads = loads?.find((load) => !!load?.loadId)?.loadId;
    return typeof fromLoads === 'string' && fromLoads.length >= 6 ? fromLoads : null;
  }

  private resolveModuleWorkpieceType(
    moduleState: ModuleState,
    resolvedActionState: { metadata?: Record<string, unknown> }
  ): 'BLUE' | 'WHITE' | 'RED' | null {
    const loadType = moduleState.loads?.find((load) => !!load?.loadType)?.loadType;
    if (loadType === 'BLUE' || loadType === 'WHITE' || loadType === 'RED') {
      return loadType;
    }

    // DPS RGB_NFC: metadata.type = WHITE (flat, not nested under workpiece)
    const flatType = resolvedActionState.metadata?.['type'];
    if (flatType === 'BLUE' || flatType === 'WHITE' || flatType === 'RED') {
      return flatType;
    }

    const loadsAlt = moduleState.loads as Array<{ type?: string; loadType?: string }> | undefined;
    const alt = loadsAlt?.find((l) => l?.type === 'BLUE' || l?.type === 'WHITE' || l?.type === 'RED')?.type;
    if (alt === 'BLUE' || alt === 'WHITE' || alt === 'RED') {
      return alt;
    }

    const fromActionState = this.extractWorkpieceTypeFromMetadata(resolvedActionState.metadata);
    if (fromActionState) {
      return fromActionState;
    }

    for (const state of moduleState.actionStates ?? []) {
      const fromActionStates = this.extractWorkpieceTypeFromMetadata(
        state?.metadata as Record<string, unknown> | undefined
      );
      if (fromActionStates) {
        return fromActionStates;
      }
    }
    return null;
  }

  private extractWorkpieceTypeFromMetadata(
    metadata: Record<string, unknown> | undefined
  ): 'BLUE' | 'WHITE' | 'RED' | null {
    const workpiece = metadata?.['workpiece'];
    if (!workpiece || typeof workpiece !== 'object') {
      return null;
    }
    const type = (workpiece as Record<string, unknown>)['type'];
    if (type === 'BLUE' || type === 'WHITE' || type === 'RED') {
      return type;
    }
    return null;
  }

  private resolveModuleOrderType(
    history: WorkpieceHistory,
    moduleState: ModuleState,
    moduleSerialId: string
  ): 'STORAGE' | 'PRODUCTION' | string {
    const fromOrderContext = history.orders?.find((order) => order.orderId === moduleState.orderId)?.orderType;
    if (fromOrderContext) {
      return fromOrderContext;
    }
    return this.determineOrderType(moduleSerialId, history.events);
  }

  /** Flush buffered DPS INPUT_RGB (Color) once workpiece identity is known. */
  private flushPendingDpsIntake(
    environmentKey: string,
    moduleSerialId: string,
    history: WorkpieceHistory,
    workpieceId: string,
    stationName: string | null
  ): void {
    const bufKey = `${environmentKey}::${moduleSerialId}`;
    const pending = this.pendingDpsIntake.get(bufKey);
    if (!pending?.length) {
      return;
    }
    this.pendingDpsIntake.delete(bufKey);
    const intakeSubOrderId = `${pending[0]?.orderId || 'dps-intake'}-intake`;
    for (const item of pending) {
      const colorEvent: TrackTraceEvent = {
        timestamp: item.timestamp,
        eventType: 'INPUT_RGB',
        workpieceId,
        workpieceType: history.workpieceType,
        location: moduleSerialId,
        moduleId: moduleSerialId,
        moduleName: stationName || 'DPS',
        orderId: item.orderId,
        orderUpdateId: item.orderUpdateId,
        orderType: 'STORAGE',
        stationId: stationName || 'DPS',
        stationName: stationName ? this.getStationDisplayName(stationName) : 'DPS',
        actionId: item.actionId,
        subOrderId: intakeSubOrderId,
        eventSource: 'MODULE',
        details: {
          actionState: 'FINISHED',
          command: 'INPUT_RGB',
          originalCommand: 'INPUT_RGB',
        },
      };
      this.attachEnvironmentSnapshotIfRelevant(colorEvent);
      this.tryAppendEvent(environmentKey, history, colorEvent);
    }
  }

  private tryAppendEvent(environmentKey: string, history: WorkpieceHistory, event: TrackTraceEvent): void {
    if (!event.workpieceId) {
      history.events.push(event);
      return;
    }
    if (!this.shouldAppendEvent(environmentKey, event.workpieceId, event)) {
      return;
    }
    history.events.push(event);
  }

  private shouldAppendEvent(environmentKey: string, workpieceId: string, event: TrackTraceEvent): boolean {
    const env = this.getOrCreate(this.dedupSeen, environmentKey, () => new Map<string, Map<string, number>>());
    const wp = this.getOrCreate(env, workpieceId, () => new Map<string, number>());

    const now = Date.now();
    const cutoff = now - WorkpieceHistoryService.DEDUP_TTL_MS;
    // Cheap prune on every insert attempt.
    for (const [key, lastSeen] of wp) {
      if (lastSeen < cutoff) {
        wp.delete(key);
      }
    }

    const key = this.buildDedupKey(event);
    const prev = wp.get(key);
    if (prev !== undefined && prev >= cutoff) {
      return false;
    }

    wp.set(key, now);
    if (wp.size > WorkpieceHistoryService.DEDUP_MAX_KEYS_PER_WORKPIECE) {
      // Evict oldest entries (simple O(n) scan; size is capped and small).
      const entries = [...wp.entries()].sort((a, b) => a[1] - b[1]);
      const toDelete = entries.length - WorkpieceHistoryService.DEDUP_MAX_KEYS_PER_WORKPIECE;
      for (let i = 0; i < toDelete; i++) {
        wp.delete(entries[i]![0]);
      }
    }

    return true;
  }

  private buildDedupKey(event: TrackTraceEvent): string {
    // Intake: one Color / one NFC per workpiece (MQTT often doubles RGB_NFC)
    const intakeType = (event.eventType || '').toUpperCase();
    if (
      (intakeType === 'INPUT_RGB' || intakeType === 'RGB_NFC') &&
      event.workpieceId &&
      event.stationId
    ) {
      return [intakeType, event.workpieceId, event.stationId].join('|');
    }

    // Module actions often arrive twice (NodeRed + direct module/state) with the
    // same actionId but different orderUpdateId (e.g. 10 vs 0). Prefer actionId.
    const stationActionTypes = new Set([
      'PICK',
      'DROP',
      'DRILL',
      'MILL',
      'CHECK_QUALITY',
      'PROCESS',
    ]);
    if (
      stationActionTypes.has(intakeType) &&
      event.actionId &&
      event.stationId &&
      event.workpieceId
    ) {
      return [
        intakeType,
        event.workpieceId,
        event.orderId ?? '',
        event.stationId,
        event.actionId,
      ].join('|');
    }

    // Prefer semantic, source-independent keys for station actions so equivalent
    // events from FTS and module streams collapse to one history entry.
    const detailsDir = typeof event.details?.['direction'] === 'string' ? String(event.details['direction']) : '';
    const hasSemanticStationKey =
      !!event.stationId && event.orderUpdateId !== undefined && event.orderUpdateId !== null;
    if (hasSemanticStationKey) {
      return [
        event.eventType ?? '',
        event.workpieceId ?? '',
        event.orderId ?? '',
        String(event.orderUpdateId ?? ''),
        event.stationId ?? '',
        detailsDir,
      ].join('|');
    }
    return [
      event.eventType ?? '',
      event.timestamp ?? '',
      event.workpieceId ?? '',
      event.orderId ?? '',
      String(event.orderUpdateId ?? ''),
      event.actionId ?? '',
      event.location ?? '',
      event.stationId ?? '',
      detailsDir,
    ].join('|');
  }

  private getOrCreate<K, V>(map: Map<K, V>, key: K, factory: () => V): V {
    const existing = map.get(key);
    if (existing !== undefined) {
      return existing;
    }
    const created = factory();
    map.set(key, created);
    return created;
  }

  /**
   * Map FTS action command to Track&Trace event type
   */
  private mapActionCommandToEventType(command: string): string {
    const upperCommand = command.toUpperCase();
    if (['DOCK', 'PICK', 'DROP', 'TRANSPORT', 'PROCESS', 'TURN', 'PASS'].includes(upperCommand)) {
      return upperCommand;
    }
    // Default to TRANSPORT for unknown commands
    return 'TRANSPORT';
  }

  private attachEnvironmentSnapshotIfRelevant(event: TrackTraceEvent): void {
    if (!this.latestEnvironmentSnapshot || !this.shouldCaptureEnvironmentSnapshot(event)) {
      return;
    }
    const details = event.details ? { ...event.details } : {};
    details['environmentSnapshot'] = this.latestEnvironmentSnapshot;
    event.details = details;
  }

  private shouldCaptureEnvironmentSnapshot(event: TrackTraceEvent): boolean {
    const station = (event.stationId || '').toUpperCase();
    const orderType = (event.orderType || '').toUpperCase();
    const type = (event.eventType || '').toUpperCase();
    if (!station || !orderType || !type) {
      return false;
    }
    if (orderType === 'PRODUCTION') {
      if (['DRILL', 'MILL', 'AIQS'].includes(station)) {
        // Process events (MODULE) + FTS DOCK arrival (incl. co-passenger Ist stops)
        return (
          type === 'PROCESS' ||
          type === 'DRILL' ||
          type === 'MILL' ||
          type === 'CHECK_QUALITY' ||
          type === 'DOCK'
        );
      }
      if (station === 'HBW') {
        // Both PICK (outbound/start of production) and DROP (return after quality fail) are relevant
        return type === 'PICK' || type === 'DROP';
      }
      if (station === 'DPS') {
        // PICK = final delivery at DPS (end of production); DROP = storage drop
        return type === 'PICK' || type === 'DROP';
      }
      return false;
    }
    if (orderType === 'STORAGE') {
      // Real storage flow: DPS DROP (into station / accept) then HBW PICK (into rack)
      if (station === 'DPS') {
        return type === 'DROP';
      }
      if (station === 'HBW') {
        return type === 'PICK';
      }
    }
    return false;
  }

  private getPlannedStationChain(
    workpieceType: string,
    orderType: 'STORAGE' | 'PRODUCTION'
  ): string[] {
    if (orderType === 'STORAGE') {
      return ['DPS', 'HBW'];
    }
    const flow = PRODUCTION_WORKFLOWS[workpieceType.toUpperCase()] ?? [];
    return ['HBW', ...flow, 'DPS'];
  }

  /**
   * Get station name from node ID
   */
  private getStationName(nodeId: string): string | null {
    // First, try to get module type from serial ID (for module serial IDs like SVR4H76449)
    const moduleType = this.moduleNameService.getModuleTypeFromSerial(nodeId);
    if (moduleType) {
      return moduleType; // Returns DRILL, MILL, AIQS, HBW, DPS, etc.
    }

    const fallbackType = MODULE_SERIAL_TYPES[nodeId];
    if (fallbackType) {
      return fallbackType;
    }
    
    // Fallback: Try to get from module name service
    const moduleName = this.moduleNameService.getModuleDisplayText(nodeId);
    if (moduleName && moduleName !== nodeId) {
      // Extract station name (e.g., "HBW" from "HBW (High-Bay Warehouse)")
      const match = moduleName.match(/^([A-Z]+)/);
      return match ? match[1] : null;
    }
    return null;
  }

  /**
   * Get human-readable station display name
   */
  private getStationDisplayName(stationId: string): string {
    return this.moduleNameService.getModuleFullName(stationId);
  }

  /**
   * Extract date information from workpiece events
   * Analyzes events to find delivery date (DPS), storage date (HBW), production start (HBW exit), delivery end (DPS)
   */
  private extractDatesFromEvents(events: TrackTraceEvent[], orderType: 'STORAGE' | 'PRODUCTION'): {
    deliveryDate?: string; // Lieferung-Datum (wann angeliefert im DPS)
    storageDate?: string; // Storage-Datum (wann im HBW eingelagert)
    productionStartDate?: string; // Produktions-Start (Auslagerung aus HBW)
    deliveryEndDate?: string; // Auslieferungs-Datum (Production-Ende im DPS)
  } {
    const dpsId = 'SVR4H73275';
    const hbwId = 'SVR3QA0022';
    
    const result: {
      deliveryDate?: string;
      storageDate?: string;
      productionStartDate?: string;
      deliveryEndDate?: string;
    } = {};
    
    // Find first DPS event (delivery date for storage orders)
    if (orderType === 'STORAGE') {
      const firstDpsEvent = events.find(e => e.location === dpsId || e.moduleId === dpsId);
      if (firstDpsEvent) {
        result.deliveryDate = firstDpsEvent.timestamp;
      }
    }
    
    // Find first HBW event (storage date)
    const firstHbwEvent = events.find(e => e.location === hbwId || e.moduleId === hbwId);
    if (firstHbwEvent) {
      result.storageDate = firstHbwEvent.timestamp;
    }
    
    // Find last HBW event before production (production start - Auslagerung aus HBW)
    if (orderType === 'PRODUCTION') {
      // Find the last HBW event before any manufacturing station event
      const manufacturingEvents = events.filter(e => 
        e.stationId === 'DRILL' || e.stationId === 'MILL' || e.stationId === 'AIQS' ||
        e.moduleName === 'DRILL' || e.moduleName === 'MILL' || e.moduleName === 'AIQS'
      );
      if (manufacturingEvents.length > 0) {
        const firstManufacturingEvent = manufacturingEvents[0];
        // Find last HBW event before first manufacturing event
        const hbwEventsBeforeProduction = events.filter(e => 
          (e.location === hbwId || e.moduleId === hbwId) &&
          new Date(e.timestamp).getTime() < new Date(firstManufacturingEvent.timestamp).getTime()
        );
        if (hbwEventsBeforeProduction.length > 0) {
          const lastHbwEvent = hbwEventsBeforeProduction[hbwEventsBeforeProduction.length - 1];
          result.productionStartDate = lastHbwEvent.timestamp;
        }
      }
    }
    
    // Find last DPS event (delivery end date for production orders)
    if (orderType === 'PRODUCTION') {
      const dpsEvents = events.filter(e => e.location === dpsId || e.moduleId === dpsId);
      if (dpsEvents.length > 0) {
        const lastDpsEvent = dpsEvents[dpsEvents.length - 1];
        result.deliveryEndDate = lastDpsEvent.timestamp;
      }
    }
    
    return result;
  }

  /**
   * A1: Collect all distinct CCU/FTS orderIds for a workpiece and rebuild STORAGE + PRODUCTION contexts.
   * Preserves previously resolved ERP/correlation fields per orderId when rebuilding.
   */
  private rebuildOrderContexts(
    history: WorkpieceHistory,
    orders: { active: Record<string, any>; completed: Record<string, any> } | unknown,
    extraOrderId?: string
  ): OrderContext[] {
    const orderIds = new Set<string>();
    const isUsableOrderId = (id: string): boolean => {
      const trimmed = id.trim();
      return trimmed.length > 0 && trimmed !== '0';
    };
    for (const event of history.events ?? []) {
      if (event.orderId && isUsableOrderId(event.orderId)) {
        orderIds.add(event.orderId);
      }
    }
    for (const order of history.orders ?? []) {
      if (order.orderId && isUsableOrderId(order.orderId)) {
        orderIds.add(order.orderId);
      }
    }
    if (extraOrderId && isUsableOrderId(extraOrderId)) {
      orderIds.add(extraOrderId);
    }

    return this.generateOrderContext(
      history.workpieceType,
      orders,
      [...orderIds],
      history.events,
      history.orders
    );
  }

  /**
   * Generate order context from active/completed CCU orders.
   * @param workpieceType - Workpiece type (BLUE, WHITE, RED)
   * @param orders - Orders object with active and completed orders
   * @param orderIds - One or more real backend order UUIDs (from FTS/module events)
   * @param events - Optional events array to extract date information
   * @param previousContexts - Optional prior contexts to preserve ERP/correlation fields
   */
  private generateOrderContext(
    workpieceType: string,
    orders: { active: Record<string, any>; completed: Record<string, any> } | unknown,
    orderIds?: string | string[],
    events?: TrackTraceEvent[],
    previousContexts?: OrderContext[]
  ): OrderContext[] {
    const contexts: OrderContext[] = [];
    const requestedIds = (Array.isArray(orderIds) ? orderIds : orderIds ? [orderIds] : [])
      .map((id) => String(id).trim())
      .filter((id) => id.length > 0);
    const requestedIdSet = new Set(requestedIds);
    const previousById = new Map((previousContexts ?? []).map((ctx) => [ctx.orderId, ctx]));

    // Without concrete backend order UUIDs we must not invent contexts from the full CCU map
    if (requestedIdSet.size === 0) {
      return [];
    }

    // Normalize orders parameter
    const normalizedOrders = orders && typeof orders === 'object' && 'active' in orders
      ? orders as { active: Record<string, any>; completed: Record<string, any> }
      : { active: {}, completed: {} };

    // Helper functions to generate fake ERP IDs
    const generatePurchaseOrderId = (): string => {
      const random = Math.random().toString(36).substring(2, 8).toUpperCase();
      return `ERP-PO-${random}`;
    };
    const generateCustomerOrderId = (): string => {
      const random = Math.random().toString(36).substring(2, 8).toUpperCase();
      return `ERP-CO-${random}`;
    };
    const generateSupplierId = (): string => {
      return `SUP-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
    };
    const generateCustomerId = (): string => {
      return `CUST-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
    };

    // Combine active and completed orders for lookup
    const allOrders = { ...normalizedOrders.active, ...normalizedOrders.completed };
    const allOrdersArray = Object.values(allOrders);
    const matchedIds = new Set<string>();

    // Match CCU orders by real backend UUID(s)
    if (allOrdersArray.length > 0) {
      for (const order of allOrdersArray) {
        if (order && typeof order === 'object' && 'orderId' in order && 'orderType' in order) {
          const orderType = String(order.orderType).toUpperCase();
          const orderId = String(order.orderId);

          // A1: only include explicitly requested backend order UUIDs
          if (!requestedIdSet.has(orderId)) {
            continue;
          }
          matchedIds.add(orderId);

          const previous = previousById.get(orderId);
          
          // Extract ERP IDs if available (for fake ERP integration)
          const purchaseOrderId = 'purchaseOrderId' in order ? String(order.purchaseOrderId) : undefined;
          const customerOrderId = 'customerOrderId' in order ? String(order.customerOrderId) : undefined;
          
          // Extract locations from production steps if available
          let fromLocation: string | undefined;
          let toLocation: string | undefined;
          if ('productionSteps' in order && Array.isArray(order.productionSteps) && order.productionSteps.length > 0) {
            const firstStep = order.productionSteps[0];
            const lastStep = order.productionSteps[order.productionSteps.length - 1];
            fromLocation = 'source' in firstStep ? String(firstStep.source) : undefined;
            toLocation = 'target' in lastStep ? String(lastStep.target) : undefined;
          }

          const orderDate = 'startedAt' in order ? String(order.startedAt) : utcIsoTimestampMs();
          
          // Determine order status: ERROR/FAILED from order.state take precedence (e.g. quality-check failure)
          const orderState = String((order.state ?? order.status ?? '')).toUpperCase();
          const isFailed = ['ERROR', 'FAILED'].includes(orderState);
          const isCompleted = normalizedOrders.completed[orderId] !== undefined;
          const orderStatus: 'ACTIVE' | 'COMPLETED' | 'FAILED' | 'ERROR' = isFailed
            ? (orderState === 'ERROR' ? 'ERROR' : 'FAILED')
            : isCompleted
              ? 'COMPLETED'
              : 'ACTIVE';

          // Extract date information from events belonging to this order when possible
          const eventsForOrder = (events ?? []).filter((event) => !event.orderId || event.orderId === orderId);
          const extractedDates = this.extractDatesFromEvents(
            eventsForOrder.length > 0 ? eventsForOrder : (events ?? []),
            orderType as 'STORAGE' | 'PRODUCTION'
          );

          if (orderType === 'STORAGE') {
            // Primary: CorrelationInfoService (dsp/correlation/info from DSP)
            // Fallback: previous context, then ErpOrderDataService
            const correlationInfo = this.correlationInfoService.getCorrelationInfo(orderId);
            const fromCorrelation = correlationInfo?.orderType === 'PURCHASE' ? correlationInfo : null;
            const workpieceTypeUpper = workpieceType.toUpperCase() as 'BLUE' | 'WHITE' | 'RED';
            const erpPurchaseData =
              fromCorrelation || previous?.purchaseOrderId
                ? null
                : this.erpOrderDataService.popPurchaseOrderForWorkpieceType(workpieceTypeUpper);

            contexts.push({
              orderId,
              orderType: 'STORAGE',
              purchaseOrderId:
                purchaseOrderId ||
                previous?.purchaseOrderId ||
                fromCorrelation?.purchaseOrderId ||
                erpPurchaseData?.purchaseOrderId ||
                generatePurchaseOrderId(),
              supplierId:
                previous?.supplierId ??
                fromCorrelation?.supplierId ??
                erpPurchaseData?.supplierId ??
                generateSupplierId(),
              orderDate:
                previous?.orderDate ??
                fromCorrelation?.orderDate ??
                erpPurchaseData?.orderDate ??
                orderDate,
              rawMaterialOrderDate:
                previous?.rawMaterialOrderDate ??
                fromCorrelation?.orderDate ??
                erpPurchaseData?.orderDate,
              deliveryDate: extractedDates.deliveryDate ?? previous?.deliveryDate ?? fromCorrelation?.plannedDeliveryDate,
              storageDate: extractedDates.storageDate ?? previous?.storageDate,
              fromLocation: fromLocation ?? previous?.fromLocation,
              toLocation: toLocation ?? previous?.toLocation,
              startTime: 'startedAt' in order ? String(order.startedAt) : previous?.startTime,
              endTime: 'stoppedAt' in order ? String(order.stoppedAt) : previous?.endTime,
              status: orderStatus,
              plannedStationChain: this.getPlannedStationChain(workpieceType, 'STORAGE'),
            });
          } else if (orderType === 'PRODUCTION') {
            // Primary: CorrelationInfoService (dsp/correlation/info from DSP)
            // Fallback: previous context, then ErpOrderDataService
            const correlationInfo = this.correlationInfoService.getCorrelationInfo(orderId);
            const fromCorrelation = correlationInfo?.orderType === 'CUSTOMER' ? correlationInfo : null;
            const erpCustomerData =
              fromCorrelation || previous?.customerOrderId
                ? null
                : this.erpOrderDataService.popCustomerOrder();

            contexts.push({
              orderId,
              orderType: 'PRODUCTION',
              customerOrderId:
                customerOrderId ||
                previous?.customerOrderId ||
                fromCorrelation?.customerOrderId ||
                erpCustomerData?.customerOrderId ||
                generateCustomerOrderId(),
              customerId:
                previous?.customerId ??
                fromCorrelation?.customerId ??
                erpCustomerData?.customerId ??
                generateCustomerId(),
              orderDate:
                previous?.orderDate ??
                fromCorrelation?.orderDate ??
                erpCustomerData?.orderDate ??
                orderDate,
              customerOrderDate:
                previous?.customerOrderDate ??
                fromCorrelation?.orderDate ??
                erpCustomerData?.orderDate,
              productionStartDate:
                extractedDates.productionStartDate ??
                previous?.productionStartDate ??
                ('startedAt' in order ? String(order.startedAt) : undefined),
              deliveryEndDate:
                extractedDates.deliveryEndDate ??
                previous?.deliveryEndDate ??
                fromCorrelation?.plannedDeliveryDate ??
                ('stoppedAt' in order ? String(order.stoppedAt) : undefined),
              fromLocation: fromLocation ?? previous?.fromLocation,
              toLocation: toLocation ?? previous?.toLocation,
              startTime: 'startedAt' in order ? String(order.startedAt) : previous?.startTime,
              endTime: 'stoppedAt' in order ? String(order.stoppedAt) : previous?.endTime,
              status: orderStatus,
              plannedStationChain: this.getPlannedStationChain(workpieceType, 'PRODUCTION'),
            });
          }
        }
      }
    }

    // For requested IDs not yet matched in CCU maps, keep previous context or create a typed shell
    for (const orderId of requestedIds) {
      if (matchedIds.has(orderId)) {
        continue;
      }
      const previous = previousById.get(orderId);
      if (previous) {
        contexts.push({ ...previous });
        continue;
      }

      const eventsForOrder = (events ?? []).filter((event) => event.orderId === orderId);
      const lastEvent = eventsForOrder[eventsForOrder.length - 1];
      const inferredType =
        eventsForOrder.find((event) => event.orderType === 'STORAGE' || event.orderType === 'PRODUCTION')
          ?.orderType ??
        (lastEvent?.location
          ? this.determineOrderType(lastEvent.location, eventsForOrder)
          : 'STORAGE');

      if (inferredType === 'PRODUCTION') {
        contexts.push({
          orderId,
          orderType: 'PRODUCTION',
          customerOrderId: generateCustomerOrderId(),
          customerId: generateCustomerId(),
          orderDate: utcIsoTimestampMs(),
          startTime: utcIsoTimestampMs(),
          plannedStationChain: this.getPlannedStationChain(workpieceType, 'PRODUCTION'),
        });
      } else {
        contexts.push({
          orderId,
          orderType: 'STORAGE',
          purchaseOrderId: generatePurchaseOrderId(),
          supplierId: generateSupplierId(),
          orderDate: utcIsoTimestampMs(),
          startTime: utcIsoTimestampMs(),
          plannedStationChain: this.getPlannedStationChain(workpieceType, 'STORAGE'),
        });
      }
    }

    // If nothing requested and nothing matched, do not invent fake dual shells with one UUID
    if (contexts.length === 0) {
      console.warn('[WorkpieceHistoryService] No orders found for requested IDs. Cannot generate order context.', {
        requestedIds,
      });
      return [];
    }

    // Stable demo order: STORAGE first, then PRODUCTION; within type by start/order date
    const typeRank = (orderType: string): number =>
      orderType.toUpperCase() === 'STORAGE' ? 0 : orderType.toUpperCase() === 'PRODUCTION' ? 1 : 2;

    const sorted = contexts.sort((a, b) => {
      const rankDiff = typeRank(a.orderType) - typeRank(b.orderType);
      if (rankDiff !== 0) {
        return rankDiff;
      }
      const aTime = Date.parse(a.startTime || a.orderDate || '') || 0;
      const bTime = Date.parse(b.startTime || b.orderDate || '') || 0;
      return aTime - bTime;
    });

    // Demo: one STORAGE + one PRODUCTION card (merge MQTT intake/transport UUID shells)
    return this.collapseOrderContextsByBusinessType(sorted, events);
  }

  /**
   * Keep at most one STORAGE and one PRODUCTION shell.
   * Prefers CCU-matched contexts with the richest dates/ERP fields.
   */
  private collapseOrderContextsByBusinessType(
    contexts: OrderContext[],
    events?: TrackTraceEvent[]
  ): OrderContext[] {
    const score = (ctx: OrderContext): number => {
      let s = 0;
      if (ctx.deliveryDate) s += 3;
      if (ctx.storageDate) s += 3;
      if (ctx.productionStartDate) s += 3;
      if (ctx.deliveryEndDate) s += 2;
      if (ctx.status === 'COMPLETED') s += 2;
      if (ctx.status === 'ACTIVE') s += 1;
      if (ctx.purchaseOrderId && !ctx.purchaseOrderId.startsWith('ERP-PO-')) s += 2;
      if (ctx.customerOrderId && !ctx.customerOrderId.startsWith('ERP-CO-')) s += 2;
      if (ctx.orderId && ctx.orderId.length > 8 && ctx.orderId !== '0') s += 1;
      const eventHits = (events ?? []).filter((e) => e.orderId === ctx.orderId).length;
      s += Math.min(eventHits, 5);
      return s;
    };

    const mergeFields = (winner: OrderContext, other: OrderContext): OrderContext => ({
      ...winner,
      purchaseOrderId: winner.purchaseOrderId || other.purchaseOrderId,
      supplierId: winner.supplierId || other.supplierId,
      customerOrderId: winner.customerOrderId || other.customerOrderId,
      customerId: winner.customerId || other.customerId,
      orderDate: winner.orderDate || other.orderDate,
      startTime: winner.startTime || other.startTime,
      endTime: winner.endTime || other.endTime,
      fromLocation: winner.fromLocation || other.fromLocation,
      toLocation: winner.toLocation || other.toLocation,
      status: winner.status || other.status,
      rawMaterialOrderDate: winner.rawMaterialOrderDate || other.rawMaterialOrderDate,
      deliveryDate: winner.deliveryDate || other.deliveryDate,
      storageDate: winner.storageDate || other.storageDate,
      customerOrderDate: winner.customerOrderDate || other.customerOrderDate,
      productionStartDate: winner.productionStartDate || other.productionStartDate,
      deliveryEndDate: winner.deliveryEndDate || other.deliveryEndDate,
      plannedStationChain: winner.plannedStationChain?.length
        ? winner.plannedStationChain
        : other.plannedStationChain,
    });

    const pickOne = (items: OrderContext[]): OrderContext | null => {
      if (items.length === 0) {
        return null;
      }
      const ranked = [...items].sort((a, b) => score(b) - score(a));
      let winner = ranked[0]!;
      for (let i = 1; i < ranked.length; i++) {
        winner = mergeFields(winner, ranked[i]!);
      }
      return winner;
    };

    const storage = pickOne(contexts.filter((c) => c.orderType.toUpperCase() === 'STORAGE'));
    const production = pickOne(contexts.filter((c) => c.orderType.toUpperCase() === 'PRODUCTION'));
    const other = contexts.filter((c) => {
      const t = c.orderType.toUpperCase();
      return t !== 'STORAGE' && t !== 'PRODUCTION';
    });

    const result: OrderContext[] = [];
    if (storage) {
      result.push(storage);
    }
    if (production) {
      result.push(production);
    }
    result.push(...other);
    return result;
  }

  /**
   * Determine order type based on current location and event history
   */
  private determineOrderType(location: string, events: TrackTraceEvent[]): 'STORAGE' | 'PRODUCTION' {
    // If at DPS (destination) or coming from DPS, it's a storage order (raw material inbound)
    // If at HBW (source) or going through manufacturing stations, it's a production order
    const dpsId = 'SVR4H73275';
    const hbwId = 'SVR3QA0022';

    // Check if we've been at HBW - if so, we're in production
    const wasAtHbw = events.some((e) => e.location === hbwId);

    // Check if we've been at any manufacturing station (MILL, DRILL, AIQS)
    const wasAtManufacturingStation = events.some((e) => {
      // Check if location is a manufacturing station serial ID
      if (MANUFACTURING_STATIONS.includes(e.location as typeof MANUFACTURING_STATIONS[number])) {
        return true;
      }
      // Check if moduleName indicates a manufacturing station
      const moduleType = e.moduleName || this.getModuleNameFromSerial(e.location);
      return moduleType === 'MILL' || moduleType === 'DRILL' || moduleType === 'AIQS';
    });

    // Check current location
    const isAtManufacturingStation = MANUFACTURING_STATIONS.includes(
      location as typeof MANUFACTURING_STATIONS[number]
    );
    const currentModuleType = this.getModuleNameFromSerial(location);
    const isCurrentManufacturingStation = 
      currentModuleType === 'MILL' || 
      currentModuleType === 'DRILL' || 
      currentModuleType === 'AIQS';

    // If at DPS and never been at HBW or manufacturing stations, it's storage
    if (location === dpsId && !wasAtHbw && !wasAtManufacturingStation) {
      return 'STORAGE';
    }

    // If we've been at HBW or manufacturing stations, it's production
    if (wasAtHbw || wasAtManufacturingStation || isAtManufacturingStation || isCurrentManufacturingStation) {
      return 'PRODUCTION';
    }

    // Default to STORAGE for safety
    return 'STORAGE';
  }

  /**
   * Get or create store for environment
   */
  private getStore(environmentKey: string): BehaviorSubject<Map<string, WorkpieceHistory>> {
    if (!this.stores.has(environmentKey)) {
      this.stores.set(environmentKey, new BehaviorSubject<Map<string, WorkpieceHistory>>(new Map()));
    }
    return this.stores.get(environmentKey)!;
  }
}

