import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { distinctUntilChanged, map } from 'rxjs';
import { DspOverviewSectionComponent } from './components/dsp-overview-section/dsp-overview-section.component';
import { DspArchitectureFunctionalSectionComponent } from './components/dsp-architecture-functional-section/dsp-architecture-functional-section.component';
import { DspArchitectureComponentSectionComponent } from './components/dsp-architecture-component-section/dsp-architecture-component-section.component';
import { DspArchitectureDeploymentSectionComponent } from './components/dsp-architecture-deployment-section/dsp-architecture-deployment-section.component';
import { DspUseCasesSectionComponent } from './components/dsp-use-cases-section/dsp-use-cases-section.component';
import { DspMethodologySectionComponent } from './components/dsp-methodology-section/dsp-methodology-section.component';
import {
  DSP_RETURN_SECTION_SESSION_KEY,
  isDspAccordionSectionId,
} from './dsp-accordion-sections';

/**
 * Main DSP (Distributed Shopfloor Processing) page component.
 * 
 * This page provides a comprehensive view of DSP including:
 * - Overview: What is DSP?
 * - Architecture (Functional view): Interactive architecture animation
 * - Components: Component view showing internal DSP Edge components
 * - Deployment: Deployment pipeline view (integration → transformation → consolidation → provisioning)
 * - Use cases (Data Aggregation, Track & Trace, Predictive Maintenance, Process Optimization)
 * - Methodology (Phases 1-5 with Autonomous & Adaptive Enterprise)
 */
@Component({
  standalone: true,
  selector: 'app-dsp-page',
  imports: [
    CommonModule,
    DspOverviewSectionComponent,
    DspArchitectureFunctionalSectionComponent,
    DspArchitectureComponentSectionComponent,
    DspArchitectureDeploymentSectionComponent,
    DspUseCasesSectionComponent,
    DspMethodologySectionComponent,
  ],
  templateUrl: './dsp-page.component.html',
  styleUrl: './dsp-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DspPageComponent {
  readonly pageTitle = $localize`:@@dspPageTitle:Distributed Shopfloor Processing`;
  readonly pageSubtitle = $localize`:@@dspPageSubtitle:Edge-to-cloud orchestration with ORBIS MES, DSP, and smart manufacturing`;

  private readonly cdr = inject(ChangeDetectorRef);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  // Accordion state - track which sections are expanded
  protected expandedSections = new Set<string>();
  private readonly storageKey = 'dsp-page-accordion-expanded-sections';

  constructor() {
    this.loadAccordionState();

    if (this.expandedSections.size === 0) {
      this.expandedSections.add('overview');
    }

    this.applyStoredReturnSectionFromSession();

    this.route.queryParamMap
      .pipe(
        map((m) => m.get('section')),
        distinctUntilChanged(),
        takeUntilDestroyed(),
      )
      .subscribe((section) => {
        if (!section || !isDspAccordionSectionId(section)) {
          return;
        }
        this.expandedSections.add(section);
        this.saveAccordionState();
        this.cdr.markForCheck();
        this.stripSectionQueryParam();
        this.scheduleScrollToAccordionSection(section);
      });
  }
  
  /**
   * Check if a section is expanded
   */
  protected isSectionExpanded(sectionId: string): boolean {
    return this.expandedSections.has(sectionId);
  }
  
  /**
   * Toggle section expansion
   */
  protected toggleSection(sectionId: string): void {
    if (this.expandedSections.has(sectionId)) {
      this.expandedSections.delete(sectionId);
    } else {
      this.expandedSections.add(sectionId);
    }
    this.saveAccordionState();
    this.cdr.markForCheck();
  }
  
  /**
   * Load accordion state from localStorage
   */
  private loadAccordionState(): void {
    try {
      const saved = localStorage.getItem(this.storageKey);
      if (saved) {
        const sections = JSON.parse(saved) as string[];
        this.expandedSections = new Set(sections);
      }
    } catch (error) {
      // Ignore localStorage errors (e.g., in private browsing mode)
      console.warn('[DspPage] Failed to load accordion state:', error);
    }
  }
  
  /**
   * Save accordion state to localStorage
   */
  private saveAccordionState(): void {
    try {
      const sections = Array.from(this.expandedSections);
      localStorage.setItem(this.storageKey, JSON.stringify(sections));
    } catch (error) {
      // Ignore localStorage errors (e.g., in private browsing mode)
      console.warn('[DspPage] Failed to save accordion state:', error);
    }
  }

  /**
   * Browser Back from a use-case detail does not run NavigationBackService; sessionStorage
   * may still hold the accordion section recorded when opening the detail from embedded tiles.
   */
  private applyStoredReturnSectionFromSession(): void {
    try {
      if (typeof sessionStorage === 'undefined') {
        return;
      }
      const raw = sessionStorage.getItem(DSP_RETURN_SECTION_SESSION_KEY);
      if (!raw || !isDspAccordionSectionId(raw)) {
        return;
      }
      sessionStorage.removeItem(DSP_RETURN_SECTION_SESSION_KEY);
      this.expandedSections.add(raw);
      this.saveAccordionState();
      this.cdr.markForCheck();
      this.scheduleScrollToAccordionSection(raw);
    } catch {
      // ignore
    }
  }

  private stripSectionQueryParam(): void {
    try {
      void this.router.navigate([], {
        relativeTo: this.route,
        replaceUrl: true,
        queryParams: { section: null },
        queryParamsHandling: 'merge',
      });
    } catch (error) {
      console.warn('[DspPage] Failed to strip section query param:', error);
    }
  }

  private scheduleScrollToAccordionSection(sectionId: string): void {
    if (!isDspAccordionSectionId(sectionId)) {
      return;
    }
    setTimeout(() => {
      document.getElementById(`dsp-accordion-${sectionId}`)?.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }, 120);
  }
}
