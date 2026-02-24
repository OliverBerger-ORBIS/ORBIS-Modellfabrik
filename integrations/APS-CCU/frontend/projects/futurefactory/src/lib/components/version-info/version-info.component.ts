import { Component } from '@angular/core';
import { VersionMismatchPopupService } from '../../services/version-mismatch-popup.service';

@Component({
  selector: 'ff-version-info',
  templateUrl: './version-info.component.html',
  styleUrls: ['./version-info.component.scss'],
  providers: [VersionMismatchPopupService],
})
export class VersionInfoComponent {
  readonly now: number;

  constructor(private mismatchPopup: VersionMismatchPopupService) {
    this.now = Date.now();
    mismatchPopup.init();
  }
}
