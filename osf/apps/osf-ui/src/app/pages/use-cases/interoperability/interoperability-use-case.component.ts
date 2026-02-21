import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UseCaseControlsComponent } from '../shared/use-case-controls/use-case-controls.component';
import { Uc00SvgGeneratorService } from './uc-00-svg-generator.service';
import { Uc00I18nService } from './uc-00-i18n.service';
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
  readonly useCaseTitle = $localize`:@@interoperabilityUseCaseHeadline:Interoperability (Event-to-Process Map)`;

  constructor(
    sanitizer: DomSanitizer,
    cdr: ChangeDetectorRef,
    http: HttpClient,
    languageService: LanguageService,
    private readonly svgGenerator: Uc00SvgGeneratorService,
    private readonly i18nService: Uc00I18nService
  ) {
    super(sanitizer, cdr, http, languageService);
  }

  override getStepsUrl(): string {
    return 'assets/use-cases/uc-00/uc-00-event-to-process-map.steps.json';
  }

  override getStepPrefix(): string {
    return 'uc00';
  }

  override getConnectionIds(): readonly string[] {
    return [];
  }

  override async loadSvgContent(): Promise<string> {
    const i18nTexts = await this.i18nService.loadTexts();
    return this.svgGenerator.generateSvg(i18nTexts);
  }
}
