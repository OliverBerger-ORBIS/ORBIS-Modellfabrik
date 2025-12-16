import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { filter, map, shareReplay, startWith } from 'rxjs/operators';
import { Observable, Subscription } from 'rxjs';
import { EnvironmentService } from '../services/environment.service';
import { MessageMonitorService } from '../services/message-monitor.service';
import { ConnectionService } from '../services/connection.service';
import { ModuleNameService } from '../services/module-name.service';

// DPS Serial Number
const DPS_SERIAL = 'SVR4H73275';
const DPS_STATE_TOPIC = `module/v1/ff/${DPS_SERIAL}/state`;
const DPS_ORDER_TOPIC = `module/v1/ff/${DPS_SERIAL}/order`;
const DPS_CONNECTION_TOPIC = `module/v1/ff/${DPS_SERIAL}/connection`;

// DPS Types
type ActionStateType = 'WAITING' | 'INITIALIZING' | 'RUNNING' | 'FINISHED' | 'FAILED' | string;
type ActionCommandType = 'INPUT_RGB' | 'RGB_NFC' | 'PICK' | 'DROP' | string;
type WorkpieceColor = 'WHITE' | 'BLUE' | 'RED' | null;

interface DpsActionState {
  id: string;
  command: ActionCommandType;
  state: ActionStateType;
  timestamp: string;
  result?: 'PASSED' | 'FAILED';
  metadata?: {
    type?: WorkpieceColor;
    workpieceId?: string;
    workpiece?: {
      type: string;
      workpieceId: string;
      state: string;
    };
  };
}

interface DpsState {
  serialNumber: string;
  timestamp: string;
  orderId?: string;
  orderUpdateId?: number;
  connectionState?: 'ONLINE' | 'OFFLINE';
  available?: 'READY' | 'BUSY' | 'ERROR';
  actionState?: DpsActionState;
  actionStates?: DpsActionState[];
}

