import { Component, ChangeDetectionStrategy } from '@angular/core';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { DEF_CONFIG } from '../../../../components/dsp-animation/configs/def/def-config';

/**
 * DEF (Digital Engineering Facility) DSP Architecture Page
 * Displays DSP architecture customized for DEF's equipment and systems
 */
@Component({
  standalone: true,
  selector: 'app-def-dsp-page',
  imports: [DspAnimationComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="customer-dsp-page">
      <header class="customer-header">
        <h1>{{ config.customerName }} - DSP Architecture</h1>
        <p class="subtitle">Interactive demonstration of DSP architecture tailored for {{ config.customerName }}</p>
      </header>
      <app-dsp-animation
        [viewMode]="'functional'"
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
      margin: 0;
    }
  `],
})
export class DefDspPageComponent {
  config = DEF_CONFIG;
}
