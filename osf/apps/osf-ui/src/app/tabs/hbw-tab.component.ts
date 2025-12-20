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

// HBW Serial Number
const HBW_SERIAL = 'SVR3QA0022';
const HBW_STATE_TOPIC = `module/v1/ff/${HBW_SERIAL}/state`;
const HBW_ORDER_TOPIC = `module/v1/ff/${HBW_SERIAL}/order`;
const HBW_CONNECTION_TOPIC = `module/v1/ff/${HBW_SERIAL}/connection`;

// HBW Types
type ActionStateType = 'WAITING' | 'INITIALIZING' | 'RUNNING' | 'FINISHED' | 'FAILED' | string;
type ActionCommandType = 'PICK' | 'DROP' | 'factsheetRequest' | string;

interface HbwActionState {
  id: string;
  command: ActionCommandType;
  state: ActionStateType;
  timestamp: string;
  result?: 'PASSED' | 'FAILED';
  metadata?: {
    slot?: string;
    level?: string;
    workpieceId?: string;
    workpiece?: {
      type: string;
      workpieceId: string;
      state: string;
    };
  };
}

interface HbwState {
  serialNumber: string;
  timestamp: string;
  orderId?: string;
  orderUpdateId?: number;
  connectionState?: 'ONLINE' | 'OFFLINE';
  available?: 'READY' | 'BUSY' | 'ERROR';
  actionState?: HbwActionState;
  actionStates?: HbwActionState[];
}

