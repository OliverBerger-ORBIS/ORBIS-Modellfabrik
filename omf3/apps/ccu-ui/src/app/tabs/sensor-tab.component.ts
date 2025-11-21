import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { getDashboardController, type DashboardStreamSet } from '../mock-dashboard';
import type { Observable } from 'rxjs';
import { map, shareReplay, filter, startWith, distinctUntilChanged } from 'rxjs/operators';
import { merge, combineLatest, Subscription } from 'rxjs';
import type { SensorOverviewState, CameraFrame, Bme680Snapshot, LdrSnapshot } from '@omf3/entities';
import { MessageMonitorService } from '../services/message-monitor.service';
import { EnvironmentService } from '../services/environment.service';
import type { OrderFixtureName } from '@omf3/testing-fixtures';
import { ConnectionService } from '../services/connection.service';

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
  readonly gaugeRadius = 65;
  readonly gaugeCircumference = Math.PI * this.gaugeRadius;
  readonly gaugeCenterX = 110;
  readonly gaugeCenterY = 95;

  readonly sensorHeadingIcon = 'headings/smart.svg';
  readonly cameraHeadingIcon = 'headings/camera.svg';
  stepSize = 10;

  readonly fixtureOptions: OrderFixtureName[] = ['startup', 'white', 'white_step3', 'blue', 'red', 'mixed', 'storage'];
  readonly fixtureLabels: Record<OrderFixtureName, string> = {
    startup: $localize`:@@fixtureLabelStartup:Startup`,
    white: $localize`:@@fixtureLabelWhite:White`,
    white_step3: $localize`:@@fixtureLabelWhiteStep3:White • Step 3`,
    blue: $localize`:@@fixtureLabelBlue:Blue`,
    red: $localize`:@@fixtureLabelRed:Red`,
    mixed: $localize`:@@fixtureLabelMixed:Mixed`,
    storage: $localize`:@@fixtureLabelStorage:Storage`,
  };
  activeFixture: OrderFixtureName = this.dashboard.getCurrentFixture();

  sensorOverview$!: Observable<SensorOverviewState>;
  cameraFrame$: Observable<CameraFrame | null> = this.dashboard.streams.cameraFrames$.pipe(
    shareReplay({ bufferSize: 1, refCount: false })
  );

  constructor(
    private readonly messageMonitor: MessageMonitorService,
    private readonly environmentService: EnvironmentService,
    private readonly connectionService: ConnectionService
  ) {
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
          this.initializeStreams();
          if (environment.key === 'mock') {
            void this.loadFixture(this.activeFixture);
          }
        })
    );

    if (this.isMockMode) {
      void this.loadFixture(this.activeFixture);
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  async loadFixture(fixture: OrderFixtureName): Promise<void> {
    if (!this.isMockMode) {
      return; // Don't load fixtures in live/replay mode
    }
    this.activeFixture = fixture;
    try {
      const streams = await this.dashboard.loadFixture(fixture);
    this.bindStreams(streams);
    } catch (error) {
      console.warn('Failed to load sensor fixture', fixture, error);
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
    this.sensorOverview$ = merge(lastSensorOverview, streams?.sensorOverview$ ?? this.dashboard.streams.sensorOverview$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );

    // Pattern enforcement: this.cameraFrame$ = this.dashboard.streams.cameraFrames$.pipe(...)
    this.cameraFrame$ = this.dashboard.streams.cameraFrames$.pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
    this.cameraFrame$ = (streams?.cameraFrames$ ?? this.dashboard.streams.cameraFrames$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );
  }
}
