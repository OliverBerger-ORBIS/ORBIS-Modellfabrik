import { Component, ChangeDetectionStrategy, OnInit, OnDestroy, ChangeDetectorRef, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { HttpClient } from '@angular/common/http';
import { Uc01SvgGeneratorService } from './uc-01-svg-generator.service';
import { Uc01I18nService } from './uc-01-i18n.service';
import { LanguageService } from '../../../services/language.service';

interface Uc01Step {
  id: string;
  title: { de: string; en: string; fr?: string };
  description?: { de: string; en: string; fr?: string };
  highlightIds: string[];
  dimIds: string[];
  showIds: string[];
  hideIds: string[];
}

/**
 * Track & Trace Genealogy Use Case Component
 * Displays the Track & Trace Genealogy diagram with step animation
 * Uses dynamic SVG generation with I18n support (DE/EN/FR)
 */
@Component({
  selector: 'app-track-trace-genealogy-use-case',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './track-trace-genealogy-use-case.component.html',
  styleUrls: ['./track-trace-genealogy-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TrackTraceGenealogyUseCaseComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('svgContainer', { static: false }) svgContainer?: ElementRef<HTMLDivElement>;
  
  svgContent: SafeHtml | null = null;
  isLoading = true;
  
  // Animation state
  steps: Uc01Step[] = [];
  currentStepIndex = 0;
  isAutoPlaying = false;
  loopToStart = true;
  showDescription = false;
  private autoPlayInterval: ReturnType<typeof setInterval> | null = null;
  
  // Zoom state
  zoom = 1;
  protected readonly minZoom = 0.4;
  protected readonly maxZoom = 1.8;
  private readonly ZOOM_STEP_FINE = 0.05;
  private readonly ZOOM_STEP_COARSE = 0.1;
  
  // I18n labels for controls
  protected readonly btnPrev = $localize`:@@dspArchPrev:Previous`;
  protected readonly btnNext = $localize`:@@dspArchNext:Next`;
  protected readonly btnAutoPlay = $localize`:@@dspArchAutoPlay:Auto Play`;
  protected readonly btnStopPlay = $localize`:@@dspArchStopPlay:Stop`;
  protected readonly zoomOutLabel = $localize`:@@shopfloorPreviewZoomOut:Zoom out`;
  protected readonly zoomInLabel = $localize`:@@shopfloorPreviewZoomIn:Zoom in`;
  protected readonly resetZoomLabel = $localize`:@@shopfloorPreviewResetZoom:Reset zoom`;

  constructor(
    private readonly sanitizer: DomSanitizer,
    private readonly cdr: ChangeDetectorRef,
    private readonly svgGenerator: Uc01SvgGeneratorService,
    private readonly i18nService: Uc01I18nService,
    private readonly http: HttpClient,
    private readonly languageService: LanguageService
  ) {}

  async ngOnInit(): Promise<void> {
    await Promise.all([this.loadSteps(), this.loadSvg()]);
  }

  ngAfterViewInit(): void {
    setTimeout(() => this.applyStep(0), 0);
  }

  ngOnDestroy(): void {
    this.stopAutoPlay();
  }

  private async loadSteps(): Promise<void> {
    try {
      const stepsUrl = `assets/use-cases/uc-01/uc-01-track-trace-genealogy.steps.json`;
      const stepsData = await this.http.get<Uc01Step[]>(stepsUrl).toPromise();
      if (stepsData) {
        this.steps = stepsData;
        this.cdr.markForCheck();
      }
    } catch (error) {
      console.error('Failed to load steps:', error);
    }
  }

  private async loadSvg(): Promise<void> {
    try {
      this.isLoading = true;
      this.cdr.markForCheck();

      const i18nTexts = await this.i18nService.loadTexts();
      const svgString = this.svgGenerator.generateSvg(i18nTexts);

      if (svgString) {
        this.svgContent = this.sanitizer.bypassSecurityTrustHtml(svgString);
        this.isLoading = false;
        this.cdr.markForCheck();
      }
    } catch (error) {
      console.error('Failed to generate SVG:', error);
      this.isLoading = false;
      this.cdr.markForCheck();
    }
  }

  // Navigation methods
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
    if (!step) {
      return;
    }

    this.currentStepIndex = index;
    
    setTimeout(() => {
      const svgElement = this.svgContainer?.nativeElement?.querySelector('svg');
      if (!svgElement) {
        return;
      }

      const titleEl = svgElement.querySelector('#uc01_title');
      const subtitle = svgElement.querySelector('#uc01_subtitle');
      const stepDesc = svgElement.querySelector('#uc01_step_description');

      if (index === 0) {
        svgElement.querySelectorAll('[id^="uc01_"]').forEach((el) => {
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
            const stepTitleEl = svgElement.querySelector('#uc01_step_description_title');
            const stepTextEl = svgElement.querySelector('#uc01_step_description_text');
            if (stepTitleEl && stepTextEl) {
              stepTitleEl.textContent = this.getCurrentStepTitle();
              stepTextEl.textContent = this.getCurrentStepDescription();
            }
          }
        } else {
          if (titleEl) (titleEl as HTMLElement).style.display = '';
          if (subtitle) (subtitle as HTMLElement).style.display = 'none';
          if (stepDesc) (stepDesc as HTMLElement).style.display = 'none';
        }
        
        // Reset all elements
        svgElement.querySelectorAll('[id^="uc01_"]').forEach((el) => {
          el.classList.remove('hl', 'dim', 'hidden');
        });

        // Apply highlight class
        step.highlightIds.forEach((id) => {
          const element = svgElement.querySelector(`#${id}`);
          if (element) {
            element.classList.add('hl');
          }
        });

        // Apply dim class
        step.dimIds.forEach((id) => {
          const element = svgElement.querySelector(`#${id}`);
          if (element) {
            element.classList.add('dim');
          }
        });

        // Apply hidden class
        step.hideIds.forEach((id) => {
          const element = svgElement.querySelector(`#${id}`);
          if (element) {
            element.classList.add('hidden');
          }
        });
      }
    }, 0);

    this.cdr.markForCheck();
  }

  protected getCurrentStepTitle(): string {
    const step = this.steps[this.currentStepIndex];
    if (!step) {
      return '';
    }
    const locale = this.languageService.current;
    if (locale === 'fr' && step.title.fr) {
      return step.title.fr;
    }
    if (locale === 'de' && step.title.de) {
      return step.title.de;
    }
    return step.title.en;
  }

  protected getCurrentStepDescription(): string {
    const step = this.steps[this.currentStepIndex];
    if (!step || !step.description) {
      return '';
    }
    const locale = this.languageService.current;
    if (locale === 'fr' && step.description.fr) {
      return step.description.fr;
    }
    if (locale === 'de' && step.description.de) {
      return step.description.de;
    }
    return step.description.en;
  }

  // Zoom methods
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
