import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { filter, map, shareReplay, startWith } from 'rxjs/operators';
import { Observable, Subscription } from 'rxjs';
import { EnvironmentService } from '../services/environment.service';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ConnectionService } from '../services/connection.service';
import { ModuleNameService } from '../services/module-name.service';
import { getDashboardController } from '../mock-dashboard';
import type { OrderFixtureName } from '@osf/testing-fixtures';

// DRILL Serial Number
const DRILL_SERIAL = 'SVR4H76449';
const DRILL_STATE_TOPIC = `module/v1/ff/${DRILL_SERIAL}/state`;
const DRILL_ORDER_TOPIC = `module/v1/ff/${DRILL_SERIAL}/order`;
const DRILL_CONNECTION_TOPIC = `module/v1/ff/${DRILL_SERIAL}/connection`;

// DRILL Types
type ActionStateType = 'WAITING' | 'INITIALIZING' | 'RUNNING' | 'FINISHED' | 'FAILED' | string;
type ActionCommandType = 'DRILL' | 'PICK' | 'DROP' | 'factsheetRequest' | string;

interface DrillActionState {
  id: string;
  command: ActionCommandType;
  state: ActionStateType;
  timestamp: string;
  result?: 'PASSED' | 'FAILED';
  metadata?: {
    drillDepth?: number;
    drillSpeed?: number;
    workpieceId?: string;
    workpiece?: {
      type: string;
      workpieceId: string;
      state: string;
    };
  };
}

interface DrillState {
  serialNumber: string;
  timestamp: string;
  orderId?: string;
  orderUpdateId?: number;
  connectionState?: 'ONLINE' | 'OFFLINE';
  available?: 'READY' | 'BUSY' | 'ERROR';
  actionState?: DrillActionState;
  actionStates?: DrillActionState[];
}

