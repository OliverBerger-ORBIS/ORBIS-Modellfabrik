import { CcuTopic, OrderRequest, OrderResponse, Workpiece } from '../../../../../common/protocol';
import { getMqttClient } from '../../../mqtt/mqtt';
import {
  AvailableState,
  FtsPairedModule,
  OrderManufactureStep,
  OrderNavigationStep,
  OrderState,
  PairedModule,
} from '../../../../../common/protocol/ccu';
import { selectFtsPathForStep, sendClearModuleNodeNavigationRequest, sendNavigationRequest } from '../../fts/navigation/navigation';
import { sendAnnounceDpsOutput, sendProductionCommand } from '../../production/production';
import { State } from '../../../../../common/protocol/vda';
import {
  DeliveryMetadata,
  DurationMetadata,
  getNfcPosition,
  HistoryPoint,
  ModuleCommandType,
  ModuleType,
  QualityResult,
  StoreMetadata,
} from '../../../../../common/protocol/module';
import { generateOrderStepList } from '../index';
import { PairingStates } from '../../pairing/pairing-states';
import { publishGatewayOrderUpdate } from '../../gateway/order/publish';
import { ControllerNotReadyError, FTSNotReadyError, FtsPathResult } from '../../../models/models';
import { FtsPairingStates } from '../../pairing/fts-pairing-states';
import { OrderFlowService } from '../flow/order-flow-service';
import { randomUUID } from 'node:crypto';
import { metadataForCommand } from '../../production/helper';
import { StockManagementService } from '../stock/stock-management-service';
import { publishStock } from '../../production/cloud-stock';
import { v4 as uuid } from 'uuid';
import { GeneralConfigService } from '../../../services/config/general-config-service';

export type OrderManagementAction = {
  index: number;
  value: OrderNavigationStep | OrderManufactureStep;
  orderId: string;
  workpiece: Workpiece;
  workpieceId?: string;
};

export class OrderManagement {
  private static instance: OrderManagement;

  public static getInstance(): OrderManagement {
    if (!OrderManagement.instance) {
      OrderManagement.instance = new OrderManagement();
    }
    return OrderManagement.instance;
  }

  /** Order queue containing all orders. The currently active order will always be at index 0 */
  private orderQueue: Array<OrderResponse>;
  private activeOrders: Array<OrderResponse>;
  private navStepsToExecute: Array<OrderManagementAction> = [];
  private manufactureStepsToExecute: Array<OrderManagementAction> = [];
  private completedOrders: Array<OrderResponse>;
  private pairingStates: PairingStates;
  private ftsPairingStates: FtsPairingStates;

  private constructor() {
    this.orderQueue = new Array<OrderResponse>();
    this.activeOrders = new Array<OrderResponse>();
    this.completedOrders = new Array<OrderResponse>();
    this.pairingStates = PairingStates.getInstance();
    this.ftsPairingStates = FtsPairingStates.getInstance();
  }

  /**
   * Reinitialize the order management and clear all orders
   */
  public async reinitialize() {
    this.orderQueue = [];
    this.activeOrders = [];
    this.completedOrders = [];
    this.navStepsToExecute = [];
    this.manufactureStepsToExecute = [];
    this.pairingStates = PairingStates.getInstance();
    this.ftsPairingStates = FtsPairingStates.getInstance();
    await this.sendOrderListUpdate();
    await this.sendCompletedOrderListUpdate();
    StockManagementService.removeAllReservations();
  }

  /**
   * Publishes the current order list to the broker
   */
  public async sendOrderListUpdate(): Promise<void> {
    const mqtt = getMqttClient();
    if (!mqtt) {
      return Promise.resolve();
    }
    await publishGatewayOrderUpdate(this.orderQueue);
    return await mqtt.publish(CcuTopic.ACTIVE_ORDERS, JSON.stringify(this.orderQueue), { qos: 2, retain: true });
  }

  private async sendCompletedOrderListUpdate(): Promise<void> {
    const mqtt = getMqttClient();
    if (!mqtt) {
      return await Promise.resolve();
    }
    return await mqtt.publish(CcuTopic.COMPLETED_ORDERS, JSON.stringify(this.completedOrders), { qos: 2, retain: true });
  }

  public async cacheOrder(order: OrderResponse): Promise<void> {
    this.orderQueue.push(order);
    await this.startOrder(order);
    return this.sendOrderListUpdate();
  }

  /** Start an order */
  public startOrder(order: OrderResponse): Promise<void> {
    const maxParallelOrders = GeneralConfigService.config.productionSettings.maxParallelOrders;
    if (this.activeOrders.length >= maxParallelOrders && order.orderType === 'PRODUCTION') {
      // StorageOrders should always be possbile
      console.debug('ORDER_MANAGEMENT: Maximum number of parallel orders reached, not starting Order with id: ' + order.orderId);
      return Promise.resolve();
    }
    // only start the order if a workpiece / empty bay can be reserved.
    if (order.orderType === 'PRODUCTION' && !StockManagementService.reserveWorkpiece(order.orderId, order.type)) {
      return Promise.resolve();
    } else if (order.orderType === 'STORAGE' && !StockManagementService.reserveEmptyBay(order.orderId, order.type)) {
      return Promise.resolve();
    }

    console.debug(`ORDER_MANAGEMENT: Starting order  ${order.orderId}`);
    this.activeOrders.push(order);
    order.state = OrderState.IN_PROGRESS;
    order.startedAt = new Date();

    const independentActionList = order.productionSteps
      .filter(step => !step.dependentActionId)
      .filter(step => step.state === OrderState.ENQUEUED)
      .map((value, index) => ({
        index,
        value,
        orderId: order.orderId,
        workpiece: order.type,
        workpieceId: order.workpieceId,
      }));
    return this.triggerIndependentActions(order, independentActionList);
  }

