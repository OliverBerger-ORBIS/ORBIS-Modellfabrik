import { Component, ChangeDetectionStrategy, OnInit, OnDestroy, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable, map, Subscription, combineLatest, BehaviorSubject } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { WorkpieceHistoryService, WorkpieceHistory, TrackTraceEvent, OrderContext, StationTaskGroup } from '../../services/workpiece-history.service';
import { ModuleNameService } from '../../services/module-name.service';
import { EnvironmentService } from '../../services/environment.service';
import { ICONS } from '../../shared/icons/icon.registry';

/** Manufacturing event types that should be grouped by station */
const MANUFACTURING_EVENT_TYPES = ['PICK', 'PROCESS', 'DROP'] as const;

/**
 * Track & Trace Component
 * Enables workpiece-based tracking through the entire production process
 * Shows Order context (Storage Order vs Production Order) with ERP links
 * Groups manufacturing tasks by station (PICK → PROCESS → DROP)
 */
@Component({
  selector: 'app-track-trace',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './track-trace.component.html',
  styleUrls: ['./track-trace.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TrackTraceComponent implements OnInit, OnDestroy {
  private readonly workpieceHistoryService = inject(WorkpieceHistoryService);
  private readonly moduleNameService = inject(ModuleNameService);
  private readonly environmentService = inject(EnvironmentService);
  private readonly cdr = inject(ChangeDetectorRef);
  private subscription?: Subscription;

  searchTerm = '';
  selectedWorkpieceId: string | null = null;
  private readonly selectedWorkpieceId$ = new BehaviorSubject<string | null>(null);

  /** All tracked workpieces */
  workpieces$!: Observable<WorkpieceHistory[]>;

  /** Currently selected workpiece history */
  selectedHistory$!: Observable<WorkpieceHistory | undefined>;

  ngOnInit(): void {
    const environmentKey = this.environmentService.current.key;
    
    // Initialize tracking for current environment
    this.workpieceHistoryService.initialize(environmentKey);

    // Get all workpieces
    this.workpieces$ = this.workpieceHistoryService.getHistory$(environmentKey).pipe(
      map((historyMap) => Array.from(historyMap.values()))
    );

    // Get selected workpiece history - reactive to selectedWorkpieceId changes
    this.selectedHistory$ = combineLatest([
      this.workpieceHistoryService.getHistory$(environmentKey),
      this.selectedWorkpieceId$.asObservable()
    ]).pipe(
      map(([historyMap, selectedId]) => (selectedId ? historyMap.get(selectedId) : undefined)),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }

  selectWorkpiece(workpieceId: string): void {
    this.selectedWorkpieceId = workpieceId;
    this.selectedWorkpieceId$.next(workpieceId);
  }

  clearSelection(): void {
    this.selectedWorkpieceId = null;
    this.searchTerm = '';
    this.selectedWorkpieceId$.next(null);
  }

  getTypeClass(type: string | undefined): string {
    if (!type) return '';
    return type.toLowerCase();
  }

  getEventIcon(eventType: string, event?: TrackTraceEvent): string {
    // Return SVG path instead of emoji
    switch (eventType.toUpperCase()) {
      case 'DOCK':
        return ICONS.shopfloor.shared.dockEvent;
      case 'PICK':
        return ICONS.shopfloor.shared.pickEvent;
      case 'DROP':
        return ICONS.shopfloor.shared.dropEvent;
      case 'TURN':
        // Check for TURN LEFT or TURN RIGHT direction
        if (event?.details && 'direction' in event.details) {
          const dir = String(event.details['direction']).toUpperCase();
          if (dir === 'LEFT') return ICONS.shopfloor.shared.turnLeftEvent;
          if (dir === 'RIGHT') return ICONS.shopfloor.shared.turnRightEvent;
        }
        return ICONS.shopfloor.shared.turnEvent; // Fallback to generic turn icon
      case 'PASS':
        return ICONS.shopfloor.shared.passEvent;
      case 'TRANSPORT':
        return ICONS.shopfloor.shared.agvVehicle;
      case 'PROCESS':
        return ICONS.shopfloor.shared.processEvent;
      default:
        return ICONS.shopfloor.shared.locationMarker;
    }
  }
  
  getEventLabel(eventType: string, event?: TrackTraceEvent): string {
    if (eventType.toUpperCase() === 'TURN' && event?.details && 'direction' in event.details) {
      const dir = String(event.details['direction']).toUpperCase();
      if (dir === 'LEFT') return $localize`:@@ftsActionTurnLeft:TURN LEFT`;
      if (dir === 'RIGHT') return $localize`:@@ftsActionTurnRight:TURN RIGHT`;
    }
    return eventType;
  }

  getOrderTypeIcon(orderType: string | undefined): string {
    if (!orderType) return 'assets/svg/ui/heading-customer-orders.svg';
    switch (orderType.toUpperCase()) {
      case 'STORAGE':
        return 'assets/svg/ui/heading-storage.svg';
      case 'PRODUCTION':
        return 'assets/svg/ui/heading-production.svg';
      default:
        return 'assets/svg/ui/heading-customer-orders.svg';
    }
  }

  getOrderTypeLabel(orderType: string | undefined): string {
    if (!orderType) return $localize`:@@trackTraceOrder:Order`;
    switch (orderType.toUpperCase()) {
      case 'STORAGE':
        return $localize`:@@trackTraceStorageOrder:Storage Order (Raw Material)`;
      case 'PRODUCTION':
        return $localize`:@@trackTraceProductionOrder:Production Order`;
      default:
        return orderType;
    }
  }

  getStationIcon(stationId: string | undefined): string {
    if (!stationId) return ICONS.shopfloor.systems.factory;
    switch (stationId.toUpperCase()) {
      case 'HBW':
        return ICONS.shopfloor.stations.hbw;
      case 'DRILL':
        return ICONS.shopfloor.stations.drill;
      case 'MILL':
        return ICONS.shopfloor.stations.mill;
      case 'AIQS':
        return ICONS.shopfloor.stations.aiqs;
      case 'DPS':
        return ICONS.shopfloor.stations.dps;
      default:
        return ICONS.shopfloor.systems.factory;
    }
  }

  formatTimestamp(timestamp: string): string {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  }

  formatDuration(seconds: number | undefined): string {
    if (!seconds) return '';
    return `${seconds}s`;
  }

  getLocationLabel(location: string): string {
    const locationInfo = this.moduleNameService.getLocationDisplayText(location);
    if (locationInfo.serialId) {
      return `${locationInfo.moduleType} (${locationInfo.fullName}) (${locationInfo.serialId})`;
    }
    return `${locationInfo.moduleType} (${locationInfo.fullName})`;
  }

  getLocationInfo(location: string): { moduleType: string; fullName: string; serialId: string | null } {
    return this.moduleNameService.getLocationDisplayText(location);
  }

  getWorkpieceIcon(workpieceType: string): string {
    const type = workpieceType.toUpperCase();
    if (type === 'BLUE') return ICONS.shopfloor.workpieces.blue.dim3;
    if (type === 'WHITE') return ICONS.shopfloor.workpieces.white.dim3;
    if (type === 'RED') return ICONS.shopfloor.workpieces.red.dim3;
    return ICONS.shopfloor.workpieces.slotEmpty;
  }

  /** Group events by order context */
  groupEventsByOrder(history: WorkpieceHistory): { order: OrderContext | null; events: TrackTraceEvent[]; stationGroups: StationTaskGroup[] }[] {
    if (!history.orders || history.orders.length === 0) {
      return [{ order: null, events: history.events, stationGroups: [] }];
    }

    const groups: { order: OrderContext | null; events: TrackTraceEvent[]; stationGroups: StationTaskGroup[] }[] = [];

    // Group events by order type
    let currentOrderType: string | undefined = undefined;
    let currentGroup: TrackTraceEvent[] = [];

    for (const event of history.events) {
      if (event.orderType !== currentOrderType) {
        if (currentGroup.length > 0) {
          const order = history.orders?.find((o) => o.orderType === currentOrderType) || null;
          const stationGroups = this.groupEventsByStation(currentGroup, currentOrderType);
          
          // All events are shown (both station and non-station events)
          // The grouping by Sub-Order-ID will handle the separation
          groups.push({ order, events: currentGroup, stationGroups });
        }
        currentOrderType = event.orderType;
        currentGroup = [event];
      } else {
        currentGroup.push(event);
      }
    }

    // Add last group
    if (currentGroup.length > 0) {
      const order = history.orders?.find((o) => o.orderType === currentOrderType) || null;
      const stationGroups = this.groupEventsByStation(currentGroup, currentOrderType);
      
      // All events are shown (both station and non-station events)
      // The grouping by Sub-Order-ID will handle the separation
      groups.push({ order, events: currentGroup, stationGroups });
    }

    return groups;
  }

  /** Group production events by station (PICK → PROCESS → DROP)
   * Includes all modules: MILL, DRILL, AIQS, HBW, DPS
   */
  private groupEventsByStation(events: TrackTraceEvent[], orderType: string | undefined): StationTaskGroup[] {
    if (orderType !== 'PRODUCTION') {
      return [];
    }

    // First, group events by subOrderId
    const eventsBySubOrder = new Map<string, TrackTraceEvent[]>();
    
    for (const event of events) {
      // Consider all module events (PICK, PROCESS, DROP) with stationId
      // Includes: MILL, DRILL, AIQS, HBW, DPS
      if (
        event.stationId &&
        MANUFACTURING_EVENT_TYPES.includes(event.eventType.toUpperCase() as (typeof MANUFACTURING_EVENT_TYPES)[number])
      ) {
        const subOrderId = event.subOrderId || 'unknown';
        if (!eventsBySubOrder.has(subOrderId)) {
          eventsBySubOrder.set(subOrderId, []);
        }
        eventsBySubOrder.get(subOrderId)!.push(event);
      }
    }

    // Then, group by station (events with same subOrderId belong to same station)
    const stationGroups: StationTaskGroup[] = [];
    const stationMap = new Map<string, StationTaskGroup>();

    for (const [subOrderId, subOrderEvents] of eventsBySubOrder.entries()) {
      if (subOrderEvents.length === 0) continue;

      // All events with same subOrderId belong to the same station
      const firstEvent = subOrderEvents[0];
      const stationId = firstEvent.stationId || 'UNKNOWN';
      const stationName = firstEvent.stationName || stationId;

      // Get or create station group
      if (!stationMap.has(stationId)) {
        const stationGroup: StationTaskGroup = {
          stationId,
          stationName,
          events: [],
          startTime: undefined,
          endTime: undefined,
          duration: undefined,
        };
        stationMap.set(stationId, stationGroup);
        stationGroups.push(stationGroup);
      }

      // Add all events from this subOrder to the station group
      const stationGroup = stationMap.get(stationId)!;
      stationGroup.events.push(...subOrderEvents);
    }

    // Sort events within each station group by timestamp
    // Calculate duration for each station group
    for (const stationGroup of stationGroups) {
      stationGroup.events.sort((a, b) => {
        return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      });

      if (stationGroup.events.length > 0) {
        stationGroup.startTime = stationGroup.events[0]?.timestamp;
        stationGroup.endTime = stationGroup.events[stationGroup.events.length - 1]?.timestamp;
        if (stationGroup.startTime && stationGroup.endTime) {
          stationGroup.duration = this.calculateDuration(stationGroup.startTime, stationGroup.endTime);
        }
      }
    }

    // Sort station groups by start time
    stationGroups.sort((a, b) => {
      if (!a.startTime || !b.startTime) return 0;
      return new Date(a.startTime).getTime() - new Date(b.startTime).getTime();
    });

    return stationGroups;
  }

  /**
   * Calculate duration in seconds between two timestamps
   */
  private calculateDuration(startTime: string, endTime: string): number {
    try {
      const start = new Date(startTime).getTime();
      const end = new Date(endTime).getTime();
      return Math.round((end - start) / 1000);
    } catch {
      return 0;
    }
  }

  formatStationDuration(seconds: number | undefined): string {
    if (!seconds) return '';
    if (seconds < 60) {
      return `${seconds}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  }

  trackByWorkpieceId(_index: number, workpiece: WorkpieceHistory): string {
    return workpiece.workpieceId;
  }

  trackByEvent(index: number, event: TrackTraceEvent): string {
    // Use combination of timestamp and index for unique tracking
    return `${event.timestamp}-${index}`;
  }

  trackByOrder(index: number, group: { order: OrderContext | null; events: TrackTraceEvent[] }): string {
    return group.order?.orderId || `group-${index}`;
  }

  trackByStation(index: number, station: StationTaskGroup): string {
    return `${station.stationId}-${index}`;
  }

  trackBySubOrderGroup(index: number, group: { subOrderId: string; moduleId?: string; moduleName?: string; events: TrackTraceEvent[] }): string {
    return group.subOrderId || `group-${index}`;
  }

  /**
   * Group events by Sub-Order-ID and Module
   * Events with same Sub-Order-ID are grouped under their module
   * Other events are listed separately
   * IMPORTANT: ALL events must be included, no filtering!
   */
  groupEventsBySubOrder(
    events: TrackTraceEvent[],
    stationGroups: StationTaskGroup[]
  ): Array<{ subOrderId: string; moduleId?: string; moduleName?: string; events: TrackTraceEvent[] }> {
    // Build map of Sub-Order-ID to Module from station groups
    const subOrderToModule = new Map<string, { moduleId: string; moduleName: string }>();
    stationGroups.forEach((station) => {
      station.events.forEach((event) => {
        if (event.subOrderId) {
          subOrderToModule.set(event.subOrderId, {
            moduleId: station.stationId,
            moduleName: station.stationName,
          });
        }
      });
    });

    // Group ALL events by Sub-Order-ID (including events without subOrderId)
    const eventsBySubOrder = new Map<string, TrackTraceEvent[]>();
    const eventsWithoutSubOrder: TrackTraceEvent[] = [];
    
    events.forEach((event) => {
      if (event.subOrderId) {
        const subOrderId = event.subOrderId;
        if (!eventsBySubOrder.has(subOrderId)) {
          eventsBySubOrder.set(subOrderId, []);
        }
        eventsBySubOrder.get(subOrderId)!.push(event);
      } else {
        // Events without subOrderId go to a special group
        eventsWithoutSubOrder.push(event);
      }
    });

    // Build result groups
    const groups: Array<{ subOrderId: string; moduleId?: string; moduleName?: string; events: TrackTraceEvent[] }> = [];

    // First, add module-grouped events (sorted by timestamp, then subOrderId, then actionId)
    const moduleGroups: Array<{ subOrderId: string; moduleId: string; moduleName: string; events: TrackTraceEvent[] }> = [];
    eventsBySubOrder.forEach((eventList, subOrderId) => {
      const moduleInfo = subOrderToModule.get(subOrderId);
      if (moduleInfo) {
        // Sort events: timestamp first, then subOrderId, then actionId
        eventList.sort((a, b) => {
          const timeDiff = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
          if (timeDiff !== 0) return timeDiff;
          
          const subOrderDiff = (a.subOrderId || '').localeCompare(b.subOrderId || '');
          if (subOrderDiff !== 0) return subOrderDiff;
          
          return (a.actionId || '').localeCompare(b.actionId || '');
        });
        moduleGroups.push({
          subOrderId,
          moduleId: moduleInfo.moduleId,
          moduleName: moduleInfo.moduleName,
          events: eventList,
        });
      }
    });

    // Collect all groups (module groups + other events) and sort them together by Sub-Order-ID
    // This ensures that FTS events are interleaved correctly with module groups
    const allGroups: Array<{ subOrderId: string; moduleId?: string; moduleName?: string; events: TrackTraceEvent[] }> = [];
    
    // Add module groups
    moduleGroups.forEach(group => {
      allGroups.push(group);
    });
    
    // Add other events with Sub-Order-ID but no module assignment
    eventsBySubOrder.forEach((eventList, subOrderId) => {
      if (!subOrderToModule.has(subOrderId)) {
        // Sort events: timestamp first, then subOrderId, then actionId
        eventList.sort((a, b) => {
          const timeDiff = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
          if (timeDiff !== 0) return timeDiff;
          
          const subOrderDiff = (a.subOrderId || '').localeCompare(b.subOrderId || '');
          if (subOrderDiff !== 0) return subOrderDiff;
          
          return (a.actionId || '').localeCompare(b.actionId || '');
        });
        allGroups.push({
          subOrderId,
          events: eventList,
        });
      }
    });
    
    // Sort ALL groups together by Sub-Order-ID (extract numeric part after last '-')
    // Format: orderId-1, orderId-2, etc. -> sort by numeric part (1, 2, 3...)
    // This ensures correct sequence: Sub-Order-ID -1, -2, -3, etc.
    allGroups.sort((a, b) => {
      const numA = this.extractSubOrderNumber(a.subOrderId);
      const numB = this.extractSubOrderNumber(b.subOrderId);
      if (numA !== null && numB !== null) {
        return numA - numB; // Numeric sort
      }
      // Fallback to string comparison if numeric extraction fails
      return (a.subOrderId || '').localeCompare(b.subOrderId || '');
    });
    
    groups.push(...allGroups);

    // Finally, add events without Sub-Order-ID (sorted by timestamp, then actionId)
    if (eventsWithoutSubOrder.length > 0) {
      eventsWithoutSubOrder.sort((a, b) => {
        const timeDiff = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
        if (timeDiff !== 0) return timeDiff;
        return (a.actionId || '').localeCompare(b.actionId || '');
      });
      groups.push({
        subOrderId: 'no-sub-order',
        events: eventsWithoutSubOrder,
      });
    }

    return groups;
  }

  /**
   * Extract numeric part from Sub-Order-ID
   * Format: "orderId-1" -> 1, "orderId-10" -> 10
   * Returns null if extraction fails
   */
  private extractSubOrderNumber(subOrderId: string | undefined): number | null {
    if (!subOrderId) return null;
    
    // Extract number after last '-'
    const parts = subOrderId.split('-');
    if (parts.length < 2) return null;
    
    const lastPart = parts[parts.length - 1];
    const num = parseInt(lastPart, 10);
    
    return isNaN(num) ? null : num;
  }

}

