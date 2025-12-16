import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { filter, map, shareReplay, startWith } from 'rxjs/operators';
import { Observable, Subscription } from 'rxjs';
import { EnvironmentService } from '../services/environment.service';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ConnectionService } from '../services/connection.service';
import { ModuleNameService } from '../services/module-name.service';

// AIQS Serial Number
const AIQS_SERIAL = 'SVR4H76530';
const AIQS_STATE_TOPIC = `module/v1/ff/${AIQS_SERIAL}/state`;
const AIQS_ORDER_TOPIC = `module/v1/ff/${AIQS_SERIAL}/order`;
const AIQS_CONNECTION_TOPIC = `module/v1/ff/${AIQS_SERIAL}/connection`;
const AIQS_NODERED_STATE_TOPIC = `module/v1/ff/NodeRed/${AIQS_SERIAL}/state`;

// AIQS Types
type ActionStateType = 'WAITING' | 'INITIALIZING' | 'RUNNING' | 'FINISHED' | 'FAILED' | string;
type ActionCommandType = 'CHECK_QUALITY' | 'PICK' | 'DROP' | string;
type QualityResult = 'PASSED' | 'FAILED';

interface AiqsActionState {
  id: string;
  command: ActionCommandType;
  state: ActionStateType;
  timestamp: string;
  result?: QualityResult;
  metadata?: Record<string, unknown>;
}

interface AiqsState {
  serialNumber: string;
  timestamp: string;
  orderId?: string;
  orderUpdateId?: number;
  connectionState?: 'ONLINE' | 'OFFLINE';
  available?: 'READY' | 'BUSY' | 'ERROR';
  actionState?: AiqsActionState;
  actionStates?: AiqsActionState[];
}

