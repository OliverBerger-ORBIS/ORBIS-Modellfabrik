import { IClientSubscribeOptions } from 'async-mqtt';
import { CcuTopic, OrderRequest, OrderResponse } from '../../../../common/protocol';
import { getMqttClient } from '../../mqtt/mqtt';
import { addOrderLogEntry } from '../state';
import { AvailableState, OrderManufactureStep, OrderNavigationStep, OrderState } from '../../../../common/protocol/ccu';
import { OrderManagement } from './management/order-management';
import { v4 as uuid } from 'uuid';
import { jsonIsoDateReviver } from '../../../../common/util/json.revivers';
import { PairingStates } from '../pairing/pairing-states';
import { ModuleType } from '../../../../common/protocol/module';
import { OrderFlowService, ProductionDefinition } from './flow/order-flow-service';
import { publishStock } from '../production/cloud-stock';
import { StockManagementService } from './stock/stock-management-service';
import { sendCancelStorageOrder } from '../production/production';

export const generateOrderStepList = (productionDefinition: ProductionDefinition): Array<OrderNavigationStep | OrderManufactureStep> => {
  let orderNavSteps: Array<OrderNavigationStep> = [];
  if (!!productionDefinition.navigationSteps) {
    orderNavSteps = productionDefinition.navigationSteps;
  }
  const orderProductionSteps: Array<OrderManufactureStep> = productionDefinition.productionSteps;
  const orderResponseSteps: Array<OrderNavigationStep | OrderManufactureStep> = [...orderNavSteps, ...orderProductionSteps];
  return sortOrderSteps(orderResponseSteps);
};

/** Sort a list of Array<OrderNavigationStep | OrderManufactureStep> where the fist element has no dependentActionId and every other element as the id from the previous as dependentActionId */
export const sortOrderSteps = (
  orderSteps: Array<OrderNavigationStep | OrderManufactureStep>,
): Array<OrderNavigationStep | OrderManufactureStep> => {
  const resultList: Array<OrderNavigationStep | OrderManufactureStep> = [];
  const indepenentIds: string[] = [];
  const dependentSteps: Array<OrderNavigationStep | OrderManufactureStep> = [];

  orderSteps.forEach(step => {
    if (!step.dependentActionId) {
      indepenentIds.push(step.id);
      resultList.push(step);
    } else {
      dependentSteps.push(step);
    }
  });

  indepenentIds.forEach(actionId => {
    let nextStep = findNextDependentStep(actionId, dependentSteps);
    while (!!nextStep) {
      resultList.push(nextStep);
      nextStep = findNextDependentStep(nextStep.id, dependentSteps);
    }
  });

  return resultList;
};

const findNextDependentStep = (
  actionId: string,
  orderSteps: Array<OrderNavigationStep | OrderManufactureStep>,
): OrderNavigationStep | OrderManufactureStep | undefined => {
  return orderSteps.find(nextStep => {
    return nextStep.dependentActionId === actionId;
  });
};

/**
 * Confirm the order by publishing a response to the mqtt topic /ccu/order/response
 * @param orderRequest the request that was received
 * @param orderId the generated order id
 * @param productionDefinition the production definition that was generated for the order
 */
export const sendResponse = async (
  orderRequest: OrderRequest,
  orderId: string,
  productionDefinition: ProductionDefinition,
): Promise<void> => {
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
    requestId: orderRequest.requestId,
  };

  await OrderManagement.getInstance().cacheOrder(response);
  console.debug('Confirm order: ', orderId);
  // TODO: What happens if this is null?
  await addOrderLogEntry(response);

  const mqtt = getMqttClient();
  return mqtt.publish(CcuTopic.ORDER_RESPONSE, JSON.stringify(response));
};

export const TOPICS: string[] = [CcuTopic.ORDER_REQUEST];
export const TOPIC_OPTIONS: IClientSubscribeOptions = {
  qos: 2,
};

export const TOPICS_CANCEL_ORDER: string[] = [CcuTopic.CANCEL_ORDERS];
export const TOPIC_OPTIONS_CANCEL_ORDER: IClientSubscribeOptions = {
  qos: 2,
};

/**
 * Setting the DPS for a specific order to ready.
 * This is done to block it from any new orders, since the workpiece is still on the DPS, and it cannot process a new one
 * @param orderId the order id enable the DPS for
 */
const setDpsReadyForOrder = async (orderId: string): Promise<void> => {
  const paringStates = PairingStates.getInstance();
  const dps = paringStates.getForModuleType(ModuleType.DPS);
  if (!dps) {
    return;
  }

  await paringStates.updateAvailability(dps.serialNumber, AvailableState.READY, orderId);
};

/**
 * Validate a storage order request and try to reserve an empty storage bay.
 * @param productionDef
 * @param orderId
 * @param orderRequest
 * @return boolean that indicates the success of validation and bay reservation
 */
export const validateStorageOrderRequestAndReserveBay = async (
  productionDef: ProductionDefinition,
  orderId: string,
  orderRequest: OrderRequest,
) => {
  if (!productionDef.navigationSteps?.length) {
    console.error('Storage order has no navigation steps configured, aborting ...');
    return false;
  } else if (!StockManagementService.reserveEmptyBay(orderId, orderRequest.type)) {
    console.error('No empty storage bay available to create storage order for ' + orderRequest.type);
    return false;
  }
  return true;
};

/**
 * Handles all incoming order messages and responds on the respective response topic
 * @param message
 */
export const handleMessage = async (message: string): Promise<void> => {
  const orderId = uuid();
  const orderRequest: OrderRequest = JSON.parse(message, jsonIsoDateReviver);

  // load the production definition to trigger following actions
  const isProductionOrder = orderRequest.orderType === 'PRODUCTION';
  let productionDef: ProductionDefinition;
  if (isProductionOrder) {
    productionDef = OrderFlowService.getProductionDefinition(orderRequest.type);
    if (!productionDef.navigationSteps) {
      console.error('Production order has no navigation steps configured, aborting ...');
      return;
    } else if (!StockManagementService.reserveWorkpiece(orderId, orderRequest.type)) {
      const warehouses = StockManagementService.getWarehouses();
      const stockItems = StockManagementService.getStock();
      console.error(
        `No workpiece available for ${orderRequest.type} - warehouses: [${warehouses.join(', ')}] stockItems: ${stockItems.length}`,
      );
      return;
    }
  } else {
    // FITEFF22-592 Require empty HBW position. Send an instantAction to the DPS to discard the workpiece if the warehouse is full
    productionDef = OrderFlowService.getStorageProductionDefinition();
    const valid = await validateStorageOrderRequestAndReserveBay(productionDef, orderId, orderRequest);
    if (!valid) {
      // send the cancel request to have the DPS discard the workpiece when it cannot be stored
      await sendCancelStorageOrder(PairingStates.getInstance().getAllReady(ModuleType.DPS)[0]?.serialNumber);
      return;
    }
    // set the dps to blocked for any new order, because a workpiece is still on it
    await setDpsReadyForOrder(orderId);
  }

  await sendResponse(orderRequest, orderId, productionDef);
  await publishStock();
};

export const handleCancelOrders = async (message: string): Promise<void> => {
  const orderIds: string[] = JSON.parse(message, jsonIsoDateReviver);

  await OrderManagement.getInstance().cancelOrders(orderIds);
};

export default handleMessage;
