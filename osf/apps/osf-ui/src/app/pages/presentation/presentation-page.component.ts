import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AgvTabComponent } from '../../tabs/agv-tab.component';
import { BackButtonComponent } from '../../components/back-button/back-button.component';

@Component({
  standalone: true,
  selector: 'app-presentation-page',
  imports: [CommonModule, BackButtonComponent, AgvTabComponent],
  template: `
    <div class="presentation-page">
      <div class="presentation-page__back">
        <app-back-button fallbackPath="dsp" />
      </div>
      <app-agv-tab [presentationMode]="true"></app-agv-tab>
    </div>
  `,
  styles: [
    `
      .presentation-page {
        position: relative;
      }

      .presentation-page__back {
        position: absolute;
        z-index: 10;
        top: 16px;
        left: 16px;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PresentationPageComponent {}

