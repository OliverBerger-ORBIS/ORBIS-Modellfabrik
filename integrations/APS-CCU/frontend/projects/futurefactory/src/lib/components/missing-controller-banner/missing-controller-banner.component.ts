import { ChangeDetectionStrategy, Component } from '@angular/core';
import { MissingControllerBannerState } from './missing-controller-banner.state';

@Component({
  selector: 'ff-missing-controller-banner',
  templateUrl: './missing-controller-banner.component.html',
  styleUrls: ['./missing-controller-banner.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [MissingControllerBannerState],
})
export class MissingControllerBannerComponent {
  constructor(public state: MissingControllerBannerState) {}
}
