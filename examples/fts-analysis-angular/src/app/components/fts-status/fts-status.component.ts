import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FtsState, FtsActionState, getActionStateClass } from '../../models/fts.types';

/** Serial number to module name mapping */
const MODULE_NAME_MAP: Record<string, { short: string; full: string }> = {
  'SVR3QA0022': { short: 'HBW', full: 'HBW (High Bay Warehouse)' },
  'SVR3QA2098': { short: 'MILL', full: 'MILL Station' },
  'SVR4H76449': { short: 'DRILL', full: 'DRILL Station' },
  'SVR4H76530': { short: 'AIQS', full: 'AIQS (Quality Inspection)' },
  'SVR4H73275': { short: 'DPS', full: 'DPS (Processing Station)' },
  'CHRG0': { short: 'CHRG', full: 'CHRG (Charging Station)' },
  '1': { short: 'INT-1', full: 'Intersection 1' },
  '2': { short: 'INT-2', full: 'Intersection 2' },
  '3': { short: 'INT-3', full: 'Intersection 3' },
  '4': { short: 'INT-4', full: 'Intersection 4' },
};

/**
 * FTS Status Component
 * Displays overall FTS status including position, action state, and driving status
 */
@Component({
  selector: 'app-fts-status',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './fts-status.component.html',
  styleUrls: ['./fts-status.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FtsStatusComponent {
  @Input() ftsState: FtsState | null = null;
  
  get serialNumber(): string {
    return this.ftsState?.serialNumber ?? 'Unknown';
  }
  
  get lastNodeId(): string {
    return this.ftsState?.lastNodeId ?? 'Unknown';
  }
  
  /** Get module name from serial number */
  get locationName(): string {
    const nodeId = this.ftsState?.lastNodeId;
    if (!nodeId) return 'Unknown';
    return MODULE_NAME_MAP[nodeId]?.full ?? nodeId;
  }
  
  /** Get short module name from serial number */
  get locationShortName(): string {
    const nodeId = this.ftsState?.lastNodeId;
    if (!nodeId) return 'Unknown';
    return MODULE_NAME_MAP[nodeId]?.short ?? nodeId;
  }
  
  get isDriving(): boolean {
    return this.ftsState?.driving ?? false;
  }
  
  get isPaused(): boolean {
    return this.ftsState?.paused ?? false;
  }
  
  get isWaitingForLoad(): boolean {
    return this.ftsState?.waitingForLoadHandling ?? false;
  }
  
  get currentAction(): FtsActionState | null {
    return this.ftsState?.actionState ?? null;
  }
  
  get recentActions(): FtsActionState[] {
    return this.ftsState?.actionStates?.slice(-5) ?? [];
  }
  
  get orderId(): string {
    const id = this.ftsState?.orderId;
    if (!id) return 'None';
    // Truncate UUID for display
    return id.length > 8 ? `${id.substring(0, 8)}...` : id;
  }
  
  get lastUpdate(): string {
    const timestamp = this.ftsState?.timestamp;
    if (!timestamp) return 'Unknown';
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  }
  
  getStateClass(state: string): string {
    return getActionStateClass(state);
  }
  
  formatTimestamp(timestamp: string): string {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  }
  
  trackByActionId(_index: number, action: FtsActionState): string {
    return action.id;
  }
}
