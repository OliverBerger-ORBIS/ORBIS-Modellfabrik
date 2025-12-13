import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { DspUseCasesComponent } from '../dsp-use-cases/dsp-use-cases.component';

/**
 * DSP Use Cases Section Component
 * 
 * Wrapper section for the DSP Use Cases content.
 */
@Component({
  standalone: true,
  selector: 'app-dsp-use-cases-section',
  imports: [CommonModule, DspUseCasesComponent],
  templateUrl: './dsp-use-cases-section.component.html',
  styleUrl: './dsp-use-cases-section.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspUseCasesSectionComponent {
  readonly sectionTitle = $localize`:@@dspUseCasesSectionTitle:Use Cases`;
  readonly sectionSubtitle = $localize`:@@dspUseCasesSectionSubtitle:Practical applications of DSP in smart manufacturing environments.`;
}
