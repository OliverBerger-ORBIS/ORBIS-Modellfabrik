import { Component, ChangeDetectionStrategy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { ECME_CONFIG } from '../../../../components/dsp-animation/configs/ecme/ecme-config';
import { VIEW_MODES } from '../shared/view-modes.const';
import { CUSTOMER_PAGE_STYLES } from '../shared/customer-page.styles';
import type { ViewMode } from '../../../../components/dsp-animation/types';

/**
 * ECME (European Company Manufacturing Everything) DSP Architecture Page
 * Displays DSP architecture customized for ECME's equipment and systems
 * Supports functional, component, and deployment view modes
 */
@Component({
  standalone: true,
  selector: 'app-ecme-dsp-page',
  imports: [CommonModule, DspAnimationComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="customer-dsp-page">
      <header class="customer-header">
        <h1>{{ config.customerName }} - DSP Architecture</h1>
        <p class="subtitle">Interactive demonstration of DSP architecture tailored for {{ config.customerName }}</p>
        
        <div class="view-mode-selector">
          <button 
            *ngFor="let mode of viewModes"
            [class.active]="currentViewMode() === mode.value"
            (click)="setViewMode(mode.value)"
            class="view-mode-btn"
          >
            {{ mode.label }}
          </button>
        </div>
      </header>
      <app-dsp-animation
        [viewMode]="currentViewMode()"
        [customerConfig]="config"
      ></app-dsp-animation>
    </div>
  `,
  styles: [CUSTOMER_PAGE_STYLES],
})
export class EcmeDspPageComponent {
  config = ECME_CONFIG;
  currentViewMode = signal<ViewMode>('functional');
  viewModes = VIEW_MODES;
  
  setViewMode(mode: ViewMode): void {
    this.currentViewMode.set(mode);
  }
}
