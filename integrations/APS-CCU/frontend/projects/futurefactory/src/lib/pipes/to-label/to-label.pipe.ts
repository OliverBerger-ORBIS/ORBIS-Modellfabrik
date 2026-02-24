import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
  name: 'toLabel'
})
export class ToLabelPipe implements PipeTransform {
  transform(value: string, labelSet: Record<string, string> = {}) {
    if (value in labelSet) {
      return labelSet[value];
    }
    return value;
  }
}
