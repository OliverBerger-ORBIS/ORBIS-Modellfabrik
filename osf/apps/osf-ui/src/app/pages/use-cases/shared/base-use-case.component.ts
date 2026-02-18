import {
  Component,
  ChangeDetectionStrategy,
  OnInit,
  OnDestroy,
  ChangeDetectorRef,
  AfterViewInit,
  ElementRef,
  ViewChild,
  Directive,
} from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { HttpClient } from '@angular/common/http';
import { LanguageService } from '../../../services/language.service';
import { applyStepToSvg } from './use-case-step-apply';

/**
 * Common step interface for all Use-Case diagram steps.
 * highlightIds, hideIds required. dimIds/showIds nicht mehr verwendet (Auto-Dim).
 */
export interface UseCaseStep {
  id: string;
  title: { de: string; en: string; fr?: string };
  description?: { de: string; en: string; fr?: string };
  highlightIds: string[];
  hideIds: string[];
}

/**
 * Abstract base class for Use-Case diagram components.
 *
 * Handles: steps loading, SVG loading (delegated to subclass via loadSvgContent),
 * step animation (applyStepToSvg), navigation, zoom, auto-play, description toggle.
 *
 * Subclasses must provide:
 * - getStepsUrl(): steps JSON path
 * - getStepPrefix(): e.g. 'uc01', 'uc02' for SVG element IDs
 * - getConnectionIds(): connection IDs for dim-conn (empty array if none)
 * - loadSvgContent(): returns SVG string (uses i18n + generator)
 */
