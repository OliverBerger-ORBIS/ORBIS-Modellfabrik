import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'toNumberFormat',
})
export class ToNumberFormatPipe implements PipeTransform {
  private readonly numberFormatter = new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 2,
  });

  transform(value: any) {
    if (Number.isSafeInteger(value)) {
      return this.numberFormatter.format(value);
    }
    return value;
  }
}
