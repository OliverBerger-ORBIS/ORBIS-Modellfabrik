import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component } from '@angular/core';
import { DspUseCasesComponent } from '../dsp/components/dsp-use-cases/dsp-use-cases.component';

/**
 * Use Case Selector Page Component
 * 
 * Reuses DspUseCasesComponent to display all use cases with navigation enabled.
 * This ensures consistency between DSP-Tab section and direct-access page.
 * 
 * Features:
 * - Single click: Highlight and show details
 * - Double click: Navigate to detail page (if implemented)
 * - "View Details" button: Navigate to detail page (if implemented)
 */
@Component({
  standalone: true,
  selector: 'app-use-case-selector-page',
  imports: [CommonModule, DspUseCasesComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="use-case-selector-page">
      <header class="use-case-selector-header">
        <h1 i18n="@@useCaseSelectorTitle">DSP Use Cases</h1>
        <p class="subtitle" i18n="@@useCaseSelectorSubtitle">
          Click on a use case to view details. Double-click or use "View Details" to navigate to the detailed implementation.
        </p>
      </header>

      <main class="use-case-selector-main">
        <app-dsp-use-cases [enableNavigation]="true"></app-dsp-use-cases>
      </main>
    </div>
  `,
  styles: [
    `
      .use-case-selector-page {
        min-height: 100vh;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
      }

      .use-case-selector-header {
        text-align: center;
        margin-bottom: 2rem;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
      }

      .use-case-selector-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 1rem;
      }

      .use-case-selector-header .subtitle {
        font-size: 1.125rem;
        color: #666;
        line-height: 1.6;
      }

      .use-case-selector-main {
        max-width: 1400px;
        margin: 0 auto;
      }
    `,
  ],
})
export class UseCaseSelectorPageComponent {}