@Component({
  standalone: true,
  selector: 'app-dps-tab',
  imports: [CommonModule],
  templateUrl: './dps-tab.component.html',
  styleUrl: './dps-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DpsTabComponent implements OnInit, OnDestroy {
  private readonly subscriptions = new Subscription();

  // Observable streams
  dpsState$!: Observable<DpsState | null>;
  connection$!: Observable<any | null>;
  dpsOrder$!: Observable<any | null>;

  // Icons
  readonly headingIcon = 'assets/svg/shopfloor/stations/dps-station.svg';
  readonly statusIcon = 'assets/svg/ui/heading-modules.svg';
  readonly workpieceIcon = 'assets/svg/ui/heading-inventory.svg';
  readonly historyIcon = 'assets/svg/ui/heading-production.svg';
  readonly connectionOnlineIcon = 'assets/svg/shopfloor/shared/status-online.svg';
  readonly connectionOfflineIcon = 'assets/svg/shopfloor/shared/status-offline.svg';

  // i18n Labels
  readonly headingTitle = $localize`:@@dpsTabTitle:Delivery & Pickup Station (DPS)`;
  readonly headingSubtitle = $localize`:@@dpsTabSubtitle:Real-time monitoring of workpiece handling and identification`;
  readonly labelConnection = $localize`:@@dpsLabelConnection:Connection`;
  readonly labelAvailability = $localize`:@@dpsLabelAvailability:Availability`;
  readonly labelCurrentAction = $localize`:@@dpsLabelCurrentAction:Current Action`;
  readonly labelWorkpieceColor = $localize`:@@dpsLabelColor:Workpiece Color`;
  readonly labelNfcCode = $localize`:@@dpsLabelNfcCode:NFC Code`;
  readonly labelCommandHistory = $localize`:@@dpsLabelHistory:Command History`;
  readonly labelColorWhite = $localize`:@@dpsColorWhite:White`;
  readonly labelColorBlue = $localize`:@@dpsColorBlue:Blue`;
  readonly labelColorRed = $localize`:@@dpsColorRed:Red`;
  readonly labelColorUnknown = $localize`:@@dpsColorUnknown:Unknown`;
  readonly labelNfcNone = $localize`:@@dpsNfcNone:None`;
  readonly statusOnline = $localize`:@@commonStatusOnline:Online`;
  readonly statusOffline = $localize`:@@commonStatusOffline:Offline`;
  readonly statusReady = $localize`:@@commonStatusReady:Ready`;
  readonly statusBusy = $localize`:@@commonStatusBusy:Busy`;
  readonly statusError = $localize`:@@commonStatusError:Error`;
  readonly labelSerialNumber = $localize`:@@dpsLabelSerialNumber:Serial Number`;
  readonly labelOrderId = $localize`:@@dpsLabelOrderId:Order ID`;
  readonly labelNoOrder = $localize`:@@dpsLabelNoOrder:No Order`;
  readonly labelCommand = $localize`:@@dpsLabelCommand:Command`;
  readonly labelState = $localize`:@@dpsLabelState:State`;
  readonly labelResult = $localize`:@@dpsLabelResult:Result`;
  readonly labelTimestamp = $localize`:@@dpsLabelTimestamp:Timestamp`;
  readonly labelWorkpieceState = $localize`:@@dpsLabelWorkpieceState:Workpiece State`;
  readonly stateWaiting = $localize`:@@dpsStateWaiting:WAITING`;
  readonly stateInitializing = $localize`:@@dpsStateInitializing:INITIALIZING`;
  readonly stateRunning = $localize`:@@dpsStateRunning:RUNNING`;
  readonly stateFinished = $localize`:@@dpsStateFinished:FINISHED`;
  readonly stateFailed = $localize`:@@dpsStateFailed:FAILED`;
  readonly resultPassed = $localize`:@@dpsResultPassed:PASSED`;
  readonly resultFailed = $localize`:@@dpsResultFailed:FAILED`;

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
    // DPS State stream
    this.dpsState$ = this.messageMonitor.getLastMessage<DpsState>(DPS_STATE_TOPIC).pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload as DpsState),
      startWith(null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Connection stream
    this.connection$ = this.messageMonitor.getLastMessage<any>(DPS_CONNECTION_TOPIC).pipe(
      map((msg) => msg?.payload ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Order stream
    this.dpsOrder$ = this.messageMonitor.getLastMessage<any>(DPS_ORDER_TOPIC).pipe(
      map((msg) => msg?.payload ?? null),
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  // Helper methods for template
  getConnectionStatus(state: DpsState | null): 'ONLINE' | 'OFFLINE' {
    return state?.connectionState ?? 'OFFLINE';
  }

  getAvailability(state: DpsState | null): string {
    return state?.available ?? 'UNKNOWN';
  }

  getCurrentAction(state: DpsState | null): DpsActionState | null {
    return state?.actionState ?? null;
  }

  getRecentActions(state: DpsState | null): DpsActionState[] {
    return state?.actionStates?.slice(-10).reverse() ?? [];
  }

  getWorkpieceColor(state: DpsState | null): WorkpieceColor {
    return state?.actionState?.metadata?.type ?? null;
  }

  getNfcCode(state: DpsState | null): string | null {
    return state?.actionState?.metadata?.workpieceId ?? null;
  }

  getWorkpieceState(state: DpsState | null): string | null {
    return state?.actionState?.metadata?.workpiece?.state ?? null;
  }

  getColorLabel(color: WorkpieceColor): string {
    if (!color) return this.labelColorUnknown;
    switch (color.toUpperCase()) {
      case 'WHITE':
        return this.labelColorWhite;
      case 'BLUE':
        return this.labelColorBlue;
      case 'RED':
        return this.labelColorRed;
      default:
        return this.labelColorUnknown;
    }
  }

  getColorClass(color: WorkpieceColor): string {
    if (!color) return 'unknown';
    return color.toLowerCase();
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

  trackByActionId(_index: number, action: DpsActionState): string {
    return action.id;
  }
}
