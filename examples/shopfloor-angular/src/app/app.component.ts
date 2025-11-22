import { Component } from '@angular/core';
import { ShopfloorComponent } from './shopfloor/shopfloor.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ShopfloorComponent],
  template: '<app-shopfloor></app-shopfloor>',
  styles: []
})
export class AppComponent {
  title = 'shopfloor-angular-example';
}
