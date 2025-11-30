import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable, map } from 'rxjs';
import { FtsMockService } from '../../services/fts-mock.service';
import { WorkpieceHistory, TrackTraceEvent } from '../../models/fts.types';

/**
 * Track & Trace Component
 * Enables workpiece-based tracking through the entire production process
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
  
  formatTimestamp(timestamp: string): string {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  }
  
  getLocationLabel(location: string): string {
    const labels: Record<string, string> = {
      'SVR3QA0022': 'HBW (High-Bay Warehouse)',
      'SVR4H76449': 'DRILL Station',
      'SVR3QA2098': 'MILL Station',
      'SVR4H76530': 'AIQS (Quality Inspection)',
      'SVR4H73275': 'DPS (Processing Station)',
      '1': 'Navigation Node 1',
      '2': 'Navigation Node 2',
      '3': 'Navigation Node 3',
    };
    return labels[location] || location;
  }
  
  trackByWorkpieceId(_index: number, workpiece: WorkpieceHistory): string {
    return workpiece.workpieceId;
  }
  
  trackByEventTimestamp(_index: number, event: TrackTraceEvent): string {
    return event.timestamp;
  }
}
