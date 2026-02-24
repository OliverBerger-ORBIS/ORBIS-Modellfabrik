import { Component, ElementRef, Input, OnDestroy, ViewChild, } from '@angular/core';
import { MatButtonToggle } from '@angular/material/button-toggle';
import { ActivatedRoute } from '@angular/router';
import {
  BehaviorSubject,
  combineLatestWith,
  distinctUntilChanged,
  filter,
  map,
  Observable,
  shareReplay,
  startWith,
  Subject,
  takeUntil,
} from 'rxjs';
import { CcuTopic } from '../../../common/protocol';
import {
  AvailableState,
  ModuleSettings,
  OrderManufactureStep,
  OrderResponse,
  OrderState,
  PairedModule,
  Workpiece,
} from '../../../common/protocol/ccu';
import {
  ModuleCommandType,
  ModuleState,
} from '../../../common/protocol/module';
import { TypedMqttService } from '../../futurefactory.service';
import { FactoryLayoutService } from '../../services/factory-layout.service';
import { OrderStatesService } from '../../services/order-states.service';
import { StatesService } from '../../services/states.service';
import { FutureFactoryRoutes } from '../../futurefactory.routes';
import { getRouteToModuleRoot } from '../../utils/routes.utils';

interface OrderStepInfo {
  command?: ModuleCommandType;
  orderId: string;
  workpiece?: Workpiece;
  workpieceId?: string;
  startedAt?: Date;
  eta?: Date;
}

@Component({
  selector: 'ff-module-details',
  templateUrl: './module-details.component.html',
  styleUrls: ['./module-details.component.scss'],
})
export class FutureFactoryModuleDetailsComponent implements OnDestroy {
  readonly ORDERS_ROUTE = FutureFactoryRoutes.ORDERS;

  @ViewChild('durationEditEnabled')
  durationEditToggle!: MatButtonToggle;
  @ViewChild('durationInput')
  durationInput!: ElementRef<HTMLInputElement>;

  readonly moduleId$ = new BehaviorSubject<string | undefined>(undefined);
  private destroyed$ = new Subject<void>();
  readonly routeToRoot$: Observable<string>;

  @Input() set moduleId(id: string | undefined) {
    this.moduleId$.next(id);
  }

  get moduleId(): string | undefined {
    return this.moduleId$.value;
  }

  readonly moduleData$: Observable<PairedModule | undefined>;

  readonly orderInfo$: Observable<OrderStepInfo | undefined>;
  readonly BLOCKED_STATE = AvailableState.BLOCKED;
  readonly CALIBRATION_ROUTE = FutureFactoryRoutes.CALIBRATION;

  /**
   * Find the latest step of the order currently executed on the module
   * @param order
   * @param serialNumber
   * @private
   */
  private findLatestOrderStepIndexForModule(
    order: OrderResponse,
    serialNumber: string
  ): number {
    for (let i = order.productionSteps.length - 1; i >= 0; i--) {
      const step = order.productionSteps[i];
      if (
        step.type === 'MANUFACTURE' &&
        step.serialNumber === serialNumber &&
        step.state !== OrderState.ENQUEUED &&
        step.startedAt
      ) {
        return i;
      }
    }
    return -1;
  }

  /**
   * Find the first step of the current sequence for the module containing the given step index
   * @param order
   * @param serialNumber
   * @param currentIndex
   * @private
   */
  private findStartOfCurrentModuleSteps(
    order: OrderResponse,
    serialNumber: string,
    currentIndex: number
  ): OrderManufactureStep | undefined {
    let firstStep: OrderManufactureStep | undefined;
    for (let i = currentIndex; i >= 0; i--) {
      const step = order.productionSteps[i];
      if (
        step.type === 'MANUFACTURE' &&
        step.serialNumber === serialNumber &&
        step.state !== OrderState.ENQUEUED &&
        step.startedAt
      ) {
        firstStep = step;
      } else {
        break;
      }
    }
    return firstStep;
  }

