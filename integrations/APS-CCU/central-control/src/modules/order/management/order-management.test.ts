import { AsyncMqttClient } from 'async-mqtt';
import { CcuTopic, OrderRequest, OrderResponse } from '../../../../../common/protocol';
import {
  AvailableState,
  FtsPairedModule,
  OrderManufactureStep,
  OrderNavigationStep,
  OrderState,
  PairedModule,
} from '../../../../../common/protocol/ccu';
import {
  DeliveryMetadata,
  DurationMetadata,
  HistoryPoint,
  ModuleCommandType,
  ModuleType,
  QualityResult,
  StoreMetadata,
} from '../../../../../common/protocol/module';
import { State } from '../../../../../common/protocol/vda';
import { FtsPathResult } from '../../../models/models';
import { createMockMqttClient } from '../../../test-helpers';
import * as navCommandSender from '../../fts/navigation/navigation';
import { NavigatorService, Path } from '../../fts/navigation/navigator-service';
import { FtsPairingStates } from '../../pairing/fts-pairing-states';
import { PairingStates } from '../../pairing/pairing-states';
import * as productionHelper from '../../production/helper';
import * as moduleCommandSender from '../../production/production';
import { StockManagementService } from '../stock/stock-management-service';
import { OrderManagement, OrderManagementAction } from './order-management';

