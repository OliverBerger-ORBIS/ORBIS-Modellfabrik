import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { ExternalLinksService } from '../../../../services/external-links.service';
import { LanguageService } from '../../../../services/language.service';
import { FMF_CONFIG } from '../../../../components/dsp-animation/configs/fmf/fmf-config';

/**
 * DSP Architecture Functional Section Component
 * 
 * Displays the DSP architecture animation in functional view mode.
 * Uses FMF (Fischertechnik Modellfabrik) as default customer configuration.
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
  readonly customerConfig = FMF_CONFIG; // Use FMF as default customer

  constructor(
    private readonly router: Router,
    private readonly route: ActivatedRoute,
    private readonly externalLinksService: ExternalLinksService,
    private readonly languageService: LanguageService
  ) {}

  onActionTriggered(event: { id: string; url: string }): void {
    if (!event.url) {
      return;
    }

    const locale = this.languageService.current;

    // Check if it's an external URL (http/https)
    if (event.url.startsWith('http://') || event.url.startsWith('https://')) {
      window.open(event.url, '_blank', 'noreferrer noopener');
      return;
    }

    // Check if it's an absolute internal path (starts with /)
    if (event.url.startsWith('/')) {
      // Remove leading slash and prepend locale
      const pathWithoutSlash = event.url.substring(1);
      const fullPath = `/${locale}/${pathWithoutSlash}`;
      this.router.navigateByUrl(fullPath);
      return;
    }

    // Handle shopfloor devices - navigate to module page with device ID
    if (event.id.startsWith('sf-device-')) {
      // Extract module type from device ID (e.g., 'sf-device-mill' -> 'MILL')
      const moduleType = event.id.replace('sf-device-', '').toUpperCase();
      const fullPath = `/${locale}/module`;
      this.router.navigate([fullPath], { 
        queryParams: { module: moduleType },
        fragment: moduleType 
      });
      return;
    }

    // Relative path - prepend with locale
    const fullPath = `/${locale}/${event.url}`;
    this.router.navigateByUrl(fullPath);
  }
}
