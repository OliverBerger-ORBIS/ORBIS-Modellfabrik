import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, ChangeDetectorRef, Component } from '@angular/core';
import { DspOverviewSectionComponent } from './components/dsp-overview-section/dsp-overview-section.component';
import { DspArchitectureFunctionalSectionComponent } from './components/dsp-architecture-functional-section/dsp-architecture-functional-section.component';
import { DspArchitectureComponentSectionComponent } from './components/dsp-architecture-component-section/dsp-architecture-component-section.component';
import { DspArchitectureDeploymentSectionComponent } from './components/dsp-architecture-deployment-section/dsp-architecture-deployment-section.component';
import { DspUseCasesSectionComponent } from './components/dsp-use-cases-section/dsp-use-cases-section.component';
import { DspMethodologySectionComponent } from './components/dsp-methodology-section/dsp-methodology-section.component';

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
  readonly pageSubtitle = $localize`:@@dspPageSubtitle:Edge-to-Cloud Orchestration for Smart Manufacturing`;
  
  // Accordion state - track which sections are expanded
  protected expandedSections = new Set<string>();
  private readonly storageKey = 'dsp-page-accordion-expanded-sections';
  
  constructor(private readonly cdr: ChangeDetectorRef) {
    // Load saved accordion state from localStorage
    this.loadAccordionState();
    
    // If no saved state, expand overview section by default
    if (this.expandedSections.size === 0) {
      this.expandedSections.add('overview');
    }
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
}
