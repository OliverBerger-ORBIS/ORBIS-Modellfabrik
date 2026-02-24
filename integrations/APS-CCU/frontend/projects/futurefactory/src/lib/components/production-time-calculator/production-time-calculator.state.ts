import { Injectable } from '@angular/core';
import {
  Observable,
  OperatorFunction,
  ReplaySubject,
  combineLatest,
  pipe,
} from 'rxjs';
import { filter, map, startWith } from 'rxjs/operators';
import { OrderResponse } from '../../../common/protocol';

@Injectable()
export class ProductionTimeCalculatorState {
  private readonly selectedOrder = new ReplaySubject<OrderResponse | undefined>(
    1
  );

  readonly startTime$: Observable<Date | undefined>;
  readonly endTime$: Observable<Date | undefined>;
  readonly duration$: Observable<number | undefined>;
  readonly calculatedProductionTime$: Observable<number | undefined>;
  readonly calculatedTransportTime$: Observable<number | undefined>;

  constructor() {
    this.startTime$ = this.setupStartTime(this.selectedOrder.asObservable());
    this.endTime$ = this.setupEndTime(this.selectedOrder.asObservable());
    this.duration$ = this.setupDuration(this.startTime$, this.endTime$);
    this.calculatedProductionTime$ = this.setupCalculatedProductionTime(
      this.selectedOrder.asObservable()
    );
    this.calculatedTransportTime$ = this.setupCalculatedTransportTime(
      this.selectedOrder.asObservable()
    );
  }

  public setSelectedOrder(order: OrderResponse | undefined) {
    this.selectedOrder.next(order);
  }

  private setupStartTime(
    order$: Observable<OrderResponse | undefined>
  ): Observable<Date | undefined> {
    return order$.pipe(
      filter((order) => !!order),
      map((order) => order?.startedAt),
      startWith<Date | undefined>(undefined)
    );
  }

  private setupEndTime(
    order$: Observable<OrderResponse | undefined>
  ): Observable<Date | undefined> {
    return order$.pipe(
      filter((order) => !!order),
      map((order) => order?.stoppedAt),
      startWith<Date | undefined>(undefined)
    );
  }

  private setupDuration(
    startTime$: Observable<Date | undefined>,
    endTime$: Observable<Date | undefined>
  ): Observable<number | undefined> {
    return combineLatest([startTime$, endTime$]).pipe(
      map(([startTime, endTime]) => {
        if (startTime && endTime) {
          return endTime.getTime() - startTime.getTime();
        }
        return undefined;
      }),
      startWith<number | undefined>(undefined)
    );
  }

  private aggregateStepDuration(
    requiredType: 'MANUFACTURE' | 'NAVIGATION'
  ): OperatorFunction<OrderResponse | undefined, number | undefined> {
    return pipe(
      filter((order) => !!order),
      map((order) => order?.productionSteps ?? []),
      map((steps) => steps.filter((step) => step.type === requiredType)),
      map((steps) =>
        steps.reduce((acc, step) => {
          if (step.startedAt && step.stoppedAt) {
            return acc + (step.stoppedAt.getTime() - step.startedAt.getTime());
          }
          return acc;
        }, 0)
      ),
      map((duration) => (duration > 0 ? duration : undefined))
    );
  }

  private setupCalculatedProductionTime(
    order$: Observable<OrderResponse | undefined>
  ): Observable<number | undefined> {
    return order$.pipe(this.aggregateStepDuration('MANUFACTURE'));
  }

  private setupCalculatedTransportTime(
    order$: Observable<OrderResponse | undefined>
  ): Observable<number | undefined> {
    return order$.pipe(this.aggregateStepDuration('NAVIGATION'));
  }
}
