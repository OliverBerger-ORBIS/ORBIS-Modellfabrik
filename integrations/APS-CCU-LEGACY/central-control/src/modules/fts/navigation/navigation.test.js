"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const ccu_1 = require("../../../../../common/protocol/ccu");
const fts_1 = require("../../../../../common/protocol/fts");
const module_1 = require("../../../../../common/protocol/module");
const models_1 = require("../../../models/models");
const test_helpers_1 = require("../../../test-helpers");
const factory_layout_service_1 = require("../../layout/factory-layout-service");
const fts_pairing_states_1 = require("../../pairing/fts-pairing-states");
const pairing_states_1 = require("../../pairing/pairing-states");
const model_1 = require("../model");
const navigation_1 = require("./navigation");
const navigator_service_1 = require("./navigator-service");
const json_revivers_1 = require("../../../../../common/util/json.revivers");
const protocol_1 = require("../../../../../common/protocol");
describe('Test Navigation', () => {
    let mqtt;
    const FTS_SERIAL = 'FTS1';
    beforeEach(() => {
        mqtt = (0, test_helpers_1.createMockMqttClient)();
        jest.spyOn(fts_pairing_states_1.FtsPairingStates, 'getInstance').mockReturnValue({
            getOpenloadingBay: () => undefined,
            getForOrder: () => undefined,
            isReadyForOrder: () => false,
            setLoadingBay: () => undefined,
            getFtsAtPosition: () => undefined,
            updateAvailability: () => jest.fn(),
            getAllReadyUnassigned: () => jest.fn(),
            getAll: () => jest.fn(),
        });
    });
    afterEach(() => {
        jest.clearAllMocks();
        jest.useRealTimers();
    });
    it('should send a navigation request for navigation step', async () => {
        const actionId = 'actionId';
        const topic = `fts/v1/ff/${FTS_SERIAL}/order`;
        jest.useFakeTimers().setSystemTime(new Date('2023-02-02T11:46:19Z'));
        jest.mock('node:crypto');
        const orderId = 'orderId';
        const orderUpdateId = 0;
        const navStep = {
            id: 'id',
            type: 'NAVIGATION',
            state: ccu_1.OrderState.ENQUEUED,
            target: module_1.ModuleType.DPS,
            source: module_1.ModuleType.DRILL,
        };
        const dpsSerial = 'DPS_SERIAL';
        const drillSerial = 'DRILL1';
        const pairedFts = {
            serialNumber: FTS_SERIAL,
            type: 'FTS',
            lastModuleSerialNumber: drillSerial,
        };
        const loadPosition = '1';
        const workpiece = 'RED';
        const workpieceId = 'test';
        const expectedOrder = {
            edges: [
                {
                    id: '2-4',
                    linkedNodes: ['2', '4'],
                    length: 400,
                },
                {
                    id: '1-2',
                    length: 400,
                    linkedNodes: ['1', '2'],
                },
            ],
            nodes: [
                {
                    id: '2',
                    linkedEdges: ['1-2', '2-3', '2-4', '2-5'],
                    action: {
                        type: fts_1.FtsCommandType.PASS,
                        id: actionId,
                    },
                },
                {
                    id: '1',
                    linkedEdges: ['1-2'],
                    action: {
                        type: fts_1.FtsCommandType.TURN,
                        metadata: {
                            direction: model_1.Direction.BACK,
                        },
                        id: 'id',
                    },
                },
            ],
            orderId,
            orderUpdateId,
            serialNumber: FTS_SERIAL,
            timestamp: new Date('2023-02-02T11:46:19.000Z'),
        };
        const expectedBlockedNodes = [
            { afterNodeId: undefined, ftsSerialNumber: 'FTS1', nodeId: '2' },
            { afterNodeId: '2', ftsSerialNumber: 'FTS1', nodeId: '1' },
        ];
        jest.mock('../../pairing/pairing-states');
        fts_pairing_states_1.FtsPairingStates.getInstance().isReady = jest.fn().mockReturnValue(true);
        fts_pairing_states_1.FtsPairingStates.getInstance().getOpenloadingBay = jest.fn().mockReturnValue(loadPosition);
        fts_pairing_states_1.FtsPairingStates.getInstance().getLoadingBayForOrder = jest.fn().mockReturnValue(undefined);
        fts_pairing_states_1.FtsPairingStates.getInstance().setLoadingBay = jest.fn();
        fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability = jest.fn();
        jest.mock('../../pairing/pairing-states');
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'isReadyForOrder').mockImplementation(() => true);
        jest.spyOn(navigator_service_1.NavigatorService, 'getFTSOrder').mockReturnValue(expectedOrder);
        jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'blockNodeSequence').mockReturnValue();
        await (0, navigation_1.sendNavigationRequest)(navStep, orderId, orderUpdateId, workpiece, workpieceId, pairedFts, dpsSerial);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().isReady).toHaveBeenCalledWith(FTS_SERIAL);
        expect(mqtt.publish).toHaveBeenCalledWith(topic, expect.anything(), { qos: 2 });
        expect(pairing_states_1.PairingStates.getInstance().isReadyForOrder).toHaveBeenCalledWith(dpsSerial, orderId);
        expect(navigator_service_1.NavigatorService.getFTSOrder).toHaveBeenCalledWith(drillSerial, dpsSerial, orderId, orderUpdateId, FTS_SERIAL, navStep.id);
        expect(factory_layout_service_1.FactoryLayoutService.blockNodeSequence).toHaveBeenCalledWith(expectedBlockedNodes);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().setLoadingBay).toHaveBeenCalledWith(FTS_SERIAL, loadPosition, orderId);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().updateAvailability).toHaveBeenCalledWith(FTS_SERIAL, ccu_1.AvailableState.BUSY, orderId, pairedFts.lastNodeId, pairedFts.lastModuleSerialNumber, loadPosition);
    });
    it('should throw an error when there is not FTS in a ready state', async () => {
        const navStep = {
            id: 'id',
            type: 'NAVIGATION',
            state: ccu_1.OrderState.ENQUEUED,
            target: module_1.ModuleType.DPS,
            source: module_1.ModuleType.DRILL,
        };
        const fts = {
            serialNumber: 'serialNumber',
            type: 'FTS',
        };
        jest.mock('../../pairing/pairing-states');
        fts_pairing_states_1.FtsPairingStates.getInstance().isReady = jest.fn().mockReturnValue(false);
        jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'blockNodeSequence').mockReturnValue();
        try {
            await (0, navigation_1.sendNavigationRequest)(navStep, 'orderId', 0, 'RED', 'test', fts, 'targetSerial');
        }
        catch (e) {
            expect(e).toBeInstanceOf(models_1.FTSNotReadyError);
        }
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().isReady).toHaveBeenCalledWith(fts.serialNumber);
        expect(mqtt.publish).not.toHaveBeenCalled();
        expect.assertions(3);
    });
    it('should calculate and sort the paths for all unassigned ready FTS', async () => {
        const targetSerial = 'targetSerial';
        const fts = {
            serialNumber: 'serialNumber',
            type: 'FTS',
            lastModuleSerialNumber: 'startMod',
        };
        const fts2 = {
            serialNumber: 'serialNumber2',
            type: 'FTS',
            lastModuleSerialNumber: 'startMod2',
        };
        const fts3 = {
            serialNumber: 'serialNumber3',
            type: 'FTS',
            lastModuleSerialNumber: 'startMod3',
        };
        const fts4 = {
            serialNumber: 'serialNumber4',
            type: 'FTS',
        };
        const ftsPaths = {
            [fts.serialNumber]: {
                path: [1, 2],
                distance: 50,
            },
            [fts2.serialNumber]: {
                path: [0, 2],
                distance: 30,
            },
            [fts3.serialNumber]: {
                path: [1],
                distance: 40,
            },
        };
        const readyData = [{ state: fts }, { state: fts2 }, { state: fts3 }, { state: fts4 }];
        const expectedResult = [
            {
                fts: fts2,
                path: ftsPaths[fts2.serialNumber],
            },
            {
                fts: fts3,
                path: ftsPaths[fts3.serialNumber],
            },
            {
                fts: fts,
                path: ftsPaths[fts.serialNumber],
            },
        ];
        jest.mock('../../pairing/pairing-states');
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'getAllReadyUnassigned').mockReturnValue(readyData);
        jest.spyOn(navigator_service_1.NavigatorService, 'getFTSPath').mockImplementation((start, target, ftsSerial) => ftsPaths[ftsSerial]);
        const result = (0, navigation_1.getSortedUnassignedFtsPaths)(targetSerial);
        expect(fts_pairing_states_1.FtsPairingStates.getInstance().getAllReadyUnassigned).toHaveBeenCalled();
        expect(navigator_service_1.NavigatorService.getFTSPath).toHaveBeenCalledTimes(3);
        expect(navigator_service_1.NavigatorService.getFTSPath).toHaveBeenNthCalledWith(1, fts.lastModuleSerialNumber, targetSerial, fts.serialNumber);
        expect(navigator_service_1.NavigatorService.getFTSPath).toHaveBeenNthCalledWith(2, fts2.lastModuleSerialNumber, targetSerial, fts2.serialNumber);
        expect(navigator_service_1.NavigatorService.getFTSPath).toHaveBeenNthCalledWith(3, fts3.lastModuleSerialNumber, targetSerial, fts3.serialNumber);
        expect(result).toEqual(expectedResult);
    });
    it('should add bay information', () => {
        const orderId = 'orderID';
        const order = {
            edges: [
                {
                    id: '2-4',
                    linkedNodes: ['2', '4'],
                    length: 400,
                },
                {
                    id: '1-2',
                    length: 400,
                    linkedNodes: ['1', '2'],
                },
            ],
            nodes: [
                {
                    id: '2',
                    linkedEdges: ['1-2', '2-3', '2-4', '2-5'],
                    action: {
                        type: fts_1.FtsCommandType.PASS,
                        id: '4',
                    },
                },
                {
                    id: '1',
                    linkedEdges: ['1-2'],
                    action: {
                        type: fts_1.FtsCommandType.DOCK,
                        id: '5',
                    },
                },
            ],
            orderId,
            orderUpdateId: 0,
            serialNumber: FTS_SERIAL,
            timestamp: new Date('2023-02-02T11:46:19.000Z'),
        };
        const loadId = 'asdasd';
        const loadPosition = '1';
        const loadType = 'RED';
        const ftsPairingStates = {
            setLoadingBay: jest.fn().mockReturnValue(loadPosition),
        };
        jest.spyOn(fts_pairing_states_1.FtsPairingStates, 'getInstance').mockReturnValue(ftsPairingStates);
        const dockingMetaData = { loadPosition, loadType, loadId };
        (0, navigation_1.addDockingMetadataToOrder)(order, ftsPairingStates, FTS_SERIAL, dockingMetaData);
        const expectedOrder = {
            edges: [
                {
                    id: '2-4',
                    linkedNodes: ['2', '4'],
                    length: 400,
                },
                {
                    id: '1-2',
                    length: 400,
                    linkedNodes: ['1', '2'],
                },
            ],
            nodes: [
                {
                    id: '2',
                    linkedEdges: ['1-2', '2-3', '2-4', '2-5'],
                    action: {
                        type: fts_1.FtsCommandType.PASS,
                        id: '4',
                    },
                },
                {
                    id: '1',
                    linkedEdges: ['1-2'],
                    action: {
                        type: fts_1.FtsCommandType.DOCK,
                        id: '5',
                        metadata: {
                            loadPosition,
                            loadType,
                            loadId,
                        },
                    },
                },
            ],
            orderId,
            orderUpdateId: 0,
            serialNumber: FTS_SERIAL,
            timestamp: new Date('2023-02-02T11:46:19.000Z'),
        };
        expect(order).toEqual(expectedOrder);
        expect(ftsPairingStates.setLoadingBay).toHaveBeenCalledWith(FTS_SERIAL, loadPosition, orderId);
    });
    it('should get the blocked nodes for an order, duplicate nodes are filtered', () => {
        const orderId = 'orderID';
        const order = {
            edges: [
                {
                    id: '2-4',
                    linkedNodes: ['2', '4'],
                    length: 400,
                },
                {
                    id: '1-2',
                    length: 400,
                    linkedNodes: ['1', '2'],
                },
            ],
            nodes: [
                {
                    id: '2',
                    linkedEdges: ['1-2', '2-3', '2-4', '2-5'],
                    action: {
                        type: fts_1.FtsCommandType.PASS,
                        id: '4',
                    },
                },
                {
                    id: '1',
                    linkedEdges: ['1-2'],
                    action: {
                        type: fts_1.FtsCommandType.TURN,
                        id: '23',
                    },
                },
                {
                    id: '1',
                    linkedEdges: ['1-2'],
                    action: {
                        type: fts_1.FtsCommandType.DOCK,
                        id: '5',
                    },
                },
            ],
            orderId,
            orderUpdateId: 0,
            serialNumber: FTS_SERIAL,
            timestamp: new Date('2023-02-02T11:46:19.000Z'),
        };
        const expectedBlockers = [
            { afterNodeId: undefined, ftsSerialNumber: 'FTS1', nodeId: '2' },
            { afterNodeId: '2', ftsSerialNumber: 'FTS1', nodeId: '1' },
        ];
        const blockers = (0, navigation_1.getBlockedNodesForOrder)(order);
        expect(blockers).toEqual(expectedBlockers);
    });
    it('should send a non-waiting docking order to remove an FTS from a module.', async () => {
        const fts = {
            serialNumber: FTS_SERIAL,
            type: 'FTS',
            lastModuleSerialNumber: 'startMod',
        };
        const blockedModuleId = 'blockedId';
        const targetModuleId = 'targetModuleId';
        const targetModule = {
            serialNumber: targetModuleId,
            type: 'MODULE',
            connected: true,
            pairedSince: new Date(),
        };
        const initialOrder = {
            edges: [
                {
                    id: `${blockedModuleId}-4`,
                    linkedNodes: [blockedModuleId, '4'],
                    length: 375,
                },
                {
                    id: `4-${targetModuleId}`,
                    length: 375,
                    linkedNodes: ['4', targetModuleId],
                },
            ],
            nodes: [
                {
                    id: blockedModuleId,
                    linkedEdges: [`${blockedModuleId}-4`],
                },
                {
                    id: '4',
                    linkedEdges: [`${blockedModuleId}-4`, `4-${targetModuleId}`],
                    action: {
                        type: fts_1.FtsCommandType.TURN,
                        metadata: {
                            direction: model_1.Direction.RIGHT,
                        },
                        id: 'id2',
                    },
                },
                {
                    id: targetModuleId,
                    linkedEdges: [`4-${targetModuleId}`],
                    action: {
                        type: fts_1.FtsCommandType.DOCK,
                        id: 'id3',
                    },
                },
            ],
            orderId: 'someOrderId',
            orderUpdateId: 0,
            serialNumber: FTS_SERIAL,
            timestamp: new Date('2023-02-02T11:46:19.000Z'),
        };
        const expectedOrder = JSON.parse(JSON.stringify(initialOrder), json_revivers_1.jsonIsoDateReviver);
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        expectedOrder.nodes[2].action.metadata = {
            loadPosition: fts_1.LoadingBay.MIDDLE,
            noLoadChange: true,
        };
        const readyFtsMock = jest
            .spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'getFtsAtPosition')
            .mockImplementation(moduleId => (moduleId === blockedModuleId ? fts : undefined));
        jest.spyOn(pairing_states_1.PairingStates.getInstance(), 'getAll').mockReturnValue([targetModule]);
        jest.spyOn(navigator_service_1.NavigatorService, 'getFTSOrder').mockReturnValue(initialOrder);
        jest.spyOn(factory_layout_service_1.FactoryLayoutService, 'blockNodeSequence').mockReturnValue();
        await (0, navigation_1.sendClearModuleNodeNavigationRequest)(blockedModuleId);
        expect(mqtt.publish).toHaveBeenCalledWith((0, protocol_1.getFtsTopic)(FTS_SERIAL, protocol_1.FtsTopic.ORDER), JSON.stringify(expectedOrder));
        expect(readyFtsMock).toHaveBeenNthCalledWith(1, blockedModuleId);
        expect(readyFtsMock).toHaveBeenNthCalledWith(2, targetModuleId);
    });
    it('should return a valid path for an FTS that can fulfill the order', async () => {
        const fts = {
            type: 'FTS',
            serialNumber: 'mockedFts',
            lastModuleSerialNumber: 'mockedModule',
            available: ccu_1.AvailableState.READY,
            connected: true,
        };
        const order = {
            orderId: 'mockOrder',
            orderType: 'PRODUCTION',
            type: 'RED',
            timestamp: new Date(),
            productionSteps: [],
            state: ccu_1.OrderState.IN_PROGRESS,
        };
        const step = {
            id: '1234567890',
            type: 'NAVIGATION',
            state: ccu_1.OrderState.ENQUEUED,
            source: module_1.ModuleType.START,
            target: module_1.ModuleType.CHRG,
        };
        const path = { path: [1], distance: 1 };
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'getForOrder').mockReturnValue(fts);
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isReadyForOrder').mockReturnValue(true);
        jest.spyOn(navigator_service_1.NavigatorService, 'getFTSPath').mockReturnValue(path);
        const result = (0, navigation_1.selectFtsPathForStep)(order, 'target', step);
        expect(result).toEqual({ fts, path });
    });
    it('should not return a valid path for an FTS that has the workpiece loaded, but is working on another order', async () => {
        const fts = {
            type: 'FTS',
            serialNumber: 'mockedFts',
            lastModuleSerialNumber: 'mockedModule',
            available: ccu_1.AvailableState.READY,
            connected: true,
        };
        const order = {
            orderId: 'mockOrder',
            orderType: 'PRODUCTION',
            type: 'RED',
            timestamp: new Date(),
            productionSteps: [],
            state: ccu_1.OrderState.IN_PROGRESS,
        };
        const step = {
            id: '1234567890',
            type: 'NAVIGATION',
            state: ccu_1.OrderState.ENQUEUED,
            source: module_1.ModuleType.START,
            target: module_1.ModuleType.CHRG,
        };
        const path = { path: [1], distance: 1 };
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'getForOrder').mockReturnValue(fts);
        jest.spyOn(fts_pairing_states_1.FtsPairingStates.getInstance(), 'isReadyForOrder').mockReturnValue(false);
        jest.spyOn(navigator_service_1.NavigatorService, 'getFTSPath').mockReturnValue(path);
        const result = (0, navigation_1.selectFtsPathForStep)(order, 'target', step);
        expect(result).toBeUndefined();
    });
});
