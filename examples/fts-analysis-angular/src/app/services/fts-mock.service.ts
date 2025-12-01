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
    // Simulated state transitions based on real production data
    return [
      // Initial idle at HBW
      {
        lastNodeId: 'SVR3QA0022',
        driving: false,
        batteryState: { currentVoltage: 9.1, minVolt: 7.84, maxVolt: 9.1, percentage: 100, charging: false },
        actionState: { id: 'a1', command: 'DOCK', state: 'FINISHED', timestamp: new Date().toISOString() },
        load: [{ loadId: null, loadType: null, loadPosition: '1' }],
      },
      // Starting DOCK action - waiting
      {
        lastNodeId: 'SVR3QA0022',
        driving: false,
        batteryState: { currentVoltage: 9.1, minVolt: 7.84, maxVolt: 9.1, percentage: 100, charging: false },
        actionState: { id: 'a2', command: 'DOCK', state: 'WAITING', timestamp: new Date().toISOString() },
        load: [{ loadId: null, loadType: null, loadPosition: '1' }],
      },
      // DOCK action - initializing
      {
        lastNodeId: 'SVR3QA0022',
        driving: true,
        batteryState: { currentVoltage: 9.1, minVolt: 7.84, maxVolt: 9.1, percentage: 100, charging: false },
        actionState: { id: 'a2', command: 'DOCK', state: 'INITIALIZING', timestamp: new Date().toISOString() },
        load: [{ loadId: null, loadType: null, loadPosition: '1' }],
      },
      // DOCK action - running
      {
        lastNodeId: 'SVR3QA0022',
        driving: true,
        batteryState: { currentVoltage: 9.1, minVolt: 7.84, maxVolt: 9.1, percentage: 100, charging: false },
        actionState: { id: 'a2', command: 'DOCK', state: 'RUNNING', timestamp: new Date().toISOString() },
        load: [{ loadId: null, loadType: null, loadPosition: '1' }],
      },
      // DOCK finished - picked up BLUE workpiece
      {
        lastNodeId: 'SVR3QA0022',
        driving: false,
        waitingForLoadHandling: true,
        batteryState: { currentVoltage: 9.0, minVolt: 7.84, maxVolt: 9.1, percentage: 92, charging: false },
        actionState: { id: 'a2', command: 'DOCK', state: 'FINISHED', timestamp: new Date().toISOString() },
        load: [{ loadId: null, loadType: 'BLUE', loadPosition: '1' }],
      },
      // Load handling complete - workpiece ID assigned
      {
        lastNodeId: 'SVR3QA0022',
        driving: false,
        waitingForLoadHandling: false,
        batteryState: { currentVoltage: 9.1, minVolt: 7.84, maxVolt: 9.1, percentage: 100, charging: false },
        actionState: { id: 'a2', command: 'DOCK', state: 'FINISHED', timestamp: new Date().toISOString() },
        load: [{ loadId: '047389ca341291', loadType: 'BLUE', loadPosition: '1' }],
      },
      // Second DOCK - picking WHITE
      {
        lastNodeId: 'SVR3QA0022',
        driving: true,
        batteryState: { currentVoltage: 9.0, minVolt: 7.84, maxVolt: 9.1, percentage: 92, charging: false },
        actionState: { id: 'a3', command: 'DOCK', state: 'RUNNING', timestamp: new Date().toISOString() },
        load: [{ loadId: '047389ca341291', loadType: 'BLUE', loadPosition: '1' }],
      },
      // Second DOCK finished - added WHITE workpiece
      {
        lastNodeId: 'SVR3QA0022',
        driving: false,
        waitingForLoadHandling: true,
        batteryState: { currentVoltage: 9.0, minVolt: 7.84, maxVolt: 9.1, percentage: 92, charging: false },
        actionState: { id: 'a3', command: 'DOCK', state: 'FINISHED', timestamp: new Date().toISOString() },
        load: [
          { loadId: '047389ca341291', loadType: 'BLUE', loadPosition: '1' },
          { loadId: null, loadType: 'WHITE', loadPosition: '2' },
        ],
      },
      // Third DOCK - picking RED
      {
        lastNodeId: 'SVR3QA0022',
        driving: true,
        batteryState: { currentVoltage: 9.0, minVolt: 7.84, maxVolt: 9.1, percentage: 92, charging: false },
        actionState: { id: 'a4', command: 'DOCK', state: 'RUNNING', timestamp: new Date().toISOString() },
        load: [
          { loadId: '047389ca341291', loadType: 'BLUE', loadPosition: '1' },
          { loadId: '04798eca341290', loadType: 'WHITE', loadPosition: '2' },
        ],
      },
      // All three workpieces loaded
      {
        lastNodeId: 'SVR3QA0022',
        driving: false,
        batteryState: { currentVoltage: 9.0, minVolt: 7.84, maxVolt: 9.1, percentage: 92, charging: false },
        actionState: { id: 'a4', command: 'DOCK', state: 'FINISHED', timestamp: new Date().toISOString() },
        load: [
          { loadId: '047389ca341291', loadType: 'BLUE', loadPosition: '1' },
          { loadId: '04798eca341290', loadType: 'WHITE', loadPosition: '2' },
          { loadId: '040a8dca341291', loadType: 'RED', loadPosition: '3' },
        ],
      },
      // TURN action at node 1
      {
        lastNodeId: '1',
        driving: true,
        batteryState: { currentVoltage: 9.0, minVolt: 7.84, maxVolt: 9.1, percentage: 92, charging: false },
        actionState: { id: 'a5', command: 'TURN', state: 'RUNNING', timestamp: new Date().toISOString() },
        load: [
          { loadId: '047389ca341291', loadType: 'BLUE', loadPosition: '1' },
          { loadId: '04798eca341290', loadType: 'WHITE', loadPosition: '2' },
          { loadId: '040a8dca341291', loadType: 'RED', loadPosition: '3' },
        ],
      },
      // TURN finished
      {
        lastNodeId: '1',
        driving: true,
        batteryState: { currentVoltage: 9.0, minVolt: 7.84, maxVolt: 9.1, percentage: 92, charging: false },
        actionState: { id: 'a5', command: 'TURN', state: 'FINISHED', timestamp: new Date().toISOString() },
        load: [
          { loadId: '047389ca341291', loadType: 'BLUE', loadPosition: '1' },
          { loadId: '04798eca341290', loadType: 'WHITE', loadPosition: '2' },
          { loadId: '040a8dca341291', loadType: 'RED', loadPosition: '3' },
        ],
      },
      // Arrived at DRILL station
      {
        lastNodeId: 'SVR4H76449',
        driving: false,
        batteryState: { currentVoltage: 8.9, minVolt: 7.84, maxVolt: 9.1, percentage: 84, charging: false },
        actionState: { id: 'a6', command: 'DOCK', state: 'FINISHED', timestamp: new Date().toISOString() },
        load: [
          { loadId: '047389ca341291', loadType: 'BLUE', loadPosition: '1' },
          { loadId: '04798eca341290', loadType: 'WHITE', loadPosition: '2' },
          { loadId: '040a8dca341291', loadType: 'RED', loadPosition: '3' },
        ],
      },
      // At MILL station - dropped BLUE
      {
        lastNodeId: 'SVR3QA2098',
        driving: false,
        batteryState: { currentVoltage: 8.8, minVolt: 7.84, maxVolt: 9.1, percentage: 76, charging: false },
        actionState: { id: 'a7', command: 'DOCK', state: 'FINISHED', timestamp: new Date().toISOString() },
        load: [
          { loadId: null, loadType: null, loadPosition: '1' },
          { loadId: '04798eca341290', loadType: 'WHITE', loadPosition: '2' },
          { loadId: '040a8dca341291', loadType: 'RED', loadPosition: '3' },
        ],
      },
      // At AIQS - inspection
      {
        lastNodeId: 'SVR4H76530',
        driving: false,
        batteryState: { currentVoltage: 8.7, minVolt: 7.84, maxVolt: 9.1, percentage: 68, charging: false },
        actionState: { id: 'a8', command: 'DOCK', state: 'FINISHED', timestamp: new Date().toISOString() },
        load: [
          { loadId: '047c8bca341291', loadType: 'WHITE', loadPosition: '1' },
          { loadId: null, loadType: null, loadPosition: '2' },
          { loadId: null, loadType: null, loadPosition: '3' },
        ],
      },
      // At DPS - storage
      {
        lastNodeId: 'SVR4H73275',
        driving: false,
        batteryState: { currentVoltage: 8.9, minVolt: 7.84, maxVolt: 9.1, percentage: 84, charging: false },
        actionState: { id: 'a9', command: 'DOCK', state: 'FINISHED', timestamp: new Date().toISOString() },
        load: [
          { loadId: null, loadType: null, loadPosition: '1' },
          { loadId: null, loadType: null, loadPosition: '2' },
          { loadId: null, loadType: null, loadPosition: '3' },
        ],
      },
    ];
  }
  
  private startSimulation(): void {
    // Update state every 2 seconds
    this.simulationSubscription = interval(2000).subscribe(() => {
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
        // DPS -> HBW is STORAGE order (raw material)
        // HBW -> Stations -> DPS is PRODUCTION order
        const orderType = this.determineOrderType(state.lastNodeId, existingHistory.events);
        
        // Add event if location changed
        const lastEvent = existingHistory.events[existingHistory.events.length - 1];
        if (!lastEvent || lastEvent.location !== state.lastNodeId) {
          existingHistory.events.push({
            timestamp: state.timestamp,
            eventType: state.actionState.command,
            workpieceId: loadItem.loadId,
            workpieceType: loadItem.loadType,
            location: state.lastNodeId,
            orderId: state.orderId,
            orderType: orderType,
            details: {
              actionState: state.actionState.state,
              loadPosition: loadItem.loadPosition,
            },
          });
        }
        
        existingHistory.currentLocation = state.lastNodeId;
        historyMap.set(loadItem.loadId, existingHistory);
      }
    });
    
    this.workpieceHistorySubject.next(historyMap);
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
