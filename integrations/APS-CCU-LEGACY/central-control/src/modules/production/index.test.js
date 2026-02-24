"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_fs_1 = __importDefault(require("node:fs"));
const node_path_1 = __importDefault(require("node:path"));
const ccu_1 = require("../../../../common/protocol/ccu");
const module_1 = require("../../../../common/protocol/module");
const vda_1 = require("../../../../common/protocol/vda");
const ftsHelper = __importStar(require("../fts/helper"));
const order_management_1 = require("../order/management/order-management");
const fts_pairing_states_1 = require("../pairing/fts-pairing-states");
const pairing_states_1 = require("../pairing/pairing-states");
const index_1 = require("./index");
jest.mock('../pairing/pairing-states');
jest.mock('../pairing/fts-pairing-states');
jest.mock('../order/management/order-management');
describe('test production update handling', () => {
    let pairingStates;
    let ftsPairingStates;
    let orderManagement;
    beforeEach(() => {
        pairingStates = {
            updateAvailability: jest.fn(),
            getFactsheet: jest.fn(),
            getWorkpieceId: jest.fn(),
            getModuleType: jest.fn(),
            get: jest.fn(),
        };
        pairing_states_1.PairingStates.getInstance = jest.fn().mockReturnValue(pairingStates);
        ftsPairingStates = {
            clearLoadingBay: jest.fn(),
            getFtsSerialNumberForOrderId: jest.fn(),
            getLoadingBayForWorkpiece: jest.fn(),
        };
        jest.spyOn(fts_pairing_states_1.FtsPairingStates, 'getInstance').mockReturnValue(ftsPairingStates);
        orderManagement = {
            getWorkpieceId: jest.fn(),
            updateOrderWorkpieceId: jest.fn(),
        };
        order_management_1.OrderManagement.getInstance = jest.fn().mockReturnValue(orderManagement);
    });
    afterEach(() => {
        jest.restoreAllMocks();
        jest.useRealTimers();
    });
    it('should update the pairing state as READY if an drop workpiece was successful', async () => {
        const orderId = 'orderId';
        const serialNumber = 'serialNumber';
        const moduleType = module_1.ModuleType.AIQS;
        const actionState = {
            state: vda_1.State.FINISHED,
            command: module_1.ModuleCommandType.DROP,
            timestamp: new Date(),
            id: 'actionStateId',
        };
        const load = {
            loadId: 'loadId',
            loadType: vda_1.LoadType.WHITE,
            loadPosition: '1',
        };
        const moduleState = {
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
        await (0, index_1.handleModuleAvailability)(moduleState);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.READY);
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
        const hbwState = JSON.parse(hbwStateJson);
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: serialNumber,
            type: 'MODULE',
            available: ccu_1.AvailableState.BUSY,
        });
        await (0, index_1.handleModuleAvailability)(hbwState);
        expect(pairingStates.updateAvailability).not.toHaveBeenCalled();
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: serialNumber,
            type: 'MODULE',
            available: ccu_1.AvailableState.READY,
        });
        await (0, index_1.handleModuleAvailability)(hbwState);
        expect(pairingStates.updateAvailability).not.toHaveBeenCalled();
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: serialNumber,
            type: 'MODULE',
            available: ccu_1.AvailableState.BLOCKED,
        });
        await (0, index_1.handleModuleAvailability)(hbwState);
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
        const hbwState = JSON.parse(hbwStateJson);
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: serialNumber,
            type: 'MODULE',
            available: ccu_1.AvailableState.BUSY,
        });
        await (0, index_1.handleModuleAvailability)(hbwState);
        expect(pairingStates.updateAvailability).toBeCalledWith('yBix', ccu_1.AvailableState.READY);
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: serialNumber,
            type: 'MODULE',
            available: ccu_1.AvailableState.READY,
        });
        await (0, index_1.handleModuleAvailability)(hbwState);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith('yBix', ccu_1.AvailableState.READY);
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: serialNumber,
            type: 'MODULE',
            available: ccu_1.AvailableState.BLOCKED,
        });
        await (0, index_1.handleModuleAvailability)(hbwState);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith('yBix', ccu_1.AvailableState.READY);
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
        const hbwState = JSON.parse(hbwStateJson);
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: serialNumber,
            type: 'MODULE',
            available: ccu_1.AvailableState.BUSY,
        });
        await (0, index_1.handleModuleAvailability)(hbwState);
        expect(pairingStates.updateAvailability).toBeCalledWith('yBix', ccu_1.AvailableState.BUSY, hbwState.orderId);
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: serialNumber,
            type: 'MODULE',
            available: ccu_1.AvailableState.READY,
        });
        await (0, index_1.handleModuleAvailability)(hbwState);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith('yBix', ccu_1.AvailableState.BUSY, hbwState.orderId);
        jest.spyOn(pairingStates, 'get').mockReturnValue({
            serialNumber: serialNumber,
            type: 'MODULE',
            available: ccu_1.AvailableState.BLOCKED,
        });
        await (0, index_1.handleModuleAvailability)(hbwState);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith('yBix', ccu_1.AvailableState.BUSY, hbwState.orderId);
    });
    it('should update the pairing state as READY if a PICK command was successful and the module indicates it does not have an active load', async () => {
        const orderId = 'orderId';
        const serialNumber = 'serialNumber';
        const moduleType = module_1.ModuleType.DPS;
        const actionState = {
            state: vda_1.State.FINISHED,
            command: module_1.ModuleCommandType.PICK,
            timestamp: new Date(),
            id: 'actionStateId',
        };
        const load = {
            loadId: 'loadId',
            loadType: vda_1.LoadType.WHITE,
            loadPosition: '1',
        };
        const moduleState = {
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
            available: ccu_1.AvailableState.BLOCKED,
        });
        await (0, index_1.handleModuleAvailability)(moduleState);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.READY);
    });
    it('should update the pairing state as READY for the same order if a PICK command was successful and the module indicates it has an active load', async () => {
        const orderId = 'orderId';
        const serialNumber = 'serialNumber';
        const moduleType = module_1.ModuleType.DPS;
        const actionState = {
            state: vda_1.State.FINISHED,
            command: module_1.ModuleCommandType.PICK,
            timestamp: new Date(),
            id: 'actionStateId',
        };
        const load = {
            loadId: 'loadId',
            loadType: vda_1.LoadType.WHITE,
        };
        const moduleState = {
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
        await (0, index_1.handleModuleAvailability)(moduleState);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.READY, orderId);
    });
    it('should update the pairing state as BUSY no command is in the ModuleState message and the state is != Finished', async () => {
        const orderId = 'orderId';
        const serialNumber = 'serialNumber';
        const moduleType = module_1.ModuleType.AIQS;
        const load = {
            loadId: 'loadId',
            loadType: vda_1.LoadType.WHITE,
        };
        const moduleState = {
            orderId,
            errors: [],
            orderUpdateId: 0,
            type: moduleType,
            timestamp: new Date(),
            paused: false,
            serialNumber,
            loads: [load],
        };
        await (0, index_1.handleModuleAvailability)(moduleState);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.BLOCKED);
    });
    it('should update the pairing state as BUSY when a command is in the ModuleState message and the state is != Finished', async () => {
        const orderId = 'orderId';
        const serialNumber = 'serialNumber';
        const moduleType = module_1.ModuleType.AIQS;
        const load = {
            loadId: 'loadId',
            loadType: vda_1.LoadType.WHITE,
            loadPosition: '1',
        };
        const actionState = {
            state: vda_1.State.RUNNING,
            command: module_1.ModuleCommandType.DROP,
            timestamp: new Date(),
            id: 'actionStateId',
        };
        const moduleState = {
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
        await (0, index_1.handleModuleAvailability)(moduleState);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.BUSY, orderId);
    });
    it('should update the pairing state as BLOCKED if no action state is present in the state message and an active load exists', async () => {
        const orderId = 'orderId';
        const serialNumber = 'serialNumber';
        const moduleType = module_1.ModuleType.AIQS;
        const load = {
            loadId: 'loadId',
            loadType: vda_1.LoadType.WHITE,
        };
        const moduleState = {
            orderId,
            errors: [],
            orderUpdateId: 0,
            type: moduleType,
            timestamp: new Date(),
            paused: false,
            serialNumber,
            loads: [load],
        };
        await (0, index_1.handleModuleAvailability)(moduleState);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.BLOCKED);
    });
    it('should update the pairing state as READY with orderId information if a command != DROP was successful and an active load exists', async () => {
        const orderId = 'orderId';
        const serialNumber = 'serialNumber';
        const moduleType = module_1.ModuleType.AIQS;
        const actionState = {
            state: vda_1.State.FINISHED,
            command: module_1.ModuleCommandType.CHECK_QUALITY,
            timestamp: new Date(),
            id: 'actionStateId',
        };
        const load = {
            loadId: 'loadId',
            loadType: vda_1.LoadType.WHITE,
        };
        const moduleState = {
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
        await (0, index_1.handleModuleAvailability)(moduleState);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.READY, orderId);
    });
    it('should send a clear load instant action to an FTS if the command was DROP and the state was successful', async () => {
        await testSendClearLoadFtsInstantAction(module_1.ModuleCommandType.DROP, false);
    });
    it('should send a clear load instant action to an FTS if the command was PICK and the state was successful', async () => {
        await testSendClearLoadFtsInstantAction(module_1.ModuleCommandType.PICK, true);
    });
    const testSendClearLoadFtsInstantAction = async (command, droppedWorkpiece) => {
        const state = {
            actionState: {
                state: vda_1.State.FINISHED,
                command,
                timestamp: new Date(),
                id: 'actionStateId',
            },
            orderId: 'orderId',
            type: module_1.ModuleType.HBW,
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
        await (0, index_1.updateFtsLoadHandler)(state);
        // validate that sendClearLoadFtsInstantAction has been called
        expect(ftsPairingStates.getFtsSerialNumberForOrderId).toHaveBeenCalledWith(state.orderId);
        expect(orderManagement.getWorkpieceId).toHaveBeenCalledWith(state.orderId);
        expect(ftsHelper.sendClearLoadFtsInstantAction).toHaveBeenCalledWith(state.orderId, ftsSerialNumber, droppedWorkpiece, workpieceId);
    };
    it('should clear the loading bay when load has been removed', () => {
        const orderId = 'orderId';
        const ftsSerialNumber = 'ftsSerialNumber';
        const loadRemoved = true;
        (0, index_1.clearLoadingBay)(loadRemoved, ftsSerialNumber, orderId);
        expect(ftsPairingStates.clearLoadingBay).toHaveBeenCalledWith(ftsSerialNumber, orderId);
    });
    it('should not clear the loading bay when load has not been removed', () => {
        const orderId = 'orderId';
        const ftsSerialNumber = 'ftsSerialNumber';
        const loadRemoved = false;
        (0, index_1.clearLoadingBay)(loadRemoved, ftsSerialNumber, orderId);
        expect(ftsPairingStates.clearLoadingBay).not.toHaveBeenCalled();
    });
    it('should not send a clear load instant action to an FTS if the command was not PICK or DROP', async () => {
        const state = {
            actionState: {
                state: vda_1.State.FINISHED,
                command: module_1.ModuleCommandType.DRILL,
                timestamp: new Date(),
                id: 'actionStateId',
            },
            orderId: 'orderId',
            type: module_1.ModuleType.HBW,
            timestamp: new Date(),
            serialNumber: 'serialNumber',
            orderUpdateId: 0,
            paused: false,
            errors: [],
        };
        jest.spyOn(ftsHelper, 'sendClearLoadFtsInstantAction').mockResolvedValue(Promise.resolve());
        await (0, index_1.updateFtsLoadHandler)(state);
        // validate that sendClearLoadFtsInstantAction has not been called
        expect(ftsHelper.sendClearLoadFtsInstantAction).not.toHaveBeenCalled();
    });
    it('should set the HBW as ready on state message on manual load', async () => {
        const hbwSerialNumber = 'yBix';
        const stateJsonPath = node_path_1.default.join(__dirname, 'mockData', 'hbw_manual_load-state.json');
        const factsheetJsonPath = node_path_1.default.join(__dirname, 'mockData', 'hbw_factsheet.json');
        const state = JSON.parse(node_fs_1.default.readFileSync(stateJsonPath, { encoding: 'utf8' }));
        const factsheet = JSON.parse(node_fs_1.default.readFileSync(factsheetJsonPath, { encoding: 'utf8' }));
        jest.spyOn(pairingStates, 'getFactsheet').mockReturnValue(factsheet);
        await (0, index_1.handleModuleAvailability)(state);
        expect(pairingStates.updateAvailability).toHaveBeenCalledWith(hbwSerialNumber, ccu_1.AvailableState.READY);
        expect(pairingStates.updateAvailability).toHaveBeenCalledTimes(1);
    });
    it('should update the workpiece id if the DROP command was from the HBW', async () => {
        const newWorkpieceId = 'newId';
        const oldWorkpieceId = 'oldId';
        const orderId = 'orderId';
        const state = {
            actionState: {
                state: vda_1.State.FINISHED,
                command: module_1.ModuleCommandType.DROP,
                timestamp: new Date(),
                id: 'actionStateId',
                result: newWorkpieceId,
            },
            orderId: orderId,
            type: module_1.ModuleType.HBW,
            timestamp: new Date(),
            serialNumber: 'serialNumber',
            orderUpdateId: 0,
            paused: false,
            errors: [],
        };
        jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(module_1.ModuleType.HBW);
        jest.spyOn(orderManagement, 'updateOrderWorkpieceId').mockReturnValue();
        jest.spyOn(orderManagement, 'getWorkpieceId').mockReturnValue(oldWorkpieceId);
        (0, index_1.updateOrderWorkpieceId)(state);
        expect(pairingStates.getModuleType).toHaveBeenCalledWith(state.serialNumber);
        expect(orderManagement.updateOrderWorkpieceId).toHaveBeenCalledWith(orderId, newWorkpieceId);
        expect(orderManagement.getWorkpieceId).toHaveBeenCalledWith(orderId);
    });
    it('should not update the workpiece id if the DROP command was not from the HBW', async () => {
        const newWorkpieceId = 'newId';
        const oldWorkpieceId = 'oldId';
        const orderId = 'orderId';
        const state = {
            actionState: {
                state: vda_1.State.FINISHED,
                command: module_1.ModuleCommandType.DROP,
                timestamp: new Date(),
                id: 'actionStateId',
                result: newWorkpieceId,
            },
            orderId: orderId,
            type: module_1.ModuleType.MILL,
            timestamp: new Date(),
            serialNumber: 'serialNumber',
            orderUpdateId: 0,
            paused: false,
            errors: [],
        };
        jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(module_1.ModuleType.MILL);
        jest.spyOn(orderManagement, 'updateOrderWorkpieceId').mockReturnValue();
        jest.spyOn(orderManagement, 'getWorkpieceId').mockReturnValue(oldWorkpieceId);
        (0, index_1.updateOrderWorkpieceId)(state);
        expect(pairingStates.getModuleType).toHaveBeenCalledWith(state.serialNumber);
        expect(orderManagement.updateOrderWorkpieceId).not.toHaveBeenCalled();
        expect(orderManagement.getWorkpieceId).not.toHaveBeenCalled();
    });
    it('should not update the workpiece id if the state is no DROP command', async () => {
        const newWorkpieceId = 'newId';
        const oldWorkpieceId = 'oldId';
        const orderId = 'orderId';
        const state = {
            actionState: {
                state: vda_1.State.FINISHED,
                command: module_1.ModuleCommandType.PICK,
                timestamp: new Date(),
                id: 'actionStateId',
                result: newWorkpieceId,
            },
            orderId: orderId,
            type: module_1.ModuleType.MILL,
            timestamp: new Date(),
            serialNumber: 'serialNumber',
            orderUpdateId: 0,
            paused: false,
            errors: [],
        };
        jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(module_1.ModuleType.MILL);
        jest.spyOn(orderManagement, 'updateOrderWorkpieceId').mockReturnValue();
        jest.spyOn(orderManagement, 'getWorkpieceId').mockReturnValue(oldWorkpieceId);
        for (const command of Object.values(module_1.ModuleCommandType)) {
            if (command === module_1.ModuleCommandType.DROP) {
                continue;
            }
            // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            state.actionState.command = command;
            (0, index_1.updateOrderWorkpieceId)(state);
        }
        expect(pairingStates.getModuleType).not.toHaveBeenCalled();
        expect(orderManagement.updateOrderWorkpieceId).not.toHaveBeenCalled();
        expect(orderManagement.getWorkpieceId).not.toHaveBeenCalled();
    });
    describe('Test input/output interaction for DPS', () => {
        it('should mark the DPS as READY if no load is given', async () => {
            jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(module_1.ModuleType.DPS);
            const orderId = 'orderId';
            const serialNumber = 'dpsSerial';
            const moduleType = module_1.ModuleType.DPS;
            const actionState = {
                state: vda_1.State.FINISHED,
                command: module_1.ModuleCommandType.PICK,
                timestamp: new Date(),
                id: 'actionStateId',
            };
            const moduleState = {
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
            await (0, index_1.handleModuleAvailability)(moduleState);
            expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.READY);
        });
        it('should mark the DPS as READY for a specific order if a load is given', async () => {
            jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(module_1.ModuleType.DPS);
            const orderId = 'orderId';
            const serialNumber = 'dpsSerial';
            const moduleType = module_1.ModuleType.DPS;
            const actionState = {
                state: vda_1.State.FINISHED,
                command: module_1.ModuleCommandType.PICK,
                timestamp: new Date(),
                id: 'actionStateId',
            };
            const load = {
                loadType: 'UNKNOWN',
            };
            const moduleState = {
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
            await (0, index_1.handleModuleAvailability)(moduleState);
            expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.READY, orderId);
        });
        it('should mark the DPS as READY for a specific order if a load is given without an action', async () => {
            jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(module_1.ModuleType.DPS);
            const orderId = 'orderId';
            const serialNumber = 'dpsSerial';
            const moduleType = module_1.ModuleType.DPS;
            const load = {
                loadType: 'UNKNOWN',
            };
            const moduleState = {
                orderId,
                errors: [],
                orderUpdateId: 0,
                type: moduleType,
                timestamp: new Date(),
                paused: false,
                serialNumber,
                loads: [load],
            };
            await (0, index_1.handleModuleAvailability)(moduleState);
            expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.READY, orderId);
        });
        it('should mark the DPS as BUSY if a load is given without an action and no orderId', async () => {
            jest.spyOn(pairingStates, 'getModuleType').mockReturnValue(module_1.ModuleType.DPS);
            const orderId = '';
            const serialNumber = 'dpsSerial';
            const moduleType = module_1.ModuleType.DPS;
            const load = {
                loadType: 'UNKNOWN',
            };
            const moduleState = {
                orderId,
                errors: [],
                orderUpdateId: 0,
                type: moduleType,
                timestamp: new Date(),
                paused: false,
                serialNumber,
                loads: [load],
            };
            await (0, index_1.handleModuleAvailability)(moduleState);
            expect(pairingStates.updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.BUSY);
        });
    });
});
