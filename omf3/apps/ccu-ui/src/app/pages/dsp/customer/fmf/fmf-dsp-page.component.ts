import { Component, ChangeDetectionStrategy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { FMF_CONFIG } from '../../../../components/dsp-animation/configs/fmf/fmf-config';
import type { ViewMode } from '../../../../components/dsp-animation/types';

/**
 * FMF (Fischertechnik Modellfabrik) DSP Architecture Page
 * Displays DSP architecture customized for FMF's equipment and systems
 * Supports functional, component, and deployment view modes
 */
@Component({
  standalone: true,
  selector: 'app-fmf-dsp-page',
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
  styles: [`
    .customer-dsp-page {
      padding: 2rem;
      min-height: 100vh;
      background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    .customer-header {
      text-align: center;
      margin-bottom: 2rem;
    }
    
    .customer-header h1 {
      font-size: 2rem;
      font-weight: 600;
      color: #164194;
      margin-bottom: 0.5rem;
    }
    
    .customer-header .subtitle {
      font-size: 1rem;
      color: #6b7280;
      margin: 0 0 1rem 0;
    }
    
    .view-mode-selector {
      display: flex;
      justify-content: center;
      gap: 0.5rem;
      margin-top: 1rem;
    }
    
    .view-mode-btn {
      padding: 0.5rem 1.5rem;
      border: 2px solid #164194;
      background: white;
      color: #164194;
      border-radius: 0.25rem;
      cursor: pointer;
      font-weight: 500;
      transition: all 0.2s;
    }
    
    .view-mode-btn:hover {
      background: #f0f4ff;
    }
    
    .view-mode-btn.active {
      background: #164194;
      color: white;
    }
  `],
})
export class FmfDspPageComponent {
  config = FMF_CONFIG;
  currentViewMode = signal<ViewMode>('functional');
  
  viewModes = [
    { value: 'functional' as ViewMode, label: 'Functional View' },
    { value: 'component' as ViewMode, label: 'Component View' },
    { value: 'deployment' as ViewMode, label: 'Deployment View' },
  ];
  
  setViewMode(mode: ViewMode): void {
    this.currentViewMode.set(mode);
  }
}
