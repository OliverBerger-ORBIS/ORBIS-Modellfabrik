import { Component, OnDestroy, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateService } from '@ngx-translate/core';
import {
  ReplaySubject,
  combineLatest,
  filter,
  firstValueFrom,
  map,
  take,
  takeUntil,
  tap,
  timeout,
} from 'rxjs';
import { CcuTopic } from '../../../common/protocol';
import {
  CloudStock,
  GeneralConfig,
  OrderRequest,
  OrderResponse,
  OrderState,
  Workpiece,
  generateOrderRequestForProduction,
} from '../../../common/protocol/ccu';
import { TypedMqttService } from '../../futurefactory.service';
import { GeneralConfigService } from '../../services/general-config.service';
import { OrderStatesService } from '../../services/order-states.service';
import { StockStatesService } from '../../services/stock-states.service';
import {
  availability,
  availabilityForOrder,
  durationForOrder,
  oee,
  oeeForOrder,
  performance,
  performanceForOrder,
  productionTimeForOrder,
  quality,
  qualityForOrder,
  waitingTimeForOrder,
} from '../../utils/oee-calculation.utils';
import { getPayload } from '../../utils/rx.utils';
import { WORKPIECE_TYPES } from '../../utils/workpiece.utils';
import { FutureFactorySimulationLayoutState } from './simulation-layout.state';

interface Simulation {
  name: string;
  workpieces: {
    type: Workpiece,
    inStock: boolean,
  }[];
}

@Component({
  templateUrl: './simulation-layout.component.html',
  styleUrls: ['./simulation-layout.component.scss'],
  providers: [FutureFactorySimulationLayoutState],
})
export class FutureFactorySimulationLayoutComponent implements OnInit, OnDestroy {
  private onDestroy$ = new ReplaySubject<void>(1);
  
  readonly stateIcons: { [t in OrderState]: string } = {
    [OrderState.ENQUEUED]: 'hourglass_empty',
    [OrderState.IN_PROGRESS]: 'play_circle',
    [OrderState.FINISHED]: 'check_circle',
    [OrderState.ERROR]: 'error',
    [OrderState.CANCELLED]: 'hourglass_disabled',
  };

  startingSimulation = false;
  simulationNameAlreadyExists = false;
  allSimulationIds: string[] = [];
  allOrders: OrderResponse[] = [];
  /**
   * undefined = no selection
   * null = selection of "no simulation"
   * string = selection of a simulation
   */
  selectedSimulationId: string | undefined | null;
  config: GeneralConfig | undefined;
  get canStartSimulation() {
    return this.simulation.workpieces.length && this.simulation.workpieces.every(w => w.inStock) && !this.simulationNameAlreadyExists && this.simulation.name?.length > 0;
  }

  simulation: Simulation = {
    name: 'Test Simulation',
    workpieces: [
      {
        type: Workpiece.RED,
        inStock: false,
      },
      {
        type: Workpiece.WHITE,
        inStock: false,
      },
      {
        type: Workpiece.BLUE,
        inStock: false,
      },
    ],
  };

  public wsTypes = WORKPIECE_TYPES;
  public runningSimulationId$ = this.orderStatesService.activeOrders$.pipe(
    map((orders: OrderResponse[]) => {
      const simulationIds = Array.from(new Set(orders.filter(o => o.orderType === 'PRODUCTION' && o.simulationId && o.simulationId.length > 0).map(o => o.simulationId!)));
      if (simulationIds.length > 0) {
        return simulationIds[0];
      }
      return undefined;
    })
  );
  public simulationIsRunning$ = this.runningSimulationId$.pipe(
    map((runningSimulationId: string | undefined) => {
      return !!runningSimulationId;
    })
  );

  constructor(
    public state: FutureFactorySimulationLayoutState,
    private orderStatesService: OrderStatesService,
    private mqttService: TypedMqttService,
    private notification: MatSnackBar,
    private translate: TranslateService,
    generalConfigService: GeneralConfigService,
    private stockStatesService: StockStatesService,
  ) {
    stockStatesService.stock$.pipe(
      tap((stock: CloudStock) => this.updateProducability(stock)),
      takeUntil(this.onDestroy$)
    ).subscribe();

    // retrieves all simulation ids and triggers the check for the simulation name
    combineLatest([this.orderStatesService.activeOrders$, this.orderStatesService.completedOrders$]).pipe(
      map(([activeOrders, completedOrders]) => [...activeOrders, ...completedOrders]),
      map((orders: OrderResponse[]) => orders.filter(o => o.orderType === 'PRODUCTION')),
      tap((orders: OrderResponse[]) => {
        this.allOrders = orders;
        this.allSimulationIds = Array.from(new Set(orders.map(o => o.simulationId!).filter(id => id?.length > 0)));
        this.checkSimulationName();
        if (!this.selectedSimulationId && this.allSimulationIds[0]) {
          this.selectedSimulationId = this.allSimulationIds[0];
        }
      }),
      takeUntil(this.onDestroy$)
    ).subscribe();

    generalConfigService.config$.pipe(
      tap((config: GeneralConfig) => this.config = config),
      takeUntil(this.onDestroy$)
    ).subscribe();
  }

