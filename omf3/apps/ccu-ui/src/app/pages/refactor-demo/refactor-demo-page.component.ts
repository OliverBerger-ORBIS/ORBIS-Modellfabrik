/**
 * Demo page for the refactored DSP Architecture component.
 * 
 * Showcases the component with view switcher and event handling.
 */

import { CommonModule } from '@angular/common';
import { Component, ChangeDetectionStrategy } from '@angular/core';
import { DspArchitectureRefactorComponent } from '../../components/dsp-architecture-refactor/dsp-architecture-refactor.component';

@Component({
  selector: 'app-refactor-demo-page',
  standalone: true,
  imports: [CommonModule, DspArchitectureRefactorComponent],
  templateUrl: './refactor-demo-page.component.html',
  styleUrls: ['./refactor-demo-page.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RefactorDemoPageComponent {
  // i18n labels
  protected readonly pageTitle = $localize`:@@refactorDemoTitle:DSP Architecture - Refactored Component Demo`;
  protected readonly pageDescription = $localize`:@@refactorDemoDesc:Demonstration of the refactored DSP architecture matching the existing reference architecture with animation steps 1, 2, 3, 7, 10, and final overview.`;

  /**
   * Handle action triggered from architecture component
   */
  protected onActionTriggered(event: { id: string; url: string }): void {
    console.log('Action triggered:', event);
    // Could navigate or perform other actions here
  }
}