@Component({
  standalone: true,
  selector: 'app-aiqs-tab',
  imports: [CommonModule],
  templateUrl: './aiqs-tab.component.html',
  styleUrl: './aiqs-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AiqsTabComponent implements OnInit, OnDestroy {
  private readonly subscriptions = new Subscription();

  // Observable streams
  aiqsState$!: Observable<AiqsState | null>;
  connection$!: Observable<any | null>;
  aiqsOrder$!: Observable<any | null>;

  // Icons
  readonly headingIcon = 'assets/svg/shopfloor/stations/aiqs-station.svg';
  readonly statusIcon = 'assets/svg/ui/heading-modules.svg';
  readonly qualityIcon = 'assets/svg/ui/heading-sensors.svg';
  readonly historyIcon = 'assets/svg/ui/heading-production.svg';
  readonly connectionOnlineIcon = 'assets/svg/shopfloor/shared/status-online.svg';
  readonly connectionOfflineIcon = 'assets/svg/shopfloor/shared/status-offline.svg';
  readonly passedIcon = 'assets/svg/shopfloor/shared/status-online.svg';
  readonly failedIcon = 'assets/svg/shopfloor/shared/status-offline.svg';

  // i18n Labels
  readonly headingTitle = $localize`:@@aiqsTabTitle:AI Quality System (AIQS)`;
  readonly headingSubtitle = $localize`:@@aiqsTabSubtitle:ML-based quality inspection and defect detection`;
  readonly labelConnection = $localize`:@@aiqsLabelConnection:Connection`;
  readonly labelAvailability = $localize`:@@aiqsLabelAvailability:Availability`;
  readonly labelCurrentAction = $localize`:@@aiqsLabelCurrentAction:Current Action`;
  readonly labelQualityResults = $localize`:@@aiqsLabelResults:Quality Results`;
  readonly labelTotalChecks = $localize`:@@aiqsLabelTotal:Total Checks`;
  readonly labelPassed = $localize`:@@aiqsLabelPassed:Passed`;
  readonly labelFailed = $localize`:@@aiqsLabelFailed:Failed`;
  readonly labelSuccessRate = $localize`:@@aiqsLabelSuccessRate:Success Rate`;
  readonly labelCheckHistory = $localize`:@@aiqsLabelHistory:Check History`;
  readonly statusPassed = $localize`:@@aiqsStatusPassed:PASSED`;
  readonly statusFailed = $localize`:@@aiqsStatusFailed:FAILED`;
  readonly commandCheckQuality = $localize`:@@aiqsCommandCheck:CHECK_QUALITY`;
  readonly commandPick = $localize`:@@aiqsCommandPick:PICK`;
  readonly commandDrop = $localize`:@@aiqsCommandDrop:DROP`;
  readonly statusOnline = $localize`:@@commonStatusOnline:Online`;
  readonly statusOffline = $localize`:@@commonStatusOffline:Offline`;
  readonly statusReady = $localize`:@@commonStatusReady:Ready`;
  readonly statusBusy = $localize`:@@commonStatusBusy:Busy`;
  readonly statusError = $localize`:@@commonStatusError:Error`;
  readonly labelSerialNumber = $localize`:@@aiqsLabelSerialNumber:Serial Number`;
  readonly labelOrderId = $localize`:@@aiqsLabelOrderId:Order ID`;
  readonly labelNoOrder = $localize`:@@aiqsLabelNoOrder:No Order`;
  readonly labelCommand = $localize`:@@aiqsLabelCommand:Command`;
  readonly labelState = $localize`:@@aiqsLabelState:State`;
  readonly labelResult = $localize`:@@aiqsLabelResult:Result`;
  readonly labelTimestamp = $localize`:@@aiqsLabelTimestamp:Timestamp`;
  readonly stateWaiting = $localize`:@@aiqsStateWaiting:WAITING`;
  readonly stateInitializing = $localize`:@@aiqsStateInitializing:INITIALIZING`;
  readonly stateRunning = $localize`:@@aiqsStateRunning:RUNNING`;
  readonly stateFinished = $localize`:@@aiqsStateFinished:FINISHED`;
  readonly stateFailed = $localize`:@@aiqsStateFailed:FAILED`;

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
    // AIQS State stream
    this.aiqsState$ = this.messageMonitor.getLastMessage<AiqsState>(AIQS_STATE_TOPIC).pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload as AiqsState),
      startWith(null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Connection stream
    this.connection$ = this.messageMonitor.getLastMessage<any>(AIQS_CONNECTION_TOPIC).pipe(
      map((msg) => msg?.payload ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Order stream
    this.aiqsOrder$ = this.messageMonitor.getLastMessage<any>(AIQS_ORDER_TOPIC).pipe(
      map((msg) => msg?.payload ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  // Helper methods for template
  getConnectionStatus(state: AiqsState | null): 'ONLINE' | 'OFFLINE' {
    return state?.connectionState ?? 'OFFLINE';
  }

  getAvailability(state: AiqsState | null): string {
    return state?.available ?? 'UNKNOWN';
  }

  getCurrentAction(state: AiqsState | null): AiqsActionState | null {
    return state?.actionState ?? null;
  }

  getRecentActions(state: AiqsState | null): AiqsActionState[] {
    return state?.actionStates?.slice(-10).reverse() ?? [];
  }

  getQualityChecks(state: AiqsState | null): AiqsActionState[] {
    return state?.actionStates?.filter(a => a.command === 'CHECK_QUALITY') ?? [];
  }

  getTotalChecks(state: AiqsState | null): number {
    return this.getQualityChecks(state).length;
  }

  getPassedCount(state: AiqsState | null): number {
    return this.getQualityChecks(state).filter(a => a.result === 'PASSED').length;
  }

  getFailedCount(state: AiqsState | null): number {
    return this.getQualityChecks(state).filter(a => a.result === 'FAILED').length;
  }

  getSuccessRate(state: AiqsState | null): number {
    const total = this.getTotalChecks(state);
    if (total === 0) return 0;
    const passed = this.getPassedCount(state);
    return Math.round((passed / total) * 100);
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

  getResultLabel(result: QualityResult | undefined): string {
    if (!result) return '-';
    return result === 'PASSED' ? this.statusPassed : this.statusFailed;
  }

  getResultClass(result: QualityResult | undefined): string {
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

  trackByActionId(_index: number, action: AiqsActionState): string {
    return action.id;
  }
}