  /**
   * Determine the target module for a navigation action
   * @param actionId
   * @returns the target
   */
  public getTargetModuleTypeForNavActionId(actionId: string): ModuleType | undefined {
    const combinedOrders = [...this.completedOrders, ...this.orderQueue];
    for (const order of combinedOrders) {
      const dockStep = order.productionSteps.find(step => step.id === actionId);
      if (dockStep && dockStep.type === 'NAVIGATION') {
        // TODO: FITEFF22-262 Change to serial number to allow multiple modules
        console.debug(`Found Id: ${dockStep.id} with target: ${dockStep.target}`);
        return dockStep.target;
      }
    }
    return undefined;
  }

  private addIfNotPresent(list: Array<OrderManagementAction>, newEntry: OrderManagementAction): void {
    const present = list.find(entry => entry.value.id === newEntry.value.id);
    if (present) {
      return;
    }
    console.log('ORDER_MANAGEMENT: Adding new entry to list: ', newEntry);
    list.push(newEntry);
  }

  // TODO: Verify this actually does what it is supposed to
  public async triggerIndependentActions(order: OrderResponse, independentActionList: OrderManagementAction[]) {
    independentActionList.filter(step => step.value.type === 'NAVIGATION').map(step => this.addIfNotPresent(this.navStepsToExecute, step));
    for (const step of independentActionList.filter(step => step.value.type === 'MANUFACTURE')) {
      const action = step.value as OrderManufactureStep;
      if (action.command === ModuleCommandType.DROP) {
        await this.handleNextActionDrop(order, step);
      } else {
        this.addIfNotPresent(this.manufactureStepsToExecute, step);
      }
    }
    await this.triggerNavigationSteps();
    await this.triggerManufactureSteps();
  }

  /**
   * Generates the actual next action if the action to be executed equals a drop action.
   * The result can either be a navigation if there is not fts docked at the module or a manufacture action if the fts is docked at the correct module.
   * @param order the order of the action is associated with
   * @param step the step to be executed
   * @private
   */
  private async handleNextActionDrop(order: OrderResponse, step: OrderManagementAction) {
    const action = await this.generateNextActionForDrop(order, step.value);
    if (action.value.type === 'NAVIGATION') {
      this.addIfNotPresent(this.navStepsToExecute, action);
    } else {
      this.addIfNotPresent(this.manufactureStepsToExecute, action);
    }
  }

  /**
   * Check that a workpiece is available when driving to the storage.
   * An FTS either already has a workpiece and deliver it workpiece or
   * or it receives it from the storage and it has to be available and reserved.
   * @param step
   * @private
   * @returns true if the target is the storage and the order has no assigned workpiece
   */
  private isStorageTargetWithoutAvailableWorkpiece(step: OrderManagementAction): boolean {
    if (step.value.type !== 'NAVIGATION' || step.value.target !== ModuleType.HBW) {
      return false;
    }
    if (step.workpieceId) {
      return false;
    }
    return !StockManagementService.reserveWorkpiece(step.orderId, step.workpiece);
  }

  /**
   * Check that an empty storage bay is available when driving to the storage with a workpiece
   * Try to reserve an empty bay if necessary.
   * @param step
   * @private
   * @returns true if the target is the storage and the order has no assigned bay for its workpiece
   */
  private isStorageTargetWithoutAvailableBay(step: OrderManagementAction): boolean {
    if (step.value.type !== 'NAVIGATION' || step.value.target !== ModuleType.HBW) {
      return false;
    }
    if (!step.workpieceId) {
      return false;
    }
    return !StockManagementService.reserveEmptyBay(step.orderId, step.workpiece);
  }

  /**
   * Choose the correct FTS for an order step
   * @param orderId
   * @param targetId
   * @param nav
   * @private
   */
  public chooseReadyFtsForStep(orderId: string, targetId: string, nav: OrderNavigationStep): FtsPathResult | undefined {
    const order = this.getActiveOrder(orderId);
    console.log('order found that needs navigation: ', order);
    if (!order) {
      return undefined;
    }
    return selectFtsPathForStep(order, targetId, nav);
  }

  public getActiveOrder(orderId: string): OrderResponse | undefined {
    return this.activeOrders.find(o => o.orderId === orderId);
  }

