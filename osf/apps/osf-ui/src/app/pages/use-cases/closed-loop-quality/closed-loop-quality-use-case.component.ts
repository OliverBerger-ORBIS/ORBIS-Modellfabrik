import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UseCaseControlsComponent } from '../shared/use-case-controls/use-case-controls.component';
import { Uc04SvgGeneratorService } from './uc-04-svg-generator.service';
import { Uc04I18nService } from './uc-04-i18n.service';
import { UC04_CONNECTION_IDS } from './uc-04-structure.config';
import { BaseUseCaseComponent } from '../shared/base-use-case.component';
import { DomSanitizer } from '@angular/platform-browser';
import { ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { LanguageService } from '../../../services/language.service';

/**
 * Closed Loop Quality Use Case Component (UC-04)
 * Quality Inspection Event → Decide → Act → Feedback to MES/ERP/Analytics
 */
@Component({
  selector: 'app-closed-loop-quality-use-case',
  standalone: true,
  imports: [CommonModule, UseCaseControlsComponent],
  templateUrl: './closed-loop-quality-use-case.component.html',
  styleUrls: ['./closed-loop-quality-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClosedLoopQualityUseCaseComponent extends BaseUseCaseComponent {
  readonly useCaseTitle = $localize`:@@closedLoopQualityUseCaseHeadline:Closed Loop Quality`;

  constructor(
    sanitizer: DomSanitizer,
    cdr: ChangeDetectorRef,
    http: HttpClient,
    languageService: LanguageService,
    private readonly svgGenerator: Uc04SvgGeneratorService,
    private readonly i18nService: Uc04I18nService
  ) {
    super(sanitizer, cdr, http, languageService);
  }

  override getStepsUrl(): string {
    return 'assets/use-cases/uc-04/uc-04-closed-loop-quality.steps.json';
  }

  override getStepPrefix(): string {
    return 'uc04';
  }

  override getConnectionIds(): readonly string[] {
    return UC04_CONNECTION_IDS;
  }

  override async loadSvgContent(): Promise<string> {
    const i18nTexts = await this.i18nService.loadTexts();
    return this.svgGenerator.generateSvg(i18nTexts);
  }
}
