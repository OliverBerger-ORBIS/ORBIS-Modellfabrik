import { Component, Input, ChangeDetectionStrategy, OnChanges, SimpleChanges, ChangeDetectorRef } from '@angular/core';
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

/** Graph structure for pathfinding */
const ADJACENCY: Record<string, string[]> = {};
EDGES.forEach(edge => {
  if (!ADJACENCY[edge.from]) ADJACENCY[edge.from] = [];
  if (!ADJACENCY[edge.to]) ADJACENCY[edge.to] = [];
  ADJACENCY[edge.from].push(edge.to);
  ADJACENCY[edge.to].push(edge.from);
});

/** Find shortest path between two nodes using BFS */
function findPath(from: string, to: string): string[] {
  if (from === to) return [from];
  
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
  
  return [from]; // No path found
}

/**
 * FTS Route Component
 * Visualizes the current FTS position and animated route on a simplified shopfloor map
 */
@Component({
  selector: 'app-fts-route',
  standalone: true,
  imports: [CommonModule, DatePipe],
  templateUrl: './fts-route.component.html',
  styleUrls: ['./fts-route.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FtsRouteComponent implements OnChanges {
  @Input() ftsState: FtsState | null = null;
  
  readonly nodePositions = NODE_POSITIONS;
  readonly nodes = Object.entries(NODE_POSITIONS).map(([id, pos]) => ({ id, ...pos }));
  readonly edges = EDGES;
  
  // Animation state
  private previousNodeId: string = '';
  private animationInterval: number | null = null;
  
  // Animated position
  animatedPosition: { x: number; y: number } | null = null;
  isAnimating = false;
  animationPath: string[] = [];
  
  constructor(private cdr: ChangeDetectorRef) {}
  
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['ftsState']) {
      const newNodeId = this.ftsState?.lastNodeId ?? '';
      const isDriving = this.ftsState?.driving ?? false;
      
      // If node changed and driving, animate along the path
      if (newNodeId && this.previousNodeId && newNodeId !== this.previousNodeId && isDriving) {
        this.startAnimation(this.previousNodeId, newNodeId);
      } else if (!isDriving) {
        // Stop animation when not driving
        this.stopAnimation();
        this.animatedPosition = null;
      }
      
      this.previousNodeId = newNodeId;
    }
  }
  
  private startAnimation(from: string, to: string): void {
    this.stopAnimation();
    
    // Find path between nodes
    this.animationPath = findPath(from, to);
    if (this.animationPath.length < 2) {
      return;
    }
    
    this.isAnimating = true;
    let animationProgress = 0;
    
    const totalSteps = (this.animationPath.length - 1) * 20; // 20 steps per segment
    let currentStep = 0;
    
    this.animationInterval = window.setInterval(() => {
      currentStep++;
      animationProgress = currentStep / totalSteps;
      
      if (currentStep >= totalSteps) {
        this.stopAnimation();
        this.animatedPosition = null;
        this.cdr.markForCheck();
        return;
      }
      
      // Calculate position along path
      const segmentIndex = Math.floor(animationProgress * (this.animationPath.length - 1));
      const segmentProgress = (animationProgress * (this.animationPath.length - 1)) - segmentIndex;
      
      const fromNode = this.animationPath[segmentIndex];
      const toNode = this.animationPath[Math.min(segmentIndex + 1, this.animationPath.length - 1)];
      
      const fromPos = NODE_POSITIONS[fromNode];
      const toPos = NODE_POSITIONS[toNode];
      
      if (fromPos && toPos) {
        this.animatedPosition = {
          x: fromPos.x + (toPos.x - fromPos.x) * segmentProgress,
          y: fromPos.y + (toPos.y - fromPos.y) * segmentProgress,
        };
        this.cdr.markForCheck();
      }
    }, 50); // 50ms per step = ~1 second per segment
  }
  
  private stopAnimation(): void {
    if (this.animationInterval) {
      window.clearInterval(this.animationInterval);
      this.animationInterval = null;
    }
    this.isAnimating = false;
    this.animationPath = [];
  }
  
  get currentNodeId(): string {
    return this.ftsState?.lastNodeId ?? '';
  }
  
  get isDriving(): boolean {
    return this.ftsState?.driving ?? false;
  }
  
  get currentPosition(): { x: number; y: number } | null {
    // Use animated position if animating
    if (this.animatedPosition && this.isAnimating) {
      return this.animatedPosition;
    }
    
    const nodeId = this.currentNodeId;
    if (!nodeId || !NODE_POSITIONS[nodeId]) return null;
    return NODE_POSITIONS[nodeId];
  }
  
  get activeRoutePath(): string[] {
    return this.animationPath;
  }
  
  get actionStates(): FtsActionState[] {
    return this.ftsState?.actionStates ?? [];
  }
  
  isCurrentNode(nodeId: string): boolean {
    return this.currentNodeId === nodeId;
  }
  
  isOnActivePath(nodeId: string): boolean {
    return this.animationPath.includes(nodeId);
  }
  
  getNodeClass(nodeId: string): string {
    if (this.isCurrentNode(nodeId)) {
      return this.isDriving ? 'current driving' : 'current';
    }
    if (this.isOnActivePath(nodeId)) {
      return 'on-path';
    }
    return '';
  }
  
  isActiveEdge(edge: { from: string; to: string }): boolean {
    if (this.animationPath.length < 2) return false;
    
    for (let i = 0; i < this.animationPath.length - 1; i++) {
      const a = this.animationPath[i];
      const b = this.animationPath[i + 1];
      if ((edge.from === a && edge.to === b) || (edge.from === b && edge.to === a)) {
        return true;
      }
    }
    return false;
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