@Component({
  standalone: true,
  selector: 'app-hbw-tab',
  imports: [CommonModule],
  templateUrl: './hbw-tab.component.html',
  styleUrl: './hbw-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HbwTabComponent implements OnInit, OnDestroy {
  private dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();

  // Observable streams
  hbwState$!: Observable<HbwState | null>;
  connection$!: Observable<any | null>;
  hbwOrder$!: Observable<any | null>;
  recentActions$!: Observable<HbwActionState[]>;

  // Fixtures for testing
  readonly fixtureOptions: OrderFixtureName[] = [
    'startup',
    'storage_blue',
    'production_bwr',
  ];
  readonly fixtureLabels: Partial<Record<OrderFixtureName, string>> = {
    startup: $localize`:@@fixtureLabelStartup:Startup`,
    storage_blue: $localize`:@@fixtureLabelStorageBlue:Storage Blue`,
    production_bwr: $localize`:@@fixtureLabelProductionBwr:Production BWR`,
  };
  activeFixture: OrderFixtureName | null = this.dashboard.getCurrentFixture();

  // Icons
  readonly headingIcon = 'assets/svg/shopfloor/stations/hbw-station.svg';
  readonly statusIcon = 'assets/svg/ui/heading-modules.svg';
  readonly storageIcon = 'assets/svg/ui/heading-inventory.svg';
  readonly historyIcon = 'assets/svg/ui/heading-production.svg';
  readonly connectionOnlineIcon = 'assets/svg/shopfloor/shared/status-online.svg';
  readonly connectionOfflineIcon = 'assets/svg/shopfloor/shared/status-offline.svg';

  // i18n Labels
  readonly headingTitle = $localize`:@@hbwTabTitle:High-Bay Warehouse (HBW)`;
  readonly headingSubtitle = $localize`:@@hbwTabSubtitle:Automated storage and retrieval system`;
  readonly labelConnection = $localize`:@@hbwLabelConnection:Connection`;
  readonly labelAvailability = $localize`:@@hbwLabelAvailability:Availability`;
  readonly labelCurrentAction = $localize`:@@hbwLabelCurrentAction:Current Action`;
  readonly labelStorageInfo = $localize`:@@hbwLabelStorageInfo:Storage Information`;
  readonly labelCommandHistory = $localize`:@@hbwLabelHistory:Command History`;
  readonly labelSlot = $localize`:@@hbwLabelSlot:Slot`;
  readonly labelLevel = $localize`:@@hbwLabelLevel:Level`;
  readonly labelWorkpieceId = $localize`:@@hbwLabelWorkpieceId:Workpiece ID`;
  readonly statusOnline = $localize`:@@commonStatusOnline:Online`;
  readonly statusOffline = $localize`:@@commonStatusOffline:Offline`;
  readonly statusReady = $localize`:@@commonStatusReady:Ready`;
  readonly statusBusy = $localize`:@@commonStatusBusy:Busy`;
  readonly statusError = $localize`:@@commonStatusError:Error`;
  readonly labelSerialNumber = $localize`:@@hbwLabelSerialNumber:Serial Number`;
  readonly labelOrderId = $localize`:@@hbwLabelOrderId:Order ID`;
  readonly labelNoOrder = $localize`:@@hbwLabelNoOrder:No Order`;
  readonly labelCommand = $localize`:@@hbwLabelCommand:Command`;
  readonly labelState = $localize`:@@hbwLabelState:State`;
  readonly labelResult = $localize`:@@hbwLabelResult:Result`;
  readonly labelTimestamp = $localize`:@@hbwLabelTimestamp:Timestamp`;
  readonly stateWaiting = $localize`:@@hbwStateWaiting:WAITING`;
  readonly stateInitializing = $localize`:@@hbwStateInitializing:INITIALIZING`;
  readonly stateRunning = $localize`:@@hbwStateRunning:RUNNING`;
  readonly stateFinished = $localize`:@@hbwStateFinished:FINISHED`;
  readonly stateFailed = $localize`:@@hbwStateFailed:FAILED`;
  readonly resultPassed = $localize`:@@hbwResultPassed:PASSED`;
  readonly resultFailed = $localize`:@@hbwResultFailed:FAILED`;
  readonly labelNoSlot = $localize`:@@hbwLabelNoSlot:No Slot`;
  readonly labelNoLevel = $localize`:@@hbwLabelNoLevel:No Level`;

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
    // HBW State stream
    this.hbwState$ = this.messageMonitor.getLastMessage<HbwState>(HBW_STATE_TOPIC).pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload as HbwState),
      startWith(null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Connection stream
    this.connection$ = this.messageMonitor.getLastMessage<any>(HBW_CONNECTION_TOPIC).pipe(
      map((msg) => msg?.payload ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Order stream
    this.hbwOrder$ = this.messageMonitor.getLastMessage<any>(HBW_ORDER_TOPIC).pipe(
      map((msg) => msg?.payload ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Recent actions stream - updates whenever state messages arrive
    this.recentActions$ = this.messageMonitor.getLastMessage<HbwState>(HBW_STATE_TOPIC).pipe(
      map(() => {
        // Build history from all messages in the monitor
        try {
          const history = this.messageMonitor.getHistory(HBW_STATE_TOPIC);
          const actions: HbwActionState[] = [];
          
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
          console.warn('[HBW Tab] Failed to get action history:', error);
          return [];
        }
      }),
      startWith([]),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  // Helper methods for template
  getConnectionStatus(state: HbwState | null): 'ONLINE' | 'OFFLINE' {
    return state?.connectionState ?? 'OFFLINE';
  }

  getAvailability(state: HbwState | null): string {
    return state?.available ?? 'UNKNOWN';
  }

  getCurrentAction(state: HbwState | null): HbwActionState | null {
    return state?.actionState ?? null;
  }

  getRecentActions(state: HbwState | null): HbwActionState[] {
    // First, try to get from actionStates array if available (mock mode)
    if (state?.actionStates && state.actionStates.length > 0) {
      return state.actionStates.slice(-10).reverse();
    }
    
    // Otherwise, build history from message monitor (replay/live mode)
    try {
      const history = this.messageMonitor.getHistory(HBW_STATE_TOPIC);
      const actions: HbwActionState[] = [];
      
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
      console.warn('[HBW Tab] Failed to get action history:', error);
      return [];
    }
  }

  getStorageSlot(state: HbwState | null): string | null {
    return state?.actionState?.metadata?.slot ?? null;
  }

  getStorageLevel(state: HbwState | null): string | null {
    return state?.actionState?.metadata?.level ?? null;
  }

  getWorkpieceId(state: HbwState | null): string | null {
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

  trackByActionId(_index: number, action: HbwActionState): string {
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
      console.info('[HBW Tab] Replay mode - HBW data should come from MQTT broker');
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
        storage_blue: 'track-trace-storage-blue',
        production_bwr: 'track-trace-production-bwr',
      };
      
      const preset = presetMap[fixture] || 'startup';
      await this.dashboard.loadTabFixture(preset);
      
      // Re-initialize streams after fixture load
      this.initializeStreams();
      
      // Trigger change detection to update UI
      this.cdr.markForCheck();
    } catch (error) {
      console.warn('Failed to load HBW fixture', fixture, error);
      console.warn('[HBW Tab] Note: HBW topics may not be included in standard fixtures. Consider using replay environment.');
    }
  }
}
