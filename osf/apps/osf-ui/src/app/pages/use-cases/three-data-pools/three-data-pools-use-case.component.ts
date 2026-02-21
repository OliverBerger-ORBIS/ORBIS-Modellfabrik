import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UseCaseControlsComponent } from '../shared/use-case-controls/use-case-controls.component';
import { Uc02SvgGeneratorService } from './uc-02-svg-generator.service';
import { Uc02SvgGeneratorLanesService } from './uc-02-svg-generator-lanes.service';
import { Uc02I18nService } from './uc-02-i18n.service';
import { BaseUseCaseComponent } from '../shared/base-use-case.component';
import { DomSanitizer } from '@angular/platform-browser';
import { ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { LanguageService } from '../../../services/language.service';

export type Uc02ViewMode = 'concept' | 'lanes';

/**
 * Three Data Pools Use Case Component (UC-02)
 * Data Aggregation: Three Data Pools for Reliable KPIs
 */
@Component({
  selector: 'app-three-data-pools-use-case',
  standalone: true,
  imports: [CommonModule, UseCaseControlsComponent],
  templateUrl: './three-data-pools-use-case.component.html',
  styleUrls: ['./three-data-pools-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ThreeDataPoolsUseCaseComponent extends BaseUseCaseComponent {
  readonly useCaseTitle = $localize`:@@threeDataPoolsUseCaseHeadline:Data Aggregation: Three Data Pools for Reliable KPIs`;

  protected readonly viewModeConceptLabel = $localize`:@@uc02ViewConcept:Concept (Sources → DSP → Targets)`;
  protected readonly viewModeLanesLabel = $localize`:@@uc02ViewLanes:Architecture Lanes (Analytics | DSP | Data)`;

  viewMode: Uc02ViewMode = 'concept';

  constructor(
    sanitizer: DomSanitizer,
    cdr: ChangeDetectorRef,
    http: HttpClient,
    languageService: LanguageService,
    private readonly svgGenerator: Uc02SvgGeneratorService,
    private readonly svgGeneratorLanes: Uc02SvgGeneratorLanesService,
    private readonly i18nService: Uc02I18nService
  ) {
    super(sanitizer, cdr, http, languageService);
  }

  override getStepsUrl(): string {
    return 'assets/use-cases/uc-02/uc-02-three-data-pools.steps.json';
  }

  override getStepPrefix(): string {
    return 'uc02';
  }

  override getConnectionIds(): readonly string[] {
    return [];
  }

  override async loadSvgContent(): Promise<string> {
    const i18nTexts = await this.i18nService.loadTexts();
    const generator = this.viewMode === 'lanes' ? this.svgGeneratorLanes : this.svgGenerator;
    return generator.generateSvg(i18nTexts);
  }

  protected setViewMode(mode: Uc02ViewMode): void {
    if (this.viewMode === mode) return;
    this.viewMode = mode;
    this.loadSvg();
  }
}
