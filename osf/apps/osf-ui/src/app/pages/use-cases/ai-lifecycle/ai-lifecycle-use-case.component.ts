import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UseCaseControlsComponent } from '../shared/use-case-controls/use-case-controls.component';
import { Uc03SvgGeneratorService } from './uc-03-svg-generator.service';
import { Uc03I18nService } from './uc-03-i18n.service';
import { UC03_CONNECTION_IDS } from './uc-03-structure.config';
import { BaseUseCaseComponent } from '../shared/base-use-case.component';
import { DomSanitizer } from '@angular/platform-browser';
import { ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { LanguageService } from '../../../services/language.service';

/**
 * AI Lifecycle Use Case Component (UC-03)
 * Train centrally → Deploy to multiple stations via DSP Edge + Management Cockpit
 */
@Component({
  selector: 'app-ai-lifecycle-use-case',
  standalone: true,
  imports: [CommonModule, UseCaseControlsComponent],
  templateUrl: './ai-lifecycle-use-case.component.html',
  styleUrls: ['./ai-lifecycle-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AiLifecycleUseCaseComponent extends BaseUseCaseComponent {
  constructor(
    sanitizer: DomSanitizer,
    cdr: ChangeDetectorRef,
    http: HttpClient,
    languageService: LanguageService,
    private readonly svgGenerator: Uc03SvgGeneratorService,
    private readonly i18nService: Uc03I18nService
  ) {
    super(sanitizer, cdr, http, languageService);
  }

  override getStepsUrl(): string {
    return 'assets/use-cases/uc-03/uc-03-ai-lifecycle.steps.json';
  }

  override getStepPrefix(): string {
    return 'uc03';
  }

  override getConnectionIds(): readonly string[] {
    return UC03_CONNECTION_IDS;
  }

  override async loadSvgContent(): Promise<string> {
    const i18nTexts = await this.i18nService.loadTexts();
    return this.svgGenerator.generateSvg(i18nTexts);
  }
}
