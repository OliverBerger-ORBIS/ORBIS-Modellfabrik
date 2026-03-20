import { Component, ChangeDetectionStrategy, OnInit, OnDestroy } from '@angular/core';
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
import { Observable, Subscription, combineLatest, firstValueFrom } from 'rxjs';
import { filter, map, startWith, debounceTime, distinctUntilChanged, shareReplay } from 'rxjs/operators';
import { ShopfloorMappingService } from '../../../services/shopfloor-mapping.service';

const VIBRATION_TOPIC_SW420 = 'osf/arduino/vibration/sw420-1/state';
const VIBRATION_TOPIC_MPU6050 = 'osf/arduino/vibration/mpu6050-1/state';
const FLAME_TOPIC = 'osf/arduino/flame/flame-1/state';
const GAS_TOPIC = 'osf/arduino/gas/mq2-1/state';
const DHT_TOPIC = 'osf/arduino/temperature/dht11-1/state';
const ALARM_ENABLED_TOPIC = 'osf/arduino/alarm/enabled';
const STORAGE_KEY_UC05_AUTO_PARK = 'OSF.uc05.autoParkOnVibrationAlarm';

interface VibrationPayload {
  vibrationLevel?: 'green' | 'yellow' | 'red';
  vibrationDetected?: boolean;
  ampel?: string;
}

interface FlamePayload {
  flameDetected?: boolean;
}

interface GasPayload {
  gasDetected?: boolean;
  gasLevel?: number;  // 0=normal, 1=warning, 2=alarm – from Arduino
}

interface DhtPayload {
  temperature?: number;
  humidity?: number;
}

function isVibrationRed(payload: VibrationPayload | null): boolean {
  if (!payload) return false;
  if (payload.vibrationLevel === 'red') return true;
  if (payload.vibrationDetected === true) return true;
  const a = payload.ampel?.toUpperCase();
  return a === 'ROT' || a === 'RED';
}

function isFlameAlarm(payload: FlamePayload | null): boolean {
  return payload?.flameDetected === true;
}

function isGasAlarm(payload: GasPayload | null): boolean {
  if (payload?.gasLevel != null) return payload.gasLevel >= 2;
  return payload?.gasDetected === true;
}

