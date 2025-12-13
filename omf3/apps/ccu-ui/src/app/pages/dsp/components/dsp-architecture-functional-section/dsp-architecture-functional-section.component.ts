import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { ExternalLinksService } from '../../../../services/external-links.service';

/**
 * DSP Architecture Functional Section Component
 * 
 * Displays the DSP architecture animation in functional view mode.
 */
@Component({
  standalone: true,
  selector: 'app-dsp-architecture-functional-section',
  imports: [CommonModule, DspAnimationComponent],
  templateUrl: './dsp-architecture-functional-section.component.html',
  styleUrl: './dsp-architecture-functional-section.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspArchitectureFunctionalSectionComponent {
  readonly sectionTitle = $localize`:@@dspArchFunctionalSectionTitle:Architecture`;
  readonly sectionSubtitle = $localize`:@@dspArchFunctionalSectionSubtitle:Functional view of the DSP reference architecture with step-by-step animation.`;
  
  readonly viewMode = 'functional' as const;

  private locale = 'en';

  constructor(
    private readonly router: Router,
    private readonly route: ActivatedRoute,
    private readonly externalLinksService: ExternalLinksService
  ) {}

  onActionTriggered(event: { id: string; url: string }): void {
    if (!event.url) {
      return;
    }

    // Check if it's an external URL (http/https)
    if (event.url.startsWith('http://') || event.url.startsWith('https://')) {
      window.open(event.url, '_blank', 'noreferrer noopener');
      return;
    }

    // Check if it's an absolute internal path
    if (event.url.startsWith('/')) {
      this.router.navigateByUrl(event.url);
      return;
    }

    // Relative path - prepend with locale
    const fullPath = `/${this.locale}/${event.url}`;
    this.router.navigateByUrl(fullPath);
  }
}
