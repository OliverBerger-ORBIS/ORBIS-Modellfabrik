import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FtsState, FtsActionState, getActionStateClass } from '../../models/fts.types';

/**
 * Node positions based on actual shopfloor layout from omf3/apps/ccu-ui/public/shopfloor/shopfloor_layout.json
 * 
 * Shopfloor Layout (800x600 canvas):
 * Row 0: ORBIS (0,0) | MILL (200,0) | AIQS (400,0) | DSP (600,0)
 * Row 1: HBW (0,100) | INT-1 (200,200) | INT-2 (400,200) | DPS (600,100)
 * Row 2: DRILL (0,400) | INT-3 (200,400) | INT-4 (400,400) | CHRG (600,400)
 * 
 * FTS Route Network (from parsed_roads):
 * - HBW (SVR3QA0022) -> intersection 1
 * - MILL (SVR3QA2098) -> intersection 1
 * - DRILL (SVR4H76449) -> intersection 3
 * - AIQS (SVR4H76530) -> intersection 2
 * - DPS (SVR4H73275) -> intersection 2
 * - CHRG (CHRG0) -> intersection 4
 * - intersection 1 <-> intersection 2
 * - intersection 3 <-> intersection 1
 * - intersection 3 <-> intersection 4
 * - intersection 4 <-> intersection 2
 */
const NODE_POSITIONS: Record<string, { x: number; y: number; label: string; isModule: boolean }> = {
  // Modules (based on actual shopfloor layout positions - center points)
  'SVR3QA0022': { x: 100, y: 300, label: 'HBW', isModule: true },      // HBW main subcell center
  'SVR3QA2098': { x: 300, y: 100, label: 'MILL', isModule: true },     // MILL center
  'SVR4H76449': { x: 100, y: 500, label: 'DRILL', isModule: true },    // DRILL center
  'SVR4H76530': { x: 500, y: 100, label: 'AIQS', isModule: true },     // AIQS center
  'SVR4H73275': { x: 700, y: 300, label: 'DPS', isModule: true },      // DPS main subcell center
  'CHRG0': { x: 700, y: 500, label: 'CHRG', isModule: true },          // Charging station center
  
  // Intersections (navigation waypoints - center points from layout)
  '1': { x: 300, y: 300, label: '①', isModule: false },  // CELL_1_1 center
  '2': { x: 500, y: 300, label: '②', isModule: false },  // CELL_1_2 center
  '3': { x: 300, y: 500, label: '③', isModule: false },  // CELL_2_1 center
  '4': { x: 500, y: 500, label: '④', isModule: false },  // CELL_2_2 center
};

/** Edge connections between nodes (from parsed_roads in shopfloor_layout.json) */
const EDGES: Array<{ from: string; to: string }> = [
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

/**
 * FTS Route Component
 * Visualizes the current FTS position and recent route on a simplified shopfloor map
 */
@Component({
  selector: 'app-fts-route',
  standalone: true,
  imports: [CommonModule, DatePipe],
  templateUrl: './fts-route.component.html',
  styleUrls: ['./fts-route.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FtsRouteComponent {
  @Input() ftsState: FtsState | null = null;
  
  readonly nodePositions = NODE_POSITIONS;
  readonly nodes = Object.entries(NODE_POSITIONS).map(([id, pos]) => ({ id, ...pos }));
  readonly edges = EDGES;
  
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
  
  isModule(nodeId: string): boolean {
    return NODE_POSITIONS[nodeId]?.isModule ?? false;
  }
  
  getEdgeCoords(edge: { from: string; to: string }): { x1: number; y1: number; x2: number; y2: number } | null {
    const fromPos = NODE_POSITIONS[edge.from];
    const toPos = NODE_POSITIONS[edge.to];
    if (!fromPos || !toPos) return null;
    return { x1: fromPos.x, y1: fromPos.y, x2: toPos.x, y2: toPos.y };
  }
  
  getStateClass(state: string): string {
    return getActionStateClass(state);
  }
}
