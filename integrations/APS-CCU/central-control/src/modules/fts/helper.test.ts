import crypto from 'node:crypto';
import { AvailableState, DeviceType, PairedModule } from '../../../../common/protocol/ccu';
import { FtsCommandType, FtsErrors, FtsState, NODE_ID_UNKNOWN } from '../../../../common/protocol/fts';
import { ModuleType } from '../../../../common/protocol/module';
import { InstantAction, InstantActions, State, VdaError } from '../../../../common/protocol/vda';
import { createMockMqttClient } from '../../test-helpers';
import { FactoryLayoutService } from '../layout/factory-layout-service';
import { OrderManagement } from '../order/management/order-management';
import { FtsPairingStates } from '../pairing/fts-pairing-states';
import { PairingStates } from '../pairing/pairing-states';
import { sendResetModuleInstantAction } from '../production/production';
import {
  checkChargerAvailability,
  getLastModuleSerialNumber,
  handleFtsState,
  handleResetWarning,
  sendClearLoadFtsInstantAction,
  updateFtsAvailability,
  updateFtsBlockedNodes,
} from './helper';

jest.mock('../production/production', () => {
  return {
    sendResetModuleInstantAction: jest.fn(),
  };
});
jest.mock('../pairing/fts-pairing-states');
jest.mock('../pairing/pairing-states');
jest.mock('../order/management/order-management');
jest.mock('./charge', () => {
  return {
    freeBlockedChargers: jest.fn(),
    handleChargingUpdate: jest.fn(),
    isBatteryLow: jest.fn(),
    retriggerChargeOrders: jest.fn(),
    triggerChargeOrderForFts: jest.fn(),
  };
});
describe('Test sending production commands', () => {
  beforeEach(() => {
    jest.spyOn(FtsPairingStates, 'getInstance').mockReturnValue({
      updateAvailability: jest.fn(),
      getLastFinishedDockId: jest.fn(),
      setLastFinishedDockId: jest.fn(),
    } as unknown as FtsPairingStates);
    jest.spyOn(OrderManagement, 'getInstance').mockReturnValue({
      getTargetModuleTypeForNavActionId: jest.fn(),
      getWorkpieceType: jest.fn(),
      isOrderActionRunning: jest.fn(),
      getActiveOrder: jest.fn(),
    } as unknown as OrderManagement);
    jest.spyOn(PairingStates, 'getInstance').mockReturnValue({
      getModuleForOrder: jest.fn(),
      getForModuleType: jest.fn(),
      clearModuleForOrder: jest.fn(),
      getAllReady: jest.fn<PairedModule[], PairedModule[]>(() => []),
    } as unknown as PairingStates);
    jest.spyOn(FactoryLayoutService, 'releaseNodesBefore').mockReturnValue();
  });

  afterEach(() => {
    OrderManagement['instance'] = undefined as unknown as OrderManagement;
    jest.clearAllMocks();
    jest.restoreAllMocks();
  });

  it('should create the correct busy state from the fts state if driving', async () => {
    const orderId = 'ID';
    const state: FtsState = {
      serialNumber: 'mocked',
      timestamp: new Date(),
      paused: false,
      driving: true,
      errors: [],
      orderId: orderId,
      nodeStates: [],
      edgeStates: [],
      lastNodeSequenceId: 0,
      lastNodeId: '1',
      load: [],
      orderUpdateId: 0,
    };

    await updateFtsAvailability(state);
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      'mocked',
      AvailableState.BUSY,
      orderId,
      state.lastNodeId,
      undefined,
    );
    expect(PairingStates.getInstance().getForModuleType).not.toHaveBeenCalled();
    expect(OrderManagement.getInstance().getTargetModuleTypeForNavActionId).not.toHaveBeenCalled();
  });

  it('should create the correct busy state from the fts state if waiting for load handler', async () => {
    const orderId = 'ID';
    const actionId = 'actionId';
    const moduleSerialNumber = 'moduleSerialNumber';
    const state: FtsState = {
      serialNumber: 'mocked',
      timestamp: new Date(),
      paused: false,
      driving: false,
      waitingForLoadHandling: true,
      errors: [],
      orderId: orderId,
      nodeStates: [],
      edgeStates: [],
      lastNodeSequenceId: 0,
      lastNodeId: '2',
      load: [],
      orderUpdateId: 0,
      actionState: {
        state: State.FINISHED,
        command: FtsCommandType.DOCK,
        timestamp: new Date(),
        id: actionId,
      },
    };

    jest.spyOn(OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(ModuleType.DPS);
    jest.spyOn(PairingStates.getInstance(), 'getForModuleType').mockReturnValue({
      serialNumber: moduleSerialNumber,
      connected: true,
      available: AvailableState.READY,
      type: 'MODULE',
    });
    await updateFtsAvailability(state);
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      'mocked',
      AvailableState.BUSY,
      orderId,
      state.lastNodeId,
      moduleSerialNumber,
    );
    expect(OrderManagement.getInstance().getTargetModuleTypeForNavActionId).toHaveBeenCalledWith(actionId);
  });

  it('should create the correct ready state from the fts state if the action was DOCK', async () => {
    const orderId = 'ID';
    const actionId = 'actionId';
    const moduleSerialNumber = 'moduleSerialNumber';
    const state: FtsState = {
      serialNumber: 'mocked',
      timestamp: new Date(),
      paused: false,
      driving: false,
      waitingForLoadHandling: false,
      errors: [],
      orderId: orderId,
      nodeStates: [],
      edgeStates: [],
      lastNodeSequenceId: 0,
      lastNodeId: '2',
      load: [],
      orderUpdateId: 0,
      actionState: {
        state: State.FINISHED,
        command: FtsCommandType.DOCK,
        timestamp: new Date(),
        id: actionId,
      },
    };

    jest.spyOn(OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(ModuleType.DPS);
    jest.spyOn(PairingStates.getInstance(), 'getForModuleType').mockReturnValue({
      serialNumber: moduleSerialNumber,
      connected: true,
      available: AvailableState.READY,
      type: 'MODULE',
    });
    await updateFtsAvailability(state);
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      'mocked',
      AvailableState.READY,
      undefined,
      state.lastNodeId,
      moduleSerialNumber,
    );
    expect(OrderManagement.getInstance().getTargetModuleTypeForNavActionId).toHaveBeenCalledWith(actionId);
  });

  it('should create the correct ready state from the fts state if the action was TURN but is referenced in the order management', async () => {
    const orderId = 'ID';
    const actionId = 'actionId';
    const dpsSerial = 'dpsSerial';
    const state: FtsState = {
      serialNumber: 'mocked',
      timestamp: new Date(),
      paused: false,
      driving: false,
      waitingForLoadHandling: false,
      errors: [],
      orderId: orderId,
      nodeStates: [],
      edgeStates: [],
      lastNodeSequenceId: 0,
      lastNodeId: '2',
      load: [],
      orderUpdateId: 0,
      actionState: {
        state: State.FINISHED,
        command: FtsCommandType.TURN,
        timestamp: new Date(),
        id: actionId,
      },
    };

    const pairedModule: PairedModule = {
      serialNumber: dpsSerial,
      type: 'MODULE',
      subType: ModuleType.DPS,
    };

    jest.spyOn(OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(ModuleType.DPS);
    jest.spyOn(PairingStates.getInstance(), 'getForModuleType').mockReturnValue(pairedModule);
    await updateFtsAvailability(state);
    expect(OrderManagement.getInstance().getTargetModuleTypeForNavActionId).toHaveBeenCalledWith(actionId);
    expect(PairingStates.getInstance().getForModuleType).toHaveBeenCalledWith(ModuleType.DPS, orderId);
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      'mocked',
      AvailableState.READY,
      undefined,
      state.lastNodeId,
      dpsSerial,
    );
  });

  it('should create the correct ready state from the fts state for any successful none docking action', async () => {
    const orderId = 'ID';
    const ftsSerialNumber = 'mocked';
    OrderManagement.getInstance().getOrderForWorkpieceId = jest.fn();
    PairingStates.getInstance().getForModuleType = jest.fn();
    for (const command of Object.values(FtsCommandType)) {
      if (command === FtsCommandType.DOCK) {
        continue;
      }

      const state: FtsState = {
        serialNumber: ftsSerialNumber,
        timestamp: new Date(),
        paused: false,
        driving: false,
        errors: [],
        orderId: orderId,
        nodeStates: [],
        edgeStates: [],
        lastNodeSequenceId: 0,
        lastNodeId: '',
        load: [],
        orderUpdateId: 0,
        actionState: {
          state: State.FINISHED,
          command,
          timestamp: new Date(),
          id: 'actionId',
        },
      };
      await updateFtsAvailability(state);
      expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
        ftsSerialNumber,
        AvailableState.READY,
        undefined,
        '',
        undefined,
      );
      expect(OrderManagement.getInstance().getOrderForWorkpieceId).not.toHaveBeenCalled();
      expect(PairingStates.getInstance().getForModuleType).not.toHaveBeenCalled();
    }
  });

  it('should set the correct position state from the ready fts state without action, on FTS start', async () => {
    const nodeId = NODE_ID_UNKNOWN;
    const stateNoAction: FtsState = {
      serialNumber: 'mocked',
      timestamp: new Date(),
      paused: false,
      driving: false,
      errors: [],
      orderId: '',
      nodeStates: [],
      edgeStates: [],
      lastNodeSequenceId: 0,
      lastNodeId: nodeId,
      load: [],
      orderUpdateId: 0,
    };
    await updateFtsAvailability(stateNoAction);
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      'mocked',
      AvailableState.BLOCKED,
      stateNoAction.orderId,
      nodeId,
    );
  });

  it('should set the correct node position from the ready fts state with an incomplete action', async () => {
    // As of FITEFF22-426, road nodes are only numeric, a not-numeric node is a module id
    const nodeId = '1';
    const moduleType = ModuleType.DPS;
    const dockActionId = 'dockActionId';
    const orderId = 'orderId';
    const targetSpy = jest.spyOn(OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(moduleType);
    const stateNoAction: FtsState = {
      serialNumber: 'mocked',
      timestamp: new Date(),
      paused: false,
      driving: false,
      errors: [],
      orderId,
      nodeStates: [],
      edgeStates: [],
      lastNodeSequenceId: 0,
      lastNodeId: nodeId,
      load: [],
      orderUpdateId: 0,
      actionState: {
        id: dockActionId,
        state: State.RUNNING,
        command: FtsCommandType.DOCK,
        timestamp: new Date(),
      },
    };
    await updateFtsAvailability(stateNoAction);
    expect(targetSpy).not.toHaveBeenCalled();
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      'mocked',
      AvailableState.BUSY,
      orderId,
      nodeId,
      undefined,
    );

    jest.clearAllMocks();
    const nodeId2 = '1nodeId-23';
    stateNoAction.lastNodeId = nodeId2;
    await updateFtsAvailability(stateNoAction);
    expect(targetSpy).not.toHaveBeenCalled();
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      'mocked',
      AvailableState.BUSY,
      orderId,
      nodeId2,
      nodeId2,
    );
  });

  it('should create the correct blocked state from the fts state', async () => {
    const orderId = '';
    const state: FtsState = {
      serialNumber: 'mocked',
      timestamp: new Date(),
      paused: true,
      driving: false,
      errors: [],
      orderId: orderId,
      nodeStates: [],
      edgeStates: [],
      lastNodeSequenceId: 0,
      lastNodeId: '',
      load: [],
      orderUpdateId: 0,
    };
    await updateFtsAvailability(state);
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      'mocked',
      AvailableState.BLOCKED,
      orderId,
      state.lastNodeId,
    );

    const state2: FtsState = {
      serialNumber: 'mocked',
      timestamp: new Date(),
      paused: false,
      driving: false,
      errors: [{ errorType: 'SAMPLE_ERROR', errorLevel: 'WARNING', timestamp: new Date() }],
      orderId: orderId,
      nodeStates: [],
      edgeStates: [],
      lastNodeSequenceId: 0,
      lastNodeId: '',
      load: [],
      orderUpdateId: 0,
    };
    await updateFtsAvailability(state2);
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      'mocked',
      AvailableState.BLOCKED,
      orderId,
      state.lastNodeId,
    );
  });

  it('should set the FTS blocked when it is at the UNKNOWN node', async () => {
    const orderId = '';
    const state: FtsState = {
      serialNumber: 'mocked',
      timestamp: new Date(),
      paused: false,
      driving: false,
      errors: [],
      orderId: orderId,
      nodeStates: [],
      edgeStates: [],
      lastNodeSequenceId: 0,
      lastNodeId: 'UNKNOWN',
      load: [],
      orderUpdateId: 0,
    };
    await updateFtsAvailability(state);
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      'mocked',
      AvailableState.BLOCKED,
      orderId,
      state.lastNodeId,
    );
  });

  it('should delete all associated actions for an order reset and reset the loading bay for the fts', async () => {
    const orderId = 'orderId';
    const serialNumber = 'mocked';
    const workpieceOrderId = 'workpieceOrderId';
    const resetWarning: Array<VdaError> = [
      {
        errorType: FtsErrors.RESET,
        timestamp: new Date(),
        errorLevel: 'WARNING',
        errorReferences: [{ referenceKey: 'orderId', referenceValue: orderId }],
      },
    ];
    const assignedModule: PairedModule = {
      type: 'MODULE',
      serialNumber: 'xyz',
    };

    FtsPairingStates.getInstance().resetLoadingBay = jest.fn();
    FtsPairingStates.getInstance().getLoadedOrderIds = jest.fn().mockReturnValue([workpieceOrderId]);
    PairingStates.getInstance().getModuleForOrder = jest.fn().mockReturnValue(assignedModule);

    OrderManagement.getInstance().resetOrder = jest.fn().mockResolvedValue(Promise.resolve());
    OrderManagement.getInstance().getOrderForWorkpieceId = jest.fn();

    await handleResetWarning(resetWarning, serialNumber);
    expect(OrderManagement.getInstance().getOrderForWorkpieceId).not.toHaveBeenCalled();
    expect(OrderManagement.getInstance().resetOrder).toHaveBeenCalledWith(workpieceOrderId);
    expect(OrderManagement.getInstance().resetOrder).toHaveBeenCalledWith(orderId);
    expect(PairingStates.getInstance().clearModuleForOrder).toHaveBeenCalledWith(workpieceOrderId);
    expect(PairingStates.getInstance().getModuleForOrder).toHaveBeenCalledWith(orderId);
    expect(PairingStates.getInstance().clearModuleForOrder).toHaveBeenCalledWith(orderId);
    expect(sendResetModuleInstantAction).toHaveBeenCalledWith(assignedModule.serialNumber);
    expect(FtsPairingStates.getInstance().getLoadedOrderIds).toHaveBeenCalledWith(serialNumber);
    expect(FtsPairingStates.getInstance().resetLoadingBay).toHaveBeenCalledWith(serialNumber);
    expect(FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(
      serialNumber,
      AvailableState.READY,
      undefined,
      NODE_ID_UNKNOWN,
      NODE_ID_UNKNOWN,
    );
  });

  it('should send an instant action to an FTS', async () => {
    const serialNumber = 'FTS1';

    const topic = `fts/v1/ff/${serialNumber}/instantAction`;
    const date = new Date('2021-01-01T00:00:00.000Z');
    const mockedUUID = 'mockedUUID';
    const orderId = 'orderId';

    // create jest mocks
    const mqttClientMock = createMockMqttClient();

    jest.useFakeTimers().setSystemTime(date);
    jest.mock('node:crypto');
    crypto.randomUUID = jest.fn().mockReturnValue(mockedUUID);

    await sendClearLoadFtsInstantAction(orderId, serialNumber, false);

    const expectedInstantAction: InstantAction = {
      serialNumber,
      timestamp: new Date(),
      actions: [
        {
          actionId: mockedUUID,
          actionType: InstantActions.CLEAR_LOAD_HANDLER,
          metadata: {
            loadDropped: false,
          },
        },
      ],
    };

    expect(OrderManagement.getInstance().getWorkpieceType).toHaveBeenCalledWith(orderId);
    expect(mqttClientMock.publish).toHaveBeenCalledWith(topic, JSON.stringify(expectedInstantAction));
    jest.clearAllMocks();
    jest.clearAllTimers();
    jest.useRealTimers();
  });

  it('should re-trigger navigation steps if FTS finished the turn at the start node', async () => {
    const actionId = 'actionId';
    const orderId = 'orderId';
    const lastNodeId = '6';
    const serialNumber = 'eBix';
    const ftsStateJson = `
    {
        "actionState": {
            "command": "TURN",
            "id": "${actionId}",
            "state": "FINISHED",
            "timestamp": "2023-04-21T06:04:59.876591Z"
        },
        "actionStates": [
            {
                "command": "PASS",
                "id": "ebf2b8d6-def2-4788-a8da-34b7fddaa3e6",
                "state": "FINISHED",
                "timestamp": "2023-04-21T06:04:45.453062Z"
            },
            {
                "command": "TURN",
                "id": "3e89d406-4cf8-4c37-8286-6e3af4c4f983",
                "state": "FINISHED",
                "timestamp": "2023-04-21T06:04:53.586752Z"
            },
            {
                "command": "TURN",
                "id": "6823729f-5d8a-462e-9e9e-5936272d0100",
                "state": "FINISHED",
                "timestamp": "2023-04-21T06:04:59.876591Z"
            }
        ],
        "batteryState": {},
        "driving": false,
        "edgeStates": [],
        "errors": [],
        "headerId": 54,
        "lastCode": "",
        "lastNodeId": "${lastNodeId}",
        "lastNodeSequenceId": 0,
        "load": [
            {
                "loadId": null,
                "loadPosition": "1",
                "loadType": null
            }
        ],
        "nodeStates": [],
        "orderId": "${orderId}",
        "orderUpdateId": 4,
        "paused": false,
        "serialNumber": "${serialNumber}",
        "timestamp": "2023-04-21T06:04:59.891309Z",
        "waitingForLoadHandling": false
    }`;
    const ftsState = JSON.parse(ftsStateJson);

    OrderManagement.getInstance().retriggerFTSSteps = jest.fn().mockResolvedValue(Promise.resolve());

    await handleFtsState(ftsState);

    expect(FactoryLayoutService.releaseNodesBefore).toHaveBeenCalledWith(serialNumber, lastNodeId);
    expect(OrderManagement.getInstance().retriggerFTSSteps).toHaveBeenCalled();
  });

  it('should return the correct last module serialNumber for an fts state', () => {
    const orderId = 'orderId';
    const modSerial = 'modSerial';
    const actionId = 'actionId';
    const targetModuleType = ModuleType.MILL;

    const ftsState: FtsState = {
      serialNumber: 'FTS1',
      orderId,
      nodeStates: [],
      orderUpdateId: 0,
      paused: false,
      errors: [],
      lastNodeSequenceId: 0,
      timestamp: new Date(),
      load: [],
      driving: false,
      edgeStates: [],
      lastNodeId: '1',
      waitingForLoadHandling: false,
      actionState: {
        state: State.FINISHED,
        id: actionId,
        timestamp: new Date(),
      },
    };

    const targetModule: PairedModule = {
      type: 'MODULE',
      serialNumber: modSerial,
    };

    jest.spyOn(OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(targetModuleType);
    jest.spyOn(PairingStates.getInstance(), 'getForModuleType').mockReturnValue(targetModule);

    const actual = getLastModuleSerialNumber(ftsState);

    expect(actual).toBeDefined();
    expect(actual).toEqual(modSerial);
    expect(OrderManagement.getInstance().getTargetModuleTypeForNavActionId).toHaveBeenCalledWith(actionId);
    expect(PairingStates.getInstance().getForModuleType).toHaveBeenCalledWith(targetModuleType, orderId);
  });

  it('should return the correct last module serialNumber for an fts state with module id as node id', () => {
    const orderId = 'orderId';
    const modSerial = 'modSerial';
    const actionId = 'actionId';
    const targetModuleType = ModuleType.MILL;

    const ftsState: FtsState = {
      serialNumber: 'FTS1',
      orderId,
      nodeStates: [],
      orderUpdateId: 0,
      paused: false,
      errors: [],
      lastNodeSequenceId: 0,
      timestamp: new Date(),
      load: [],
      driving: false,
      edgeStates: [],
      lastNodeId: modSerial,
      waitingForLoadHandling: false,
      actionState: {
        state: State.FINISHED,
        id: actionId,
        timestamp: new Date(),
      },
    };

    const targetModule: PairedModule = {
      type: 'MODULE',
      serialNumber: 'mocked',
    };

    jest.spyOn(OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(targetModuleType);
    jest.spyOn(PairingStates.getInstance(), 'getForModuleType').mockReturnValue(targetModule);

    const actual = getLastModuleSerialNumber(ftsState);

    expect(actual).toBeDefined();
    expect(actual).toEqual(modSerial);
    expect(OrderManagement.getInstance().getTargetModuleTypeForNavActionId).not.toHaveBeenCalled();
    expect(PairingStates.getInstance().getForModuleType).not.toHaveBeenCalled();
  });

  it('should return true, if the available charger is ready', () => {
    jest.spyOn(PairingStates.getInstance(), 'getAllReady').mockReturnValue([
      {
        serialNumber: 'CHRG1',
        connected: true,
        available: AvailableState.READY,
        type: DeviceType.MODULE,
        subType: ModuleType.CHRG,
      },
    ]);
    const hasChargerAvailable = checkChargerAvailability();
    expect(hasChargerAvailable).toBeTruthy();
  });

  it('should return false, if the available charger is not ready', () => {
    const hasChargerAvailable = checkChargerAvailability();
    expect(hasChargerAvailable).toBeFalsy();
  });

  describe('Verify updateFtsBlockedNodes function', () => {
    const FTS_TEMPLATE: FtsState = {
      serialNumber: 'someFts',
      timestamp: new Date(),
      orderId: 'someOrder',
      orderUpdateId: 0,
      lastNodeId: NODE_ID_UNKNOWN,
      lastNodeSequenceId: 0,
      nodeStates: [],
      edgeStates: [],
      driving: false,
      paused: false,
      errors: [],
      load: [],
    };
    let isOrderActionRunningMOCK: jest.SpyInstance,
      getActiveOrderMOCK: jest.SpyInstance,
      getLastFinishedDockIdMOCK: jest.SpyInstance,
      setLastFinishedDockIdMOCK: jest.SpyInstance,
      releaseAllNodesMOCK: jest.SpyInstance,
      releaseAllNodesExceptMOCK: jest.SpyInstance,
      releaseNodesBeforeMOCK: jest.SpyInstance;

    beforeEach(() => {
      isOrderActionRunningMOCK = jest.spyOn(OrderManagement.getInstance(), 'isOrderActionRunning').mockReturnValue(false);
      getActiveOrderMOCK = jest.spyOn(OrderManagement.getInstance(), 'getActiveOrder').mockReturnValue(undefined);
      getLastFinishedDockIdMOCK = jest.spyOn(FtsPairingStates.getInstance(), 'getLastFinishedDockId').mockReturnValue(undefined);
      setLastFinishedDockIdMOCK = jest.spyOn(FtsPairingStates.getInstance(), 'setLastFinishedDockId').mockReturnValue(undefined);
      releaseAllNodesMOCK = jest.spyOn(FactoryLayoutService, 'releaseAllNodes').mockReturnValue(undefined);
      releaseAllNodesExceptMOCK = jest.spyOn(FactoryLayoutService, 'releaseAllNodesExcept').mockReturnValue(undefined);
      releaseNodesBeforeMOCK = jest.spyOn(FactoryLayoutService, 'releaseNodesBefore').mockReturnValue(undefined);
    });

    afterEach(() => {
      jest.clearAllMocks();
    });

    test('should release all nodes when lastNodeId is NODE_ID_UNKNOWN', () => {
      const state: FtsState = { ...FTS_TEMPLATE, lastNodeId: NODE_ID_UNKNOWN, serialNumber: 'serial123' };
      updateFtsBlockedNodes(state);
      expect(releaseAllNodesMOCK).toHaveBeenCalledWith('serial123');
    });

    test('should release nodes before lastNodeId when actionState is null or undefined', () => {
      const state: FtsState = { ...FTS_TEMPLATE, lastNodeId: 'node123', serialNumber: 'serial456' };
      updateFtsBlockedNodes({ ...state, actionState: null });
      expect(releaseNodesBeforeMOCK).toHaveBeenCalledWith('serial456', 'node123');
      updateFtsBlockedNodes({ ...state, actionState: undefined });
      expect(releaseNodesBeforeMOCK).toHaveBeenCalledWith('serial456', 'node123');
    });

    test('should release all nodes except lastNodeId when FTS is docked and it is a running dock action', () => {
      const state: FtsState = {
        ...FTS_TEMPLATE,
        lastNodeId: 'node123',
        serialNumber: 'serial456',
        actionState: { state: State.FINISHED, command: FtsCommandType.DOCK, id: 'dock123', timestamp: new Date() },
        orderId: 'order456',
      };
      isOrderActionRunningMOCK.mockReturnValue(true); // Mocking condition to true
      getActiveOrderMOCK.mockReturnValue({ placeholder: true });
      updateFtsBlockedNodes(state);
      expect(releaseAllNodesExceptMOCK).toHaveBeenCalledWith('serial456', 'node123');
      expect(setLastFinishedDockIdMOCK).toHaveBeenCalledWith('serial456', 'dock123');
    });

    test('should release all nodes except lastNodeId when FTS is docked and the dock action is not handled', () => {
      const state: FtsState = {
        ...FTS_TEMPLATE,
        lastNodeId: 'node123',
        serialNumber: 'serial456',
        actionState: { state: State.FINISHED, command: FtsCommandType.DOCK, id: 'dock123', timestamp: new Date() },
        orderId: 'order456',
      };
      isOrderActionRunningMOCK.mockReturnValue(false);
      getActiveOrderMOCK.mockReturnValue(undefined);
      getLastFinishedDockIdMOCK.mockReturnValue('differentDockId');
      updateFtsBlockedNodes(state);
      expect(releaseAllNodesExceptMOCK).toHaveBeenCalledWith('serial456', 'node123');
      expect(setLastFinishedDockIdMOCK).toHaveBeenCalledWith('serial456', 'dock123');
    });

    test('should not release nodes when FTS is docked and the order action had been handled', () => {
      const state: FtsState = {
        ...FTS_TEMPLATE,
        lastNodeId: 'node123',
        serialNumber: 'serial456',
        actionState: { state: State.FINISHED, command: FtsCommandType.DOCK, id: 'dock123', timestamp: new Date() },
        orderId: 'order456',
      };

      isOrderActionRunningMOCK.mockReturnValue(false); // Mocking condition to false
      getActiveOrderMOCK.mockReturnValue({ placeholder: true });
      getLastFinishedDockIdMOCK.mockReturnValue('differentDockId'); // Mocking condition to true
      updateFtsBlockedNodes(state);
      expect(FactoryLayoutService.releaseAllNodesExcept).not.toHaveBeenCalled();
      expect(FactoryLayoutService.releaseNodesBefore).not.toHaveBeenCalled();
      expect(setLastFinishedDockIdMOCK).toHaveBeenCalledWith('serial456', 'dock123');
    });

    test('should not release nodes when FTS is docked and the dock action is the latest handled', () => {
      const state: FtsState = {
        ...FTS_TEMPLATE,
        lastNodeId: 'node123',
        serialNumber: 'serial456',
        actionState: { state: State.FINISHED, command: FtsCommandType.DOCK, id: 'dock123', timestamp: new Date() },
        orderId: 'order456',
      };

      isOrderActionRunningMOCK.mockReturnValue(false); // Mocking condition to false
      getActiveOrderMOCK.mockReturnValue(undefined);
      getLastFinishedDockIdMOCK.mockReturnValue('dock123'); // Mocking condition to true
      updateFtsBlockedNodes(state);
      expect(FactoryLayoutService.releaseAllNodesExcept).not.toHaveBeenCalled();
      expect(FactoryLayoutService.releaseNodesBefore).not.toHaveBeenCalled();
      expect(setLastFinishedDockIdMOCK).toHaveBeenCalledWith('serial456', 'dock123');
    });

    test('should release nodes before lastNodeId for any other scenario', () => {
      const state: FtsState = { ...FTS_TEMPLATE, lastNodeId: 'node123', serialNumber: 'serial456' };
      updateFtsBlockedNodes(state);
      expect(FactoryLayoutService.releaseNodesBefore).toHaveBeenCalledWith('serial456', 'node123');
    });
  });
});
