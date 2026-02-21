import { ChangeDetectionStrategy, ChangeDetectorRef, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer } from '@angular/platform-browser';
import { HttpClient } from '@angular/common/http';
import { UseCaseControlsComponent } from '../shared/use-case-controls/use-case-controls.component';
import { Uc06SvgGeneratorService } from './uc-06-svg-generator.service';
import { Uc06I18nService } from './uc-06-i18n.service';
import { UC06_CONNECTION_IDS } from './uc-06-structure.config';
import { BaseUseCaseComponent } from '../shared/base-use-case.component';
import { LanguageService } from '../../../services/language.service';

/**
 * Process Optimization Use Case Component (UC-06)
 * Observe → Analyze → Recommend → Simulate → Execute → Feedback (KPI-to-Action Loop)
 */
@Component({
  selector: 'app-process-optimization-use-case',
  standalone: true,
  imports: [CommonModule, UseCaseControlsComponent],
  templateUrl: './process-optimization-use-case.component.html',
  styleUrls: ['./process-optimization-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProcessOptimizationUseCaseComponent extends BaseUseCaseComponent {
  readonly useCaseTitle = $localize`:@@processOptimizationUseCaseHeadline:Process Optimization`;

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
    return 'assets/use-cases/uc-06/uc-06-process-optimization.steps.json';
  }

  override getStepPrefix(): string {
    return 'uc06';
  }

  override getConnectionIds(): readonly string[] {
    return UC06_CONNECTION_IDS;
  }

  override async loadSvgContent(): Promise<string> {
    const i18nTexts = await this.i18nService.loadTexts();
    return this.svgGenerator.generateSvg(i18nTexts);
  }
}
