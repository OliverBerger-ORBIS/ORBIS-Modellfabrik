import { ChangeDetectionStrategy, Component } from "@angular/core";

@Component({
  selector: 'ff-banner',
  templateUrl: './banner.component.html',
  styleUrls: ['./banner.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BannerComponent {}
