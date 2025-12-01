import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FtsBatteryState, getBatteryLevel } from '../../models/fts.types';

/**
 * FTS Battery Status Component
 * Displays battery voltage, percentage, and charging status
 */
@Component({
  selector: 'app-fts-battery',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './fts-battery.component.html',
  styleUrls: ['./fts-battery.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FtsBatteryComponent {
  @Input() batteryState: FtsBatteryState | null = null;
  
  get level(): 'high' | 'medium' | 'low' {
    return getBatteryLevel(this.batteryState?.percentage ?? 0);
  }
  
  get percentageDisplay(): string {
    return `${this.batteryState?.percentage ?? 0}%`;
  }
  
  get voltageDisplay(): string {
    return `${this.batteryState?.currentVoltage?.toFixed(1) ?? '0.0'}V`;
  }
  
  get voltageRange(): string {
    const min = this.batteryState?.minVolt?.toFixed(2) ?? '0.00';
    const max = this.batteryState?.maxVolt?.toFixed(2) ?? '0.00';
    return `${min}V - ${max}V`;
  }
}
