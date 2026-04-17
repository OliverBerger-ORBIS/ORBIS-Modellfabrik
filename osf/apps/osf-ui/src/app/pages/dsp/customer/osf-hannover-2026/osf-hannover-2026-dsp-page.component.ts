import { Component, ChangeDetectionStrategy, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { OSF_HANNOVER_2026_CONFIG } from '../../../../components/dsp-animation/configs/osf/osf-hannover-2026-config';
import { VIEW_MODES } from '../shared/view-modes.const';
import { CUSTOMER_PAGE_STYLES } from '../shared/customer-page.styles';
import type { ViewMode } from '../../../../components/dsp-animation/types';

const VALID_VIEW_MODES: ViewMode[] = ['functional', 'component', 'deployment'];

@Component({
  standalone: true,
  selector: 'app-osf-hannover-2026-dsp-page',
  imports: [CommonModule, DspAnimationComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="customer-dsp-page">
      <header class="customer-header">
        <h1>{{ config.customerName }} - DSP Architecture</h1>
        <p class="subtitle">Slimmed-down presentation sequence for Hannover Messe.</p>

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
export class OsfHannover2026DspPageComponent implements OnInit {
  config = OSF_HANNOVER_2026_CONFIG;
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