  /**
   * Choose the module target for a navigation step.
   * If an order has a reserved workpiece when navigating to an HBW, then select that HBW.
   * If an order is currently assigned to a module, then use that module and fail if the module type does not match
   * If nothing applies, choose module that is ready to accept this order.
   * @param orderId
   * @param targetType
   * @private
   */
  private chooseModuleForNavigationTarget(orderId: string, targetType: ModuleType): PairedModule | undefined {
    if (targetType === ModuleType.HBW) {
      const serialNumber = StockManagementService.getReservedWarehouse(orderId);
      if (serialNumber && this.pairingStates.get(serialNumber)) {
        console.log(`ORDER_MANAGEMENT: Navigation to the warehouse with the reserved workpiece for ${orderId}: ${serialNumber}`);
        return this.pairingStates.get(serialNumber);
      }
    }
    console.log(
      `ORDER_MANAGEMENT: Finding Navigation target module currently assigned to the order ${orderId} and target type: ${targetType}`,
    );
    const orderTarget = this.pairingStates.getModuleForOrder(orderId);
    console.log(`ORDER_MANAGEMENT: Found order target ${JSON.stringify(orderTarget)}`);

    // An assigned target was found, return that
    if (orderTarget && orderTarget.subType === targetType) {
      console.log(`ORDER_MANAGEMENT: Navigation to the module currently assigned to the order ${orderId}: ${orderTarget.serialNumber}`);
      return orderTarget;
    }
    // An assigned target was found, but the subtype is invalid. Try to look again (maybe there are duplicate assignments
    if (orderTarget && orderTarget.subType !== targetType) {
      console.log(
        `ORDER_MANAGEMENT: Assigned module is of the wrong type for ${orderId}. Expected ${targetType} but got ${orderTarget.subType}`,
      );
      const orderTargetModule = this.pairingStates.getModuleForOrder(orderId, targetType);
      if (orderTargetModule) {
        console.warn(`ORDER_MANAGEMENT: Found module of the correct type for ${orderId}: ${orderTargetModule.serialNumber}
          This indicates that some module was still assigned to an order which should not happen.`);
        return orderTargetModule;
      }
    }

    // choose a ready unassigned module if the order has no module assigned.
    const target = this.pairingStates.getReadyForModuleType(targetType, orderId);
    if (target) {
      return target;
    }
  }

  private async triggerNavigationSteps(): Promise<number> {
    // only trigger steps which are not in progress
    let triggeredSteps = 0;
    const unTriggeredNav = this.navStepsToExecute.filter(step => step.value.state === OrderState.ENQUEUED);
    const availableFtsIds = new Set(this.ftsPairingStates.getAllReadyUnassigned().map(fts => fts.state.serialNumber));
    const blockedModules: Array<{ ftsSerial: string; moduleSerial: string }> = [];
    for (const step of unTriggeredNav) {
      try {
        if (step.value.type !== 'NAVIGATION') {
          console.log('ORDER_MANAGEMENT: Wrong step type assigned to navigation step array');
          continue;
        }
        const nav = step.value;

        // only try to navigate to the HBW for an order when we have a workpiece or can reserve one.
        if (this.isStorageTargetWithoutAvailableWorkpiece(step)) {
          console.log('ORDER_MANAGEMENT: No workpiece available for order : ' + step.orderId);
          continue;
        }
        // only try to navigate to the HBW for a STORAGE order if we can store the workpiece in an empty bay.
        if (this.isStorageTargetWithoutAvailableBay(step)) {
          console.log('ORDER_MANAGEMENT: No empty storage bay available for order : ' + step.orderId);
          continue;
        }

        // find module that exists for order
        const target = this.chooseModuleForNavigationTarget(step.orderId, nav.target);
        if (!target) {
          console.log('ORDER_MANAGEMENT: No module ready for order : ' + step.orderId);
          continue;
        } else if (!this.pairingStates.isReadyForOrder(target.serialNumber, step.orderId)) {
          console.log(`ORDER_MANAGEMENT: Chosen module ${target.serialNumber} for order ${step.orderId} is not ready`);
          continue;
        }

        const ftsPath = this.chooseReadyFtsForStep(step.orderId, target.serialNumber, nav);
        console.log('ftspath: ', ftsPath);
        if (!ftsPath || !ftsPath.path) {
          console.log('ORDER_MANAGEMENT: No FTS with free path ready for order: ' + step.orderId);
          const fts = this.ftsPairingStates.getFtsAtPosition(target.serialNumber);
          if (fts) {
            console.log(`ORDER_MANAGEMENT: FTS ${fts.serialNumber} is blocking module ${target.serialNumber}`);
            blockedModules.push({
              ftsSerial: fts.serialNumber,
              moduleSerial: target.serialNumber,
            });
          }
          continue;
        }

        const fts = ftsPath.fts;
        // Setting the state to in progress will prevent the step from being triggered again
        step.value.state = OrderState.IN_PROGRESS;
        await sendNavigationRequest(nav, step.orderId, step.index, step.workpiece, step.workpieceId, fts, target.serialNumber);
        // send the active output to the DPS
        if (nav.target === ModuleType.DPS && this.getNextStepCommand(step) === ModuleCommandType.PICK) {
          await sendAnnounceDpsOutput(target.serialNumber, step.orderId, step.workpiece);
        }
        availableFtsIds.delete(fts.serialNumber);
        console.debug(`sending nav command for order: ${step.orderId} source: ${nav.source} target: ${nav.target}`);
        this.navStepsToExecute.splice(this.navStepsToExecute.indexOf(step), 1);
        // log the time the command was sent as the start time of this step
        nav.startedAt = new Date();
        triggeredSteps++;
        // remove the return command allowing only a single order.
        // the FTS is now assigned to the order and cannot be reused.
        // that makes it possible to start the next order with the next FTS.
      } catch (e) {
        if (e instanceof FTSNotReadyError) {
          console.warn(`FTS not ready order: ${step.orderId} action: ${step.value.id} message: ${e.message}`);
        } else {
          console.warn('Error while sending navigation request', e);
        }
        // if an error occurs, we set the state back to enqueued to try again later
        step.value.state = OrderState.ENQUEUED;
      }
    }

    // After all possible normal navigation orders are sent look for modules that are blocked by an FTS and move those.
    for (const blocked of blockedModules) {
      if (availableFtsIds.has(blocked.ftsSerial)) {
        try {
          await sendClearModuleNodeNavigationRequest(blocked.moduleSerial);
          availableFtsIds.delete(blocked.ftsSerial);
        } catch (e) {
          // If an error occurs, continue and wait
          console.warn(`Error while sending navigation request to ${blocked.ftsSerial} to clear module ${blocked.moduleSerial}`, e);
        }
      }
    }
    return triggeredSteps;
  }

