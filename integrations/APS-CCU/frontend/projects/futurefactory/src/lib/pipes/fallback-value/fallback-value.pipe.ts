import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'fallback',
})
export class FallbackValuePipe implements PipeTransform {
  transform(value: any, fallback?: any): any {
    return value ?? fallback ?? undefined;
  }
}
