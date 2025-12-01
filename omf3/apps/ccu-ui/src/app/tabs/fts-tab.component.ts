import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { filter, map, shareReplay, startWith, switchMap, catchError, tap, debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { Observable, Subscription, of, combineLatest, BehaviorSubject } from 'rxjs';
import { EnvironmentService } from '../services/environment.service';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ConnectionService } from '../services/connection.service';
import { ModuleNameService } from '../services/module-name.service';
import { FtsRouteService } from '../services/fts-route.service';
import { FtsAnimationService, type AnimationState } from '../services/fts-animation.service';
import { ShopfloorPreviewComponent } from '../components/shopfloor-preview/shopfloor-preview.component';
import { getDashboardController } from '../mock-dashboard';
import type { OrderFixtureName } from '@omf3/testing-fixtures';
import type { ShopfloorLayoutConfig, ShopfloorPoint, ParsedRoad, ShopfloorCellConfig, ShopfloorRoadEndpoint } from '../components/shopfloor-preview/shopfloor-layout.types';

// FTS Types (from example app - will be moved to @omf3/entities later)
interface FtsBatteryState {
  currentVoltage: number;
  minVolt: number;
  maxVolt: number;
  percentage: number;
  charging: boolean;
}

type ActionStateType = 'WAITING' | 'INITIALIZING' | 'RUNNING' | 'FINISHED' | 'FAILED' | string;
type ActionCommandType = 'DOCK' | 'TURN' | 'PASS' | 'PICK' | 'DROP' | 'clearLoadHandler' | string;

interface FtsActionState {
  id: string;
  command: ActionCommandType;
  state: ActionStateType;
  timestamp: string;
}

interface FtsLoadInfo {
  loadId: string | null;
  loadType: 'BLUE' | 'WHITE' | 'RED' | null;
  loadPosition: string;
}

interface FtsState {
  serialNumber: string;
  headerId: number;
  timestamp: string;
  orderId: string;
  orderUpdateId: number;
  lastNodeId: string;
  lastNodeSequenceId: number;
  lastCode: string;
  driving: boolean;
  paused: boolean;
  waitingForLoadHandling: boolean;
  batteryState: FtsBatteryState;
  actionState: FtsActionState;
  actionStates: FtsActionState[];
  load: FtsLoadInfo[];
  nodeStates: unknown[];
  edgeStates: unknown[];
  errors: unknown[];
}

// FTS Serial Number (from message-monitor-tab.component.ts)
const FTS_SERIAL = '5iO4';
const FTS_STATE_TOPIC = `fts/v1/ff/${FTS_SERIAL}/state`;

// Serial number to module type mapping (from message-monitor-tab.component.ts)
const SERIAL_TO_MODULE_TYPE: Record<string, string> = {
  'SVR3QA0022': 'HBW',
  'SVR4H76449': 'DRILL',
  'SVR3QA2098': 'MILL',
  'SVR4H76530': 'AIQS',
  'SVR4H73275': 'DPS',
  'CHRG0': 'CHRG',
};

