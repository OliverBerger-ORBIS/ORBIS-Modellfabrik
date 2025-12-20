import { Injectable, OnDestroy, inject } from '@angular/core';
import { BehaviorSubject, Observable, combineLatest, Subscription, merge } from 'rxjs';
import { map, distinctUntilChanged, shareReplay, startWith, filter } from 'rxjs/operators';
import { MessageMonitorService } from './message-monitor.service';
import { ModuleNameService } from './module-name.service';
import { EnvironmentService } from './environment.service';
import { FtsRouteService } from './fts-route.service';
import { ErpOrderDataService } from './erp-order-data.service';

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
  status?: 'ACTIVE' | 'COMPLETED'; // Order status from Orders-Tab
  // Additional date fields for better tracking
  rawMaterialOrderDate?: string; // Bestellung-Datum RAW-Material (wann bestellt im Process-Tab)
  deliveryDate?: string; // Lieferung-Datum (wann angeliefert im DPS)
  storageDate?: string; // Storage-Datum (wann im HBW eingelagert)
  customerOrderDate?: string; // Bestellung-Datum Customer-Order (wann erfolgte Kunden-Bestellung)
  productionStartDate?: string; // Produktions-Start (Auslagerung aus HBW)
  deliveryEndDate?: string; // Auslieferungs-Datum (Production-Ende im DPS)
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
  } | null;
  loads?: Array<{
    loadType?: 'BLUE' | 'WHITE' | 'RED' | null;
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
  private readonly environmentService = inject(EnvironmentService);
  private readonly ftsRouteService = inject(FtsRouteService);
  private readonly erpOrderDataService = inject(ErpOrderDataService);
  // TURN direction lookup (from order stream) - similar to FTS-Tab
  private readonly turnDirectionByActionId = new Map<string, 'LEFT' | 'RIGHT' | string>();

  ngOnDestroy(): void {
    // Clean up all subscriptions
    this.subscriptions.forEach((sub) => sub.unsubscribe());
    this.subscriptions.clear();
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
  }

  /**
   * Initialize tracking for an environment
   * Subscribes to relevant MQTT topics and aggregates events
   */
  initialize(environmentKey: string): void {
    if (this.subscriptions.has(environmentKey)) {
      return; // Already initialized
    }

    const historyMap = this.getStore(environmentKey);

    // Subscribe to FTS state messages
    const ftsState$ = this.messageMonitor.getLastMessage('fts/v1/ff/5iO4/state').pipe(
      map((msg) => {
        if (!msg?.valid || !msg.payload) return null;
        try {
          const payload = typeof msg.payload === 'string' ? JSON.parse(msg.payload) : msg.payload;
          // Extract module serial ID from topic
          const moduleSerialId = this.extractModuleSerialFromTopic(msg.topic);
          return {
            ...payload,
            _topic: msg.topic,
            _moduleSerialId: moduleSerialId,
          };
        } catch {
          return null;
        }
      })
    );

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
    
    // Combine FTS state and orders to update history
    // Use startWith(null) to ensure combineLatest emits even if one stream hasn't emitted yet
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
    // Combine with allOrders to have order context available
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

    // Combine both subscriptions
    const combinedSubscription = new Subscription();
    combinedSubscription.add(ftsSubscription);
    combinedSubscription.add(moduleSubscription);

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
  private getModuleNameFromSerial(serialId: string | null | undefined): string | null {
    if (!serialId) return null;
    
    // Check if it's an intersection using FtsRouteService mapping
    const resolved = this.ftsRouteService.resolveNodeRef(serialId);
    if (resolved && resolved.startsWith('intersection:')) {
      return null; // Intersections are handled separately
    }

    // Try to resolve via ModuleNameService
    const moduleType = this.moduleNameService.getModuleTypeFromSerial(serialId);
    if (moduleType) {
      return moduleType;
    }

    // Check if it's FTS (common serial: 5iO4)
    if (serialId === '5iO4' || serialId.toLowerCase().includes('fts')) {
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
    const moduleName = this.getModuleNameFromSerial(moduleSerialId) || 'FTS';

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
          orders: this.generateOrderContext(loadItem.loadType, normalizedOrders, state.orderId, []),
        };

        // Determine order type based on location
        const orderType = this.determineOrderType(state.lastNodeId, existingHistory.events);

        // Get station info
        const stationName = this.getStationName(state.lastNodeId);
        const isModuleStation = MODULE_STATIONS.includes(
          state.lastNodeId as typeof MODULE_STATIONS[number]
        );
        const isManufacturingStation = MANUFACTURING_STATIONS.includes(
          state.lastNodeId as typeof MANUFACTURING_STATIONS[number]
        );
        const processDuration = stationName ? PROCESS_DURATIONS[stationName] : undefined;

        // Check if location changed to generate proper station events
        // ALWAYS generate an event if location changed OR if this is the first event
        const lastEvent = existingHistory.events[existingHistory.events.length - 1];
        const locationChanged = !lastEvent || lastEvent.location !== state.lastNodeId;
        
        if (locationChanged) {
          // Debug: Log location change and order type determination
          console.log('[WorkpieceHistoryService] Location changed for workpiece:', {
            workpieceId: loadItem.loadId,
            workpieceType: loadItem.loadType,
            oldLocation: lastEvent?.location,
            newLocation: state.lastNodeId,
            stationName,
            orderType,
            isManufacturingStation,
            wasAtHbw: existingHistory.events.some((e) => e.location === 'SVR3QA0022'),
            wasAtManufacturingStation: existingHistory.events.some((e) => {
              const moduleType = e.moduleName || this.getModuleNameFromSerial(e.location);
              return moduleType === 'MILL' || moduleType === 'DRILL' || moduleType === 'AIQS';
            }),
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
          };

          // Generate sub-order ID for this event sequence
          const subOrderId = `${state.orderId}-${existingHistory.events.length + 1}`;
          // Use action state ID as actionId for sorting
          const actionId = state.actionState.id;

          // CRITICAL: Check if this workpiece can actually be processed at this station
          // RED workpieces do NOT go to DRILL, etc.
          // This check is ONLY for PROCESS events, not for transport events
          const canBeProcessed = this.canWorkpieceBeProcessedAtStation(loadItem.loadType, stationName);

          // Only generate PROCESS events (PICK → PROCESS → DROP) if:
          // 1. It's a module station
          // 2. It's a production order
          // 3. The workpiece can actually be processed at this station
          if (isModuleStation && orderType === 'PRODUCTION' && canBeProcessed) {
            // Generate PICK -> PROCESS -> DROP sequence for manufacturing stations
            // PICK event
            existingHistory.events.push({
              ...baseEvent,
              eventType: 'PICK',
              timestamp: state.timestamp,
              subOrderId,
              actionId,
              details: { actionState: 'FINISHED', loadPosition: loadItem.loadPosition },
            } as TrackTraceEvent);

            // PROCESS event (drilling, milling, etc.)
            const processTime = new Date(new Date(state.timestamp).getTime() + 1000);
            existingHistory.events.push({
              ...baseEvent,
              eventType: 'PROCESS',
              timestamp: processTime.toISOString(),
              processDuration: processDuration,
              subOrderId,
              actionId,
              details: {
                actionState: 'FINISHED',
                loadPosition: loadItem.loadPosition,
                processType: stationName,
              },
            } as TrackTraceEvent);

            // DROP event
            const dropTime = new Date(processTime.getTime() + (processDuration || 10) * 1000);
            existingHistory.events.push({
              ...baseEvent,
              eventType: 'DROP',
              timestamp: dropTime.toISOString(),
              subOrderId,
              actionId,
              details: { actionState: 'FINISHED', loadPosition: loadItem.loadPosition },
            } as TrackTraceEvent);
          } else {
            // Regular event for transport/storage
            // Also for cases where workpiece cannot be processed at this station (e.g., RED at DRILL)
            const eventType = this.mapActionCommandToEventType(state.actionState.command);
            // Extract TURN direction from actionState metadata or turnDirectionByActionId map
            let turnDirection: string | undefined;
            if (eventType === 'TURN') {
              // Try to get direction from actionState metadata (if available in FTS state)
              const actionStateMeta = (state.actionState as any)?.metadata;
              if (actionStateMeta?.direction) {
                turnDirection = actionStateMeta.direction;
              } else {
                // Fallback to order-derived map
                turnDirection = this.turnDirectionByActionId.get(state.actionState.id);
              }
            }
            
            existingHistory.events.push({
              ...baseEvent,
              eventType: eventType,
              subOrderId,
              actionId,
              details: {
                actionState: state.actionState.state,
                loadPosition: loadItem.loadPosition,
                direction: turnDirection, // Store direction in details for TURN events
              },
            } as TrackTraceEvent);
          }
          
          console.log('[WorkpieceHistoryService] Generated event for workpiece:', {
            workpieceId: loadItem.loadId,
            eventType: isModuleStation && orderType === 'PRODUCTION' && canBeProcessed ? 'PICK/PROCESS/DROP' : baseEvent.eventType,
            location: state.lastNodeId,
            eventsCount: existingHistory.events.length,
          });
        }

        existingHistory.currentLocation = state.lastNodeId;
        existingHistory.currentState = state.driving ? 'IN_TRANSPORT' : 'STATIONARY';
        
        // Update order context with extracted dates from events
        if (existingHistory.orders && existingHistory.orders.length > 0) {
          const orderType = this.determineOrderType(state.lastNodeId, existingHistory.events);
          const extractedDates = this.extractDatesFromEvents(existingHistory.events, orderType);
          
          existingHistory.orders = existingHistory.orders.map(order => {
            if (order.orderType === 'STORAGE') {
              return {
                ...order,
                deliveryDate: extractedDates.deliveryDate || order.deliveryDate,
                storageDate: extractedDates.storageDate || order.storageDate,
              };
            } else if (order.orderType === 'PRODUCTION') {
              return {
                ...order,
                productionStartDate: extractedDates.productionStartDate || order.productionStartDate,
                deliveryEndDate: extractedDates.deliveryEndDate || order.deliveryEndDate,
              };
            }
            return order;
          });
        }
        
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

    // Skip if no actionState or no loads
    if (!moduleState.actionState || !moduleState.loads || moduleState.loads.length === 0) {
      return;
    }

    const actionState = moduleState.actionState;
    const command = actionState.command.toUpperCase();
    const actionStateValue = actionState.state.toUpperCase();

    // Map CHECK_QUALITY to PROCESS for AIQS
    const mappedCommand = command === 'CHECK_QUALITY' ? 'PROCESS' : command;

    // Only process PICK, PROCESS, DROP commands (including CHECK_QUALITY mapped to PROCESS)
    if (!['PICK', 'PROCESS', 'DROP'].includes(mappedCommand)) {
      return;
    }

    // Get workpiece type from loads array
    const loadItem = moduleState.loads[0];
    const workpieceType = loadItem?.loadType;

    if (!workpieceType) {
      return; // No workpiece type, skip
    }

    // Find workpiece history by matching orderId and workpieceType
    // We need to find the workpiece that matches this module's orderId and workpieceType
    let matchingWorkpieceId: string | null = null;
    let matchingHistory: WorkpieceHistory | null = null;

    for (const [workpieceId, history] of historyMap.entries()) {
      if (history.workpieceType === workpieceType) {
        // Check if any event has matching orderId and orderUpdateId
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

    // If no matching workpiece found, we might need to create one
    // But for now, we'll skip if we can't find a match
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

    // Check if this event already exists (avoid duplicates)
    const eventExists = matchingHistory.events.some(
      (event) =>
        event.moduleId === moduleSerialId &&
        event.eventType === mappedCommand &&
        event.actionId === actionState.id &&
        event.timestamp === moduleState.timestamp
    );

    if (eventExists) {
      return; // Event already exists, skip
    }

    // Generate event
    // IMPORTANT: For module events, use stationName (DRILL, AIQS, etc.) as moduleName
    // This ensures that events in Level 3 show "DRILL PICK" instead of "FTS PICK"
    const eventModuleName = stationName || moduleName || 'UNKNOWN';
    
    const baseEvent: Partial<TrackTraceEvent> = {
      timestamp: moduleState.timestamp,
      workpieceId: matchingWorkpieceId,
      workpieceType: workpieceType,
      location: moduleSerialId,
      moduleId: moduleSerialId,
      moduleName: eventModuleName, // Use stationName (DRILL, AIQS, etc.) for module events
      orderId: moduleState.orderId,
      orderUpdateId: moduleState.orderUpdateId,
      orderType: 'PRODUCTION', // Module events are always production
      stationId: stationName || undefined,
      stationName: stationName ? this.getStationDisplayName(stationName) : undefined,
      eventType: mappedCommand, // Use mapped command (CHECK_QUALITY -> PROCESS)
      actionId: actionState.id,
      processDuration: mappedCommand === 'PROCESS' && stationName ? PROCESS_DURATIONS[stationName] : undefined,
      details: {
        actionState: actionStateValue,
        command: command, // Keep original command in details
        originalCommand: command, // Store original for reference
      },
    };

    // Generate sub-order ID - find the most recent FTS event that brought the workpiece to this module
    // This ensures Module-Events use the same Sub-Order-ID as the FTS DOCK event
    const ftsDockEvent = matchingHistory.events
      .filter((e) => 
        e.orderId === moduleState.orderId &&
        e.location === moduleSerialId &&
        e.eventType === 'DOCK' &&
        e.moduleName === 'FTS'
      )
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0];
    
    // If we found a DOCK event, use its subOrderId
    // Otherwise, try to find any event with matching orderId and orderUpdateId
    let subOrderId: string;
    if (ftsDockEvent?.subOrderId) {
      subOrderId = ftsDockEvent.subOrderId;
    } else {
      // Fallback: find the most recent event with matching orderId and orderUpdateId
      const matchingEvent = matchingHistory.events
        .filter((e) => 
          e.orderId === moduleState.orderId &&
          (moduleState.orderUpdateId === undefined || e.orderUpdateId === moduleState.orderUpdateId)
        )
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0];
      
      subOrderId = matchingEvent?.subOrderId || `${moduleState.orderId}-${matchingHistory.events.length + 1}`;
    }
    
    baseEvent.subOrderId = subOrderId;

    // Add event to history
    matchingHistory.events.push(baseEvent as TrackTraceEvent);

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

    historyMap.set(matchingWorkpieceId, matchingHistory);
    this.getStore(environmentKey).next(historyMap);
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

  /**
   * Get station name from node ID
   */
  private getStationName(nodeId: string): string | null {
    // First, try to get module type from serial ID (for module serial IDs like SVR4H76449)
    const moduleType = this.moduleNameService.getModuleTypeFromSerial(nodeId);
    if (moduleType) {
      return moduleType; // Returns DRILL, MILL, AIQS, HBW, DPS, etc.
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
    const names: Record<string, string> = {
      'HBW': 'High Bay Warehouse',
      'DRILL': 'Drilling Station',
      'MILL': 'Milling Station',
      'AIQS': 'Quality Inspection',
      'DPS': 'Dispatch Station',
    };
    return names[stationId] || stationId;
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
   * Generate order context from active orders
   * @param workpieceType - Workpiece type (BLUE, WHITE, RED)
   * @param orders - Orders object with active and completed orders
   * @param ftsOrderId - Order ID from FTS state (real UUID from backend, not generated!)
   * @param events - Optional events array to extract date information
   */
  private generateOrderContext(
    workpieceType: string,
    orders: { active: Record<string, any>; completed: Record<string, any> } | unknown,
    ftsOrderId?: string,
    events?: TrackTraceEvent[]
  ): OrderContext[] {
    const contexts: OrderContext[] = [];

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
    const activeOrdersArray = Object.values(normalizedOrders.active);
    const allOrdersArray = Object.values(allOrders);

    // Try to extract order info from orders if available
    // Match orders by orderId - prefer FTS orderId if provided
    if (allOrdersArray.length > 0) {
      for (const order of allOrdersArray) {
        if (order && typeof order === 'object' && 'orderId' in order && 'orderType' in order) {
          const orderType = String(order.orderType).toUpperCase();
          const orderId = String(order.orderId);

          // If ftsOrderId is provided, only process matching orders
          // This ensures we use the real UUID from FTS state
          if (ftsOrderId && orderId !== ftsOrderId) {
            continue; // Skip orders that don't match the FTS orderId
          }
          
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

          const orderDate = 'startedAt' in order ? String(order.startedAt) : new Date().toISOString();
          
          // Determine order status (ACTIVE or COMPLETED)
          const isCompleted = normalizedOrders.completed[orderId] !== undefined;
          const orderStatus: 'ACTIVE' | 'COMPLETED' = isCompleted ? 'COMPLETED' : 'ACTIVE';

          // Extract date information from events if available
          const extractedDates = events ? this.extractDatesFromEvents(events, orderType as 'STORAGE' | 'PRODUCTION') : {};

          if (orderType === 'STORAGE') {
            // Try to get ERP Purchase Order data from ErpOrderDataService
            // Match by workpieceType (BLUE, WHITE, RED)
            const workpieceTypeUpper = workpieceType.toUpperCase() as 'BLUE' | 'WHITE' | 'RED';
            const erpPurchaseData = this.erpOrderDataService.popPurchaseOrderForWorkpieceType(workpieceTypeUpper);
            
            contexts.push({
              orderId,
              orderType: 'STORAGE',
              purchaseOrderId: purchaseOrderId || erpPurchaseData?.purchaseOrderId || generatePurchaseOrderId(),
              supplierId: erpPurchaseData?.supplierId || generateSupplierId(),
              orderDate: erpPurchaseData?.orderDate || orderDate, // Bestellung-Datum RAW-Material
              rawMaterialOrderDate: erpPurchaseData?.orderDate, // Bestellung-Datum RAW-Material (explicit)
              deliveryDate: extractedDates.deliveryDate, // Lieferung-Datum (wann angeliefert im DPS)
              storageDate: extractedDates.storageDate, // Storage-Datum (wann im HBW eingelagert)
              fromLocation,
              toLocation,
              startTime: 'startedAt' in order ? String(order.startedAt) : undefined, // Storage-Start
              endTime: 'stoppedAt' in order ? String(order.stoppedAt) : undefined, // Storage-Ende
              status: orderStatus,
            });
          } else if (orderType === 'PRODUCTION') {
            // Try to get ERP Customer Order data from ErpOrderDataService
            const erpCustomerData = this.erpOrderDataService.popCustomerOrder();
            
            contexts.push({
              orderId,
              orderType: 'PRODUCTION',
              customerOrderId: customerOrderId || erpCustomerData?.customerOrderId || generateCustomerOrderId(),
              customerId: erpCustomerData?.customerId || generateCustomerId(),
              orderDate: erpCustomerData?.orderDate || orderDate, // Bestellung-Datum Customer-Order
              customerOrderDate: erpCustomerData?.orderDate, // Bestellung-Datum Customer-Order (explicit)
              productionStartDate: extractedDates.productionStartDate || ('startedAt' in order ? String(order.startedAt) : undefined), // Produktions-Start (Auslagerung aus HBW)
              deliveryEndDate: extractedDates.deliveryEndDate || ('stoppedAt' in order ? String(order.stoppedAt) : undefined), // Auslieferungs-Datum (Production-Ende im DPS)
              fromLocation,
              toLocation,
              startTime: 'startedAt' in order ? String(order.startedAt) : undefined, // Produktions-Start
              endTime: 'stoppedAt' in order ? String(order.stoppedAt) : undefined, // Auslieferungs-Datum
              status: orderStatus,
            });
          }
        }
      }
    }

    // If no orders found, but we have an FTS orderId, create context with real orderId
    // This ensures we always use the real UUID from the backend, not generated IDs
    if (contexts.length === 0 && ftsOrderId) {
      const now = new Date();
      const oneHourAgo = new Date(now.getTime() - 3600000);

      // Try to get ERP data from ErpOrderDataService
      const workpieceTypeUpper = workpieceType.toUpperCase() as 'BLUE' | 'WHITE' | 'RED';
      const erpPurchaseData = this.erpOrderDataService.popPurchaseOrderForWorkpieceType(workpieceTypeUpper);
      const erpCustomerData = this.erpOrderDataService.popCustomerOrder();

      // Determine order type based on workpiece history (will be refined by determineOrderType)
      // For now, create both contexts and let the event system determine which one to use
      // The orderId will be the real UUID from FTS state
      return [
        {
          orderId: ftsOrderId, // Use real UUID from FTS state, not generated!
          orderType: 'STORAGE',
          purchaseOrderId: erpPurchaseData?.purchaseOrderId || generatePurchaseOrderId(), // Use ERP data if available
          supplierId: erpPurchaseData?.supplierId || generateSupplierId(), // Use ERP data if available
          orderDate: erpPurchaseData?.orderDate || oneHourAgo.toISOString(),
          startTime: oneHourAgo.toISOString(),
        },
        {
          orderId: ftsOrderId, // Use real UUID from FTS state, not generated!
          orderType: 'PRODUCTION',
          customerOrderId: erpCustomerData?.customerOrderId || generateCustomerOrderId(), // Use ERP data if available
          customerId: erpCustomerData?.customerId || generateCustomerId(), // Use ERP data if available
          orderDate: erpCustomerData?.orderDate || now.toISOString(),
          startTime: now.toISOString(),
        },
      ];
    }

    // If no orders found and no FTS orderId, return empty array
    // This should not happen in normal operation, but prevents generating fake orderIds
    if (contexts.length === 0) {
      console.warn('[WorkpieceHistoryService] No orders found and no FTS orderId available. Cannot generate order context.');
      return [];
    }

    return contexts;
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

