import { Component, ChangeDetectionStrategy, OnInit, OnDestroy, ChangeDetectorRef, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { HttpClient } from '@angular/common/http';
import { Uc06SvgGeneratorService } from './uc-06-svg-generator.service';
import { Uc06I18nService } from './uc-06-i18n.service';
import { LanguageService } from '../../../services/language.service';

interface Uc06Step {
  id: string;
  title: { de: string; en: string; fr?: string };
  description?: { de: string; en: string; fr?: string };
  highlightIds: string[];
  dimIds: string[];
  showIds: string[];
  hideIds: string[];
}

/**
 * Interoperability Use Case Component
 * Displays the Event-to-Process Map for the Interoperability use case
 * Uses dynamic SVG generation with I18n support (DE/EN/FR) and step animation
 */
@Component({
  selector: 'app-interoperability-use-case',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './interoperability-use-case.component.html',
  styleUrls: ['./interoperability-use-case.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InteroperabilityUseCaseComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('svgContainer', { static: false }) svgContainer?: ElementRef<HTMLDivElement>;
  
  svgContent: SafeHtml | null = null;
  isLoading = true;
  
  // Animation state
  steps: Uc06Step[] = [];
  currentStepIndex = 0;
  isAutoPlaying = false;
  loopToStart = true;
  private autoPlayInterval: ReturnType<typeof setInterval> | null = null;
  
  // Zoom state
  zoom = 1;
  protected readonly minZoom = 0.4;
  protected readonly maxZoom = 1.8;
  private readonly ZOOM_STEP_FINE = 0.05;
  private readonly ZOOM_STEP_COARSE = 0.1;
  
  // i18n labels
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
    private readonly svgGenerator: Uc06SvgGeneratorService,
    private readonly i18nService: Uc06I18nService,
    private readonly http: HttpClient,
    private readonly languageService: LanguageService
  ) {}

  async ngOnInit(): Promise<void> {
    await Promise.all([this.loadSteps(), this.loadSvg()]);
  }

  ngAfterViewInit(): void {
    // Apply initial step after view is initialized
    setTimeout(() => this.applyStep(0), 0);
  }

  ngOnDestroy(): void {
    this.stopAutoPlay();
  }

  private async loadSteps(): Promise<void> {
    try {
      const locale = this.languageService.current;
      const stepsUrl = `assets/use-cases/uc-06/uc-06-event-to-process-map.steps.json`;
      const stepsData = await this.http.get<Uc06Step[]>(stepsUrl).toPromise();
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
      // Load I18n texts
      const i18nTexts = await this.i18nService.loadTexts();
      
      // Generate SVG dynamically
      const svgString = this.svgGenerator.generateSvg(i18nTexts);
      
      if (svgString) {
        // Sanitize and set SVG content for inline rendering
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
    
    // Apply CSS classes to SVG elements
    setTimeout(() => {
      const svgElement = this.svgContainer?.nativeElement?.querySelector('svg');
      if (!svgElement) {
        return;
      }

      // Step 0 (Overview): No highlighting, show everything, show subtitle, hide step description
      if (index === 0) {
        // Reset all elements - no highlighting
        svgElement.querySelectorAll('[id^="uc06_"]').forEach((el) => {
          el.classList.remove('hl', 'dim', 'hidden');
        });
        // Show subtitle, hide step description
        const subtitle = svgElement.querySelector('#uc06_subtitle');
        if (subtitle) {
          (subtitle as HTMLElement).style.display = '';
        }
        const stepDesc = svgElement.querySelector('#uc06_step_description');
        if (stepDesc) {
          (stepDesc as HTMLElement).style.display = 'none';
        }
      } else {
        // Hide subtitle, show step description
        const subtitle = svgElement.querySelector('#uc06_subtitle');
        if (subtitle) {
          (subtitle as HTMLElement).style.display = 'none';
        }
        const stepDesc = svgElement.querySelector('#uc06_step_description');
        if (stepDesc) {
          (stepDesc as HTMLElement).style.display = '';
          // Update step description text
          const stepTitleEl = svgElement.querySelector('#uc06_step_description_title');
          const stepTextEl = svgElement.querySelector('#uc06_step_description_text');
          if (stepTitleEl && stepTextEl) {
            stepTitleEl.textContent = this.getCurrentStepTitle();
            stepTextEl.textContent = this.getCurrentStepDescription();
          }
        }
        // Step 1+: Apply highlighting
        // Reset all elements
        svgElement.querySelectorAll('[id^="uc06_"]').forEach((el) => {
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
    // Handle locale with fallback: fr -> en, de -> en, en -> en
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
    // Handle locale with fallback: fr -> en, de -> en, en -> en
    if (locale === 'fr' && step.description.fr) {
      return step.description.fr;
    }
    if (locale === 'de' && step.description.de) {
      return step.description.de;
    }
    return step.description.en || '';
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
