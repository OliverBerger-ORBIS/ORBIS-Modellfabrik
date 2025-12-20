import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { ExternalLinksService } from '../../../../services/external-links.service';
import { LanguageService } from '../../../../services/language.service';
import { FMF_CONFIG } from '../../../../components/dsp-animation/configs/fmf/fmf-config';

/**
 * DSP Architecture Component Section Component
 * 
 * Displays the DSP architecture animation in component view mode.
 * Uses FMF (Fischertechnik Modellfabrik) as default customer configuration.
 */
@Component({
  standalone: true,
  selector: 'app-dsp-architecture-component-section',
  imports: [CommonModule, DspAnimationComponent],
  templateUrl: './dsp-architecture-component-section.component.html',
  styleUrl: './dsp-architecture-component-section.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspArchitectureComponentSectionComponent {
  readonly sectionTitle = $localize`:@@dspArchComponentSectionTitle:Components`;
  readonly sectionSubtitle = $localize`:@@dspArchComponentSectionSubtitle:Component view showing internal DSP Edge components and their connections.`;
  
  readonly viewMode = 'component' as const;
  readonly customerConfig = FMF_CONFIG; // Use FMF as default customer

  private locale = 'en';

  constructor(
    private readonly router: Router,
    private readonly route: ActivatedRoute,
    private readonly externalLinksService: ExternalLinksService,
    private readonly languageService: LanguageService
  ) {}

  private getErpUrl(): string {
    // Task 12: Use ERP URL from settings, fallback to 'process' for internal route
    return this.externalLinksService.current.erpSystemUrl || 'process';
  }

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

    // Task 11: Handle shopfloor devices - navigate to module page with device ID
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

    // Task 10: Handle AGV/FTS systems - navigate to AGV-Tab
    if (event.id.startsWith('sf-system-') && (event.url === 'fts' || event.id.includes('fts') || event.id.includes('agv'))) {
      const fullPath = `/${locale}/fts`;
      this.router.navigateByUrl(fullPath);
      return;
    }

    // Task 12: Handle BP-ERP - navigate to Process-Tab or external ERP/SAP URL
    if (event.id === 'bp-erp') {
      const erpUrl = this.getErpUrl();
      // Check if it's an external URL (http/https)
      if (erpUrl.startsWith('http://') || erpUrl.startsWith('https://')) {
        window.open(erpUrl, '_blank', 'noreferrer noopener');
        return;
      }
      // Internal route - navigate to Process-Tab
      const fullPath = `/${locale}/${erpUrl}`;
      this.router.navigateByUrl(fullPath);
      return;
    }

    // Relative path - prepend with locale
    const fullPath = `/${locale}/${event.url}`;
    this.router.navigateByUrl(fullPath);
  }
}
