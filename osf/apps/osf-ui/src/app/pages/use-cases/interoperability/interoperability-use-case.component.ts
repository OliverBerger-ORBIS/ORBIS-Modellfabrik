import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UseCaseControlsComponent } from '../shared/use-case-controls/use-case-controls.component';
import { Uc06SvgGeneratorService } from './uc-06-svg-generator.service';
import { Uc06I18nService } from './uc-06-i18n.service';
import { BaseUseCaseComponent } from '../shared/base-use-case.component';
import { DomSanitizer } from '@angular/platform-browser';
import { ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { LanguageService } from '../../../services/language.service';

/**
 * Interoperability Use Case Component
 * Displays the Event-to-Process Map for the Interoperability use case
 * Uses dynamic SVG generation with I18n support (DE/EN/FR) and step animation
 */
@Component({
  selector: 'app-interoperability-use-case',
  standalone: true,
  imports: [CommonModule, UseCaseControlsComponent],
  templateUrl: './interoperability-use-case.component.html',
  styleUrls: ['./interoperability-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InteroperabilityUseCaseComponent extends BaseUseCaseComponent {
  constructor(
    sanitizer: DomSanitizer,
    cdr: ChangeDetectorRef,
    http: HttpClient,
    languageService: LanguageService,
    private readonly svgGenerator: Uc06SvgGeneratorService,
    private readonly i18nService: Uc06I18nService
  ) {
    super(sanitizer, cdr, http, languageService);
  }

  override getStepsUrl(): string {
    return 'assets/use-cases/uc-06/uc-06-event-to-process-map.steps.json';
  }

  override getStepPrefix(): string {
    return 'uc06';
  }

  override getConnectionIds(): readonly string[] {
    return [];
  }

  override async loadSvgContent(): Promise<string> {
    const i18nTexts = await this.i18nService.loadTexts();
    return this.svgGenerator.generateSvg(i18nTexts);
  }
}
