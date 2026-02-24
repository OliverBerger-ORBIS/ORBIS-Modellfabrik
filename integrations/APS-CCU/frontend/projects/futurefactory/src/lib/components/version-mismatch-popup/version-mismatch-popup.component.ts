import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MismatchedModule, MismatchedVersionMessage } from '../../../common/protocol/ccu';

@Component({
  selector: 'ff-version-mismatch-popup',
  templateUrl: './version-mismatch-popup.component.html',
  styleUrls: ['./version-mismatch-popup.component.scss']
})
export class VersionMismatchPopupComponent {
  readonly displayedColumns: Array<keyof MismatchedModule | "description"> = ['serialNumber', 'moduleType', 'description', 'version', 'requiredVersion'];

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: { message: MismatchedVersionMessage },
  ) {}

}
