import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { getDashboardController } from '../mock-dashboard';
import type { Observable } from 'rxjs';
import { map, shareReplay, filter, startWith } from 'rxjs/operators';
import { merge, combineLatest } from 'rxjs';
import type { SensorOverviewState, CameraFrame, Bme680Snapshot, LdrSnapshot } from '@omf3/entities';
import { MessageMonitorService } from '../services/message-monitor.service';

@Component({
  standalone: true,
  selector: 'app-sensor-tab',
  imports: [CommonModule],
  templateUrl: './sensor-tab.component.html',
  styleUrl: './sensor-tab.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SensorTabComponent {
  private readonly dashboard = getDashboardController();
  readonly gaugeRadius = 65;
  readonly gaugeCircumference = Math.PI * this.gaugeRadius;
  readonly gaugeCenterX = 110;
  readonly gaugeCenterY = 95;

  readonly sensorHeadingIcon = 'headings/smart.svg';
  readonly cameraHeadingIcon = 'headings/camera.svg';
  stepSize = 10;

  readonly sensorOverview$: Observable<SensorOverviewState>;
  readonly cameraFrame$: Observable<CameraFrame | null>;

  constructor(private readonly messageMonitor: MessageMonitorService) {
    // For sensorOverview$, merge MessageMonitor last values with dashboard stream
    // MessageMonitor stores raw Bme680Snapshot and LdrSnapshot, need to transform to SensorOverviewState
    // IMPORTANT: MessageMonitor streams come first in merge to ensure they have priority over dashboard stream
    const lastBme680 = this.messageMonitor.getLastMessage<Bme680Snapshot>('/j1/txt/1/i/bme680').pipe(
      map((msg) => {
        // If message exists and is valid, use it; otherwise return null
        if (msg !== null && msg.valid) {
          return msg.payload;
        }
        return null;
      })
    );
    const lastLdr = this.messageMonitor.getLastMessage<LdrSnapshot>('/j1/txt/1/i/ldr').pipe(
      map((msg) => {
        // If message exists and is valid, use it; otherwise return null
        if (msg !== null && msg.valid) {
          return msg.payload;
        }
        return null;
      })
    );
    
    // Pattern 2: sensorOverview$ comes from gateway.sensorBme680$ and sensorLdr$ which have NO startWith
    // Combine last BME680 and LDR values from MessageMonitor
    // Use startWith(null) so combineLatest emits even if one stream has no value yet
    const lastSensorOverview = combineLatest([
      lastBme680.pipe(
        map((bme) => bme ?? null),
        startWith(null as Bme680Snapshot | null)
      ),
      lastLdr.pipe(
        map((ldr) => ldr ?? null),
        startWith(null as LdrSnapshot | null)
      )
    ]).pipe(
      map(([bme, ldr]) => this.buildSensorOverviewState(bme, ldr)),
      startWith(this.buildSensorOverviewState(null, null))
    );
    
    // Merge MessageMonitor last values with dashboard stream
    // MessageMonitor streams come first to ensure they take priority when messages are available
    // If MessageMonitor has no values yet, dashboard stream will provide the initial empty state
    this.sensorOverview$ = merge(lastSensorOverview, this.dashboard.streams.sensorOverview$).pipe(
      shareReplay({ bufferSize: 1, refCount: false })
    );

    this.cameraFrame$ = this.dashboard.streams.cameraFrames$.pipe(
      shareReplay({ bufferSize: 1, refCount: false }) // refCount: false to keep stream alive
    );
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

  cameraControl(action: 'up' | 'down' | 'left' | 'right' | 'center'): void {
    console.info('[sensor-tab] camera control action', action, 'step', this.stepSize);
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
}
