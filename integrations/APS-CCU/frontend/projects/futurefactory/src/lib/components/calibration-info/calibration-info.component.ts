import { Component, Input } from '@angular/core';
import { ReferenceValue } from '../../../common/protocol/vda';

@Component({
  selector: 'ff-calibration-info',
  templateUrl: './calibration-info.component.html',
  styleUrls: ['./calibration-info.component.scss'],
})
export class CalibrationInfoComponent {
  @Input() imageData: Array<ReferenceValue> = [];
  @Input() statusValues: Array<ReferenceValue> = [];
}
