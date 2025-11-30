import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FtsState, FtsActionState, getActionStateClass } from '../../models/fts.types';

/** Node positions for visualization (simplified shopfloor layout) */
const NODE_POSITIONS: Record<string, { x: number; y: number; label: string }> = {
  'SVR3QA0022': { x: 50, y: 50, label: 'HBW' },
  '1': { x: 150, y: 50, label: 'Node 1' },
  '2': { x: 150, y: 150, label: 'Node 2' },
  '3': { x: 250, y: 50, label: 'Node 3' },
  'SVR4H76449': { x: 350, y: 50, label: 'DRILL' },
  'SVR3QA2098': { x: 50, y: 150, label: 'MILL' },
  'SVR4H76530': { x: 250, y: 150, label: 'AIQS' },
  'SVR4H73275': { x: 350, y: 150, label: 'DPS' },
};

/**
 * FTS Route Component
 * Visualizes the current FTS position and recent route on a simplified shopfloor map
 */
@Component({
  selector: 'app-fts-route',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './fts-route.component.html',
  styleUrls: ['./fts-route.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FtsRouteComponent {
  @Input() ftsState: FtsState | null = null;
  
  readonly nodePositions = NODE_POSITIONS;
  readonly nodes = Object.entries(NODE_POSITIONS).map(([id, pos]) => ({ id, ...pos }));
  
  get currentNodeId(): string {
    return this.ftsState?.lastNodeId ?? '';
  }
  
  get isDriving(): boolean {
    return this.ftsState?.driving ?? false;
  }
  
  get currentPosition(): { x: number; y: number } | null {
    const nodeId = this.currentNodeId;
    if (!nodeId || !NODE_POSITIONS[nodeId]) return null;
    return NODE_POSITIONS[nodeId];
  }
  
  get actionStates(): FtsActionState[] {
    return this.ftsState?.actionStates ?? [];
  }
  
  isCurrentNode(nodeId: string): boolean {
    return this.currentNodeId === nodeId;
  }
  
  getNodeClass(nodeId: string): string {
    if (this.isCurrentNode(nodeId)) {
      return this.isDriving ? 'current driving' : 'current';
    }
    return '';
  }
  
  getStateClass(state: string): string {
    return getActionStateClass(state);
  }
}