  /**
   * Skips the current navigation step and directly start the manufacture
   * @param step
   * @param order
   * @param nextStep manufacture step
   * @param fts
   * @throws FTSNotReadyError
   * @private
   */
  private async skipNavStepAndStartDrop(
    step: OrderManagementAction,
    order: OrderResponse,
    nextStep: OrderManufactureStep,
    fts: FtsPairedModule,
  ) {
    if (!fts.lastLoadPosition || !fts.lastModuleSerialNumber || step.value.type !== 'NAVIGATION') {
      return;
    }
    if (
      !this.ftsPairingStates.isLoadingBayFree(fts.serialNumber, fts.lastLoadPosition) &&
      // allow the loading bay to be filled/reserved by the same orderId
      this.ftsPairingStates.getLoadingBayForOrder(fts.serialNumber, order.orderId) !== fts.lastLoadPosition
    ) {
      throw new FTSNotReadyError(`FTS ${fts.serialNumber} is docked, but loading bay ${fts.lastLoadPosition} is occupied`);
    }
    if (!this.pairingStates.isReadyForOrder(fts.lastModuleSerialNumber, order.orderId)) {
      throw new ControllerNotReadyError('MODULE', nextStep.moduleType, `Module with workpiece is not ready to drop`);
    }
    step.value.startedAt = new Date();
    step.value.stoppedAt = new Date();
    step.value.state = OrderState.FINISHED;
    this.navStepsToExecute.splice(this.navStepsToExecute.indexOf(step), 1);
    const nextStepIndex = order.productionSteps.indexOf(nextStep);
    this.ftsPairingStates.setLoadingBay(fts.serialNumber, fts.lastLoadPosition, order.orderId);
    await this.ftsPairingStates.updateAvailability(fts.serialNumber, AvailableState.READY, order.orderId);
    const nextStepAction = this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
    // block the target for the current order so that the command can be sent to the correct one and no other order can use it
    await this.pairingStates.updateAvailability(fts.lastModuleSerialNumber, AvailableState.READY, order.orderId);
    this.manufactureStepsToExecute.push(nextStepAction);
    await this.triggerOneManufactureStep(nextStepAction);
  }

  private async triggerManufactureSteps(): Promise<number> {
    let triggeredSteps = 0;
    const unTriggeredManufacture = this.manufactureStepsToExecute.filter(step => step.value.state === OrderState.ENQUEUED);
    for (const step of unTriggeredManufacture) {
      if (await this.triggerOneManufactureStep(step)) {
        triggeredSteps++;
      }
    }
    return triggeredSteps;
  }

  async triggerOneManufactureStep(step: OrderManagementAction): Promise<boolean> {
    let result = false;
    try {
      const prod = step.value as OrderManufactureStep;
      const pairedModule = PairingStates.getInstance().getReadyForModuleType(prod.moduleType, step.orderId);
      if (!pairedModule) {
        console.warn(`Module for action of type ${(step.value as OrderManufactureStep).moduleType} is not ready. Retrying later`);
        return false;
      }
      const serialNumber = pairedModule.serialNumber;

      step.value.state = OrderState.IN_PROGRESS;
      // generate metadata for the command and add it as parameter to sendProductionCommand
      const metadata = this.generateMetadataForProductionCommand(prod, pairedModule, step.workpiece, step.workpieceId);
      await sendProductionCommand(prod, step.orderId, step.index, pairedModule, metadata);
      console.debug(
        `COMMAND_SENDING: manufacturing nav command for order: ${step.orderId} module: ${prod.moduleType} command: ${prod.command} workpieceId: ${step.workpieceId}`,
      );
      const stepIndex = this.manufactureStepsToExecute.indexOf(step);
      if (stepIndex >= 0) {
        this.manufactureStepsToExecute.splice(stepIndex, 1);
      }
      // log the time the command was sent as the start time of this step
      prod.startedAt = new Date();
      // remember the module that was chosen for this step
      prod.serialNumber = serialNumber;
      result = true;
    } catch (e) {
      console.warn(`Module for action of type ${(step.value as OrderManufactureStep).moduleType} is not ready. Retrying`, e);
      step.value.state = OrderState.ENQUEUED;
    }
    return result;
  }

