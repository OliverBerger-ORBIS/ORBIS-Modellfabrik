import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FtsLoadInfo } from '../../models/fts.types';

/**
 * FTS Loads Component
 * Displays information about workpieces currently loaded on the FTS
 */
@Component({
  selector: 'app-fts-loads',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './fts-loads.component.html',
  styleUrls: ['./fts-loads.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FtsLoadsComponent {
  @Input() loads: FtsLoadInfo[] = [];
  
  get loadedCount(): number {
    return this.loads.filter(l => l.loadType !== null).length;
  }
  
  get totalPositions(): number {
    return this.loads.length;
  }
  
  getLoadTypeClass(loadType: string | null): string {
    if (!loadType) return '';
    return loadType.toLowerCase();
  }
  
  getLoadDisplay(load: FtsLoadInfo): string {
    if (!load.loadType) return 'Empty';
    return load.loadType;
  }
  
  getLoadIdDisplay(load: FtsLoadInfo): string {
    if (!load.loadId) return 'No ID';
    // Truncate long IDs for display
    return load.loadId.length > 12 ? `${load.loadId.substring(0, 12)}...` : load.loadId;
  }
}
