import { ChangeDetectionStrategy, Component } from '@angular/core';
import { AgvTabComponent } from '../../tabs/agv-tab.component';

@Component({
  standalone: true,
  selector: 'app-presentation-page',
  imports: [AgvTabComponent],
  template: `
    <app-agv-tab [presentationMode]="true"></app-agv-tab>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PresentationPageComponent {}

