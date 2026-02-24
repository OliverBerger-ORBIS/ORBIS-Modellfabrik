import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
  name: 'toIcon'
})
export class ToIconPipe implements PipeTransform {
  transform(value: string, iconSet: Record<string, string> = {}) {
    if (value in iconSet) {
      return iconSet[value];
    }
    return value;
  }
}
