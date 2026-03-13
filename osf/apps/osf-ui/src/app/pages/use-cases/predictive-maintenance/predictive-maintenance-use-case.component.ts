import { Component, ChangeDetectionStrategy, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UseCaseControlsComponent } from '../shared/use-case-controls/use-case-controls.component';
import { Uc05SvgGeneratorService } from './uc-05-svg-generator.service';
import { Uc05I18nService } from './uc-05-i18n.service';
import { UC05_CONNECTION_IDS } from './uc-05-structure.config';
import { BaseUseCaseComponent } from '../shared/base-use-case.component';
import { DomSanitizer } from '@angular/platform-browser';
import { ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { LanguageService } from '../../../services/language.service';
import { getDashboardController } from '../../../mock-dashboard';
import { MessageMonitorService } from '../../../services/message-monitor.service';
import { ConnectionService } from '../../../services/connection.service';
import { EnvironmentService } from '../../../services/environment.service';
import { Observable, Subscription, combineLatest } from 'rxjs';
import { filter, map, startWith, debounceTime } from 'rxjs/operators';

const VIBRATION_TOPIC_SW420 = 'osf/arduino/vibration/sw420-1/state';
const VIBRATION_TOPIC_MPU6050 = 'osf/arduino/vibration/mpu6050-1/state';

interface VibrationPayload {
  vibrationLevel?: 'green' | 'yellow' | 'red';
  vibrationDetected?: boolean;
  ampel?: string;
}

function isVibrationRed(payload: VibrationPayload | null): boolean {
  if (!payload) return false;
  if (payload.vibrationLevel === 'red') return true;
  if (payload.vibrationDetected === true) return true;
  const a = payload.ampel?.toUpperCase();
  return a === 'ROT' || a === 'RED';
}

/**
 * Predictive Maintenance Use Case Component (UC-05)
 * Condition monitoring: Detect → Evaluate → Alarm → Act → Feedback
 */
@Component({
  selector: 'app-predictive-maintenance-use-case',
  standalone: true,
  imports: [CommonModule, UseCaseControlsComponent],
  templateUrl: './predictive-maintenance-use-case.component.html',
  styleUrls: ['./predictive-maintenance-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PredictiveMaintenanceUseCaseComponent extends BaseUseCaseComponent implements OnDestroy {
  readonly useCaseTitle = $localize`:@@predictiveMaintenanceUseCaseHeadline:Predictive Maintenance`;
  activeTab: 'concept' | 'live-demo' = 'concept';

  private readonly dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();
  private vibrationAlarmSub?: Subscription;
  private feedbackTimeout: ReturnType<typeof setTimeout> | null = null;
  enqueuedOrderIds: string[] = [];
  simulateFeedback = false;

  /** When true: vibration RED → auto publish park + cancel (demo mode) */
  autoParkOnVibrationAlarm = false;

  /** Can use auto-park: Mock always, Live/Replay when connected */
  canUseAutoPark$!: Observable<boolean>;

  constructor(
    sanitizer: DomSanitizer,
    cdr: ChangeDetectorRef,
    http: HttpClient,
    languageService: LanguageService,
    private readonly svgGenerator: Uc05SvgGeneratorService,
    private readonly i18nService: Uc05I18nService,
    private readonly messageMonitor: MessageMonitorService,
    private readonly connectionService: ConnectionService,
    private readonly environmentService: EnvironmentService
  ) {
    super(sanitizer, cdr, http, languageService);
    this.canUseAutoPark$ = combineLatest([
      this.connectionService.state$,
      this.environmentService.environment$,
    ]).pipe(
      map(([state, env]) => {
        if (env.key === 'mock') return true;
        return state === 'connected';
      })
    );
    this.subscriptions.add(
      this.messageMonitor
        .getLastMessage<{ orderId?: string; state?: string; status?: string }[] | { orderId?: string; state?: string; status?: string }>(
          'ccu/order/active'
        )
        .pipe(
          filter((msg) => msg !== null && msg.valid && msg.payload != null),
          map((msg) => {
            const payload = msg!.payload;
            const arr = Array.isArray(payload) ? payload : [payload];
            return arr
              .filter((o) => o && (o.state ?? o.status ?? '').toUpperCase() === 'ENQUEUED' && o.orderId)
              .map((o) => o.orderId as string);
          }),
          startWith([] as string[])
        )
        .subscribe((ids) => {
          this.enqueuedOrderIds = ids;
          this.cdr.markForCheck();
        })
    );
  }

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  override ngOnDestroy(): void {
    this.vibrationAlarmSub?.unsubscribe();
    if (this.feedbackTimeout) clearTimeout(this.feedbackTimeout);
    this.subscriptions.unsubscribe();
    super.ngOnDestroy();
  }

  toggleAutoParkOnVibration(event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    this.autoParkOnVibrationAlarm = checked;
    this.vibrationAlarmSub?.unsubscribe();
    this.vibrationAlarmSub = undefined;
    if (checked) {
      const vibrationState$ = combineLatest([
        this.messageMonitor.getLastMessage<VibrationPayload>(VIBRATION_TOPIC_SW420),
        this.messageMonitor.getLastMessage<VibrationPayload>(VIBRATION_TOPIC_MPU6050),
      ]).pipe(
        map(([sw, mpu]) => {
          if (mpu?.valid && mpu?.payload) return mpu.payload as VibrationPayload;
          if (sw?.valid && sw?.payload) return sw.payload as VibrationPayload;
          return null;
        }),
        startWith(null),
        filter((p): p is VibrationPayload => isVibrationRed(p)),
        debounceTime(2000)
      );
      this.vibrationAlarmSub = vibrationState$.subscribe(() => {
        void this.simulateDanger();
      });
    }
    this.cdr.markForCheck();
  }

  private async simulateDanger(): Promise<void> {
    try {
      await this.dashboard.commands.simulateDanger(this.enqueuedOrderIds);
      this.simulateFeedback = true;
      this.cdr.markForCheck();
      if (this.feedbackTimeout) clearTimeout(this.feedbackTimeout);
      this.feedbackTimeout = setTimeout(() => {
        this.feedbackTimeout = null;
        this.simulateFeedback = false;
        this.cdr.markForCheck();
      }, 3000);
    } catch (error) {
      console.warn('[uc-05] simulateDanger failed:', error);
    }
  }

  override getStepsUrl(): string {
    return 'assets/use-cases/uc-05/uc-05-predictive-maintenance.steps.json';
  }

  override getStepPrefix(): string {
    return 'uc05';
  }

  override getConnectionIds(): readonly string[] {
    return UC05_CONNECTION_IDS;
  }

  override async loadSvgContent(): Promise<string> {
    const i18nTexts = await this.i18nService.loadTexts();
    return this.svgGenerator.generateSvg(i18nTexts);
  }
}
