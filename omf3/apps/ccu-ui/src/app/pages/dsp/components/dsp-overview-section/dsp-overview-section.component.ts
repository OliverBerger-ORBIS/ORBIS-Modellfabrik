import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { DspIntroComponent } from '../dsp-intro/dsp-intro.component';

/**
 * DSP Overview Section Component
 * 
 * Wrapper section for the DSP Introduction/Overview content.
 */
@Component({
  standalone: true,
  selector: 'app-dsp-overview-section',
  imports: [CommonModule, DspIntroComponent],
  templateUrl: './dsp-overview-section.component.html',
  styleUrl: './dsp-overview-section.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspOverviewSectionComponent {
  readonly sectionTitle = $localize`:@@dspOverviewSectionTitle:Overview`;
  readonly sectionSubtitle = $localize`:@@dspOverviewSectionSubtitle:What is DSP?`;
}
