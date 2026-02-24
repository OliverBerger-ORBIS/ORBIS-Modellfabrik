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
Object.defineProperty(exports, "__esModule", { value: true });
const ccu_1 = require("../../../../../common/protocol/ccu");
const module_1 = require("../../../../../common/protocol/module");
const navCommandSender = __importStar(require("../../fts/navigation/navigation"));
const navigator_service_1 = require("../../fts/navigation/navigator-service");
const fts_pairing_states_1 = require("../../pairing/fts-pairing-states");
const pairing_states_1 = require("../../pairing/pairing-states");
const moduleCommandSender = __importStar(require("../../production/production"));
const stock_management_service_1 = require("../stock/stock-management-service");
const order_management_1 = require("./order-management");
describe('Test order management handling for DPS announcements', () => {
    const MOCKED_DATE = new Date('2021-01-01T00:00:00.000Z');
    const MOCKED_PATH = { path: [1], distance: 1 };
    const MOCKED_MODULE_SERIAL = 'mockedSerial';
    let underTest;
    beforeEach(() => {
        jest.spyOn(navCommandSender, 'sendNavigationRequest').mockResolvedValue();
        jest.spyOn(navCommandSender, 'sendClearModuleNodeNavigationRequest').mockRejectedValue('Tests should not try to clear a module.');
        jest.spyOn(moduleCommandSender, 'sendProductionCommand').mockResolvedValue();
        jest.spyOn(stock_management_service_1.StockManagementService, 'stockAvailable').mockReturnValue(undefined);
        jest.spyOn(navigator_service_1.NavigatorService, 'getFTSPath').mockReturnValue(MOCKED_PATH);
        jest.useFakeTimers().setSystemTime(MOCKED_DATE);
        jest.mock('../../pairing/fts-pairing-states');
        fts_pairing_states_1.FtsPairingStates.getInstance().getAllReadyUnassigned = jest.fn().mockReturnValue([]);
        fts_pairing_states_1.FtsPairingStates.getInstance().getReady = jest.fn();
        pairing_states_1.PairingStates.getInstance().getReadyForModuleType = jest.fn().mockReturnValue({ serialNumber: MOCKED_MODULE_SERIAL });
        pairing_states_1.PairingStates.getInstance().isReadyForOrder = jest.fn().mockReturnValue(true);
        underTest = order_management_1.OrderManagement.getInstance();
        stock_management_service_1.StockManagementService.reset();
        jest.mock('../../production/helper');
    });
    afterEach(() => {
        // resetting the singleton for clean tests
        underTest['orderQueue'] = new Array();
        underTest['activeOrders'] = [];
        underTest['completedOrders'] = [];
        underTest['navStepsToExecute'] = [];
        underTest['manufactureStepsToExecute'] = [];
        jest.resetAllMocks();
        jest.restoreAllMocks();
        jest.useRealTimers();
    });
    it('should announce the output to the DPS when the navigation to it is started for PICK', async () => {
        const orderId2 = 'orderId2';
        const workpiece2 = 'WHITE';
        const workpieceId2 = undefined;
        const navStepOrder2Id = 'navStepOrder2';
        const dpsSerial = 'dpsSerial';
        await setupAndTriggerNavigationRequestExpectSuccess(module_1.ModuleCommandType.PICK, workpiece2, workpieceId2, navStepOrder2Id, orderId2, dpsSerial, module_1.ModuleType.DPS);
        expect(moduleCommandSender.sendAnnounceDpsOutput).toHaveBeenCalledWith(dpsSerial, orderId2, workpiece2);
    });
    it('should not announce the output to the DPS when the navigation to it is started for DROP', async () => {
        const orderId2 = 'orderId2';
        const workpiece2 = 'WHITE';
        const workpieceId2 = undefined;
        const navStepOrder2Id = 'navStepOrder2';
        const dpsSerial = 'dpsSerial';
        await setupAndTriggerNavigationRequestExpectSuccess(module_1.ModuleCommandType.DROP, workpiece2, workpieceId2, navStepOrder2Id, orderId2, dpsSerial, module_1.ModuleType.DPS);
        expect(moduleCommandSender.sendAnnounceDpsOutput).not.toHaveBeenCalled();
        expect(underTest['navStepsToExecute']).toEqual([]);
        expect(underTest['manufactureStepsToExecute']).toEqual([]);
    });
    it('should NOT announce the output for a not-DPS when the navigation to it is started for PICK', async () => {
        const orderId2 = 'orderId2';
        const workpiece2 = 'WHITE';
        const workpieceId2 = undefined;
        const navStepOrder2Id = 'navStepOrder2';
        const hbwSerial = 'dpsSerial';
        await setupAndTriggerNavigationRequestExpectSuccess(module_1.ModuleCommandType.PICK, workpiece2, workpieceId2, navStepOrder2Id, orderId2, hbwSerial, module_1.ModuleType.HBW);
        expect(moduleCommandSender.sendAnnounceDpsOutput).toHaveBeenCalledWith(hbwSerial, orderId2, workpiece2);
    });
    it('should not announce the output to the DPS when the navigation to it is started for DROP', async () => {
        const orderId2 = 'orderId2';
        const workpiece2 = 'WHITE';
        const workpieceId2 = undefined;
        const navStepOrder2Id = 'navStepOrder2';
        const hbwSerial = 'dpsSerial';
        await setupAndTriggerNavigationRequestExpectSuccess(module_1.ModuleCommandType.DROP, workpiece2, workpieceId2, navStepOrder2Id, orderId2, hbwSerial, module_1.ModuleType.HBW);
        expect(moduleCommandSender.sendAnnounceDpsOutput).not.toHaveBeenCalled();
        expect(underTest['navStepsToExecute']).toEqual([]);
        expect(underTest['manufactureStepsToExecute']).toEqual([]);
    });
    async function setupAndTriggerNavigationRequestExpectSuccess(command, workpiece2, workpieceId2, navStepOrder2Id, orderId2, moduleSerial, moduleType) {
        const navStepOrder2 = {
            id: navStepOrder2Id,
            type: 'NAVIGATION',
            target: module_1.ModuleType.DPS,
            state: ccu_1.OrderState.ENQUEUED,
            source: module_1.ModuleType.START,
        };
        const dropStepOrder2 = {
            id: navStepOrder2Id,
            type: 'MANUFACTURE',
            moduleType: module_1.ModuleType.DPS,
            command: command,
            dependentActionId: navStepOrder2Id,
            state: ccu_1.OrderState.ENQUEUED,
        };
        const navStepOrder2Action = {
            index: 0,
            workpieceId: workpieceId2,
            workpiece: workpiece2,
            value: navStepOrder2,
            orderId: orderId2,
        };
        const order2 = {
            orderType: 'PRODUCTION',
            orderId: orderId2,
            state: ccu_1.OrderState.IN_PROGRESS,
            workpieceId: workpieceId2,
            type: workpiece2,
            timestamp: new Date(),
            startedAt: new Date(),
            productionSteps: [navStepOrder2, dropStepOrder2],
        };
        underTest['activeOrders'] = [order2];
        underTest['orderQueue'] = [order2];
        underTest['navStepsToExecute'] = [navStepOrder2Action];
        const fts = {
            serialNumber: 'serialNumber',
            type: 'FTS',
            lastModuleSerialNumber: 'HBW',
            lastLoadPosition: '2',
        };
        const module = {
            serialNumber: moduleSerial,
            type: 'MODULE',
            subType: moduleType,
        };
        let ftsIsBusy = false;
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getModuleForOrder').mockReturnValue(undefined);
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getReadyForModuleType').mockReturnValue(module);
        jest
            .spyOn(underTest, 'chooseReadyFtsForStep')
            .mockImplementation(() => (ftsIsBusy ? undefined : { fts, path: { path: [1], distance: 0 } }));
        jest.spyOn(navCommandSender, 'sendNavigationRequest').mockImplementation(() => {
            ftsIsBusy = true;
            return Promise.resolve();
        });
        jest.spyOn(moduleCommandSender, 'sendProductionCommand').mockImplementation(() => {
            return Promise.reject();
        });
        jest.spyOn(moduleCommandSender, 'sendAnnounceDpsOutput').mockImplementation(() => {
            return Promise.resolve();
        });
        jest.spyOn(stock_management_service_1.StockManagementService, 'stockAvailable').mockReturnValue(undefined);
        jest.spyOn(stock_management_service_1.StockManagementService, 'reserveWorkpiece').mockReturnValue(undefined);
        await underTest.retriggerFTSSteps();
        expect(underTest.chooseReadyFtsForStep).toHaveBeenCalledWith(orderId2, moduleSerial, expect.anything());
        expect(navCommandSender.sendNavigationRequest).toHaveBeenCalledWith(navStepOrder2Action.value, orderId2, navStepOrder2Action.index, workpiece2, workpieceId2, fts, module.serialNumber);
        expect(moduleCommandSender.sendProductionCommand).not.toHaveBeenCalled();
        expect(underTest['navStepsToExecute']).toEqual([]);
        expect(underTest['manufactureStepsToExecute']).toEqual([]);
    }
});
