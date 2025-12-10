/**
 * Demo page for the refactored DSP Architecture component.
 * 
 * Showcases the component with multi-view mode switcher (Functional, Component, Deployment).
 */

import { CommonModule } from '@angular/common';
import { Component, ChangeDetectionStrategy } from '@angular/core';
import { DspArchitectureRefactorComponent } from '../../components/dsp-architecture-refactor/dsp-architecture-refactor.component';
import type { ViewMode } from '../../components/dsp-architecture-refactor/types';

@Component({
  selector: 'app-refactor-demo-page',
  standalone: true,
  imports: [CommonModule, DspArchitectureRefactorComponent],
  templateUrl: './refactor-demo-page.component.html',
  styleUrls: ['./refactor-demo-page.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RefactorDemoPageComponent {
  // View mode state
  protected viewMode: ViewMode = 'functional';
  
  // i18n labels
  protected readonly pageTitle = $localize`:@@refactorDemoTitle:DSP Architecture - Refactored Component Demo`;
  protected readonly pageDescription = $localize`:@@refactorDemoDesc:Interactive demonstration of the refactored DSP architecture visualization with multiple views and animations.`;
  protected readonly labelViewMode = $localize`:@@refactorDemoViewMode:View Mode:`;
  protected readonly labelFunctional = $localize`:@@refactorDemoViewFunctional:Functional`;
  protected readonly labelComponent = $localize`:@@refactorDemoViewComponent:Component`;
  protected readonly labelDeployment = $localize`:@@refactorDemoViewDeployment:Deployment`;
  protected readonly labelEnableAnimations = $localize`:@@refactorDemoEnableAnim:Enable Animations`;

  /**
   * Select a view mode
   */
  protected selectViewMode(mode: ViewMode): void {
    this.viewMode = mode;
  }

  /**
   * Handle action triggered from architecture component
   */
  protected onActionTriggered(event: { id: string; url: string }): void {
    console.log('Action triggered:', event);
    // Could navigate or perform other actions here
  }
}
