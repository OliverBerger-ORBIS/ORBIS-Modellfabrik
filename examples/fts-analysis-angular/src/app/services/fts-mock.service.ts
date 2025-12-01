import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Observable, interval, Subscription } from 'rxjs';
import { map, distinctUntilChanged } from 'rxjs/operators';
import {
  FtsState,
  FtsOrder,
  FtsBatteryState,
  FtsActionState,
  FtsLoadInfo,
  TrackTraceEvent,
  WorkpieceHistory,
  OrderContext,
} from '../models/fts.types';

/** Generate fake ERP IDs for demo */
function generatePurchaseOrderId(): string {
  return `PO-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
}

function generateCustomerOrderId(): string {
  return `CO-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
}

/**
 * Route network matching the shopfloor layout
 * Edges from parsed_roads in shopfloor_layout.json
 */
const ROUTE_EDGES: Array<{ from: string; to: string }> = [
  // Module to intersection connections
  { from: 'SVR3QA0022', to: '1' },   // HBW -> intersection 1
  { from: 'SVR3QA2098', to: '1' },   // MILL -> intersection 1  
  { from: 'SVR4H76449', to: '3' },   // DRILL -> intersection 3
  { from: 'SVR4H76530', to: '2' },   // AIQS -> intersection 2
  { from: 'SVR4H73275', to: '2' },   // DPS -> intersection 2
  { from: 'CHRG0', to: '4' },        // CHRG -> intersection 4
  
  // Intersection to intersection connections
  { from: '1', to: '2' },            // intersection 1 <-> intersection 2
  { from: '3', to: '1' },            // intersection 3 <-> intersection 1
  { from: '3', to: '4' },            // intersection 3 <-> intersection 4
  { from: '4', to: '2' },            // intersection 4 <-> intersection 2
];

/** Build adjacency list for pathfinding */
const ADJACENCY: Record<string, string[]> = {};
ROUTE_EDGES.forEach(edge => {
  if (!ADJACENCY[edge.from]) ADJACENCY[edge.from] = [];
  if (!ADJACENCY[edge.to]) ADJACENCY[edge.to] = [];
  ADJACENCY[edge.from].push(edge.to);
  ADJACENCY[edge.to].push(edge.from);
});

/** Find shortest path between two nodes using BFS */
function findPath(from: string, to: string): string[] {
  if (from === to) return [from];
  if (!ADJACENCY[from] || !ADJACENCY[to]) return [from, to]; // Direct fallback
  
  const visited = new Set<string>();
  const queue: { node: string; path: string[] }[] = [{ node: from, path: [from] }];
  visited.add(from);
  
  while (queue.length > 0) {
    const { node, path } = queue.shift()!;
    const neighbors = ADJACENCY[node] || [];
    
    for (const neighbor of neighbors) {
      if (neighbor === to) {
        return [...path, neighbor];
      }
      if (!visited.has(neighbor)) {
        visited.add(neighbor);
        queue.push({ node: neighbor, path: [...path, neighbor] });
      }
    }
  }
  
  return [from, to]; // No path found, direct fallback
}

/**
 * Mock MQTT Service for FTS Data
 * 
 * Simulates real-time FTS/AGV data based on actual production data from
 * data/omf-data/fts-analysis/production_order_bwr_20251110_182819_fts_state.json
 * 
 * In production, replace with actual MQTT subscription via MessageMonitorService
 */
@Injectable({
  providedIn: 'root'
})
export class FtsMockService implements OnDestroy {
  private ftsStateSubject = new BehaviorSubject<FtsState>(this.createInitialState());
  private ftsOrderSubject = new BehaviorSubject<FtsOrder | null>(null);
  private workpieceHistorySubject = new BehaviorSubject<Map<string, WorkpieceHistory>>(new Map());
  
  private simulationIndex = 0;
  private readonly simulatedStates: Partial<FtsState>[] = this.createSimulatedStates();
  private simulationSubscription: Subscription | null = null;
  
  constructor() {
    this.startSimulation();
  }
  
  ngOnDestroy(): void {
    this.simulationSubscription?.unsubscribe();
  }
  
