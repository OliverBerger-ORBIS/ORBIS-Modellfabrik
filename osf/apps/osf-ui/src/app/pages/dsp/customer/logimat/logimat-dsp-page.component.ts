import { Component, ChangeDetectionStrategy, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { LOGIMAT_CONFIG } from '../../../../components/dsp-animation/configs/logimat/logimat-config';
import { VIEW_MODES } from '../shared/view-modes.const';
import { CUSTOMER_PAGE_STYLES } from '../shared/customer-page.styles';
import type { ViewMode } from '../../../../components/dsp-animation/types';

const VALID_VIEW_MODES: ViewMode[] = ['functional', 'component', 'deployment'];

/**
 * LogiMAT customer DSP architecture page (functional steps + EWM / MES cluster).
 */
@Component({
  standalone: true,
  selector: 'app-logimat-dsp-page',
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
        [initialStep]="initialStep()"
      ></app-dsp-animation>
    </div>
  `,
  styles: [CUSTOMER_PAGE_STYLES],
})
export class LogimatDspPageComponent implements OnInit {
  config = LOGIMAT_CONFIG;
  currentViewMode = signal<ViewMode>('functional');
  initialStep = signal<number>(0);
  viewModes = VIEW_MODES;

  constructor(private readonly route: ActivatedRoute) {}

  ngOnInit(): void {
    const applyParams = (params: Record<string, string>) => {
      const vm = params['viewMode'];
      if (vm && VALID_VIEW_MODES.includes(vm as ViewMode)) {
        this.currentViewMode.set(vm as ViewMode);
      }
      const step = params['step'];
      if (step !== undefined) {
        const num = parseInt(step, 10);
        if (!isNaN(num)) {
          this.initialStep.set(num);
        }
      }
    };
    applyParams(this.route.snapshot.queryParams);
    this.route.queryParams.subscribe(applyParams);
  }

  setViewMode(mode: ViewMode): void {
    this.currentViewMode.set(mode);
  }
}