  ngOnInit() {
    this.checkSimulationName();
  }

  ngOnDestroy(): void {
    this.onDestroy$.next();
    this.onDestroy$.complete();
  }

  async startSimulation() {
    this.startingSimulation = true;
    const simulationId = this.simulation.name.trim();
    // We need to add additional milliseconds to the timestamp, so the filter inside the cloud gateway does not filter the order request
    // because the timestamp is identical to the timestamp of the last order request
    // We add 25ms (arbitrary value) for each order request, so the timestamp is unique for each order request
    const orderRequests: OrderRequest[] = this.simulation.workpieces.map(
      (w, idx) => generateOrderRequestForProduction(w.type, simulationId, new Date(Date.now() + idx * 25/*ms*/))
    );

    for (const orderRequest of orderRequests) {
      // due to the mqtt-implementation, we need to wait for the response of the order request
      // before we can send the next order request
      try {
        await new Promise((resolve, reject) => {
          this.mqttService.subscribe<OrderResponse>(CcuTopic.ORDER_RESPONSE).pipe(
            getPayload(),
            // moved the check from the if-clause to the filter, because we might receive a message
            // that is not related to the current simulationId or a retained response from a previous order request
            filter(orderResponse => orderResponse.simulationId === simulationId),
            take(1),
            takeUntil(this.onDestroy$),
            timeout(30000)
          ).subscribe({
            next: () => resolve(true),
            error: (err: any) => reject(err),
          });

          // subscribing to the order-response-topic before sending the order-request
          this.mqttService.publish(CcuTopic.ORDER_REQUEST, orderRequest, { qos: 2 });
        });
      } catch (err) {
        this.notification.open(
          this.translate.instant('Beim Starten des Planspiels ist ein Fehler aufgetreten.'),
          this.translate.instant('OK'),
          { duration: 10000, panelClass: 'error-snackbar' }
        );
        this.startingSimulation = false;
        return;
      }
    }

    this.notification.open(
      this.translate.instant('Das Planspiel wurde erfolgreich gestartet.'),
      this.translate.instant('OK'),
      { duration: 10000, panelClass: 'success-snackbar' }
    );
    this.startingSimulation = false;
  }

  removeWorkpiece(workpiece: any) {
    this.simulation.workpieces = this.simulation.workpieces.filter(
      (w) => w !== workpiece
    );
  }

  addWorkpiece() {
    this.simulation.workpieces.push({
      type: Workpiece.WHITE,
      inStock: false,
    });
    this.updateProducability();
  }

  async updateProducability(stock?: CloudStock) {
    if (!stock) {
      stock = await firstValueFrom(this.stockStatesService.stock$);
    }
    if (stock) {
      const reserverForCurrentCalculationLoop: string[] = [];
      this.simulation.workpieces.forEach((w) => {
        const suitableWorkpiece = stock!.stockItems.find(stockItem => stockItem.workpiece?.state !== "RESERVED" && stockItem.workpiece?.type === w.type && reserverForCurrentCalculationLoop.indexOf(stockItem.workpiece?.id) === -1);
        if (suitableWorkpiece) {
          w.inStock = true;
          reserverForCurrentCalculationLoop.push(suitableWorkpiece.workpiece?.id!);
        } else {
          w.inStock = false;
        }
      });
    } else {
      this.simulation.workpieces.forEach((w) => {
        w.inStock = false;
      });
    }
  }

  checkSimulationName() {
    const name = this.simulation.name.trim();
    if (name.length === 0) {
      this.simulationNameAlreadyExists = false;
      return;
    }
    this.simulationNameAlreadyExists = this.allSimulationIds.some(simulationId => simulationId === name);
  }

  toggleSelectSimulation(simulationId: string | null) {
    if (this.selectedSimulationId === simulationId) {
      this.selectedSimulationId = undefined;
    } else {
      this.selectedSimulationId = simulationId;
    }
    this.state.setSelectedOrder(undefined);
  }

  /** OEE calculations */
  oee(simulationId: string | null): number {
    if (!this.config) {
      return 0;
    }
    const orders = this.allOrders.filter(o => o.simulationId == simulationId);
    return oee(orders, this.config);
  }