  /** Observable for current FTS state */
  get ftsState$(): Observable<FtsState> {
    return this.ftsStateSubject.asObservable();
  }
  
  /** Observable for current FTS order */
  get ftsOrder$(): Observable<FtsOrder | null> {
    return this.ftsOrderSubject.asObservable();
  }
  
  /** Observable for battery state only */
  get batteryState$(): Observable<FtsBatteryState> {
    return this.ftsState$.pipe(
      map(state => state.batteryState),
      distinctUntilChanged((a, b) => 
        a.percentage === b.percentage && 
        a.currentVoltage === b.currentVoltage && 
        a.charging === b.charging
      )
    );
  }
  
  /** Observable for current action state */
  get actionState$(): Observable<FtsActionState> {
    return this.ftsState$.pipe(
      map(state => state.actionState),
      distinctUntilChanged((a, b) => a.state === b.state && a.command === b.command)
    );
  }
  
  /** Observable for load information */
  get loads$(): Observable<FtsLoadInfo[]> {
    return this.ftsState$.pipe(
      map(state => state.load),
      distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b))
    );
  }
  
  /** Observable for workpiece history */
  get workpieceHistory$(): Observable<Map<string, WorkpieceHistory>> {
    return this.workpieceHistorySubject.asObservable();
  }
  
  /** Get history for a specific workpiece */
  getWorkpieceHistory(workpieceId: string): Observable<WorkpieceHistory | undefined> {
    return this.workpieceHistory$.pipe(
      map(historyMap => historyMap.get(workpieceId))
    );
  }
  
  private createInitialState(): FtsState {
    return {
      serialNumber: '5iO4',
      headerId: 383,
      timestamp: new Date().toISOString(),
      orderId: 'eb4d90bc-f842-4c59-9cff-07299bb78aa4',
      orderUpdateId: 2,
      lastNodeId: 'SVR3QA0022',
      lastNodeSequenceId: 0,
      lastCode: '',
      driving: false,
      paused: false,
      waitingForLoadHandling: false,
      batteryState: {
        currentVoltage: 9.1,
        minVolt: 7.84,
        maxVolt: 9.1,
        percentage: 100,
        charging: false,
      },
      actionState: {
        id: '0783dd8a-4bc5-4d1f-878f-63c5bf5798de',
        command: 'DOCK',
        state: 'FINISHED',
        timestamp: new Date().toISOString(),
      },
      actionStates: [
        {
          id: '3e3a0658-412c-444b-b9ca-655a06fb4142',
          command: 'PASS',
          state: 'FINISHED',
          timestamp: new Date().toISOString(),
        },
        {
          id: '8bbacf5a-d64b-427f-a624-8db8e346dc1a',
          command: 'PASS',
          state: 'FINISHED',
          timestamp: new Date().toISOString(),
        },
        {
          id: '0783dd8a-4bc5-4d1f-878f-63c5bf5798de',
          command: 'DOCK',
          state: 'FINISHED',
          timestamp: new Date().toISOString(),
        },
      ],
      load: [
        { loadId: null, loadType: null, loadPosition: '1' },
      ],
      nodeStates: [],
      edgeStates: [],
      errors: [],
    };
  }
  
  private createSimulatedStates(): Partial<FtsState>[] {
    const states: Partial<FtsState>[] = [];
    
    // Helper to create a state at a node
    const createState = (
      nodeId: string, 
      driving: boolean, 
      actionId: string, 
      command: string, 
      actionState: string, 
      battery: number, 
      load: FtsLoadInfo[]
    ): Partial<FtsState> => ({
      lastNodeId: nodeId,
      driving,
      batteryState: { currentVoltage: 7.84 + (battery / 100) * 1.26, minVolt: 7.84, maxVolt: 9.1, percentage: battery, charging: false },
      actionState: { id: actionId, command, state: actionState, timestamp: new Date().toISOString() },
      load,
    });
    
    // Helper to generate movement states between two nodes
    const generateMovement = (
      fromNode: string, 
      toNode: string, 
      actionId: string, 
      battery: number, 
      load: FtsLoadInfo[]
    ): Partial<FtsState>[] => {
      const path = findPath(fromNode, toNode);
      const moveStates: Partial<FtsState>[] = [];
      
      for (let i = 0; i < path.length; i++) {
        const node = path[i];
        const isLastNode = i === path.length - 1;
        
        // At each intermediate node, show PASS action
        if (i > 0 && !isLastNode) {
          // Passing through intersection
          moveStates.push(createState(node, true, actionId, 'PASS', 'RUNNING', battery, load));
          moveStates.push(createState(node, true, actionId, 'PASS', 'FINISHED', battery, load));
        } else if (i > 0 && isLastNode) {
          // Arriving at destination - will get DOCK action later
          moveStates.push(createState(node, true, actionId, 'PASS', 'FINISHED', battery, load));
        } else if (i === 0 && path.length > 1) {
          // Starting movement from first node
          moveStates.push(createState(node, true, actionId, 'PASS', 'RUNNING', battery, load));
        }
      }
      
      return moveStates;
    };
    
    // Initial load at HBW
    const emptyLoad: FtsLoadInfo[] = [{ loadId: null, loadType: null, loadPosition: '1' }];
    const blueLoad: FtsLoadInfo[] = [{ loadId: '047389ca341291', loadType: 'BLUE', loadPosition: '1' }];
    const twoLoad: FtsLoadInfo[] = [
      { loadId: '047389ca341291', loadType: 'BLUE', loadPosition: '1' },
      { loadId: '04798eca341290', loadType: 'WHITE', loadPosition: '2' },
    ];
    const fullLoad: FtsLoadInfo[] = [
      { loadId: '047389ca341291', loadType: 'BLUE', loadPosition: '1' },
      { loadId: '04798eca341290', loadType: 'WHITE', loadPosition: '2' },
      { loadId: '040a8dca341291', loadType: 'RED', loadPosition: '3' },
    ];
    
    // Phase 1: Loading at HBW
    states.push(createState('SVR3QA0022', false, 'a1', 'DOCK', 'FINISHED', 100, emptyLoad));
    states.push(createState('SVR3QA0022', false, 'a2', 'DOCK', 'WAITING', 100, emptyLoad));
    states.push(createState('SVR3QA0022', true, 'a2', 'DOCK', 'INITIALIZING', 100, emptyLoad));
    states.push(createState('SVR3QA0022', true, 'a2', 'DOCK', 'RUNNING', 100, emptyLoad));
    states.push(createState('SVR3QA0022', false, 'a2', 'DOCK', 'FINISHED', 98, blueLoad));
    states.push(createState('SVR3QA0022', true, 'a3', 'DOCK', 'RUNNING', 96, blueLoad));
    states.push(createState('SVR3QA0022', false, 'a3', 'DOCK', 'FINISHED', 94, twoLoad));
    states.push(createState('SVR3QA0022', true, 'a4', 'DOCK', 'RUNNING', 92, twoLoad));
    states.push(createState('SVR3QA0022', false, 'a4', 'DOCK', 'FINISHED', 90, fullLoad));
    
    // Phase 2: Move from HBW to DRILL (HBW -> 1 -> 3 -> DRILL)
    states.push(...generateMovement('SVR3QA0022', 'SVR4H76449', 'a5', 88, fullLoad));
    states.push(createState('SVR4H76449', false, 'a6', 'DOCK', 'RUNNING', 86, fullLoad));
    states.push(createState('SVR4H76449', false, 'a6', 'DOCK', 'FINISHED', 84, fullLoad));
    
    // Phase 3: Move from DRILL to MILL (DRILL -> 3 -> 1 -> MILL)
    states.push(...generateMovement('SVR4H76449', 'SVR3QA2098', 'a7', 82, fullLoad));
    states.push(createState('SVR3QA2098', false, 'a8', 'DOCK', 'RUNNING', 80, fullLoad));
    const afterMillLoad: FtsLoadInfo[] = [
      { loadId: null, loadType: null, loadPosition: '1' },
      { loadId: '04798eca341290', loadType: 'WHITE', loadPosition: '2' },
      { loadId: '040a8dca341291', loadType: 'RED', loadPosition: '3' },
    ];
    states.push(createState('SVR3QA2098', false, 'a8', 'DOCK', 'FINISHED', 78, afterMillLoad));
    
    // Phase 4: Move from MILL to AIQS (MILL -> 1 -> 2 -> AIQS)
    states.push(...generateMovement('SVR3QA2098', 'SVR4H76530', 'a9', 76, afterMillLoad));
    states.push(createState('SVR4H76530', false, 'a10', 'DOCK', 'RUNNING', 74, afterMillLoad));
    const afterAiqsLoad: FtsLoadInfo[] = [
      { loadId: '047c8bca341291', loadType: 'WHITE', loadPosition: '1' },
      { loadId: null, loadType: null, loadPosition: '2' },
      { loadId: null, loadType: null, loadPosition: '3' },
    ];
    states.push(createState('SVR4H76530', false, 'a10', 'DOCK', 'FINISHED', 72, afterAiqsLoad));
    
    // Phase 5: Move from AIQS to DPS (AIQS -> 2 -> DPS)
    states.push(...generateMovement('SVR4H76530', 'SVR4H73275', 'a11', 70, afterAiqsLoad));
    states.push(createState('SVR4H73275', false, 'a12', 'DOCK', 'RUNNING', 68, afterAiqsLoad));
    const finalLoad: FtsLoadInfo[] = [
      { loadId: null, loadType: null, loadPosition: '1' },
      { loadId: null, loadType: null, loadPosition: '2' },
      { loadId: null, loadType: null, loadPosition: '3' },
    ];
    states.push(createState('SVR4H73275', false, 'a12', 'DOCK', 'FINISHED', 66, finalLoad));
    
    return states;
  }
  
  private startSimulation(): void {
    // Update state every 1 second for smoother movement animation
    this.simulationSubscription = interval(1000).subscribe(() => {
      const partialState = this.simulatedStates[this.simulationIndex];
      const currentState = this.ftsStateSubject.value;
      
      const newState: FtsState = {
        ...currentState,
        ...partialState,
        headerId: currentState.headerId + 1,
        timestamp: new Date().toISOString(),
      };
      
      // Update action states history
      if (partialState.actionState) {
        const existingIndex = newState.actionStates.findIndex(a => a.id === partialState.actionState!.id);
        if (existingIndex >= 0) {
          newState.actionStates[existingIndex] = partialState.actionState;
        } else {
          newState.actionStates = [...newState.actionStates.slice(-4), partialState.actionState];
        }
      }
      
      this.ftsStateSubject.next(newState);
      
      // Update workpiece history
      this.updateWorkpieceHistory(newState);
      
      // Move to next state
      this.simulationIndex = (this.simulationIndex + 1) % this.simulatedStates.length;
    });
  }
  
  private updateWorkpieceHistory(state: FtsState): void {
    const historyMap = new Map(this.workpieceHistorySubject.value);
    
    // Station serial number to name mapping
    const stationNames: Record<string, string> = {
      'SVR3QA0022': 'HBW',
      'SVR4H76449': 'DRILL',
      'SVR3QA2098': 'MILL',
      'SVR4H76530': 'AIQS',
      'SVR4H73275': 'DPS',
    };
    
    // Process durations in seconds for each station
    const processDurations: Record<string, number> = {
      'DRILL': 15,
      'MILL': 20,
      'AIQS': 10,
    };
    
    state.load.forEach(loadItem => {
      if (loadItem.loadId && loadItem.loadType) {
        const existingHistory = historyMap.get(loadItem.loadId) || {
          workpieceId: loadItem.loadId,
          workpieceType: loadItem.loadType,
          events: [],
          currentLocation: state.lastNodeId,
          currentState: 'IN_TRANSPORT',
          orders: this.generateOrderContext(loadItem.loadType),
        };
        
        // Determine order type based on location
        const orderType = this.determineOrderType(state.lastNodeId, existingHistory.events);
        
        // Get station info
        const stationName = stationNames[state.lastNodeId];
        const isStation = ['SVR4H76449', 'SVR3QA2098', 'SVR4H76530'].includes(state.lastNodeId);
        const processDuration = stationName ? processDurations[stationName] : undefined;
        
        // Check if location changed to generate proper station events
        const lastEvent = existingHistory.events[existingHistory.events.length - 1];
        if (!lastEvent || lastEvent.location !== state.lastNodeId) {
          const baseEvent = {
            timestamp: state.timestamp,
            workpieceId: loadItem.loadId,
            workpieceType: loadItem.loadType,
            location: state.lastNodeId,
            orderId: state.orderId,
            orderType: orderType,
            stationId: stationName || undefined,
            stationName: stationName ? this.getStationDisplayName(stationName) : undefined,
          };
          
          if (isStation && orderType === 'PRODUCTION') {
            // Generate PICK -> PROCESS -> DROP sequence for manufacturing stations
            // PICK event
            existingHistory.events.push({
              ...baseEvent,
              eventType: 'PICK',
              timestamp: state.timestamp,
              details: { actionState: 'FINISHED', loadPosition: loadItem.loadPosition },
            });
            
            // PROCESS event (drilling, milling, etc.)
            const processTime = new Date(new Date(state.timestamp).getTime() + 1000);
            existingHistory.events.push({
              ...baseEvent,
              eventType: 'PROCESS',
              timestamp: processTime.toISOString(),
              processDuration: processDuration,
              details: { 
                actionState: 'FINISHED', 
                loadPosition: loadItem.loadPosition,
                processType: stationName,
              },
            });
            
            // DROP event
            const dropTime = new Date(processTime.getTime() + (processDuration || 10) * 1000);
            existingHistory.events.push({
              ...baseEvent,
              eventType: 'DROP',
              timestamp: dropTime.toISOString(),
              details: { actionState: 'FINISHED', loadPosition: loadItem.loadPosition },
            });
          } else {
            // Regular event for transport/storage
            existingHistory.events.push({
              ...baseEvent,
              eventType: state.actionState.command,
              details: {
                actionState: state.actionState.state,
                loadPosition: loadItem.loadPosition,
              },
            });
          }
        }
        
        existingHistory.currentLocation = state.lastNodeId;
        historyMap.set(loadItem.loadId, existingHistory);
      }
    });
    
    this.workpieceHistorySubject.next(historyMap);
  }
  
  /** Get human-readable station display name */
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
  
  /** Generate order context with fake ERP IDs */
  private generateOrderContext(workpieceType: string): OrderContext[] {
    return [
      {
        orderId: `storage-${workpieceType.toLowerCase()}-${Date.now()}`,
        orderType: 'STORAGE',
        purchaseOrderId: generatePurchaseOrderId(),
        fromLocation: 'SVR4H73275', // DPS
        toLocation: 'SVR3QA0022',   // HBW
        startTime: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
      },
      {
        orderId: `production-${workpieceType.toLowerCase()}-${Date.now()}`,
        orderType: 'PRODUCTION',
        customerOrderId: generateCustomerOrderId(),
        fromLocation: 'SVR3QA0022', // HBW
        toLocation: 'SVR4H73275',   // DPS
        startTime: new Date().toISOString(),
      },
    ];
  }
  
  /** Determine order type based on current location and event history */
  private determineOrderType(location: string, events: TrackTraceEvent[]): 'STORAGE' | 'PRODUCTION' {
    // If at DPS (destination) or coming from DPS, it's a storage order (raw material inbound)
    // If at HBW (source) or going through stations, it's a production order
    const dpsId = 'SVR4H73275';
    const hbwId = 'SVR3QA0022';
    
    // Check if we've been at HBW - if so, we're in production
    const wasAtHbw = events.some(e => e.location === hbwId);
    
    if (location === dpsId && !wasAtHbw) {
      return 'STORAGE';
    }
    
    return wasAtHbw ? 'PRODUCTION' : 'STORAGE';
  }
  
  /** Reset simulation to initial state */
  resetSimulation(): void {
    this.simulationIndex = 0;
    this.ftsStateSubject.next(this.createInitialState());
    this.workpieceHistorySubject.next(new Map());
  }
}
