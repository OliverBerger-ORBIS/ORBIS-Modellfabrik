import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { filter, map, shareReplay, startWith, switchMap, catchError, tap, debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { Observable, Subscription, of, combineLatest, BehaviorSubject } from 'rxjs';
import { EnvironmentService } from '../services/environment.service';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ConnectionService } from '../services/connection.service';
import { ModuleNameService } from '../services/module-name.service';
import { ShopfloorMappingService, type AgvOption } from '../services/shopfloor-mapping.service';
import { AgvRouteService } from '../services/agv-route.service';
import { AgvAnimationService, type AnimationState } from '../services/agv-animation.service';
import { ShopfloorPreviewComponent } from '../components/shopfloor-preview/shopfloor-preview.component';
import { getDashboardController } from '../mock-dashboard';
import { LanguageService, type LocaleKey } from '../services/language.service';
import type { OrderFixtureName } from '@osf/testing-fixtures';
import type { ShopfloorLayoutConfig, ShopfloorPoint, ParsedRoad, ShopfloorCellConfig, ShopfloorRoadEndpoint } from '../components/shopfloor-preview/shopfloor-layout.types';
import { ICONS } from '../shared/icons/icon.registry';
import {
  ftsCanOfferInitialDockCommand,
  ftsCanOfferStartChargeCommand,
  ftsCanOfferStopChargeCommand,
  type FtsCommandAvailabilityInput,
} from '@osf/entities';

// FTS Types (from example app - will be moved to @osf/entities later)
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
  lastModuleSerialNumber?: string; // When docked at module
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

