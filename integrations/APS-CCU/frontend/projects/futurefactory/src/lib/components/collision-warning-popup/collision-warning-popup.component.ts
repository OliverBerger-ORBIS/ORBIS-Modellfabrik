import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FtsState } from '../../../common/protocol/fts';


@Component({
  selector: 'ff-collision-warning-popup',
  templateUrl: './collision-warning-popup.component.html',
  styleUrls: ['./colission-warning-popup.component.scss']
})
export class CollisionWarningPopupComponent {

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: { collisions: Array<FtsState> },
  ) {}

}
