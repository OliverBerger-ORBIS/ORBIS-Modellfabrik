import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { DspMethodologyComponent } from '../dsp-methodology/dsp-methodology.component';

/**
 * DSP Methodology Section Component
 * 
 * Wrapper section for the DSP Methodology content.
 */
@Component({
  standalone: true,
  selector: 'app-dsp-methodology-section',
  imports: [CommonModule, DspMethodologyComponent],
  templateUrl: './dsp-methodology-section.component.html',
  styleUrl: './dsp-methodology-section.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspMethodologySectionComponent {
  readonly sectionTitle = $localize`:@@dspMethodologySectionTitle:Methodology`;
  readonly sectionSubtitle = $localize`:@@dspMethodologySectionSubtitle:A structured 5-phase approach from data foundation to AI-driven autonomous operations.`;
}