  /**
   * Checks if there are still incomplete steps for the current module
   * @param order
   * @param serialNumber
   * @param currentIndex
   * @private
   */
  private hasCurrentlyRemainingModuleSteps(
    order: OrderResponse,
    serialNumber: string,
    currentIndex: number
  ): boolean {
    let remaining = false;
    if (currentIndex < 0) {
      return false;
    }
    for (let i = currentIndex; i < order.productionSteps.length; i++) {
      const step = order.productionSteps[i];
      if (step.type !== 'MANUFACTURE' || step.serialNumber !== serialNumber) {
        break;
      } else if (
        step.state === OrderState.ENQUEUED ||
        step.state === OrderState.IN_PROGRESS
      ) {
        remaining = true;
        break;
      }
    }
    return remaining;
  }

  constructor(
    readonly factoryLayoutService: FactoryLayoutService,
    readonly statesService: StatesService,
    private orderStatesService: OrderStatesService,
    private mqttClient: TypedMqttService,
    private route: ActivatedRoute,
  ) {
    route.params.pipe(takeUntil(this.destroyed$)).subscribe((params) => {
      if (params['moduleId']) {
        this.moduleId = params['moduleId'];
      }
    });

    this.routeToRoot$ = getRouteToModuleRoot(route);

    this.moduleData$ = this.createModuleDataObservable();

    this.orderInfo$ = this.createOrderInfoObservable();
  }

  /**
   * Get the current order information for the current module
   * @private
   */
  private createOrderInfoObservable(): Observable<OrderStepInfo | undefined> {
    // Use module state to get order id
    const moduleState$ = this.statesService.moduleStates$.pipe(
      combineLatestWith(this.moduleId$),
      map(([states, serialNumber]) =>
        serialNumber ? states.get(serialNumber) : undefined
      ),
      filter((state): state is ModuleState => !!state),
      distinctUntilChanged()
    );

    // get the order information for that id.
    return moduleState$.pipe(
      combineLatestWith(
        this.orderStatesService.activeOrders$.pipe(startWith([]))
      ),
      map(([state, orders]) => {
        let orderStepInfo: OrderStepInfo | undefined;
        let firstModuleStep: OrderManufactureStep | undefined;
        const currentOrder = orders.find((o) => o.orderId === state.orderId);

        if (currentOrder) {
          const currentModuleStepIndex = this.findLatestOrderStepIndexForModule(
            currentOrder,
            state.serialNumber
          );
          firstModuleStep = this.findStartOfCurrentModuleSteps(
            currentOrder,
            state.serialNumber,
            currentModuleStepIndex
          );
          if (
            this.hasCurrentlyRemainingModuleSteps(
              currentOrder,
              state.serialNumber,
              currentModuleStepIndex
            )
          ) {
            orderStepInfo = {
              orderId: state.orderId,
              workpiece: currentOrder?.type,
              workpieceId: currentOrder?.workpieceId,
              startedAt: firstModuleStep?.startedAt,
            };
          }
        }
        return orderStepInfo;
      })
    );
  }

  /**
   * Get the paired module data for the given module
   * @private
   */
  private createModuleDataObservable() {
    return this.factoryLayoutService.pairedModules$.pipe(
      combineLatestWith(this.moduleId$),
      map(([modules, moduleId]) =>
        moduleId
          ? modules.find((module) => module.serialNumber === moduleId)
          : undefined
      ),
      shareReplay(1),
      takeUntil(this.destroyed$),
    );
  }

  ngOnDestroy() {
    this.destroyed$.complete();
    this.moduleId$.complete();
  }

  clickEditDuration() {
    if (this.moduleId && !this.durationEditToggle.checked) {
      const settings: ModuleSettings = {
        serialNumber: this.moduleId,
        duration: Number(this.durationInput.nativeElement.value),
      };
      this.mqttClient.publish(CcuTopic.SET_MODULE_DURATION, settings);
    }
  }
}
