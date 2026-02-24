import { Pipe, PipeTransform } from '@angular/core';
import {
  CalibrationData,
  calibrationData,
} from '../../../common/data/calibration';
import { ModuleType } from '../../../common/protocol/module';
import { ReferenceValue } from '../../../common/protocol/vda';

@Pipe({
  name: 'filterRef',
})
export class FilterRefPipe implements PipeTransform {
  private calibrationData: CalibrationData = calibrationData;

  transform(
    value: Array<ReferenceValue>,
    positionName: string,
    moduleType: ModuleType
  ): Array<ReferenceValue> {
    if (!positionName || !moduleType) {
      return [];
    }
    const positionCalibrationValues =
      this.calibrationData[moduleType][positionName] ?? [];
    return (value ?? []).filter((ref) =>
      positionCalibrationValues.includes(ref.referenceKey)
    );
  }
}
