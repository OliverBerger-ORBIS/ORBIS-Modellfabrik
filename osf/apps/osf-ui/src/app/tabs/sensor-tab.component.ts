import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { getDashboardController, type DashboardStreamSet } from '../mock-dashboard';
import type { Observable } from 'rxjs';
import { map, shareReplay, filter, startWith, distinctUntilChanged } from 'rxjs/operators';
import { merge, combineLatest, Subscription } from 'rxjs';
import type { SensorOverviewState, CameraFrame, Bme680Snapshot, LdrSnapshot } from '@osf/entities';

/** osf/arduino/vibration/{sw420-1|mpu6050-1}/state – Vibrationssensor; OSF-UI mappt auf Ampel */
export interface VibrationStatePayload {
  /** MPU-6050: direkt; SW-420: abgeleitet aus vibrationDetected */
  vibrationLevel?: 'green' | 'yellow' | 'red';
  /** SW-420: direkt; MPU-6050: true bei gelb/rot */
  vibrationDetected?: boolean;
  impulseCount: number;
  /** MPU-6050: Beschleunigungs-Magnitude */
  magnitude?: number;
  /** ISO 8601 (analog Fischertechnik/DSP) – MPU-6050 via NTP, SW-420 ohne RTC: "" */
  timestamp?: string;
  /** @deprecated Legacy: ampel (GRUEN/GELB/ROT) */
  ampel?: string;
}

/** osf/arduino/temperature/dht11-1/state – DHT11 Temp + Humidity */
export interface Dht11StatePayload {
  temperature?: number;
  humidity?: number;
  temperatureUnit?: string;
  humidityUnit?: string;
}

/** osf/arduino/flame/flame-1/state – KY-026 Flame sensor. rawValue 0–1023; low = flame. Inverted bar: left=high (safe), right=low (danger) */
export interface FlameStatePayload {
  flameDetected?: boolean;
  rawValue?: number;
  timestamp?: string;
}

/** osf/arduino/gas/mq2-1/state – MQ-2 Gas sensor (Rauch/CO). rawValue 0–1023; high = danger. gasLevel from sensor: 0=normal, 1=warning, 2=alarm */
export interface GasStatePayload {
  gasDetected?: boolean;
  gasLevel?: number;  // 0=normal, 1=warning, 2=alarm – from Arduino, no UI interpretation
  rawValue?: number;
  timestamp?: string;
}
import { MessageMonitorService } from '../services/message-monitor.service';
import { EnvironmentService } from '../services/environment.service';
import type { OrderFixtureName } from '@osf/testing-fixtures';
import { ConnectionService, type ConnectionState } from '../services/connection.service';
import { SensorStateService } from '../services/sensor-state.service';

