/**
 * Demo page for the refactored DSP Architecture component.
 * 
 * Showcases the component with view switcher and event handling.
 */

import { CommonModule } from '@angular/common';
import { Component, ChangeDetectionStrategy } from '@angular/core';
import { DspArchitectureRefactorComponent } from '../../components/dsp-architecture-refactor/dsp-architecture-refactor.component';
import type { ViewMode, BoxClickEvent, StepChangeEvent } from '../../components/dsp-architecture-refactor/types';

@Component({
  selector: 'app-refactor-demo-page',
  standalone: true,
  imports: [CommonModule, DspArchitectureRefactorComponent],
  templateUrl: './refactor-demo-page.component.html',
  styleUrls: ['./refactor-demo-page.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RefactorDemoPageComponent {
  protected currentView: ViewMode = 'functional';
  protected animationEnabled = true;

  // i18n labels
  protected readonly pageTitle = $localize`:@@refactorDemoTitle:DSP Architecture - Refactored Component Demo`;
  protected readonly pageDescription = $localize`:@@refactorDemoDesc:Interactive demonstration of the refactored DSP architecture visualization with multiple views and animations.`;
  protected readonly labelViewMode = $localize`:@@refactorViewMode:View Mode:`;
  protected readonly labelFunctional = $localize`:@@refactorViewFunctional:Functional`;
  protected readonly labelComponent = $localize`:@@refactorViewComponent:Component`;
  protected readonly labelDeployment = $localize`:@@refactorViewDeployment:Deployment`;
  protected readonly labelAnimations = $localize`:@@refactorAnimations:Enable Animations`;
  protected readonly labelEventLog = $localize`:@@refactorEventLog:Event Log`;

  // Event log
  protected eventLog: string[] = [];
  protected readonly maxLogEntries = 10;

  /**
   * Handle view change
   */
  protected onViewChange(view: ViewMode): void {
    this.currentView = view;
    this.addLogEntry(`View changed to: ${view}`);
  }

  /**
   * Handle box click event
   */
  protected onBoxClick(event: BoxClickEvent): void {
    this.addLogEntry(`Box clicked: ${event.label} (${event.boxId}) in layer ${event.layer}`);
  }

  /**
   * Handle step change event
   */
  protected onStepChange(event: StepChangeEvent): void {
    this.addLogEntry(
      `Animation step: ${event.stepIndex + 1}/${event.totalSteps} - ${event.stepId} (scene: ${event.sceneId})`
    );
  }

  /**
   * Toggle animations
   */
  protected toggleAnimations(): void {
    this.animationEnabled = !this.animationEnabled;
    this.addLogEntry(`Animations ${this.animationEnabled ? 'enabled' : 'disabled'}`);
  }

  /**
   * Add entry to event log
   */
  private addLogEntry(message: string): void {
    const timestamp = new Date().toLocaleTimeString();
    this.eventLog.unshift(`[${timestamp}] ${message}`);
    
    // Keep only the last N entries
    if (this.eventLog.length > this.maxLogEntries) {
      this.eventLog = this.eventLog.slice(0, this.maxLogEntries);
    }
  }

  /**
   * Clear event log
   */
  protected clearLog(): void {
    this.eventLog = [];
  }
}
