import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ModuleType } from '../../../common/protocol/module';

@Component({
  selector: 'ff-calibration-caption',
  templateUrl: './calibration-caption.component.html',
  styleUrls: ['./calibration-caption.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CalibrationCaptionComponent {
  readonly ModuleType = ModuleType;
  @Input() moduleType: ModuleType | null = null;
}