  public generateMetadataForProductionCommand(
    productionStep: OrderManufactureStep,
    pairedModule: PairedModule,
    workpiece: Workpiece,
    workpieceId?: string,
  ): DurationMetadata | StoreMetadata | DeliveryMetadata {
    if (productionStep.moduleType === ModuleType.DPS && workpieceId) {
      // in case of DPS generate the workpiece production history
      return this.generateDpsMetadata(workpiece, workpieceId);
    }
    return metadataForCommand(productionStep.moduleType, productionStep.command, pairedModule, workpiece, workpieceId);
  }

  private generateDpsMetadata(workpiece: Workpiece, workpieceId: string): DeliveryMetadata {
    const history: HistoryPoint[] = [];
    // history ts ist der timestamp von end of the process
    [...this.orderQueue, ...this.completedOrders]
      .filter(order => order.workpieceId === workpieceId)
      .map(order => {
        order.productionSteps
          .filter(step => step.type === 'MANUFACTURE')
          .map(step => step as OrderManufactureStep)
          .filter(step => step.state === OrderState.FINISHED)
          .forEach(step => {
            const nfcPosition = getNfcPosition(step.moduleType, step.command);
            if (!nfcPosition) {
              return;
            }

            history.push({
              // we filter for finished steps a few lines above, so we can be sure that stoppedAt is set
              // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
              ts: step.stoppedAt!.getTime(),
              code: nfcPosition,
            });
          });
      });
    console.debug(`ORDER_MANAGEMENT: Building history for workpieceId: ${workpieceId} history:`, history);
    return <DeliveryMetadata>{
      workpiece: {
        workpieceId,
        type: workpiece,
        history: history,
        state: 'PROCESSED',
      },
    };
  }

