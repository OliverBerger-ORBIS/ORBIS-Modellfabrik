import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable, map } from 'rxjs';
import { FtsMockService } from '../../services/fts-mock.service';
import { WorkpieceHistory, TrackTraceEvent, OrderContext, StationTaskGroup } from '../../models/fts.types';

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
export class TrackTraceComponent {
  private ftsService = inject(FtsMockService);
  
  searchTerm = '';
  selectedWorkpieceId: string | null = null;
  
  /** All tracked workpieces */
  workpieces$: Observable<WorkpieceHistory[]> = this.ftsService.workpieceHistory$.pipe(
    map(historyMap => Array.from(historyMap.values()))
  );
  
  /** Currently selected workpiece history */
  selectedHistory$: Observable<WorkpieceHistory | undefined> = this.ftsService.workpieceHistory$.pipe(
    map(historyMap => this.selectedWorkpieceId ? historyMap.get(this.selectedWorkpieceId) : undefined)
  );
  
  selectWorkpiece(workpieceId: string): void {
    this.selectedWorkpieceId = workpieceId;
  }
  
  clearSelection(): void {
    this.selectedWorkpieceId = null;
    this.searchTerm = '';
  }
  
  getTypeClass(type: string | undefined): string {
    if (!type) return '';
    return type.toLowerCase();
  }
  
  getEventIcon(eventType: string): string {
    switch (eventType.toUpperCase()) {
      case 'DOCK': return '🔗';
      case 'PICK': return '📤';
      case 'DROP': return '📥';
      case 'TURN': return '↩️';
      case 'PASS': return '➡️';
      case 'TRANSPORT': return '🚗';
      case 'PROCESS': return '⚙️';
      default: return '📌';
    }
  }
  
  getOrderTypeIcon(orderType: string | undefined): string {
    if (!orderType) return '📋';
    switch (orderType.toUpperCase()) {
      case 'STORAGE': return '📥';
      case 'PRODUCTION': return '🏭';
      default: return '📋';
    }
  }
  
  getOrderTypeLabel(orderType: string | undefined): string {
    if (!orderType) return 'Order';
    switch (orderType.toUpperCase()) {
      case 'STORAGE': return 'Storage Order (Raw Material)';
      case 'PRODUCTION': return 'Production Order';
      default: return orderType;
    }
  }
  
  getStationIcon(stationId: string | undefined): string {
    if (!stationId) return '🏭';
    switch (stationId.toUpperCase()) {
      case 'HBW': return '🏢';
      case 'DRILL': return '🔩';
      case 'MILL': return '⚙️';
      case 'AIQS': return '🔍';
      case 'DPS': return '📦';
      default: return '🏭';
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
    const labels: Record<string, string> = {
      'SVR3QA0022': 'HBW (High-Bay Warehouse)',
      'SVR4H76449': 'DRILL Station',
      'SVR3QA2098': 'MILL Station',
      'SVR4H76530': 'AIQS (Quality Inspection)',
      'SVR4H73275': 'DPS (Processing Station)',
      '1': 'Intersection ①',
      '2': 'Intersection ②',
      '3': 'Intersection ③',
      '4': 'Intersection ④',
    };
    return labels[location] || location;
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
          const order = history.orders?.find(o => o.orderType === currentOrderType) || null;
          const stationGroups = this.groupEventsByStation(currentGroup, currentOrderType);
          groups.push({ order, events: [...currentGroup], stationGroups });
        }
        currentOrderType = event.orderType;
        currentGroup = [event];
      } else {
        currentGroup.push(event);
      }
    }
    
    // Add last group
    if (currentGroup.length > 0) {
      const order = history.orders?.find(o => o.orderType === currentOrderType) || null;
      const stationGroups = this.groupEventsByStation(currentGroup, currentOrderType);
      groups.push({ order, events: currentGroup, stationGroups });
    }
    
    return groups;
  }
  
  /** Group production events by station (PICK → PROCESS → DROP) */
  private groupEventsByStation(events: TrackTraceEvent[], orderType: string | undefined): StationTaskGroup[] {
    if (orderType !== 'PRODUCTION') {
      return [];
    }
    
    const stationGroups: StationTaskGroup[] = [];
    let currentStation: string | undefined = undefined;
    let currentStationEvents: TrackTraceEvent[] = [];
    
    for (const event of events) {
      // Only group station events (PICK, PROCESS, DROP)
      if (event.stationId && ['PICK', 'PROCESS', 'DROP'].includes(event.eventType.toUpperCase())) {
        if (event.stationId !== currentStation) {
          // Save previous station group
          if (currentStation && currentStationEvents.length > 0) {
            stationGroups.push({
              stationId: currentStation,
              stationName: currentStationEvents[0]?.stationName || currentStation,
              events: [...currentStationEvents],
              startTime: currentStationEvents[0]?.timestamp,
              endTime: currentStationEvents[currentStationEvents.length - 1]?.timestamp,
            });
          }
          currentStation = event.stationId;
          currentStationEvents = [event];
        } else {
          currentStationEvents.push(event);
        }
      }
    }
    
    // Add last station group
    if (currentStation && currentStationEvents.length > 0) {
      stationGroups.push({
        stationId: currentStation,
        stationName: currentStationEvents[0]?.stationName || currentStation,
        events: [...currentStationEvents],
        startTime: currentStationEvents[0]?.timestamp,
        endTime: currentStationEvents[currentStationEvents.length - 1]?.timestamp,
      });
    }
    
    return stationGroups;
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
}
