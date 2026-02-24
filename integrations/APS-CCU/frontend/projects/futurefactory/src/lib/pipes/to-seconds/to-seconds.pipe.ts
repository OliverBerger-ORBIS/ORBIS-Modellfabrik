import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'toSeconds',
})
export class ToSecondsPipe implements PipeTransform {
  private readonly numberFormatter = new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 2,
  });

  transform(value: any) {
    if (Number.isSafeInteger(value)) {
      return `${this.numberFormatter.format(value / 1000)}s`;
    }
    return value;
  }
}
