import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UseCaseControlsComponent } from '../shared/use-case-controls/use-case-controls.component';
import { Uc05SvgGeneratorService } from './uc-05-svg-generator.service';
import { Uc05I18nService } from './uc-05-i18n.service';
import { UC05_CONNECTION_IDS } from './uc-05-structure.config';
import { BaseUseCaseComponent } from '../shared/base-use-case.component';
import { DomSanitizer } from '@angular/platform-browser';
import { ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { LanguageService } from '../../../services/language.service';

/**
 * Predictive Maintenance Use Case Component (UC-05)
 * Condition monitoring: Detect → Evaluate → Alarm → Act → Feedback
 */
@Component({
  selector: 'app-predictive-maintenance-use-case',
  standalone: true,
  imports: [CommonModule, UseCaseControlsComponent],
  templateUrl: './predictive-maintenance-use-case.component.html',
  styleUrls: ['./predictive-maintenance-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PredictiveMaintenanceUseCaseComponent extends BaseUseCaseComponent {
  constructor(
    sanitizer: DomSanitizer,
    cdr: ChangeDetectorRef,
    http: HttpClient,
    languageService: LanguageService,
    private readonly svgGenerator: Uc05SvgGeneratorService,
    private readonly i18nService: Uc05I18nService
  ) {
    super(sanitizer, cdr, http, languageService);
  }

  override getStepsUrl(): string {
    return 'assets/use-cases/uc-05/uc-05-predictive-maintenance.steps.json';
  }

  override getStepPrefix(): string {
    return 'uc05';
  }

  override getConnectionIds(): readonly string[] {
    return UC05_CONNECTION_IDS;
  }

  override async loadSvgContent(): Promise<string> {
    const i18nTexts = await this.i18nService.loadTexts();
    return this.svgGenerator.generateSvg(i18nTexts);
  }
}
