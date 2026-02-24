import fs from 'node:fs';
import path from 'node:path';
import { AvailableState } from '../../../../common/protocol/ccu';
import { ModuleCommandType, ModuleState, ModuleType } from '../../../../common/protocol/module';
import { ActionState, Factsheet, Load, LoadType, State } from '../../../../common/protocol/vda';
import * as ftsHelper from '../fts/helper';
import { OrderManagement } from '../order/management/order-management';
import { FtsPairingStates } from '../pairing/fts-pairing-states';
import { PairingStates } from '../pairing/pairing-states';
import { clearLoadingBay, handleModuleAvailability, updateFtsLoadHandler, updateOrderWorkpieceId } from './index';

jest.mock('../pairing/pairing-states');
jest.mock('../pairing/fts-pairing-states');
jest.mock('../order/management/order-management');
describe('test production update handling', () => {
  let pairingStates: PairingStates;
  let ftsPairingStates: FtsPairingStates;
  let orderManagement: OrderManagement;

  beforeEach(() => {
    pairingStates = {
      updateAvailability: jest.fn(),
      getFactsheet: jest.fn(),
      getWorkpieceId: jest.fn(),
      getModuleType: jest.fn(),
      get: jest.fn(),
    } as unknown as PairingStates;
    PairingStates.getInstance = jest.fn().mockReturnValue(pairingStates);
    ftsPairingStates = {
      clearLoadingBay: jest.fn(),
      getFtsSerialNumberForOrderId: jest.fn(),
      getLoadingBayForWorkpiece: jest.fn(),
    } as unknown as FtsPairingStates;
    jest.spyOn(FtsPairingStates, 'getInstance').mockReturnValue(ftsPairingStates);
    orderManagement = {
      getWorkpieceId: jest.fn(),
      updateOrderWorkpieceId: jest.fn(),
    } as unknown as OrderManagement;
    OrderManagement.getInstance = jest.fn().mockReturnValue(orderManagement);
  });

  afterEach(() => {
    jest.restoreAllMocks();
    jest.useRealTimers();
  });

  it('should update the pairing state as READY if an drop workpiece was successful', async () => {
    const orderId = 'orderId';
    const serialNumber = 'serialNumber';
    const moduleType = ModuleType.AIQS;
    const actionState: ActionState<ModuleCommandType> = {
      state: State.FINISHED,
      command: ModuleCommandType.DROP,
      timestamp: new Date(),
      id: 'actionStateId',
    };
    const load: Load = {
      loadId: 'loadId',
      loadType: LoadType.WHITE,
      loadPosition: '1',
    };

    const moduleState: ModuleState = {
      actionState: actionState,
      orderId,
      errors: [],
      orderUpdateId: 0,
      type: moduleType,
      timestamp: new Date(),
      paused: false,
      serialNumber,
      loads: [load],
    };

    await handleModuleAvailability(moduleState);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, AvailableState.READY);
  });

  it('should not update the availability for the passive instant action "factsheetRequest" because it does not matter for the availability state of a module', async () => {
    const serialNumber = 'yBix';
    const hbwStateJson = `{
      "actionState": {
          "command": "factsheetRequest",
          "id": "0876448e-fdd2-4cd8-846c-08ef007bb8b9",
          "state": "FINISHED",
          "timestamp": "2023-05-04T13:57:24.701372Z"
      },
      "batteryState": {},
      "errors": [],
      "headerId": 16,
      "loads": [
          {
              "loadId": "",
              "loadPosition": "B1",
              "loadType": "BLUE"
          },
          {
              "loadId": "",
              "loadPosition": "A2",
              "loadType": "NONE"
          }
      ],
      "orderId": "34affed8-94e3-4955-bae0-036b464ef705",
      "orderUpdateId": 1,
      "paused": false,
      "serialNumber": "${serialNumber}",
      "timestamp": "2023-05-04T13:57:24.698860Z"
    }`;
    const hbwState = JSON.parse(hbwStateJson) as ModuleState;

    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: serialNumber,
      type: 'MODULE',
      available: AvailableState.BUSY,
    });

    await handleModuleAvailability(hbwState);

    expect(pairingStates.updateAvailability).not.toHaveBeenCalled();

    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: serialNumber,
      type: 'MODULE',
      available: AvailableState.READY,
    });

    await handleModuleAvailability(hbwState);

    expect(pairingStates.updateAvailability).not.toHaveBeenCalled();

    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: serialNumber,
      type: 'MODULE',
      available: AvailableState.BLOCKED,
    });

    await handleModuleAvailability(hbwState);

    expect(pairingStates.updateAvailability).not.toHaveBeenCalled();
  });

  it('should update the availability for the active instant action "stopCalibration" in state "FINISHED" because it does matter for the availability state of a module', async () => {
    const serialNumber = 'yBix';
    const hbwStateJson = `{
      "actionState": {
          "command": "stopCalibration",
          "id": "0876448e-fdd2-4cd8-846c-08ef007bb8b9",
          "state": "FINISHED",
          "timestamp": "2023-05-04T13:57:24.701372Z"
      },
      "batteryState": {},
      "errors": [],
      "headerId": 16,
      "loads": [
          {
              "loadId": "",
              "loadPosition": "B1",
              "loadType": "BLUE"
          },
          {
              "loadId": "",
              "loadPosition": "A2",
              "loadType": "NONE"
          }
      ],
      "orderId": "34affed8-94e3-4955-bae0-036b464ef705",
      "orderUpdateId": 1,
      "paused": false,
      "serialNumber": "${serialNumber}",
      "timestamp": "2023-05-04T13:57:24.698860Z"
    }`;
    const hbwState = JSON.parse(hbwStateJson) as ModuleState;

    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: serialNumber,
      type: 'MODULE',
      available: AvailableState.BUSY,
    });

    await handleModuleAvailability(hbwState);

    expect(pairingStates.updateAvailability).toBeCalledWith('yBix', AvailableState.READY);

    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: serialNumber,
      type: 'MODULE',
      available: AvailableState.READY,
    });

    await handleModuleAvailability(hbwState);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith('yBix', AvailableState.READY);

    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: serialNumber,
      type: 'MODULE',
      available: AvailableState.BLOCKED,
    });

    await handleModuleAvailability(hbwState);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith('yBix', AvailableState.READY);
  });

  it('should update the availability for the active instant action "stopCalibration" in state "RUNNING" because it does matter for the availability state of a module', async () => {
    const serialNumber = 'yBix';
    const hbwStateJson = `{
      "actionState": {
          "command": "stopCalibration",
          "id": "0876448e-fdd2-4cd8-846c-08ef007bb8b9",
          "state": "RUNNING",
          "timestamp": "2023-05-04T13:57:24.701372Z"
      },
      "batteryState": {},
      "errors": [],
      "headerId": 16,
      "loads": [
          {
              "loadId": "",
              "loadPosition": "B1",
              "loadType": "BLUE"
          },
          {
              "loadId": "",
              "loadPosition": "A2",
              "loadType": "NONE"
          }
      ],
      "orderId": "34affed8-94e3-4955-bae0-036b464ef705",
      "orderUpdateId": 1,
      "paused": false,
      "serialNumber": "${serialNumber}",
      "timestamp": "2023-05-04T13:57:24.698860Z"
    }`;
    const hbwState = JSON.parse(hbwStateJson) as ModuleState;

    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: serialNumber,
      type: 'MODULE',
      available: AvailableState.BUSY,
    });

    await handleModuleAvailability(hbwState);

    expect(pairingStates.updateAvailability).toBeCalledWith('yBix', AvailableState.BUSY, hbwState.orderId);

    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: serialNumber,
      type: 'MODULE',
      available: AvailableState.READY,
    });

    await handleModuleAvailability(hbwState);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith('yBix', AvailableState.BUSY, hbwState.orderId);

    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: serialNumber,
      type: 'MODULE',
      available: AvailableState.BLOCKED,
    });

    await handleModuleAvailability(hbwState);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith('yBix', AvailableState.BUSY, hbwState.orderId);
  });

  it('should update the pairing state as READY if a PICK command was successful and the module indicates it does not have an active load', async () => {
    const orderId = 'orderId';
    const serialNumber = 'serialNumber';
    const moduleType = ModuleType.DPS;
    const actionState: ActionState<ModuleCommandType> = {
      state: State.FINISHED,
      command: ModuleCommandType.PICK,
      timestamp: new Date(),
      id: 'actionStateId',
    };
    const load: Load = {
      loadId: 'loadId',
      loadType: LoadType.WHITE,
      loadPosition: '1',
    };

    const moduleState: ModuleState = {
      actionState: actionState,
      orderId,
      errors: [],
      orderUpdateId: 0,
      type: moduleType,
      timestamp: new Date(),
      paused: false,
      serialNumber,
      loads: [load],
    };

    jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue({
      serialNumber,
      headerId: 1,
      timestamp: new Date(),
      version: '2',
      manufacturer: 'manufacturer',
      typeSpecification: {
        seriesName: 'seriesName',
      },
      protocolFeatures: {
        moduleParameters: {
          clearModuleOnPick: true,
        },
      },
    });

    jest.spyOn(pairingStates, 'get').mockReturnValue({
      serialNumber: 'any',
      type: 'MODULE',
      available: AvailableState.BLOCKED,
    });

    await handleModuleAvailability(moduleState);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, AvailableState.READY);
  });

  it('should update the pairing state as READY for the same order if a PICK command was successful and the module indicates it has an active load', async () => {
    const orderId = 'orderId';
    const serialNumber = 'serialNumber';
    const moduleType = ModuleType.DPS;
    const actionState: ActionState<ModuleCommandType> = {
      state: State.FINISHED,
      command: ModuleCommandType.PICK,
      timestamp: new Date(),
      id: 'actionStateId',
    };
    const load: Load = {
      loadId: 'loadId',
      loadType: LoadType.WHITE,
    };

    const moduleState: ModuleState = {
      actionState: actionState,
      orderId,
      errors: [],
      orderUpdateId: 0,
      type: moduleType,
      timestamp: new Date(),
      paused: false,
      serialNumber,
      loads: [load],
    };

    jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue({
      serialNumber,
      headerId: 1,
      timestamp: new Date(),
      version: '2',
      manufacturer: 'manufacturer',
      typeSpecification: {
        seriesName: 'seriesName',
      },
      protocolFeatures: {
        moduleParameters: {
          clearModuleOnPick: false,
        },
      },
    });

    await handleModuleAvailability(moduleState);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, AvailableState.READY, orderId);
  });

  it('should update the pairing state as BUSY no command is in the ModuleState message and the state is != Finished', async () => {
    const orderId = 'orderId';
    const serialNumber = 'serialNumber';
    const moduleType = ModuleType.AIQS;
    const load: Load = {
      loadId: 'loadId',
      loadType: LoadType.WHITE,
    };

    const moduleState: ModuleState = {
      orderId,
      errors: [],
      orderUpdateId: 0,
      type: moduleType,
      timestamp: new Date(),
      paused: false,
      serialNumber,
      loads: [load],
    };

    await handleModuleAvailability(moduleState);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, AvailableState.BLOCKED);
  });

  it('should update the pairing state as BUSY when a command is in the ModuleState message and the state is != Finished', async () => {
    const orderId = 'orderId';
    const serialNumber = 'serialNumber';
    const moduleType = ModuleType.AIQS;
    const load: Load = {
      loadId: 'loadId',
      loadType: LoadType.WHITE,
      loadPosition: '1',
    };
    const actionState: ActionState<ModuleCommandType> = {
      state: State.RUNNING,
      command: ModuleCommandType.DROP,
      timestamp: new Date(),
      id: 'actionStateId',
    };

    const moduleState: ModuleState = {
      actionState: actionState,
      orderId,
      errors: [],
      orderUpdateId: 0,
      type: moduleType,
      timestamp: new Date(),
      paused: false,
      serialNumber,
      loads: [load],
    };

    await handleModuleAvailability(moduleState);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, AvailableState.BUSY, orderId);
  });

  it('should update the pairing state as BLOCKED if no action state is present in the state message and an active load exists', async () => {
    const orderId = 'orderId';
    const serialNumber = 'serialNumber';
    const moduleType = ModuleType.AIQS;
    const load: Load = {
      loadId: 'loadId',
      loadType: LoadType.WHITE,
    };

    const moduleState: ModuleState = {
      orderId,
      errors: [],
      orderUpdateId: 0,
      type: moduleType,
      timestamp: new Date(),
      paused: false,
      serialNumber,
      loads: [load],
    };

    await handleModuleAvailability(moduleState);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, AvailableState.BLOCKED);
  });

  it('should update the pairing state as READY with orderId information if a command != DROP was successful and an active load exists', async () => {
    const orderId = 'orderId';
    const serialNumber = 'serialNumber';
    const moduleType = ModuleType.AIQS;
    const actionState: ActionState<ModuleCommandType> = {
      state: State.FINISHED,
      command: ModuleCommandType.CHECK_QUALITY,
      timestamp: new Date(),
      id: 'actionStateId',
    };
    const load: Load = {
      loadId: 'loadId',
      loadType: LoadType.WHITE,
    };

    const moduleState: ModuleState = {
      actionState: actionState,
      orderId,
      errors: [],
      orderUpdateId: 0,
      type: moduleType,
      timestamp: new Date(),
      paused: false,
      serialNumber,
      loads: [load],
    };

    await handleModuleAvailability(moduleState);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, AvailableState.READY, orderId);
  });

  it('should send a clear load instant action to an FTS if the command was DROP and the state was successful', async () => {
    await testSendClearLoadFtsInstantAction(ModuleCommandType.DROP, false);
  });

  it('should send a clear load instant action to an FTS if the command was PICK and the state was successful', async () => {
    await testSendClearLoadFtsInstantAction(ModuleCommandType.PICK, true);
  });

  const testSendClearLoadFtsInstantAction = async (command: ModuleCommandType, droppedWorkpiece: boolean) => {
    const state: ModuleState = {
      actionState: {
        state: State.FINISHED,
        command,
        timestamp: new Date(),
        id: 'actionStateId',
      },
      orderId: 'orderId',
      type: ModuleType.HBW,
      timestamp: new Date(),
      serialNumber: 'serialNumber',
      orderUpdateId: 0,
      paused: false,
      errors: [],
    };

    const workpieceId = 'workpieceId';
    const ftsSerialNumber = 'ftsSerialNumber';
    jest.spyOn(ftsHelper, 'sendClearLoadFtsInstantAction').mockResolvedValue(Promise.resolve());
    jest.spyOn(ftsPairingStates, 'getFtsSerialNumberForOrderId').mockReturnValue(ftsSerialNumber);
    jest.spyOn(orderManagement, 'getWorkpieceId').mockReturnValue(workpieceId);

    await updateFtsLoadHandler(state);

    // validate that sendClearLoadFtsInstantAction has been called
    expect(ftsPairingStates.getFtsSerialNumberForOrderId).toHaveBeenCalledWith(state.orderId);
    expect(orderManagement.getWorkpieceId).toHaveBeenCalledWith(state.orderId);
    expect(ftsHelper.sendClearLoadFtsInstantAction).toHaveBeenCalledWith(state.orderId, ftsSerialNumber, droppedWorkpiece, workpieceId);
  };

  it('should clear the loading bay when load has been removed', () => {
    const orderId = 'orderId';
    const ftsSerialNumber = 'ftsSerialNumber';
    const loadRemoved = true;

    clearLoadingBay(loadRemoved, ftsSerialNumber, orderId);

    expect(ftsPairingStates.clearLoadingBay).toHaveBeenCalledWith(ftsSerialNumber, orderId);
  });

  it('should not clear the loading bay when load has not been removed', () => {
    const orderId = 'orderId';
    const ftsSerialNumber = 'ftsSerialNumber';
    const loadRemoved = false;

    clearLoadingBay(loadRemoved, ftsSerialNumber, orderId);

    expect(ftsPairingStates.clearLoadingBay).not.toHaveBeenCalled();
  });

  it('should not send a clear load instant action to an FTS if the command was not PICK or DROP', async () => {
    const state: ModuleState = {
      actionState: {
        state: State.FINISHED,
        command: ModuleCommandType.DRILL,
        timestamp: new Date(),
        id: 'actionStateId',
      },
      orderId: 'orderId',
      type: ModuleType.HBW,
      timestamp: new Date(),
      serialNumber: 'serialNumber',
      orderUpdateId: 0,
      paused: false,
      errors: [],
    };

    jest.spyOn(ftsHelper, 'sendClearLoadFtsInstantAction').mockResolvedValue(Promise.resolve());

    await updateFtsLoadHandler(state);

    // validate that sendClearLoadFtsInstantAction has not been called
    expect(ftsHelper.sendClearLoadFtsInstantAction).not.toHaveBeenCalled();
  });

  it('should set the HBW as ready on state message on manual load', async () => {
    const hbwSerialNumber = 'yBix';
    const stateJsonPath = path.join(__dirname, 'mockData', 'hbw_manual_load-state.json');
    const factsheetJsonPath = path.join(__dirname, 'mockData', 'hbw_factsheet.json');
    const state: ModuleState = JSON.parse(fs.readFileSync(stateJsonPath, { encoding: 'utf8' }));
    const factsheet: Factsheet = JSON.parse(fs.readFileSync(factsheetJsonPath, { encoding: 'utf8' }));

    jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue(factsheet);
    await handleModuleAvailability(state);

    expect(pairingStates.updateAvailability).toHaveBeenCalledWith(hbwSerialNumber, AvailableState.READY);
    expect(pairingStates.updateAvailability).toHaveBeenCalledTimes(1);
  });

  it('should update the workpiece id if the DROP command was from the HBW', async () => {
    const newWorkpieceId = 'newId';
    const oldWorkpieceId = 'oldId';
    const orderId = 'orderId';
    const state: ModuleState = {
      actionState: {
        state: State.FINISHED,
        command: ModuleCommandType.DROP,
        timestamp: new Date(),
        id: 'actionStateId',
        result: newWorkpieceId,
      },
      orderId: orderId,
      type: ModuleType.HBW,
      timestamp: new Date(),
      serialNumber: 'serialNumber',
      orderUpdateId: 0,
      paused: false,
      errors: [],
    };
    jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(ModuleType.HBW);
    jest.spyOn(orderManagement, 'updateOrderWorkpieceId').mockReturnValue();
    jest.spyOn(orderManagement, 'getWorkpieceId').mockReturnValue(oldWorkpieceId);

    updateOrderWorkpieceId(state);

    expect(pairingStates.getModuleType).toHaveBeenCalledWith(state.serialNumber);
    expect(orderManagement.updateOrderWorkpieceId).toHaveBeenCalledWith(orderId, newWorkpieceId);
    expect(orderManagement.getWorkpieceId).toHaveBeenCalledWith(orderId);
  });

  it('should not update the workpiece id if the DROP command was not from the HBW', async () => {
    const newWorkpieceId = 'newId';
    const oldWorkpieceId = 'oldId';
    const orderId = 'orderId';
    const state: ModuleState = {
      actionState: {
        state: State.FINISHED,
        command: ModuleCommandType.DROP,
        timestamp: new Date(),
        id: 'actionStateId',
        result: newWorkpieceId,
      },
      orderId: orderId,
      type: ModuleType.MILL,
      timestamp: new Date(),
      serialNumber: 'serialNumber',
      orderUpdateId: 0,
      paused: false,
      errors: [],
    };
    jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(ModuleType.MILL);
    jest.spyOn(orderManagement, 'updateOrderWorkpieceId').mockReturnValue();
    jest.spyOn(orderManagement, 'getWorkpieceId').mockReturnValue(oldWorkpieceId);

    updateOrderWorkpieceId(state);

    expect(pairingStates.getModuleType).toHaveBeenCalledWith(state.serialNumber);
    expect(orderManagement.updateOrderWorkpieceId).not.toHaveBeenCalled();
    expect(orderManagement.getWorkpieceId).not.toHaveBeenCalled();
  });

  it('should not update the workpiece id if the state is no DROP command', async () => {
    const newWorkpieceId = 'newId';
    const oldWorkpieceId = 'oldId';
    const orderId = 'orderId';
    const state: ModuleState = {
      actionState: {
        state: State.FINISHED,
        command: ModuleCommandType.PICK,
        timestamp: new Date(),
        id: 'actionStateId',
        result: newWorkpieceId,
      },
      orderId: orderId,
      type: ModuleType.MILL,
      timestamp: new Date(),
      serialNumber: 'serialNumber',
      orderUpdateId: 0,
      paused: false,
      errors: [],
    };
    jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(ModuleType.MILL);
    jest.spyOn(orderManagement, 'updateOrderWorkpieceId').mockReturnValue();
    jest.spyOn(orderManagement, 'getWorkpieceId').mockReturnValue(oldWorkpieceId);

    for (const command of Object.values(ModuleCommandType)) {
      if (command === ModuleCommandType.DROP) {
        continue;
      }
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      state.actionState!.command = command;
      updateOrderWorkpieceId(state);
    }

    expect(pairingStates.getModuleType).not.toHaveBeenCalled();
    expect(orderManagement.updateOrderWorkpieceId).not.toHaveBeenCalled();
    expect(orderManagement.getWorkpieceId).not.toHaveBeenCalled();
  });

  describe('Test input/output interaction for DPS', () => {
    it('should mark the DPS as READY if no load is given', async () => {
      jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(ModuleType.DPS);
      const orderId = 'orderId';
      const serialNumber = 'dpsSerial';
      const moduleType = ModuleType.DPS;
      const actionState: ActionState<ModuleCommandType> = {
        state: State.FINISHED,
        command: ModuleCommandType.PICK,
        timestamp: new Date(),
        id: 'actionStateId',
      };

      const moduleState: ModuleState = {
        actionState: actionState,
        orderId,
        errors: [],
        orderUpdateId: 0,
        type: moduleType,
        timestamp: new Date(),
        paused: false,
        serialNumber,
        loads: [],
      };

      await handleModuleAvailability(moduleState);

      expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, AvailableState.READY);
    });

    it('should mark the DPS as READY for a specific order if a load is given', async () => {
      jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(ModuleType.DPS);
      const orderId = 'orderId';
      const serialNumber = 'dpsSerial';
      const moduleType = ModuleType.DPS;
      const actionState: ActionState<ModuleCommandType> = {
        state: State.FINISHED,
        command: ModuleCommandType.PICK,
        timestamp: new Date(),
        id: 'actionStateId',
      };
      const load: Load = {
        loadType: 'UNKNOWN' as unknown as LoadType,
      };

      const moduleState: ModuleState = {
        actionState: actionState,
        orderId,
        errors: [],
        orderUpdateId: 0,
        type: moduleType,
        timestamp: new Date(),
        paused: false,
        serialNumber,
        loads: [load],
      };

      await handleModuleAvailability(moduleState);

      expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, AvailableState.READY, orderId);
    });

    it('should mark the DPS as READY for a specific order if a load is given without an action', async () => {
      jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(ModuleType.DPS);
      const orderId = 'orderId';
      const serialNumber = 'dpsSerial';
      const moduleType = ModuleType.DPS;
      const load: Load = {
        loadType: 'UNKNOWN' as unknown as LoadType,
      };

      const moduleState: ModuleState = {
        orderId,
        errors: [],
        orderUpdateId: 0,
        type: moduleType,
        timestamp: new Date(),
        paused: false,
        serialNumber,
        loads: [load],
      };

      await handleModuleAvailability(moduleState);

      expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, AvailableState.READY, orderId);
    });

    it('should mark the DPS as BUSY if a load is given without an action and no orderId', async () => {
      jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(ModuleType.DPS);
      const orderId = '';
      const serialNumber = 'dpsSerial';
      const moduleType = ModuleType.DPS;
      const load: Load = {
        loadType: 'UNKNOWN' as unknown as LoadType,
      };

      const moduleState: ModuleState = {
        orderId,
        errors: [],
        orderUpdateId: 0,
        type: moduleType,
        timestamp: new Date(),
        paused: false,
        serialNumber,
        loads: [load],
      };

      await handleModuleAvailability(moduleState);

      expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, AvailableState.BUSY);
    });
  });
});