  availability(simulationId: string | null): number {
    const orders = this.allOrders.filter(o => o.simulationId == simulationId);
    return availability(orders);
  }

  availabilityForOrder(order: OrderResponse): number {
    return availabilityForOrder(order);
  }

  quality(simulationId: string | null): number {
    const orders = this.allOrders.filter(o => o.simulationId == simulationId);
    return quality(orders);
  }

  qualityForOrder(order: OrderResponse): number {
    return qualityForOrder(order);
  }

  performance(simulationId: string | null): number {
    if (!this.config) {
      return 0;
    }
    const orders = this.allOrders.filter(o => o.simulationId == simulationId);
    return performance(orders, this.config);
  }

  downloadCsv() {
    this.downloadCsvOee();
    this.downloadRawDataCsv();
  }

  downloadCsvOee() {
    const csvContent = 'data:text/csv;charset=utf-8,' + [
      'Simulation',
      'OrderId',
      'OEE',
      'Availability',
      'Quality',
      'Performance',
      'Number of Orders',
      'Duration (seconds)',
      'Waiting Time (seconds)',
      'Producton Time (seconds)',
      'Start',
      'End',
      'Received At',
    ].join(',') + '\n' + [...this.allSimulationIds, null].map(simulationId => {
      const orders = this.allOrders.filter(o => o.simulationId == simulationId && o.orderType === 'PRODUCTION');
      const simulationIdForCsv = simulationId?.includes(',') ? `'${simulationId}'` : (simulationId ?? 'without simulation');
      const mainRow = [
        simulationIdForCsv,
        'Planspielzusammenfassung',
        oee(orders, this.config!),
        availability(orders),
        quality(orders),
        performance(orders, this.config!),
        orders.length,
        orders.reduce((acc, order) => acc + durationForOrder(order, this.config!), 0),
        orders.reduce((acc, order) => acc + waitingTimeForOrder(order), 0),
        orders.reduce((acc, order) => acc + productionTimeForOrder(order), 0),
        orders.reduce((acc, order) => {
          if (order.startedAt && (!acc || order.startedAt.getTime() < acc.getTime())) {
            return order.startedAt;
          }
          return acc;
        }, new Date()),
        orders.reduce((acc, order) => {
          if (order.stoppedAt && (!acc || order.stoppedAt.getTime() > acc.getTime())) {
            return order.stoppedAt;
          }
          return acc;
        }, new Date()),
      ].join(',');
      const orderRows = orders.map(order => [
        simulationIdForCsv,
        order.orderId,
        oeeForOrder(order, this.config!),
        availabilityForOrder(order),
        qualityForOrder(order),
        performanceForOrder(order, this.config!),
        1,
        durationForOrder(order, this.config!),
        waitingTimeForOrder(order),
        productionTimeForOrder(order),
        order.startedAt,
        order.stoppedAt,
        order.receivedAt,
      ].join(','));
      return [mainRow, ...orderRows].join('\n');
    }).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'oee.csv');
    document.body.appendChild(link); // Required for FF
    link.click();
  }

  downloadRawDataCsv() {
    const csvContent = 'data:text/csv;charset=utf-8,' + [
      'Simulation',
      'OrderId',
      'WorkpieceType',
      'WorkpieceId',
      'StepId',
      'Type',
      'State',
      'StartedAt',
      'StoppedAt',
      'ReceivedAt',
      'ModuleType',
      'Command',
      'PreviousStepId',
    ].join(',') + '\n' + [...this.allSimulationIds, null].map(simulationId => {
      const orders = this.allOrders.filter(o => o.simulationId == simulationId && o.orderType === 'PRODUCTION');
      const simulationIdForCsv = simulationId?.includes(',') ? `'${simulationId}'` : (simulationId ?? 'without simulation');
      const orderRows = orders.map(order => {
        const mainRow = [
          simulationIdForCsv,
          order.orderId,
          order.type,
          order.workpieceId,
          '',
          'PRODUCTION',
          order.state,
          order.startedAt,
          order.stoppedAt,
          order.receivedAt,
          '',
          '',
          '',
        ].join(',');
        const subRows = order.productionSteps.map(step => [
          simulationIdForCsv,
          order.orderId,
          order.type,
          order.workpieceId,
          step.id,
          step.type,
          step.state,
          step.startedAt,
          step.stoppedAt,
          '',
          (step.type === 'MANUFACTURE' ? step.moduleType : step.target),
          (step.type === 'MANUFACTURE' ? step.command : 'DRIVE'),
          step.dependentActionId,
        ].join(',')).join('\n');
        return [mainRow, subRows].join('\n');
      });
      return orderRows.join('\n');
    }).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'raw-data.csv');
    document.body.appendChild(link); // Required for FF
    link.click();
  }
}