function isDhtAlarm(payload: DhtPayload | null): boolean {
  if (!payload) return false;
  const t = payload.temperature ?? 0;
  const h = payload.humidity ?? 0;
  return t >= 35 || h >= 90;
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
export class PredictiveMaintenanceUseCaseComponent extends BaseUseCaseComponent implements OnInit, OnDestroy {
  readonly useCaseTitle = $localize`:@@predictiveMaintenanceUseCaseHeadline:Predictive Maintenance`;
  activeTab: 'concept' | 'live-demo' = 'concept';

  private readonly dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();
  private sensorAlarmSub?: Subscription;
  private feedbackTimeout: ReturnType<typeof setTimeout> | null = null;
  enqueuedOrderIds: string[] = [];
  simulateFeedback = false;
  /** Last sent topics on alarm (for display in Live Demo). Persists until next alarm. */
  lastSentTopics: Array<{ topic: string; timestamp: string }> = [];

  /** When true: any Arduino sensor alarm (vibration, flame, gas, DHT) → auto publish park + cancel (demo mode). Persisted to localStorage. */
  autoParkOnSensorAlarm = this.loadAutoParkPersisted();

  /** Can use auto-park: Mock always, Live/Replay when connected */
  canUseAutoPark$!: Observable<boolean>;

  /** Sirene aktiv – Arduino Relais 4; beide Toggles (Sensor-Tab + UC-05) steuern denselben Topic */
  alarmEnabled$!: Observable<boolean>;

  constructor(
    sanitizer: DomSanitizer,
    cdr: ChangeDetectorRef,
    http: HttpClient,
    languageService: LanguageService,
    private readonly svgGenerator: Uc05SvgGeneratorService,
    private readonly i18nService: Uc05I18nService,
    private readonly messageMonitor: MessageMonitorService,
    private readonly connectionService: ConnectionService,
    private readonly environmentService: EnvironmentService,
    private readonly mappingService: ShopfloorMappingService
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
    this.alarmEnabled$ = this.messageMonitor.getLastMessage<unknown>(ALARM_ENABLED_TOPIC).pipe(
      map((msg) => msg?.payload === true || msg?.payload === 'true'),
      startWith(false),
      distinctUntilChanged(),
      shareReplay({ bufferSize: 1, refCount: false })
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

  override async ngOnInit(): Promise<void> {
    await super.ngOnInit();
    if (this.autoParkOnSensorAlarm) {
      this.setupSensorAlarmSubscription();
    }
  }

  override ngOnDestroy(): void {
    this.sensorAlarmSub?.unsubscribe();
    if (this.feedbackTimeout) clearTimeout(this.feedbackTimeout);
    this.subscriptions.unsubscribe();
    super.ngOnDestroy();
  }

  async setAlarmEnabled(enabled: boolean): Promise<void> {
    try {
      await this.connectionService.publish(ALARM_ENABLED_TOPIC, enabled, {
        qos: 1,
        retain: true,
      });
    } catch (error) {
      console.warn('[uc-05] setAlarmEnabled failed:', error);
    }
  }

  private loadAutoParkPersisted(): boolean {
    try {
      const stored = localStorage?.getItem(STORAGE_KEY_UC05_AUTO_PARK);
      return stored === 'true';
    } catch {
      return false;
    }
  }

  private setupSensorAlarmSubscription(): void {
    this.sensorAlarmSub?.unsubscribe();
    this.sensorAlarmSub = undefined;
    const alarmState$ = combineLatest([
      this.messageMonitor.getLastMessage<VibrationPayload>(VIBRATION_TOPIC_SW420),
      this.messageMonitor.getLastMessage<VibrationPayload>(VIBRATION_TOPIC_MPU6050),
      this.messageMonitor.getLastMessage<FlamePayload>(FLAME_TOPIC),
      this.messageMonitor.getLastMessage<GasPayload>(GAS_TOPIC),
      this.messageMonitor.getLastMessage<DhtPayload>(DHT_TOPIC),
    ]).pipe(
      map(([sw, mpu, flame, gas, dht]) => {
        const v = isVibrationRed(mpu?.valid && mpu?.payload ? (mpu.payload as VibrationPayload) : null) ||
          isVibrationRed(sw?.valid && sw?.payload ? (sw.payload as VibrationPayload) : null);
        const f = isFlameAlarm(flame?.valid && flame?.payload ? (flame.payload as FlamePayload) : null);
        const g = isGasAlarm(gas?.valid && gas?.payload ? (gas.payload as GasPayload) : null);
        const d = isDhtAlarm(dht?.valid && dht?.payload ? (dht.payload as DhtPayload) : null);
        return v || f || g || d;
      }),
      startWith(false),
      filter((alarm) => alarm),
      debounceTime(2000)
    );
    this.sensorAlarmSub = alarmState$.subscribe(() => {
      void this.simulateDanger();
    });
  }

  /** FTS serials for alarm: from ftsStates$ (active) + layout fallback. Deduplicated. */
  private async getFtsSerialsForAlarm(): Promise<string[]> {
    const fromStates = await firstValueFrom(
      this.dashboard.streams.ftsStates$.pipe(
        map((s) => Object.keys(s).filter((k) => k && k !== 'unknown'))
      )
    );
    const fromLayout = this.mappingService.getAgvOptions().map((o) => o.serial);
    const seen = new Set<string>();
    const result: string[] = [];
    for (const s of [...fromStates, ...fromLayout]) {
      if (s && !seen.has(s)) {
        seen.add(s);
        result.push(s);
      }
    }
    return result;
  }

  toggleAutoParkOnSensorAlarm(event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    this.autoParkOnSensorAlarm = checked;
    try {
      localStorage?.setItem(STORAGE_KEY_UC05_AUTO_PARK, String(checked));
    } catch {
      // Ignore storage errors
    }
    if (checked) {
      this.setupSensorAlarmSubscription();
    } else {
      this.sensorAlarmSub?.unsubscribe();
      this.sensorAlarmSub = undefined;
    }
    this.cdr.markForCheck();
  }

  private async simulateDanger(): Promise<void> {
    try {
      const ftsSerials = await this.getFtsSerialsForAlarm();
      const { sentTopics } = await this.dashboard.commands.simulateDanger(this.enqueuedOrderIds, { ftsSerials });
      this.lastSentTopics = sentTopics;
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
