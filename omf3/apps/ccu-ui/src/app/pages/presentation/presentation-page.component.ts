import { ChangeDetectionStrategy, Component } from '@angular/core';
import { FtsTabComponent } from '../../tabs/fts-tab.component';

@Component({
  standalone: true,
  selector: 'app-presentation-page',
  imports: [FtsTabComponent],
  template: `
    <app-fts-tab [presentationMode]="true"></app-fts-tab>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PresentationPageComponent {}