// Fallback serial when layout has no FTS config (Phase A: AGV selection via dropdown)
const FTS_SERIAL_FALLBACK = '5iO4';
const CCU_SET_CHARGE_TOPIC = 'ccu/set/charge';
const ftsStateTopic = (serial: string) => `fts/v1/ff/${serial}/state`;
const ftsOrderTopic = (serial: string) => `fts/v1/ff/${serial}/order`;
const ftsInstantActionTopic = (serial: string) => `fts/v1/ff/${serial}/instantAction`;
const DOCK_NODE_DPS = 'SVR4H73275'; // DPS serial (from fixtures/tests)
const HBW_SERIAL = 'SVR3QA0022';
const DPS_SERIAL = 'SVR4H73275';
const AIQS_SERIAL = 'SVR4H76530';
const INTERSECTION_2 = '2';
/** Supervisor nav targets: module serials or layout node id (e.g. intersection `"2"`). */
const NAV_TARGET_MAP: Record<string, string> = {
  MILL: 'SVR3QA2098',
  DRILL: 'SVR4H76449',
  HBW: HBW_SERIAL,
  DPS: DPS_SERIAL,
  AIQS: AIQS_SERIAL,
  CHRG: 'CHRG0',
  IX2: INTERSECTION_2,
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
  selector: 'app-agv-tab',
  imports: [CommonModule, FormsModule, ShopfloorPreviewComponent],
  templateUrl: './agv-tab.component.html',
  styleUrl: './agv-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AgvTabComponent implements OnInit, OnDestroy {
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
  readonly ccuSetChargeTopic = CCU_SET_CHARGE_TOPIC;

  /** Selected AGV serial for state/order/commands (Phase A: dropdown selection) */
  readonly selectedAgvSerial$ = new BehaviorSubject<string>(FTS_SERIAL_FALLBACK);

  get ftsOrderTopic(): string {
    return ftsOrderTopic(this.selectedAgvSerial$.value);
  }
  get ftsInstantActionTopic(): string {
    return ftsInstantActionTopic(this.selectedAgvSerial$.value);
  }
  /** Supervisor drive target (graph id via {@link NAV_TARGET_MAP}); start is always FTS-reported position. */
  readonly navTargetModuleOptions = ['MILL', 'DRILL', 'HBW', 'DPS', 'AIQS', 'CHRG', 'IX2'] as const;
  selectedNavTargetModule: (typeof this.navTargetModuleOptions)[number] = 'HBW';
  // Labels aligned to Module-Tab naming; default EN text, ready for translation (DE/FR)
  readonly labelChargeOn = $localize`:@@ftsCommandChargeOn:Charge`;
  readonly labelChargeOff = $localize`:@@ftsCommandChargeOff:Stop Charging`;
  readonly labelDockInitial = $localize`:@@ftsCommandDockInitial:Dock`;
  readonly labelNavigateToTargetDisabledHint = $localize`:@@ftsCommandNavigateToTargetDisabledHint:No live position, already at target, or no route`;
  readonly labelNavigateNoFtsState = $localize`:@@ftsNavigateNoFtsState:Wait for FTS state (connect or select AGV)`;
  readonly labelNavigatePositionUnclear = $localize`:@@ftsNavigatePositionUnclear:Reported position missing or UNKNOWN`;
  readonly labelNavigateAlreadyAtTarget = $localize`:@@ftsNavigateAlreadyAtTarget:Already at selected target`;
  readonly labelNavigateNoRoute = $localize`:@@ftsNavigateNoRoute:No route to selected target from reported position`;
  readonly labelSupervisorSection = $localize`:@@ftsSupervisorSection:Supervisor navigation`;
  readonly labelSupervisorTarget = $localize`:@@ftsSupervisorTarget:Target`;
  readonly labelSupervisorFootnote = $localize`:@@ftsSupervisorFootnote:After manual → HBW the vehicle often waits for module load handling. Use Clear load handling when physically safe (empty bays / no active CCU PICK) to publish clearLoadHandler on instantAction — then the CCU can assign orders again.`;
  readonly labelClearLoadHandler = $localize`:@@ftsCommandClearLoadHandler:Clear load handling`;
  readonly labelClearLoadHandlerHint = $localize`:@@ftsCommandClearLoadHandlerHint:Available when FTS reports waiting for load handling`;
  readonly labelSupervisorCcuReady = $localize`:@@ftsSupervisorCcuReady:CCU: Likely READY`;
  readonly labelSupervisorCcuBusy = $localize`:@@ftsSupervisorCcuBusy:CCU: Likely BUSY`;
  readonly labelSupervisorCcuBlocked = $localize`:@@ftsSupervisorCcuBlocked:CCU: Likely BLOCKED`;
  readonly labelSupervisorCcuUnknown = $localize`:@@ftsSupervisorCcuUnknown:CCU: Unknown (no state)`;
  readonly labelSupervisorCcuBusyDriving = $localize`:@@ftsSupervisorCcuBusyDriving:Driving or waiting for load handling`;
  readonly labelSupervisorCcuBusyAction = $localize`:@@ftsSupervisorCcuBusyAction:Action not finished`;
  readonly labelSupervisorCcuBlockedPaused = $localize`:@@ftsSupervisorCcuBlockedPaused:See details below`;
  readonly labelNavTargetSelect = $localize`:@@ftsCommandNavTargetSelect:Target`;
  readonly labelCommandDisabledNoTelemetry = $localize`:@@ftsCommandDisabledNoTelemetry:Wait for FTS state for this AGV`;
  readonly labelDockDisabledPositionKnown = $localize`:@@ftsDockDisabledPositionKnown:Position already known (node and module)`;
  readonly labelDockDisabledDriving = $localize`:@@ftsDockDisabledDriving:Not available while driving`;
  readonly labelDockDisabledLoadHandling = $localize`:@@ftsDockDisabledLoadHandling:Not available while waiting for load handling`;
  readonly labelChargeStartDisabledDriving = $localize`:@@ftsChargeStartDisabledDriving:Not available while driving`;
  readonly labelChargeStartDisabledLoadHandling = $localize`:@@ftsChargeStartDisabledLoadHandling:Not available while waiting for load handling`;
  readonly labelChargeStopDisabledNotCharging = $localize`:@@ftsChargeStopDisabledNotCharging:Not charging`;
  readonly labelChargeCommandUnavailable = $localize`:@@ftsChargeCommandUnavailable:Charge command not available in this state`;
  readonly badgeTextFtsPosition = $localize`:@@ftsBadgePosition:Position`;
  readonly devModeTitle = $localize`:@@ftsDevModeTitle:Developer Mode (Topics & Payload)`;
  readonly devChargeTitle = $localize`:@@ftsDevChargeTitle:Charge ON/OFF`;
  readonly devDockTitle = $localize`:@@ftsDevDockTitle:Dock to Initial`;
  readonly devNavigateToTargetTitle = $localize`:@@ftsDevNavigateToTargetTitle:Drive to target (from reported position)`;
  readonly devClearLoadHandlerTitle = $localize`:@@ftsDevClearLoadHandlerTitle:Clear load handling (instantAction)`;
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
    'storage_blue_agv2',
    'storage_blue_parallel',
    'track-trace-production-bwr',
    'production_blue_dual_agv_step15',
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
    storage_blue_agv2: $localize`:@@fixtureLabelStorageBlueAgv2:Storage Blue (AGV-2)`,
    storage_blue_parallel: $localize`:@@fixtureLabelStorageBlueParallel:Storage Blue (Both AGVs)`,
    'track-trace-production-bwr': $localize`:@@fixtureLabelTrackTraceBwr:TrackTrace Production BWR`,
    production_blue_dual_agv_step15: $localize`:@@fixtureLabelProductionBlueDualAgv:Production Blue • Dual AGV (step 15 demo)`,
  };
  activeFixture: OrderFixtureName | null = this.dashboard.getCurrentFixture();

  // Observable streams
  ftsState$!: Observable<FtsState | null>;
  batteryState$!: Observable<FtsBatteryState | null>;
  loads$!: Observable<FtsLoadInfo[]>;
  ftsOrder$!: Observable<any | null>;
  
  // FTS position for shopfloor preview (single AGV - backward compat)
  ftsPosition$!: Observable<{ x: number; y: number } | null>;
  // FTS positions for all AGVs (multi-AGV with colors)
  ftsPositions$!: Observable<Array<{ serial: string; x: number; y: number; color?: string }>>;
  
  // Active route segments for animation (currently driving) - from animation service
  activeRouteSegments$!: Observable<Array<{ x1: number; y1: number; x2: number; y2: number }>>;

  /** Last FTS order payload per AGV (all serials in layout) – for multi-AGV route overlay. */
  allAgvOrders$!: Observable<Array<{ serial: string; order: unknown }>>;

  /** Last validated FTS state per AGV topic in MessageMonitor (ensures both markers when `ftsStates$` is incomplete). */
  allAgvMonitorFtsStates$!: Observable<Record<string, FtsState | null>>;

  /** Merged map segments: order-based routes per AGV in AGV colors; selected AGV uses animation path while animating. */
  combinedAgvRouteSegments$!: Observable<Array<{ x1: number; y1: number; x2: number; y2: number; stroke?: string }>>;
  
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
    private readonly mappingService: ShopfloorMappingService,
    private readonly agvRouteService: AgvRouteService,
    private readonly agvAnimationService: AgvAnimationService,
    private readonly languageService: LanguageService,
    private readonly cdr: ChangeDetectorRef,
    private readonly http: HttpClient
  ) {
    // Initialize animation state observable after service is available
    this.animationState$ = this.agvAnimationService.animationState$;
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
    // Initialize route service with layout (also initializes mappingService)
    this.agvRouteService.initializeLayout(config);

    // Ensure selected AGV is in options; default to first AGV if not
    const opts = this.mappingService.getAgvOptions();
    if (opts.length > 0 && !opts.some((o) => o.serial === this.selectedAgvSerial$.value)) {
      this.selectedAgvSerial$.next(opts[0].serial);
    }

    // Re-initialize streams to update position calculation
    this.initializeStreams();
    this.cdr.markForCheck();
  }

  /** AGV options for dropdown (AGV-1, AGV-2); fallback if layout not loaded */
  get agvOptions(): AgvOption[] {
    const opts = this.mappingService.getAgvOptions();
    return opts.length > 0 ? opts : [{ serial: FTS_SERIAL_FALLBACK, label: 'AGV-1' }];
  }

  onSelectedAgvChange(serial: string): void {
    this.selectedAgvSerial$.next(serial);
    this.previousNodeId = null; // Reset animation context when switching AGV
    this.initializeStreams();
    this.cdr.markForCheck();
  }

  /** Display label for AGV by serial (e.g. AGV-1, AGV-2) – for badge/UI */
  getAgvLabel(serial: string): string | null {
    return this.mappingService.getAgvLabel(serial);
  }
  
  /**
   * Compute stationary position: 60% of the route from intersection/road to module center
   * Delegates to AgvRouteService
   */
  private computeStationaryPosition(nodeId: string): ShopfloorPoint | null {
    return this.agvRouteService.computeStationaryPosition(nodeId);
  }
  
  /**
   * Resolve node reference to canonical form
   * Delegates to AgvRouteService
   */
  private resolveNodeRef(value: string | undefined): string | null {
    return this.agvRouteService.resolveNodeRef(value);
  }
  
  /**
   * Find route path using BFS
   * Delegates to AgvRouteService
   */
  private findRoutePath(start: string, target: string): string[] | null {
    return this.agvRouteService.findRoutePath(start, target);
  }

  /**
   * Drawable route segments from FTS order.nodes (each consecutive pair resolved on the layout graph).
   */
  private buildRouteSegmentsFromFtsOrder(order: unknown): Array<{ x1: number; y1: number; x2: number; y2: number }> {
    if (!order || typeof order !== 'object') {
      return [];
    }
    const nodes = (order as { nodes?: Array<{ id?: string }> }).nodes;
    if (!Array.isArray(nodes) || nodes.length < 2) {
      return [];
    }
    const ids = nodes.map((n) => n?.id).filter((id): id is string => Boolean(id));
    if (ids.length < 2) {
      return [];
    }
    const all: Array<{ x1: number; y1: number; x2: number; y2: number }> = [];
    for (let i = 0; i < ids.length - 1; i++) {
      const path = this.agvRouteService.findRoutePath(ids[i], ids[i + 1]);
      if (path && path.length >= 2) {
        all.push(...this.agvRouteService.pathToRouteSegments(path));
      }
    }
    return all;
  }

  /**
   * Find road between two nodes
   * Delegates to AgvRouteService
   */
  private findRoadBetween(a: string, b: string): ParsedRoad | null {
    return this.agvRouteService.findRoadBetween(a, b);
  }
  
  /**
   * Build road segment with trimmed endpoints
   * Delegates to AgvRouteService
   */
  private buildRoadSegment(road: ParsedRoad): { x1: number; y1: number; x2: number; y2: number } | null {
    return this.agvRouteService.buildRoadSegment(road);
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
    const animationState = this.agvAnimationService.getState();
    
    // CRITICAL: If we have an active animation path, NEVER touch the route
    // The route is managed exclusively by the animation logic
    // This prevents the route from being cleared or overwritten during multi-segment animation
    if (animationState.animationPath.length >= 2) {
      // Only check if FTS stopped - then we need to stop animation
      if (!isDriving && animationState.isAnimating) {
        this.agvAnimationService.stopAnimation();
      }
      // Don't process further - let animation complete
      // The route is already set and must remain unchanged
      return;
    }
    
    // During animation, ignore new state changes to prevent route visualization from being disturbed
    if (animationState.isAnimating) {
      // Only check if FTS stopped - then we need to stop animation
      if (!isDriving) {
        this.agvAnimationService.stopAnimation();
      }
      // Don't process further - let animation complete
      return;
    }
    
    // If node changed and driving, animate along the path
    if (newNodeId && this.previousNodeId && newNodeId !== this.previousNodeId) {
      if (isDriving) {
        // Start new animation with callbacks
        this.agvAnimationService.animateBetweenNodes(this.previousNodeId, newNodeId, {
          onAnimationComplete: (finalNodeId) => {
            // Update previousNodeId now that animation is complete
            // This prevents flickering and position resets
            this.previousNodeId = finalNodeId;
            this.cdr.markForCheck();
          },
        });
      } else {
        // FTS stopped - clear animation
        this.agvAnimationService.stopAnimation();
      }
    } else if (!isDriving) {
      // FTS stopped - clear animation
      this.agvAnimationService.stopAnimation();
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
    const animationState = this.agvAnimationService.getState();
    
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
        this.agvAnimationService.animateBetweenNodes(this.previousNodeId, state.lastNodeId, {
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
    this.agvAnimationService.stopAnimation();
    this.subscriptions.unsubscribe();
  }

  private initializeStreams(): void {
    const serial = this.selectedAgvSerial$.value;
    const stateTopic = ftsStateTopic(serial);
    const orderTopic = ftsOrderTopic(serial);

    // Pattern 2: MessageMonitor + Streams; topics depend on selected AGV
    this.ftsState$ = this.messageMonitor.getLastMessage<FtsState>(stateTopic).pipe(
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
      map((s) => s?.batteryState ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Loads stream
    this.loads$ = this.ftsState$.pipe(
      map((s) => s?.load ?? []),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Order stream (for TURN direction etc.) - per selected AGV
    this.ftsOrder$ = this.messageMonitor.getLastMessage<any>(orderTopic).pipe(
      map((msg) => msg?.payload ?? null),
      tap((order) => {
        if (!order) return;
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

    const agvOpts =
      this.mappingService.getAgvOptions().length > 0
        ? this.mappingService.getAgvOptions()
        : [{ serial: FTS_SERIAL_FALLBACK, label: 'AGV-1' }];

    const perAgvOrderStreams = agvOpts.map((opt) =>
      this.messageMonitor.getLastMessage<any>(ftsOrderTopic(opt.serial)).pipe(
        map((msg) => ({ serial: opt.serial, order: msg?.payload ?? null })),
        shareReplay({ bufferSize: 1, refCount: false })
      )
    );

    this.allAgvOrders$ =
      perAgvOrderStreams.length > 0
        ? combineLatest(perAgvOrderStreams)
        : of([] as Array<{ serial: string; order: unknown }>);

    const perAgvMonitorStateStreams = agvOpts.map((opt) =>
      this.messageMonitor.getLastMessage<FtsState>(ftsStateTopic(opt.serial)).pipe(
        map((msg) => (msg !== null && msg.valid ? (msg.payload as FtsState) : null)),
        startWith(null),
        shareReplay({ bufferSize: 1, refCount: false })
      )
    );

    this.allAgvMonitorFtsStates$ =
      perAgvMonitorStateStreams.length > 0
        ? combineLatest(perAgvMonitorStateStreams).pipe(
            map((states) => {
              const rec: Record<string, FtsState | null> = {};
              agvOpts.forEach((opt, i) => {
                rec[opt.serial] = states[i];
              });
              return rec;
            }),
            shareReplay({ bufferSize: 1, refCount: false })
          )
        : of({} as Record<string, FtsState | null>);

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
        
        const animationState = this.agvAnimationService.getState();
        
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
        let nodePos = this.agvRouteService.getNodePosition(nodeId);
        
        // If not found, try canonical lookup via resolveNodeRef
        if (!nodePos) {
          const canonical = this.resolveNodeRef(nodeId);
          if (canonical) {
            nodePos = this.agvRouteService.getNodePosition(canonical);
          }
        }
        
        // If still not found, try serial number mapping
        if (!nodePos) {
          const moduleType = SERIAL_TO_MODULE_TYPE[nodeId];
          if (moduleType) {
            nodePos = this.agvRouteService.getNodePosition(moduleType);
            // Also try serial: prefix
            if (!nodePos) {
              nodePos = this.agvRouteService.getNodePosition(`serial:${moduleType}`);
            }
          }
        }
        
        // If still not found, try intersection: prefix for numeric IDs
        if (!nodePos && nodeId.match(/^\d+$/)) {
          // Try intersection: prefix first (canonical form)
          nodePos = this.agvRouteService.getNodePosition(`intersection:${nodeId}`);
          // Also try direct numeric lookup (alias)
          if (!nodePos) {
            nodePos = this.agvRouteService.getNodePosition(nodeId);
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
          if (this.agvRouteService.isLayoutInitialized()) {
            const availableNodes = this.agvRouteService.getAvailableNodeIds();
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

  this.combinedAgvRouteSegments$ = combineLatest([
    this.animationState$,
    this.allAgvOrders$,
    this.selectedAgvSerial$.pipe(distinctUntilChanged()),
  ]).pipe(
    map(([anim, orders]) => {
      const selected = this.selectedAgvSerial$.value;
      const animSegs = anim?.activeRouteSegments ?? [];
      const useAnimForSelected = Boolean(anim?.isAnimating && animSegs.length > 0);
      const out: Array<{ x1: number; y1: number; x2: number; y2: number; stroke?: string }> = [];

      for (const { serial, order } of orders) {
        const stroke = this.mappingService.getAgvColor(serial);
        if (useAnimForSelected && serial === selected) {
          for (const s of animSegs) {
            out.push({ ...s, stroke });
          }
          continue;
        }
        const fromOrder = this.buildRouteSegmentsFromFtsOrder(order);
        for (const s of fromOrder) {
          out.push({ ...s, stroke });
        }
      }
      return out;
    }),
    distinctUntilChanged((a, b) => {
      if (a.length !== b.length) {
        return false;
      }
      return a.every((item, i) => {
        const o = b[i];
        return (
          o &&
          item.stroke === o.stroke &&
          Math.abs(item.x1 - o.x1) < 0.5 &&
          Math.abs(item.y1 - o.y1) < 0.5 &&
          Math.abs(item.x2 - o.x2) < 0.5 &&
          Math.abs(item.y2 - o.y2) < 0.5
        );
      });
    }),
    shareReplay({ bufferSize: 1, refCount: false })
  );

  // Observable for current position node (for highlighting current position)
  this.currentPositionNode$ = this.ftsState$.pipe(
    map((state) => state?.lastNodeId ? [state.lastNodeId] : null),
    shareReplay({ bufferSize: 1, refCount: false })
  );

  // FTS positions for all AGVs — Route & Position + Presentation (both when telemetry exists)
  this.ftsPositions$ = combineLatest([
    this.dashboard.streams.ftsStates$,
    this.allAgvMonitorFtsStates$,
    this.ftsPosition$,
    this.animationState$.pipe(
      map((a) => a.animatedPosition),
      distinctUntilChanged((p, c) => {
        if (!p && !c) return true;
        if (!p || !c) return false;
        return Math.abs(p.x - c.x) < 2 && Math.abs(p.y - c.y) < 2;
      })
    ),
  ]).pipe(
    map(([ftsStates, monitorStates, singlePosition, animatedPos]) => {
      const opts = this.agvOptions;
      const selectedSerial = this.selectedAgvSerial$.value;
      const animState = this.agvAnimationService.getState();
      const result: Array<{ serial: string; x: number; y: number; color?: string }> = [];

      const resolveRawState = (serial: string): { lastNodeId?: string; driving?: boolean } | undefined => {
        const fromMap =
          (ftsStates[serial] as FtsState | undefined) ??
          (Object.entries(ftsStates).find(([, s]) => (s as FtsState | undefined)?.serialNumber === serial)?.[1] as
            | FtsState
            | undefined);
        const fromMonitor = monitorStates[serial] ?? null;
        const b = fromMap as { lastNodeId?: string; driving?: boolean } | undefined;
        const m = fromMonitor as { lastNodeId?: string; driving?: boolean } | null;
        if (b?.lastNodeId != null && String(b.lastNodeId).length > 0) {
          return b;
        }
        if (m?.lastNodeId != null && String(m.lastNodeId).length > 0) {
          return m;
        }
        return b ?? m ?? undefined;
      };

      for (const opt of opts) {
        const rawState = resolveRawState(opt.serial);
        const nodeId = rawState?.lastNodeId;
        if (!nodeId) continue;
        let pos: { x: number; y: number } | null = null;
        if (opt.serial === selectedSerial && animatedPos && animState.isAnimating && rawState?.driving) {
          pos = animatedPos;
        }
        if (!pos) {
          pos = this.getPositionFromNodeId(nodeId);
        }
        if (pos) {
          result.push({
            serial: opt.serial,
            x: pos.x,
            y: pos.y,
            color: this.mappingService.getAgvColor(opt.serial),
          });
        }
      }

      // Fallback: no multi layout match — selected AGV only from ftsPosition$
      if (result.length === 0 && singlePosition) {
        result.push({
          serial: selectedSerial,
          x: singlePosition.x,
          y: singlePosition.y,
          color: this.mappingService.getAgvColor(selectedSerial),
        });
      }
      return result;
    }),
    distinctUntilChanged((a, b) => {
      if (a.length !== b.length) return false;
      return a.every((item, i) => {
        const o = b[i];
        return o && item.serial === o.serial && Math.abs(item.x - o.x) < 2 && Math.abs(item.y - o.y) < 2;
      });
    }),
    debounceTime(100),
    shareReplay({ bufferSize: 1, refCount: false })
  );
  }

  /** Helper: resolve lastNodeId to shopfloor coordinates */
  private getPositionFromNodeId(nodeId: string): { x: number; y: number } | null {
    let nodePos = this.agvRouteService.getNodePosition(nodeId);
    if (!nodePos) {
      const canonical = this.resolveNodeRef(nodeId);
      if (canonical) nodePos = this.agvRouteService.getNodePosition(canonical);
    }
    if (!nodePos) {
      const moduleType = SERIAL_TO_MODULE_TYPE[nodeId];
      if (moduleType) {
        nodePos = this.agvRouteService.getNodePosition(moduleType) ?? this.agvRouteService.getNodePosition(`serial:${moduleType}`);
      }
    }
    if (!nodePos && nodeId.match(/^\d+$/)) {
      nodePos = this.agvRouteService.getNodePosition(`intersection:${nodeId}`) ?? this.agvRouteService.getNodePosition(nodeId);
    }
    return nodePos ? { x: nodePos.x, y: nodePos.y } : null;
  }

  // Helper methods for template
  getLocationName(nodeId: string | undefined): string {
    if (!nodeId) return $localize`:@@ftsLocationUnknown:Unknown`;
    
    // For intersections, use AgvRouteService mapping
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
    
    // For intersections, use AgvRouteService mapping
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
        storage_blue_agv2: 'track-trace-storage-blue-agv2',
        storage_blue_parallel: 'track-trace-storage-blue-parallel',
        production_blue_dual_agv_step15: 'order-production-blue-dual-agv-step15',
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
      if (dir === 'LEFT') return $localize`:@@ftsActionTurnLeft:TURN LEFT`;
      if (dir === 'RIGHT') return $localize`:@@ftsActionTurnRight:TURN RIGHT`;
      return $localize`:@@ftsActionTurn:TURN`;
    }
    if (cmd === 'DOCK') return $localize`:@@ftsActionDock:DOCK`;
    if (cmd === 'PASS') return $localize`:@@ftsActionPass:PASS`;
    if (cmd === 'PICK') return $localize`:@@ftsActionPick:PICK`;
    if (cmd === 'DROP') return $localize`:@@ftsActionDrop:DROP`;
    if (cmd === 'CLEARLOADHANDLER') return $localize`:@@ftsActionClearLoadHandler:clearLoadHandler`;
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

  onNavTargetModuleChange(value: string): void {
    if (this.navTargetModuleOptions.includes(value as (typeof this.navTargetModuleOptions)[number])) {
      this.selectedNavTargetModule = value as (typeof this.navTargetModuleOptions)[number];
    } else {
      this.selectedNavTargetModule = 'HBW';
    }
  }

  /** Button label e.g. `→ HBW` from {@link selectedNavTargetModule}. */
  getNavigateToTargetButtonLabel(): string {
    return `→ ${this.getNavTargetModuleLabel(this.selectedNavTargetModule)}`;
  }

  get isCharging(): boolean {
    return this.lastFtsState?.batteryState?.charging ?? false;
  }

  get chargeButtonLabel(): string {
    return this.isCharging ? this.labelChargeOff : this.labelChargeOn;
  }

  private getFtsCommandAvailabilityInput(): FtsCommandAvailabilityInput {
    const s = this.lastFtsState;
    if (!s) {
      return { connected: false, charging: false };
    }
    return {
      connected: true,
      lastNodeId: s.lastNodeId,
      lastModuleSerialNumber: s.lastModuleSerialNumber,
      charging: s.batteryState?.charging ?? false,
      driving: s.driving,
      waitingForLoadHandling: s.waitingForLoadHandling,
    };
  }

  canOfferInitialDock(): boolean {
    return ftsCanOfferInitialDockCommand(this.getFtsCommandAvailabilityInput());
  }

  getDockInitialDisabledReason(): string | null {
    if (this.canOfferInitialDock()) {
      return null;
    }
    const input = this.getFtsCommandAvailabilityInput();
    if (!input.connected) {
      return this.labelCommandDisabledNoTelemetry;
    }
    if (input.driving === true) {
      return this.labelDockDisabledDriving;
    }
    if (input.waitingForLoadHandling === true) {
      return this.labelDockDisabledLoadHandling;
    }
    return this.labelDockDisabledPositionKnown;
  }

  canChargeCommandClick(): boolean {
    const input = this.getFtsCommandAvailabilityInput();
    return this.isCharging
      ? ftsCanOfferStopChargeCommand(input)
      : ftsCanOfferStartChargeCommand(input);
  }

  getChargeCommandDisabledReason(): string | null {
    if (this.canChargeCommandClick()) {
      return null;
    }
    const input = this.getFtsCommandAvailabilityInput();
    if (!input.connected) {
      return this.labelCommandDisabledNoTelemetry;
    }
    if (this.isCharging) {
      return this.labelChargeStopDisabledNotCharging;
    }
    if (input.driving === true) {
      return this.labelChargeStartDisabledDriving;
    }
    if (input.waitingForLoadHandling === true) {
      return this.labelChargeStartDisabledLoadHandling;
    }
    return this.labelChargeCommandUnavailable;
  }

  getNavTargetModuleLabel(option: (typeof this.navTargetModuleOptions)[number]): string {
    switch (option) {
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
      case 'IX2':
        return $localize`:@@ftsNavTargetIx2:Intersection 2`;
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
    return $localize`:@@ftsVehicleLabelLong:Automated Guided Vehicle (FTS)`;
  }

  get statusSubtitle(): string {
    return $localize`:@@ftsStatusSubtitle:Real-time status, battery, and route information for the FTS.`;
  }

  get badgeTextVehiclePosition(): string {
    return $localize`:@@ftsBadgePosition:Position`;
  }

  // Example payloads for developer view
  private get selectedAgvSerial(): string {
    return this.selectedAgvSerial$.value;
  }

  private getSelectedNavTargetSerial(): string | null {
    return NAV_TARGET_MAP[this.selectedNavTargetModule] ?? null;
  }

  get chargeExamplePayload() {
    return {
      topic: CCU_SET_CHARGE_TOPIC,
      payload: {
        serialNumber: this.selectedAgvSerial,
        charge: true,
      },
      options: { qos: 1, retain: false },
    };
  }

  get dockExamplePayload() {
    return {
      topic: this.ftsInstantActionTopic,
      payload: {
        serialNumber: this.selectedAgvSerial,
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

  get driveNavigateToTargetExamplePayload() {
    const target = this.getSelectedNavTargetSerial() ?? HBW_SERIAL;
    const start = this.lastFtsState?.lastNodeId ?? DPS_SERIAL;
    const { payload } = this.buildOrderFromTo(start, target);
    return { topic: this.ftsOrderTopic, payload, options: { qos: 1, retain: false } };
  }

  get clearLoadHandlerExamplePayload() {
    return {
      topic: this.ftsInstantActionTopic,
      payload: {
        timestamp: new Date().toISOString(),
        serialNumber: this.selectedAgvSerial,
        actions: [
          {
            actionId: 'clear-load-example',
            actionType: 'clearLoadHandler',
            metadata: { loadDropped: false },
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

  getStateLabel(state: string): string {
    const stateUpper = state.toUpperCase();
    if (stateUpper === 'WAITING') return $localize`:@@ftsStateWaiting:WAITING`;
    if (stateUpper === 'INITIALIZING') return $localize`:@@ftsStateInitializing:INITIALIZING`;
    if (stateUpper === 'RUNNING') return $localize`:@@ftsStateRunning:RUNNING`;
    if (stateUpper === 'FINISHED') return $localize`:@@ftsStateFinished:FINISHED`;
    if (stateUpper === 'FAILED') return $localize`:@@ftsStateFailed:FAILED`;
    return $localize`:@@ftsStateUnknown:UNKNOWN`;
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
    await this.dashboard.commands.setFtsCharge(this.selectedAgvSerial, enable);
  }

  async sendDockInitial(): Promise<void> {
    await this.dashboard.commands.dockFts(this.selectedAgvSerial, DOCK_NODE_DPS);
  }

  /** True if AGV is at the given module (by serial or resolved node). */
  isAgvAtModule(state: FtsState | null, moduleSerial: string): boolean {
    if (!state) return false;
    if (state.lastModuleSerialNumber === moduleSerial) return true;
    if (state.lastNodeId === moduleSerial) return true;
    const resolved = this.resolveNodeRef(state.lastNodeId);
    const canonical = `serial:${moduleSerial}`;
    return resolved === canonical || resolved === moduleSerial;
  }

  /**
   * Loose mirror of CCU `updateFtsAvailability` for supervisor transparency only —
   * the MQTT `fts/.../state` topic remains authoritative.
   */
  getSupervisorCcuReadiness(ftsState: FtsState | null): {
    kind: 'ready' | 'busy' | 'blocked' | 'unknown';
    badgeClass: string;
    line: string;
    detail?: string;
  } {
    if (!ftsState) {
      return { kind: 'unknown', badgeClass: 'ccu-readiness--unknown', line: this.labelSupervisorCcuUnknown };
    }
    const last = ftsState.lastNodeId;
    if (ftsState.paused || last === 'UNKNOWN' || this.ftsStateHasBlockingError(ftsState.errors)) {
      return {
        kind: 'blocked',
        badgeClass: 'ccu-readiness--blocked',
        line: this.labelSupervisorCcuBlocked,
        detail: this.formatSupervisorBlockedDetail(ftsState),
      };
    }
    if (ftsState.driving || ftsState.waitingForLoadHandling) {
      return {
        kind: 'busy',
        badgeClass: 'ccu-readiness--busy',
        line: this.labelSupervisorCcuBusy,
        detail: this.labelSupervisorCcuBusyDriving,
      };
    }
    const action = ftsState.actionState;
    if (action && String(action.state).toUpperCase() !== 'FINISHED') {
      return {
        kind: 'busy',
        badgeClass: 'ccu-readiness--busy',
        line: this.labelSupervisorCcuBusy,
        detail: this.labelSupervisorCcuBusyAction,
      };
    }
    return { kind: 'ready', badgeClass: 'ccu-readiness--ready', line: this.labelSupervisorCcuReady };
  }

  private ftsStateHasBlockingError(errors: unknown[] | undefined): boolean {
    if (!errors?.length) {
      return false;
    }
    return errors.some((e) => {
      if (e && typeof e === 'object' && 'errorLevel' in e) {
        return String((e as { errorLevel?: string }).errorLevel).toUpperCase() === 'FATAL';
      }
      return false;
    });
  }

  private ftsStateFirstFatalErrorSummary(errors: unknown[] | undefined): string | null {
    if (!errors?.length) {
      return null;
    }
    for (const e of errors) {
      if (e && typeof e === 'object' && 'errorLevel' in e) {
        const level = String((e as { errorLevel?: string }).errorLevel).toUpperCase();
        if (level === 'FATAL') {
          const errorType = (e as { errorType?: string }).errorType ?? 'FATAL';
          return `${errorType} (FATAL)`;
        }
      }
    }
    return null;
  }

  private formatSupervisorBlockedDetail(ftsState: FtsState): string {
    const parts: string[] = [];
    if (ftsState.paused) {
      parts.push('Paused');
    }
    if (ftsState.lastNodeId === 'UNKNOWN') {
      parts.push('Last node UNKNOWN');
    }
    const fatal = this.ftsStateFirstFatalErrorSummary(ftsState.errors);
    if (fatal) {
      parts.push(fatal);
    }
    return parts.length > 0 ? parts.join(' · ') : this.labelSupervisorCcuBlockedPaused;
  }

  /** True when FTS reports a usable node for routing (not missing / UNKNOWN). */
  isReportedPositionNavigable(ftsState: FtsState | null): boolean {
    const id = ftsState?.lastNodeId;
    return Boolean(id && id !== 'UNKNOWN');
  }

  getNavigateToTargetDisabledReason(ftsState: FtsState | null): string | null {
    if (this.canDriveToSelectedNavTarget(ftsState)) {
      return null;
    }
    if (!ftsState) {
      return this.labelNavigateNoFtsState;
    }
    if (!this.isReportedPositionNavigable(ftsState)) {
      return this.labelNavigatePositionUnclear;
    }
    const start = this.resolveRouteStartNode(ftsState);
    const targetSerial = this.getSelectedNavTargetSerial();
    if (!start || !targetSerial) {
      return this.labelNavigateToTargetDisabledHint;
    }
    const startRef = this.resolveNodeRef(start) ?? start;
    const targetRef = this.resolveNodeRef(targetSerial) ?? targetSerial;
    if (startRef === targetRef) {
      return this.labelNavigateAlreadyAtTarget;
    }
    if (this.findRoutePath(start, targetSerial) === null) {
      return this.labelNavigateNoRoute;
    }
    return this.labelNavigateToTargetDisabledHint;
  }

  /** From line: always FTS-reported position (no manual start). */
  getSupervisorNavFromSummary(ftsState: FtsState | null): string {
    const node = ftsState?.lastNodeId;
    const loc = node && node !== 'UNKNOWN' ? this.getLocationName(node) : '—';
    const idPart = node && node !== 'UNKNOWN' ? node : '—';
    return `From reported — ${loc} (${idPart})`;
  }

  getSupervisorNavTargetSummary(): string {
    const mod = this.selectedNavTargetModule;
    const serial = this.getSelectedNavTargetSerial();
    const label = this.getNavTargetModuleLabel(mod);
    return serial
      ? `${this.labelSupervisorTarget}: ${label} (${serial})`
      : `${this.labelSupervisorTarget}: ${label}`;
  }

  /** True when FTS is waiting for load/dock handshake — clearLoadHandler can release it (see APS-CCU agv.md). */
  canClearLoadHandling(ftsState: FtsState | null): boolean {
    return Boolean(ftsState?.waitingForLoadHandling);
  }

  async sendClearLoadHandlerSupervisor(): Promise<void> {
    await this.dashboard.commands.clearLoadHandlerFts(this.selectedAgvSerial, { loadDropped: false });
  }

  /**
   * True when a route exists from FTS-reported position to {@link selectedNavTargetModule} and AGV is not already there.
   */
  canDriveToSelectedNavTarget(ftsState: FtsState | null): boolean {
    if (!this.isReportedPositionNavigable(ftsState)) {
      return false;
    }
    const start = this.resolveRouteStartNode(ftsState);
    const targetSerial = this.getSelectedNavTargetSerial();
    if (!start || !targetSerial) return false;
    const startRef = this.resolveNodeRef(start) ?? start;
    const targetRef = this.resolveNodeRef(targetSerial) ?? targetSerial;
    if (startRef === targetRef) return false;
    const path = this.findRoutePath(start, targetSerial);
    return path !== null && path.length >= 1;
  }

  async sendNavigateToTarget(): Promise<void> {
    if (!this.isReportedPositionNavigable(this.lastFtsState)) {
      console.warn('[AGV] Drive to target aborted: no clear reported position (wait for FTS state)');
      return;
    }
    const start = this.resolveRouteStartNode(this.lastFtsState);
    const targetSerial = this.getSelectedNavTargetSerial();
    if (!start || !targetSerial) {
      console.warn('[AGV] Drive to target aborted: missing start or target');
      return;
    }
    const { payload } = this.buildOrderFromTo(start, targetSerial);
    await this.connectionService.publish(this.ftsOrderTopic, payload, { qos: 1 });
  }

  /** Route start: FTS-reported `lastNodeId` only (supervisor target is chosen separately). */
  private resolveRouteStartNode(ftsState: FtsState | null): string | null {
    return ftsState?.lastNodeId ?? null;
  }

  /** Metadata for HBW DOCK actions (matches CCU/storage-order FTS order payloads). */
  private getHbwDockMetadata(): Record<string, unknown> {
    const loads = this.lastFtsState?.load ?? [];
    for (const slot of loads) {
      if (slot.loadType && slot.loadId) {
        return {
          loadId: slot.loadId,
          loadType: slot.loadType,
          loadPosition: slot.loadPosition || '1',
        };
      }
    }
    return {
      loadId: null,
      loadType: null,
      loadPosition: '1',
    };
  }

  /**
   * CCU / VDA payloads use factory-graph ids: module serial only, intersection as `"1"`, `"2"`, …
   * (see `NavigatorService.convertPathToOrder`, session extracts under `data/osf-data/fts-analysis/`).
   */
  private ccuLayoutNodeId(shopfloorRef: string): string {
    if (shopfloorRef.startsWith('serial:')) {
      return shopfloorRef.slice('serial:'.length);
    }
    if (shopfloorRef.startsWith('intersection:')) {
      return shopfloorRef.slice('intersection:'.length);
    }
    return shopfloorRef;
  }

  private invertRoadCardinal(d: ParsedRoad['direction']): ParsedRoad['direction'] {
    const m: Record<ParsedRoad['direction'], ParsedRoad['direction']> = {
      NORTH: 'SOUTH',
      SOUTH: 'NORTH',
      EAST: 'WEST',
      WEST: 'EAST',
    };
    return m[d];
  }

  /** Travel direction from `fromRef` to `toRef` along one layout road (matches CCU directed edges). */
  private travelDirectionAlongRoad(road: ParsedRoad, fromRef: string, toRef: string): ParsedRoad['direction'] | null {
    if (road.from.ref === fromRef && road.to.ref === toRef) {
      return road.direction;
    }
    if (road.from.ref === toRef && road.to.ref === fromRef) {
      return this.invertRoadCardinal(road.direction);
    }
    return null;
  }

  /**
   * Same orthogonality rules as `NavigatorService.inferTurnDirectionFromRoadDirections`.
   * Returns null if directions are equal (caller should emit PASS) or on unexpected pairs.
   */
  private inferTurnLeftRightFromDirections(
    inbound: ParsedRoad['direction'],
    outbound: ParsedRoad['direction'],
  ): 'LEFT' | 'RIGHT' | null {
    if (inbound === outbound) {
      return null;
    }
    if (inbound === 'NORTH') {
      if (outbound === 'EAST') return 'RIGHT';
      if (outbound === 'WEST') return 'LEFT';
    } else if (inbound === 'SOUTH') {
      if (outbound === 'EAST') return 'LEFT';
      if (outbound === 'WEST') return 'RIGHT';
    } else if (inbound === 'EAST') {
      if (outbound === 'NORTH') return 'LEFT';
      if (outbound === 'SOUTH') return 'RIGHT';
    } else if (inbound === 'WEST') {
      if (outbound === 'NORTH') return 'RIGHT';
      if (outbound === 'SOUTH') return 'LEFT';
    }
    return null;
  }

  private intersectionActionForPath(path: string[], idx: number): { type: 'PASS' | 'TURN'; metadata?: Record<string, string> } {
    const inboundRoad = this.findRoadBetween(path[idx - 1], path[idx]);
    const outboundRoad = this.findRoadBetween(path[idx], path[idx + 1]);
    if (!inboundRoad?.direction || !outboundRoad?.direction) {
      return { type: 'PASS' };
    }
    const inDir = this.travelDirectionAlongRoad(inboundRoad, path[idx - 1], path[idx]);
    const outDir = this.travelDirectionAlongRoad(outboundRoad, path[idx], path[idx + 1]);
    if (!inDir || !outDir) {
      return { type: 'PASS' };
    }
    const turn = this.inferTurnLeftRightFromDirections(inDir, outDir);
    if (!turn) {
      return { type: 'PASS' };
    }
    return { type: 'TURN', metadata: { direction: turn } };
  }

  private buildOrderFromTo(startNodeId: string, targetNodeId: string): {
    payload: Record<string, unknown>;
    pathUsed: string[] | null;
  } {
    const path = this.findRoutePath(startNodeId, targetNodeId);
    const nodes: Array<Record<string, unknown>> = [];
    const edges: Array<{ id: string; length: number; linkedNodes: string[] }> = [];
    const targetIsHbw = targetNodeId === HBW_SERIAL;

    if (path && path.length >= 2) {
      const ccuPath = path.map((ref) => this.ccuLayoutNodeId(ref));

      for (let i = 0; i < path.length - 1; i++) {
        const a = path[i];
        const b = path[i + 1];
        const road = this.findRoadBetween(a, b);
        if (road) {
          const fromCcu = this.ccuLayoutNodeId(a);
          const toCcu = this.ccuLayoutNodeId(b);
          edges.push({
            id: `${fromCcu}-${toCcu}`,
            length: road.length,
            linkedNodes: [fromCcu, toCcu],
          });
        }
      }

      const edgeIdAlongPath = (fromIdx: number, toIdx: number): string =>
        `${ccuPath[fromIdx]}-${ccuPath[toIdx]}`;

      for (let idx = 0; idx < path.length; idx++) {
        const ccuId = ccuPath[idx];
        let linkedEdges: string[];
        if (idx === 0) {
          linkedEdges = [edgeIdAlongPath(0, 1)];
        } else if (idx === path.length - 1) {
          linkedEdges = [edgeIdAlongPath(idx - 1, idx)];
        } else {
          linkedEdges = [edgeIdAlongPath(idx - 1, idx), edgeIdAlongPath(idx, idx + 1)];
        }

        if (idx === 0) {
          nodes.push({
            id: ccuId,
            linkedEdges,
          });
          continue;
        }
        const isLast = idx === path.length - 1;
        if (isLast) {
          if (targetIsHbw) {
            nodes.push({
              id: ccuId,
              linkedEdges,
              action: {
                id: this.uuid(),
                type: 'DOCK',
                metadata: this.getHbwDockMetadata(),
              },
            });
          } else {
            nodes.push({
              id: ccuId,
              linkedEdges,
              action: {
                id: `stop-${this.uuid()}`,
                type: 'STOP',
                metadata: {},
              },
            });
          }
          continue;
        }
        const passOrTurn = this.intersectionActionForPath(path, idx);
        nodes.push({
          id: ccuId,
          linkedEdges,
          action: {
            id: this.uuid(),
            type: passOrTurn.type,
            metadata: passOrTurn.metadata ?? {},
          },
        });
      }
    } else {
      nodes.push({
        id: this.ccuLayoutNodeId(targetNodeId),
        linkedEdges: [],
        action: targetIsHbw
          ? {
              id: this.uuid(),
              type: 'DOCK',
              metadata: this.getHbwDockMetadata(),
            }
          : {
              id: `stop-${this.uuid()}`,
              type: 'STOP',
              metadata: {},
            },
      });
    }

    const payload: Record<string, unknown> = {
      timestamp: new Date().toISOString(),
      orderId: this.uuid(),
      orderUpdateId: 0,
      nodes,
      edges,
      serialNumber: this.selectedAgvSerial,
    };

    return { payload, pathUsed: path };
  }

  trackByActionId(_index: number, action: FtsActionState): string {
    return action.id;
  }

  // Removed toggleBatteryDetails - always show details like example app
}