@Component({
  standalone: true,
  selector: 'app-sensor-tab',
  imports: [CommonModule],
  templateUrl: './sensor-tab.component.html',
  styleUrl: './sensor-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SensorTabComponent implements OnInit, OnDestroy {
  private dashboard = getDashboardController();
  private readonly subscriptions = new Subscription();
  private sensorOverviewSub?: Subscription;
  private currentEnvironmentKey: string;
  readonly gaugeRadius = 65;
  readonly gaugeCircumference = Math.PI * this.gaugeRadius;
  readonly gaugeCenterX = 110;
  readonly gaugeCenterY = 95;

  readonly sensorHeadingIcon = 'assets/svg/ui/heading-sensors.svg';
  readonly cameraHeadingIcon = 'assets/svg/ui/heading-camera.svg';
  stepSize = 10;

  readonly fixtureOptions: OrderFixtureName[] = ['startup', 'white', 'white_step3', 'blue', 'red', 'mixed', 'storage'];
  readonly fixtureLabels: Partial<Record<OrderFixtureName, string>> = {
    startup: $localize`:@@fixtureLabelStartup:Startup`,
    white: $localize`:@@fixtureLabelWhite:White`,
    white_step3: $localize`:@@fixtureLabelWhiteStep3:White • Step 3`,
    blue: $localize`:@@fixtureLabelBlue:Blue`,
    red: $localize`:@@fixtureLabelRed:Red`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
    storage: $localize`:@@fixtureLabelStorage:Storage`,
  };
  activeFixture: OrderFixtureName = this.dashboard.getCurrentFixture();

  /** Arduino fixture presets for Mock – Idle, Warning, Alarm */
  readonly arduinoFixturePresets = ['sensor-arduino-idle', 'sensor-arduino-warning', 'sensor-arduino-alarm'] as const;
  readonly arduinoFixtureLabels: Record<(typeof this.arduinoFixturePresets)[number], string> = {
    'sensor-arduino-idle': $localize`:@@sensorArduinoFixtureIdle:Idle`,
    'sensor-arduino-warning': $localize`:@@sensorArduinoFixtureWarning:Warning`,
    'sensor-arduino-alarm': $localize`:@@sensorArduinoFixtureAlarm:Alarm`,
  };
  activeArduinoFixture: (typeof this.arduinoFixturePresets)[number] = 'sensor-arduino-idle';

  sensorOverview$!: Observable<SensorOverviewState>;
  cameraFrame$: Observable<CameraFrame | null> = this.dashboard.streams.cameraFrames$.pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );

  readonly VIBRATION_TOPIC_SW420 = 'osf/arduino/vibration/sw420-1/state';
  readonly VIBRATION_TOPIC_MPU6050 = 'osf/arduino/vibration/mpu6050-1/state';
  readonly DHT11_TOPIC = 'osf/arduino/temperature/dht11-1/state';
  readonly FLAME_TOPIC = 'osf/arduino/flame/flame-1/state';
  readonly GAS_TOPIC = 'osf/arduino/gas/mq2-1/state';
  readonly ALARM_ENABLED_TOPIC = 'osf/arduino/alarm/enabled';

  /** MPU-6050 vibration – 3 levels (green/yellow/red) */
  mpuVibrationState$!: Observable<VibrationStatePayload | null>;
  /** SW-420 vibration – binary (green/red) */
  sw420VibrationState$!: Observable<VibrationStatePayload | null>;
  /** DHT11 temperature + humidity. Arduino spec: temp 0–50°C, humidity 0–100% */
  dht11State$!: Observable<Dht11StatePayload | null>;
  /** Flame sensor. Arduino spec: rawValue 0–1023, inverted bar (left=high=safe, right=low=danger) */
  flameState$!: Observable<FlameStatePayload | null>;
  /** MQ-2 Gas sensor. rawValue 0–1023; high = danger (Rauch/CO) */
  gasState$!: Observable<GasStatePayload | null>;
  /** Sirene aktiv – von osf-ui Toggle gesteuert, Arduino schaltet Relais 4 nur bei true */
  alarmEnabled$!: Observable<boolean>;

  /** Für Template: Gefahrensimulation-Button (Connection-State) */
  connectionState$!: Observable<ConnectionState>;

  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly environmentService: EnvironmentService,
    private readonly connectionService: ConnectionService,
    private readonly sensorState: SensorStateService
  ) {
    this.alarmEnabled$ = this.messageMonitor.getLastMessage<unknown>(this.ALARM_ENABLED_TOPIC).pipe(
      map((msg) => msg?.payload === true || msg?.payload === 'true'),
      startWith(false),
      distinctUntilChanged(),
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.connectionState$ = this.connectionService.state$;
    this.currentEnvironmentKey = this.environmentService.current.key;
    this.mpuVibrationState$ = this.messageMonitor
      .getLastMessage<VibrationStatePayload>(this.VIBRATION_TOPIC_MPU6050)
      .pipe(
        map((msg) => (msg?.valid && msg?.payload ? (msg.payload as VibrationStatePayload) : null)),
        startWith(null as VibrationStatePayload | null),
        shareReplay({ bufferSize: 1, refCount: false })
      );
    this.sw420VibrationState$ = this.messageMonitor
      .getLastMessage<VibrationStatePayload>(this.VIBRATION_TOPIC_SW420)
      .pipe(
        map((msg) => (msg?.valid && msg?.payload ? (msg.payload as VibrationStatePayload) : null)),
        startWith(null as VibrationStatePayload | null),
        shareReplay({ bufferSize: 1, refCount: false })
      );
    this.dht11State$ = this.messageMonitor.getLastMessage<Dht11StatePayload>(this.DHT11_TOPIC).pipe(
      map((msg) => (msg?.valid && msg?.payload ? (msg.payload as Dht11StatePayload) : null)),
      startWith(null as Dht11StatePayload | null),
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.flameState$ = this.messageMonitor.getLastMessage<FlameStatePayload>(this.FLAME_TOPIC).pipe(
      map((msg) => (msg?.valid && msg?.payload ? (msg.payload as FlameStatePayload) : null)),
      startWith(null as FlameStatePayload | null),
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.gasState$ = this.messageMonitor.getLastMessage<GasStatePayload>(this.GAS_TOPIC).pipe(
      map((msg) => (msg?.valid && msg?.payload ? (msg.payload as GasStatePayload) : null)),
      startWith(null as GasStatePayload | null),
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.bindCacheOutputs();
    this.initializeStreams();
  }

  gaugeRatio(value: number | undefined, min: number, max: number): number {
    return this.computeRatio(value, min, max, 'linear');
  }

  gaugeDashOffset(
    value: number | undefined,
    min: number,
    max: number,
    scale: 'linear' | 'log' = 'linear'
  ): number {
    const ratio = this.computeRatio(value, min, max, scale);
    return this.gaugeCircumference * (1 - ratio);
  }

  needleTransform(
    value: number | undefined,
    min: number,
    max: number,
    scale: 'linear' | 'log' = 'linear'
  ): string {
    const ratio = this.computeRatio(value, min, max, scale);
    const angle = ratio * 180 - 90;
    return `rotate(${angle} ${this.gaugeCenterX} ${this.gaugeCenterY})`;
  }

  formatTimestamp(ts?: string): string {
    if (!ts) {
      return $localize`:@@sensorNoTimestamp:No recent data`;
    }
    try {
      const date = new Date(ts);
      if (Number.isNaN(date.getTime())) {
        return ts;
      }
      return date.toLocaleString();
    } catch (error) {
      return ts;
    }
  }

  airQualityStatus(sensor: SensorOverviewState | null): string {
    if (!sensor?.airQualityClassification) {
      return $localize`:@@sensorAirQualityUnknown:Unknown`;
    }
    return sensor.airQualityClassification;
  }

  async cameraControl(action: 'up' | 'down' | 'left' | 'right' | 'center'): Promise<void> {
    try {
      const commandMap: Record<'up' | 'down' | 'left' | 'right' | 'center', 'relmove_up' | 'relmove_down' | 'relmove_left' | 'relmove_right' | 'home'> = {
        up: 'relmove_up',
        down: 'relmove_down',
        left: 'relmove_left',
        right: 'relmove_right',
        center: 'home', // Changed from 'center' to 'home' based on OMF2 examples
      };
      
      const command = commandMap[action];
      // For 'home', degree is not sent (based on examples)
      // For movement commands, use stepSize from UI (default: 10)
      const degree = action === 'center' ? 0 : this.stepSize;
      
      await this.dashboard.commands.moveCamera(command, degree);
    } catch (error) {
      console.warn('Failed to move camera', action, error);
    }
  }

  async stopCamera(): Promise<void> {
    try {
      // 'stop' command doesn't require degree parameter
      await this.dashboard.commands.moveCamera('stop', 0);
    } catch (error) {
      console.warn('Failed to stop camera', error);
    }
  }

  getAriaLabel(action: 'up' | 'left' | 'center' | 'right' | 'down'): string {
    switch (action) {
      case 'up':
        return $localize`:@@sensorControlUp:Up`;
      case 'left':
        return $localize`:@@sensorControlLeft:Left`;
      case 'center':
        return $localize`:@@sensorControlCenter:Center`;
      case 'right':
        return $localize`:@@sensorControlRight:Right`;
      case 'down':
        return $localize`:@@sensorControlDown:Down`;
    }
  }

  onStepSizeChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const value = Number.parseInt(input.value, 10);
    if (Number.isFinite(value)) {
      this.stepSize = Math.max(1, Math.min(value, 90));
    }
  }

  gaugeTicks(
    min: number,
    max: number,
    step: number,
    scale: 'linear' | 'log' = 'linear',
    tickValues?: number[]
  ): Array<{
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    labelX: number;
    labelY: number;
    value: number;
  }> {
    const values =
      tickValues && tickValues.length
        ? tickValues
        : Array.from({ length: Math.floor((max - min) / step) + 1 }, (_, index) => min + index * step);

    return values.map((value) => {
      const ratio = this.computeRatio(value, min, max, scale);
      // Rotate ticks 90° counter-clockwise so they start at bottom-left
      // Original: ratio * 180 - 90 (starts at top)
      // Fixed: ratio * 180 - 180 (starts at bottom-left)
      const angleDeg = ratio * 180 - 180;
      const angleRad = (angleDeg * Math.PI) / 180;
      const outerX = this.gaugeCenterX + this.gaugeRadius * Math.cos(angleRad);
      const outerY = this.gaugeCenterY + this.gaugeRadius * Math.sin(angleRad);
      const innerX = this.gaugeCenterX + (this.gaugeRadius - 8) * Math.cos(angleRad);
      const innerY = this.gaugeCenterY + (this.gaugeRadius - 8) * Math.sin(angleRad);
      const labelRadius = this.gaugeRadius + 24;
      const labelX = this.gaugeCenterX + labelRadius * Math.cos(angleRad);
      const labelY = this.gaugeCenterY + labelRadius * Math.sin(angleRad) + 3;
      return { x1: innerX, y1: innerY, x2: outerX, y2: outerY, labelX, labelY, value };
    });
  }

  airQualityLevel(sensor: SensorOverviewState | null): string {
    const level = sensor?.airQualityClassification?.toLowerCase();
    switch (level) {
      case 'excellent':
        return 'excellent';
      case 'good':
        return 'good';
      case 'moderate':
        return 'moderate';
      case 'poor':
        return 'poor';
      case 'critical':
        return 'critical';
      default:
        return 'unknown';
    }
  }

  formatLarge(value: number): string {
    if (value >= 1_000_000) {
      return `${Math.round(value / 100_000) / 10}M`;
    }
    if (value >= 1_000) {
      return `${Math.round(value / 100) / 10}k`;
    }
    return `${value}`;
  }

  formatExponent(value: number): string {
    const power = Math.round(Math.log10(Math.max(value, 1)));
    return `10^${power}`;
  }

  formatTickLabel(value: number, mode: 'linear' | 'exponent'): string {
    return mode === 'exponent' ? this.formatExponent(value) : `${value}`;
  }

  airQualityRemaining(sensor: SensorOverviewState | null): string {
    const ratio = this.computeRatio(sensor?.airQualityScore, 0, 5, 'linear');
    return `${(100 - ratio * 100).toFixed(1)}%`;
  }

  /** vibrationLevel (MPU-6050) – 3-Stufen. Oder vibrationDetected/ampel (SW-420). */
  vibrationLevel(vibration: VibrationStatePayload | null): 'green' | 'red' | 'yellow' | 'unknown' {
    if (!vibration) return 'unknown';
    if (vibration.vibrationLevel === 'green' || vibration.vibrationLevel === 'yellow' || vibration.vibrationLevel === 'red') {
      return vibration.vibrationLevel;
    }
    if (typeof vibration.vibrationDetected === 'boolean') {
      return vibration.vibrationDetected ? 'red' : 'green';
    }
    const a = vibration.ampel?.toUpperCase();
    if (a === 'GRUEN' || a === 'GREEN') return 'green';
    if (a === 'ROT' || a === 'RED') return 'red';
    if (a === 'GELB' || a === 'YELLOW') return 'yellow';
    return 'unknown';
  }

  /** SW-420 (digital): green (idle) or red (alarm). false = idle = green, true = alarm = red. */
  sw420Level(vibration: VibrationStatePayload | null): 'green' | 'red' | 'unknown' {
    if (!vibration) return 'unknown';
    if (typeof vibration.vibrationDetected === 'boolean') {
      return vibration.vibrationDetected ? 'red' : 'green';
    }
    const a = vibration.ampel?.toUpperCase();
    if (a === 'ROT' || a === 'RED') return 'red';
    if (a === 'GRUEN' || a === 'GREEN') return 'green';
    return 'unknown';
  }

  /** MPU-6050 magnitude range (0–35k typical; ~16k idle, 20k+ warning, 28k+ alarm). */
  readonly MPU_MAGNITUDE_MIN = 0;
  readonly MPU_MAGNITUDE_MAX = 35000;

  formatMagnitude(magnitude: number | undefined): string {
    if (magnitude == null || Number.isNaN(magnitude)) return '—';
    return `${magnitude.toLocaleString()}`;
  }

  vibrationStatus(vibration: VibrationStatePayload | null): string {
    if (!vibration) return $localize`:@@sensorVibrationNoData:No data`;
    const level = this.vibrationLevel(vibration);
    const isAlarm = level === 'red';
    const isWarning = level === 'yellow';
    if (isAlarm) return $localize`:@@sensorVibrationStatusRed:Alarm`;
    if (isWarning) return $localize`:@@sensorVibrationStatusYellow:Warning`;
    return $localize`:@@sensorVibrationStatusGreen:Idle`;
  }

  /** SW-420 status: Idle (green) or Alarm (red). */
  sw420Status(vibration: VibrationStatePayload | null): string {
    if (!vibration) return $localize`:@@sensorVibrationNoData:No data`;
    const level = this.sw420Level(vibration);
    if (level === 'red') return $localize`:@@sensorVibrationStatusRed:Alarm`;
    if (level === 'green') return $localize`:@@sensorVibrationStatusGreen:Idle`;
    return $localize`:@@sensorVibrationNoData:No data`;
  }

  /** Alarm state for highlighting: sensor would trigger UC-05 danger simulation. */
  isMpuAlarm(vibration: VibrationStatePayload | null): boolean {
    return this.vibrationLevel(vibration) === 'red';
  }

  /** Warning state (yellow) – orange border, consistent with Gas. */
  isMpuWarning(vibration: VibrationStatePayload | null): boolean {
    return this.vibrationLevel(vibration) === 'yellow';
  }

  /** Alarm state for highlighting. */
  isSw420Alarm(vibration: VibrationStatePayload | null): boolean {
    return this.sw420Level(vibration) === 'red';
  }

  /** Alarm state for highlighting (temp >= 35°C or humidity >= 90%). */
  isDhtAlarm(dht: Dht11StatePayload | null): boolean {
    if (!dht) return false;
    const t = dht.temperature ?? 0;
    const h = dht.humidity ?? 0;
    return t >= 35 || h >= 90;
  }

  /** Warning state (temp 30–35°C or humidity 80–90%) – orange border, consistent with MPU/Gas. */
  isDhtWarning(dht: Dht11StatePayload | null): boolean {
    if (!dht) return false;
    const t = dht.temperature ?? 0;
    const h = dht.humidity ?? 0;
    return (t >= 30 && t < 35) || (h >= 80 && h < 90);
  }

  /** Flame: alarm only (binary from sensor). No warning level. */
  isFlameAlarm(flame: FlameStatePayload | null): boolean {
    return flame?.flameDetected === true;
  }

  /** Flame has no warning level (digital sensor). */
  isFlameWarning(_flame: FlameStatePayload | null): boolean {
    return false;
  }

  /** Gas: alarm = level 2 from sensor. Backward compat: gasLevel undefined → use gasDetected. */
  isGasAlarm(gas: GasStatePayload | null): boolean {
    if (gas?.gasLevel != null) return gas.gasLevel >= 2;
    return gas?.gasDetected === true;
  }

  /** Gas: warning = level 1 from sensor. */
  isGasWarning(gas: GasStatePayload | null): boolean {
    return gas?.gasLevel === 1;
  }

  /** Sirene ein/aus – Arduino Relais 4; Ampel (Grün/Gelb/Rot) bleibt sensor-gesteuert */
  async setAlarmEnabled(enabled: boolean): Promise<void> {
    try {
      await this.connectionService.publish(this.ALARM_ENABLED_TOPIC, enabled, {
        qos: 1,
        retain: true,
      });
    } catch (error) {
      console.warn('[sensor-tab] setAlarmEnabled failed:', error);
    }
  }

  formatDht11Temp(dht11: Dht11StatePayload | null): string {
    if (dht11?.temperature == null || Number.isNaN(dht11.temperature)) return '—';
    return `${dht11.temperature.toFixed(1)}°C`;
  }

  formatDht11Humidity(dht11: Dht11StatePayload | null): string {
    if (dht11?.humidity == null || Number.isNaN(dht11.humidity)) return '—';
    return `${dht11.humidity.toFixed(1)}%`;
  }

  /** Flame danger %: logarithmic scale. High raw = safe, low raw = danger. log10(raw+1)/log10(1024) = safe ratio. */
  flameDangerPercent(flame: FlameStatePayload | null): number {
    const raw = flame?.rawValue;
    if (raw == null || Number.isNaN(raw)) return 0;
    const clamped = Math.min(1023, Math.max(0, raw));
    const logSafe = Math.log10(clamped + 1) / Math.log10(1024);
    return (1 - logSafe) * 100;
  }

  /** Flame safe % for mask width (logarithmic scale). Mask covers right side = safe zone. */
  flameSafePercent(flame: FlameStatePayload | null): string {
    const raw = flame?.rawValue;
    if (raw == null || Number.isNaN(raw)) return '100%';
    const clamped = Math.min(1023, Math.max(0, raw));
    const logSafe = Math.log10(clamped + 1) / Math.log10(1024);
    return `${(logSafe * 100).toFixed(1)}%`;
  }

  /** Display danger % for UI. E.g. raw 888 → 13%, raw 12 → 99%. */
  formatFlameDangerPercent(flame: FlameStatePayload | null): string {
    const pct = this.flameDangerPercent(flame);
    if (flame?.rawValue == null || Number.isNaN(flame.rawValue)) return '—';
    return `${pct.toFixed(0)}%`;
  }

  formatFlameRaw(flame: FlameStatePayload | null): string {
    const raw = flame?.rawValue;
    if (raw == null || Number.isNaN(raw)) return '—';
    return String(raw);
  }

  /** MQ-2 Gas danger %: raw/1023*100. High raw = danger (Rauch/CO). */
  gasDangerPercent(gas: GasStatePayload | null): number {
    const raw = gas?.rawValue;
    if (raw == null || Number.isNaN(raw)) return 0;
    const clamped = Math.min(1023, Math.max(0, raw));
    return (clamped / 1023) * 100;
  }

  /** Gas safe % for mask (like Air Quality). Mask from right = safe zone. */
  gasSafePercent(gas: GasStatePayload | null): string {
    const raw = gas?.rawValue;
    if (raw == null || Number.isNaN(raw)) return '100%';
    const clamped = Math.min(1023, Math.max(0, raw));
    const safe = ((1023 - clamped) / 1023) * 100;
    return `${safe.toFixed(1)}%`;
  }

  /** Display gas danger % for UI. */
  formatGasDangerPercent(gas: GasStatePayload | null): string {
    const pct = this.gasDangerPercent(gas);
    if (gas?.rawValue == null || Number.isNaN(gas.rawValue)) return '—';
    return `${pct.toFixed(0)}%`;
  }

  formatGasRaw(gas: GasStatePayload | null): string {
    const raw = gas?.rawValue;
    if (raw == null || Number.isNaN(raw)) return '—';
    return String(raw);
  }

  /** Mock only: Vibration-State per injectMessage setzen (zum Testen der Anzeige) */
  injectVibrationState(vibrationDetected: boolean): void {
    const payload: VibrationStatePayload = {
      vibrationDetected,
      impulseCount: vibrationDetected ? 99 : 0,
      timestamp: new Date().toISOString(),
    };
    const message = {
      topic: this.VIBRATION_TOPIC_SW420,
      payload,
      timestamp: new Date().toISOString(),
    };
    this.dashboard.injectMessage?.(message);
  }

  private computeRatio(
    rawValue: number | undefined,
    min: number,
    max: number,
    scale: 'linear' | 'log'
  ): number {
    if (rawValue == null || Number.isNaN(rawValue) || max <= min) {
      return 0;
    }

    const clamped = Math.min(Math.max(rawValue, min), max);

    if (scale === 'log') {
      const safeMin = Math.max(min, 1);
      const safeMax = Math.max(max, safeMin + 1);
      const safeValue = Math.max(clamped, safeMin);
      const minLog = Math.log10(safeMin);
      const maxLog = Math.log10(safeMax);
      const valueLog = Math.log10(safeValue);
      const ratio = (valueLog - minLog) / (maxLog - minLog);
      return Math.min(1, Math.max(0, Number(ratio.toFixed(3))));
    }

    const ratio = (clamped - min) / (max - min);
    return Math.min(1, Math.max(0, Number(ratio.toFixed(3))));
  }

  /**
   * Build SensorOverviewState from Bme680Snapshot and LdrSnapshot
   * This matches the logic in business layer buildSensorOverviewState
   */
  private buildSensorOverviewState(
    bme680: Bme680Snapshot | null,
    ldr: LdrSnapshot | null
  ): SensorOverviewState {
    const temperatureC = bme680?.t ?? undefined;
    const humidityPercent = bme680?.h ?? undefined;
    const pressureHpa = bme680?.p ?? undefined;
    const lightLux = ldr?.ldr ?? ldr?.br ?? undefined;
    const iaq = bme680?.iaq ?? undefined;
    const airQualityScore = bme680?.aq ?? undefined;
    const airQualityClassification = this.classifyAirQuality(airQualityScore);

    return {
      timestamp: bme680?.ts ?? ldr?.ts,
      temperatureC,
      humidityPercent,
      pressureHpa,
      lightLux,
      iaq,
      airQualityScore,
      airQualityClassification,
    };
  }

  /**
   * Classify air quality based on score
   * This matches the logic in business layer classifyAirQuality
   */
  private classifyAirQuality(score: number | undefined): string | undefined {
    if (score === undefined || score === null) {
      return undefined;
    }
    if (score >= 4.5) {
      return 'excellent';
    }
    if (score >= 3.5) {
      return 'good';
    }
    if (score >= 2.5) {
      return 'moderate';
    }
    if (score >= 1.5) {
      return 'poor';
    }
    return 'critical';
  }

  get isMockMode(): boolean {
    return this.environmentService.current.key === 'mock';
  }

  ngOnInit(): void {
    this.subscriptions.add(
      this.connectionService.state$
        .pipe(distinctUntilChanged())
        .subscribe((state) => {
          if (state === 'connected') {
            this.initializeStreams();
          }
        })
    );

    this.subscriptions.add(
      this.environmentService.environment$
        .pipe(distinctUntilChanged((prev, next) => prev.key === next.key))
        .subscribe((environment) => {
          this.currentEnvironmentKey = environment.key;
          this.sensorState.clear(this.currentEnvironmentKey);
          this.bindCacheOutputs();
          this.initializeStreams();
          if (environment.key === 'mock') {
            void this.loadArduinoFixture(this.activeArduinoFixture);
          }
        })
    );

    if (this.isMockMode) {
      void this.loadArduinoFixture('sensor-arduino-idle');  // Load Arduino fixture so all Arduino sensors show data
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
    this.sensorOverviewSub?.unsubscribe();
  }

  async loadFixture(fixture: OrderFixtureName): Promise<void> {
    if (!this.isMockMode) {
      return; // Don't load fixtures in live/replay mode
    }
    this.activeFixture = fixture;
    try {
      // Always use sensor-startup preset (only startup fixtures needed for Sensor/Environmental Data tab)
      // The fixture parameter is kept for UI consistency, but we always load startup
      await this.dashboard.loadTabFixture('sensor-startup');
      const streams = this.dashboard.streams;
      this.sensorState.clear(this.currentEnvironmentKey);
      this.bindStreams(streams);
    } catch (error) {
      console.warn('Failed to load sensor fixture', fixture, error);
    }
  }

  /** Load Arduino fixture preset (Idle, Warning, Alarm) – Mock only */
  async loadArduinoFixture(preset: 'sensor-arduino-idle' | 'sensor-arduino-warning' | 'sensor-arduino-alarm'): Promise<void> {
    if (!this.isMockMode) return;
    this.activeArduinoFixture = preset;
    try {
      await this.dashboard.loadTabFixture(preset);
      const streams = this.dashboard.streams;
      this.sensorState.clear(this.currentEnvironmentKey);
      this.bindStreams(streams);
    } catch (error) {
      console.warn('Failed to load Arduino fixture', preset, error);
    }
  }

  private initializeStreams(): void {
    const controller = getDashboardController();
    this.dashboard = controller;
    this.activeFixture = controller.getCurrentFixture();
    this.bindStreams(this.dashboard.streams);
  }

  private bindStreams(streams?: DashboardStreamSet): void {
    const lastBme680 = this.messageMonitor.getLastMessage<Bme680Snapshot>('/j1/txt/1/i/bme680').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload)
    );
    const lastLdr = this.messageMonitor.getLastMessage<LdrSnapshot>('/j1/txt/1/i/ldr').pipe(
      filter((msg) => msg !== null && msg.valid),
      map((msg) => msg!.payload)
    );

    const bme680WithDefault = lastBme680.pipe(startWith(null as Bme680Snapshot | null));
    const ldrWithDefault = lastLdr.pipe(startWith(null as LdrSnapshot | null));
    const lastSensorOverview = combineLatest([bme680WithDefault, ldrWithDefault]).pipe(
      map(([bme, ldr]) => this.buildSensorOverviewState(bme, ldr)),
      startWith(this.buildSensorOverviewState(null, null))
    );

    // Pattern enforcement: merge(lastSensorOverview, this.dashboard.streams.sensorOverview$)
    const mergedSensorOverview$ = merge(
      lastSensorOverview,
      streams?.sensorOverview$ ?? this.dashboard.streams.sensorOverview$
    ).pipe(shareReplay({ bufferSize: 1, refCount: false }));

    this.sensorOverview$ = mergedSensorOverview$;
    this.sensorOverviewSub?.unsubscribe();
    this.sensorOverviewSub = mergedSensorOverview$.subscribe((state) => {
      this.sensorState.setState(this.currentEnvironmentKey, state);
    });
    this.bindCacheOutputs();

    // Pattern enforcement: this.cameraFrame$ = this.dashboard.streams.cameraFrames$.pipe(...)
    this.cameraFrame$ = this.dashboard.streams.cameraFrames$.pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.cameraFrame$ = (streams?.cameraFrames$ ?? this.dashboard.streams.cameraFrames$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }

  private bindCacheOutputs(): void {
    this.sensorOverview$ = this.sensorState
      .getState$(this.currentEnvironmentKey)
      .pipe(
        map((state) => state ?? this.buildSensorOverviewState(null, null)),
        shareReplay({ bufferSize: 1, refCount: true })
      );
  }
}
