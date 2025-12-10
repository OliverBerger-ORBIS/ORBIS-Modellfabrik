import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit, Input } from '@angular/core';
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
import { LanguageService, type LocaleKey } from '../services/language.service';
import type { OrderFixtureName } from '@omf3/testing-fixtures';
import type { ShopfloorLayoutConfig, ShopfloorPoint, ParsedRoad, ShopfloorCellConfig, ShopfloorRoadEndpoint } from '../components/shopfloor-preview/shopfloor-layout.types';
import { ICONS } from '../shared/icons/icon.registry';

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
  metadata?: Record<string, unknown>;
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
const FTS_ORDER_TOPIC = `fts/v1/ff/${FTS_SERIAL}/order`;
const FTS_INSTANT_ACTION_TOPIC = `fts/v1/ff/${FTS_SERIAL}/instantAction`;
const CCU_SET_CHARGE_TOPIC = 'ccu/set/charge';
const DOCK_NODE_DPS = 'SVR4H73275'; // DPS serial (from fixtures/tests)
const START_NODE_MAP: Record<string, string> = {
  MILL: 'SVR3QA2098',
  DRILL: 'SVR4H76449',
  HBW: 'SVR3QA0022',
  DPS: 'SVR4H73275',
  AIQS: 'SVR4H76530',
  CHRG: 'CHRG0',
};

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
  @Input() presentationMode = false;
  private dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();
  
  // Route animation state (from Example-App)
  private previousNodeId: string | null = null;
  private layoutConfig: ShopfloorLayoutConfig | null = null;
  private turnDirectionByActionId = new Map<string, 'LEFT' | 'RIGHT' | string>();
  private lastFtsState: FtsState | null = null;

  // Icons - neue SVGs aus assets/svg/ui & shopfloor
  readonly headingIcon = 'assets/svg/shopfloor/shared/agv-vehicle.svg'; // FTS/AGV Icon
  readonly statusIcon = 'assets/svg/shopfloor/shared/agv-vehicle.svg';
  readonly batteryIcon = 'assets/svg/shopfloor/shared/battery.svg';
  readonly loadIcon = 'assets/svg/ui/heading-purchase-orders.svg';
  readonly routeIcon = 'assets/svg/ui/heading-route.svg';
  readonly turnLeftIcon = 'assets/svg/shopfloor/shared/turn-left-event.svg';
  readonly turnRightIcon = 'assets/svg/shopfloor/shared/turn-right-event.svg';
  readonly turnDefaultIcon = 'assets/svg/shopfloor/shared/turn-right-event.svg';
  readonly ftsOrderTopic = FTS_ORDER_TOPIC;
  readonly ftsInstantActionTopic = FTS_INSTANT_ACTION_TOPIC;
  readonly ccuSetChargeTopic = CCU_SET_CHARGE_TOPIC;
  readonly startNodeOptions = ['auto', 'MILL', 'DRILL', 'HBW', 'DPS', 'AIQS', 'CHRG'] as const;
  selectedStartNode: (typeof this.startNodeOptions)[number] = 'auto';
  // Labels aligned to Module-Tab naming; default EN text, ready for translation (DE/FR)
  readonly labelChargeOn = $localize`:@@ftsCommandChargeOn:Charge`;
  readonly labelChargeOff = $localize`:@@ftsCommandChargeOff:Stop Charging`;
  readonly labelDockInitial = $localize`:@@ftsCommandDockInitial:Dock`;
  readonly labelDriveInstant = $localize`:@@ftsCommandDriveInstant:Drive to Intersection 2 (instant)`;
  readonly labelDriveOrder = $localize`:@@ftsCommandDriveOrder:Drive to Intersection 2 (order)`;
  readonly labelStartSelect = $localize`:@@ftsCommandStartSelect:Start`;
  readonly labelStartAuto = $localize`:@@ftsCommandStartAuto:Auto (current position)`;
  readonly badgeTextFtsPosition = $localize`:@@ftsBadgePosition:Position`;
  readonly devModeTitle = $localize`:@@ftsDevModeTitle:Developer Mode (Topics & Payload)`;
  readonly devChargeTitle = $localize`:@@ftsDevChargeTitle:Charge ON/OFF`;
  readonly devDockTitle = $localize`:@@ftsDevDockTitle:Dock to Initial`;
  readonly devDriveOrderTitle = $localize`:@@ftsDevDriveOrderTitle:Drive to Intersection 2`;
  readonly devDriveInstantTitle = $localize`:@@ftsDevDriveInstantTitle:Drive to Intersection 2 (instant)`;
  readonly vehicleLabelEn = 'AGV';
  readonly vehicleLabelFr = 'AGV';
  readonly vehicleLabelDe = 'FTS';

  // Status icons - verwende neue SVGs
  readonly drivingIcon = 'assets/svg/shopfloor/shared/driving-status.svg';
  readonly stoppedIcon = 'assets/svg/shopfloor/shared/stopped-status.svg';
  readonly pausedIcon = 'assets/svg/shopfloor/shared/paused-status.svg';
  readonly loadingIcon = 'assets/svg/ui/heading-purchase-orders.svg';
  readonly chargingIcon = 'assets/svg/shopfloor/shared/charging-active.svg';

  // Fixtures für Testing
  readonly fixtureOptions: OrderFixtureName[] = [
    'startup',
    'white',
    'blue',
    'red',
    'mixed',
    'storage',
    'production_bwr',
    'production_white',
    'storage_blue',
    'track-trace-production-bwr',
  ];
  readonly fixtureLabels: Partial<Record<OrderFixtureName, string>> = {
    startup: $localize`:@@fixtureLabelStartup:Startup`,
    white: $localize`:@@fixtureLabelWhite:White`,
    blue: $localize`:@@fixtureLabelBlue:Blue`,
    red: $localize`:@@fixtureLabelRed:Red`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
    storage: $localize`:@@fixtureLabelStorage:Storage`,
    production_bwr: $localize`:@@fixtureLabelProductionBwr:Production BWR`,
    production_white: $localize`:@@fixtureLabelProductionWhite:Production White`,
    storage_blue: $localize`:@@fixtureLabelStorageBlue:Storage Blue`,
    'track-trace-production-bwr': $localize`:@@fixtureLabelTrackTraceBwr:TrackTrace Production BWR`,
  };
  activeFixture: OrderFixtureName | null = this.dashboard.getCurrentFixture();

  // Observable streams
  ftsState$!: Observable<FtsState | null>;
  batteryState$!: Observable<FtsBatteryState | null>;
  loads$!: Observable<FtsLoadInfo[]>;
  ftsOrder$!: Observable<any | null>;
  
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
    private readonly languageService: LanguageService,
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

  private uuid(): string {
    // Simple RFC4122-ish generator sufficient for client-side IDs
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
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
    this.lastFtsState = state;
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

    // Order stream (for TURN direction etc.)
    this.ftsOrder$ = this.messageMonitor.getLastMessage<any>(FTS_ORDER_TOPIC).pipe(
      map((msg) => msg?.payload ?? null),
      tap((order) => {
        if (!order) return;
        // Build actionId -> direction map for TURN actions
        // Order schema: nodes[].action.id / type / metadata.direction
        if (Array.isArray(order.nodes)) {
          order.nodes.forEach((node: any) => {
            const action = node?.action;
            if (action?.type === 'TURN' && action?.id && action?.metadata?.direction) {
              this.turnDirectionByActionId.set(action.id, action.metadata.direction);
            }
          });
        }
      }),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Warm up order stream so direction map is populated
    this.subscriptions.add(this.ftsOrder$.subscribe());

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
      const presetMap: Partial<Record<OrderFixtureName, string>> = {
        startup: 'startup',
        white: 'order-white',
        blue: 'order-blue',
        red: 'order-red',
        mixed: 'order-mixed',
        storage: 'order-storage',
        production_bwr: 'track-trace-production-bwr',
        production_white: 'track-trace-production-white',
        storage_blue: 'track-trace-storage-blue',
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
    const cmd = command.toUpperCase();
    if (cmd === 'TURN') return this.turnDefaultIcon;
    if (cmd === 'DOCK') return ICONS.shopfloor.shared.dockEvent;
    if (cmd === 'PASS') return ICONS.shopfloor.shared.passEvent;
    if (cmd === 'PICK') return ICONS.shopfloor.shared.pickEvent;
    if (cmd === 'DROP') return ICONS.shopfloor.shared.dropEvent;
    if (cmd === 'PROCESS') return ICONS.shopfloor.shared.processEvent;
    return ICONS.shopfloor.shared.processEvent;
  }

  getActionIconFor(action: FtsActionState): string {
    const dir = this.getActionDirection(action)?.toUpperCase();
    if (action.command === 'TURN' && dir === 'LEFT') return this.turnLeftIcon;
    if (action.command === 'TURN' && dir === 'RIGHT') return this.turnRightIcon;
    return this.getActionIcon(action.command);
  }

  getActionLabel(action: FtsActionState): string {
    const cmd = action.command.toUpperCase();
    if (cmd === 'TURN') {
      const dir = this.getActionDirection(action)?.toUpperCase();
      if (dir === 'LEFT') return 'TURN LEFT';
      if (dir === 'RIGHT') return 'TURN RIGHT';
      return 'TURN';
    }
    return action.command;
  }
  
  getLoadIcon(load: FtsLoadInfo): string {
    if (!load.loadType) {
      return ICONS.shopfloor.workpieces.slotEmpty;
    }
    const color = load.loadType.toLowerCase();
    // Use _instock_processed.svg as specified by user
    if (color === 'blue') return ICONS.shopfloor.workpieces.blue.instockProcessed;
    if (color === 'white') return ICONS.shopfloor.workpieces.white.instockProcessed;
    if (color === 'red') return ICONS.shopfloor.workpieces.red.instockProcessed;
    return ICONS.shopfloor.workpieces.slotEmpty;
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

  // TURN direction lookup (from order stream)
  getActionDirection(action: FtsActionState): string | undefined {
    if (action.command !== 'TURN') return undefined;
    // Prefer direction from action metadata if present
    const metaDir = (action as any)?.metadata?.direction;
    if (typeof metaDir === 'string' && metaDir.trim().length > 0) {
      return metaDir;
    }
    // Fallback to order-derived map
    return this.turnDirectionByActionId.get(action.id);
  }

  onStartNodeChange(value: string): void {
    if (this.startNodeOptions.includes(value as any)) {
      this.selectedStartNode = value as (typeof this.startNodeOptions)[number];
    } else {
      this.selectedStartNode = 'auto';
    }
  }

  get isCharging(): boolean {
    return this.lastFtsState?.batteryState?.charging ?? false;
  }

  get chargeButtonLabel(): string {
    return this.isCharging ? this.labelChargeOff : this.labelChargeOn;
  }

  get showDockInitial(): boolean {
    const node = this.lastFtsState?.lastNodeId;
    return !node || node === 'UNKNOWN';
  }

  getStartOptionLabel(option: (typeof this.startNodeOptions)[number]): string {
    switch (option) {
      case 'auto':
        return this.labelStartAuto;
      case 'MILL':
        return $localize`:@@ftsStartOptionMill:MILL`;
      case 'DRILL':
        return $localize`:@@ftsStartOptionDrill:DRILL`;
      case 'HBW':
        return $localize`:@@ftsStartOptionHbw:HBW`;
      case 'DPS':
        return $localize`:@@ftsStartOptionDps:DPS`;
      case 'AIQS':
        return $localize`:@@ftsStartOptionAiqs:AIQS`;
      case 'CHRG':
        return $localize`:@@ftsStartOptionChrg:CHRG`;
      default:
        return option;
    }
  }

  get locale(): LocaleKey {
    return this.languageService.current ?? 'en';
  }

  get vehicleLabelShort(): string {
    if (this.locale === 'de') return this.vehicleLabelDe;
    if (this.locale === 'fr') return this.vehicleLabelFr;
    return this.vehicleLabelEn;
  }

  get vehicleLabelLong(): string {
    if (this.locale === 'de') return 'Fahrerloses Transportsystem (FTS)';
    if (this.locale === 'fr') return 'Véhicule autoguidé (AGV)';
    return 'Automated Guided Vehicle (AGV)';
  }

  get statusSubtitle(): string {
    if (this.locale === 'de') {
      return 'Echtzeit-Status, Batterie- und Routeninformationen für das Fahrerlose Transportsystem.';
    }
    if (this.locale === 'fr') {
      return 'Statut en temps réel, batterie et informations de route pour l’AGV.';
    }
    return 'Real-time status, battery, and route information for the AGV.';
  }

  get badgeTextVehiclePosition(): string {
    if (this.locale === 'de') return 'FTS-Position';
    if (this.locale === 'fr') return 'Position AGV';
    return 'AGV Position';
  }

  // Example payloads for developer view
  get chargeExamplePayload() {
    return {
      topic: CCU_SET_CHARGE_TOPIC,
      payload: {
        serialNumber: FTS_SERIAL,
        charge: true,
      },
      options: { qos: 1, retain: false },
    };
  }

  get dockExamplePayload() {
    return {
      topic: FTS_INSTANT_ACTION_TOPIC,
      payload: {
        serialNumber: FTS_SERIAL,
        timestamp: '2025-01-01T12:00:00.000Z',
        actions: [
          {
            actionId: 'dock-xxxx',
            actionType: 'findInitialDockPosition',
            metadata: { nodeId: DOCK_NODE_DPS },
          },
        ],
      },
      options: { qos: 1, retain: false },
    };
  }

  get driveExamplePayload() {
    return {
      topic: FTS_ORDER_TOPIC,
      payload: {
        timestamp: '2025-01-01T12:00:00.000Z',
        orderId: 'example-order-id',
        orderUpdateId: 0,
        nodes: [
          {
            id: '2',
            linkedEdges: ['1-2'],
            action: {
              type: 'STOP',
              id: 'example-stop-id',
              metadata: {},
            },
          },
        ],
        edges: [
          {
            id: '1-2',
            length: 360,
            linkedNodes: ['1', '2'],
          },
        ],
        serialNumber: FTS_SERIAL,
        metadata: {
          requestedFrom: '1',
        },
      },
      options: { qos: 1, retain: false },
    };
  }

  get driveInstantExamplePayload() {
    return {
      topic: FTS_INSTANT_ACTION_TOPIC,
      payload: {
        serialNumber: FTS_SERIAL,
        timestamp: '2025-01-01T12:00:00.000Z',
        actions: [
          {
            actionId: 'drive-xxxx',
            actionType: 'findPosition',
            metadata: { nodeId: '2' },
          },
        ],
      },
      options: { qos: 1, retain: false },
    };
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

  // --- Command publishing (AGV controls) ---

  async sendCharge(enable: boolean): Promise<void> {
    // Reuse business command to ensure exact payload/topic as Module-Tab tests
    await this.dashboard.commands.setFtsCharge(FTS_SERIAL, enable);
  }

  async sendDockInitial(): Promise<void> {
    // Use the same command as Module-Tab (instantAction findInitialDockPosition with nodeId DPS)
    await this.dashboard.commands.dockFts(FTS_SERIAL, DOCK_NODE_DPS);
  }

  async sendDriveToIntersection2Instant(): Promise<void> {
    const actionId = `drive-${this.uuid()}`;
    const payload = {
      serialNumber: FTS_SERIAL,
      timestamp: new Date().toISOString(),
      actions: [
        {
          actionId,
          actionType: 'findPosition',
          metadata: { nodeId: '2' },
        },
      ],
    };
    await this.connectionService.publish(FTS_INSTANT_ACTION_TOPIC, payload, { qos: 1 });
  }

  private buildOrderToIntersection2(): {
    payload: any;
    pathUsed: string[] | null;
  } {
    const target = '2';
    const start =
      this.selectedStartNode === 'auto'
        ? this.lastFtsState?.lastNodeId ?? null
        : START_NODE_MAP[this.selectedStartNode] ?? null;
    const path = start ? this.findRoutePath(start, target) : null;

    // Build nodes and edges from path if available
    const nodes: any[] = [];
    const edges: any[] = [];

    if (path && path.length >= 1) {
      // Build edge list from consecutive nodes
      for (let i = 0; i < path.length - 1; i++) {
        const a = path[i];
        const b = path[i + 1];
        const road = this.findRoadBetween(a, b);
        if (road) {
          edges.push({
            id: road.id,
            length: road.length,
            linkedNodes: [road.from.ref, road.to.ref],
          });
        }
      }

      // Build nodes with linkedEdges
      const linkedEdgesMap = new Map<string, Set<string>>();
      edges.forEach((e) => {
        const from = e.linkedNodes[0];
        const to = e.linkedNodes[1];
        if (!linkedEdgesMap.has(from)) linkedEdgesMap.set(from, new Set());
        if (!linkedEdgesMap.has(to)) linkedEdgesMap.set(to, new Set());
        linkedEdgesMap.get(from)!.add(e.id);
        linkedEdgesMap.get(to)!.add(e.id);
      });

      path.forEach((nodeId, idx) => {
        const edgeSet = linkedEdgesMap.get(nodeId) ?? new Set<string>();
        const isTarget = idx === path.length - 1;
        nodes.push({
          id: nodeId,
          linkedEdges: Array.from(edgeSet),
          ...(isTarget
            ? {
                action: {
                  id: `stop-${this.uuid()}`,
                  type: 'STOP',
                  metadata: {},
                },
              }
            : {}),
        });
      });
    } else {
      // Fallback minimal order: target node only
      nodes.push({
        id: target,
        linkedEdges: [],
        action: {
          id: `stop-${this.uuid()}`,
          type: 'STOP',
          metadata: {},
        },
      });
    }

    const payload = {
      timestamp: new Date().toISOString(),
      orderId: this.uuid(),
      orderUpdateId: 0,
      nodes,
      edges,
      serialNumber: FTS_SERIAL,
      metadata: {
        requestedFrom: start ?? undefined,
      },
    };

    return { payload, pathUsed: path };
  }

  async sendDriveToIntersection2Order(): Promise<void> {
    const { payload } = this.buildOrderToIntersection2();
    await this.connectionService.publish(FTS_ORDER_TOPIC, payload, { qos: 1 });
  }

  trackByActionId(_index: number, action: FtsActionState): string {
    return action.id;
  }

  // Removed toggleBatteryDetails - always show details like example app
}

