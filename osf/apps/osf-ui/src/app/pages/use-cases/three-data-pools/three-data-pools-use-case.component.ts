import {
  Component,
  ChangeDetectionStrategy,
  OnInit,
  OnDestroy,
  ChangeDetectorRef,
  AfterViewInit,
  ElementRef,
  ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { HttpClient } from '@angular/common/http';
import { Uc02SvgGeneratorService } from './uc-02-svg-generator.service';
import { Uc02SvgGeneratorLanesService } from './uc-02-svg-generator-lanes.service';
import { Uc02I18nService } from './uc-02-i18n.service';
import { LanguageService } from '../../../services/language.service';

export type Uc02ViewMode = 'concept' | 'lanes';

interface Uc02Step {
  id: string;
  title: { de: string; en: string; fr?: string };
  description?: { de: string; en: string; fr?: string };
  highlightIds: string[];
  dimIds: string[];
  hideIds: string[];
}

/**
 * Three Data Pools Use Case Component (UC-02)
 * Data Aggregation: Three Data Pools for Reliable KPIs
 */
@Component({
  selector: 'app-three-data-pools-use-case',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './three-data-pools-use-case.component.html',
  styleUrls: ['./three-data-pools-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ThreeDataPoolsUseCaseComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('svgContainer', { static: false }) svgContainer?: ElementRef<HTMLDivElement>;

  svgContent: SafeHtml | null = null;
  isLoading = true;

  steps: Uc02Step[] = [];
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
  protected readonly viewModeConceptLabel = $localize`:@@uc02ViewConcept:Concept (Sources → DSP → Targets)`;
  protected readonly viewModeLanesLabel = $localize`:@@uc02ViewLanes:Architecture Lanes (Analytics | DSP | Data)`;

  viewMode: Uc02ViewMode = 'concept';

  constructor(
    private readonly sanitizer: DomSanitizer,
    private readonly cdr: ChangeDetectorRef,
    private readonly elementRef: ElementRef<HTMLElement>,
    private readonly svgGenerator: Uc02SvgGeneratorService,
    private readonly svgGeneratorLanes: Uc02SvgGeneratorLanesService,
    private readonly i18nService: Uc02I18nService,
    private readonly http: HttpClient,
    private readonly languageService: LanguageService
  ) {}

  async ngOnInit(): Promise<void> {
    await Promise.all([this.loadSteps(), this.loadSvg()]);
  }

  ngAfterViewInit(): void {
    if (!this.isLoading && this.svgContent) {
      requestAnimationFrame(() => this.applyStep(this.currentStepIndex));
    }
  }

  ngOnDestroy(): void {
    this.stopAutoPlay();
  }

  private async loadSteps(): Promise<void> {
    try {
      const stepsUrl = `assets/use-cases/uc-02/uc-02-three-data-pools.steps.json`;
      const stepsData = await this.http.get<Uc02Step[]>(stepsUrl).toPromise();
      if (stepsData) {
        this.steps = stepsData;
        this.cdr.markForCheck();
      }
    } catch (error) {
      console.error('Failed to load UC-02 steps:', error);
    }
  }

  private async loadSvg(): Promise<void> {
    try {
      const i18nTexts = await this.i18nService.loadTexts();
      const generator = this.viewMode === 'lanes' ? this.svgGeneratorLanes : this.svgGenerator;
      const svgString = generator.generateSvg(i18nTexts);
      if (svgString) {
        this.svgContent = this.sanitizer.bypassSecurityTrustHtml(svgString);
        this.isLoading = false;
        this.cdr.markForCheck();
        this.cdr.detectChanges();
        // Defer applyStep so Angular can render the new SVG (especially after view-mode switch)
        setTimeout(() => this.applyStep(this.currentStepIndex), 80);
      }
    } catch (error) {
      console.error('Failed to generate UC-02 SVG:', error);
      this.isLoading = false;
      this.cdr.markForCheck();
    }
  }

  protected setViewMode(mode: Uc02ViewMode): void {
    if (this.viewMode === mode) return;
    this.viewMode = mode;
    this.isLoading = true;
    this.cdr.markForCheck();
    this.loadSvg();
  }

  protected prevStep(): void {
    if (this.currentStepIndex > 0) {
      this.applyStep(this.currentStepIndex - 1);
    }
  }

  protected nextStep(): void {
    if (this.currentStepIndex < this.steps.length - 1) {
      this.applyStep(this.currentStepIndex + 1);
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

    const runApply = (): void => {
      const svgElement =
        this.svgContainer?.nativeElement?.querySelector('svg') ??
        this.elementRef.nativeElement?.querySelector('.three-data-pools-use-case__svg-wrapper svg');
      if (!svgElement) return;

      const titleEl = svgElement.querySelector('#uc02_title');
      const subtitle = svgElement.querySelector('#uc02_subtitle');
      const stepDesc = svgElement.querySelector('#uc02_step_description');

      if (index === 0) {
        svgElement.querySelectorAll('[id^="uc02_"]').forEach((el) => {
          el.classList.remove('hl', 'dim', 'hidden');
        });
        if (titleEl) (titleEl as HTMLElement).style.display = '';
        if (subtitle) (subtitle as HTMLElement).style.display = '';
        if (stepDesc) (stepDesc as HTMLElement).style.display = 'none';
      } else {
        if (this.showDescription) {
          if (titleEl) (titleEl as HTMLElement).style.display = 'none';
          if (subtitle) (subtitle as HTMLElement).style.display = 'none';
          if (stepDesc) {
            (stepDesc as HTMLElement).style.display = '';
            const titleEl = svgElement.querySelector('#uc02_step_description_title');
            const textEl = svgElement.querySelector('#uc02_step_description_text');
            if (titleEl && textEl) {
              titleEl.textContent = this.getCurrentStepTitle();
              textEl.textContent = this.getCurrentStepDescription();
            }
          }
        } else {
          if (titleEl) (titleEl as HTMLElement).style.display = '';
          if (subtitle) (subtitle as HTMLElement).style.display = 'none';
          if (stepDesc) (stepDesc as HTMLElement).style.display = 'none';
        }
        svgElement.querySelectorAll('[id^="uc02_"]').forEach((el) => {
          el.classList.remove('hl', 'dim', 'hidden');
        });
        step.highlightIds.forEach((id) => {
          const el = svgElement.querySelector(`#${id}`);
          if (el) el.classList.add('hl');
        });
        step.dimIds.forEach((id) => {
          const el = svgElement.querySelector(`#${id}`);
          if (el) el.classList.add('dim');
        });
        step.hideIds.forEach((id) => {
          const el = svgElement.querySelector(`#${id}`);
          if (el) el.classList.add('hidden');
        });
      }
    };

    setTimeout(runApply, 0);
    this.cdr.markForCheck();
  }

  protected getCurrentStepTitle(): string {
    return this.getStepTitle(this.steps[this.currentStepIndex]);
  }

  protected getStepTitle(step: Uc02Step | undefined): string {
    if (!step) return '';
    const locale = this.languageService.current;
    if (locale === 'fr' && step.title.fr) return step.title.fr;
    if (locale === 'de' && step.title.de) return step.title.de;
    return step.title.en;
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