describe('Test order management handling', () => {
  const MOCKED_DATE = new Date('2021-01-01T00:00:00.000Z');
  const MOCKED_PATH: Path = { path: [1], distance: 1 };
  const MOCKED_MODULE_SERIAL = 'mockedSerial';
  const MOCKED_MODULE = {
    serialNumber: MOCKED_MODULE_SERIAL,
  };
  let underTest: OrderManagement;
  let mqtt: AsyncMqttClient;

  beforeEach(() => {
    mqtt = createMockMqttClient();
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockResolvedValue();
    jest.spyOn(navCommandSender, 'sendClearModuleNodeNavigationRequest').mockRejectedValue('Tests should not try to clear a module.');
    jest.spyOn(moduleCommandSender, 'sendProductionCommand').mockResolvedValue();
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue(undefined);
    jest.spyOn(NavigatorService, 'getFTSPath').mockReturnValue(MOCKED_PATH);
    jest.useFakeTimers().setSystemTime(MOCKED_DATE);
    jest.mock('../../pairing/fts-pairing-states');
    FtsPairingStates.getInstance().getAllReadyUnassigned = jest.fn().mockReturnValue([]);
    FtsPairingStates.getInstance().getReady = jest.fn();
    PairingStates.getInstance().getReadyForModuleType = jest.fn().mockReturnValue({ serialNumber: MOCKED_MODULE_SERIAL });
    PairingStates.getInstance().isReadyForOrder = jest.fn().mockReturnValue(true);
    underTest = OrderManagement.getInstance();
    StockManagementService.reset();

    jest.mock('../../production/helper');
  });

  afterEach(() => {
    // resetting the singleton for clean tests
    underTest['orderQueue'] = new Array<OrderResponse>();
    underTest['activeOrders'] = [];
    underTest['completedOrders'] = [];
    underTest['navStepsToExecute'] = [];
    underTest['manufactureStepsToExecute'] = [];
    FtsPairingStates.getInstance().reset();
    jest.resetAllMocks();
    jest.restoreAllMocks();
    jest.useRealTimers();
  });

  it('should return instance when undefined', () => {
    expect(underTest).toBeDefined();
  });

  it('should send an order list update and start the first action when there is not an active order and stock is available', async () => {
    const orderId = 'orderId';
    const workpiece = 'BLUE';
    const workpieceId = 'workpieceId';
    const navStep: OrderNavigationStep = {
      id: 'navStepId',
      state: OrderState.ENQUEUED,
      type: 'NAVIGATION',
      target: ModuleType.DPS,
      source: ModuleType.DRILL,
    };
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      id: 'prodStepId',
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DRILL,
    };
    const orderResponse: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [navStep, prodStep],
      state: OrderState.ENQUEUED,
      workpieceId,
    };

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
    };
    FtsPairingStates.getInstance().getReady = jest.fn().mockReturnValue(fts);
    jest.spyOn(underTest, 'chooseReadyFtsForStep').mockReturnValue({ fts, path: MOCKED_PATH });
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue('hbwSerial');

    await underTest.cacheOrder(orderResponse);

    const expectedNavStep: OrderNavigationStep = {
      id: 'navStepId',
      state: OrderState.IN_PROGRESS,
      type: 'NAVIGATION',
      target: ModuleType.DPS,
      source: ModuleType.DRILL,
      startedAt: MOCKED_DATE,
    };
    const expectedProdStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: 'prodStepId',
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DRILL,
      startedAt: MOCKED_DATE,
      serialNumber: MOCKED_MODULE_SERIAL,
    };
    const expectedOrderResponse: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [expectedNavStep, expectedProdStep],
      state: OrderState.IN_PROGRESS,
      workpieceId,
      startedAt: MOCKED_DATE,
    };

    const metadata: StoreMetadata = {
      type: workpiece,
      workpieceId,
    };

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId, MOCKED_MODULE_SERIAL, expect.anything());
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      navStep,
      orderId,
      0,
      workpiece,
      workpieceId,
      fts,
      MOCKED_MODULE_SERIAL,
    );
    expect(moduleCommandSender.sendProductionCommand).toHaveBeenCalledWith(prodStep, orderId, 1, MOCKED_MODULE, metadata);
    expect(mqtt.publish).toHaveBeenCalledWith(CcuTopic.ACTIVE_ORDERS, JSON.stringify([expectedOrderResponse]), {
      qos: 2,
      retain: true,
    });
  });

  it('should not start the production if there are already 3 orders is already active', async () => {
    const activeOrder1: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'orderId',
      type: 'BLUE',
      timestamp: MOCKED_DATE,
      productionSteps: [
        {
          id: 'navStepId',
          state: OrderState.ENQUEUED,
          type: 'NAVIGATION',
          target: ModuleType.DPS,
          source: ModuleType.DRILL,
        },
      ],
      state: OrderState.IN_PROGRESS,
      startedAt: MOCKED_DATE,
      workpieceId: 'workpieceId',
    };
    const activeOrder2: OrderResponse = { ...activeOrder1, orderId: 'orderId2' };
    const activeOrder3: OrderResponse = { ...activeOrder1, orderId: 'orderId3' };

    underTest['activeOrders'] = [activeOrder1, activeOrder2, activeOrder3];
    underTest['orderQueue'] = [activeOrder1, activeOrder2, activeOrder3];

    const secondOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'orderId2',
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      workpieceId: 'workpieceId',
      productionSteps: [
        {
          id: 'navStepId',
          state: OrderState.ENQUEUED,
          type: 'NAVIGATION',
          target: ModuleType.DPS,
          source: ModuleType.DRILL,
        },
      ],
      state: OrderState.ENQUEUED,
      startedAt: MOCKED_DATE,
    };

    await underTest.cacheOrder(secondOrder);

    expect(navCommandSender.sendNavigationRequest).not.toHaveBeenCalled();
    expect(moduleCommandSender.sendProductionCommand).not.toHaveBeenCalled();
    expect(mqtt.publish).toHaveBeenCalledWith(
      CcuTopic.ACTIVE_ORDERS,
      JSON.stringify([activeOrder1, activeOrder2, activeOrder3, secondOrder]),
      {
        qos: 2,
        retain: true,
      },
    );
  });

  it('should start the next action when the previous one is finished', async () => {
    const orderId = 'orderId';
    const navStepId = 'navStepId';
    const workpiece = 'BLUE';
    const navStep: OrderNavigationStep = {
      id: navStepId,
      state: OrderState.ENQUEUED,
      type: 'NAVIGATION',
      target: ModuleType.DPS,
      source: ModuleType.DRILL,
    };
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      id: 'prodStepId',
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DRILL,
      dependentActionId: navStepId,
    };
    const activeOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [navStep, prodStep],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };

    underTest['activeOrders'] = [activeOrder];
    underTest['orderQueue'] = [activeOrder];

    await underTest.handleActionUpdate(orderId, navStepId, State.FINISHED);

    const expectedNavStep: OrderNavigationStep = {
      id: navStepId,
      state: OrderState.FINISHED,
      type: 'NAVIGATION',
      target: ModuleType.DPS,
      source: ModuleType.DRILL,
      stoppedAt: MOCKED_DATE,
    };
    const expectedProdStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: 'prodStepId',
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DRILL,
      dependentActionId: navStepId,
      startedAt: MOCKED_DATE,
      serialNumber: MOCKED_MODULE_SERIAL,
    };
    const expectedActiveOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [expectedNavStep, expectedProdStep],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };

    const metadata: StoreMetadata = {
      type: workpiece,
      workpieceId: 'workpieceId',
    };

    expect(moduleCommandSender.sendProductionCommand).toHaveBeenCalledWith(expectedProdStep, orderId, 1, MOCKED_MODULE, metadata);
    expect(mqtt.publish).toHaveBeenCalledWith(CcuTopic.ACTIVE_ORDERS, JSON.stringify([expectedActiveOrder]), {
      qos: 2,
      retain: true,
    });
  });

  it('should start the next order when the previous orders last action is finished and stock is available', async () => {
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue('hbwSerial');
    const orderId = 'orderId';
    const orderIdActive = 'orderIdActive';
    const navStepId = 'navStepId';
    const workpiece = 'WHITE';
    const navStep: OrderNavigationStep = {
      id: navStepId,
      state: OrderState.ENQUEUED,
      type: 'NAVIGATION',
      target: ModuleType.DPS,
      source: ModuleType.DRILL,
    };
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      id: 'prodStepId',
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DRILL,
    };
    const activeOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderIdActive,
      type: 'BLUE',
      timestamp: MOCKED_DATE,
      productionSteps: [navStep],
      state: OrderState.IN_PROGRESS,
      workpieceId: 'workpieceId',
    };

    const nextOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [prodStep],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };

    underTest['activeOrders'] = [activeOrder];
    underTest['orderQueue'] = [activeOrder, nextOrder];

    await underTest.handleActionUpdate(orderIdActive, navStepId, State.FINISHED);

    const expectedProdStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: 'prodStepId',
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DRILL,
      startedAt: MOCKED_DATE,
      serialNumber: MOCKED_MODULE_SERIAL,
    };
    const expectedCompletedOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderIdActive,
      type: 'BLUE',
      timestamp: MOCKED_DATE,
      productionSteps: [navStep],
      state: OrderState.FINISHED,
      workpieceId: 'workpieceId',
      stoppedAt: MOCKED_DATE,
    };
    const expectedActiveOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [expectedProdStep],
      state: OrderState.IN_PROGRESS,
      workpieceId: 'workpieceId',
      startedAt: MOCKED_DATE,
    };

    const metadata: StoreMetadata = {
      type: workpiece,
      workpieceId: 'workpieceId',
    };

    expect(moduleCommandSender.sendProductionCommand).toHaveBeenCalledWith(expectedProdStep, orderId, 0, MOCKED_MODULE, metadata);
    expect(mqtt.publish).toHaveBeenCalledWith(CcuTopic.ACTIVE_ORDERS, JSON.stringify([expectedActiveOrder]), {
      qos: 2,
      retain: true,
    });
    expect(mqtt.publish).toHaveBeenCalledWith(CcuTopic.COMPLETED_ORDERS, JSON.stringify([expectedCompletedOrder]), {
      qos: 2,
      retain: true,
    });
  });

  it('should not send any order update on reset if the order id is not present', async () => {
    const order: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'orderIdPresent',
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };
    underTest['orderQueue'] = [order];

    await underTest.resetOrder('orderIdNotPresent');

    expect(mqtt.publish).not.toHaveBeenCalled();
  });

  it('should not send any order update on reset if order queue is empty', async () => {
    underTest['orderQueue'] = [];

    await underTest.resetOrder('orderIdNotPresent');

    expect(mqtt.publish).not.toHaveBeenCalled();
  });

  it('should not reset an order if there is not active order', async () => {
    const orderId = 'orderIdPresent';

    underTest['orderQueue'] = [];
    underTest['activeOrders'] = [];

    await underTest.resetOrder(orderId);

    expect(mqtt.publish).not.toHaveBeenCalled();
  });

  it('should reset the active order and start the next from the queue when stock is available', async () => {
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue('hbwSerial');
    const orderId = 'orderIdPresent';
    const orderToReset: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };
    const order1: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'order1',
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };
    const order2: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'order2',
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };
    const order3: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'order2',
      type: 'WHITE',
      workpieceId: 'workpieceId',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.ENQUEUED,
    };

    const actualOrderQueue = [orderToReset, order3, order1, order2];
    underTest['orderQueue'] = actualOrderQueue;
    underTest['activeOrders'] = [orderToReset];

    await underTest.resetOrder(orderId);

    const activeOrder = {
      ...order3,
      state: OrderState.IN_PROGRESS,
    };
    const expectedOrderQueue = [activeOrder, order1, order2];

    expect(actualOrderQueue).toStrictEqual(expectedOrderQueue);
    expect(mqtt.publish).toHaveBeenCalledWith(CcuTopic.ACTIVE_ORDERS, JSON.stringify(expectedOrderQueue), {
      qos: 2,
      retain: true,
    });
  });

  it('should reset a non-active order', async () => {
    const orderId = 'orderIdPresent';
    const orderToReset: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };
    const order1: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'order1',
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };
    const order2: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'order2',
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };
    const order3: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'order2',
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };

    const actualOrderQueue = [order3, orderToReset, order1, order2];
    underTest['orderQueue'] = actualOrderQueue;
    underTest['activeOrders'] = [order3];

    const expectedOrderQueue = [order3, orderToReset, order1, order2];
    await underTest.resetOrder(orderId);

    expect(actualOrderQueue).toStrictEqual(expectedOrderQueue);
    expect(mqtt.publish).not.toHaveBeenCalled();
  });

  it('should not delete the active order', async () => {
    const orderId = 'orderIdPresent';
    const activeOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.IN_PROGRESS,
      workpieceId: 'workpieceId',
    };

    const orderQueue = [activeOrder];
    underTest['orderQueue'] = orderQueue;
    underTest['activeOrders'] = [activeOrder];

    await underTest.cancelOrders([orderId]);
    expect(mqtt.publish).toHaveBeenCalledWith(CcuTopic.ACTIVE_ORDERS, JSON.stringify([activeOrder]), {
      qos: 2,
      retain: true,
    });
    expect(orderQueue).toStrictEqual([activeOrder]);
  });

  it('should delete none active orders', async () => {
    const orderIdToDelete1 = 'orderIdToDelete1';
    const orderIdToDelete2 = 'orderIdToDelete2';
    const activeOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'orderIdPresent',
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.IN_PROGRESS,
      workpieceId: 'workpieceId',
    };

    const orderToDelete1: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderIdToDelete1,
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };
    const orderToDelete2: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderIdToDelete2,
      type: 'WHITE',
      timestamp: MOCKED_DATE,
      productionSteps: [],
      state: OrderState.ENQUEUED,
      workpieceId: 'workpieceId',
    };

    const orderQueue = [activeOrder, orderToDelete1, orderToDelete2];
    underTest['orderQueue'] = orderQueue;
    underTest['activeOrders'] = [activeOrder];

    await underTest.cancelOrders([orderIdToDelete1, orderIdToDelete2]);
    expect(mqtt.publish).toHaveBeenCalledWith(CcuTopic.ACTIVE_ORDERS, JSON.stringify([activeOrder]), {
      qos: 2,
      retain: true,
    });
    expect(orderQueue).toStrictEqual([activeOrder]);
  });

  it('should detect a failed quality check result', () => {
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: 'prodStepId',
      moduleType: ModuleType.AIQS,
      command: ModuleCommandType.CHECK_QUALITY,
    };
    expect(underTest.isQualityCheckFailure(prodStep, QualityResult.FAILED)).toBe(true);
  });

  it('should not erroneously detect a failed quality check result', () => {
    const prodStepA: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: 'prodStepId',
      moduleType: ModuleType.AIQS,
      command: ModuleCommandType.CHECK_QUALITY,
    };
    const prodStepB: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: 'prodStepId',
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.CHECK_QUALITY,
    };
    const prodStepC: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: 'prodStepId',
      moduleType: ModuleType.AIQS,
      command: ModuleCommandType.DRILL,
    };
    const prodStepD: OrderNavigationStep = {
      type: 'NAVIGATION',
      state: OrderState.IN_PROGRESS,
      id: 'navStepId',
      target: ModuleType.AIQS,
      source: ModuleType.AIQS,
    };

    expect(underTest.isQualityCheckFailure(prodStepA)).toBe(false);
    expect(underTest.isQualityCheckFailure(prodStepA, QualityResult.PASSED)).toBe(false);
    expect(underTest.isQualityCheckFailure(prodStepA, '')).toBe(false);

    expect(underTest.isQualityCheckFailure(prodStepB, QualityResult.FAILED)).toBe(false);
    expect(underTest.isQualityCheckFailure(prodStepC, QualityResult.FAILED)).toBe(false);
    expect(underTest.isQualityCheckFailure(prodStepD, QualityResult.FAILED)).toBe(false);
  });

  it('should try to create a new order when the quality check fails', async () => {
    const configSpy = jest.spyOn(OrderManagement.getInstance(), 'createOrder').mockResolvedValue(null);

    const orderId = 'orderId';
    const navStepId = 'navStepId';
    const prodStepId = 'prodStepId';
    const workpiece = 'BLUE';
    const workpieceId = 'workpieceId';
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: prodStepId,
      moduleType: ModuleType.AIQS,
      command: ModuleCommandType.CHECK_QUALITY,
      startedAt: MOCKED_DATE,
    };
    const navStep: OrderNavigationStep = {
      id: navStepId,
      state: OrderState.ENQUEUED,
      type: 'NAVIGATION',
      target: ModuleType.DPS,
      source: ModuleType.AIQS,
      dependentActionId: prodStepId,
    };
    const activeOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [prodStep, navStep],
      state: OrderState.IN_PROGRESS,
      startedAt: MOCKED_DATE,
      workpieceId,
    };

    underTest['activeOrders'] = [activeOrder];
    underTest['orderQueue'] = [activeOrder];

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
    };
    FtsPairingStates.getInstance().getReady = jest.fn().mockReturnValue(fts);
    jest.spyOn(underTest, 'chooseReadyFtsForStep').mockReturnValue({ fts, path: MOCKED_PATH });

    await underTest.handleActionUpdate(orderId, prodStepId, State.FINISHED, QualityResult.FAILED);

    const expectedProdStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.ERROR,
      id: prodStepId,
      moduleType: ModuleType.AIQS,
      command: ModuleCommandType.CHECK_QUALITY,
      startedAt: MOCKED_DATE,
      stoppedAt: MOCKED_DATE,
    };
    const expectedNavStep: OrderNavigationStep = {
      id: navStepId,
      state: OrderState.CANCELLED,
      type: 'NAVIGATION',
      target: ModuleType.DPS,
      source: ModuleType.AIQS,
      dependentActionId: prodStepId,
    };
    const expectedActiveOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [expectedProdStep, expectedNavStep],
      state: OrderState.ERROR,
      startedAt: MOCKED_DATE,
      workpieceId: workpieceId,
      stoppedAt: MOCKED_DATE,
    };

    expect(configSpy).toHaveBeenCalledWith(<OrderRequest>{
      type: workpiece,
      timestamp: MOCKED_DATE,
      orderType: 'PRODUCTION',
    });
    expect(mqtt.publish).toHaveBeenNthCalledWith(1, CcuTopic.COMPLETED_ORDERS, JSON.stringify([expectedActiveOrder]), {
      qos: 2,
      retain: true,
    });
    // The testcase does not create a new order, only checks if the function to create a new order is called
    expect(mqtt.publish).toHaveBeenNthCalledWith(3, CcuTopic.ACTIVE_ORDERS, JSON.stringify([]), {
      qos: 2,
      retain: true,
    });
  });

  it('should return the target for a navigation action id', async () => {
    const orderId = 'orderId';
    const workpiece = 'BLUE';
    const navStepId = 'navStepId';
    const targetModule = ModuleType.DRILL;
    const navStep: OrderNavigationStep = {
      id: navStepId,
      state: OrderState.ENQUEUED,
      type: 'NAVIGATION',
      source: ModuleType.START,
      target: targetModule,
    };
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      id: 'prodStepId',
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DRILL,
      dependentActionId: navStepId,
    };
    const orderResponse: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [navStep, prodStep],
      state: OrderState.IN_PROGRESS,
      startedAt: new Date(),
      workpieceId: 'workpieceId',
    };
    underTest['activeOrders'] = [orderResponse];
    underTest['orderQueue'] = [orderResponse];

    expect(underTest.getTargetModuleTypeForNavActionId(navStepId)).toEqual(targetModule);
  });

  it('should return the order id for a workpiece id', async () => {
    const orderId = 'orderId';
    const workpieceId = 'wpId';
    const navStepId = 'navStepId';
    const targetModule = ModuleType.DRILL;
    const navStep: OrderNavigationStep = {
      id: navStepId,
      state: OrderState.ENQUEUED,
      type: 'NAVIGATION',
      source: ModuleType.START,
      target: targetModule,
    };
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      id: 'prodStepId',
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DRILL,
      dependentActionId: navStepId,
    };
    const orderResponse: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: 'BLUE',
      timestamp: MOCKED_DATE,
      productionSteps: [navStep, prodStep],
      state: OrderState.IN_PROGRESS,
      startedAt: new Date(),
      workpieceId,
    };
    underTest['activeOrders'] = [orderResponse];
    underTest['orderQueue'] = [orderResponse];

    expect(underTest.getOrderForWorkpieceId(workpieceId)).toEqual(orderId);
  });

  it('should not return the target for manufacturing steps', async () => {
    const orderId = 'orderId';
    const workpiece = 'BLUE';
    const prodStepId = 'prodStepId';
    const navStepId = 'navStepId';
    const targetModule = ModuleType.DPS;
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      id: prodStepId,
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DRILL,
    };
    const navStep: OrderNavigationStep = {
      id: navStepId,
      state: OrderState.ENQUEUED,
      type: 'NAVIGATION',
      source: ModuleType.DRILL,
      target: targetModule,
      dependentActionId: prodStepId,
    };
    const orderResponse: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [navStep, prodStep],
      state: OrderState.IN_PROGRESS,
      startedAt: new Date(),
      workpieceId: 'workpieceId',
    };
    underTest['activeOrders'] = [orderResponse];
    underTest['orderQueue'] = [orderResponse];
    expect(underTest.getTargetModuleTypeForNavActionId(prodStepId)).toBeUndefined();
  });

  it('should start the next navigation step in the queue', async () => {
    const orderId1 = 'orderId1';
    const state1 = State.FINISHED;
    const workpiece1 = 'BLUE';
    const workpieceId1 = 'workpieceId1';
    const navStep1Order1Id = 'navStep1Order1';
    const navStep2Order1Id = 'navStep2Order1';

    const navStep1Order1: OrderNavigationStep = {
      id: navStep1Order1Id,
      type: 'NAVIGATION',
      target: ModuleType.DRILL,
      state: OrderState.IN_PROGRESS,
      source: ModuleType.START,
    };
    const navStep2Order1: OrderNavigationStep = {
      id: navStep2Order1Id,
      type: 'NAVIGATION',
      target: ModuleType.DRILL,
      state: OrderState.ENQUEUED,
      source: ModuleType.START,
      dependentActionId: navStep1Order1Id,
    };

    const order1: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId1,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId1,
      type: workpiece1,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStep1Order1, navStep2Order1],
    };

    const orderId2 = 'orderId2';
    const workpiece2 = 'WHITE';
    const workpieceId2 = 'workpieceId2';
    const navStepOrder2Id = 'navStepOrder2';

    const navStepOrder2: OrderNavigationStep = {
      id: navStepOrder2Id,
      type: 'NAVIGATION',
      target: ModuleType.DRILL,
      state: OrderState.ENQUEUED,
      source: ModuleType.START,
    };

    const navStepOrder2Action: OrderManagementAction = {
      index: 0,
      workpieceId: workpieceId2,
      workpiece: workpiece2,
      value: navStepOrder2,
      orderId: orderId2,
    };

    const order2: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId2,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId2,
      type: workpiece2,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStepOrder2],
    };

    underTest['activeOrders'] = [order1, order2];
    underTest['orderQueue'] = [order1, order2];
    underTest['navStepsToExecute'] = [navStepOrder2Action];

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
    };
    let ftsIsBusy = false;
    jest.spyOn(underTest, 'chooseReadyFtsForStep').mockImplementation(() => (ftsIsBusy ? undefined : { fts, path: MOCKED_PATH }));
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockImplementation(() => {
      ftsIsBusy = true;
      return Promise.resolve();
    });

    await underTest.handleActionUpdate(orderId1, navStep1Order1Id, state1);

    const navStep2Order1Action: OrderManagementAction = {
      index: 1,
      workpieceId: workpieceId1,
      workpiece: workpiece1,
      value: navStep2Order1,
      orderId: orderId1,
    };

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId2, MOCKED_MODULE_SERIAL, expect.anything());
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      navStepOrder2,
      orderId2,
      navStepOrder2Action.index,
      workpiece2,
      workpieceId2,
      fts,
      MOCKED_MODULE_SERIAL,
    );
    expect(underTest['navStepsToExecute']).toEqual([navStep2Order1Action]);
  });

  it('should skip the next navigation step in the order and try to send the following DROP command if the FTS is docked', async () => {
    const orderId1 = 'orderId1';
    const state1 = State.FINISHED;
    const workpiece1 = 'BLUE';
    const workpieceId1 = 'workpieceId1';
    const navStep1Order1Id = 'navStep1Order1';
    const pickStepOrder1Id = 'pickStepOrder1';

    const navStep1Order1: OrderNavigationStep = {
      id: navStep1Order1Id,
      type: 'NAVIGATION',
      target: ModuleType.HBW,
      state: OrderState.FINISHED,
      source: ModuleType.START,
    };
    const pickStepOrder1: OrderManufactureStep = {
      id: pickStepOrder1Id,
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      moduleType: ModuleType.HBW,
      command: ModuleCommandType.PICK,
      dependentActionId: navStep1Order1Id,
    };

    const order1: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId1,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId1,
      type: workpiece1,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStep1Order1, pickStepOrder1],
    };

    const orderId2 = 'orderId2';
    const workpiece2 = 'WHITE';
    const workpieceId2 = undefined;
    const navStepOrder2Id = 'navStepOrder2';
    const metadataOrder2: StoreMetadata = {
      type: workpiece2,
      workpieceId: workpieceId2,
    };

    const navStepOrder2: OrderNavigationStep = {
      id: navStepOrder2Id,
      type: 'NAVIGATION',
      target: ModuleType.HBW,
      state: OrderState.ENQUEUED,
      source: ModuleType.START,
    };
    const dropStepOrder2: OrderManufactureStep = {
      id: navStepOrder2Id,
      type: 'MANUFACTURE',
      moduleType: ModuleType.HBW,
      command: ModuleCommandType.DROP,
      dependentActionId: navStepOrder2Id,
      state: OrderState.ENQUEUED,
    };

    const navStepOrder2Action: OrderManagementAction = {
      index: 0,
      workpieceId: workpieceId2,
      workpiece: workpiece2,
      value: navStepOrder2,
      orderId: orderId2,
    };

    const order2: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId2,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId2,
      type: workpiece2,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStepOrder2, dropStepOrder2],
    };

    underTest['activeOrders'] = [order1, order2];
    underTest['orderQueue'] = [order1, order2];
    underTest['navStepsToExecute'] = [navStepOrder2Action];

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
      lastLoadPosition: '2',
    };
    const module: PairedModule = {
      serialNumber: 'module',
      type: 'MODULE',
      subType: ModuleType.HBW,
    };
    let ftsIsBusy = false;
    jest.spyOn(PairingStates.getInstance(), 'getModuleForOrder').mockReturnValue(module);
    jest.spyOn(PairingStates.getInstance(), 'getReadyForModuleType').mockReturnValue(module);
    jest
      .spyOn(underTest, 'chooseReadyFtsForStep')
      .mockImplementation(() => (ftsIsBusy ? undefined : <FtsPathResult>{ fts, path: { path: [1], distance: 0 } }));
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockImplementation(() => {
      ftsIsBusy = true;
      return Promise.resolve();
    });
    jest.spyOn(moduleCommandSender, 'sendProductionCommand').mockImplementation(() => {
      return Promise.reject();
    });
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue('hbwSerial');
    jest.spyOn(StockManagementService, 'reserveWorkpiece').mockReturnValue('hbwSerial');

    await underTest.handleActionUpdate(orderId1, pickStepOrder1Id, state1);

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId2, module.serialNumber, expect.anything());
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      expect.anything(),
      orderId2,
      0,
      workpiece2,
      workpieceId2,
      fts,
      module.serialNumber,
    );
    expect(moduleCommandSender.sendProductionCommand).not.toHaveBeenCalledWith(dropStepOrder2, orderId2, 1, module, metadataOrder2);
    expect(underTest['navStepsToExecute']).toEqual([]);
    expect(underTest['manufactureStepsToExecute']).toEqual([]);
  });

  it('should skip the next navigation step during retriggerFTSSteps and try to send the following DROP command if an FTS is docked', async () => {
    const orderId2 = 'orderId2';
    const workpiece2 = 'WHITE';
    const workpieceId2 = undefined;
    const navStepOrder2Id = 'navStepOrder2';
    const metadataOrder2: StoreMetadata = {
      type: workpiece2,
      workpieceId: workpieceId2,
    };

    const navStepOrder2: OrderNavigationStep = {
      id: navStepOrder2Id,
      type: 'NAVIGATION',
      target: ModuleType.HBW,
      state: OrderState.ENQUEUED,
      source: ModuleType.START,
    };
    const dropStepOrder2: OrderManufactureStep = {
      id: navStepOrder2Id,
      type: 'MANUFACTURE',
      moduleType: ModuleType.HBW,
      command: ModuleCommandType.DROP,
      dependentActionId: navStepOrder2Id,
      state: OrderState.ENQUEUED,
    };

    const navStepOrder2Action: OrderManagementAction = {
      index: 0,
      workpieceId: workpieceId2,
      workpiece: workpiece2,
      value: navStepOrder2,
      orderId: orderId2,
    };

    const order2: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId2,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId2,
      type: workpiece2,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStepOrder2, dropStepOrder2],
    };

    underTest['activeOrders'] = [order2];
    underTest['orderQueue'] = [order2];
    underTest['navStepsToExecute'] = [navStepOrder2Action];

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
      lastLoadPosition: '2',
    };
    const module: PairedModule = {
      serialNumber: 'module',
      type: 'MODULE',
      subType: ModuleType.HBW,
    };
    let ftsIsBusy = false;
    jest.spyOn(PairingStates.getInstance(), 'getModuleForOrder').mockReturnValue(module);
    jest.spyOn(PairingStates.getInstance(), 'getReadyForModuleType').mockReturnValue(module);
    jest
      .spyOn(underTest, 'chooseReadyFtsForStep')
      .mockImplementation(() => (ftsIsBusy ? undefined : <FtsPathResult>{ fts, path: { path: [1], distance: 0 } }));
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockImplementation(() => {
      ftsIsBusy = true;
      return Promise.resolve();
    });
    jest.spyOn(moduleCommandSender, 'sendProductionCommand').mockImplementation(() => {
      return Promise.reject();
    });
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue('hbwSerial');
    jest.spyOn(StockManagementService, 'reserveWorkpiece').mockReturnValue('hbwSerial');

    await underTest.retriggerFTSSteps();

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId2, module.serialNumber, expect.anything());
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      expect.anything(),
      orderId2,
      0,
      workpiece2,
      workpieceId2,
      fts,
      module.serialNumber,
    );
    expect(moduleCommandSender.sendProductionCommand).not.toHaveBeenCalledWith(dropStepOrder2, orderId2, 1, module, metadataOrder2);
    expect(underTest['navStepsToExecute']).toEqual([]);
    expect(underTest['manufactureStepsToExecute']).toEqual([]);
  });

  it('should assign the target module to the order when skipping the navigation', async () => {
    const orderId2 = 'orderId2';
    const workpiece2 = 'WHITE';
    const workpieceId2 = undefined;
    const navStepOrder2Id = 'navStepOrder2';

    const navStepOrder2: OrderNavigationStep = {
      id: navStepOrder2Id,
      type: 'NAVIGATION',
      target: ModuleType.HBW,
      state: OrderState.ENQUEUED,
      source: ModuleType.START,
    };
    const dropStepOrder2: OrderManufactureStep = {
      id: navStepOrder2Id,
      type: 'MANUFACTURE',
      moduleType: ModuleType.HBW,
      command: ModuleCommandType.DROP,
      dependentActionId: navStepOrder2Id,
      state: OrderState.ENQUEUED,
    };

    const navStepOrder2Action: OrderManagementAction = {
      index: 0,
      workpieceId: workpieceId2,
      workpiece: workpiece2,
      value: navStepOrder2,
      orderId: orderId2,
    };

    const order2: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId2,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId2,
      type: workpiece2,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStepOrder2, dropStepOrder2],
    };

    underTest['activeOrders'] = [order2];
    underTest['orderQueue'] = [order2];
    underTest['navStepsToExecute'] = [navStepOrder2Action];

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
      lastLoadPosition: '2',
    };
    const module: PairedModule = {
      serialNumber: 'module',
      type: 'MODULE',
      subType: ModuleType.HBW,
    };
    const ftsIsBusy = false;
    jest.spyOn(PairingStates.getInstance(), 'getModuleForOrder').mockReturnValue(module);
    jest.spyOn(PairingStates.getInstance(), 'updateAvailability').mockResolvedValue();
    jest
      .spyOn(underTest, 'chooseReadyFtsForStep')
      .mockImplementation(() => (ftsIsBusy ? undefined : <FtsPathResult>{ fts, path: { path: [1], distance: 0 } }));
    jest.spyOn(underTest, 'triggerOneManufactureStep').mockResolvedValue(true);
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue('hbwSerial');
    jest.spyOn(StockManagementService, 'reserveWorkpiece').mockReturnValue('hbwSerial');

    await underTest.retriggerFTSSteps();

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId2, module.serialNumber, expect.anything());
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      expect.anything(),
      orderId2,
      0,
      workpiece2,
      workpieceId2,
      fts,
      module.serialNumber,
    );
    expect(PairingStates.getInstance().updateAvailability).not.toHaveBeenCalledWith(module.serialNumber, AvailableState.READY, orderId2);
  });

  it('should not skip the navigation step during retriggerFTSSteps and retry later if an FTS is docked but it cannot accept a DROP', async () => {
    const orderId2 = 'orderId2';
    const workpiece2 = 'WHITE';
    const workpieceId2 = undefined;
    const navStepOrder2Id = 'navStepOrder2';

    const navStepOrder2: OrderNavigationStep = {
      id: navStepOrder2Id,
      type: 'NAVIGATION',
      target: ModuleType.HBW,
      state: OrderState.ENQUEUED,
      source: ModuleType.START,
    };
    const dropStepOrder2: OrderManufactureStep = {
      id: navStepOrder2Id,
      type: 'MANUFACTURE',
      moduleType: ModuleType.HBW,
      command: ModuleCommandType.DROP,
      dependentActionId: navStepOrder2Id,
      state: OrderState.ENQUEUED,
    };

    const navStepOrder2Action: OrderManagementAction = {
      index: 0,
      workpieceId: workpieceId2,
      workpiece: workpiece2,
      value: navStepOrder2,
      orderId: orderId2,
    };

    const order2: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId2,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId2,
      type: workpiece2,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStepOrder2, dropStepOrder2],
    };

    underTest['activeOrders'] = [order2];
    underTest['orderQueue'] = [order2];
    underTest['navStepsToExecute'] = [navStepOrder2Action];

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
      lastLoadPosition: '2',
    };
    const module: PairedModule = {
      serialNumber: 'module',
      type: 'MODULE',
      subType: ModuleType.HBW,
    };
    let ftsIsBusy = false;
    jest.spyOn(PairingStates.getInstance(), 'getModuleForOrder').mockReturnValue(module);
    jest.spyOn(PairingStates.getInstance(), 'getReadyForModuleType').mockReturnValue(module);
    jest.spyOn(FtsPairingStates.getInstance(), 'isLoadingBayFree').mockReturnValue(false);
    jest
      .spyOn(underTest, 'chooseReadyFtsForStep')
      .mockImplementation(() => (ftsIsBusy ? undefined : <FtsPathResult>{ fts, path: { path: [1], distance: 0 } }));
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockImplementation(() => {
      ftsIsBusy = true;
      return Promise.resolve();
    });
    jest.spyOn(moduleCommandSender, 'sendProductionCommand').mockImplementation(() => {
      return Promise.reject();
    });
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue('hbwSerial');
    jest.spyOn(StockManagementService, 'reserveWorkpiece').mockReturnValue('hbwSerial');

    await underTest.retriggerFTSSteps();

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId2, module.serialNumber, expect.anything());
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      expect.anything(),
      orderId2,
      0,
      workpiece2,
      workpieceId2,
      fts,
      module.serialNumber,
    );
    expect(moduleCommandSender.sendProductionCommand).not.toHaveBeenCalled();
    expect(underTest['navStepsToExecute']).toEqual([]);
    expect(underTest['manufactureStepsToExecute']).toEqual([]);
  });

  it('should NOT skip the next navigation step during retriggerFTSSteps if it is followed by a DROP command and no FTS is docked', async () => {
    const orderId2 = 'orderId2';
    const workpiece2 = 'WHITE';
    const navStepOrder2Id = 'navStepOrder2';

    const navStepOrder2: OrderNavigationStep = {
      id: navStepOrder2Id,
      type: 'NAVIGATION',
      target: ModuleType.HBW,
      state: OrderState.ENQUEUED,
      source: ModuleType.START,
    };
    const dropStepOrder2: OrderManufactureStep = {
      id: navStepOrder2Id,
      type: 'MANUFACTURE',
      moduleType: ModuleType.HBW,
      command: ModuleCommandType.DROP,
      dependentActionId: navStepOrder2Id,
      state: OrderState.ENQUEUED,
    };

    const navStepOrder2Action: OrderManagementAction = {
      index: 0,
      workpiece: workpiece2,
      value: navStepOrder2,
      orderId: orderId2,
    };

    const order2: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId2,
      state: OrderState.IN_PROGRESS,
      type: workpiece2,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStepOrder2, dropStepOrder2],
    };

    underTest['activeOrders'] = [order2];
    underTest['orderQueue'] = [order2];
    underTest['navStepsToExecute'] = [navStepOrder2Action];

    const module: PairedModule = {
      serialNumber: 'module',
      type: 'MODULE',
      subType: ModuleType.HBW,
    };
    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'dpsSerial',
      lastLoadPosition: '2',
    };
    let ftsIsBusy = false;
    jest.spyOn(PairingStates.getInstance(), 'getModuleForOrder').mockReturnValue(module);
    jest.spyOn(PairingStates.getInstance(), 'getReadyForModuleType').mockReturnValue(module);
    jest
      .spyOn(underTest, 'chooseReadyFtsForStep')
      .mockImplementation(() => (ftsIsBusy ? undefined : <FtsPathResult>{ fts, path: { path: [1], distance: 0 } }));
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockImplementation(() => {
      ftsIsBusy = true;
      return Promise.resolve();
    });
    jest.spyOn(moduleCommandSender, 'sendProductionCommand').mockImplementation(() => {
      return Promise.reject();
    });
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue('hbwSerial');

    await underTest.retriggerFTSSteps();

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId2, module.serialNumber, expect.anything());
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      navStepOrder2,
      orderId2,
      navStepOrder2Action.index,
      workpiece2,
      undefined,
      fts,
      module.serialNumber,
    );
    expect(moduleCommandSender.sendProductionCommand).not.toHaveBeenCalled();
    expect(underTest['navStepsToExecute']).toEqual([]);
    expect(underTest['manufactureStepsToExecute']).toEqual([]);
  });

  it('should NOT skip the next navigation step during retriggerFTSSteps if there is no following manufacture command', async () => {
    const orderId2 = 'orderId2';
    const workpiece2 = 'WHITE';
    const workpieceId2 = 'workpieceId2';
    const navStepOrder2Id = 'navStepOrder2';

    const navStepOrder2: OrderNavigationStep = {
      id: navStepOrder2Id,
      type: 'NAVIGATION',
      target: ModuleType.DPS,
      state: OrderState.ENQUEUED,
      source: ModuleType.HBW,
    };

    const navStepOrder2Action: OrderManagementAction = {
      index: 0,
      workpieceId: workpieceId2,
      workpiece: workpiece2,
      value: navStepOrder2,
      orderId: orderId2,
    };

    const order2: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId2,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId2,
      type: workpiece2,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStepOrder2],
    };

    underTest['activeOrders'] = [order2];
    underTest['orderQueue'] = [order2];
    underTest['navStepsToExecute'] = [navStepOrder2Action];

    const module: PairedModule = {
      serialNumber: 'module',
      type: 'MODULE',
      subType: ModuleType.HBW,
    };
    const module2: PairedModule = {
      serialNumber: 'module2',
      type: 'MODULE',
      subType: ModuleType.DPS,
    };
    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: module.serialNumber,
      lastLoadPosition: '2',
    };
    let ftsIsBusy = false;
    jest.spyOn(PairingStates.getInstance(), 'getModuleForOrder').mockReturnValue(undefined);
    jest.spyOn(PairingStates.getInstance(), 'getReadyForModuleType').mockReturnValue(module2);
    jest
      .spyOn(underTest, 'chooseReadyFtsForStep')
      .mockImplementation(() => (ftsIsBusy ? undefined : <FtsPathResult>{ fts, path: { path: [1], distance: 0 } }));
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockImplementation(() => {
      ftsIsBusy = true;
      return Promise.resolve();
    });
    jest.spyOn(moduleCommandSender, 'sendProductionCommand').mockImplementation(() => {
      return Promise.reject();
    });

    await underTest.retriggerFTSSteps();

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId2, module2.serialNumber, expect.anything());
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      navStepOrder2,
      orderId2,
      navStepOrder2Action.index,
      workpiece2,
      workpieceId2,
      fts,
      module2.serialNumber,
    );
    expect(moduleCommandSender.sendProductionCommand).not.toHaveBeenCalled();
    expect(underTest['navStepsToExecute']).toEqual([]);
    expect(underTest['manufactureStepsToExecute']).toEqual([]);
  });

  it('should send an navigation request if the FTS is available', async () => {
    const index = 0;
    const orderId = 'orderId';
    const workpieceId = 'workpieceId';
    const workpiece = 'BLUE';
    const navStep: OrderNavigationStep = {
      id: 'navStepId',
      state: OrderState.ENQUEUED,
      target: ModuleType.DRILL,
      source: ModuleType.START,
      type: 'NAVIGATION',
    };
    const navStepAction: OrderManagementAction = {
      index,
      workpieceId,
      orderId,
      value: navStep,
      workpiece,
    };

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
    };
    FtsPairingStates.getInstance().getReady = jest.fn().mockReturnValue(fts);
    jest.spyOn(underTest, 'chooseReadyFtsForStep').mockReturnValue({ fts, path: MOCKED_PATH });

    underTest['navStepsToExecute'] = [navStepAction];
    await underTest.retriggerFTSSteps();

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId, MOCKED_MODULE_SERIAL, expect.anything());
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      navStep,
      orderId,
      index,
      workpiece,
      workpieceId,
      fts,
      MOCKED_MODULE_SERIAL,
    );
    expect(underTest['navStepsToExecute']).toEqual([]);
  });

  it('should send an order to clear the target module if an FTS is blocking it', async () => {
    const index = 0;
    const orderId = 'orderId';
    const workpieceId = 'workpieceId';
    const workpiece = 'BLUE';
    const navStep: OrderNavigationStep = {
      id: 'navStepId',
      state: OrderState.ENQUEUED,
      target: ModuleType.DRILL,
      source: ModuleType.START,
      type: 'NAVIGATION',
    };
    const navStepAction: OrderManagementAction = {
      index,
      workpieceId,
      orderId,
      value: navStep,
      workpiece,
    };

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: MOCKED_MODULE_SERIAL,
    };
    FtsPairingStates.getInstance().getReady = jest.fn().mockReturnValue(fts);
    jest.spyOn(FtsPairingStates.getInstance(), 'getAllReadyUnassigned').mockReturnValue([{ state: fts }]);
    jest.spyOn(FtsPairingStates.getInstance(), 'getFtsAtPosition').mockReturnValue(fts);
    // no FTS has a path to the module as it is blocked by another one
    jest.spyOn(underTest, 'chooseReadyFtsForStep').mockReturnValue(undefined);
    jest.spyOn(navCommandSender, 'sendClearModuleNodeNavigationRequest').mockResolvedValue();

    underTest['navStepsToExecute'] = [navStepAction];
    await underTest.retriggerFTSSteps();

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId, MOCKED_MODULE_SERIAL, expect.anything());
    expect(navCommandSender.sendNavigationRequest).not.toHaveBeenCalled();
    expect(navCommandSender.sendClearModuleNodeNavigationRequest).toHaveBeenCalledWith(MOCKED_MODULE_SERIAL);
    expect(underTest['navStepsToExecute']).toEqual([navStepAction]);
  });

  it('should choose an FTS for a navigation request if the FTS would be filled and a PICK is guaranteed', async () => {
    const orderId = 'orderId';
    const workpieceId = 'workpieceId';
    const workpiece = 'BLUE';
    const navStep: OrderNavigationStep = {
      id: 'navStepId',
      state: OrderState.ENQUEUED,
      target: ModuleType.DRILL,
      source: ModuleType.HBW,
      type: 'NAVIGATION',
    };
    const dropStep: OrderManufactureStep = {
      id: 'dropStep',
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      command: ModuleCommandType.DROP,
      dependentActionId: navStep.id,
      moduleType: ModuleType.HBW,
    };
    const pickStep: OrderManufactureStep = {
      id: 'dropStep',
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      command: ModuleCommandType.PICK,
      dependentActionId: dropStep.id,
      moduleType: ModuleType.DRILL,
    };

    const order1: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId,
      type: workpiece,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [pickStep, navStep, dropStep],
    };

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
    };
    const targetModule: PairedModule = {
      type: 'MODULE',
      serialNumber: MOCKED_MODULE_SERIAL,
    };
    jest.spyOn(FtsPairingStates.getInstance(), 'getForOrder').mockReturnValue(undefined);
    jest.spyOn(FtsPairingStates.getInstance(), 'getAllReadyUnassigned').mockReturnValue([{ state: fts }]);
    jest.spyOn(PairingStates.getInstance(), 'getReadyForModuleType').mockReturnValue(targetModule);
    jest.spyOn(FtsPairingStates.getInstance(), 'getOpenloadingBay').mockReturnValue('1');
    jest.spyOn(FtsPairingStates.getInstance(), 'getLoadedOrderIds').mockReturnValue(['a', 'b']);
    underTest['activeOrders'] = [order1];

    expect(underTest.chooseReadyFtsForStep(orderId, MOCKED_MODULE_SERIAL, navStep)).toEqual({ fts, path: MOCKED_PATH });
  });

  it('should not choose an FTS for a navigation request if the FTS would be filled and no PICK is guaranteed', async () => {
    const orderId = 'orderId';
    const workpieceId = 'workpieceId';
    const workpiece = 'BLUE';
    const pickStep: OrderManufactureStep = {
      id: 'dropStep',
      type: 'MANUFACTURE',
      state: OrderState.FINISHED,
      command: ModuleCommandType.PICK,
      moduleType: ModuleType.DRILL,
    };
    const navStep: OrderNavigationStep = {
      id: 'navStepId',
      state: OrderState.ENQUEUED,
      target: ModuleType.DRILL,
      source: ModuleType.HBW,
      dependentActionId: pickStep.id,
      type: 'NAVIGATION',
    };
    const dropStep: OrderManufactureStep = {
      id: 'dropStep',
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      command: ModuleCommandType.DROP,
      dependentActionId: navStep.id,
      moduleType: ModuleType.HBW,
    };

    const order1: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId,
      type: workpiece,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStep, dropStep, pickStep],
    };

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
    };
    jest.spyOn(FtsPairingStates.getInstance(), 'getForOrder').mockReturnValue(undefined);
    jest.spyOn(FtsPairingStates.getInstance(), 'getAllReadyUnassigned').mockReturnValue([{ state: fts }]);
    jest
      .spyOn(PairingStates.getInstance(), 'getReadyForModuleType')
      .mockReturnValue({ serialNumber: 'readyModule' } as unknown as PairedModule);
    jest.spyOn(FtsPairingStates.getInstance(), 'getOpenloadingBay').mockReturnValue('1');
    jest.spyOn(FtsPairingStates.getInstance(), 'getLoadedOrderIds').mockReturnValue(['a', 'b']);
    underTest['activeOrders'] = [order1];

    expect(underTest.chooseReadyFtsForStep(orderId, 'readyModule', navStep)).toEqual(undefined);
  });

  it('should choose the empty FTS for a navigation request if the other FTS would be filled and no PICK is guaranteed', async () => {
    const orderId = 'orderId';
    const workpieceId = 'workpieceId';
    const workpiece = 'BLUE';
    const pickStep: OrderManufactureStep = {
      id: 'dropStep',
      type: 'MANUFACTURE',
      state: OrderState.FINISHED,
      command: ModuleCommandType.PICK,
      moduleType: ModuleType.DRILL,
    };
    const navStep: OrderNavigationStep = {
      id: 'navStepId',
      state: OrderState.ENQUEUED,
      target: ModuleType.DRILL,
      source: ModuleType.HBW,
      dependentActionId: pickStep.id,
      type: 'NAVIGATION',
    };
    const dropStep: OrderManufactureStep = {
      id: 'dropStep',
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      command: ModuleCommandType.DROP,
      dependentActionId: navStep.id,
      moduleType: ModuleType.HBW,
    };

    const order1: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId,
      type: workpiece,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStep, dropStep, pickStep],
    };

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber1',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
    };
    const fts2: FtsPairedModule = {
      serialNumber: 'serialNumber2',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
    };
    const targetModule: PairedModule = {
      type: 'MODULE',
      serialNumber: MOCKED_MODULE_SERIAL,
    };
    jest.spyOn(FtsPairingStates.getInstance(), 'getForOrder').mockReturnValue(undefined);
    jest.spyOn(FtsPairingStates.getInstance(), 'getAllReadyUnassigned').mockReturnValue([{ state: fts }, { state: fts2 }]);
    jest.spyOn(PairingStates.getInstance(), 'getReadyForModuleType').mockReturnValue(targetModule);
    jest.spyOn(FtsPairingStates.getInstance(), 'getOpenloadingBay').mockReturnValue('1');
    jest
      .spyOn(FtsPairingStates.getInstance(), 'getLoadedOrderIds')
      .mockImplementation(serialNumber => (serialNumber === fts2.serialNumber ? [] : ['a', 'b']));
    underTest['activeOrders'] = [order1];

    expect(underTest.chooseReadyFtsForStep(orderId, MOCKED_MODULE_SERIAL, navStep)).toEqual({ fts: fts2, path: MOCKED_PATH });
  });

  it('should always use the FTS for a navigation request that has the order assigned to it', async () => {
    const orderId = 'orderId';
    const workpieceId = 'workpieceId';
    const workpiece = 'BLUE';
    const pickStep: OrderManufactureStep = {
      id: 'dropStep',
      type: 'MANUFACTURE',
      state: OrderState.FINISHED,
      command: ModuleCommandType.PICK,
      moduleType: ModuleType.DRILL,
    };
    const navStep: OrderNavigationStep = {
      id: 'navStepId',
      state: OrderState.ENQUEUED,
      target: ModuleType.DRILL,
      source: ModuleType.HBW,
      dependentActionId: pickStep.id,
      type: 'NAVIGATION',
    };
    const dropStep: OrderManufactureStep = {
      id: 'dropStep',
      type: 'MANUFACTURE',
      state: OrderState.ENQUEUED,
      command: ModuleCommandType.DROP,
      dependentActionId: navStep.id,
      moduleType: ModuleType.HBW,
    };

    const order1: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: orderId,
      state: OrderState.IN_PROGRESS,
      workpieceId: workpieceId,
      type: workpiece,
      timestamp: new Date(),
      startedAt: new Date(),
      productionSteps: [navStep, dropStep, pickStep],
    };

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber1',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
    };
    const fts2: FtsPairedModule = {
      serialNumber: 'serialNumber2',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
    };
    const targetModule: PairedModule = {
      type: 'MODULE',
      serialNumber: MOCKED_MODULE_SERIAL,
    };
    jest.spyOn(FtsPairingStates.getInstance(), 'getForOrder').mockReturnValue(fts);
    jest.spyOn(FtsPairingStates.getInstance(), 'isReadyForOrder').mockReturnValue(true);
    jest.spyOn(FtsPairingStates.getInstance(), 'getAllReadyUnassigned').mockReturnValue([{ state: fts }, { state: fts2 }]);
    jest.spyOn(PairingStates.getInstance(), 'getReadyForModuleType').mockReturnValue(targetModule);
    jest.spyOn(FtsPairingStates.getInstance(), 'getOpenloadingBay').mockReturnValue('1');
    jest
      .spyOn(FtsPairingStates.getInstance(), 'getLoadedOrderIds')
      .mockImplementation(serialNumber => (serialNumber === fts2.serialNumber ? [] : ['a', 'b']));
    underTest['activeOrders'] = [order1];

    expect(underTest.chooseReadyFtsForStep(orderId, MOCKED_MODULE_SERIAL, navStep)).toEqual({ fts, path: MOCKED_PATH });
  });

  it('should reset the navigation step state to enqueue if sending the command failed', async () => {
    const index = 0;
    const orderId = 'orderId';
    const workpieceId = 'workpieceId';
    const workpiece = 'BLUE';
    const navStep: OrderNavigationStep = {
      id: 'navStepId',
      state: OrderState.ENQUEUED,
      target: ModuleType.DRILL,
      source: ModuleType.START,
      type: 'NAVIGATION',
    };
    const navStepAction: OrderManagementAction = {
      index,
      workpieceId,
      orderId,
      value: navStep,
      workpiece,
    };

    const fts: FtsPairedModule = {
      serialNumber: 'serialNumber',
      type: 'FTS',
      lastModuleSerialNumber: 'module',
    };
    FtsPairingStates.getInstance().getReady = jest.fn().mockReturnValue(fts);
    jest.spyOn(underTest, 'chooseReadyFtsForStep').mockReturnValue({ fts, path: MOCKED_PATH });
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockRejectedValue(new Error('error'));

    underTest['navStepsToExecute'] = [navStepAction];
    await underTest.retriggerFTSSteps();

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId, MOCKED_MODULE_SERIAL, expect.anything());
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      navStep,
      orderId,
      index,
      workpiece,
      workpieceId,
      fts,
      MOCKED_MODULE_SERIAL,
    );

    const expectedNavStepAction: OrderManagementAction = {
      index,
      workpieceId,
      orderId,
      value: {
        id: 'navStepId',
        state: OrderState.ENQUEUED,
        target: ModuleType.DRILL,
        source: ModuleType.START,
        type: 'NAVIGATION',
      },
      workpiece,
    };
    expect(underTest['navStepsToExecute']).toEqual([expectedNavStepAction]);
  });

  it('should not send an navigation request if the FTS is not available', async () => {
    const index = 0;
    const orderId = 'orderId';
    const workpieceId = 'workpieceId';
    const workpiece = 'BLUE';
    const navStep: OrderNavigationStep = {
      id: 'navStepId',
      state: OrderState.ENQUEUED,
      target: ModuleType.DRILL,
      source: ModuleType.START,
      type: 'NAVIGATION',
    };
    const navStepAction: OrderManagementAction = {
      index,
      workpieceId,
      orderId,
      value: navStep,
      workpiece,
    };

    FtsPairingStates.getInstance().getReady = jest.fn().mockReturnValue(undefined);
    jest.spyOn(underTest, 'chooseReadyFtsForStep').mockReturnValue(undefined);

    underTest['navStepsToExecute'] = [navStepAction];
    await underTest.retriggerFTSSteps();

    expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId, MOCKED_MODULE_SERIAL, expect.anything());
    expect(navCommandSender.sendNavigationRequest).not.toHaveBeenCalled();
    expect(underTest['navStepsToExecute']).toEqual([navStepAction]);
  });

  it('should trigger a navigation step if the an FTS in not at the module for a drop command', async () => {
    const orderId = 'orderId';
    const workpiece = 'BLUE';
    const workpieceId = 'workpieceId';
    const drillId = 'drillId';
    const dropId = 'dropId';
    const drillSerial = 'drillSerial';

    const drill: OrderManufactureStep = {
      type: 'MANUFACTURE',
      command: ModuleCommandType.DRILL,
      state: OrderState.FINISHED,
      id: drillId,
      moduleType: ModuleType.DRILL,
      serialNumber: drillSerial,
    };

    const drop: OrderManufactureStep = {
      type: 'MANUFACTURE',
      command: ModuleCommandType.DROP,
      state: OrderState.ENQUEUED,
      id: dropId,
      moduleType: ModuleType.DRILL,
      dependentActionId: drillId,
    };

    const productionSteps: Array<OrderNavigationStep | OrderManufactureStep> = [drill, drop];

    const order: OrderResponse = {
      type: workpiece,
      orderId,
      productionSteps: productionSteps,
      workpieceId,
      orderType: 'PRODUCTION',
      state: OrderState.IN_PROGRESS,
      timestamp: new Date(),
    };

    underTest['activeOrders'] = [order];
    underTest['orderQueue'] = [order];

    const dropAction: OrderManagementAction = {
      index: 1,
      workpieceId,
      value: drop,
      orderId,
      workpiece,
    };

    const fts: FtsPairedModule = {
      serialNumber: 'ftsSerialNumber',
    } as unknown as FtsPairedModule;

    FtsPairingStates.getInstance().isFtsWaitingAtPosition = jest.fn().mockReturnValue(false);
    jest.spyOn(underTest, 'chooseReadyFtsForStep').mockReturnValue({ fts, path: MOCKED_PATH });
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockResolvedValue();

    await underTest.triggerIndependentActions(order, [dropAction]);

    expect(FtsPairingStates.getInstance().isFtsWaitingAtPosition).toHaveBeenCalledWith(orderId, drillSerial);
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      expect.anything(),
      orderId,
      1,
      workpiece,
      workpieceId,
      fts,
      MOCKED_MODULE_SERIAL,
    );
    expect(moduleCommandSender.sendProductionCommand).not.toHaveBeenCalled();

    expect(order.productionSteps.length).toEqual(3); // 2 + 1 for the new navigation command to the module
    const actualDrop = order.productionSteps[2];
    let actualNav = order.productionSteps[1];
    expect(actualNav.type).toEqual('NAVIGATION');
    actualNav = actualNav as OrderNavigationStep;
    expect(actualNav.target).toEqual(ModuleType.DRILL);
    expect(actualNav.state).toEqual(OrderState.IN_PROGRESS);
    expect(actualNav.dependentActionId).toEqual(drillId);
    expect(actualDrop.state).toEqual(OrderState.ENQUEUED);
    expect(actualDrop.dependentActionId).toEqual(actualNav.id);
  });

  it('should trigger a drop step if the an FTS in at the module for a drop command', async () => {
    const orderId = 'orderId';
    const workpiece = 'BLUE';
    const workpieceId = 'workpieceId';
    const drillId = 'drillId';
    const dropId = 'dropId';
    const drillSerial = 'drillSerial';

    const drill: OrderManufactureStep = {
      type: 'MANUFACTURE',
      command: ModuleCommandType.DRILL,
      state: OrderState.FINISHED,
      id: drillId,
      moduleType: ModuleType.DRILL,
      serialNumber: drillSerial,
    };

    const drop: OrderManufactureStep = {
      type: 'MANUFACTURE',
      command: ModuleCommandType.DROP,
      state: OrderState.ENQUEUED,
      id: dropId,
      moduleType: ModuleType.DRILL,
      dependentActionId: drillId,
    };

    const productionSteps: Array<OrderNavigationStep | OrderManufactureStep> = [drill, drop];

    const order: OrderResponse = {
      type: workpiece,
      orderId,
      productionSteps: productionSteps,
      workpieceId,
      orderType: 'PRODUCTION',
      state: OrderState.IN_PROGRESS,
      timestamp: new Date(),
    };

    underTest['activeOrders'] = [order];
    underTest['orderQueue'] = [order];

    const dropAction: OrderManagementAction = {
      index: 1,
      workpieceId,
      value: drop,
      orderId,
      workpiece,
    };

    const pairedModule: PairedModule = {
      serialNumber: drillSerial,
    } as unknown as PairedModule;
    FtsPairingStates.getInstance().isFtsWaitingAtPosition = jest.fn().mockReturnValue(true);
    PairingStates.getInstance().getReadyForModuleType = jest.fn().mockReturnValue(pairedModule);
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockResolvedValue();

    await underTest.triggerIndependentActions(order, [dropAction]);

    const metadata: StoreMetadata = {
      type: workpiece,
      workpieceId,
    };

    expect(FtsPairingStates.getInstance().isFtsWaitingAtPosition).toHaveBeenCalledWith(orderId, drillSerial);
    expect(PairingStates.getInstance().getReadyForModuleType).toHaveBeenCalledWith(ModuleType.DRILL, orderId);
    expect(navCommandSender.sendNavigationRequest).not.toHaveBeenCalled();
    expect(moduleCommandSender.sendProductionCommand).toHaveBeenCalledWith(expect.anything(), orderId, 1, pairedModule, metadata);

    expect(order.productionSteps.length).toEqual(2);
    const actualDrop = order.productionSteps[1];
    expect(actualDrop.state).toEqual(OrderState.IN_PROGRESS);
    expect(actualDrop.dependentActionId).toEqual(drillId);
  });

  it('should trigger a drop step if the FTS is at the module without an order', async () => {
    const orderId = 'orderId';
    const workpiece = 'BLUE';
    const workpieceId = 'workpieceId';
    const drillId = 'drillId';
    const dropId = 'dropId';
    const drillSerial = 'drillSerial';

    const drill: OrderManufactureStep = {
      type: 'MANUFACTURE',
      command: ModuleCommandType.DRILL,
      state: OrderState.FINISHED,
      id: drillId,
      moduleType: ModuleType.DRILL,
      serialNumber: drillSerial,
    };

    const drop: OrderManufactureStep = {
      type: 'MANUFACTURE',
      command: ModuleCommandType.DROP,
      state: OrderState.ENQUEUED,
      id: dropId,
      moduleType: ModuleType.DRILL,
      dependentActionId: drillId,
    };

    const productionSteps: Array<OrderNavigationStep | OrderManufactureStep> = [drill, drop];

    const order: OrderResponse = {
      type: workpiece,
      orderId,
      productionSteps: productionSteps,
      workpieceId,
      orderType: 'PRODUCTION',
      state: OrderState.IN_PROGRESS,
      timestamp: new Date(),
    };

    underTest['activeOrders'] = [order];
    underTest['orderQueue'] = [order];

    const dropAction: OrderManagementAction = {
      index: 1,
      workpieceId,
      value: drop,
      orderId,
      workpiece,
    };

    const pairedFts: FtsPairedModule = {
      type: 'FTS',
      serialNumber: 'ftsSerial',
      lastLoadPosition: '1',
    };
    const pairedModule: PairedModule = {
      serialNumber: drillSerial,
    } as unknown as PairedModule;
    FtsPairingStates.getInstance().isFtsWaitingAtPosition = jest.fn().mockReturnValue(false);
    FtsPairingStates.getInstance().getFtsAtPosition = jest.fn().mockReturnValue(pairedFts);
    PairingStates.getInstance().getReadyForModuleType = jest.fn().mockReturnValue(pairedModule);
    jest.spyOn(navCommandSender, 'sendNavigationRequest').mockResolvedValue();

    await underTest.triggerIndependentActions(order, [dropAction]);

    const metadata: StoreMetadata = {
      type: workpiece,
      workpieceId,
    };

    expect(FtsPairingStates.getInstance().isFtsWaitingAtPosition).toHaveBeenCalledWith(orderId, drillSerial);
    expect(FtsPairingStates.getInstance().getFtsAtPosition).toHaveBeenCalledWith(drillSerial, orderId);
    expect(PairingStates.getInstance().getReadyForModuleType).toHaveBeenCalledWith(ModuleType.DRILL, orderId);
    expect(navCommandSender.sendNavigationRequest).not.toHaveBeenCalled();
    expect(moduleCommandSender.sendProductionCommand).toHaveBeenCalledWith(expect.anything(), orderId, 1, pairedModule, metadata);

    expect(order.productionSteps.length).toEqual(2);
    const actualDrop = order.productionSteps[1];
    expect(actualDrop.state).toEqual(OrderState.IN_PROGRESS);
    expect(actualDrop.dependentActionId).toEqual(drillId);
  });

  it('should generate the correct metadata of the workpiece history', () => {
    const workpieceId = 'workpieceId';
    const workpiece = 'BLUE';
    const dpsDropMs = 1643803994000;
    const dpsPickMs = 1643804174000;
    const hbwPickMs = 1643804054000;
    const hbwDropMs = 1643804114000;
    const dpsDrop = new Date(dpsDropMs);
    const hbwPick = new Date(hbwPickMs);
    const hbwDrop = new Date(hbwDropMs);
    const dpsPick = new Date(dpsPickMs);
    // const
    const completedOrder: OrderResponse = {
      productionSteps: [
        {
          type: 'MANUFACTURE',
          state: OrderState.FINISHED,
          moduleType: ModuleType.DPS,
          command: ModuleCommandType.DROP,
          stoppedAt: dpsDrop,
        },
        {
          type: 'MANUFACTURE',
          state: OrderState.FINISHED,
          moduleType: ModuleType.HBW,
          command: ModuleCommandType.PICK,
          stoppedAt: hbwPick,
        },
      ],
      workpieceId,
    } as unknown as OrderResponse;

    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.FINISHED,
      moduleType: ModuleType.DPS,
      command: ModuleCommandType.PICK,
      stoppedAt: dpsPick,
      id: 'id',
      serialNumber: 'serialNumber',
    };

    const activeOrder: OrderResponse = {
      productionSteps: [
        {
          type: 'MANUFACTURE',
          state: OrderState.FINISHED,
          moduleType: ModuleType.HBW,
          command: ModuleCommandType.DROP,
          stoppedAt: hbwDrop,
        },
        prodStep,
      ],
      workpieceId,
    } as unknown as OrderResponse;

    underTest['completedOrders'] = [completedOrder];
    underTest['orderQueue'] = [activeOrder];
    underTest['activeOrders'] = [activeOrder];

    const pairedModule: PairedModule = {} as unknown as PairedModule; // not needed in this test
    const actualMetadata = underTest.generateMetadataForProductionCommand(
      prodStep,
      pairedModule,
      workpiece,
      workpieceId,
    ) as DeliveryMetadata;
    const expectedHistoryPoints: Array<HistoryPoint> = [
      {
        ts: dpsDropMs,
        code: 100,
      },
      {
        ts: hbwPickMs,
        code: 300,
      },
      {
        ts: hbwDropMs,
        code: 400,
      },
      {
        ts: dpsPickMs,
        code: 800,
      },
    ];

    expect(actualMetadata.workpiece.workpieceId).toEqual(workpieceId);
    expect(actualMetadata.workpiece.type).toEqual(workpiece);
    expect(actualMetadata.workpiece.state).toEqual('PROCESSED');
    expect(actualMetadata.workpiece.history).toEqual(expect.arrayContaining(expectedHistoryPoints));
  });

  it('should call metadataForCommand if the production step is not for a DPS', () => {
    const moduleType = ModuleType.DRILL;
    const command = ModuleCommandType.DRILL;
    const workpiece = 'BLUE';
    const workpieceId = 'workpieceId';
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.FINISHED,
      moduleType,
      command,
      id: 'id',
      serialNumber: 'serialNumber',
    };

    const metadata: DurationMetadata = {
      duration: 1000,
    };

    jest.spyOn(productionHelper, 'metadataForCommand').mockReturnValue(metadata);

    const pairedModule: PairedModule = {} as unknown as PairedModule; // not needed in this test
    const actualMetadata = underTest.generateMetadataForProductionCommand(prodStep, pairedModule, workpiece, workpieceId);
    expect(actualMetadata).toEqual(metadata);
    expect(productionHelper.metadataForCommand).toHaveBeenCalledWith(moduleType, command, pairedModule, workpiece, workpieceId);
  });

  it('should update the workpiece id for a given order id when requested', async () => {
    jest.spyOn(StockManagementService, 'stockAvailable').mockReturnValue(undefined).mockReturnValueOnce('hbwSerial');
    const orderId = 'orderId';
    const workpiece = 'BLUE';
    const workpieceId = 'workpieceId';
    const newWorkpieceId = 'newWorkpieceId';
    const drillId = 'drillId';
    const navId = 'dropId';

    const drill: OrderManufactureStep = {
      type: 'MANUFACTURE',
      command: ModuleCommandType.DRILL,
      state: OrderState.ENQUEUED,
      id: drillId,
      moduleType: ModuleType.DRILL,
      serialNumber: MOCKED_MODULE_SERIAL,
    };

    const nav: OrderNavigationStep = {
      type: 'NAVIGATION',
      target: ModuleType.MILL,
      source: ModuleType.HBW,
      state: OrderState.ENQUEUED,
      id: navId,
    };

    const productionSteps: Array<OrderNavigationStep | OrderManufactureStep> = [drill, nav];

    const order: OrderResponse = {
      type: workpiece,
      orderId,
      productionSteps: productionSteps,
      workpieceId,
      orderType: 'PRODUCTION',
      state: OrderState.IN_PROGRESS,
      timestamp: new Date(),
    };

    jest.spyOn(underTest, 'sendOrderListUpdate').mockResolvedValue(undefined);
    // no-explicit-any is needed here as the methods are private
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const triggerNavigationStepsSpy = jest.spyOn(underTest as any, 'triggerNavigationSteps').mockResolvedValue(undefined);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const triggerManufactureStepSpy = jest.spyOn(underTest as any, 'triggerManufactureSteps').mockResolvedValue(undefined);
    await underTest.cacheOrder(order);
    expect(underTest.getWorkpieceId(orderId)).toEqual(workpieceId);

    underTest.updateOrderWorkpieceId(orderId, newWorkpieceId);

    expect(underTest.getWorkpieceId(orderId)).toEqual(newWorkpieceId);

    // make sure the new workpiece id is also sent when retriggering steps.
    triggerNavigationStepsSpy.mockReset();
    triggerManufactureStepSpy.mockReset();
    jest.spyOn(underTest, 'chooseReadyFtsForStep').mockReturnValue({ fts: { serialNumber: 'someId', type: 'FTS' }, path: MOCKED_PATH });

    await underTest.retriggerFTSSteps();
    expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(
      expect.anything(),
      orderId,
      expect.anything(),
      expect.anything(),
      newWorkpieceId,
      expect.anything(),
      MOCKED_MODULE_SERIAL,
    );
    await underTest.retriggerModuleSteps();
    expect(moduleCommandSender.sendProductionCommand).toHaveBeenCalledWith(
      expect.anything(),
      orderId,
      expect.anything(),
      expect.anything(),
      expect.objectContaining({ workpieceId: newWorkpieceId }),
    );
  });

  it('should start the order if a workpiece is available', async () => {
    const order: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'orderId',
      type: 'WHITE',
      timestamp: new Date(MOCKED_DATE),
      state: OrderState.ENQUEUED,
      workpieceId: 'wpId',
      productionSteps: [],
    };
    jest.spyOn(StockManagementService, 'reserveWorkpiece').mockReturnValue('hbwSerial');
    jest.spyOn(underTest, 'triggerIndependentActions').mockResolvedValue();
    await underTest.startOrder(order);
    expect(StockManagementService.reserveWorkpiece).toHaveBeenCalledWith(order.orderId, order.type);
    expect(underTest.triggerIndependentActions).toHaveBeenCalled();
  });

  it('should not start the order if no workpiece is available', async () => {
    const order: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId: 'orderId',
      type: 'WHITE',
      timestamp: new Date(MOCKED_DATE),
      state: OrderState.ENQUEUED,
      workpieceId: 'wpId',
      productionSteps: [],
    };
    jest.spyOn(StockManagementService, 'reserveWorkpiece').mockReturnValue(undefined);
    jest.spyOn(underTest, 'triggerIndependentActions').mockResolvedValue();
    await underTest.startOrder(order);
    expect(StockManagementService.reserveWorkpiece).toHaveBeenCalledWith(order.orderId, order.type);
    expect(underTest.triggerIndependentActions).not.toHaveBeenCalled();
  });

  it('should start the storage order if an empty storage bay is available', async () => {
    const order: OrderResponse = {
      orderType: 'STORAGE',
      orderId: 'orderId',
      type: 'WHITE',
      timestamp: new Date(MOCKED_DATE),
      state: OrderState.ENQUEUED,
      workpieceId: 'wpId',
      productionSteps: [],
    };
    jest.spyOn(StockManagementService, 'reserveEmptyBay').mockReturnValue('hbwId');
    jest.spyOn(underTest, 'triggerIndependentActions').mockResolvedValue();
    await underTest.startOrder(order);
    expect(StockManagementService.reserveEmptyBay).toHaveBeenCalledWith(order.orderId, order.type);
    expect(underTest.triggerIndependentActions).toHaveBeenCalled();
  });

  it('should not start the storage order if no empty storage bay is available', async () => {
    const order: OrderResponse = {
      orderType: 'STORAGE',
      orderId: 'orderId',
      type: 'WHITE',
      timestamp: new Date(MOCKED_DATE),
      state: OrderState.ENQUEUED,
      workpieceId: 'wpId',
      productionSteps: [],
    };
    jest.spyOn(StockManagementService, 'reserveEmptyBay').mockReturnValue(undefined);
    jest.spyOn(underTest, 'triggerIndependentActions').mockResolvedValue();
    await underTest.startOrder(order);
    expect(StockManagementService.reserveEmptyBay).toHaveBeenCalledWith(order.orderId, order.type);
    expect(underTest.triggerIndependentActions).not.toHaveBeenCalled();
  });

  it('should remove bay reservations after the storage pick has finished', async () => {
    const orderId = 'orderId';
    const prodStepId = 'prodStepId';
    const workpiece = 'BLUE';
    const workpieceId = 'workpieceId';
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: prodStepId,
      moduleType: ModuleType.HBW,
      command: ModuleCommandType.PICK,
      startedAt: MOCKED_DATE,
    };
    const activeOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [prodStep],
      state: OrderState.IN_PROGRESS,
      startedAt: MOCKED_DATE,
      workpieceId,
    };

    underTest['activeOrders'] = [activeOrder];
    underTest['orderQueue'] = [activeOrder];

    jest.spyOn(underTest, 'startNextOrder').mockResolvedValue();
    jest.spyOn(underTest, 'retriggerFTSSteps').mockResolvedValue(0);
    jest.spyOn(underTest, 'sendOrderListUpdate').mockResolvedValue(undefined);
    jest.spyOn(StockManagementService, 'removeReservation').mockReturnValue();

    await underTest.handleActionUpdate(orderId, prodStepId, State.FINISHED);
    expect(StockManagementService.removeReservation).toHaveBeenCalledWith(activeOrder.orderId);
  });

  it('should remove bay reservations after the storage drop has finished', async () => {
    const orderId = 'orderId';
    const prodStepId = 'prodStepId';
    const workpiece = 'BLUE';
    const workpieceId = 'workpieceId';
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: prodStepId,
      moduleType: ModuleType.HBW,
      command: ModuleCommandType.DROP,
      startedAt: MOCKED_DATE,
    };
    const activeOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [prodStep],
      state: OrderState.IN_PROGRESS,
      startedAt: MOCKED_DATE,
      workpieceId,
    };

    underTest['activeOrders'] = [activeOrder];
    underTest['orderQueue'] = [activeOrder];

    jest.spyOn(underTest, 'startNextOrder').mockResolvedValue();
    jest.spyOn(underTest, 'retriggerFTSSteps').mockResolvedValue(0);
    jest.spyOn(underTest, 'sendOrderListUpdate').mockResolvedValue(undefined);
    jest.spyOn(StockManagementService, 'removeReservation').mockReturnValue();

    await underTest.handleActionUpdate(orderId, prodStepId, State.FINISHED);
    expect(StockManagementService.removeReservation).toHaveBeenCalledWith(activeOrder.orderId);
  });
  it('should not remove bay reservations after a non-storage pick has finished', async () => {
    const orderId = 'orderId';
    const prodStepId = 'prodStepId';
    const workpiece = 'BLUE';
    const workpieceId = 'workpieceId';
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: prodStepId,
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.PICK,
      startedAt: MOCKED_DATE,
    };
    const activeOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [prodStep],
      state: OrderState.IN_PROGRESS,
      startedAt: MOCKED_DATE,
      workpieceId,
    };

    underTest['activeOrders'] = [activeOrder];
    underTest['orderQueue'] = [activeOrder];

    jest.spyOn(underTest, 'startNextOrder').mockResolvedValue();
    jest.spyOn(underTest, 'retriggerFTSSteps').mockResolvedValue(0);
    jest.spyOn(underTest, 'sendOrderListUpdate').mockResolvedValue(undefined);
    jest.spyOn(StockManagementService, 'removeReservation').mockReturnValue();

    await underTest.handleActionUpdate(orderId, prodStepId, State.FINISHED);
    expect(StockManagementService.removeReservation).not.toHaveBeenCalled();
  });

  it('should not remove bay reservations after a non-storage drop has finished', async () => {
    const orderId = 'orderId';
    const prodStepId = 'prodStepId';
    const workpiece = 'BLUE';
    const workpieceId = 'workpieceId';
    const prodStep: OrderManufactureStep = {
      type: 'MANUFACTURE',
      state: OrderState.IN_PROGRESS,
      id: prodStepId,
      moduleType: ModuleType.DRILL,
      command: ModuleCommandType.DROP,
      startedAt: MOCKED_DATE,
    };
    const activeOrder: OrderResponse = {
      orderType: 'PRODUCTION',
      orderId,
      type: workpiece,
      timestamp: MOCKED_DATE,
      productionSteps: [prodStep],
      state: OrderState.IN_PROGRESS,
      startedAt: MOCKED_DATE,
      workpieceId,
    };

    underTest['activeOrders'] = [activeOrder];
    underTest['orderQueue'] = [activeOrder];

    jest.spyOn(underTest, 'startNextOrder').mockResolvedValue();
    jest.spyOn(underTest, 'retriggerFTSSteps').mockResolvedValue(0);
    jest.spyOn(underTest, 'sendOrderListUpdate').mockResolvedValue(undefined);
    jest.spyOn(StockManagementService, 'removeReservation').mockReturnValue();

    await underTest.handleActionUpdate(orderId, prodStepId, State.FINISHED);
    expect(StockManagementService.removeReservation).not.toHaveBeenCalled();
  });

  it('should start the next order if resuming without active orders', async () => {
    jest.spyOn(underTest, 'hasActiveOrders').mockReturnValue(false);
    jest.spyOn(underTest, 'startNextOrder').mockResolvedValue();
    jest.spyOn(underTest, 'retriggerFTSSteps').mockResolvedValue(1);
    jest.spyOn(underTest, 'retriggerModuleSteps').mockResolvedValue(1);
    jest.spyOn(underTest, 'sendOrderListUpdate').mockResolvedValue();
    await underTest.resumeOrders();
    expect(underTest.startNextOrder).toHaveBeenCalled();
    expect(underTest.retriggerModuleSteps).not.toHaveBeenCalled();
    expect(underTest.retriggerFTSSteps).not.toHaveBeenCalled();
  });

  it('should retrigger the queued steps if resuming with an active orders', async () => {
    jest.spyOn(underTest, 'hasActiveOrders').mockReturnValue(true);
    jest.spyOn(underTest, 'startNextOrder').mockResolvedValue();
    jest.spyOn(underTest, 'retriggerFTSSteps').mockResolvedValue(1);
    jest.spyOn(underTest, 'retriggerModuleSteps').mockResolvedValue(1);
    jest.spyOn(underTest, 'sendOrderListUpdate').mockResolvedValue();
    await underTest.resumeOrders();
    expect(underTest.startNextOrder).not.toHaveBeenCalled();
    expect(underTest.retriggerModuleSteps).toHaveBeenCalled();
    expect(underTest.retriggerFTSSteps).toHaveBeenCalled();
  });
});
