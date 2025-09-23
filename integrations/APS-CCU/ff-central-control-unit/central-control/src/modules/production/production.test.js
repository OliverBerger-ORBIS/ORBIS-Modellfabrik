"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const node_crypto_1 = __importDefault(require("node:crypto"));
const ccu_1 = require("../../../../common/protocol/ccu");
const module_1 = require("../../../../common/protocol/module");
const vda_1 = require("../../../../common/protocol/vda");
const models_1 = require("../../models/models");
const test_helpers_1 = require("../../test-helpers");
const pairing_states_1 = require("../pairing/pairing-states");
const production_1 = require("./production");
describe('Test production updates', () => {
    let mqtt;
    let uuid_counter = 0;
    beforeEach(() => {
        mqtt = (0, test_helpers_1.createMockMqttClient)();
        jest.useFakeTimers().setSystemTime(new Date('2023-02-010T10:20:19Z'));
        // mock uuids with sequential deterministic values
        jest.spyOn(node_crypto_1.default, 'randomUUID').mockImplementation(() => {
            uuid_counter++;
            return `aabbccdd-eeee-ffff-1111-${uuid_counter}`;
        });
    });
    afterEach(() => {
        jest.clearAllMocks();
        jest.restoreAllMocks();
        jest.useRealTimers();
    });
    it('should should send a production command without metadata', async () => {
        const actionId = 'actionId';
        const serialNumber = 'serNr';
        const orderId = 'orderId';
        const orderUpdateId = 0;
        const prodStep = {
            id: actionId,
            type: 'MANUFACTURE',
            state: ccu_1.OrderState.ENQUEUED,
            moduleType: module_1.ModuleType.DRILL,
            command: module_1.ModuleCommandType.DROP,
            dependentActionId: 'dependentActionId',
        };
        const workpiece = 'RED';
        const metadata = {
            type: workpiece,
            workpieceId: 'workpieceId',
        };
        const command = {
            timestamp: new Date(),
            serialNumber: serialNumber,
            orderId,
            orderUpdateId,
            action: {
                id: actionId,
                command: module_1.ModuleCommandType.DROP,
                metadata,
            },
        };
        const pairedModule = {
            type: 'MODULE',
            serialNumber: serialNumber,
            available: ccu_1.AvailableState.READY,
            pairedSince: new Date(),
            connected: true,
            lastSeen: new Date(),
        };
        mockPairedState(pairedModule);
        await (0, production_1.sendProductionCommand)(prodStep, orderId, orderUpdateId, pairedModule, metadata);
        const topic = `module/v1/ff/${serialNumber}/order`;
        expect(mqtt.publish).toHaveBeenCalledWith(topic, JSON.stringify(command));
    });
    it('should should send a production command with metadata', async () => {
        const actionId = 'actionId';
        const serialNumber = 'serNr';
        const orderId = 'orderId';
        const orderUpdateId = 0;
        const prodStep = {
            id: actionId,
            type: 'MANUFACTURE',
            state: ccu_1.OrderState.ENQUEUED,
            moduleType: module_1.ModuleType.DRILL,
            command: module_1.ModuleCommandType.DRILL,
            dependentActionId: 'dependentActionId',
        };
        const metadata = {
            duration: 5,
        };
        const command = {
            timestamp: new Date(),
            serialNumber: serialNumber,
            orderId,
            orderUpdateId,
            action: {
                id: actionId,
                command: module_1.ModuleCommandType.DRILL,
                metadata,
            },
        };
        const pairedModule = {
            type: 'MODULE',
            serialNumber: serialNumber,
            available: ccu_1.AvailableState.READY,
            pairedSince: new Date(),
            connected: true,
            lastSeen: new Date(),
            productionDuration: 5,
        };
        mockPairedState(pairedModule);
        await (0, production_1.sendProductionCommand)(prodStep, orderId, orderUpdateId, pairedModule, metadata);
        const topic = `module/v1/ff/${serialNumber}/order`;
        expect(mqtt.publish).toHaveBeenCalledWith(topic, JSON.stringify(command));
    });
    it('should throw an error when the requested module is not ready to accept a new production command', async () => {
        const actionId = 'actionId';
        const orderId = 'orderId';
        const orderUpdateId = 0;
        const moduleType = module_1.ModuleType.MILL;
        const prodStep = {
            id: actionId,
            type: 'MANUFACTURE',
            state: ccu_1.OrderState.ENQUEUED,
            moduleType,
            command: module_1.ModuleCommandType.MILL,
            dependentActionId: 'dependentActionId',
        };
        mockPairedState(undefined);
        const metadata = {
            duration: 5,
        };
        try {
            await (0, production_1.sendProductionCommand)(prodStep, orderId, orderUpdateId, { serialNumber: 'not_ready' }, metadata);
        }
        catch (e) {
            expect(e).toBeInstanceOf(models_1.ControllerNotReadyError);
        }
        expect(mqtt.publish).not.toHaveBeenCalled();
        expect.assertions(2);
    });
    const mockPairedState = (pairedModule) => {
        pairing_states_1.PairingStates['instance'] = {
            getReadyForModuleType: jest.fn().mockReturnValue(pairedModule),
            isReadyForOrder: jest.fn().mockReturnValue(!!pairedModule),
        };
    };
    it('should should send a announceOutput instant action', async () => {
        const serialNumber = 'serNr';
        const orderId = 'orderId';
        const workpiece = ccu_1.Workpiece.RED;
        const expected = {
            serialNumber,
            timestamp: new Date(),
            actions: [
                {
                    actionId: 'aabbccdd-eeee-ffff-1111-1',
                    actionType: vda_1.InstantActions.ANNOUNCE_OUTPUT,
                    metadata: {
                        orderId: orderId,
                        type: workpiece,
                    },
                },
            ],
        };
        await (0, production_1.sendAnnounceDpsOutput)(serialNumber, orderId, workpiece);
        const topic = `module/v1/ff/${serialNumber}/instantAction`;
        expect(mqtt.publish).toHaveBeenCalledWith(topic, JSON.stringify(expected), { qos: 2 });
    });
});
