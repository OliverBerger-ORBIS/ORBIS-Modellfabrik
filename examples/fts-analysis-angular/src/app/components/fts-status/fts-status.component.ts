import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FtsState, FtsActionState, getActionStateClass } from '../../models/fts.types';

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
