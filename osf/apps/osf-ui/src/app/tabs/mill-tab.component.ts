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

// MILL Serial Number
const MILL_SERIAL = 'SVR3QA2098';
const MILL_STATE_TOPIC = `module/v1/ff/${MILL_SERIAL}/state`;
const MILL_ORDER_TOPIC = `module/v1/ff/${MILL_SERIAL}/order`;
const MILL_CONNECTION_TOPIC = `module/v1/ff/${MILL_SERIAL}/connection`;

// MILL Types
type ActionStateType = 'WAITING' | 'INITIALIZING' | 'RUNNING' | 'FINISHED' | 'FAILED' | string;
type ActionCommandType = 'MILL' | 'PICK' | 'DROP' | 'factsheetRequest' | string;

interface MillActionState {
  id: string;
  command: ActionCommandType;
  state: ActionStateType;
  timestamp: string;
  result?: 'PASSED' | 'FAILED';
  metadata?: {
    millDepth?: number;
    millSpeed?: number;
    workpieceId?: string;
    workpiece?: {
      type: string;
      workpieceId: string;
      state: string;
    };
  };
}

interface MillState {
  serialNumber: string;
  timestamp: string;
  orderId?: string;
  orderUpdateId?: number;
  connectionState?: 'ONLINE' | 'OFFLINE';
  available?: 'READY' | 'BUSY' | 'ERROR';
  actionState?: MillActionState;
  actionStates?: MillActionState[];
}

@Component({
  standalone: true,
  selector: 'app-mill-tab',
  imports: [CommonModule],
  templateUrl: './mill-tab.component.html',
  styleUrl: './mill-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MillTabComponent implements OnInit, OnDestroy {
  private dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();

  // Observable streams
  millState$!: Observable<MillState | null>;
  connection$!: Observable<any | null>;
  millOrder$!: Observable<any | null>;
  recentActions$!: Observable<MillActionState[]>;

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
  readonly headingIcon = 'assets/svg/shopfloor/stations/mill-station.svg';
  readonly statusIcon = 'assets/svg/ui/heading-modules.svg';
  readonly millIcon = 'assets/svg/ui/heading-sensors.svg';
  readonly historyIcon = 'assets/svg/ui/heading-production.svg';
  readonly connectionOnlineIcon = 'assets/svg/shopfloor/shared/status-online.svg';
  readonly connectionOfflineIcon = 'assets/svg/shopfloor/shared/status-offline.svg';

  // i18n Labels
  readonly headingTitle = $localize`:@@millTabTitle:Milling Station (MILL)`;
  readonly headingSubtitle = $localize`:@@millTabSubtitle:Precision milling operations and monitoring`;
  readonly labelConnection = $localize`:@@millLabelConnection:Connection`;
  readonly labelAvailability = $localize`:@@millLabelAvailability:Availability`;
  readonly labelCurrentAction = $localize`:@@millLabelCurrentAction:Current Action`;
  readonly labelMillingInfo = $localize`:@@millLabelMillingInfo:Milling Information`;
  readonly labelCommandHistory = $localize`:@@millLabelHistory:Command History`;
  readonly labelMillDepth = $localize`:@@millLabelDepth:Mill Depth`;
  readonly labelMillSpeed = $localize`:@@millLabelSpeed:Mill Speed`;
  readonly labelWorkpieceId = $localize`:@@millLabelWorkpieceId:Workpiece ID`;
  readonly statusOnline = $localize`:@@commonStatusOnline:Online`;
  readonly statusOffline = $localize`:@@commonStatusOffline:Offline`;
  readonly statusReady = $localize`:@@commonStatusReady:Ready`;
  readonly statusBusy = $localize`:@@commonStatusBusy:Busy`;
  readonly statusError = $localize`:@@commonStatusError:Error`;
  readonly labelSerialNumber = $localize`:@@millLabelSerialNumber:Serial Number`;
  readonly labelOrderId = $localize`:@@millLabelOrderId:Order ID`;
  readonly labelNoOrder = $localize`:@@millLabelNoOrder:No Order`;
  readonly labelCommand = $localize`:@@millLabelCommand:Command`;
  readonly labelState = $localize`:@@millLabelState:State`;
  readonly labelResult = $localize`:@@millLabelResult:Result`;
  readonly labelTimestamp = $localize`:@@millLabelTimestamp:Timestamp`;
  readonly stateWaiting = $localize`:@@millStateWaiting:WAITING`;
  readonly stateInitializing = $localize`:@@millStateInitializing:INITIALIZING`;
  readonly stateRunning = $localize`:@@millStateRunning:RUNNING`;
  readonly stateFinished = $localize`:@@millStateFinished:FINISHED`;
  readonly stateFailed = $localize`:@@millStateFailed:FAILED`;
  readonly resultPassed = $localize`:@@millResultPassed:PASSED`;
  readonly resultFailed = $localize`:@@millResultFailed:FAILED`;

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
    // MILL State stream
    this.millState$ = this.messageMonitor.getLastMessage<MillState>(MILL_STATE_TOPIC).pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload as MillState),
      startWith(null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Connection stream
    this.connection$ = this.messageMonitor.getLastMessage<any>(MILL_CONNECTION_TOPIC).pipe(
      map((msg) => msg?.payload ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Order stream
    this.millOrder$ = this.messageMonitor.getLastMessage<any>(MILL_ORDER_TOPIC).pipe(
      map((msg) => msg?.payload ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Recent actions stream - updates whenever state messages arrive
    this.recentActions$ = this.messageMonitor.getLastMessage<MillState>(MILL_STATE_TOPIC).pipe(
      map(() => {
        // Build history from all messages in the monitor
        try {
          const history = this.messageMonitor.getHistory(MILL_STATE_TOPIC);
          const actions: MillActionState[] = [];
          
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
          console.warn('[MILL Tab] Failed to get action history:', error);
          return [];
        }
      }),
      startWith([]),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  // Helper methods for template
  getConnectionStatus(state: MillState | null): 'ONLINE' | 'OFFLINE' {
    return state?.connectionState ?? 'OFFLINE';
  }

  getAvailability(state: MillState | null): string {
    return state?.available ?? 'UNKNOWN';
  }

  getCurrentAction(state: MillState | null): MillActionState | null {
    return state?.actionState ?? null;
  }

  getRecentActions(state: MillState | null): MillActionState[] {
    // First, try to get from actionStates array if available (mock mode)
    if (state?.actionStates && state.actionStates.length > 0) {
      return state.actionStates.slice(-10).reverse();
    }
    
    // Otherwise, build history from message monitor (replay/live mode)
    try {
      const history = this.messageMonitor.getHistory(MILL_STATE_TOPIC);
      const actions: MillActionState[] = [];
      
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
      console.warn('[MILL Tab] Failed to get action history:', error);
      return [];
    }
  }

  getMillDepth(state: MillState | null): number | null {
    return state?.actionState?.metadata?.millDepth ?? null;
  }

  getMillSpeed(state: MillState | null): number | null {
    return state?.actionState?.metadata?.millSpeed ?? null;
  }

  getWorkpieceId(state: MillState | null): string | null {
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

  trackByActionId(_index: number, action: MillActionState): string {
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
      console.info('[MILL Tab] Replay mode - MILL data should come from MQTT broker');
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
      console.warn('Failed to load MILL fixture', fixture, error);
      console.warn('[MILL Tab] Note: MILL topics may not be included in standard fixtures. Consider using replay environment.');
    }
  }
}
