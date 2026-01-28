import { Component, ChangeDetectionStrategy, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { LanguageService } from '../../../services/language.service';
import { Uc06SvgGeneratorService } from './uc-06-svg-generator.service';
import { Uc06SvgGeneratorEnhancedService } from './uc-06-svg-generator-enhanced.service';
import { Uc06I18nService } from './uc-06-i18n.service';

/**
 * Interoperability Use Case Component
 * Displays the Event-to-Process Map for the Interoperability use case
 * Uses dynamic SVG generation with I18n support (DE/EN/FR)
 */
@Component({
  selector: 'app-interoperability-use-case',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './interoperability-use-case.component.html',
  styleUrls: ['./interoperability-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InteroperabilityUseCaseComponent implements OnInit {
  svgContent: SafeHtml | null = null;
  isLoading = true;

  constructor(
    private readonly languageService: LanguageService,
    private readonly sanitizer: DomSanitizer,
    private readonly cdr: ChangeDetectorRef,
    private readonly svgGenerator: Uc06SvgGeneratorService,
    private readonly svgGeneratorEnhanced: Uc06SvgGeneratorEnhancedService,
    private readonly i18nService: Uc06I18nService
  ) {}

  async ngOnInit(): Promise<void> {
    await this.loadSvg();
  }

  private async loadSvg(): Promise<void> {
    try {
      // Load I18n texts
      const i18nTexts = await this.i18nService.loadTexts();
      
      // Use enhanced generator for EN locale, standard for others
      const isEnglish = this.languageService.current === 'en';
      const generator = isEnglish ? this.svgGeneratorEnhanced : this.svgGenerator;
      
      // Generate SVG dynamically
      const svgString = generator.generateSvg(i18nTexts);
      
      if (svgString) {
        // Sanitize and set SVG content for inline rendering
        this.svgContent = this.sanitizer.bypassSecurityTrustHtml(svgString);
        this.isLoading = false;
        this.cdr.markForCheck();
      }
    } catch (error) {
      console.error('Failed to generate SVG:', error);
      this.isLoading = false;
      this.cdr.markForCheck();
    }
  }
}