  public async handleActionUpdate(orderId: string, actionId: string, state: State, result?: string): Promise<void> {
    // if the action is not finished or failed don't do anything. Errors have to be rest manually on the
    // FTS/Module which will delete the order completely
    console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} and action id: ${actionId} and state: ${state}`);
    if (state !== State.FINISHED && state !== State.FAILED) {
      return Promise.resolve();
    }

    const activeOrder = this.activeOrders.find(order => order.orderId === orderId);
    if (!activeOrder) {
      console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} no active order found`);
      return Promise.resolve();
    }

    const step = activeOrder.productionSteps.find(step => step.id === actionId);
    if (!step) {
      console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} no step found for id: ${actionId}`);
      return Promise.resolve();
    }
    if (step.state !== OrderState.IN_PROGRESS && step.state !== OrderState.ENQUEUED) {
      console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} steps has already been handled for id: ${actionId}`);
      return Promise.resolve();
    }
    // log the first time the finished or error status has been received for an action
    if (!step.stoppedAt) {
      step.stoppedAt = new Date();
    }

    if (state === State.FAILED) {
      // a failed action will only set the error state. The error has to be cleared on the fts/module
      console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} set error for id: ${actionId}`);
      step.state = OrderState.ERROR;
      return this.sendOrderListUpdate();
    } else {
      step.state = OrderState.FINISHED;
    }

    if (this.isQualityCheckFailure(step, result)) {
      return this.handleActionUpdateQualityCheckFailure(activeOrder, step as OrderManufactureStep);
    }

    if (this.isStoragePickDrop(step)) {
      StockManagementService.removeReservation(orderId);
      await publishStock();
      // start next order if possible
      await this.startNextOrder();
    }

    const stepIndex = activeOrder.productionSteps.indexOf(step);
    // if step is last step in order, remove order from queue and start next order
    if (stepIndex === activeOrder.productionSteps.length - 1) {
      console.debug(
        `ORDER_MANAGEMENT: handle action update for orderId: ${orderId} action: ${actionId} is the last step in order. Starting next one if present`,
      );
      activeOrder.state = OrderState.FINISHED;
      await this.deleteFinishedOrders(activeOrder);
      // try to resume existing orders
      await this.retriggerFTSSteps();
      await this.startNextOrder();
    } else {
      console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} starting next step in order`);
      await this.startNextStep(activeOrder, step);
    }

    return this.sendOrderListUpdate();
  }

  /**
   * Handle the case of an unsatisfactory quality check.
   *
   * If the quality check fails the workpiece, then it is discarded
   * and a new workpiece is commissioned and attached to the order
   *
   * @param order The order that contains the step
   * @param step The quality control step that failed
   * @returns `true` if the step was handled, `false` if the step is still unhandled
   * @private
   */
  private async handleActionUpdateQualityCheckFailure(order: OrderResponse, step: OrderManufactureStep): Promise<void> {
    // set the AIQS availability to available for any order, since the workpiece will be discarded and is no longer on the module itself
    this.pairingStates.clearModuleForOrder(order.orderId);

    step.state = OrderState.ERROR;
    // cancel the remaining order steps
    this.cancelRemainingSteps(order, step);
    // as of FITEFF22-657 create a new order instead of updating the old one.
    order.state = OrderState.ERROR;
    await this.deleteFinishedOrders(order);

    const orderRequest: OrderRequest = {
      orderType: order.orderType,
      type: order.type,
      timestamp: order.timestamp,
      simulationId: order.simulationId,
    };
    const response = await this.createOrder(orderRequest);
    console.debug(`QUALITY_FAILURE: Replacing order ${order.orderId} with new order ${response?.orderId ?? 'FAILED'}`);
  }

  public async createOrder(orderRequest: OrderRequest): Promise<OrderResponse | null> {
    const orderId = uuid();
    const productionDefinition = OrderFlowService.getProductionDefinition(orderRequest.type);
    if (!productionDefinition.navigationSteps) {
      console.error('Production order has no navigation steps configured, aborting ...');
      return null;
    } else if (!StockManagementService.reserveWorkpiece(orderId, orderRequest.type)) {
      console.error('No workpiece available to create order for ' + orderRequest.type);
      return null;
    }
    const productionSteps: Array<OrderNavigationStep | OrderManufactureStep> = generateOrderStepList(productionDefinition);
    const response: OrderResponse = {
      orderType: orderRequest.orderType,
      type: orderRequest.type,
      timestamp: orderRequest.timestamp,
      orderId,
      productionSteps: productionSteps,
      receivedAt: new Date(),
      state: OrderState.ENQUEUED,
      workpieceId: orderRequest.workpieceId ? orderRequest.workpieceId : undefined,
      simulationId: orderRequest.simulationId,
    };
    await this.cacheOrder(response);
    return response;
  }

  /**
   * Checks if the given step is a quality control action that failed the quality check
   * @param step The step to check
   * @param result The result of the action triggered by the step
   */
  isQualityCheckFailure(step: OrderNavigationStep | OrderManufactureStep, result?: string) {
    return (
      step &&
      step.type === 'MANUFACTURE' &&
      step.moduleType === ModuleType.AIQS &&
      step.command === ModuleCommandType.CHECK_QUALITY &&
      result === QualityResult.FAILED
    );
  }

  /**
   * Checks if the given step is a storage pick or drop action
   * @param step The step to check
   */
  isStoragePickDrop(step: OrderNavigationStep | OrderManufactureStep) {
    if (!step || step.type !== 'MANUFACTURE' || step.moduleType !== ModuleType.HBW) {
      return false;
    }
    return step.command === ModuleCommandType.DROP || step.command === ModuleCommandType.PICK;
  }

  /**
   * Generate the production steps necessary to produce a new workpiece when the FTS is docked at AIQS
   * @param type the workpiece type to produce again
   * @returns all steps to send the FTS to the start and produce the workpiece
   * @private
   */
  private generateReproductionOrderSteps(type: Workpiece): Array<OrderManufactureStep | OrderNavigationStep> {
    const productionDefinition = OrderFlowService.getProductionDefinition(type);
    return generateOrderStepList(productionDefinition);
  }

  /**
   * Cancel all remaining actions of an order.
   *
   * This should be done when the result of a step indicates that the order cannot be continued further.
   *
   * @param order The order that contains the step
   * @param step The last step that is not cancelled, usually a failed step
   * @private
   */
  private cancelRemainingSteps(order: OrderResponse, step: OrderManufactureStep | OrderNavigationStep) {
    const stepIndex = order.productionSteps.indexOf(step);
    if (stepIndex < 0) {
      return;
    }
    // cancel all following steps
    const nextStepIndex = stepIndex + 1;
    for (const nextStep of order.productionSteps.slice(nextStepIndex)) {
      nextStep.state = OrderState.CANCELLED;
    }
    console.debug(`Cancelled remaining steps for order ${order.orderId}`);
  }

  private async startNextStep(order: OrderResponse, step: OrderManufactureStep | OrderNavigationStep): Promise<void> {
    step.state = OrderState.FINISHED;
    const nextStep = order.productionSteps.find(nextStep => nextStep.dependentActionId === step.id);
    if (!nextStep) {
      console.debug(`ORDER_MANAGEMENT: start next step for orderId: ${order.orderId} no next step found`);
      return Promise.resolve();
    }

    if (nextStep.state !== OrderState.ENQUEUED) {
      console.debug(
        `ORDER_MANAGEMENT: next step for orderId: ${order.orderId} is not in state ENQUEUED but ${nextStep.state} no need to start it`,
      );
      // try to resume navigation for other existing orders
      await this.retriggerFTSSteps();
      return Promise.resolve();
    }

    console.debug(`ORDER_MANAGEMENT: start next step for orderId: ${order.orderId} next step found with id ${nextStep.id}`);
    const nextStepIndex = order.productionSteps.indexOf(nextStep);
    const nextStepAction = this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
    return this.triggerIndependentActions(order, [nextStepAction]);
  }

  /**
   * Returns the command for the next step.
   * @param step
   */
  public getNextStepCommand(step: OrderManagementAction): ModuleCommandType | 'NAVIGATION' | undefined {
    const order = this.orderQueue.find(order => order.orderId === step.orderId);
    const nextStep = order?.productionSteps.find(nextStep => nextStep.dependentActionId === step.value.id);
    if (nextStep?.type === 'MANUFACTURE') {
      return nextStep.command;
    } else if (nextStep?.type === 'NAVIGATION') {
      return 'NAVIGATION';
    }
  }

  /**
   * Generates the next action for a drop command.
   * If there is no FTS docked ot the target module, generate a navigation command to navigate one to it. And add the new action to the production definitions of the order
   * If there is one generate the drop command as is
   * @param order the order of the step
   * @param nextStep the next step to get the target
   * @private
   */
  private async generateNextActionForDrop(
    order: OrderResponse,
    nextStep: OrderNavigationStep | OrderManufactureStep,
  ): Promise<OrderManagementAction> {
    const idPrevStep = nextStep?.dependentActionId;
    const nextStepIndex = order.productionSteps.indexOf(nextStep);
    if (!idPrevStep) {
      return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
    }
    const prevStep = order.productionSteps.find(step => step.id === idPrevStep);
    if (!prevStep) {
      return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
    }

    if (prevStep.type !== 'MANUFACTURE') {
      return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
    }

    const serialNumberPrevStep = prevStep.serialNumber;

    if (!serialNumberPrevStep) {
      return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
    }

    if (this.ftsPairingStates.isFtsWaitingAtPosition(order.orderId, serialNumberPrevStep)) {
      return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
    }

    const fts = this.ftsPairingStates.getFtsAtPosition(serialNumberPrevStep, order.orderId);
    if (fts && fts.lastLoadPosition) {
      // This sets the load for the current position to the order that will run
      this.ftsPairingStates.setLoadingBay(fts.serialNumber, fts.lastLoadPosition, order.orderId);
      await this.ftsPairingStates.updateAvailability(fts.serialNumber, AvailableState.BUSY, order.orderId);
      return this.generateOrderManagementAction(nextStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
    }

    const moduleType = prevStep.moduleType;

    // generate navigation steps to move the FTS to the next module and update the dependent actionIds and action list
    const navId = randomUUID();
    const navStep = OrderFlowService.getNavigationStep(navId, moduleType, (nextStep as OrderManufactureStep).moduleType);
    nextStep.dependentActionId = navId;

    navStep.dependentActionId = idPrevStep;

    // update the action list
    const navIndexNew = order.productionSteps.indexOf(nextStep);
    order.productionSteps.splice(navIndexNew, 0, navStep);

    return this.generateOrderManagementAction(navStep, nextStepIndex, order.orderId, order.type, order.workpieceId);
  }

  private isOrderStartable(order: OrderResponse) {
    if (order.state !== OrderState.ENQUEUED) {
      return false;
    }
    if (order.orderType === 'STORAGE') {
      return StockManagementService.hasReservedEmptyBay(order.orderId) || StockManagementService.emptyBayAvailable(order.type);
    }
    return StockManagementService.hasReservedWorkpiece(order.orderId) || StockManagementService.stockAvailable(order.type);
  }

  /** Start the next order in the queue that has available stock */
  public async startNextOrder(): Promise<void> {
    const nextOrder = this.orderQueue.find(order => {
      return this.isOrderStartable(order);
    });
    if (!nextOrder) {
      return Promise.resolve();
    }
    await this.startOrder(nextOrder);
    await this.sendOrderListUpdate();
  }

  /**
   * Retry FTS steps that had unavailable modules or FTS
   * @returns the number of sent navigation requests
   */
  public async retriggerFTSSteps(): Promise<number> {
    console.log(`ORDER_MANAGEMENT: re-triggering FTS steps`);
    return await this.triggerNavigationSteps();
  }

  /**
   * Retry module steps that had unavailable modules
   * @returns the number of sent manufacture requests
   */
  public async retriggerModuleSteps(): Promise<number> {
    return await this.triggerManufactureSteps();
  }

  /**
   * Retry queued order steps that were blocked by unavailable modules or fts.
   * If no steps are queued, try to start a new waiting order.
   */
  async resumeOrders(): Promise<void> {
    if (!this.hasActiveOrders()) {
      return this.startNextOrder();
    }
    const triggeredFtsSteps = await this.retriggerFTSSteps();
    const triggeredModuleSteps = await this.retriggerModuleSteps();
    if (triggeredFtsSteps > 0 || triggeredModuleSteps > 0) {
      return this.sendOrderListUpdate();
    }
  }

  /**
   *  Reset an order this will delete an order based on the provided orderId. This will delete any order regardless of its state.
   *  @param orderId the id of the order to reset
   */
  public async resetOrder(orderId: string): Promise<void> {
    const activeOrder = this.activeOrders.find(order => order.orderId === orderId);
    if (activeOrder) {
      activeOrder.state = OrderState.CANCELLED;
      await this.deleteFinishedOrders(activeOrder);
      StockManagementService.removeReservation(orderId);
      await publishStock();
      this.navStepsToExecute = this.navStepsToExecute.filter(step => step.orderId !== orderId);
      this.manufactureStepsToExecute = this.manufactureStepsToExecute.filter(step => step.orderId !== orderId);
    }
    await this.retriggerFTSSteps();
    await this.startNextOrder();
    return activeOrder ? this.sendOrderListUpdate() : Promise.resolve();
  }

  private async deleteFinishedOrders(order: OrderResponse): Promise<void> {
    if (!order.stoppedAt) {
      order.stoppedAt = new Date();
    }
    this.completedOrders.push(order);
    await this.sendCompletedOrderListUpdate();
    const queuePos = this.orderQueue.indexOf(order);
    if (queuePos !== -1) {
      this.orderQueue.splice(queuePos, 1);
    }
    const activePos = this.activeOrders.indexOf(order);
    if (activePos !== -1) {
      this.activeOrders.splice(activePos, 1);
    }
    await this.sendOrderListUpdate();
    // make sure no reservation is left over.
    if (StockManagementService.hasReservedWorkpiece(order.orderId)) {
      console.warn(`ORDER_MANAGEMENT: Stock reservation still exists while handling a completed order: ${order.orderId}`);
      StockManagementService.removeReservation(order.orderId);
      await publishStock();
    }
  }

  private async deleteOrder(orderId: string): Promise<void> {
    const order = this.orderQueue.find(order => order.orderId === orderId);
    if (!order) {
      return;
    }

    if (order.state === OrderState.IN_PROGRESS) {
      return;
    }

    order.state = OrderState.CANCELLED;
    this.completedOrders.push(order);
    this.orderQueue.splice(this.orderQueue.indexOf(order), 1);
    await this.sendCompletedOrderListUpdate();
    if (StockManagementService.hasReservedWorkpiece(order.orderId)) {
      console.warn(`ORDER_MANAGEMENT: Stock reservation still exists while deleting an order: ${order.orderId}`);
      StockManagementService.removeReservation(order.orderId);
      await publishStock();
    }
  }

  public async cancelOrders(orderIds: string[]): Promise<void> {
    for (const orderId of orderIds) {
      await this.deleteOrder(orderId);
    }
    return this.sendOrderListUpdate();
  }

  public getWorkpieceType(orderId: string): Workpiece | undefined {
    let workpieceType = this.orderQueue.find(order => order.orderId === orderId)?.type;
    if (!workpieceType) {
      workpieceType = this.completedOrders.find(order => order.orderId === orderId)?.type;
    }
    return workpieceType;
  }

  public getWorkpieceId(orderId: string): string | undefined {
    let workpieceId = this.orderQueue.find(order => order.orderId === orderId)?.workpieceId;
    if (!workpieceId) {
      workpieceId = this.completedOrders.find(order => order.orderId === orderId)?.workpieceId;
    }
    return workpieceId;
  }

  public getOrderForWorkpieceId(workpieceId: string): string | undefined {
    let orderId = this.orderQueue.find(order => order.workpieceId === workpieceId)?.orderId;
    if (!orderId) {
      orderId = this.completedOrders.find(order => order.workpieceId === workpieceId)?.orderId;
    }
    return orderId;
  }

  hasActiveOrders() {
    return this.activeOrders.length > 0;
  }

  /**
   * Generate an action from an order step to be executed by the order management service
   * @param nextStep the next step to be executed
   * @param stepIndex the index of the step in the order
   * @param orderId the id of the order
   * @param workpiece the workpiece type
   * @param workpieceId the id of the workpiece
   * @private
   */
  private generateOrderManagementAction(
    nextStep: OrderManufactureStep | OrderNavigationStep,
    stepIndex: number,
    orderId: string,
    workpiece: Workpiece,
    workpieceId?: string,
  ): OrderManagementAction {
    return {
      index: stepIndex,
      value: nextStep,
      orderId,
      workpiece,
      workpieceId,
    };
  }

  /**
   * Update an order and set a new workpiece id.
   * This happens when a new workpiece is fetched from the HBW for the order.
   *
   * @param orderId
   * @param newWorkpieceId
   */
  updateOrderWorkpieceId(orderId: string, newWorkpieceId: string) {
    const order = this.orderQueue.find(order => order.orderId === orderId);
    if (!order) {
      return;
    }
    console.debug(`ORDER_MANAGEMENT: update workpieceId for order: ${orderId} from ${order.workpieceId} to ${newWorkpieceId}`);
    order.workpieceId = newWorkpieceId;
    const navStepsToUpdate = this.navStepsToExecute.filter(step => step.orderId === orderId);
    for (const step of navStepsToUpdate) {
      step.workpieceId = newWorkpieceId;
    }
    const manufactureStepsToUpdate = this.manufactureStepsToExecute.filter(step => step.orderId === orderId);
    for (const step of manufactureStepsToUpdate) {
      step.workpieceId = newWorkpieceId;
    }
  }

  isOrderActionRunning(orderId: string, actionId: string): boolean {
    const activeOrder = this.activeOrders.find(order => order.orderId === orderId);
    if (!activeOrder) {
      console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} no active order found`);
      return false;
    }

    const step = activeOrder.productionSteps.find(step => step.id === actionId);
    if (!step) {
      console.debug(`ORDER_MANAGEMENT: handle action update for orderId: ${orderId} no step found for id: ${actionId}`);
      return false;
    }
    return step.state == OrderState.IN_PROGRESS;
  }
}
