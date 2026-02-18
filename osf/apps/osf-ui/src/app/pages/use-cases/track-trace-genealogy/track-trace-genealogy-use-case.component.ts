import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UseCaseControlsComponent } from '../shared/use-case-controls/use-case-controls.component';
import { Uc01SvgGeneratorService } from './uc-01-svg-generator.service';
import { Uc01I18nService } from './uc-01-i18n.service';
import { BaseUseCaseComponent } from '../shared/base-use-case.component';
import { DomSanitizer } from '@angular/platform-browser';
import { ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { LanguageService } from '../../../services/language.service';

/**
 * Track & Trace Genealogy Use Case Component
 * Displays the Track & Trace Genealogy diagram with step animation
 * Uses dynamic SVG generation with I18n support (DE/EN/FR)
 */
@Component({
  selector: 'app-track-trace-genealogy-use-case',
  standalone: true,
  imports: [CommonModule, UseCaseControlsComponent],
  templateUrl: './track-trace-genealogy-use-case.component.html',
  styleUrls: ['./track-trace-genealogy-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TrackTraceGenealogyUseCaseComponent extends BaseUseCaseComponent {
  constructor(
    sanitizer: DomSanitizer,
    cdr: ChangeDetectorRef,
    http: HttpClient,
    languageService: LanguageService,
    private readonly svgGenerator: Uc01SvgGeneratorService,
    private readonly i18nService: Uc01I18nService
  ) {
    super(sanitizer, cdr, http, languageService);
  }

  override getStepsUrl(): string {
    return 'assets/use-cases/uc-01/uc-01-track-trace-genealogy.steps.json';
  }

  override getStepPrefix(): string {
    return 'uc01';
  }

  override getConnectionIds(): readonly string[] {
    return [];
  }

  override async loadSvgContent(): Promise<string> {
    const i18nTexts = await this.i18nService.loadTexts();
    return this.svgGenerator.generateSvg(i18nTexts);
  }
}
