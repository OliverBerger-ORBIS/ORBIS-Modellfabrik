import { ModuleCommandType, ModuleType } from '../../../../common/protocol/module';
import {
  OrderManufactureStep,
  OrderNavigationStep,
  OrderRequest,
  OrderResponse,
  OrderResponseStep,
  OrderState,
} from '../../../../common/protocol/ccu';
import { generateOrderStepList, sendResponse, validateStorageOrderRequestAndReserveBay } from './index';
import { ProductionDefinition } from './flow/order-flow-service';
import { AsyncMqttClient } from 'async-mqtt';
import * as localMqtt from '../../mqtt/mqtt';
import { CcuTopic } from '../../../../common/protocol';
import { OrderManagement } from './management/order-management';
import * as stateMock from '../state';
import { StockManagementService } from './stock/stock-management-service';

describe('Test order request handling', () => {
  const MOCK_DATE = new Date('2023-05-10T07:55:58.510Z');
  beforeEach(() => {
    jest.spyOn(stateMock, 'addOrderLogEntry').mockImplementation(jest.fn());
    jest.useFakeTimers().setSystemTime(MOCK_DATE);
  });

  afterEach(() => {
    jest.clearAllMocks();
    jest.useRealTimers();
  });

  it('should convert production definition to a list of response steps', () => {
    const actionIdProduction = 'actionIdProduction';
    const actionIdNavIndependent = 'actionIdNavIndependent';
    const actionIdNavDependent = 'actionIdNavDependent';

    const navTypeIndependent: OrderNavigationStep = {
      id: actionIdNavIndependent,
      target: ModuleType.DRILL,
      source: ModuleType.START,
      state: OrderState.ENQUEUED,
      type: 'NAVIGATION',
    };

    const navTypeDependent: OrderNavigationStep = {
      id: actionIdNavDependent,
      target: ModuleType.DPS,
      source: ModuleType.DRILL,
      dependentActionId: actionIdProduction,
      state: OrderState.ENQUEUED,
      type: 'NAVIGATION',
    };

    const prodType: OrderManufactureStep = {
      id: actionIdProduction,
      dependentActionId: actionIdNavIndependent,
      command: ModuleCommandType.DRILL,
      moduleType: ModuleType.DRILL,
      state: OrderState.ENQUEUED,
      type: 'MANUFACTURE',
    };

    const prodDef: ProductionDefinition = {
      navigationSteps: [navTypeIndependent, navTypeDependent],
      productionSteps: [prodType],
    };

    const actualResponseSteps: Array<OrderResponseStep> = generateOrderStepList(prodDef);

    const expededResponseSteps: Array<OrderResponseStep> = [
      <OrderNavigationStep>{
        id: actionIdNavIndependent,
        type: 'NAVIGATION',
        target: ModuleType.DRILL,
        source: ModuleType.START,
        state: OrderState.ENQUEUED,
      },
      <OrderManufactureStep>{
        id: actionIdProduction,
        type: 'MANUFACTURE',
        moduleType: ModuleType.DRILL,
        command: ModuleCommandType.DRILL,
        dependentActionId: actionIdNavIndependent,
        state: OrderState.ENQUEUED,
      },
      <OrderNavigationStep>{
        id: actionIdNavDependent,
        type: 'NAVIGATION',
        target: ModuleType.DPS,
        source: ModuleType.DRILL,
        dependentActionId: actionIdProduction,
        state: OrderState.ENQUEUED,
      },
    ];

    expect(actualResponseSteps.length).toBe(expededResponseSteps.length);
    expect(actualResponseSteps).toEqual(expededResponseSteps);
    expect(actualResponseSteps).toStrictEqual(expededResponseSteps);

    expect(actualResponseSteps).toStrictEqual(expededResponseSteps);
  });

  it('should send the correct order response including the set workpiece id', async () => {
    const workpieceId = '04339d7adb7281';
    const type = 'WHITE';
    const storageOrderJson = `{
      "orderType": "STORAGE",
      "timestamp": "2023-05-10T07:33:16.154840Z",
      "type": "${type}",
      "workpieceId": "${workpieceId}"
    }`;
    const storageOrder: OrderRequest = JSON.parse(storageOrderJson);
    const orderId = 'order-id-123';
    const productionDefinition: ProductionDefinition = {
      navigationSteps: [],
      productionSteps: [],
    };

    const mqtt = {
      publish: () => Promise.resolve(),
    } as unknown as AsyncMqttClient;
    jest.spyOn(mqtt, 'publish');
    jest.spyOn(localMqtt, 'getMqttClient').mockReturnValue(mqtt);

    jest.mock('./management/order-management');
    jest.spyOn(OrderManagement, 'getInstance').mockReturnValue({
      cacheOrder: jest.fn().mockResolvedValue(Promise.resolve()),
    } as unknown as OrderManagement);

    await sendResponse(storageOrder, orderId, productionDefinition);

    const expectedOrderResponse: OrderResponse = {
      orderType: 'STORAGE',
      type,
      timestamp: storageOrder.timestamp,
      orderId,
      productionSteps: [],
      receivedAt: MOCK_DATE,
      state: OrderState.ENQUEUED,
      workpieceId,
    };

    expect(OrderManagement.getInstance().cacheOrder).toHaveBeenCalledWith(expectedOrderResponse);
    expect(mqtt.publish).toHaveBeenCalledWith(CcuTopic.ORDER_RESPONSE, JSON.stringify(expectedOrderResponse));
  });

  it('should validate that a storage order can be generated', async () => {
    const prodDef: ProductionDefinition = {
      navigationSteps: [{ id: 'first', source: ModuleType.START, target: ModuleType.DPS, type: 'NAVIGATION', state: OrderState.ENQUEUED }],
      productionSteps: [],
    };
    const orderRequest: OrderRequest = {
      orderType: 'STORAGE',
      type: 'RED',
      timestamp: new Date(),
      workpieceId: 'workpieceId',
    };
    jest.spyOn(StockManagementService, 'reserveEmptyBay').mockReturnValue('hbwId');
    const result = await validateStorageOrderRequestAndReserveBay(prodDef, 'orderId', orderRequest);
    expect(result).toBeTruthy();
  });

  it('should fail if a storage order has no navigation steps', async () => {
    const prodDef: ProductionDefinition = {
      navigationSteps: [],
      productionSteps: [],
    };
    const orderRequest: OrderRequest = {
      orderType: 'STORAGE',
      type: 'RED',
      timestamp: new Date(),
      workpieceId: 'workpieceId',
    };
    const result = await validateStorageOrderRequestAndReserveBay(prodDef, 'orderId', orderRequest);
    expect(result).toBeFalsy();
  });

  it('should fail if a storage order cannot be stored', async () => {
    const prodDef: ProductionDefinition = {
      navigationSteps: [{ id: 'first', source: ModuleType.START, target: ModuleType.DPS, type: 'NAVIGATION', state: OrderState.ENQUEUED }],
      productionSteps: [],
    };
    const orderRequest: OrderRequest = {
      orderType: 'STORAGE',
      type: 'RED',
      timestamp: new Date(),
      workpieceId: 'workpieceId',
    };
    jest.spyOn(StockManagementService, 'reserveEmptyBay').mockReturnValue(undefined);
    const result = await validateStorageOrderRequestAndReserveBay(prodDef, 'orderId', orderRequest);
    expect(result).toBeFalsy();
  });
});