@Directive()
export abstract class BaseUseCaseComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('svgContainer', { static: false }) svgContainer?: ElementRef<HTMLDivElement>;

  svgContent: SafeHtml | null = null;
  isLoading = true;

  steps: UseCaseStep[] = [];
  currentStepIndex = 0;
  isAutoPlaying = false;
  loopToStart = true;
  showDescription = false;
  private autoPlayInterval: ReturnType<typeof setInterval> | null = null;

  zoom = 1;
  protected readonly minZoom = 0.4;
  protected readonly maxZoom = 1.8;
  private readonly ZOOM_STEP_FINE = 0.05;
  private readonly ZOOM_STEP_COARSE = 0.1;

  protected readonly btnPrev = $localize`:@@dspArchPrev:Previous`;
  protected readonly btnNext = $localize`:@@dspArchNext:Next`;
  protected readonly btnAutoPlay = $localize`:@@dspArchAutoPlay:Auto Play`;
  protected readonly btnStopPlay = $localize`:@@dspArchStopPlay:Stop`;
  protected readonly zoomOutLabel = $localize`:@@shopfloorPreviewZoomOut:Zoom out`;
  protected readonly zoomInLabel = $localize`:@@shopfloorPreviewZoomIn:Zoom in`;
  protected readonly resetZoomLabel = $localize`:@@shopfloorPreviewResetZoom:Reset zoom`;

  constructor(
    protected readonly sanitizer: DomSanitizer,
    protected readonly cdr: ChangeDetectorRef,
    protected readonly http: HttpClient,
    protected readonly languageService: LanguageService
  ) {}

  abstract getStepsUrl(): string;
  abstract getStepPrefix(): string;
  abstract getConnectionIds(): readonly string[];
  abstract loadSvgContent(): Promise<string>;

  async ngOnInit(): Promise<void> {
    await Promise.all([this.loadSteps(), this.loadSvg()]);
  }

  ngAfterViewInit(): void {
    setTimeout(() => this.applyStep(this.currentStepIndex), 0);
  }

  ngOnDestroy(): void {
    this.stopAutoPlay();
  }

  protected async loadSteps(): Promise<void> {
    try {
      const stepsData = await this.http.get<UseCaseStep[]>(this.getStepsUrl()).toPromise();
      if (stepsData) {
        this.steps = stepsData;
        this.cdr.markForCheck();
      }
    } catch (error) {
      console.error('Failed to load steps:', error);
    }
  }

  protected async loadSvg(): Promise<void> {
    try {
      this.isLoading = true;
      this.cdr.markForCheck();

      const svgString = await this.loadSvgContent();
      if (svgString) {
        this.svgContent = this.sanitizer.bypassSecurityTrustHtml(svgString);
        this.isLoading = false;
        this.cdr.markForCheck();
        this.cdr.detectChanges();
        setTimeout(() => this.applyStep(this.currentStepIndex), 80);
      }
    } catch (error) {
      console.error('Failed to generate SVG:', error);
      this.isLoading = false;
      this.cdr.markForCheck();
    }
  }

  protected prevStep(): void {
    if (this.currentStepIndex > 0) {
      this.applyStep(this.currentStepIndex - 1);
    }
  }

  protected nextStep(): void {
    if (this.currentStepIndex < this.steps.length - 1) {
      this.applyStep(this.currentStepIndex + 1);
    } else {
      this.applyStep(0);
    }
  }

  protected goToStep(index: number): void {
    if (index >= 0 && index < this.steps.length) {
      this.applyStep(index);
    }
  }

  protected toggleAutoPlay(): void {
    if (this.isAutoPlaying) {
      this.stopAutoPlay();
    } else {
      this.startAutoPlay();
    }
  }

  private startAutoPlay(): void {
    this.isAutoPlaying = true;
    this.autoPlayInterval = setInterval(() => {
      if (this.currentStepIndex < this.steps.length - 1) {
        this.nextStep();
      } else {
        if (this.loopToStart) {
          this.applyStep(0);
        } else {
          this.stopAutoPlay();
        }
      }
    }, 3000);
    this.cdr.markForCheck();
  }

  protected toggleLoop(): void {
    this.loopToStart = !this.loopToStart;
    this.cdr.markForCheck();
  }

  protected toggleDescription(): void {
    this.showDescription = !this.showDescription;
    this.applyStep(this.currentStepIndex);
    this.cdr.markForCheck();
  }

  private stopAutoPlay(): void {
    this.isAutoPlaying = false;
    if (this.autoPlayInterval) {
      clearInterval(this.autoPlayInterval);
      this.autoPlayInterval = null;
    }
    this.cdr.markForCheck();
  }

  private applyStep(index: number): void {
    const step = this.steps[index];
    if (!step) return;

    this.currentStepIndex = index;

    setTimeout(() => {
      const svgElement = this.svgContainer?.nativeElement?.querySelector('svg');
      if (!svgElement) return;

      applyStepToSvg({
        svgElement,
        step: { highlightIds: step.highlightIds, hideIds: step.hideIds },
        stepIndex: index,
        stepPrefix: this.getStepPrefix(),
        connectionIds: this.getConnectionIds(),
        showDescription: this.showDescription,
        getStepTitle: () => this.getCurrentStepTitle(),
        getStepDescription: () => this.getCurrentStepDescription(),
      });
    }, 0);

    this.cdr.markForCheck();
  }

  protected getStepTitle(step: UseCaseStep | undefined): string {
    if (!step) return '';
    const locale = this.languageService.current;
    if (locale === 'fr' && step.title.fr) return step.title.fr;
    if (locale === 'de' && step.title.de) return step.title.de;
    return step.title.en;
  }

  protected getCurrentStepTitle(): string {
    return this.getStepTitle(this.steps[this.currentStepIndex]);
  }

  protected getCurrentStepDescription(): string {
    const step = this.steps[this.currentStepIndex];
    if (!step?.description) return '';
    const locale = this.languageService.current;
    if (locale === 'fr' && step.description.fr) return step.description.fr;
    if (locale === 'de' && step.description.de) return step.description.de;
    return step.description.en || '';
  }

  protected zoomIn(): void {
    const step = this.zoom < 1 ? this.ZOOM_STEP_FINE : this.ZOOM_STEP_COARSE;
    this.zoom = Math.min(this.maxZoom, this.zoom + step);
    this.cdr.markForCheck();
  }

  protected zoomOut(): void {
    const step = this.zoom <= 1 ? this.ZOOM_STEP_FINE : this.ZOOM_STEP_COARSE;
    this.zoom = Math.max(this.minZoom, this.zoom - step);
    this.cdr.markForCheck();
  }

  protected resetZoom(): void {
    this.zoom = 1;
    this.cdr.markForCheck();
  }
}
