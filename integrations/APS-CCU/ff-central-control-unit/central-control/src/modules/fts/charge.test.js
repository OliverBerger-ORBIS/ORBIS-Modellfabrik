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
const factory_layout_service_1 = require("../layout/factory-layout-service");
const order_management_1 = require("../order/management/order-management");
const fts_pairing_states_1 = require("../pairing/fts-pairing-states");
const pairing_states_1 = require("../pairing/pairing-states");
const chargeSpies = __importStar(require("./charge"));
const charge_1 = require("./charge");
const navigationSpies = __importStar(require("./navigation/navigation"));
const mqttSpies = __importStar(require("../../mqtt/mqtt"));
const module_1 = require("../../../../common/protocol/module");
const navigator_service_1 = require("./navigation/navigator-service");
const fts_1 = require("../../../../common/protocol/fts");
const config_1 = __importDefault(require("../../config"));
jest.mock('../pairing/fts-pairing-states');
jest.mock('../pairing/pairing-states');
jest.mock('../order/management/order-management');
describe('Test sending charging commands', () => {
    beforeEach(() => {
        jest.spyOn(mqttSpies, 'getMqttClient').mockReturnValue({ publish: jest.fn() });
        jest.spyOn(fts_pairing_states_1.FtsPairingStates, 'getInstance').mockReturnValue({
            getFtsAtPosition: jest.fn(),
            updateAvailability: jest.fn(),
            isReady: jest.fn(),
            isCharging: jest.fn(),
            get: jest.fn(),
            updateCharge: jest.fn(),
        });
        jest.spyOn(order_management_1.OrderManagement, 'getInstance').mockReturnValue({
            getTargetModuleTypeForNavActionId: jest.fn(),
            getWorkpieceType: jest.fn(),
        });
        jest.spyOn(pairing_states_1.PairingStates, 'getInstance').mockReturnValue({
            updateAvailability: jest.fn(),
            get: jest.fn(),
            getAllReady: jest.fn(),
            isReady: jest.fn(),
            getForModuleType: jest.fn(),
            clearModuleForOrder: jest.fn(),
        });
        jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'releaseNodesBefore').mockReturnValue();
        jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'blockNodeSequence').mockReturnValue();
        charge_1.FTS_WAITING_FOR_RECHARGE.clear();
    });
    afterEach(() => {
        order_management_1.OrderManagement['instance'] = undefined;
        jest.clearAllMocks();
        jest.restoreAllMocks();
        charge_1.FTS_WAITING_FOR_RECHARGE.clear();
    });
    it('should ignore a partially filled battery without percentage and minVolt', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                currentVoltage: 8.6,
                minVolt: undefined,
                percentage: null,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        const isLow = (0, charge_1.isBatteryLow)(state);
        expect(isLow).toBe(false);
    });
    it('should ignore a battery info without percentage and minVolt', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                currentVoltage: 8.2,
                minVolt: undefined,
                percentage: null,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        const isLow = (0, charge_1.isBatteryLow)(state);
        expect(isLow).toBe(false);
    });
    it('should ignore a battery info without percentage', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                currentVoltage: 8.6,
                minVolt: 8.5,
                percentage: null,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        const isLow = (0, charge_1.isBatteryLow)(state);
        expect(isLow).toBe(false);
    });
    it('should detect a low battery', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                currentVoltage: 8.6,
                minVolt: 8.5,
                percentage: 10,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        const isLow = (0, charge_1.isBatteryLow)(state);
        expect(isLow).toBe(true);
    });
    it('should detect an extremely low battery', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                currentVoltage: 7.7,
                minVolt: 8.4,
                maxVolt: 10,
                percentage: -15,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        const isLow = (0, charge_1.isBatteryLow)(state);
        expect(isLow).toBe(true);
    });
    it('should detect a low battery with configured values from the fts', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                currentVoltage: 8.52,
                minVolt: 8.4,
                maxVolt: 10.0,
                percentage: 10,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        const isLow = (0, charge_1.isBatteryLow)(state);
        expect(isLow).toBe(true);
    });
    it('should detect a battery that is partially charged', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                currentVoltage: 8.76,
                minVolt: 8.4,
                maxVolt: 10.0,
                percentage: 30,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        const isLow = (0, charge_1.isBatteryLow)(state);
        expect(isLow).toBe(false);
    });
    it('should detect a full battery', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                currentVoltage: 8.94,
                minVolt: 8.4,
                percentage: 45,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        const isLow = (0, charge_1.isBatteryLow)(state);
        expect(isLow).toBe(false);
    });
    it('should detect a low battery with percentage only', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                minVolt: 8.4,
                percentage: 4,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        const isLow = (0, charge_1.isBatteryLow)(state);
        expect(isLow).toBe(true);
    });
    it('should detect a full battery with percentage only', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                minVolt: 8.5,
                percentage: 80,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        const isLow = (0, charge_1.isBatteryLow)(state);
        expect(isLow).toBe(false);
    });
    it('should not detect a missing value as a low battery', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                minVolt: 8.5,
                percentage: undefined,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        const isLow = (0, charge_1.isBatteryLow)(state);
        expect(isLow).toBe(false);
    });
    it('should set charging state', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                charging: true,
                currentVoltage: 8,
                percentage: 10,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(false);
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'updateCharge').mockReturnValue();
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'clearModuleForOrder').mockReturnValue();
        (0, charge_1.handleChargingUpdate)(state);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().isCharging).not.toHaveBeenCalled();
        expect(pairing_states_1.PairingStates.getInstance().clearModuleForOrder).not.toHaveBeenCalled();
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateCharge).toHaveBeenCalledWith(ftsSerial, true, state.batteryState.currentVoltage, // eslint-disable-line @typescript-eslint/no-non-null-assertion
        state.batteryState.percentage);
    });
    it('should set charging state to false', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: '1',
            batteryState: {
                charging: false,
                currentVoltage: 8,
                percentage: 10,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(false);
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'updateCharge').mockReturnValue();
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'clearModuleForOrder').mockReturnValue();
        (0, charge_1.handleChargingUpdate)(state);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().isCharging).toHaveBeenCalledWith(ftsSerial);
        expect(pairing_states_1.PairingStates.getInstance().clearModuleForOrder).not.toHaveBeenCalled();
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateCharge).toHaveBeenCalledWith(ftsSerial, false, state.batteryState.currentVoltage, // eslint-disable-line @typescript-eslint/no-non-null-assertion
        state.batteryState.percentage);
    });
    it('should set charging state to false and clear the module if the old state was charging', () => {
        const ftsSerial = 'FTS';
        const state = {
            serialNumber: ftsSerial,
            orderId: 'orderId',
            batteryState: {
                charging: false,
                currentVoltage: 8,
                percentage: 10,
            },
            lastNodeId: '',
            paused: true,
            timestamp: new Date(),
            orderUpdateId: 0,
            lastNodeSequenceId: 0,
            nodeStates: [],
            edgeStates: [],
            driving: false,
            errors: [],
            load: [],
        };
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(true);
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'updateCharge').mockReturnValue();
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'clearModuleForOrder').mockReturnValue();
        (0, charge_1.handleChargingUpdate)(state);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().isCharging).toHaveBeenCalledWith(ftsSerial);
        expect(pairing_states_1.PairingStates.getInstance().clearModuleForOrder).toHaveBeenCalledWith(state.orderId);
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateCharge).toHaveBeenCalledWith(ftsSerial, false, state.batteryState.currentVoltage, // eslint-disable-line @typescript-eslint/no-non-null-assertion
        state.batteryState.percentage);
    });
    it('should trigger a charge order', async () => {
        const ftsSerial = 'FTS';
        const chargeModule = {
            type: 'MODULE',
            subType: module_1.ModuleType.CHRG,
            serialNumber: 'CHRG1',
        };
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'get').mockReturnValue({
            serialNumber: ftsSerial,
            type: 'FTS',
            lastModuleSerialNumber: 'someModule',
        });
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isReady').mockReturnValue(true);
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(false);
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getAllReady').mockReturnValue([chargeModule]);
        jest.spyOn(chargeSpies, 'sendChargingNavigationRequest').mockResolvedValue();
        jest.spyOn(navigationSpies, 'getSortedModulePaths').mockReturnValue([{ module: chargeModule, path: { distance: 2, path: [] } }]);
        await (0, charge_1.triggerChargeOrderForFts)(ftsSerial);
        if (!config_1.default.ftsCharge.disabled) {
            expect(chargeSpies.sendChargingNavigationRequest).toHaveBeenCalledWith(ftsSerial, chargeModule.serialNumber);
        }
        else {
            expect(chargeSpies.sendChargingNavigationRequest).not.toHaveBeenCalledWith(ftsSerial, chargeModule.serialNumber);
        }
        expect(charge_1.FTS_WAITING_FOR_RECHARGE).toEqual(new Set());
        expect(charge_1.FTS_WAITING_FOR_RECHARGE.size).toEqual(0);
    });
    it('should not trigger a charge order if the FTS is not ready and add it to the queue', async () => {
        const ftsSerial = 'FTS';
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'get').mockReturnValue({
            serialNumber: ftsSerial,
            type: 'FTS',
            lastModuleSerialNumber: 'someModule',
        });
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isReady').mockReturnValue(false);
        jest.spyOn(chargeSpies, 'sendChargingNavigationRequest').mockResolvedValue();
        await (0, charge_1.triggerChargeOrderForFts)(ftsSerial);
        expect(chargeSpies.sendChargingNavigationRequest).not.toHaveBeenCalled();
        if (!config_1.default.ftsCharge.disabled) {
            expect(charge_1.FTS_WAITING_FOR_RECHARGE.size).toEqual(1);
            expect(charge_1.FTS_WAITING_FOR_RECHARGE).toEqual(new Set([ftsSerial]));
        }
        else {
            expect(charge_1.FTS_WAITING_FOR_RECHARGE.size).toEqual(0);
            expect(charge_1.FTS_WAITING_FOR_RECHARGE).toEqual(new Set());
        }
    });
    it('should not trigger a charge order if there is no ready charging module', async () => {
        const ftsSerial = 'FTS';
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'get').mockReturnValue({
            serialNumber: ftsSerial,
            type: 'FTS',
            lastModuleSerialNumber: 'someModule',
        });
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isReady').mockReturnValue(true);
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(false);
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getAllReady').mockReturnValue([]);
        jest.spyOn(chargeSpies, 'sendChargingNavigationRequest').mockResolvedValue();
        await (0, charge_1.triggerChargeOrderForFts)(ftsSerial);
        expect(chargeSpies.sendChargingNavigationRequest).not.toHaveBeenCalled();
        if (!config_1.default.ftsCharge.disabled) {
            expect(charge_1.FTS_WAITING_FOR_RECHARGE.size).toEqual(1);
            expect(charge_1.FTS_WAITING_FOR_RECHARGE).toEqual(new Set([ftsSerial]));
        }
        else {
            expect(charge_1.FTS_WAITING_FOR_RECHARGE.size).toEqual(0);
            expect(charge_1.FTS_WAITING_FOR_RECHARGE).toEqual(new Set());
        }
    });
    it('should not trigger a charge order if there is no path to a ready charging module', async () => {
        const ftsSerial = 'FTS';
        const chargeModule = {
            type: 'MODULE',
            subType: module_1.ModuleType.CHRG,
            serialNumber: 'CHRG1',
        };
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'get').mockReturnValue({
            serialNumber: ftsSerial,
            type: 'FTS',
            lastModuleSerialNumber: 'someModule',
        });
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isReady').mockReturnValue(true);
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isCharging').mockReturnValue(false);
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getAllReady').mockReturnValue([chargeModule]);
        jest.spyOn(navigationSpies, 'getSortedModulePaths').mockReturnValue([]);
        jest.spyOn(chargeSpies, 'sendChargingNavigationRequest').mockResolvedValue();
        await (0, charge_1.triggerChargeOrderForFts)(ftsSerial);
        expect(chargeSpies.sendChargingNavigationRequest).not.toHaveBeenCalled();
        if (!config_1.default.ftsCharge.disabled) {
            expect(charge_1.FTS_WAITING_FOR_RECHARGE.size).toEqual(1);
            expect(charge_1.FTS_WAITING_FOR_RECHARGE).toEqual(new Set([ftsSerial]));
        }
        else {
            expect(charge_1.FTS_WAITING_FOR_RECHARGE.size).toEqual(0);
            expect(charge_1.FTS_WAITING_FOR_RECHARGE).toEqual(new Set());
        }
    });
    it('should send a navigation request for charging', async () => {
        const ftsSerial = 'FTS';
        const chargeModule = {
            type: 'MODULE',
            subType: module_1.ModuleType.CHRG,
            serialNumber: 'CHRG1',
        };
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'get').mockReturnValue({
            serialNumber: ftsSerial,
            type: 'FTS',
            lastModuleSerialNumber: 'someModule',
        });
        const orderToSend = {
            orderId: 'orderId',
            timestamp: new Date('2022-02-02T12:12:12Z'),
            orderUpdateId: 0,
            serialNumber: ftsSerial,
            nodes: [
                { id: '1', action: { type: fts_1.FtsCommandType.PASS, id: 'action1' }, linkedEdges: [] },
                { id: chargeModule.serialNumber, action: { type: fts_1.FtsCommandType.DOCK, id: 'actionDock' }, linkedEdges: [] },
            ],
            edges: [],
        };
        const expectedOrder = JSON.parse(JSON.stringify(orderToSend));
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        expectedOrder.nodes[1].action.metadata = {
            loadPosition: fts_1.LoadingBay.MIDDLE,
            charge: true,
        };
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isReady').mockReturnValue(true);
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'get').mockReturnValue(chargeModule);
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'isReady').mockReturnValue(true);
        jest.spyOn(navigationSpies, 'getBlockedNodesForOrder').mockReturnValue([]);
        jest.spyOn(navigator_service_1.NavigatorService, 'getFTSOrder').mockReturnValue(orderToSend);
        await (0, charge_1.sendChargingNavigationRequest)(ftsSerial, chargeModule.serialNumber);
        expect(mqttSpies.getMqttClient().publish).toHaveBeenCalledWith('fts/v1/ff/FTS/order', JSON.stringify(expectedOrder));
    });
    it('should free a blocked charger if an FTS wants to charge', async () => {
        const ftsSerial = 'FTS';
        const chargeModule = {
            type: 'MODULE',
            subType: module_1.ModuleType.CHRG,
            serialNumber: 'CHRG1',
        };
        const fts = {
            serialNumber: ftsSerial,
            type: 'FTS',
            lastModuleSerialNumber: 'someModule',
        };
        charge_1.FTS_WAITING_FOR_RECHARGE.add('someFts');
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getAllReady').mockReturnValue([chargeModule]);
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'getFtsAtPosition').mockReturnValue(fts);
        jest.spyOn(navigationSpies, 'sendClearModuleNodeNavigationRequest').mockResolvedValue();
        await (0, charge_1.freeBlockedChargers)();
        expect(navigationSpies.sendClearModuleNodeNavigationRequest).toHaveBeenCalledWith(chargeModule.serialNumber);
    });
    it('should not free a blocked charger if no FTS wants to charge', async () => {
        const ftsSerial = 'FTS';
        const chargeModule = {
            type: 'MODULE',
            subType: module_1.ModuleType.CHRG,
            serialNumber: 'CHRG1',
        };
        const fts = {
            serialNumber: ftsSerial,
            type: 'FTS',
            lastModuleSerialNumber: 'someModule',
        };
        charge_1.FTS_WAITING_FOR_RECHARGE.clear();
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getAllReady').mockReturnValue([chargeModule]);
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'getFtsAtPosition').mockReturnValue(fts);
        jest.spyOn(navigationSpies, 'sendClearModuleNodeNavigationRequest').mockResolvedValue();
        await (0, charge_1.freeBlockedChargers)();
        expect(navigationSpies.sendClearModuleNodeNavigationRequest).not.toHaveBeenCalled();
    });
    it('should free a blocked charger if no FTS wants to charge and clearing is forced', async () => {
        const ftsSerial = 'FTS';
        const chargeModule = {
            type: 'MODULE',
            subType: module_1.ModuleType.CHRG,
            serialNumber: 'CHRG1',
        };
        const fts = {
            serialNumber: ftsSerial,
            type: 'FTS',
            lastModuleSerialNumber: 'someModule',
        };
        charge_1.FTS_WAITING_FOR_RECHARGE.clear();
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getAllReady').mockReturnValue([chargeModule]);
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'getFtsAtPosition').mockReturnValue(fts);
        jest.spyOn(navigationSpies, 'sendClearModuleNodeNavigationRequest').mockResolvedValue();
        await (0, charge_1.freeBlockedChargers)(true);
        expect(navigationSpies.sendClearModuleNodeNavigationRequest).toHaveBeenCalledWith(chargeModule.serialNumber);
    });
});