@Component({
  standalone: true,
  selector: 'app-fts-tab',
  imports: [CommonModule, ShopfloorPreviewComponent],
  templateUrl: './fts-tab.component.html',
  styleUrl: './fts-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FtsTabComponent implements OnInit, OnDestroy {
  private dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();
  
  // Route animation state (from Example-App)
  private previousNodeId: string | null = null;
  private layoutConfig: ShopfloorLayoutConfig | null = null;

  // Icons - verwende neue SVGs aus shopfloor/ und headings/
  readonly headingIcon = 'shopfloor/robotic.svg'; // FTS/AGV Icon
  readonly statusIcon = 'shopfloor/robotic.svg';
  readonly batteryIcon = 'shopfloor/battery.svg'; // ✅ Neues SVG
  readonly loadIcon = 'headings/box.svg'; // ✅ Verwendet box.svg aus headings
  readonly routeIcon = 'headings/route.svg'; // ✅ Neues SVG

  // Status icons - verwende neue SVGs
  readonly drivingIcon = 'shopfloor/driving-status.svg'; // ✅ Neues SVG
  readonly stoppedIcon = 'shopfloor/stopped-status.svg'; // ✅ Neues SVG
  readonly pausedIcon = 'shopfloor/paused-status.svg'; // ✅ Neues SVG
  readonly loadingIcon = 'headings/box.svg';
  readonly chargingIcon = 'shopfloor/charging-active.svg'; // ✅ Neues SVG

  // Fixtures für Testing
  readonly fixtureOptions: OrderFixtureName[] = ['startup', 'mixed'];
  readonly fixtureLabels: Record<string, string> = {
    startup: $localize`:@@fixtureLabelStartup:Startup`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
  };
  activeFixture: OrderFixtureName = this.dashboard.getCurrentFixture();

  // Observable streams
  ftsState$!: Observable<FtsState | null>;
  batteryState$!: Observable<FtsBatteryState | null>;
  loads$!: Observable<FtsLoadInfo[]>;
  
  // FTS position for shopfloor preview
  ftsPosition$!: Observable<{ x: number; y: number } | null>;
  
  // Active route segments for animation (orange - currently driving) - from animation service
  activeRouteSegments$!: Observable<Array<{ x1: number; y1: number; x2: number; y2: number }>>;
  
  // Current position node (for highlighting current position in ORBIS-blue-medium)
  currentPositionNode$!: Observable<string[] | null>;
  
  // Animation state from service (initialized in constructor)
  animationState$!: Observable<AnimationState>;

  // UI state (removed batteryDetailsExpanded - always show details like example)

  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly environmentService: EnvironmentService,
    private readonly connectionService: ConnectionService,
    private readonly moduleNameService: ModuleNameService,
    private readonly ftsRouteService: FtsRouteService,
    private readonly ftsAnimationService: FtsAnimationService,
    private readonly cdr: ChangeDetectorRef,
    private readonly http: HttpClient
  ) {
    // Initialize animation state observable after service is available
    this.animationState$ = this.ftsAnimationService.animationState$;
    this.loadShopfloorLayout();
    this.initializeStreams();
  }
  
  private loadShopfloorLayout(): void {
    this.subscriptions.add(
      this.http.get<ShopfloorLayoutConfig>('shopfloor/shopfloor_layout.json').pipe(
        catchError((error) => {
          console.warn('[FTS Tab] Failed to load shopfloor layout:', error);
          return of(null);
        })
      ).subscribe((config) => {
        if (config) {
          this.layoutConfig = config;
          this.parseLayout(config);
        }
      })
    );
  }
  
  private parseLayout(config: ShopfloorLayoutConfig): void {
    // Initialize route service with layout
    this.ftsRouteService.initializeLayout(config);
    
    // Re-initialize streams to update position calculation
    this.initializeStreams();
    this.cdr.markForCheck();
  }
  
  /**
   * Compute stationary position: 60% of the route from intersection/road to module center
   * Delegates to FtsRouteService
   */
  private computeStationaryPosition(nodeId: string): ShopfloorPoint | null {
    return this.ftsRouteService.computeStationaryPosition(nodeId);
  }
  
  /**
   * Resolve node reference to canonical form
   * Delegates to FtsRouteService
   */
  private resolveNodeRef(value: string | undefined): string | null {
    return this.ftsRouteService.resolveNodeRef(value);
  }
  
  /**
   * Find route path using BFS
   * Delegates to FtsRouteService
   */
  private findRoutePath(start: string, target: string): string[] | null {
    return this.ftsRouteService.findRoutePath(start, target);
  }
  
  /**
   * Find road between two nodes
   * Delegates to FtsRouteService
   */
  private findRoadBetween(a: string, b: string): ParsedRoad | null {
    return this.ftsRouteService.findRoadBetween(a, b);
  }
  
  /**
   * Build road segment with trimmed endpoints
   * Delegates to FtsRouteService
   */
  private buildRoadSegment(road: ParsedRoad): { x1: number; y1: number; x2: number; y2: number } | null {
    return this.ftsRouteService.buildRoadSegment(road);
  }
  
  private handleFtsStateChange(state: FtsState): void {
    const newNodeId = state.lastNodeId ?? '';
    const isDriving = state.driving ?? false;
    
    // Initialize previousNodeId if not set
    if (this.previousNodeId === null && newNodeId) {
      this.previousNodeId = newNodeId;
    }
    
    // Get current animation state
    const animationState = this.ftsAnimationService.getState();
    
    // CRITICAL: If we have an active animation path, NEVER touch the route
    // The route is managed exclusively by the animation logic
    // This prevents the route from being cleared or overwritten during multi-segment animation
    if (animationState.animationPath.length >= 2) {
      // Only check if FTS stopped - then we need to stop animation
      if (!isDriving && animationState.isAnimating) {
        this.ftsAnimationService.stopAnimation();
      }
      // Don't process further - let animation complete
      // The route is already set and must remain unchanged
      return;
    }
    
    // During animation, ignore new state changes to prevent route visualization from being disturbed
    if (animationState.isAnimating) {
      // Only check if FTS stopped - then we need to stop animation
      if (!isDriving) {
        this.ftsAnimationService.stopAnimation();
      }
      // Don't process further - let animation complete
      return;
    }
    
    // If node changed and driving, animate along the path
    if (newNodeId && this.previousNodeId && newNodeId !== this.previousNodeId) {
      if (isDriving) {
        // Start new animation with callbacks
        this.ftsAnimationService.animateBetweenNodes(this.previousNodeId, newNodeId, {
          onAnimationComplete: (finalNodeId) => {
            // Update previousNodeId now that animation is complete
            // This prevents flickering and position resets
            this.previousNodeId = finalNodeId;
            this.cdr.markForCheck();
          },
        });
      } else {
        // FTS stopped - clear animation
        this.ftsAnimationService.stopAnimation();
      }
    } else if (!isDriving) {
      // FTS stopped - clear animation
      this.ftsAnimationService.stopAnimation();
    }
    
    // DON'T update previousNodeId here - it should only be updated when animation completes
    // This prevents flickering and position resets
    
    // Only update route segments if not animating (to prevent disturbance)
    if (!animationState.isAnimating) {
      this.updateActiveRouteSegments(state);
    }
    
    // Force position update
    this.cdr.markForCheck();
  }
  
  
  
  private updateActiveRouteSegments(state: FtsState): void {
    // Get current animation state
    const animationState = this.ftsAnimationService.getState();
    
    // CRITICAL: NEVER update route segments if we have an active animation path
    // The route must remain visible during the entire multi-segment animation
    if (animationState.animationPath.length >= 2) {
      // We have an active route - keep it visible, don't touch it
      // The route will only be cleared when animation completes
      return;
    }
    
    // NEVER update route segments during animation - they are managed by animation logic
    if (animationState.isAnimating) {
      return;
    }
    
    if (!state.driving) {
      // When FTS stops and no animation path exists, clear route segments
      // Route segments are managed by animation service, so we don't need to clear them here
      return;
    }
    
    // Calculate full route path from previous to current node (over intersections)
    // Only if we don't have an active animation path
    if (state.lastNodeId && this.previousNodeId && state.lastNodeId !== this.previousNodeId) {
      const fullPath = this.findRoutePath(this.previousNodeId, state.lastNodeId);
      if (fullPath && fullPath.length >= 2) {
        // Start animation - this will handle route segments
        this.ftsAnimationService.animateBetweenNodes(this.previousNodeId, state.lastNodeId, {
          onAnimationComplete: (finalNodeId) => {
            this.previousNodeId = finalNodeId;
            this.cdr.markForCheck();
          },
        });
        return;
      }
    }
    
    // No route available (and no active animation path)
    // Route segments are managed by animation service
  }

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  get isReplayMode(): boolean {
    return this.environmentService.current.key === 'replay';
  }

  ngOnInit(): void {
    this.subscriptions.add(
      this.connectionService.state$
        .pipe(filter((state) => state === 'connected'))
        .subscribe(() => {
          this.initializeStreams();
        })
    );
  }

  ngOnDestroy(): void {
    this.ftsAnimationService.stopAnimation();
    this.subscriptions.unsubscribe();
  }

  private initializeStreams(): void {
    // Pattern 2: MessageMonitor + Streams (analog zu OrderTabComponent)
    this.ftsState$ = this.messageMonitor.getLastMessage<FtsState>(FTS_STATE_TOPIC).pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload as FtsState),
      tap((state) => {
        if (state) {
          this.handleFtsStateChange(state);
        }
      }),
      startWith(null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Battery state stream
    this.batteryState$ = this.ftsState$.pipe(
      map((state) => state?.batteryState ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Loads stream
    this.loads$ = this.ftsState$.pipe(
      map((state) => state?.load ?? []),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // FTS position for shopfloor preview - calculated from lastNodeId using shopfloor layout
    // Use combineLatest to react to both state changes and animation updates
    this.ftsPosition$ = combineLatest([
      this.ftsState$,
      this.animationState$.pipe(
        map((animState) => animState.animatedPosition),
        distinctUntilChanged((prev, curr) => {
          if (!prev && !curr) return true;
          if (!prev || !curr) return false;
          const dx = Math.abs(prev.x - curr.x);
          const dy = Math.abs(prev.y - curr.y);
          return dx < 2 && dy < 2;
        })
      ),
    ]).pipe(
      map(([state, animatedPos]) => {
        if (!state?.lastNodeId) return null;
        
        const animationState = this.ftsAnimationService.getState();
        
        // Use animated position if animating (when driving) - like example app
        if (animatedPos && animationState.isAnimating && state.driving) {
          return animatedPos;
        }
        
        // Like example app: when animation completes, animatedPosition is null and we use node position
        // Use exact node center position (like example app - no 60% offset for FTS tab)
        const nodeId = state.lastNodeId;
        if (!nodeId) return null;
        
        // Try to get position from route service
        // First try direct lookup
        let nodePos = this.ftsRouteService.getNodePosition(nodeId);
        
        // If not found, try canonical lookup via resolveNodeRef
        if (!nodePos) {
          const canonical = this.resolveNodeRef(nodeId);
          if (canonical) {
            nodePos = this.ftsRouteService.getNodePosition(canonical);
          }
        }
        
        // If still not found, try serial number mapping
        if (!nodePos) {
          const moduleType = SERIAL_TO_MODULE_TYPE[nodeId];
          if (moduleType) {
            nodePos = this.ftsRouteService.getNodePosition(moduleType);
            // Also try serial: prefix
            if (!nodePos) {
              nodePos = this.ftsRouteService.getNodePosition(`serial:${moduleType}`);
            }
          }
        }
        
        // If still not found, try intersection: prefix for numeric IDs
        if (!nodePos && nodeId.match(/^\d+$/)) {
          // Try intersection: prefix first (canonical form)
          nodePos = this.ftsRouteService.getNodePosition(`intersection:${nodeId}`);
          // Also try direct numeric lookup (alias)
          if (!nodePos) {
            nodePos = this.ftsRouteService.getNodePosition(nodeId);
          }
        }
        
        if (nodePos) {
          // Use exact center position (like example app)
          return { x: nodePos.x, y: nodePos.y };
        }
        
        // Fallback: return null if node not found (layout not loaded yet)
        // Only warn if it's not a known intersection and layout is initialized
        if (!nodeId.match(/^\d+$/)) {
          // Only warn if layout is initialized but this specific node is missing
          if (this.ftsRouteService.isLayoutInitialized()) {
            const availableNodes = this.ftsRouteService.getAvailableNodeIds();
            console.warn('[FTS Tab] Node not found in layout:', state.lastNodeId, '- Available nodes:', availableNodes.slice(0, 10));
          }
          // If layout not initialized yet, silently return null (will be retried when layout loads)
        }
        return null;
      }),
      distinctUntilChanged((prev, curr) => {
        // Only emit if position actually changed significantly (more than 2px)
        if (!prev || !curr) return prev === curr;
        const dx = Math.abs(prev.x - curr.x);
        const dy = Math.abs(prev.y - curr.y);
        return dx < 2 && dy < 2;
      }),
      debounceTime(100), // Debounce to prevent flickering
      shareReplay({ bufferSize: 1, refCount: false })
    );
    
  // Active route segments for animation - from animation service
  this.activeRouteSegments$ = this.animationState$.pipe(
    map((animState) => animState.activeRouteSegments),
    shareReplay({ bufferSize: 1, refCount: false })
  );
  
  // Observable for current position node (for highlighting current position)
  this.currentPositionNode$ = this.ftsState$.pipe(
    map((state) => state?.lastNodeId ? [state.lastNodeId] : null),
    shareReplay({ bufferSize: 1, refCount: false })
  );
  }

  // Helper methods for template
  getLocationName(nodeId: string | undefined): string {
    if (!nodeId) return $localize`:@@ftsLocationUnknown:Unknown`;
    
    // For intersections, use FtsRouteService mapping
    const resolved = this.resolveNodeRef(nodeId);
    if (resolved && resolved.startsWith('intersection:')) {
      const intersectionNumber = resolved.replace('intersection:', '');
      return $localize`:@@ftsLocationIntersection:Intersection ${intersectionNumber}`;
    }
    
    // Convert serial number to module type, then get full name
    const moduleType = SERIAL_TO_MODULE_TYPE[nodeId];
    if (moduleType) {
      return this.moduleNameService.getModuleDisplayText(moduleType, 'full-only');
    }
    
    // Fallback: try direct lookup (in case it's already a module type)
    return this.moduleNameService.getModuleDisplayText(nodeId, 'full-only');
  }

  getLocationShortName(nodeId: string | undefined): string {
    if (!nodeId) return $localize`:@@ftsLocationUnknown:Unknown`;
    
    // For intersections, use FtsRouteService mapping
    const resolved = this.resolveNodeRef(nodeId);
    if (resolved && resolved.startsWith('intersection:')) {
      const intersectionNumber = resolved.replace('intersection:', '');
      return `INT-${intersectionNumber}`;
    }
    
    // Convert serial number to module type, then get ID
    const moduleType = SERIAL_TO_MODULE_TYPE[nodeId];
    if (moduleType) {
      return this.moduleNameService.getModuleDisplayText(moduleType, 'id-only');
    }
    
    // Fallback: try direct lookup
    return this.moduleNameService.getModuleDisplayText(nodeId, 'id-only');
  }

  getRouteStatus(ftsState: FtsState | null): string {
    if (!ftsState) return $localize`:@@ftsRouteStatusUnknown:Unknown`;
    if (ftsState.driving) return $localize`:@@ftsRouteStatusInTransit:In Transit`;
    return $localize`:@@ftsRouteStatusStationary:Stationary`;
  }

  getUnknownLocationText(): string {
    return $localize`:@@ftsLocationUnknown:Unknown`;
  }

  getOrderIdDisplay(orderId: string | undefined): string {
    if (!orderId) return $localize`:@@ftsStatusNoOrder:None`;
    return orderId.length > 8 ? `${orderId.substring(0, 8)}...` : orderId;
  }

  getLoadedCount(loads: FtsLoadInfo[]): number {
    return loads.filter(l => l.loadType !== null).length;
  }

  getBatteryLevelClass(percentage: number): 'high' | 'medium' | 'low' {
    if (percentage >= 60) return 'high';
    if (percentage >= 30) return 'medium';
    return 'low';
  }

  getVoltageDisplay(batteryState: FtsBatteryState | null): string {
    if (!batteryState) return '0.0V';
    return `${batteryState.currentVoltage.toFixed(1)}V`;
  }

  getVoltageRange(batteryState: FtsBatteryState | null): string {
    if (!batteryState) return '0.00V - 0.00V';
    const min = batteryState.minVolt.toFixed(2);
    const max = batteryState.maxVolt.toFixed(2);
    return `${min}V - ${max}V`;
  }

  getChargingStatusText(charging: boolean): string {
    return charging 
      ? $localize`:@@commonYes:Yes`
      : $localize`:@@commonNo:No`;
  }

  async loadFixture(fixture: OrderFixtureName): Promise<void> {
    // In replay mode, fixtures are loaded from MQTT broker, not from local files
    if (this.isReplayMode) {
      console.info('[FTS Tab] Replay mode - FTS data should come from MQTT broker');
      // In replay mode, we just wait for messages from the broker
      // The streams will automatically update when messages arrive
      this.activeFixture = fixture;
      this.cdr.markForCheck();
      return;
    }
    
    if (!this.isMockMode) {
      return; // Don't load fixtures in live mode
    }
    
    this.activeFixture = fixture;
    
    try {
      // Map OrderFixtureName to tab-specific preset
      const presetMap: Record<string, string> = {
        startup: 'startup',
        mixed: 'order-mixed',
      };
      
      const preset = presetMap[fixture] || 'startup';
      await this.dashboard.loadTabFixture(preset);
      
      // Re-initialize streams after fixture load (like order-tab does)
      this.initializeStreams();
      
      // Trigger change detection to update UI
      this.cdr.markForCheck();
    } catch (error) {
      console.warn('Failed to load FTS fixture', fixture, error);
      console.warn('[FTS Tab] Note: FTS topics may not be included in standard fixtures. Consider using replay environment.');
    }
  }

  getCurrentAction(ftsState: FtsState | null): FtsActionState | null {
    return ftsState?.actionState ?? null;
  }

  getRecentActions(ftsState: FtsState | null): FtsActionState[] {
    return ftsState?.actionStates?.slice(-5) ?? [];
  }

  // Aggregated action states across all orders (from MessageMonitor)
  private allActionStates: FtsActionState[] = [];
  
  getActionStates(ftsState: FtsState | null): FtsActionState[] {
    // Aggregate actions from current state
    if (ftsState?.actionStates) {
      // Merge with existing actions, avoiding duplicates
      const newActions = ftsState.actionStates.filter(
        (action) => !this.allActionStates.some(
          (existing) => existing.id === action.id && existing.timestamp === action.timestamp
        )
      );
      this.allActionStates = [...this.allActionStates, ...newActions];
    }
    
    // Sort by timestamp descending (newest first)
    return [...this.allActionStates].sort((a, b) => {
      const timeA = new Date(a.timestamp).getTime();
      const timeB = new Date(b.timestamp).getTime();
      return timeB - timeA; // Descending order
    });
  }
  
  getActionStatesSorted(ftsState: FtsState | null): FtsActionState[] {
    return this.getActionStates(ftsState);
  }
  
  getActionIcon(command: string): string {
    const iconMap: Record<string, string> = {
      'TURN': 'shopfloor/turn-event.svg',
      'DOCK': 'shopfloor/dock-event.svg',
      'PASS': 'shopfloor/pass-event.svg',
      'PICK': 'shopfloor/pick-event.svg',
      'DROP': 'shopfloor/drop-event.svg',
      'PROCESS': 'shopfloor/process-event.svg',
    };
    return iconMap[command.toUpperCase()] || 'shopfloor/process-event.svg';
  }
  
  getLoadIcon(load: FtsLoadInfo): string {
    if (!load.loadType) {
      return 'workpieces/slot_empty.svg';
    }
    const color = load.loadType.toLowerCase();
    // Use _instock_processed.svg as specified by user
    return `workpieces/${color}_instock_processed.svg`;
  }
  
  // Ensure we always have 3 load positions
  getLoadPositions(loads: FtsLoadInfo[]): FtsLoadInfo[] {
    const positions: FtsLoadInfo[] = [];
    for (let i = 1; i <= 3; i++) {
      const load = loads.find(l => l.loadPosition === i.toString() || l.loadPosition === `Position ${i}`);
      positions.push(load || {
        loadId: null,
        loadType: null,
        loadPosition: i.toString(),
      });
    }
    return positions;
  }

  getStateClass(state: string): string {
    const stateUpper = state.toUpperCase();
    if (stateUpper === 'WAITING') return 'waiting';
    if (stateUpper === 'INITIALIZING') return 'initializing';
    if (stateUpper === 'RUNNING') return 'running';
    if (stateUpper === 'FINISHED') return 'finished';
    if (stateUpper === 'FAILED') return 'failed';
    return 'unknown';
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

  // Removed toggleBatteryDetails - always show details like example app
}

