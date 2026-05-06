import { Component, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UseCaseControlsComponent } from '../shared/use-case-controls/use-case-controls.component';
import { BaseUseCaseComponent } from '../shared/base-use-case.component';
import { DomSanitizer } from '@angular/platform-browser';
import { HttpClient } from '@angular/common/http';
import { LanguageService } from '../../../services/language.service';
import { ViewScaleService } from '../../../services/view-scale.service';
import { Uc07SvgGeneratorService } from './uc-07-svg-generator.service';
import { Uc07I18nService } from './uc-07-i18n.service';
import { UC07_CONNECTION_IDS } from './uc-07-structure.config';

@Component({
  selector: 'app-anomaly-detection-use-case',
  standalone: true,
  imports: [CommonModule, UseCaseControlsComponent],
  templateUrl: './anomaly-detection-use-case.component.html',
  styleUrls: ['./anomaly-detection-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AnomalyDetectionUseCaseComponent extends BaseUseCaseComponent {
  readonly useCaseTitle = $localize`:@@anomalyDetectionUseCaseHeadline:Anomaly Detection`;
  activeTab: 'concept' | 'live-demo' = 'concept';

  constructor(
    sanitizer: DomSanitizer,
    cdr: ChangeDetectorRef,
    http: HttpClient,
    languageService: LanguageService,
    viewScale: ViewScaleService,
    private readonly svgGenerator: Uc07SvgGeneratorService,
    private readonly i18nService: Uc07I18nService
  ) {
    super(sanitizer, cdr, http, languageService, viewScale);
  }

  override getStepsUrl(): string {
    return 'assets/use-cases/uc-07/uc-07-anomaly-detection.steps.json';
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
