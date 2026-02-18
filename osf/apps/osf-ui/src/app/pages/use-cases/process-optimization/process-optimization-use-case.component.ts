import { ChangeDetectionStrategy, ChangeDetectorRef, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer } from '@angular/platform-browser';
import { HttpClient } from '@angular/common/http';
import { UseCaseControlsComponent } from '../shared/use-case-controls/use-case-controls.component';
import { Uc07SvgGeneratorService } from './uc-07-svg-generator.service';
import { Uc07I18nService } from './uc-07-i18n.service';
import { UC07_CONNECTION_IDS } from './uc-07-structure.config';
import { BaseUseCaseComponent } from '../shared/base-use-case.component';
import { LanguageService } from '../../../services/language.service';

/**
 * Process Optimization Use Case Component (UC-07)
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
  constructor(
    sanitizer: DomSanitizer,
    cdr: ChangeDetectorRef,
    http: HttpClient,
    languageService: LanguageService,
    private readonly svgGenerator: Uc07SvgGeneratorService,
    private readonly i18nService: Uc07I18nService
  ) {
    super(sanitizer, cdr, http, languageService);
  }

  override getStepsUrl(): string {
    return 'assets/use-cases/uc-07/uc-07-process-optimization.steps.json';
  }

  override getStepPrefix(): string {
    return 'uc07';
  }

  override getConnectionIds(): readonly string[] {
    return UC07_CONNECTION_IDS;
  }

  override async loadSvgContent(): Promise<string> {
    const i18nTexts = await this.i18nService.loadTexts();
    return this.svgGenerator.generateSvg(i18nTexts);
  }
}
