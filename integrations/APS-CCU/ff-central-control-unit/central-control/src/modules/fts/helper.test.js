"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_crypto_1 = __importDefault(require("node:crypto"));
const ccu_1 = require("../../../../common/protocol/ccu");
const fts_1 = require("../../../../common/protocol/fts");
const module_1 = require("../../../../common/protocol/module");
const vda_1 = require("../../../../common/protocol/vda");
const test_helpers_1 = require("../../test-helpers");
const factory_layout_service_1 = require("../layout/factory-layout-service");
const order_management_1 = require("../order/management/order-management");
const fts_pairing_states_1 = require("../pairing/fts-pairing-states");
const pairing_states_1 = require("../pairing/pairing-states");
const production_1 = require("../production/production");
const helper_1 = require("./helper");
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
        jest.spyOn(fts_pairing_states_1.FtsPairingStates, 'getInstance').mockReturnValue({
            updateAvailability: jest.fn(),
            getLastFinishedDockId: jest.fn(),
            setLastFinishedDockId: jest.fn(),
        });
        jest.spyOn(order_management_1.OrderManagement, 'getInstance').mockReturnValue({
            getTargetModuleTypeForNavActionId: jest.fn(),
            getWorkpieceType: jest.fn(),
            isOrderActionRunning: jest.fn(),
            getActiveOrder: jest.fn(),
        });
        jest.spyOn(pairing_states_1.PairingStates, 'getInstance').mockReturnValue({
            getModuleForOrder: jest.fn(),
            getForModuleType: jest.fn(),
            clearModuleForOrder: jest.fn(),
            getAllReady: jest.fn(() => []),
        });
        jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'releaseNodesBefore').mockReturnValue();
    });
    afterEach(() => {
        order_management_1.OrderManagement['instance'] = undefined;
        jest.clearAllMocks();
        jest.restoreAllMocks();
    });
    it('should create the correct busy state from the fts state if driving', async () => {
        const orderId = 'ID';
        const state = {
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
        await (0, helper_1.updateFtsAvailability)(state);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith('mocked', ccu_1.AvailableState.BUSY, orderId, state.lastNodeId, undefined);
        expect(pairing_states_1.PairingStates.getInstance().getForModuleType).not.toHaveBeenCalled();
        expect(order_management_1.OrderManagement.getInstance().getTargetModuleTypeForNavActionId).not.toHaveBeenCalled();
    });
    it('should create the correct busy state from the fts state if waiting for load handler', async () => {
        const orderId = 'ID';
        const actionId = 'actionId';
        const moduleSerialNumber = 'moduleSerialNumber';
        const state = {
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
                state: vda_1.State.FINISHED,
                command: fts_1.FtsCommandType.DOCK,
                timestamp: new Date(),
                id: actionId,
            },
        };
        jest.spyOn(order_management_1.OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(module_1.ModuleType.DPS);
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getForModuleType').mockReturnValue({
            serialNumber: moduleSerialNumber,
            connected: true,
            available: ccu_1.AvailableState.READY,
            type: 'MODULE',
        });
        await (0, helper_1.updateFtsAvailability)(state);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith('mocked', ccu_1.AvailableState.BUSY, orderId, state.lastNodeId, moduleSerialNumber);
        expect(order_management_1.OrderManagement.getInstance().getTargetModuleTypeForNavActionId).toHaveBeenCalledWith(actionId);
    });
    it('should create the correct ready state from the fts state if the action was DOCK', async () => {
        const orderId = 'ID';
        const actionId = 'actionId';
        const moduleSerialNumber = 'moduleSerialNumber';
        const state = {
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
                state: vda_1.State.FINISHED,
                command: fts_1.FtsCommandType.DOCK,
                timestamp: new Date(),
                id: actionId,
            },
        };
        jest.spyOn(order_management_1.OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(module_1.ModuleType.DPS);
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getForModuleType').mockReturnValue({
            serialNumber: moduleSerialNumber,
            connected: true,
            available: ccu_1.AvailableState.READY,
            type: 'MODULE',
        });
        await (0, helper_1.updateFtsAvailability)(state);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith('mocked', ccu_1.AvailableState.READY, undefined, state.lastNodeId, moduleSerialNumber);
        expect(order_management_1.OrderManagement.getInstance().getTargetModuleTypeForNavActionId).toHaveBeenCalledWith(actionId);
    });
    it('should create the correct ready state from the fts state if the action was TURN but is referenced in the order management', async () => {
        const orderId = 'ID';
        const actionId = 'actionId';
        const dpsSerial = 'dpsSerial';
        const state = {
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
                state: vda_1.State.FINISHED,
                command: fts_1.FtsCommandType.TURN,
                timestamp: new Date(),
                id: actionId,
            },
        };
        const pairedModule = {
            serialNumber: dpsSerial,
            type: 'MODULE',
            subType: module_1.ModuleType.DPS,
        };
        jest.spyOn(order_management_1.OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(module_1.ModuleType.DPS);
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getForModuleType').mockReturnValue(pairedModule);
        await (0, helper_1.updateFtsAvailability)(state);
        expect(order_management_1.OrderManagement.getInstance().getTargetModuleTypeForNavActionId).toHaveBeenCalledWith(actionId);
        expect(pairing_states_1.PairingStates.getInstance().getForModuleType).toHaveBeenCalledWith(module_1.ModuleType.DPS, orderId);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith('mocked', ccu_1.AvailableState.READY, undefined, state.lastNodeId, dpsSerial);
    });
    it('should create the correct ready state from the fts state for any successful none docking action', async () => {
        const orderId = 'ID';
        const ftsSerialNumber = 'mocked';
        order_management_1.OrderManagement.getInstance().getOrderForWorkpieceId = jest.fn();
        pairing_states_1.PairingStates.getInstance().getForModuleType = jest.fn();
        for (const command of Object.values(fts_1.FtsCommandType)) {
            if (command === fts_1.FtsCommandType.DOCK) {
                continue;
            }
            const state = {
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
                    state: vda_1.State.FINISHED,
                    command,
                    timestamp: new Date(),
                    id: 'actionId',
                },
            };
            await (0, helper_1.updateFtsAvailability)(state);
            expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(ftsSerialNumber, ccu_1.AvailableState.READY, undefined, '', undefined);
            expect(order_management_1.OrderManagement.getInstance().getOrderForWorkpieceId).not.toHaveBeenCalled();
            expect(pairing_states_1.PairingStates.getInstance().getForModuleType).not.toHaveBeenCalled();
        }
    });
    it('should set the correct position state from the ready fts state without action, on FTS start', async () => {
        const nodeId = fts_1.NODE_ID_UNKNOWN;
        const stateNoAction = {
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
        await (0, helper_1.updateFtsAvailability)(stateNoAction);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith('mocked', ccu_1.AvailableState.BLOCKED, stateNoAction.orderId, nodeId);
    });
    it('should set the correct node position from the ready fts state with an incomplete action', async () => {
        // As of FITEFF22-426, road nodes are only numeric, a not-numeric node is a module id
        const nodeId = '1';
        const moduleType = module_1.ModuleType.DPS;
        const dockActionId = 'dockActionId';
        const orderId = 'orderId';
        const targetSpy = jest.spyOn(order_management_1.OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(moduleType);
        const stateNoAction = {
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
                state: vda_1.State.RUNNING,
                command: fts_1.FtsCommandType.DOCK,
                timestamp: new Date(),
            },
        };
        await (0, helper_1.updateFtsAvailability)(stateNoAction);
        expect(targetSpy).not.toHaveBeenCalled();
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith('mocked', ccu_1.AvailableState.BUSY, orderId, nodeId, undefined);
        jest.clearAllMocks();
        const nodeId2 = '1nodeId-23';
        stateNoAction.lastNodeId = nodeId2;
        await (0, helper_1.updateFtsAvailability)(stateNoAction);
        expect(targetSpy).not.toHaveBeenCalled();
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith('mocked', ccu_1.AvailableState.BUSY, orderId, nodeId2, nodeId2);
    });
    it('should create the correct blocked state from the fts state', async () => {
        const orderId = '';
        const state = {
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
        await (0, helper_1.updateFtsAvailability)(state);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith('mocked', ccu_1.AvailableState.BLOCKED, orderId, state.lastNodeId);
        const state2 = {
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
        await (0, helper_1.updateFtsAvailability)(state2);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith('mocked', ccu_1.AvailableState.BLOCKED, orderId, state.lastNodeId);
    });
    it('should set the FTS blocked when it is at the UNKNOWN node', async () => {
        const orderId = '';
        const state = {
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
        await (0, helper_1.updateFtsAvailability)(state);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith('mocked', ccu_1.AvailableState.BLOCKED, orderId, state.lastNodeId);
    });
    it('should delete all associated actions for an order reset and reset the loading bay for the fts', async () => {
        const orderId = 'orderId';
        const serialNumber = 'mocked';
        const workpieceOrderId = 'workpieceOrderId';
        const resetWarning = [
            {
                errorType: fts_1.FtsErrors.RESET,
                timestamp: new Date(),
                errorLevel: 'WARNING',
                errorReferences: [{ referenceKey: 'orderId', referenceValue: orderId }],
            },
        ];
        const assignedModule = {
            type: 'MODULE',
            serialNumber: 'xyz',
        };
        fts_pairing_states_1.FtsPairingStates.getInstance().resetLoadingBay = jest.fn();
        fts_pairing_states_1.FtsPairingStates.getInstance().getLoadedOrderIds = jest.fn().mockReturnValue([workpieceOrderId]);
        pairing_states_1.PairingStates.getInstance().getModuleForOrder = jest.fn().mockReturnValue(assignedModule);
        order_management_1.OrderManagement.getInstance().resetOrder = jest.fn().mockResolvedValue(Promise.resolve());
        order_management_1.OrderManagement.getInstance().getOrderForWorkpieceId = jest.fn();
        await (0, helper_1.handleResetWarning)(resetWarning, serialNumber);
        expect(order_management_1.OrderManagement.getInstance().getOrderForWorkpieceId).not.toHaveBeenCalled();
        expect(order_management_1.OrderManagement.getInstance().resetOrder).toHaveBeenCalledWith(workpieceOrderId);
        expect(order_management_1.OrderManagement.getInstance().resetOrder).toHaveBeenCalledWith(orderId);
        expect(pairing_states_1.PairingStates.getInstance().clearModuleForOrder).toHaveBeenCalledWith(workpieceOrderId);
        expect(pairing_states_1.PairingStates.getInstance().getModuleForOrder).toHaveBeenCalledWith(orderId);
        expect(pairing_states_1.PairingStates.getInstance().clearModuleForOrder).toHaveBeenCalledWith(orderId);
        expect(production_1.sendResetModuleInstantAction).toHaveBeenCalledWith(assignedModule.serialNumber);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().getLoadedOrderIds).toHaveBeenCalledWith(serialNumber);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().resetLoadingBay).toHaveBeenCalledWith(serialNumber);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(serialNumber, ccu_1.AvailableState.READY, undefined, fts_1.NODE_ID_UNKNOWN, fts_1.NODE_ID_UNKNOWN);
    });
    it('should send an instant action to an FTS', async () => {
        const serialNumber = 'FTS1';
        const topic = `fts/v1/ff/${serialNumber}/instantAction`;
        const date = new Date('2021-01-01T00:00:00.000Z');
        const mockedUUID = 'mockedUUID';
        const orderId = 'orderId';
        // create jest mocks
        const mqttClientMock = (0, test_helpers_1.createMockMqttClient)();
        jest.useFakeTimers().setSystemTime(date);
        jest.mock('node:crypto');
        node_crypto_1.default.randomUUID = jest.fn().mockReturnValue(mockedUUID);
        await (0, helper_1.sendClearLoadFtsInstantAction)(orderId, serialNumber, false);
        const expectedInstantAction = {
            serialNumber,
            timestamp: new Date(),
            actions: [
                {
                    actionId: mockedUUID,
                    actionType: vda_1.InstantActions.CLEAR_LOAD_HANDLER,
                    metadata: {
                        loadDropped: false,
                    },
                },
            ],
        };
        expect(order_management_1.OrderManagement.getInstance().getWorkpieceType).toHaveBeenCalledWith(orderId);
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
        order_management_1.OrderManagement.getInstance().retriggerFTSSteps = jest.fn().mockResolvedValue(Promise.resolve());
        await (0, helper_1.handleFtsState)(ftsState);
        expect(factory_layout_service_1.FactoryLayoutService.releaseNodesBefore).toHaveBeenCalledWith(serialNumber, lastNodeId);
        expect(order_management_1.OrderManagement.getInstance().retriggerFTSSteps).toHaveBeenCalled();
    });
    it('should return the correct last module serialNumber for an fts state', () => {
        const orderId = 'orderId';
        const modSerial = 'modSerial';
        const actionId = 'actionId';
        const targetModuleType = module_1.ModuleType.MILL;
        const ftsState = {
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
                state: vda_1.State.FINISHED,
                id: actionId,
                timestamp: new Date(),
            },
        };
        const targetModule = {
            type: 'MODULE',
            serialNumber: modSerial,
        };
        jest.spyOn(order_management_1.OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(targetModuleType);
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getForModuleType').mockReturnValue(targetModule);
        const actual = (0, helper_1.getLastModuleSerialNumber)(ftsState);
        expect(actual).toBeDefined();
        expect(actual).toEqual(modSerial);
        expect(order_management_1.OrderManagement.getInstance().getTargetModuleTypeForNavActionId).toHaveBeenCalledWith(actionId);
        expect(pairing_states_1.PairingStates.getInstance().getForModuleType).toHaveBeenCalledWith(targetModuleType, orderId);
    });
    it('should return the correct last module serialNumber for an fts state with module id as node id', () => {
        const orderId = 'orderId';
        const modSerial = 'modSerial';
        const actionId = 'actionId';
        const targetModuleType = module_1.ModuleType.MILL;
        const ftsState = {
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
                state: vda_1.State.FINISHED,
                id: actionId,
                timestamp: new Date(),
            },
        };
        const targetModule = {
            type: 'MODULE',
            serialNumber: 'mocked',
        };
        jest.spyOn(order_management_1.OrderManagement.getInstance(), 'getTargetModuleTypeForNavActionId').mockReturnValue(targetModuleType);
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getForModuleType').mockReturnValue(targetModule);
        const actual = (0, helper_1.getLastModuleSerialNumber)(ftsState);
        expect(actual).toBeDefined();
        expect(actual).toEqual(modSerial);
        expect(order_management_1.OrderManagement.getInstance().getTargetModuleTypeForNavActionId).not.toHaveBeenCalled();
        expect(pairing_states_1.PairingStates.getInstance().getForModuleType).not.toHaveBeenCalled();
    });
    it('should return true, if the available charger is ready', () => {
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getAllReady').mockReturnValue([
            {
                serialNumber: 'CHRG1',
                connected: true,
                available: ccu_1.AvailableState.READY,
                type: ccu_1.DeviceType.MODULE,
                subType: module_1.ModuleType.CHRG,
            },
        ]);
        const hasChargerAvailable = (0, helper_1.checkChargerAvailability)();
        expect(hasChargerAvailable).toBeTruthy();
    });
    it('should return false, if the available charger is not ready', () => {
        const hasChargerAvailable = (0, helper_1.checkChargerAvailability)();
        expect(hasChargerAvailable).toBeFalsy();
    });
    describe('Verify updateFtsBlockedNodes function', () => {
        const FTS_TEMPLATE = {
            serialNumber: 'someFts',
            timestamp: new Date(),
            orderId: 'someOrder',
            orderUpdateId: 0,
            lastNodeId: fts_1.NODE_ID_UNKNOWN,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            paused: false,
            errors: [],
            load: [],
        };
        let isOrderActionRunningMOCK, getActiveOrderMOCK, getLastFinishedDockIdMOCK, setLastFinishedDockIdMOCK, releaseAllNodesMOCK, releaseAllNodesExceptMOCK, releaseNodesBeforeMOCK;
        beforeEach(() => {
            isOrderActionRunningMOCK = jest.spyOn(order_management_1.OrderManagement.getInstance(), 'isOrderActionRunning').mockReturnValue(false);
            getActiveOrderMOCK = jest.spyOn(order_management_1.OrderManagement.getInstance(), 'getActiveOrder').mockReturnValue(undefined);
            getLastFinishedDockIdMOCK = jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'getLastFinishedDockId').mockReturnValue(undefined);
            setLastFinishedDockIdMOCK = jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'setLastFinishedDockId').mockReturnValue(undefined);
            releaseAllNodesMOCK = jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'releaseAllNodes').mockReturnValue(undefined);
            releaseAllNodesExceptMOCK = jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'releaseAllNodesExcept').mockReturnValue(undefined);
            releaseNodesBeforeMOCK = jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'releaseNodesBefore').mockReturnValue(undefined);
        });
        afterEach(() => {
            jest.clearAllMocks();
        });
        test('should release all nodes when lastNodeId is NODE_ID_UNKNOWN', () => {
            const state = { ...FTS_TEMPLATE, lastNodeId: fts_1.NODE_ID_UNKNOWN, serialNumber: 'serial123' };
            (0, helper_1.updateFtsBlockedNodes)(state);
            expect(releaseAllNodesMOCK).toHaveBeenCalledWith('serial123');
        });
        test('should release nodes before lastNodeId when actionState is null or undefined', () => {
            const state = { ...FTS_TEMPLATE, lastNodeId: 'node123', serialNumber: 'serial456' };
            (0, helper_1.updateFtsBlockedNodes)({ ...state, actionState: null });
            expect(releaseNodesBeforeMOCK).toHaveBeenCalledWith('serial456', 'node123');
            (0, helper_1.updateFtsBlockedNodes)({ ...state, actionState: undefined });
            expect(releaseNodesBeforeMOCK).toHaveBeenCalledWith('serial456', 'node123');
        });
        test('should release all nodes except lastNodeId when FTS is docked and it is a running dock action', () => {
            const state = {
                ...FTS_TEMPLATE,
                lastNodeId: 'node123',
                serialNumber: 'serial456',
                actionState: { state: vda_1.State.FINISHED, command: fts_1.FtsCommandType.DOCK, id: 'dock123', timestamp: new Date() },
                orderId: 'order456',
            };
            isOrderActionRunningMOCK.mockReturnValue(true); // Mocking condition to true
            getActiveOrderMOCK.mockReturnValue({ placeholder: true });
            (0, helper_1.updateFtsBlockedNodes)(state);
            expect(releaseAllNodesExceptMOCK).toHaveBeenCalledWith('serial456', 'node123');
            expect(setLastFinishedDockIdMOCK).toHaveBeenCalledWith('serial456', 'dock123');
        });
        test('should release all nodes except lastNodeId when FTS is docked and the dock action is not handled', () => {
            const state = {
                ...FTS_TEMPLATE,
                lastNodeId: 'node123',
                serialNumber: 'serial456',
                actionState: { state: vda_1.State.FINISHED, command: fts_1.FtsCommandType.DOCK, id: 'dock123', timestamp: new Date() },
                orderId: 'order456',
            };
            isOrderActionRunningMOCK.mockReturnValue(false);
            getActiveOrderMOCK.mockReturnValue(undefined);
            getLastFinishedDockIdMOCK.mockReturnValue('differentDockId');
            (0, helper_1.updateFtsBlockedNodes)(state);
            expect(releaseAllNodesExceptMOCK).toHaveBeenCalledWith('serial456', 'node123');
            expect(setLastFinishedDockIdMOCK).toHaveBeenCalledWith('serial456', 'dock123');
        });
        test('should not release nodes when FTS is docked and the order action had been handled', () => {
            const state = {
                ...FTS_TEMPLATE,
                lastNodeId: 'node123',
                serialNumber: 'serial456',
                actionState: { state: vda_1.State.FINISHED, command: fts_1.FtsCommandType.DOCK, id: 'dock123', timestamp: new Date() },
                orderId: 'order456',
            };
            isOrderActionRunningMOCK.mockReturnValue(false); // Mocking condition to false
            getActiveOrderMOCK.mockReturnValue({ placeholder: true });
            getLastFinishedDockIdMOCK.mockReturnValue('differentDockId'); // Mocking condition to true
            (0, helper_1.updateFtsBlockedNodes)(state);
            expect(factory_layout_service_1.FactoryLayoutService.releaseAllNodesExcept).not.toHaveBeenCalled();
            expect(factory_layout_service_1.FactoryLayoutService.releaseNodesBefore).not.toHaveBeenCalled();
            expect(setLastFinishedDockIdMOCK).toHaveBeenCalledWith('serial456', 'dock123');
        });
        test('should not release nodes when FTS is docked and the dock action is the latest handled', () => {
            const state = {
                ...FTS_TEMPLATE,
                lastNodeId: 'node123',
                serialNumber: 'serial456',
                actionState: { state: vda_1.State.FINISHED, command: fts_1.FtsCommandType.DOCK, id: 'dock123', timestamp: new Date() },
                orderId: 'order456',
            };
            isOrderActionRunningMOCK.mockReturnValue(false); // Mocking condition to false
            getActiveOrderMOCK.mockReturnValue(undefined);
            getLastFinishedDockIdMOCK.mockReturnValue('dock123'); // Mocking condition to true
            (0, helper_1.updateFtsBlockedNodes)(state);
            expect(factory_layout_service_1.FactoryLayoutService.releaseAllNodesExcept).not.toHaveBeenCalled();
            expect(factory_layout_service_1.FactoryLayoutService.releaseNodesBefore).not.toHaveBeenCalled();
            expect(setLastFinishedDockIdMOCK).toHaveBeenCalledWith('serial456', 'dock123');
        });
        test('should release nodes before lastNodeId for any other scenario', () => {
            const state = { ...FTS_TEMPLATE, lastNodeId: 'node123', serialNumber: 'serial456' };
            (0, helper_1.updateFtsBlockedNodes)(state);
            expect(factory_layout_service_1.FactoryLayoutService.releaseNodesBefore).toHaveBeenCalledWith('serial456', 'node123');
        });
    });
});
