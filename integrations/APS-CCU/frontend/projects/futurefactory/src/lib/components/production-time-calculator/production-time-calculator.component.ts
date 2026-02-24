import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { OrderResponse } from '../../../common/protocol';
import { ProductionTimeCalculatorState } from './production-time-calculator.state';

@Component({
  selector: 'ff-production-time-calculator',
  templateUrl: './production-time-calculator.component.html',
  styleUrls: ['./production-time-calculator.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [ProductionTimeCalculatorState],
})
export class ProductionTimeCalculatorComponent {
  @Input() set order(order: OrderResponse | undefined) {
    this.state.setSelectedOrder(order);
  }

  constructor(public readonly state: ProductionTimeCalculatorState) {}
}