@Component({
  standalone: true,
  selector: 'app-drill-tab',
  imports: [CommonModule],
  templateUrl: './drill-tab.component.html',
  styleUrl: './drill-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DrillTabComponent implements OnInit, OnDestroy {
  private dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();

  // Observable streams
  drillState$!: Observable<DrillState | null>;
  connection$!: Observable<any | null>;
  drillOrder$!: Observable<any | null>;
  recentActions$!: Observable<DrillActionState[]>;

  // Fixtures for testing
  readonly fixtureOptions: OrderFixtureName[] = [
    'startup',
    'production_bwr',
  ];
  readonly fixtureLabels: Partial<Record<OrderFixtureName, string>> = {
    startup: $localize`:@@fixtureLabelStartup:Startup`,
    production_bwr: $localize`:@@fixtureLabelProductionBwr:Production BWR`,
  };
  activeFixture: OrderFixtureName | null = this.dashboard.getCurrentFixture();

  // Icons
  readonly headingIcon = 'assets/svg/shopfloor/stations/drill-station.svg';
  readonly statusIcon = 'assets/svg/ui/heading-modules.svg';
  readonly drillIcon = 'assets/svg/ui/heading-sensors.svg';
  readonly historyIcon = 'assets/svg/ui/heading-production.svg';
  readonly connectionOnlineIcon = 'assets/svg/shopfloor/shared/status-online.svg';
  readonly connectionOfflineIcon = 'assets/svg/shopfloor/shared/status-offline.svg';

  // i18n Labels
  readonly headingTitle = $localize`:@@drillTabTitle:Drilling Station (DRILL)`;
  readonly headingSubtitle = $localize`:@@drillTabSubtitle:Precision drilling operations and monitoring`;
  readonly labelConnection = $localize`:@@drillLabelConnection:Connection`;
  readonly labelAvailability = $localize`:@@drillLabelAvailability:Availability`;
  readonly labelCurrentAction = $localize`:@@drillLabelCurrentAction:Current Action`;
  readonly labelDrillingInfo = $localize`:@@drillLabelDrillingInfo:Drilling Information`;
  readonly labelCommandHistory = $localize`:@@drillLabelHistory:Command History`;
  readonly labelDrillDepth = $localize`:@@drillLabelDepth:Drill Depth`;
  readonly labelDrillSpeed = $localize`:@@drillLabelSpeed:Drill Speed`;
  readonly labelWorkpieceId = $localize`:@@drillLabelWorkpieceId:Workpiece ID`;
  readonly statusOnline = $localize`:@@commonStatusOnline:Online`;
  readonly statusOffline = $localize`:@@commonStatusOffline:Offline`;
  readonly statusReady = $localize`:@@commonStatusReady:Ready`;
  readonly statusBusy = $localize`:@@commonStatusBusy:Busy`;
  readonly statusError = $localize`:@@commonStatusError:Error`;
  readonly labelSerialNumber = $localize`:@@drillLabelSerialNumber:Serial Number`;
  readonly labelOrderId = $localize`:@@drillLabelOrderId:Order ID`;
  readonly labelNoOrder = $localize`:@@drillLabelNoOrder:No Order`;
  readonly labelCommand = $localize`:@@drillLabelCommand:Command`;
  readonly labelState = $localize`:@@drillLabelState:State`;
  readonly labelResult = $localize`:@@drillLabelResult:Result`;
  readonly labelTimestamp = $localize`:@@drillLabelTimestamp:Timestamp`;
  readonly stateWaiting = $localize`:@@drillStateWaiting:WAITING`;
  readonly stateInitializing = $localize`:@@drillStateInitializing:INITIALIZING`;
  readonly stateRunning = $localize`:@@drillStateRunning:RUNNING`;
  readonly stateFinished = $localize`:@@drillStateFinished:FINISHED`;
  readonly stateFailed = $localize`:@@drillStateFailed:FAILED`;
  readonly resultPassed = $localize`:@@drillResultPassed:PASSED`;
  readonly resultFailed = $localize`:@@drillResultFailed:FAILED`;

  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly environmentService: EnvironmentService,
    private readonly connectionService: ConnectionService,
    private readonly moduleNameService: ModuleNameService,
    private readonly cdr: ChangeDetectorRef,
  ) {
    this.initializeStreams();
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
    this.subscriptions.unsubscribe();
  }

  private initializeStreams(): void {
    // DRILL State stream
    this.drillState$ = this.messageMonitor.getLastMessage<DrillState>(DRILL_STATE_TOPIC).pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload as DrillState),
      startWith(null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Connection stream
    this.connection$ = this.messageMonitor.getLastMessage<any>(DRILL_CONNECTION_TOPIC).pipe(
      map((msg) => msg?.payload ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Order stream
    this.drillOrder$ = this.messageMonitor.getLastMessage<any>(DRILL_ORDER_TOPIC).pipe(
      map((msg) => msg?.payload ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Recent actions stream - updates whenever state messages arrive
    this.recentActions$ = this.messageMonitor.getLastMessage<DrillState>(DRILL_STATE_TOPIC).pipe(
      map(() => {
        // Build history from all messages in the monitor
        try {
          const history = this.messageMonitor.getHistory(DRILL_STATE_TOPIC);
          const actions: DrillActionState[] = [];
          
          // Extract actionState from each historical message
          for (const msg of history) {
            try {
              const payload = typeof msg.payload === 'string' ? JSON.parse(msg.payload) : msg.payload;
              if (payload?.actionState) {
                actions.push(payload.actionState);
              }
            } catch (error) {
              // Skip invalid messages
            }
          }
          
          // Return last 10 actions in reverse order (newest first)
          return actions.slice(-10).reverse();
        } catch (error) {
          console.warn('[DRILL Tab] Failed to get action history:', error);
          return [];
        }
      }),
      startWith([]),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  // Helper methods for template
  getConnectionStatus(state: DrillState | null): 'ONLINE' | 'OFFLINE' {
    return state?.connectionState ?? 'OFFLINE';
  }

  getAvailability(state: DrillState | null): string {
    return state?.available ?? 'UNKNOWN';
  }

  getCurrentAction(state: DrillState | null): DrillActionState | null {
    return state?.actionState ?? null;
  }

  getRecentActions(state: DrillState | null): DrillActionState[] {
    // First, try to get from actionStates array if available (mock mode)
    if (state?.actionStates && state.actionStates.length > 0) {
      return state.actionStates.slice(-10).reverse();
    }
    
    // Otherwise, build history from message monitor (replay/live mode)
    try {
      const history = this.messageMonitor.getHistory(DRILL_STATE_TOPIC);
      const actions: DrillActionState[] = [];
      
      // Extract actionState from each historical message
      for (const msg of history) {
        try {
          const payload = typeof msg.payload === 'string' ? JSON.parse(msg.payload) : msg.payload;
          if (payload?.actionState) {
            actions.push(payload.actionState);
          }
        } catch (error) {
          // Skip invalid messages
        }
      }
      
      // Return last 10 actions in reverse order (newest first)
      return actions.slice(-10).reverse();
    } catch (error) {
      console.warn('[DRILL Tab] Failed to get action history:', error);
      return [];
    }
  }

  getDrillDepth(state: DrillState | null): number | null {
    return state?.actionState?.metadata?.drillDepth ?? null;
  }

  getDrillSpeed(state: DrillState | null): number | null {
    return state?.actionState?.metadata?.drillSpeed ?? null;
  }

  getWorkpieceId(state: DrillState | null): string | null {
    return state?.actionState?.metadata?.workpieceId ?? null;
  }

  getStateLabel(state: ActionStateType): string {
    const stateUpper = state.toUpperCase();
    if (stateUpper === 'WAITING') return this.stateWaiting;
    if (stateUpper === 'INITIALIZING') return this.stateInitializing;
    if (stateUpper === 'RUNNING') return this.stateRunning;
    if (stateUpper === 'FINISHED') return this.stateFinished;
    if (stateUpper === 'FAILED') return this.stateFailed;
    return state;
  }

  getStateClass(state: ActionStateType): string {
    const stateUpper = state.toUpperCase();
    if (stateUpper === 'WAITING') return 'waiting';
    if (stateUpper === 'INITIALIZING') return 'initializing';
    if (stateUpper === 'RUNNING') return 'running';
    if (stateUpper === 'FINISHED') return 'finished';
    if (stateUpper === 'FAILED') return 'failed';
    return 'unknown';
  }

  getResultLabel(result: 'PASSED' | 'FAILED' | undefined): string {
    if (!result) return '-';
    return result === 'PASSED' ? this.resultPassed : this.resultFailed;
  }

  getResultClass(result: 'PASSED' | 'FAILED' | undefined): string {
    if (!result) return '';
    return result.toLowerCase();
  }

  formatTimestamp(timestamp: string): string {
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  }

  getOrderIdDisplay(orderId: string | undefined): string {
    if (!orderId) return this.labelNoOrder;
    return orderId.length > 12 ? `${orderId.substring(0, 12)}...` : orderId;
  }

  trackByActionId(_index: number, action: DrillActionState): string {
    return action.id;
  }

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  get isReplayMode(): boolean {
    return this.environmentService.current.key === 'replay';
  }

  async loadFixture(fixture: OrderFixtureName): Promise<void> {
    // In replay mode, fixtures are loaded from MQTT broker, not from local files
    if (this.isReplayMode) {
      console.info('[DRILL Tab] Replay mode - DRILL data should come from MQTT broker');
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
        production_bwr: 'track-trace-production-bwr',
      };
      
      const preset = presetMap[fixture] || 'startup';
      await this.dashboard.loadTabFixture(preset);
      
      // Re-initialize streams after fixture load
      this.initializeStreams();
      
      // Trigger change detection to update UI
      this.cdr.markForCheck();
    } catch (error) {
      console.warn('Failed to load DRILL fixture', fixture, error);
      console.warn('[DRILL Tab] Note: DRILL topics may not be included in standard fixtures. Consider using replay environment.');
    }
  }
}
